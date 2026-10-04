import os
import sys
import asyncio
import logging

# Ensure backend root is in pythonpath
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import init_db_engine
from app.models.note import Note
from app.models.task import Task
from app.models.user import User
from app.services.auth import hash_password
from app.services.rag import index_note_chunks
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowledge_ai.seed")

INITIAL_NOTES = [
    {
        "id": "note-1",
        "title": "🧠 AI Agent Architecture & pgvector Integration",
        "category": "Architecture",
        "tags": ["AI", "pgvector", "Backend", "FastAPI"],
        "is_favorite": True,
        "content": """# 🧠 AI Agent Architecture & pgvector Integration

This document outlines the hybrid retrieval strategy combining **PostgreSQL Full-Text Search (`tsvector`)** with **vector embeddings (`pgvector`)** to power the autonomous AI agent.

---

## 1. High-Level Flow
```
User Query ──► Query Embedding
                    │
                    ▼
         Hybrid Retrieval Engine
         ├── Full-Text Search (ts_rank)
         └── Cosine Similarity (<=>)
                    │
                    ▼
         Reranked Top-K Context
                    │
                    ▼
         LangGraph Agent (Tools Execution)
```

## 2. Key Components
* **FastAPI Async Engine**: Handles non-blocking database queries with `asyncpg`.
* **Hybrid Scoring Formula**:
  $$\\text{Score} = 0.65 \\times \\text{SemanticSimilarity} + 0.35 \\times \\text{FTSScore}$$
* **Entity Extractor**: Background PyTorch lightweight model detecting action items.

## 3. Action Items
- [x] Configure PostgreSQL 16 with `pgvector` extension
- [ ] Implement async connection pool in FastAPI
- [ ] Create LangGraph workflow with tool-calling for task dispatch
- [ ] Benchmark cosine distance lookup on 50,000 note chunks
"""
    },
    {
        "id": "note-2",
        "title": "⚡ Sprint 24 Planning: Autonomous Task Extraction",
        "category": "Productivity",
        "tags": ["Sprint", "Planning", "Tasks", "NLP"],
        "is_favorite": True,
        "content": """# ⚡ Sprint 24 Planning: Autonomous Task Extraction

Meeting with engineering & product team to finalize the real-time action extractor.

## Objectives
1. Automatically detect `TODO:` and action-oriented verbs when user types in the Markdown editor.
2. Provide a 1-click **"Extract Tasks to Kanban"** action in the AI Assistant Drawer.

## Proposed Pipeline
| Stage | Tech Stack | Target Latency |
| :--- | :--- | :--- |
| **Debounced Trigger** | React hook (800ms) | < 10ms |
| **Token Classification** | Local PyTorch NLP Worker | < 45ms |
| **Candidate Parsing** | Regex & Heuristics | < 5ms |

## Critical Deadlines
- **Design Review**: Wednesday 2:00 PM
- **Frontend Mock Integration**: Friday 5:00 PM
- **Backend API Handshake**: Next Monday
"""
    },
    {
        "id": "note-3",
        "title": "🎨 Frontend Design System & Glassmorphism Guidelines",
        "category": "Design",
        "tags": ["UI", "Tailwind", "DesignSystem"],
        "is_favorite": False,
        "content": """# 🎨 Frontend Design System Guidelines

Aesthetic guidelines for dark-mode first, glassmorphic UI.

### Color Tokens
- **Background Root**: `#090d16` (Dark Cosmic)
- **Glass Card Fill**: `rgba(30, 41, 59, 0.55)`
- **Accent Glow**: `#6366f1` (Indigo) / `#8b5cf6` (Violet)
- **Success Glow**: `#10b981` (Emerald)

### Micro-interactions
> Every interactive element must have hover elevation, subtle border lighting, and keyboard accessibility.
"""
    }
]

