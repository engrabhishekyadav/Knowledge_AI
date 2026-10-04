import uuid
import pytest

@pytest.mark.asyncio
async def test_notes_crud_and_isolation(client):
    # Create two distinct users
    user1_email = f"user1_{uuid.uuid4().hex[:6]}@example.com"
    user2_email = f"user2_{uuid.uuid4().hex[:6]}@example.com"

    res1 = await client.post("/api/v1/auth/signup", json={
        "email": user1_email,
        "password": "Password123!",
        "fullName": "User One"
    })
    token1 = res1.json()["accessToken"]

    res2 = await client.post("/api/v1/auth/signup", json={
        "email": user2_email,
        "password": "Password123!",
        "fullName": "User Two"
    })
    token2 = res2.json()["accessToken"]

    # 1. User 1 creates a private note
    create_res = await client.post(
        "/api/v1/notes",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "title": "Confidential Project Alpha",
            "content": "# Secret specs for Project Alpha\n- [ ] Deploy node",
            "category": "Architecture",
            "tags": ["Confidential", "Alpha"],
            "isFavorite": True
        }
    )
    assert create_res.status_code == 200
    note_id = create_res.json()["id"]

    # 2. User 1 can view note
    get_res1 = await client.get(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert get_res1.status_code == 200
    assert get_res1.json()["title"] == "Confidential Project Alpha"

    # 3. User 2 CANNOT view User 1's private note (403 Forbidden)
    get_res2 = await client.get(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert get_res2.status_code == 403

    # 4. User 2 CANNOT update User 1's note
    update_res2 = await client.put(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"title": "Hacked Title"}
    )
    assert update_res2.status_code == 403

    # 5. User 1 CAN update note
    update_res1 = await client.put(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "Updated Alpha Project"}
    )
    assert update_res1.status_code == 200
    assert update_res1.json()["title"] == "Updated Alpha Project"

    # 6. User 2 CANNOT delete User 1's note
    del_res2 = await client.delete(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert del_res2.status_code == 403

    # 7. User 1 CAN delete note
    del_res1 = await client.delete(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert del_res1.status_code == 200
