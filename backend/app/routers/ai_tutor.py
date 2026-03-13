"""AI Tutor chat router (SQLite)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from datetime import datetime

from app.database import get_db
from app.models import ChatSession, ChatMessage, Topic, Chapter, Subject
from app.routers.auth import get_current_user
from app.config import get_settings
from app.services.ai_service import generate_tutor_response, explain_textbook_paragraph

router = APIRouter(prefix="/ai-tutor", tags=["AI Tutor"])
settings = get_settings()


@router.post("/chat")
async def chat_with_tutor(
    req: dict,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat with the AI tutor."""
    message = req.get("message", "")
    session_id = req.get("session_id")
    topic_id = req.get("topic_id")
    language = req.get("language", "English")
    student_class = req.get("student_class") or user.get("student_class", "10")
    subject = req.get("subject", "General")
    topic_name = req.get("topic_name", "General")

    # Get or create session
    session = None
    if session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == int(session_id),
                ChatSession.user_id == user["id"],
            )
        )
        session = result.scalar_one_or_none()

    if not session:
        session = ChatSession(
            user_id=user["id"],
            topic_id=topic_id,
            language=language,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    session_id = str(session.id)

    # Get chat history
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == int(session_id))
        .order_by(ChatMessage.created_at)
        .limit(20)
    )
    history = result.scalars().all()
    chat_history = [{"role": m.role, "content": m.content} for m in history]

    # Try to get topic context
    if topic_id:
        t_result = await db.execute(select(Topic).where(Topic.id == int(topic_id)))
        topic_obj = t_result.scalar_one_or_none()
        if topic_obj:
            topic_name = topic_obj.name
            ch_result = await db.execute(select(Chapter).where(Chapter.id == topic_obj.chapter_id))
            chapter = ch_result.scalar_one_or_none()
            if chapter:
                s_result = await db.execute(select(Subject).where(Subject.id == chapter.subject_id))
                subj = s_result.scalar_one_or_none()
                if subj:
                    subject = subj.name

    # Generate AI response (graceful fallback when AI provider is not configured)
    if not settings.GROQ_API_KEY:
        ai_response = (
            "AI Tutor is currently running in limited mode because GROQ_API_KEY is not configured on the server. "
            "Please set GROQ_API_KEY in backend/.env and restart the backend to enable full AI responses."
        )
    else:
        try:
            ai_response = await generate_tutor_response(
                message=message,
                student_class=str(student_class),
                subject=subject,
                topic=topic_name,
                language=language,
                chat_history=chat_history[-10:],
            )
        except Exception as e:
            ai_response = f"AI service is temporarily unavailable: {str(e)}"

    # Save messages
    now = datetime.utcnow()
    db.add_all([
        ChatMessage(session_id=int(session_id), role="user", content=message, created_at=now),
        ChatMessage(session_id=int(session_id), role="assistant", content=ai_response, created_at=now),
    ])
    await db.commit()

    return {"response": ai_response, "session_id": session_id}


@router.get("/sessions")
async def get_chat_sessions(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all chat sessions for the current user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user["id"])
        .order_by(ChatSession.created_at.desc())
        .limit(20)
    )
    sessions = result.scalars().all()

    out = []
    for s in sessions:
        count_result = await db.execute(
            select(func.count()).where(ChatMessage.session_id == s.id)
        )
        msg_count = count_result.scalar() or 0

        first_user_msg_result = await db.execute(
            select(ChatMessage.content)
            .where(
                ChatMessage.session_id == s.id,
                ChatMessage.role == "user",
            )
            .order_by(ChatMessage.created_at.asc())
            .limit(1)
        )
        first_user_msg = first_user_msg_result.scalar_one_or_none()
        title = (first_user_msg or "").strip()
        if not title:
            title = f"Session {s.id}"
        elif len(title) > 36:
            title = f"{title[:36].rstrip()}..."

        out.append({
            "id": str(s.id),
            "title": title,
            "topic_id": s.topic_id,
            "language": s.language,
            "created_at": s.created_at.isoformat() if s.created_at else "",
            "message_count": msg_count,
        })
    return out


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete one chat session for the current user."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == int(session_id),
            ChatSession.user_id == user["id"],
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == int(session_id)))
    await db.delete(session)
    await db.commit()
    return {"message": "Session deleted", "session_id": str(session_id)}


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a chat session."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == int(session_id),
            ChatSession.user_id == user["id"],
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == int(session_id))
        .order_by(ChatMessage.created_at)
        .limit(100)
    )
    messages = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else "",
        }
        for m in messages
    ]


@router.post("/explain-text")
async def explain_text(
    paragraph: str,
    subject: str = "General",
    language: str = "English",
    user: dict = Depends(get_current_user),
):
    """Explain a highlighted textbook paragraph."""
    student_class = user.get("student_class", "10")
    if not settings.GROQ_API_KEY:
        return {
            "explanation": (
                "AI explanation is unavailable because GROQ_API_KEY is not configured on the server. "
                "Set GROQ_API_KEY in backend/.env and restart the backend."
            )
        }
    try:
        explanation = await explain_textbook_paragraph(
            paragraph=paragraph,
            student_class=str(student_class),
            subject=subject,
            language=language,
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
