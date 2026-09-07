import io
import httpx
import json
import sys

def test_document_upload_and_interview_prep():
    print("=== 1. Testing Document Upload API (TXT / DOC) ===", flush=True)
    
    sample_jd = (
        "# Senior Full-Stack Python & AI Engineer\n\n"
        "## Responsibilities:\n"
        "- Build scalable microservices using FastAPI, PostgreSQL, and asyncpg.\n"
        "- Design vector search pipelines using pgvector and dense embeddings.\n"
        "- Implement real-time SSE streaming for LLM agents.\n"
        "- Build responsive UI with React, Tailwind CSS, and WebSockets.\n\n"
        "## Requirements:\n"
        "- 4+ years of Python (FastAPI / Django).\n"
        "- Strong experience with PostgreSQL database optimization and connection pooling.\n"
        "- Hands-on knowledge of LangChain, RAG architectures, and OpenAI/OpenRouter APIs.\n"
    )
    
    file_bytes = sample_jd.encode('utf-8')
    files = {
        'file': ('Senior_Python_AI_Job_Description.md', io.BytesIO(file_bytes), 'text/markdown')
    }
    data = {
        'category': 'Interview Prep'
    }

    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=45.0) as client:
        res = client.post("/notes/upload", files=files, data=data)
        print("Upload Response Status:", res.status_code, flush=True)
        assert res.status_code == 200, f"Upload failed: {res.text}"
        uploaded_note = res.json()
        print(f"Successfully Created Note from Document: {uploaded_note['id']}", flush=True)
        print(f"Title: {uploaded_note['title']}", flush=True)
        print(f"Category: {uploaded_note['category']}", flush=True)
        print(f"Tags: {uploaded_note['tags']}", flush=True)
        
        print("\n=== 2. Testing AI Interview Prep Generation via SSE ===", flush=True)
        with client.stream(
            "GET", 
            f"/ai/chat/stream?prompt=Generate+interview+questions+for+this+job+description&note_id={uploaded_note['id']}"
        ) as stream_res:
            print("Stream Status:", stream_res.status_code, flush=True)
            assert stream_res.status_code == 200
            accumulated = ""
            for line in stream_res.iter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        chunk = json.loads(line[6:])
                        if chunk.get("type") == "token":
                            accumulated += chunk.get("content", "")
                    except Exception:
                        pass
            
            print(f"Received {len(accumulated)} chars of AI Interview Prep.", flush=True)
            safe_snippet = accumulated[:200].encode('ascii', 'ignore').decode('ascii')
            print("Snippet:\n" + safe_snippet + "...\n", flush=True)
            
        print("=== 3. Testing Chat History Persistence for Uploaded Document ===", flush=True)
        history_res = client.get(f"/ai/chat/history?note_id={uploaded_note['id']}")
        history = history_res.json()
        print(f"Chat History for Uploaded Doc: {len(history)} message(s) stored in PostgreSQL", flush=True)
        assert len(history) >= 2, "User prompt and AI reply should both be persisted in PostgreSQL"


    print("\n[SUCCESS] FEATURE 2 AUTOMATED TEST PASSED WITH 0 ERRORS!", flush=True)

if __name__ == "__main__":
    test_document_upload_and_interview_prep()
