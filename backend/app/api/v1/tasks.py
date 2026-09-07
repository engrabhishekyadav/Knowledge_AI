import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse, BatchTasksCreate
from app.services.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return []

    stmt = select(Task).where(Task.user_id == current_user.id).order_by(Task.created_at.desc())
    res = await db.execute(stmt)
    tasks = res.scalars().all()

    filtered = []
    for t in tasks:
        if status and t.status != status:
            continue
        if priority and t.priority != priority:
            continue
        if tag and (not t.tags or tag not in t.tags):
            continue
        filtered.append(t.to_dict())
    return filtered

@router.post("", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    new_task = Task(
        id=task_id,
        user_id=current_user.id if current_user else None,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.dueDate,
        linked_note_id=task_in.linkedNoteId,
        linked_note_title=task_in.linkedNoteTitle,
        tags=task_in.tags
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task.to_dict()

@router.post("/batch", response_model=List[TaskResponse])
async def create_tasks_batch(
    batch_in: BatchTasksCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    created_items = []
    for item in batch_in.tasks:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        t = Task(
            id=task_id,
            user_id=current_user.id if current_user else None,
            title=item.title,
            description=item.description,
            status=item.status,
            priority=item.priority,
            due_date=item.dueDate,
            linked_note_id=item.linkedNoteId,
            linked_note_title=item.linkedNoteTitle,
            tags=item.tags
        )
        db.add(t)
        created_items.append(t)

    await db.commit()
    for t in created_items:
        await db.refresh(t)
    return [t.to_dict() for t in created_items]

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    if "dueDate" in update_data:
        task.due_date = update_data.pop("dueDate")
    if "linkedNoteId" in update_data:
        task.linked_note_id = update_data.pop("linkedNoteId")
    if "linkedNoteTitle" in update_data:
        task.linked_note_title = update_data.pop("linkedNoteTitle")

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task.to_dict()

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: str,
    status_in: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = status_in.status
    await db.commit()
    await db.refresh(task)
    return task.to_dict()

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return {"status": "success", "message": f"Deleted task {task_id}"}
