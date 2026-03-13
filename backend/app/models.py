"""SQLAlchemy ORM models for Smart Shiksha."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    clerk_id = Column(String, unique=True, nullable=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    student_class = Column(String, nullable=True)
    board = Column(String, nullable=True)
    language = Column(String, default="English")
    role = Column(String, default="student")
    onboarding_complete = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    icon = Column(String, default="📚")
    color = Column(String, default="#6366f1")
    classes = Column(JSON, default=list)
    board = Column(String, default="CBSE")
    created_at = Column(DateTime, default=datetime.utcnow)


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    student_class = Column(String, nullable=True)
    board = Column(String, nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    explanation = Column(Text, default="")
    examples = Column(Text, default="")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(String, nullable=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="MCQ")
    options = Column(JSON, default=list)
    correct_answer = Column(String, default="")
    difficulty = Column(String, default="Medium")
    marks = Column(Integer, default=1)
    explanation = Column(Text, default="")
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MockTest(Base):
    __tablename__ = "mock_tests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    test_type = Column(String, default="Chapter Test")
    student_class = Column(String, nullable=True)
    subject_name = Column(String, nullable=True)
    duration_minutes = Column(Integer, default=60)
    total_marks = Column(Integer, default=100)
    question_count = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestQuestion(Base):
    __tablename__ = "test_questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey("mock_tests.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="MCQ")
    options = Column(JSON, default=list)
    correct_answer = Column(String, default="")
    marks = Column(Integer, default=1)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentAttempt(Base):
    __tablename__ = "student_attempts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    test_id = Column(String, nullable=False)
    score = Column(Float, default=0)
    total_marks = Column(Float, default=0)
    percentage = Column(Float, default=0)
    time_taken_seconds = Column(Integer, default=0)
    proctoring_warnings = Column(Integer, default=0)
    auto_submitted = Column(Boolean, default=False)
    answers = Column(JSON, default=list)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    topic_id = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    topic_id = Column(String, nullable=True)
    language = Column(String, default="English")
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Textbook(Base):
    __tablename__ = "textbooks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    student_class = Column(String, nullable=True)
    board = Column(String, default="CBSE")
    subject = Column(String, default="")
    file_url = Column(String, default="")
    file_size_mb = Column(Float, default=0)
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExamPaper(Base):
    __tablename__ = "exam_papers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    student_class = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    chapter = Column(String, default="")
    topic = Column(String, default="")
    difficulty = Column(String, default="Medium")
    num_questions = Column(Integer, default=0)
    questions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class CommunityPost(Base):
    __tablename__ = "community_posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(String, nullable=False, index=True)
    author_name = Column(String, default="")
    author_avatar = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    subject = Column(String, default="General")
    topic = Column(String, default="General")
    parent_id = Column(Integer, nullable=True, index=True)
    replies_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
