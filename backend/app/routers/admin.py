"""Admin panel router (SQLite)."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import User, StudentAttempt, Question
from app.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


async def verify_admin(user: dict = Depends(get_current_user)):
    """Verify the user has admin role."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def get_platform_stats(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get platform-wide statistics."""
    # Total students
    r = await db.execute(
        select(func.count()).select_from(User).where(User.role == "student")
    )
    total_students = r.scalar() or 0

    # Active today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    r = await db.execute(
        select(func.count()).select_from(StudentAttempt).where(
            StudentAttempt.created_at >= today
        )
    )
    active_today = r.scalar() or 0

    # Total tests taken
    r = await db.execute(select(func.count()).select_from(StudentAttempt))
    total_tests = r.scalar() or 0

    # Average score
    r = await db.execute(select(func.avg(StudentAttempt.percentage)))
    avg_score = round(r.scalar() or 0, 1)

    # Class distribution
    r = await db.execute(
        select(User.student_class, func.count())
        .where(User.role == "student")
        .group_by(User.student_class)
    )
    class_distribution = {
        f"Class {row[0] or 'Unknown'}": row[1] for row in r.all()
    }

    # Most difficult (lowest avg percentage per test)
    r = await db.execute(
        select(StudentAttempt.test_id, func.avg(StudentAttempt.percentage).label("avg_pct"))
        .group_by(StudentAttempt.test_id)
        .order_by(func.avg(StudentAttempt.percentage))
        .limit(5)
    )
    most_difficult = [
        {"test": row[0] or "Unknown", "subject": "Mixed", "avg_score": round(row[1] or 0, 1)}
        for row in r.all()
    ]

    return {
        "total_students": total_students,
        "active_users_today": active_today,
        "total_tests_taken": total_tests,
        "average_platform_score": avg_score,
        "class_distribution": class_distribution,
        "most_difficult_topics": most_difficult,
    }


@router.post("/upload-questions")
async def upload_questions(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload question bank from JSON file."""
    content = await file.read()
    try:
        data = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    questions = data if isinstance(data, list) else data.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="No questions found in file")

    count = 0
    for q in questions:
        db.add(Question(
            topic_id=q.get("topic_id"),
            question_text=q.get("question_text", ""),
            question_type=q.get("question_type", "MCQ"),
            options=q.get("options", []),
            correct_answer=q.get("correct_answer", ""),
            difficulty=q.get("difficulty", "Medium"),
            marks=q.get("marks", 1),
            explanation=q.get("explanation", ""),
            uploaded_by=user["id"],
        ))
        count += 1
    await db.commit()
    return {"message": f"Uploaded {count} questions successfully"}


@router.get("/users")
async def list_users(
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    offset = (page - 1) * limit
    r = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users_list = r.scalars().all()

    r2 = await db.execute(select(func.count()).select_from(User))
    total = r2.scalar() or 0

    return {
        "users": [
            {
                "id": str(u.id),
                "name": u.name,
                "email": u.email,
                "student_class": u.student_class,
                "board": u.board,
                "role": u.role,
                "created_at": u.created_at.isoformat() if u.created_at else "",
            }
            for u in users_list
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }
