import uuid
import pytest

@pytest.mark.asyncio
async def test_tasks_crud_and_status_flow(client):
    user_email = f"taskuser_{uuid.uuid4().hex[:6]}@example.com"
    auth_res = await client.post("/api/v1/auth/signup", json={
        "email": user_email,
        "password": "Password123!",
        "fullName": "Task Manager"
    })
    token = auth_res.json()["accessToken"]

    # 1. Create a single task
    create_res = await client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Optimize vector indexing",
            "description": "Benchmark HNSW search latency",
            "status": "todo",
            "priority": "urgent",
            "dueDate": "2026-10-01",
            "tags": ["DevOps", "Database"]
        }
    )
    assert create_res.status_code == 200
    task_id = create_res.json()["id"]
    assert create_res.json()["status"] == "todo"

    # 2. Update status to in_progress
    status_res = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "in_progress"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "in_progress"

    # 3. Batch create tasks
    batch_res = await client.post(
        "/api/v1/tasks/batch",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tasks": [
                {"title": "Batch task 1", "priority": "high", "status": "todo"},
                {"title": "Batch task 2", "priority": "medium", "status": "todo"}
            ]
        }
    )
    assert batch_res.status_code == 200
    batch_data = batch_res.json()
    assert len(batch_data) == 2

    # 4. List tasks
    list_res = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {token}"})
    assert list_res.status_code == 200
    tasks = list_res.json()
    assert len(tasks) >= 3

    # 5. Delete task
    del_res = await client.delete(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 200