INITIAL_TASKS = [
    {
        "id": "task-1",
        "title": "Implement LangGraph tool-calling for task dispatch",
        "description": "Allow AI agent to autonomously create and update tasks in PostgreSQL when instructed in chat.",
        "status": "in_progress",
        "priority": "urgent",
        "due_date": "2026-09-10",
        "linked_note_id": "note-1",
        "linked_note_title": "🧠 AI Agent Architecture",
        "tags": ["AI", "Backend"]
    },
    {
        "id": "task-2",
        "title": "Benchmark pgvector cosine similarity lookup",
        "description": "Run latency and recall benchmarks across synthetic note vectors.",
        "status": "todo",
        "priority": "high",
        "due_date": "2026-09-12",
        "linked_note_id": "note-1",
        "linked_note_title": "🧠 AI Agent Architecture",
        "tags": ["pgvector", "Database"]
    },
    {
        "id": "task-3",
        "title": "Design interactive AI action confirmation cards",
        "description": "Create preview widgets in AI Drawer so user can approve extracted tasks before board insertion.",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-09-08",
        "linked_note_id": "note-2",
        "linked_note_title": "⚡ Sprint 24 Planning",
        "tags": ["UI", "React"]
    },
    {
        "id": "task-4",
        "title": "Setup PostgreSQL schema & vector extension",
        "description": "Initial migration script with notes and tasks.",
        "status": "done",
        "priority": "medium",
        "due_date": "2026-09-05",
        "linked_note_id": "note-1",
        "linked_note_title": "🧠 AI Agent Architecture",
        "tags": ["Database"]
    }
]

async def seed():
    session_maker = await init_db_engine()
    async with session_maker() as db:
        # 1. Ensure default admin user exists
        res = await db.execute(select(User).where(User.id == "user-demo-admin"))
        demo_user = res.scalar_one_or_none()
        if not demo_user:
            demo_user = User(
                id="user-demo-admin",
                email="admin@knowledgeai.internal",
                full_name="System Admin",
                hashed_password=hash_password("admin123")
            )
            db.add(demo_user)
            await db.commit()
            logger.info("Seeded default admin user (user-demo-admin).")
        
        # 2. Check existing notes
        res = await db.execute(select(Note))
        existing_notes = res.scalars().all()
        if not existing_notes:
            logger.info("Seeding initial notes and indexing document chunks...")
            for n_data in INITIAL_NOTES:
                note = Note(
                    id=n_data["id"],
                    user_id=demo_user.id,
                    title=n_data["title"],
                    content=n_data["content"],
                    category=n_data["category"],
                    tags=n_data["tags"],
                    is_favorite=n_data["is_favorite"],
                    embedding=None
                )
                db.add(note)
            await db.commit()

            # Index semantic chunks with pgvector embeddings
            for n_data in INITIAL_NOTES:
                await index_note_chunks(db, n_data["id"], n_data["content"])

            logger.info(f"Seeded and chunk-indexed {len(INITIAL_NOTES)} notes.")
        else:
            logger.info(f"Database already contains {len(existing_notes)} notes. Skipping notes seed.")

        # 3. Check existing tasks
        res = await db.execute(select(Task))
        existing_tasks = res.scalars().all()
        if not existing_tasks:
            logger.info("Seeding initial tasks...")
            for t_data in INITIAL_TASKS:
                task = Task(
                    id=t_data["id"],
                    user_id=demo_user.id,
                    title=t_data["title"],
                    description=t_data["description"],
                    status=t_data["status"],
                    priority=t_data["priority"],
                    due_date=t_data["due_date"],
                    linked_note_id=t_data["linked_note_id"],
                    linked_note_title=t_data["linked_note_title"],
                    tags=t_data["tags"]
                )
                db.add(task)
            await db.commit()
            logger.info(f"Seeded {len(INITIAL_TASKS)} tasks.")
        else:
            logger.info(f"Database already contains {len(existing_tasks)} tasks. Skipping tasks seed.")

if __name__ == "__main__":
    asyncio.run(seed())
