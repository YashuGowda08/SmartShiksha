"""MongoDB adapter — translates SQLAlchemy ORM queries to MongoDB operations.

Provides a MongoSession class that is compatible with SQLAlchemy's AsyncSession
interface for the subset of operations actually used by the SmartShiksha routers:

  execute(select(Model).where(...).order_by(...).limit(...).offset(...))
  result.scalars().all()  /  result.scalar_one_or_none()  /  result.scalar()
  db.add(obj)  /  db.add_all(objs)
  db.commit()  /  db.refresh(obj)  /  db.delete(obj)
  func.count()  /  func.avg()  /  func.sum()  with .group_by()
"""
from __future__ import annotations

import copy
import operator as _op
from datetime import datetime
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase
else:
    class AsyncIOMotorDatabase:  # pragma: no cover - typing fallback only
        pass
from sqlalchemy import Select, func as _sa_func
from sqlalchemy.sql import operators as sa_ops
from sqlalchemy.sql.elements import (
    BinaryExpression,
    BooleanClauseList,
    UnaryExpression,
    BindParameter,
    Null,
    True_,
    False_,
    ClauseList,
    Grouping,
)
from sqlalchemy.sql.functions import Function


# ────────────────────── helpers ──────────────────────


def _extract_value(element) -> Any:
    """Pull a plain Python value out of a SQLAlchemy element."""
    if isinstance(element, BindParameter):
        return element.value
    if isinstance(element, Null):
        return None
    if isinstance(element, (True_,)):
        return True
    if isinstance(element, (False_,)):
        return False
    if isinstance(element, Grouping):
        return _extract_value(element.element)
    if hasattr(element, "value"):
        return element.value
    return element


def _col_name(col) -> str:
    if hasattr(col, "key"):
        return col.key
    if hasattr(col, "name"):
        return col.name
    return str(col)


def _model_from_col(col):
    """Get the ORM model class from a Column / InstrumentedAttribute."""
    if hasattr(col, "class_"):
        return col.class_
    if hasattr(col, "entity_namespace"):
        return col.entity_namespace
    return None


# ────────────────────── condition parser ──────────────────────


def _parse_condition(expr) -> dict:
    """Recursively translate a SQLAlchemy WHERE clause → MongoDB filter dict."""
    if expr is None:
        return {}

    if isinstance(expr, BooleanClauseList):
        parts = [_parse_condition(c) for c in expr.clauses]
        # SQLAlchemy BooleanClauseList with 'AND' operator
        merged: dict = {}
        for p in parts:
            for k, v in p.items():
                if k in merged:
                    # same field, merge with $and
                    if "$and" not in merged:
                        merged["$and"] = []
                    merged["$and"].append({k: v})
                else:
                    merged[k] = v
        return merged

    if isinstance(expr, BinaryExpression):
        left = expr.left
        right = expr.right
        col = _col_name(left)
        val = _extract_value(right)
        op = expr.operator

        if op is sa_ops.eq:
            return {col: val}
        if op is sa_ops.ne:
            return {col: {"$ne": val}}
        if op is sa_ops.ge:
            return {col: {"$gte": val}}
        if op is sa_ops.le:
            return {col: {"$lte": val}}
        if op is sa_ops.gt:
            return {col: {"$gt": val}}
        if op is sa_ops.lt:
            return {col: {"$lt": val}}
        if op is sa_ops.in_op:
            return {col: {"$in": list(val) if val else []}}
        if op is sa_ops.not_in_op:
            return {col: {"$nin": list(val) if val else []}}
        if op is sa_ops.ilike_op:
            regex = str(val).replace("%", ".*").replace("_", ".")
            return {col: {"$regex": regex, "$options": "i"}}
        if op is sa_ops.is_:
            return {col: val}

        # Fallback: equality
        return {col: val}

    return {}


# ────────────────────── order-by parser ──────────────────────


def _parse_order_by(clauses) -> list[tuple[str, int]]:
    sort_list: list[tuple[str, int]] = []
    for clause in clauses:
        if isinstance(clause, UnaryExpression):
            col = clause.element
            direction = -1 if clause.modifier is sa_ops.desc_op else 1
            sort_list.append((_col_name(col), direction))
        else:
            sort_list.append((_col_name(clause), 1))
    return sort_list


# ────────────────────── result wrappers ──────────────────────


class _ScalarResult:
    def __init__(self, items: list):
        self._items = items

    def all(self) -> list:
        return self._items


class MongoResult:
    """Mimics sqlalchemy.engine.Result for MongoDB query output."""

    def __init__(self, items: list, *, is_scalar: bool = False, raw_rows: bool = False):
        self._items = items
        self._is_scalar = is_scalar
        self._raw_rows = raw_rows

    def scalars(self) -> _ScalarResult:
        return _ScalarResult(self._items)

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalar(self):
        if not self._items:
            return None
        return self._items[0]

    def all(self) -> list:
        """Return raw row tuples (for GROUP BY queries)."""
        return self._items


