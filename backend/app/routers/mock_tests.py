"""Mock test CRUD and evaluation router (SQLite)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import MockTest, TestQuestion, StudentAttempt
from app.routers.auth import get_current_user

router = APIRouter(prefix="/mock-tests", tags=["Mock Tests"])


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
async def list_tests(
    test_type: Optional[str] = None,
    student_class: Optional[str] = None,
    subject_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List available mock tests."""
    stmt = select(MockTest).where(MockTest.is_active == True)
    if test_type:
        stmt = stmt.where(MockTest.test_type == test_type)
    if student_class:
        stmt = stmt.where(MockTest.student_class == student_class)
    if subject_name:
        stmt = stmt.where(MockTest.subject_name == subject_name)
    stmt = stmt.order_by(MockTest.created_at.desc())
    result = await db.execute(stmt)
    tests = result.scalars().all()
    return [serialize_model(t) for t in tests]


@router.get("/{test_id}")
async def get_test(test_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific test with its questions."""
    result = await db.execute(select(MockTest).where(MockTest.id == int(test_id)))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    q_result = await db.execute(
        select(TestQuestion)
        .where(TestQuestion.test_id == int(test_id))
        .order_by(TestQuestion.order_index)
    )
    questions = q_result.scalars().all()

    test_data = serialize_model(test)
    test_data["questions"] = [serialize_model(q) for q in questions]
    return test_data


@router.post("/")
async def create_test(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new mock test (admin only)."""
    test = MockTest(
        title=data.get("title", ""),
        description=data.get("description", ""),
        test_type=data.get("test_type", "Chapter Test"),
        student_class=data.get("student_class"),
        subject_name=data.get("subject_name"),
        duration_minutes=data.get("duration_minutes", 60),
        total_marks=data.get("total_marks", 100),
        question_count=data.get("question_count", 10),
        is_active=True,
    )
    db.add(test)
    await db.commit()
    await db.refresh(test)

    if "questions" in data:
        for i, q_data in enumerate(data["questions"]):
            tq = TestQuestion(
                test_id=test.id,
                question_text=q_data.get("question_text", ""),
                question_type=q_data.get("question_type", "MCQ"),
                options=q_data.get("options", []),
                correct_answer=q_data.get("correct_answer", ""),
                marks=q_data.get("marks", 1),
                order_index=i,
            )
            db.add(tq)
        await db.commit()

    return serialize_model(test)


@router.post("/{test_id}/submit")
async def submit_test(
    test_id: str,
    req: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a test attempt and auto-evaluate."""
    result = await db.execute(select(MockTest).where(MockTest.id == int(test_id)))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    answers = req.get("answers", [])
    time_taken = req.get("time_taken_seconds", 0)
    proctoring_warnings = req.get("proctoring_warnings", 0)
    auto_submitted = req.get("auto_submitted", False)

    total_score = 0
    total_marks = 0
    evaluated_answers = []

    for answer in answers:
        q_id = answer.get("question_id")
        student_ans = answer.get("student_answer", "")

        question = None
        if q_id:
            try:
                q_result = await db.execute(select(TestQuestion).where(TestQuestion.id == int(q_id)))
                question = q_result.scalar_one_or_none()
            except (ValueError, TypeError):
                pass

        if not question:
            evaluated_answers.append({
                "question_id": q_id,
                "student_answer": student_ans,
                "is_correct": False,
                "marks_obtained": 0,
            })
            total_marks += 1
            continue

        marks = question.marks or 1
        total_marks += marks
        correct_answer = question.correct_answer or ""
        is_correct = student_ans.strip().lower() == correct_answer.strip().lower() if correct_answer else False
        marks_obtained = marks if is_correct else 0
        total_score += marks_obtained

        evaluated_answers.append({
            "question_id": q_id,
            "student_answer": student_ans,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "marks_obtained": marks_obtained,
        })

    percentage = (total_score / total_marks * 100) if total_marks > 0 else 0

    attempt = StudentAttempt(
        user_id=user["id"],
        test_id=test_id,
        score=total_score,
        total_marks=total_marks,
        percentage=round(percentage, 1),
        time_taken_seconds=time_taken,
        proctoring_warnings=proctoring_warnings,
        auto_submitted=auto_submitted,
        answers=evaluated_answers,
        completed_at=datetime.utcnow(),
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    return {
        "attempt_id": str(attempt.id),
        "score": total_score,
        "total_marks": total_marks,
        "percentage": round(percentage, 1),
        "time_taken_seconds": time_taken,
        "proctoring_warnings": proctoring_warnings,
        "auto_submitted": auto_submitted,
    }


@router.get("/{test_id}/attempts")
async def get_test_attempts(
    test_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all attempts for a test by the current user."""
    result = await db.execute(
        select(StudentAttempt)
        .where(StudentAttempt.user_id == user["id"], StudentAttempt.test_id == test_id)
        .order_by(StudentAttempt.created_at.desc())
    )
    attempts = result.scalars().all()
    return [serialize_model(a) for a in attempts]


@router.get("/my/attempts")
async def get_my_attempts(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all test attempts for the current user."""
    result = await db.execute(
        select(StudentAttempt)
        .where(StudentAttempt.user_id == user["id"])
        .order_by(StudentAttempt.created_at.desc())
        .limit(30)
    )
    attempts = result.scalars().all()
    return [serialize_model(a) for a in attempts]
