"""Textbook management router (SQLite)."""
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Textbook
from app.routers.auth import get_current_user

router = APIRouter(prefix="/textbooks", tags=["Textbooks"])


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


@router.get("/")
async def list_textbooks(
    student_class: Optional[str] = None,
    board: Optional[str] = None,
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List available textbooks with flexible filtering."""
    stmt = select(Textbook)
    if student_class and student_class != "all":
        stmt = stmt.where(Textbook.student_class == student_class)
    if board:
        stmt = stmt.where(Textbook.board == board)
    if subject:
        stmt = stmt.where(Textbook.subject.ilike(f"%{subject}%"))
    stmt = stmt.order_by(Textbook.created_at.desc())
    result = await db.execute(stmt)
    return [serialize_model(t) for t in result.scalars().all()]


@router.get("/{textbook_id}")
async def get_textbook(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific textbook."""
    result = await db.execute(select(Textbook).where(Textbook.id == int(textbook_id)))
    textbook = result.scalar_one_or_none()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    return serialize_model(textbook)


@router.post("/")
async def upload_textbook(
    title: str = Form(...),
    student_class: str = Form(...),
    board: str = Form("CBSE"),
    subject: str = Form(""),
    file: UploadFile = File(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new textbook (admin only)."""
    file_url = ""
    file_size_mb = 0.0

    if file:
        content = await file.read()
        file_size_mb = round(len(content) / (1024 * 1024), 1)
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
        file_url = f"/uploads/{file.filename}"

    tb = Textbook(
        title=title,
        student_class=student_class,
        board=board,
        subject=subject,
        file_url=file_url,
        file_size_mb=file_size_mb,
        uploaded_by=user["id"],
    )
    db.add(tb)
    await db.commit()
    await db.refresh(tb)
    return serialize_model(tb)


@router.delete("/{textbook_id}")
async def delete_textbook(
    textbook_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a textbook (admin only)."""
    result = await db.execute(select(Textbook).where(Textbook.id == int(textbook_id)))
    tb = result.scalar_one_or_none()
    if not tb:
        raise HTTPException(status_code=404, detail="Textbook not found")
    await db.delete(tb)
    await db.commit()
    return {"message": "Textbook deleted"}
