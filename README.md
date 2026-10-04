# KnowledgeAI — AI-Powered Knowledge & Productivity Platform

A full-stack, enterprise-grade AI productivity and knowledge management workspace combining interactive Markdown notes, Kanban boards, interactive knowledge graphs, and real-time LLM-grounded Copilot assistance powered by Gemini.

---

## 🚀 Features

- **Split Markdown Editor & Live Preview**: Distraction-free Markdown writing with instant live rendering, syntax highlighting, and note categorization.
- **Kanban Board**: Drag-and-drop / single-click task workflow with priorities (`Low`, `Medium`, `High`, `Urgent`), custom tags, and linked note references.
- **AI Workspace Copilot**:
  - Grounded in active notes & workspace context.
  - Streaming responses powered by Google Gemini via OpenRouter.
  - Expandable drawer with full-width reading mode.
  - Generates custom **Interview Prep** questions and answers based on uploaded documents.
  - Auto-extracts actionable checklist items into Kanban tasks with one click.
- **Interactive Knowledge Graph**: Visual semantic network connecting notes, tasks, categories, and tags.
- **Document Ingestion**: Upload `.txt`, `.md`, and `.doc` files to instantly generate knowledge bases, summaries, and action plans.
- **Customizable Theming**:
  - Dark Slate, Indigo Aura, Cyber Emerald, Midnight Amethyst, and Clean Light.
  - Single-page consolidated Account, Profile, and Appearance settings.

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: React 18, Vite, Lucide React icons, Tailwind CSS / Vanilla CSS design system.
- **Backend**: FastAPI (Python 3.11+ async), SQLAlchemy, SQLite / PostgreSQL ready.
- **AI & NLP Engine**: OpenRouter SSE streaming API (Gemini 2.5/3.5 Flash), rule-based task extractor, regex parser.
- **Authentication**: JWT token-based auth with bcrypt password hashing + guest demo mode.

---

## ⚡ Quick Start

### 0. Instant Docker Quick Start (Recommended)
Run the entire stack (PostgreSQL 16 with `pgvector`, FastAPI backend, and Vite frontend) with a single command:
```bash
docker compose up --build
```
* **Frontend**: `http://localhost:5173`
* **FastAPI Docs**: `http://localhost:8000/docs`
* **PostgreSQL + pgvector**: `localhost:5433`

### 1. Manual Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env

# Optional: Run Alembic database migrations
alembic upgrade head

# Run FastAPI backend (Auto-creates tables if PostgreSQL or SQLite fallback)
python run.py
```
Backend will start at: `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`)

### 2. Frontend Setup
```bash
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
Frontend will be live at: `http://localhost:5173`

---

## 🧪 Testing

### Automated Pytest Suite (AsyncClient)
Run the comprehensive test suite (Auth, Multi-Tenant Notes isolation, Tasks, RAG chunking & reranker) without needing a live server:
```bash
cd backend
pytest tests -v
```

### Standalone Live Integration Tests
Run tests against a running backend server (`http://127.0.0.1:8000`):
```bash
cd backend
python test_auth.py
python test_doc_upload.py
python test_integration.py
```

### Frontend Linting & Production Build
```bash
cd frontend
npx oxlint
npm run build
```

---

## 🔒 Security
- API keys and environment files (`.env`) are excluded via `.gitignore`. Never commit `.env` to public repositories.
- Always use environment variables for sensitive tokens.
