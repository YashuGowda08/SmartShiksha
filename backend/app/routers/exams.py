"""Exam paper generation router (SQLite)."""
import json
import io
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models import ExamPaper, User
from app.routers.auth import get_current_user
from app.services.ai_service import generate_exam_questions
from app.services.pdf_service import create_exam_pdf

router = APIRouter(prefix="/exams", tags=["Exam Papers"])


async def get_optional_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get user if authenticated, otherwise return a guest dict."""
    try:
        if authorization and authorization.startswith("Bearer "):
            user = await get_current_user(authorization=authorization, db=db)
            return {
                "id": user["id"],
                "student_class": user.get("student_class") or "10",
                "role": user.get("role") or "student",
            }
        return {"id": "guest", "student_class": "10", "role": "student"}
    except Exception:
        return {"id": "guest", "student_class": "10", "role": "student"}


@router.post("/generate")
async def generate_paper(
    req: dict,
    user: dict = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI-powered exam paper and return as PDF."""
    student_class = req.get("student_class", user.get("student_class", "10"))
    subject_name = req.get("subject_name", "Mathematics")
    chapter_name = req.get("chapter_name", "")
    topic_name = req.get("topic_name", "")
    difficulty = req.get("difficulty", "Medium")
    question_types = req.get("question_types", ["MCQ", "Short Answer"])
    if isinstance(question_types, list):
        question_types = ", ".join(question_types)
    num_questions = min(req.get("num_questions", 20), 50)
    language = req.get("language", "English")
    test_type = req.get("test_type", "Chapter Test")

    try:
        questions_text = await generate_exam_questions(
            student_class=str(student_class),
            subject=subject_name,
            chapter=chapter_name,
            topic=topic_name,
            difficulty=difficulty,
            question_types=question_types,
            num_questions=num_questions,
            language=language,
            test_type=test_type,
        )

        try:
            if isinstance(questions_text, str):
                questions = json.loads(questions_text)
            else:
                questions = questions_text

            if isinstance(questions, dict) and "questions" in questions:
                questions = questions["questions"]
            elif isinstance(questions, dict) and any(isinstance(v, list) for v in questions.values()):
                for v in questions.values():
                    if isinstance(v, list):
                        questions = v
                        break
        except Exception:
            questions = [{
                "question_text": f"Explain the key concepts of {topic_name or chapter_name or subject_name}.",
                "question_type": "Short Answer",
                "correct_answer": "Multiple points relating to the topic.",
                "explanation": "This is a comprehensive overview question.",
                "marks": 5,
            }]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

    # Save exam paper
    paper = ExamPaper(
        user_id=user["id"],
        student_class=str(student_class),
        subject=subject_name,
        chapter=chapter_name,
        topic=topic_name,
        difficulty=difficulty,
        num_questions=len(questions),
        questions=questions,
    )
    db.add(paper)
    await db.commit()

    # Generate PDF
    pdf_bytes = create_exam_pdf(
        title=f"{subject_name} Exam Paper",
        student_class=str(student_class),
        subject=subject_name,
        questions=questions,
        test_type=test_type,
    )

    pdf_buffer = io.BytesIO(pdf_bytes)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SmartShiksha_{subject_name}_Paper.pdf"},
    )


@router.get("/my-papers")
async def get_my_papers(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all generated exam papers for the current user."""
    result = await db.execute(
        select(ExamPaper)
        .where(ExamPaper.user_id == user["id"])
        .order_by(ExamPaper.created_at.desc())
        .limit(20)
    )
    papers = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "subject": p.subject,
            "chapter": p.chapter,
            "student_class": p.student_class,
            "difficulty": p.difficulty,
            "num_questions": p.num_questions,
            "created_at": p.created_at.isoformat() if p.created_at else "",
        }
        for p in papers
    ]
