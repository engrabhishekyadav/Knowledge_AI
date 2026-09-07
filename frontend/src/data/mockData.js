export const INITIAL_NOTES = [
  {
    id: 'note-1',
    title: '🧠 AI Agent Architecture & pgvector Integration',
    category: 'Architecture',
    tags: ['AI', 'pgvector', 'Backend', 'FastAPI'],
    updatedAt: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    isFavorite: true,
    content: `# 🧠 AI Agent Architecture & pgvector Integration

This document outlines the hybrid retrieval strategy combining **PostgreSQL Full-Text Search (\`tsvector\`)** with **vector embeddings (\`pgvector\`)** to power the autonomous AI agent.

---

## 1. High-Level Flow
\`\`\`
User Query ──► Query Embedding (text-embedding-3-small)
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
\`\`\`

## 2. Key Components
* **FastAPI Async Engine**: Handles non-blocking database queries with \`asyncpg\`.
* **Hybrid Scoring Formula**:
  $$\\text{Score} = 0.65 \\times \\text{SemanticSimilarity} + 0.35 \\times \\text{FTSScore}$$
* **Entity Extractor**: Background PyTorch lightweight model detecting action items.

## 3. Action Items
- [x] Configure PostgreSQL 16 with \`pgvector\` extension
- [ ] Implement async connection pool in FastAPI
- [ ] Create LangGraph workflow with tool-calling for task dispatch
- [ ] Benchmark cosine distance lookup on 50,000 note chunks
`
  },
  {
    id: 'note-2',
    title: '⚡ Sprint 24 Planning: Autonomous Task Extraction',
    category: 'Productivity',
    tags: ['Sprint', 'Planning', 'Tasks', 'NLP'],
    updatedAt: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    isFavorite: true,
    content: `# ⚡ Sprint 24 Planning: Autonomous Task Extraction

Meeting with engineering & product team to finalize the real-time action extractor.

## Objectives
1. Automatically detect \`TODO:\` and action-oriented verbs when user types in the Markdown editor.
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
`
  },
  {
    id: 'note-3',
    title: '🎨 Frontend Design System & Glassmorphism Guidelines',
    category: 'Design',
    tags: ['UI', 'Tailwind', 'DesignSystem'],
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    isFavorite: false,
    content: `# 🎨 Frontend Design System Guidelines

Aesthetic guidelines for dark-mode first, glassmorphic UI.

### Color Tokens
- **Background Root**: \`#090d16\` (Dark Cosmic)
- **Glass Card Fill**: \`rgba(30, 41, 59, 0.55)\`
- **Accent Glow**: \`#6366f1\` (Indigo) / \`#8b5cf6\` (Violet)
- **Success Glow**: \`#10b981\` (Emerald)

### Micro-interactions
> Every interactive element must have hover elevation, subtle border lighting, and keyboard accessibility.
`
  },
  {
    id: 'note-4',
    title: '🛡️ Enterprise Security & Data Encryption Spec',
    category: 'Security',
    tags: ['Security', 'Auth', 'Compliance'],
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
    isFavorite: false,
    content: `# 🛡️ Enterprise Security Spec

Details for end-to-end encryption and workspace isolation.

### Authentication
- JWT Bearer tokens with short expiry (15 mins) and sliding refresh tokens.
- Role-Based Access Control (RBAC): \`Viewer\`, \`Editor\`, \`Admin\`.

### Data Protection
- AES-256 for note payloads at rest.
- Vector embeddings stored with hashed user tenant IDs.
`
  }
];

export const INITIAL_TASKS = [
  {
    id: 'task-1',
    title: 'Implement LangGraph tool-calling for task dispatch',
    description: 'Allow AI agent to autonomously create and update tasks in PostgreSQL when instructed in chat or note parsing.',
    status: 'in_progress',
    priority: 'urgent',
    dueDate: '2026-09-10',
    linkedNoteId: 'note-1',
    linkedNoteTitle: '🧠 AI Agent Architecture',
    tags: ['AI', 'Backend']
  },
  {
    id: 'task-2',
    title: 'Benchmark pgvector cosine similarity lookup',
    description: 'Run latency and recall benchmarks across 50,000 synthetic note vectors.',
    status: 'todo',
    priority: 'high',
    dueDate: '2026-09-12',
    linkedNoteId: 'note-1',
    linkedNoteTitle: '🧠 AI Agent Architecture',
    tags: ['pgvector', 'Database']
  },
  {
    id: 'task-3',
    title: 'Design interactive AI action confirmation cards',
    description: 'Create preview widgets in AI Drawer so user can approve extracted tasks before board insertion.',
    status: 'in_progress',
    priority: 'high',
    dueDate: '2026-09-08',
    linkedNoteId: 'note-2',
    linkedNoteTitle: '⚡ Sprint 24 Planning',
    tags: ['UI', 'React']
  },
  {
    id: 'task-4',
    title: 'Setup PostgreSQL 16 schema & vector extension',
    description: 'Initial migration script with users, notes (embedding vector(1536)), and tasks.',
    status: 'done',
    priority: 'medium',
    dueDate: '2026-09-05',
    linkedNoteId: 'note-1',
    linkedNoteTitle: '🧠 AI Agent Architecture',
    tags: ['Database']
  },
  {
    id: 'task-5',
    title: 'Implement Command Palette (Ctrl+K) fuzzy search',
    description: 'Global modal searching across active notes, tasks, and system shortcuts.',
    status: 'done',
    priority: 'medium',
    dueDate: '2026-09-06',
    linkedNoteId: 'note-3',
    linkedNoteTitle: '🎨 Frontend Design System',
    tags: ['UI', 'Feature']
  },
  {
    id: 'task-6',
    title: 'Local PyTorch NLP Action Item Extractor prototype',
    description: 'Train lightweight token classification model on task phrasing.',
    status: 'todo',
    priority: 'low',
    dueDate: '2026-09-18',
    linkedNoteId: 'note-2',
    linkedNoteTitle: '⚡ Sprint 24 Planning',
    tags: ['NLP', 'PyTorch']
  }
];

export const INITIAL_AI_MESSAGES = [
  {
    id: 'msg-1',
    sender: 'ai',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    text: "Hello! I am your **Knowledge AI Copilot**. I can help you search notes with hybrid vector queries, summarize documents, or automatically extract action items into your Kanban board.\n\nHow can I assist your workflow today?",
    actions: []
  }
];
