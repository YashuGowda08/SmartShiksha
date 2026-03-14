# Smart Shiksha — AI-Powered Education Platform for Rural India

Smart Shiksha is a free, AI-powered education platform designed for Class 8–12 students in rural India. It provides personalized tutoring, mock tests, exam paper generation, and offline content access — all in multiple Indian languages.

---

## Features

| Feature | Description |
|---------|-------------|
| **AI Tutor** | Chat with "Shiksha AI" powered by Groq (LLaMA 3.3 70B) for instant explanations in English, Hindi, Kannada, Telugu, or Tamil |
| **Mock Tests** | Timed tests with auto-evaluation, per-question scoring, and performance analytics |
| **Exam Generator** | Generate custom exam papers with downloadable PDFs — choose subject, difficulty, and question types |
| **Subject Browser** | Browse CBSE/State Board curriculum organized by Subject → Chapter → Topic with AI-generated content |
| **Offline Mode** | Download lessons and quizzes to IndexedDB for use without internet |
| **Community Q&A** | Post doubts, share images, and reply to peers organized by subject |
| **Textbook Library** | Upload and browse NCERT/state board textbooks |
| **JEE/NEET Prep** | Competitive exam preparation for Class 11–12 students |
| **Progress Dashboard** | Track topics completed, test scores, study time, and per-subject progress with charts |
| **Admin Panel** | Platform statistics, question bank upload, and user management |
| **Multilingual** | Full UI translation in English, Hindi, Kannada, Telugu, and Tamil |
| **PWA Support** | Installable as a Progressive Web App with offline status indicator |

---

## Tech Stack

### Frontend
- **Framework:** Next.js 16.1.6 (App Router, Turbopack)
- **Language:** TypeScript 5
- **UI:** Tailwind CSS 4, Radix UI, Lucide Icons
- **Auth:** Clerk (NextJS SDK)
- **Charts:** Recharts 3
- **Offline:** Dexie.js (IndexedDB)
- **Markdown:** react-markdown + remark-gfm
- **HTTP:** Axios
- **PWA:** @ducanh2912/next-pwa

### Backend
- **Framework:** FastAPI 0.109.0 (Python 3.13)
- **Database:** MangoDB
- **AI:** Groq Cloud API → LLaMA 3.3 70B Versatile via LangChain
- **Auth:** Clerk JWT verification (python-jose)
- **PDF Generation:** ReportLab
- **File Uploads:** python-multipart
- **Rate Limiting:** SlowAPI

### Database Schema (15 Tables)
`users` · `subjects` · `chapters` · `topics` · `questions` · `mock_tests` · `test_questions` · `student_attempts` · `progress` · `chat_sessions` · `chat_messages` · `textbooks` · `exam_papers` · `community_posts`

---

## Project Structure

```
SmartShiksha/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # pydantic-settings config
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── models.py            # 15 ORM model classes
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── seed_data.py         # Database seeder (99 subjects, 3355 chapters)
│   │   ├── routers/
│   │   │   ├── auth.py          # Clerk auth + user registration
│   │   │   ├── subjects.py      # Subjects/Chapters/Topics CRUD
│   │   │   ├── ai_tutor.py      # AI chat with LangChain
│   │   │   ├── exams.py         # Exam paper generation (PDF)
│   │   │   ├── mock_tests.py    # Mock tests + auto-evaluation
│   │   │   ├── progress.py      # Student progress tracking
│   │   │   ├── admin.py         # Admin stats + question upload
│   │   │   ├── textbooks.py     # Textbook CRUD + file upload
│   │   │   ├── community.py     # Community posts + replies
│   │   │   └── offline.py       # Offline content download
│   │   └── services/
│   │       ├── ai_service.py    # Groq LLM integration
│   │       └── pdf_service.py   # PDF report generation
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout with ClerkProvider
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── (app)/           # Protected app routes
│   │   │   │   ├── layout.tsx   # Sidebar, nav, user init
│   │   │   │   ├── dashboard/   # Progress dashboard
│   │   │   │   ├── subjects/    # Subject browser
│   │   │   │   ├── ai-tutor/    # AI chat interface
│   │   │   │   ├── mock-tests/  # Mock test listing + test-taking
│   │   │   │   ├── exam-generator/ # Custom exam paper creator
│   │   │   │   ├── community/   # Community Q&A forum
│   │   │   │   ├── textbooks/   # Textbook library
│   │   │   │   ├── offline/     # Offline content manager
│   │   │   │   ├── admin/       # Admin dashboard
│   │   │   │   ├── jee-neet/    # Competitive exam prep
│   │   │   │   └── profile/     # User profile settings
│   │   │   ├── onboarding/      # Class/board/language selection
│   │   │   ├── sign-in/         # Clerk sign-in
│   │   │   └── sign-up/         # Clerk sign-up
│   │   ├── lib/
│   │   │   ├── api.ts           # Axios API client (9 service modules)
│   │   │   ├── i18n.ts          # Translation system (5 languages)
│   │   │   └── offline-db.ts    # Dexie IndexedDB schema
│   │   ├── contexts/
│   │   │   ├── LanguageContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   ├── components/
│   │   │   └── OfflineStatus.tsx
│   │   └── middleware.ts        # Clerk route protection
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
├── database/
│   └── schema.sql
├── docker-compose.yml
└── .env
```