# ────────────────────── auto-increment ──────────────────────


async def _next_id(db, collection_name: str) -> int:
    """Thread-safe auto-incrementing integer id."""
    doc = await db["_counters"].find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return doc["seq"]


# ────────────────────── MongoSession ──────────────────────


class MongoSession:
    """Drop-in replacement for SQLAlchemy AsyncSession backed by Motor/MongoDB.

    Supports the subset of AsyncSession API used across all SmartShiksha routers.
    """

    def __init__(self, db):
        self.db = db
        self._pending_adds: list = []
        self._pending_deletes: list = []
        self._tracked: list = []  # objects returned from queries (for dirty checking)
        self._snapshots: dict[int, dict] = {}  # id(obj) → snapshot at query time

    # ── query ──

    async def execute(self, stmt):
        if isinstance(stmt, Select):
            return await self._exec_select(stmt)
        raise NotImplementedError(f"MongoSession.execute does not support {type(stmt).__name__}")

    async def _exec_select(self, stmt: Select):
        descs = stmt.column_descriptions

        # Detect aggregate functions (func.count / func.avg / func.sum)
        has_func = any(isinstance(d.get("expr"), Function) for d in descs)
        has_model = any(d.get("entity") is not None for d in descs)

        if has_func and not has_model:
            return await self._exec_aggregate(stmt, descs)
        if has_func and has_model:
            # Mixed: e.g. select(Model.col, func.count()).group_by(...)
            return await self._exec_group_by(stmt, descs)

        # Plain model select
        model_class = descs[0]["entity"] if descs else None
        if model_class is None:
            froms = list(stmt.froms)
            if froms and hasattr(froms[0], "__tablename__"):
                model_class = froms[0]
        if model_class is None:
            return MongoResult([])

        coll_name = model_class.__tablename__
        filters = _parse_condition(stmt.whereclause)
        cursor = self.db[coll_name].find(filters)

        order_clauses = getattr(stmt, "_order_by_clauses", ())
        if order_clauses:
            cursor = cursor.sort(_parse_order_by(order_clauses))

        offset_clause = getattr(stmt, "_offset_clause", None)
        if offset_clause is not None:
            cursor = cursor.skip(_extract_value(offset_clause))

        limit_clause = getattr(stmt, "_limit_clause", None)
        limit_val = _extract_value(limit_clause) if limit_clause is not None else None
        if limit_val is not None:
            cursor = cursor.limit(limit_val)

        docs = await cursor.to_list(length=limit_val or 50_000)

        instances = []
        for doc in docs:
            obj = model_class()
            for k, v in doc.items():
                if k == "_id":
                    continue
                if hasattr(obj, k):
                    setattr(obj, k, v)
            instances.append(obj)
            # Track for dirty-checking on commit
            self._tracked.append(obj)
            self._snapshots[id(obj)] = self._obj_to_dict(obj)

        return MongoResult(instances)

    async def _exec_aggregate(self, stmt: Select, descs: list[dict]):
        """Handle select(func.count/avg/sum ...) queries."""
        func_expr: Function = descs[0]["expr"]
        func_name = func_expr.name.lower()

        # Determine collection from .select_from() or whereclause columns
        model_class = self._resolve_model(stmt)
        if model_class is None:
            return MongoResult([None], is_scalar=True)

        coll_name = model_class.__tablename__
        filters = _parse_condition(stmt.whereclause)

        if func_name == "count":
            val = await self.db[coll_name].count_documents(filters)
            return MongoResult([val], is_scalar=True)

        # avg / sum → aggregation pipeline
        if func_name in ("avg", "sum"):
            col = func_expr.clauses[0] if func_expr.clauses else None
            col_name = _col_name(col) if col else None
            if col_name is None:
                return MongoResult([None], is_scalar=True)

            mongo_op = "$avg" if func_name == "avg" else "$sum"
            pipeline = []
            if filters:
                pipeline.append({"$match": filters})
            pipeline.append({"$group": {"_id": None, "_val": {mongo_op: f"${col_name}"}}})
            docs = await self.db[coll_name].aggregate(pipeline).to_list(1)
            val = docs[0]["_val"] if docs else (0 if func_name == "sum" else None)
            return MongoResult([val], is_scalar=True)

        return MongoResult([None], is_scalar=True)

    async def _exec_group_by(self, stmt: Select, descs: list[dict]):
        """Handle select(col, func...).group_by(col) queries."""
        model_class = self._resolve_model(stmt)
        if model_class is None:
            return MongoResult([], raw_rows=True)

        coll_name = model_class.__tablename__
        filters = _parse_condition(stmt.whereclause)

        # Determine group-by column
        group_by_clauses = getattr(stmt, "_group_by_clauses", ())
        if not group_by_clauses:
            return MongoResult([], raw_rows=True)

        group_col = _col_name(group_by_clauses[0])

        # Build aggregation
        pipeline: list[dict] = []
        if filters:
            pipeline.append({"$match": filters})

        group_stage: dict = {"_id": f"${group_col}"}
        # Detect aggregate expressions in column descriptions
        for d in descs:
            expr = d.get("expr")
            if isinstance(expr, Function):
                fname = expr.name.lower()
                if fname == "count":
                    group_stage["_count"] = {"$sum": 1}
                elif fname in ("avg", "sum"):
                    agg_col = _col_name(expr.clauses[0]) if expr.clauses else None
                    mongo_op = "$avg" if fname == "avg" else "$sum"
                    group_stage[f"_{fname}"] = {mongo_op: f"${agg_col}" if agg_col else 1}

        pipeline.append({"$group": group_stage})

        # Order by
        order_clauses = getattr(stmt, "_order_by_clauses", ())
        if order_clauses:
            sort_stage: dict = {}
            for clause in order_clauses:
                if isinstance(clause, UnaryExpression):
                    inner = clause.element
                    direction = -1 if clause.modifier is sa_ops.desc_op else 1
                    if isinstance(inner, Function):
                        fname = inner.name.lower()
                        sort_stage[f"_{fname}"] = direction
                    else:
                        sort_stage[_col_name(inner)] = direction
                elif isinstance(clause, Function):
                    sort_stage[f"_{clause.name.lower()}"] = 1
                else:
                    sort_stage[_col_name(clause)] = 1
            if sort_stage:
                pipeline.append({"$sort": sort_stage})

        # Limit
        limit_clause = getattr(stmt, "_limit_clause", None)
        if limit_clause is not None:
            pipeline.append({"$limit": _extract_value(limit_clause)})

        docs = await self.db[coll_name].aggregate(pipeline).to_list(1000)

        # Convert to row tuples matching SQLAlchemy's .all() output
        rows = []
        for doc in docs:
            # First element = group key, remaining = aggregate values
            row = [doc.get("_id")]
            for d in descs:
                expr = d.get("expr")
                if isinstance(expr, Function):
                    fname = expr.name.lower()
                    row.append(doc.get(f"_{fname}", 0))
            rows.append(tuple(row))

        return MongoResult(rows, raw_rows=True)

    def _resolve_model(self, stmt: Select):
        """Extract the ORM model class from a Select statement."""
        descs = stmt.column_descriptions
        for d in descs:
            if d.get("entity"):
                return d["entity"]
            expr = d.get("expr")
            if isinstance(expr, Function) and expr.clauses:
                col = list(expr.clauses)[0]
                model = _model_from_col(col)
                if model:
                    return model
        # Try froms
        for f in stmt.froms:
            if hasattr(f, "__tablename__"):
                return f
        # Try extracting from where clause
        wc = stmt.whereclause
        if wc is not None and isinstance(wc, BinaryExpression):
            return _model_from_col(wc.left)
        return None

    # ── write operations ──

    def add(self, obj):
        self._pending_adds.append(obj)

    def add_all(self, objs):
        self._pending_adds.extend(objs)

    async def commit(self):
        # 1. Insert / upsert pending adds
        for obj in self._pending_adds:
            coll = self.db[obj.__tablename__]
            if obj.id is None:
                obj.id = await _next_id(self.db, obj.__tablename__)
            data = self._obj_to_dict(obj)
            await coll.update_one({"id": obj.id}, {"$set": data}, upsert=True)
        self._pending_adds = []

        # 2. Delete pending
        for obj in self._pending_deletes:
            coll = self.db[obj.__tablename__]
            await coll.delete_one({"id": obj.id})
        self._pending_deletes = []

        # 3. Flush dirty tracked objects
        for obj in self._tracked:
            snap = self._snapshots.get(id(obj))
            if snap is None:
                continue
            current = self._obj_to_dict(obj)
            if current != snap:
                coll = self.db[obj.__tablename__]
                await coll.update_one({"id": obj.id}, {"$set": current})
                self._snapshots[id(obj)] = current

    async def flush(self):
        await self.commit()

    async def refresh(self, obj):
        coll = self.db[obj.__tablename__]
        doc = await coll.find_one({"id": obj.id})
        if doc:
            for k, v in doc.items():
                if k == "_id":
                    continue
                if hasattr(obj, k):
                    setattr(obj, k, v)
            self._snapshots[id(obj)] = self._obj_to_dict(obj)

    async def delete(self, obj):
        self._pending_deletes.append(obj)

    # ── helpers ──

    @staticmethod
    def _obj_to_dict(obj) -> dict:
        data: dict = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.key, None)
            data[col.key] = val
        return data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass
