"""Student progress tracking router (SQLite)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.database import get_db
from app.models import Progress, StudentAttempt, Topic, Subject, Chapter
from app.routers.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/update")
async def update_progress(
    data: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update topic progress for the current user."""
    topic_id = data.get("topic_id")
    completed = data.get("completed", False)
    time_spent = data.get("time_spent_seconds", 0)

    result = await db.execute(
        select(Progress).where(
            Progress.user_id == user["id"], Progress.topic_id == topic_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.completed = completed
        existing.time_spent_seconds = (existing.time_spent_seconds or 0) + time_spent
        existing.updated_at = datetime.utcnow()
    else:
        db.add(Progress(
            user_id=user["id"],
            topic_id=topic_id,
            completed=completed,
            time_spent_seconds=time_spent,
        ))
    await db.commit()
    return {"message": "Progress updated"}


@router.get("/dashboard")
async def get_dashboard(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics for the current user."""
    uid = user["id"]

    # Topics completed
    r = await db.execute(
        select(func.count()).select_from(Progress).where(
            Progress.user_id == uid, Progress.completed == True
        )
    )
    topics_completed = r.scalar() or 0

    r = await db.execute(select(func.count()).select_from(Topic))
    total_topics = r.scalar() or 0

    # Tests taken
    r = await db.execute(
        select(func.count()).select_from(StudentAttempt).where(
            StudentAttempt.user_id == uid
        )
    )
    tests_taken = r.scalar() or 0

    # Average score
    r = await db.execute(
        select(func.avg(StudentAttempt.percentage)).where(
            StudentAttempt.user_id == uid
        )
    )
    average_score = round(r.scalar() or 0, 1)

    # Total study time
    r = await db.execute(
        select(func.sum(Progress.time_spent_seconds)).where(
            Progress.user_id == uid
        )
    )
    total_seconds = r.scalar() or 0
    total_hours = round(total_seconds / 3600, 1)

    # Subject progress
    subject_progress = {}
    subjects_r = await db.execute(select(Subject))
    for subj in subjects_r.scalars().all():
        ch_r = await db.execute(
            select(Chapter.id).where(Chapter.subject_id == subj.id)
        )
        chapter_ids = [c for c in ch_r.scalars().all()]

        if chapter_ids:
            tp_r = await db.execute(
                select(Topic.id).where(Topic.chapter_id.in_(chapter_ids))
            )
            topic_ids = [str(t) for t in tp_r.scalars().all()]
        else:
            topic_ids = []

        total_in_subject = len(topic_ids)
        if topic_ids:
            cr = await db.execute(
                select(func.count()).select_from(Progress).where(
                    Progress.user_id == uid,
                    Progress.topic_id.in_(topic_ids),
                    Progress.completed == True,
                )
            )
            completed_in_subject = cr.scalar() or 0
        else:
            completed_in_subject = 0

        pct = round(completed_in_subject / total_in_subject * 100, 1) if total_in_subject else 0
        subject_progress[subj.name or "Unknown"] = {
            "completed": completed_in_subject,
            "total": total_in_subject,
            "percentage": pct,
        }

    # Recent scores
    recent_r = await db.execute(
        select(StudentAttempt)
        .where(StudentAttempt.user_id == uid)
        .order_by(StudentAttempt.created_at.desc())
        .limit(5)
    )
    recent_scores = [
        {
            "test_id": a.test_id,
            "score": a.score,
            "percentage": a.percentage,
            "date": a.created_at.isoformat() if a.created_at else "",
        }
        for a in recent_r.scalars().all()
    ]

    # Recommended topics (uncompleted)
    completed_r = await db.execute(
        select(Progress.topic_id).where(
            Progress.user_id == uid, Progress.completed == True
        )
    )
    completed_topic_ids = [t for t in completed_r.scalars().all()]
    stmt = select(Topic)
    if completed_topic_ids:
        int_ids = []
        for tid in completed_topic_ids:
            try:
                int_ids.append(int(tid))
            except (ValueError, TypeError):
                pass
        if int_ids:
            stmt = stmt.where(Topic.id.not_in(int_ids))
    stmt = stmt.limit(3)
    rec_r = await db.execute(stmt)
    recommended = [
        {"topic_id": str(t.id), "name": t.name or "Unknown", "score": 0}
        for t in rec_r.scalars().all()
    ]

    return {
        "topics_completed": topics_completed,
        "total_topics": total_topics or 120,
        "tests_taken": tests_taken,
        "average_score": average_score,
        "total_study_time_hours": total_hours,
        "subject_progress": subject_progress,
        "recent_scores": recent_scores,
        "recommended_topics": recommended,
    }


@router.get("/topics")
async def get_topic_progress(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get progress for all topics."""
    result = await db.execute(
        select(Progress).where(Progress.user_id == user["id"])
    )
    return [
        {
            "topic_id": p.topic_id,
            "completed": p.completed,
            "time_spent_seconds": p.time_spent_seconds or 0,
        }
        for p in result.scalars().all()
    ]