---

## Getting Started

### Prerequisites
- **Python 3.11** (recommended for backend compatibility)
- **Node.js 18+**
- **npm**

### 1. Clone the Repository
```bash
git clone https://github.com/YashuGowda08/SmartShiksha.git
cd SmartShiksha
```

### 2. Backend Setup
```bash
python -m venv .venv311
.venv311\Scripts\activate
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=sqlite+aiosqlite:///./smart_shiksha.db
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
CLERK_SECRET_KEY=your_clerk_secret_key
ALLOWED_ORIGINS=http://localhost:3000
DEBUG=true
```

Seed the database and start the server:
```bash
python -m app.seed_data
..\.venv311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

Start the development server:
```bash
npm run dev
```

### 4. Open in Browser
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 5. Flutter (Windows) Setup
```bash
cd mobile
flutter pub get
flutter analyze
flutter build windows --release
```

Run the built app:
```bash
mobile\build\windows\x64\runner\Release\smart_shiksha.exe
```

---

## Current Validation Status (Mar 13, 2026)

- Backend: running on `127.0.0.1:8000`, health endpoint returns healthy.
- Website: running on `127.0.0.1:3000` with Clerk-enabled auth routes (`/sign-in`, `/mobile-auth`).
- Flutter Windows app: builds and launches successfully (`smart_shiksha.exe`).
- Frontend production build: passes (`next build` successful).
- Flutter static analysis: passes (`No issues found`).

### Notes

- Backend dependency set is currently incompatible with Python 3.13 in this workspace; use the project-local Python 3.11 virtual environment (`.venv311`) for backend runs.
- Some frontend accessibility/style diagnostics remain as non-blocking code quality warnings and do not prevent runtime.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register user from Clerk |
| `GET` | `/api/v1/auth/me` | Get current user profile |
| `PATCH` | `/api/v1/auth/me` | Update user profile |
| `POST` | `/api/v1/auth/onboarding` | Complete onboarding |
| `GET` | `/api/v1/content/subjects` | List all subjects |
| `GET` | `/api/v1/content/subjects/{id}/chapters` | Get chapters for a subject |
| `GET` | `/api/v1/content/chapters/{id}/topics` | Get topics for a chapter |
| `GET` | `/api/v1/content/topics/{id}` | Get topic details |
| `POST` | `/api/v1/ai-tutor/chat` | Chat with AI tutor |
| `GET` | `/api/v1/mock-tests/` | List mock tests |
| `GET` | `/api/v1/mock-tests/{id}` | Get test with questions |
| `POST` | `/api/v1/mock-tests/{id}/submit` | Submit test answers |
| `POST` | `/api/v1/exams/generate` | Generate exam paper (PDF) |
| `GET` | `/api/v1/progress/dashboard` | Get student dashboard stats |
| `POST` | `/api/v1/progress/update` | Update topic progress |
| `GET` | `/api/v1/community/posts` | List community posts |
| `POST` | `/api/v1/community/posts` | Create a post |
| `GET` | `/api/v1/textbooks/` | List textbooks |
| `GET` | `/api/v1/admin/stats` | Get platform statistics |
| `GET` | `/api/v1/offline/lessons` | Download lessons bundle |
| `GET` | `/api/v1/offline/quizzes` | Download quizzes bundle |

---

## Seeded Data

The `seed_data.py` script populates the database with:
- **99 subjects** across Classes 8–12 (CBSE)
- **3,355 chapters** with descriptions
- **39 mock tests** (Chapter Tests, Mock Tests, JEE, NEET)
- **390 test questions** with correct answers
- **1 admin user**

---

## Supported Languages

| Language | Native Name |
|----------|-------------|
| English | English |
| Hindi | हिन्दी |
| Kannada | ಕನ್ನಡ |
| Telugu | తెలుగు |
| Tamil | தமிழ் |

---

## License

This project is open source and available for educational purposes.

---

## Authors

- **YashuGowda08** — [GitHub](https://github.com/YashuGowda08)
