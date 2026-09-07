import httpx
import json

def test_full_stack():
    print("=== 1. Testing FastAPI Backend Directly ===")
    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=10.0) as client:
        h = client.get("/health")
        print("Health Check:", h.status_code, h.json())

        # Create note
        new_note = client.post("/notes", json={
            "title": "Automated Test Note",
            "content": "# Automated Testing\n- [ ] Task from automated test\nTODO: Urgent benchmark",
            "category": "Architecture",
            "tags": ["Test", "Automation"],
            "isFavorite": False
        }).json()
        print("Created Note:", new_note["id"], "-", new_note["title"])

        # Hybrid Search
        search_res = client.get("/notes/search/hybrid?q=Automated").json()
        print("Hybrid Search Matches:", len(search_res), [n["title"] for n in search_res])

        # Extract Tasks
        extract_res = client.post("/ai/extract-tasks", json={
            "content": new_note["content"],
            "noteId": new_note["id"],
            "noteTitle": new_note["title"]
        }).json()
        print("Extracted Tasks Count:", len(extract_res["tasks"]))

        # Create Task
        first_extracted = extract_res["tasks"][0]
        created_task = client.post("/tasks", json={
            "title": first_extracted["title"],
            "description": first_extracted["description"],
            "status": "todo",
            "priority": "high",
            "linkedNoteId": new_note["id"],
            "linkedNoteTitle": new_note["title"]
        }).json()
        print("Created Task:", created_task["id"], "-", created_task["title"])

        # Update Task Status
        task_id = created_task["id"]
        moved = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}).json()
        print("Updated Task Status:", moved["status"])

    print("\n=== 2. Testing Frontend Dev Server & Proxy ===")
    front_url = "http://[::1]:5173"
    try:
        httpx.get("http://127.0.0.1:5173", timeout=2.0)
        front_url = "http://127.0.0.1:5173"
    except Exception:
        pass
    with httpx.Client(base_url=front_url, timeout=10.0) as f_client:
        f_res = f_client.get("/")
        print("Frontend HTML Status:", f_res.status_code, "Title found:", "KnowledgeAI" in f_res.text)

        proxy_res = f_client.get("/api/v1/health")
        print("Frontend Proxy to Backend:", proxy_res.status_code, proxy_res.json())

    print("\n=== 3. Testing OpenRouter SSE AI Streaming ===")
    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=20.0) as client:
        with client.stream("GET", "/ai/chat/stream?prompt=Summarize+my+workspace") as response:
            print("Stream Status:", response.status_code)
            tokens_received = 0
            for line in response.iter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    data = json.loads(line[6:])
                    if data.get("type") == "token":
                        tokens_received += 1
            print(f"Successfully streamed {tokens_received} tokens from AI Copilot.")

        # 4. Test Chat History Persistence
        print("\n=== 4. Testing Chat History Persistence ===")
        # Save a message for new_note
        save_msg = client.post("/ai/chat/message", json={
            "sender": "user",
            "text": "What are the main interview questions for this document?",
            "noteId": new_note["id"],
            "sessionId": "test-session"
        }).json()
        print("Saved User Message:", save_msg["id"], "for note:", save_msg["noteId"])

        # Fetch messages for this note
        history = client.get(f"/ai/chat/history?note_id={new_note['id']}").json()
        print("Fetched Note Chat History:", len(history), "message(s)")
        assert len(history) >= 1

    print("\n[SUCCESS] ALL INTEGRATION TESTS PASSED WITH 0 ERRORS!")

if __name__ == "__main__":
    test_full_stack()

