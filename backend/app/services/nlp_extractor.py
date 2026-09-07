import re
import uuid
from typing import List, Dict, Any

def extract_tasks_from_text(content: str, note_id: str = None, note_title: str = None) -> List[Dict[str, Any]]:
    """
    Extracts actionable tasks, unchecked markdown checkboxes, and TODO markers.
    """
    if not content:
        return []

    lines = content.split("\n")
    tasks = []

    for line in lines:
        stripped = line.strip()
        # 1. Match unchecked Markdown checkboxes: - [ ] Task name
        if stripped.startswith("- [ ]"):
            task_text = stripped[5:].strip()
            if task_text:
                priority = "urgent" if any(w in task_text.lower() for w in ["urgent", "critical", "p0", "asap"]) else "high"
                tasks.append({
                    "id": f"task-gen-{uuid.uuid4().hex[:8]}",
                    "title": task_text,
                    "description": f"Extracted from document: '{note_title or 'Untitled'}'",
                    "status": "todo",
                    "priority": priority,
                    "dueDate": None,
                    "linkedNoteId": note_id,
                    "linkedNoteTitle": note_title,
                    "tags": ["AI-Extracted"]
                })
        # 2. Match TODO: or ACTION: or FIXME:
        elif re.match(r"^(todo|action|fixme|task):", stripped, re.IGNORECASE):
            task_text = re.sub(r"^(todo|action|fixme|task):\s*", "", stripped, flags=re.IGNORECASE).strip()
            if task_text:
                tasks.append({
                    "id": f"task-gen-{uuid.uuid4().hex[:8]}",
                    "title": task_text,
                    "description": f"Auto-detected action item from: '{note_title or 'Untitled'}'",
                    "status": "todo",
                    "priority": "medium",
                    "dueDate": None,
                    "linkedNoteId": note_id,
                    "linkedNoteTitle": note_title,
                    "tags": ["AI-Extracted"]
                })

    return tasks
