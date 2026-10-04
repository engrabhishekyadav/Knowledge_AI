import re
from typing import List, Dict, Any

def chunk_document_text(
    text: str,
    chunk_size: int = 700,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits document text into semantically aware overlapping chunks.
    Preserves Markdown heading context (H1, H2, H3) for each chunk.
    """
    if not text or not text.strip():
        return []

    cleaned = text.strip()
    if len(cleaned) <= chunk_size:
        return [{
            "chunk_index": 0,
            "content": cleaned,
            "section": "Overview",
            "char_count": len(cleaned)
        }]

    # Split by lines and track headings
    lines = cleaned.split("\n")
    sections: List[Dict[str, Any]] = []
    current_heading = "Overview"
    current_buffer: List[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,4})\s+(.+)$", line.strip())
        if heading_match:
            # Save previous section if not empty
            if current_buffer:
                body = "\n".join(current_buffer).strip()
                if body:
                    sections.append({"heading": current_heading, "text": body})
                current_buffer = []
            current_heading = heading_match.group(2).strip()
            current_buffer.append(line)
        else:
            current_buffer.append(line)

    if current_buffer:
        body = "\n".join(current_buffer).strip()
        if body:
            sections.append({"heading": current_heading, "text": body})

    # Now split each section into chunks respecting chunk_size and chunk_overlap
    chunks: List[Dict[str, Any]] = []
    chunk_idx = 0

    for sec in sections:
        sec_text = sec["text"]
        sec_heading = sec["heading"]

        def format_chunk(text_val: str, heading: str) -> str:
            clean = text_val.strip()
            if heading and heading != "Overview" and not clean.startswith("#") and not clean.startswith(f"[{heading}]"):
                return f"[{heading}]\n{clean}"
            return clean

        if len(sec_text) <= chunk_size:
            formatted = format_chunk(sec_text, sec_heading)
            chunks.append({
                "chunk_index": chunk_idx,
                "content": formatted,
                "section": sec_heading,
                "char_count": len(formatted)
            })
            chunk_idx += 1
            continue

        # Split long section text into paragraphs/sentences
        paragraphs = sec_text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if not current_chunk:
                current_chunk = para
            elif len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk += "\n\n" + para
            else:
                # Current chunk is full
                formatted = format_chunk(current_chunk, sec_heading)
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": formatted,
                    "section": sec_heading,
                    "char_count": len(formatted)
                })
                chunk_idx += 1

                # Retain overlap from end of current chunk
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = (overlap_text + "\n\n" + para).strip() if overlap_text else para

        if current_chunk:
            formatted = format_chunk(current_chunk, sec_heading)
            chunks.append({
                "chunk_index": chunk_idx,
                "content": formatted,
                "section": sec_heading,
                "char_count": len(formatted)
            })
            chunk_idx += 1

    return chunks
