"""Community Chatting Router — Posts and Replies (SQLite)."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import os
import shutil

from app.database import get_db
from app.models import CommunityPost
from app.routers.auth import get_current_user

router = APIRouter(prefix="/community", tags=["Community"])


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


@router.get("/posts")
async def get_posts(
    subject: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all community posts with pagination."""
    stmt = select(CommunityPost).where(CommunityPost.parent_id == None)
    if subject and subject != "General":
        stmt = stmt.where(CommunityPost.subject == subject)
    stmt = stmt.order_by(CommunityPost.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [serialize_model(p) for p in result.scalars().all()]


@router.post("/posts")
async def create_post(
    content: str = Form(...),
    subject: str = Form("General"),
    topic: str = Form("General"),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new community post with optional image."""
    image_url = None
    if image:
        os.makedirs("uploads/community", exist_ok=True)
        file_path = f"uploads/community/{datetime.utcnow().timestamp()}_{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/uploads/community/{os.path.basename(file_path)}"

    post = CommunityPost(
        author_id=user["id"],
        author_name=user["name"],
        author_avatar=user.get("avatar_url"),
        content=content,
        image_url=image_url,
        subject=subject,
        topic=topic,
        parent_id=None,
        replies_count=0,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return serialize_model(post)


@router.get("/posts/{post_id}/replies")
async def get_replies(post_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch all replies for a specific post."""
    result = await db.execute(
        select(CommunityPost)
        .where(CommunityPost.parent_id == int(post_id))
        .order_by(CommunityPost.created_at)
    )
    return [serialize_model(r) for r in result.scalars().all()]


@router.post("/posts/{post_id}/replies")
async def create_reply(
    post_id: str,
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a community post."""
    result = await db.execute(
        select(CommunityPost).where(CommunityPost.id == int(post_id))
    )
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent post not found")

    image_url = None
    if image:
        os.makedirs("uploads/community", exist_ok=True)
        file_path = f"uploads/community/{datetime.utcnow().timestamp()}_{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/uploads/community/{os.path.basename(file_path)}"

    reply = CommunityPost(
        author_id=user["id"],
        author_name=user["name"],
        author_avatar=user.get("avatar_url"),
        content=content,
        image_url=image_url,
        parent_id=int(post_id),
    )
    db.add(reply)

    parent.replies_count = (parent.replies_count or 0) + 1

    await db.commit()
    await db.refresh(reply)
    return serialize_model(reply)
