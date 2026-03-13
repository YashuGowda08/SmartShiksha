"""Offline content download endpoints — bundles lessons and quizzes as JSON."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Subject, Chapter, Topic, MockTest, TestQuestion

router = APIRouter(prefix="/offline", tags=["Offline"])


def serialize_model(obj) -> dict:
    if not obj:
        return None
    d = {}
    for c in obj.__table__.columns:
        val = getattr(obj, c.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        d[c.name] = val
    d["id"] = str(d.pop("id"))
    return d


@router.get("/lessons")
async def download_lessons(
    student_class: Optional[str] = Query(None),
    board: Optional[str] = Query(None),
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Download lessons (subjects → chapters → topics) as a single JSON bundle
    for offline caching in the frontend IndexedDB."""
    # Filter subjects
    stmt = select(Subject)
    if subject_id:
        stmt = stmt.where(Subject.id == subject_id)
    if board:
        stmt = stmt.where(Subject.board == board)
    result = await db.execute(stmt)
    subjects = result.scalars().all()

    bundle = []
    for subj in subjects:
        # If student_class filter is set, check the JSON classes list
        if student_class and subj.classes:
            if student_class not in subj.classes:
                continue

        subj_data = serialize_model(subj)

        # Get chapters
        ch_stmt = select(Chapter).where(Chapter.subject_id == subj.id)
        if student_class:
            ch_stmt = ch_stmt.where(Chapter.student_class == student_class)
        ch_stmt = ch_stmt.order_by(Chapter.order_index)
        ch_result = await db.execute(ch_stmt)
        chapters = ch_result.scalars().all()

        subj_data["chapters"] = []
        for ch in chapters:
            ch_data = serialize_model(ch)

            # Get topics
            tp_result = await db.execute(
                select(Topic)
                .where(Topic.chapter_id == ch.id)
                .order_by(Topic.order_index)
            )
            ch_data["topics"] = [serialize_model(t) for t in tp_result.scalars().all()]
            subj_data["chapters"].append(ch_data)

        bundle.append(subj_data)

    return {"lessons": bundle, "downloaded_at": datetime.utcnow().isoformat()}


@router.get("/quizzes")
async def download_quizzes(
    student_class: Optional[str] = Query(None),
    test_type: Optional[str] = Query(None),
    subject_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Download mock tests with their questions as a single JSON bundle
    for offline caching in the frontend IndexedDB."""
    stmt = select(MockTest).where(MockTest.is_active == True)
    if student_class:
        stmt = stmt.where(MockTest.student_class == student_class)
    if test_type:
        stmt = stmt.where(MockTest.test_type == test_type)
    if subject_name:
        stmt = stmt.where(MockTest.subject_name == subject_name)
    stmt = stmt.order_by(MockTest.created_at.desc())
    result = await db.execute(stmt)
    tests = result.scalars().all()

    bundle = []
    for test in tests:
        test_data = serialize_model(test)

        q_result = await db.execute(
            select(TestQuestion)
            .where(TestQuestion.test_id == test.id)
            .order_by(TestQuestion.order_index)
        )
        test_data["questions"] = [serialize_model(q) for q in q_result.scalars().all()]
        bundle.append(test_data)

    return {"quizzes": bundle, "downloaded_at": datetime.utcnow().isoformat()}
