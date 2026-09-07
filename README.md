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

### 1. Backend Setup
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
# Copy .env.example to .env and set your GEMINI_API_KEY (or OPENROUTER_API_KEY)
copy .env.example .env

# Run FastAPI backend
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

Run backend tests from the `backend/` folder:
```bash
# Test Authentication & JWT flow
python test_auth.py

# Test Document Ingestion & AI SSE Streaming
python test_doc_upload.py

# Test Full-Stack Integration
python test_integration.py
```

Run frontend linting & production build:
```bash
cd frontend
npx oxlint
npm run build
```

---

## 🔒 Security
- API keys and environment files (`.env`) are excluded via `.gitignore`. Never commit `.env` to public repositories.
- Always use environment variables for sensitive tokens.
