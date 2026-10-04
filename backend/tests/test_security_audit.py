import uuid
import pytest
from app.services.embedding import generate_fallback_embedding
from app.services.document_parser import sanitize_filename

@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected(client):
    """Verify all modifying and sensitive endpoints return 401 when unauthenticated."""
    # 1. Notes create
    res = await client.post("/api/v1/notes", json={"title": "Test", "content": "Content"})
    assert res.status_code == 401

    # 2. Document upload
    res = await client.post("/api/v1/notes/upload", files={"file": ("test.txt", b"Hello")})
    assert res.status_code == 401

    # 3. RAG Search
    res = await client.get("/api/v1/notes/rag/search?q=test")
    assert res.status_code == 401

    # 4. Chat history
    res = await client.get("/api/v1/ai/chat/history")
    assert res.status_code == 401

    # 5. Tasks create
    res = await client.post("/api/v1/tasks", json={"title": "Task 1", "status": "todo"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_cross_tenant_rag_isolation(client):
    """Verify User B cannot retrieve document chunks or notes belonging to User A."""
    user1_email = f"sec_user1_{uuid.uuid4().hex[:6]}@example.com"
    user2_email = f"sec_user2_{uuid.uuid4().hex[:6]}@example.com"

    # Register User 1
    r1 = await client.post("/api/v1/auth/signup", json={
        "email": user1_email,
        "password": "Password123!",
        "fullName": "User One"
    })
    token1 = r1.json()["accessToken"]

    # Register User 2
    r2 = await client.post("/api/v1/auth/signup", json={
        "email": user2_email,
        "password": "Password123!",
        "fullName": "User Two"
    })
    token2 = r2.json()["accessToken"]

    # User 1 creates note with unique classified text
    secret_term = f"ZEUS_TOKEN_{uuid.uuid4().hex[:8]}"
    create_res = await client.post(
        "/api/v1/notes",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "title": "Secret Defense Dossier",
            "content": f"# Classified Mission\nKey identifier: {secret_term}\nCritical deployment directives.",
            "category": "Defense"
        }
    )
    assert create_res.status_code == 200
    note_id = create_res.json()["id"]

    # User 2 performs RAG search for User 1's secret term without note_id
    rag_res2 = await client.get(
        f"/api/v1/notes/rag/search?q={secret_term}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert rag_res2.status_code == 200
    chunks_found = rag_res2.json()["chunks"]
    assert len(chunks_found) == 0, "Security violation: User 2 retrieved User 1's RAG chunks!"

    # User 2 attempts RAG search specifying User 1's note_id
    rag_res2_direct = await client.get(
        f"/api/v1/notes/rag/search?q={secret_term}&note_id={note_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert rag_res2_direct.status_code == 403, "User 2 should receive 403 when accessing User 1's note chunks"

    # User 2 performs hybrid search for secret term
    hybrid_res2 = await client.get(
        f"/api/v1/notes/search/hybrid?q={secret_term}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert hybrid_res2.status_code == 200
    assert len(hybrid_res2.json()) == 0, "Security violation: User 2 retrieved User 1's note in hybrid search!"


@pytest.mark.asyncio
async def test_chat_isolation_and_cross_tenant_deletion(client):
    """Verify chat messages are strictly isolated per user and cannot be read or deleted across users."""
    user1_email = f"chat_user1_{uuid.uuid4().hex[:6]}@example.com"
    user2_email = f"chat_user2_{uuid.uuid4().hex[:6]}@example.com"

    r1 = await client.post("/api/v1/auth/signup", json={
        "email": user1_email,
        "password": "Password123!",
        "fullName": "Chat User One"
    })
    token1 = r1.json()["accessToken"]

    r2 = await client.post("/api/v1/auth/signup", json={
        "email": user2_email,
        "password": "Password123!",
        "fullName": "Chat User Two"
    })
    token2 = r2.json()["accessToken"]

    common_session = "workspace-shared-session"

    # User 1 saves a chat message
    save_res = await client.post(
        "/api/v1/ai/chat/message",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "sender": "user",
            "text": "User 1 confidential chat message",
            "sessionId": common_session
        }
    )
    assert save_res.status_code == 200

    # User 2 queries chat history for the same session ID
    u2_history = await client.get(
        f"/api/v1/ai/chat/history?session_id={common_session}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert u2_history.status_code == 200
    assert len(u2_history.json()) == 0, "Security violation: User 2 saw User 1's chat messages!"

    # User 2 attempts to delete chat history for the session
    del_res = await client.delete(
        f"/api/v1/ai/chat/history?session_id={common_session}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert del_res.status_code == 200

    # User 1 verifies their message was NOT deleted by User 2
    u1_history = await client.get(
        f"/api/v1/ai/chat/history?session_id={common_session}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert u1_history.status_code == 200
    assert len(u1_history.json()) >= 1, "Security violation: User 2 was able to delete User 1's chat messages!"


def test_deterministic_fallback_embeddings():
    """Verify that fallback feature hashing is deterministic and stable."""
    sample_text = "Knowledge AI Retrieval-Augmented Generation Architecture"
    emb1 = generate_fallback_embedding(sample_text)
    emb2 = generate_fallback_embedding(sample_text)
    assert emb1 == emb2
    assert len(emb1) == 768


def test_filename_sanitization():
    """Verify filename sanitization strips path traversal and malicious markdown formatting."""
    malicious = "../../../secret<script>alert(1)</script> file.txt"
    sanitized = sanitize_filename(malicious)
    assert ".." not in sanitized
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert sanitized.endswith(".txt")

@pytest.mark.asyncio
async def test_agent_package_modular_components():
    """Verify agent modular sub-components and streaming orchestrator."""
    from app.services.agent import (
        classify_agent_intent,
        build_system_prompt,
        generate_dynamic_fallback,
        stream_agent_response
    )

    # 1. Test intent classification
    intent = classify_agent_intent("Please generate 10 interview questions for this note")
    assert intent["is_interview"] is True
    assert intent["target_count"] == 10

    # 2. Test prompt building with security boundaries
    rag_prompt = build_system_prompt(
        prompt="Test question",
        retrieved_chunks=[{"section": "Intro", "content": "Chunk content", "similarity_score": 0.9, "rerank_score": 0.95}],
        has_relevant_context=True,
        is_interview=True,
        target_count=5
    )
    assert "<retrieved_knowledge_context>" in rag_prompt
    assert "<document_excerpt" in rag_prompt

    doc_prompt = build_system_prompt(
        prompt="Test question",
        active_note={"title": "Doc 1", "content": "Content 1", "category": "General", "tags": []},
        retrieved_chunks=None,
        has_relevant_context=True
    )
    assert "<active_document_context>" in doc_prompt
    assert "Doc 1" in doc_prompt

    # 3. Test dynamic fallback
    fallback = generate_dynamic_fallback(
        prompt="Summarize this",
        active_note={"title": "Test Plan", "content": "# Overview\nKey facts here."},
        is_interview=False,
        is_summary=True
    )
    assert "Test Plan" in fallback
    assert "Executive Summary" in fallback

    # 4. Test stream generation lifecycle
    chunks = []
    async for chunk in stream_agent_response("Explain how vector indexing works", active_note=None):
        chunks.append(chunk)

    assert len(chunks) > 0
    assert chunks[-1] == "data: [DONE]\n\n"

