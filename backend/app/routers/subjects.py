"""Subjects, Chapters, Topics CRUD router (SQLite)."""
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models import Subject, Chapter, Topic, Question
from app.services.ai_service import generate_topic_content

router = APIRouter(prefix="/content", tags=["Content"])


def _extract_topic_content(explanation: str, examples: str) -> tuple[str, str]:
    """Normalize AI topic payloads where explanation may contain a JSON object."""
    exp = (explanation or "").strip()
    exm = (examples or "").strip()

    if exp.startswith("{") and '"explanation"' in exp:
        try:
            parsed = json.loads(exp)
            if isinstance(parsed, dict):
                exp = str(parsed.get("explanation") or exp).strip()
                if not exm or exm == "Example problems coming soon...":
                    exm = str(parsed.get("examples") or exm).strip()
        except Exception:
            pass

    return exp, exm


def _is_placeholder_examples(value: str) -> bool:
    v = (value or "").strip().lower()
    return not v or v in {
        "example problems coming soon...",
        "detailed content coming soon...",
    }


def serialize_model(obj) -> dict:
    """Convert a SQLAlchemy model instance to a JSON-safe dict."""
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


# ── Subjects ───────────────────────────────────────────────────────────

@router.get("/subjects")
async def get_subjects(
    student_class: Optional[str] = Query(None),
    board: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all subjects, optionally filtered by class and board."""
    stmt = select(Subject)
    if board:
        stmt = stmt.where(Subject.board == board)
    result = await db.execute(stmt)
    subjects = result.scalars().all()
    out = []
    for s in subjects:
        d = serialize_model(s)
        if student_class and student_class not in (d.get("classes") or []):
            continue
        out.append(d)
    return out


@router.get("/subjects/{subject_id}")
async def get_subject(subject_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single subject by ID."""
    result = await db.execute(select(Subject).where(Subject.id == int(subject_id)))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return serialize_model(subject)


@router.post("/subjects")
async def create_subject(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new subject (admin only)."""
    subject = Subject(
        name=data.get("name", ""),
        description=data.get("description", ""),
        icon=data.get("icon", "📚"),
        color=data.get("color", "#6366f1"),
        classes=data.get("classes", []),
        board=data.get("board", "CBSE"),
    )
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return serialize_model(subject)


# ── Chapters ───────────────────────────────────────────────────────────

@router.get("/subjects/{subject_id}/chapters")
async def get_chapters(
    subject_id: str,
    student_class: Optional[str] = Query(None),
    board: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all chapters for a subject."""
    stmt = select(Chapter).where(Chapter.subject_id == int(subject_id)).order_by(Chapter.order_index)
    if student_class:
        stmt = stmt.where(Chapter.student_class == student_class)
    if board:
        stmt = stmt.where(Chapter.board == board)
    result = await db.execute(stmt)
    chapters = result.scalars().all()
    return [serialize_model(c) for c in chapters]


@router.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single chapter."""
    result = await db.execute(select(Chapter).where(Chapter.id == int(chapter_id)))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return serialize_model(chapter)


@router.post("/chapters")
async def create_chapter(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new chapter (admin only)."""
    chapter = Chapter(
        subject_id=int(data["subject_id"]),
        student_class=data.get("student_class"),
        board=data.get("board"),
        name=data.get("name", ""),
        description=data.get("description", ""),
        order_index=data.get("order_index", 0),
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return serialize_model(chapter)


# ── Topics ─────────────────────────────────────────────────────────────

@router.get("/chapters/{chapter_id}/topics")
async def get_topics(chapter_id: str, db: AsyncSession = Depends(get_db)):
    """Get all topics for a chapter with auto-discovery."""
    result = await db.execute(
        select(Topic).where(Topic.chapter_id == int(chapter_id)).order_by(Topic.order_index)
    )
    topics = result.scalars().all()

    if not topics:
        ch_result = await db.execute(select(Chapter).where(Chapter.id == int(chapter_id)))
        chapter = ch_result.scalar_one_or_none()
        if chapter:
            defaults = [
                (f"Introduction to {chapter.name}", 0),
                (f"Core Concepts of {chapter.name}", 1),
                (f"Practice & Applications: {chapter.name}", 2),
            ]
            for name, idx in defaults:
                t = Topic(
                    chapter_id=int(chapter_id),
                    name=name,
                    explanation="Detailed content coming soon...",
                    examples="Example problems coming soon...",
                    order_index=idx,
                )
                db.add(t)
            await db.commit()
            result = await db.execute(
                select(Topic).where(Topic.chapter_id == int(chapter_id)).order_by(Topic.order_index)
            )
            topics = result.scalars().all()

    return [serialize_model(t) for t in topics]


@router.get("/topics/{topic_id}")
async def get_topic(
    topic_id: str,
    language: str = "English",
    db: AsyncSession = Depends(get_db),
):
    """Get a single topic with dynamic generation if needed."""
    result = await db.execute(select(Topic).where(Topic.id == int(topic_id)))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.explanation, topic.examples = _extract_topic_content(topic.explanation, topic.examples)

    if (
        not topic.explanation
        or topic.explanation == "Detailed content coming soon..."
        or _is_placeholder_examples(topic.examples)
    ):
        ch_result = await db.execute(select(Chapter).where(Chapter.id == topic.chapter_id))
        chapter = ch_result.scalar_one_or_none()
        sub_result = await db.execute(select(Subject).where(Subject.id == chapter.subject_id))
        subject = sub_result.scalar_one_or_none()

        content = await generate_topic_content(
            student_class=chapter.student_class,
            subject=subject.name,
            chapter=chapter.name,
            topic=topic.name,
            language=language,
        )

        topic.explanation = content.get("explanation", "")
        topic.examples = content.get("examples", "")
        topic.explanation, topic.examples = _extract_topic_content(topic.explanation, topic.examples)

        if _is_placeholder_examples(topic.examples):
            topic.examples = (
                "1. Identify 3 rational numbers between 1/2 and 3/4.\n"
                "2. Convert 0.125 into a rational number in simplest form.\n"
                "3. Solve: 2/3 + 5/6.\n"
                "4. Solve: 7/8 - 3/4."
            )

        topic.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(topic)

    return serialize_model(topic)


@router.post("/topics")
async def create_topic(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new topic (admin only)."""
    topic = Topic(
        chapter_id=int(data["chapter_id"]),
        name=data.get("name", ""),
        explanation=data.get("explanation", ""),
        examples=data.get("examples", ""),
        order_index=data.get("order_index", 0),
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return serialize_model(topic)


# ── Questions ──────────────────────────────────────────────────────────

@router.get("/topics/{topic_id}/questions")
async def get_questions(
    topic_id: str,
    question_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get questions for a topic."""
    stmt = select(Question).where(Question.topic_id == topic_id)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
    result = await db.execute(stmt)
    questions = result.scalars().all()
    if questions:
        return [serialize_model(q) for q in questions]

    # Fallback practice set so Practice tab is never blank for active topics.
    t_result = await db.execute(select(Topic).where(Topic.id == int(topic_id)))
    topic = t_result.scalar_one_or_none()
    topic_name = topic.name if topic else "this topic"

    return [
        {
            "id": "tmp-1",
            "topic_id": str(topic_id),
            "question_text": f"Which of the following is a rational number in {topic_name}?",
            "question_type": "MCQ",
            "options": ["sqrt(2)", "pi", "3/4", "sqrt(5)"],
            "correct_answer": "3/4",
            "difficulty": "Easy",
            "marks": 1,
            "explanation": "A rational number can be written as p/q where p and q are integers and q != 0.",
        },
        {
            "id": "tmp-2",
            "topic_id": str(topic_id),
            "question_text": f"Compute: 2/3 + 1/6 in {topic_name}.",
            "question_type": "MCQ",
            "options": ["1/2", "5/6", "4/5", "1"],
            "correct_answer": "5/6",
            "difficulty": "Easy",
            "marks": 1,
            "explanation": "LCM of 3 and 6 is 6. So 2/3 = 4/6, then 4/6 + 1/6 = 5/6.",
        },
        {
            "id": "tmp-3",
            "topic_id": str(topic_id),
            "question_text": f"Which statement is true about rational numbers in {topic_name}?",
            "question_type": "MCQ",
            "options": [
                "Denominator can be zero",
                "Every integer is rational",
                "pi is rational",
                "sqrt(3) is rational",
            ],
            "correct_answer": "Every integer is rational",
            "difficulty": "Medium",
            "marks": 1,
            "explanation": "Any integer n can be written as n/1, so every integer is rational.",
        },
    ]


@router.post("/questions")
async def create_question(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new question (admin only)."""
    q = Question(
        topic_id=data.get("topic_id", ""),
        question_text=data.get("question_text", ""),
        question_type=data.get("question_type", "MCQ"),
        options=data.get("options", []),
        correct_answer=data.get("correct_answer", ""),
        difficulty=data.get("difficulty", "Medium"),
        marks=data.get("marks", 1),
    )
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return serialize_model(q)


@router.post("/questions/bulk")
async def create_questions_bulk(questions: List[dict], db: AsyncSession = Depends(get_db)):
    """Bulk create questions (admin only)."""
    objs = []
    for data in questions:
        q = Question(
            topic_id=data.get("topic_id", ""),
            question_text=data.get("question_text", ""),
            question_type=data.get("question_type", "MCQ"),
            options=data.get("options", []),
            correct_answer=data.get("correct_answer", ""),
            difficulty=data.get("difficulty", "Medium"),
            marks=data.get("marks", 1),
        )
        objs.append(q)
    db.add_all(objs)
    await db.commit()
    return {"message": f"Created {len(objs)} questions"}
