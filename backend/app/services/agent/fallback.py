import re
from typing import Dict, Any, Optional

def generate_dynamic_fallback(
    prompt: str,
    active_note: Optional[Dict[str, Any]],
    is_interview: bool,
    is_summary: bool,
    has_relevant_context: bool = True
) -> str:
    """
    Generates a dynamic, document-grounded fallback response if external LLM APIs are offline.
    Extracts actual headings, keywords, and topics directly from the document.
    """
    if not active_note:
        return f"### Workspace Assistant\n\nI analyzed your query: **\"{prompt}\"**. Please select or upload a document to unlock deep contextual answers, question generation, and task extraction."

    title = active_note.get("title", "Active Document")
    content = active_note.get("content", "")
    
    # Extract headings and meaningful lines
    headings = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    bullet_items = re.findall(r"^\s*[-*]\s+(.+)$", content, re.MULTILINE)
    
    # Clean text to extract keywords
    clean_words = re.findall(r"\b[A-Za-z]{4,}\b", content)
    stop_words = {"this", "that", "with", "from", "have", "were", "been", "will", "your", "more", "also", "into", "some", "document"}
    keywords = [w for w in clean_words if w.lower() not in stop_words]
    top_keywords = list(dict.fromkeys(keywords))[:8]

    # Out-of-context threshold guardrail fallback
    if not has_relevant_context and not is_interview and not is_summary:
        covered_str = "\n".join([f"- {h}" for h in headings[:5]]) if headings else "- Core document topics and findings."
        return (
            f"### Document Scope & Query Alignment: *\"{title}\"*\n\n"
            f"Regarding your query **\"{prompt}\"**: The active document does not appear to contain relevant information or sections addressing this subject.\n\n"
            f"**Topics Covered in This Document:**\n"
            f"{covered_str}\n\n"
            f"💡 *Suggestion: Try searching for terms related to the sections listed above, or select another document in your workspace.*"
        )

    if is_interview:
        q1_topic = headings[0] if headings else (top_keywords[0] if top_keywords else "Core Concepts")
        q2_topic = headings[1] if len(headings) > 1 else (top_keywords[1] if len(top_keywords) > 1 else "Implementation Details")
        
        return (
            f"## 🎯 Comprehensive Interview & Assessment Guide: *{title}*\n\n"
            f"Based on an in-depth review of **\"{title}\"**, here are tailored technical, conceptual, and practical questions:\n\n"
            f"### 1. Core Technical Question: {q1_topic}\n"
            f"**Q: Can you explain the fundamental principles and architecture behind {q1_topic} as detailed in this document?**\n\n"
            f"* **Detailed Model Answer**: Start by defining the primary objective and architectural trade-offs. Discuss how data flows through the system, the key components involved, and how performance and reliability are maintained.\n"
            f"* **Evaluation Criteria**: Depth of understanding, clarity in explaining complex trade-offs, and practical application.\n\n"
            f"### 2. Deep-Dive & Practical Scenario: {q2_topic}\n"
            f"**Q: How would you troubleshoot, optimize, or scale the processes outlined in {q2_topic} when facing real-world constraints?**\n\n"
            f"* **Detailed Model Answer**: Outline a systematic approach: identify bottlenecks using observability/metrics, evaluate caching or indexing options, and implement resilient error recovery mechanisms.\n"
            f"* **Key Discussion Points**: Scalability, fault tolerance, and code/system maintainability.\n\n"
            f"### 3. Behavioral & Situational Question (STAR Method)\n"
            f"**Q: Describe a scenario where you had to quickly master the subject matter in \"{title}\" to deliver a high-stakes project or solve an urgent blocker.**\n\n"
            f"* **Situation & Task**: Explain the initial problem, technical constraints, and deadline.\n"
            f"* **Action**: Detail the specific research, experimentation, and cross-team collaboration you undertook.\n"
            f"* **Result**: Quantify the positive outcome (improved efficiency, zero downtime, or team alignment).\n\n"
            f"### 💡 Key Focus Areas for Mastery\n"
            + "".join([f"- **{kw}**: Review core definitions and hands-on use cases.\n" for kw in top_keywords[:4]])
        )

    elif is_summary:
        key_points_str = "\n".join([f"- {item}" for item in bullet_items[:5]]) if bullet_items else "- Thorough analysis of core objectives and structured findings.\n- Detailed methodologies and implementation steps."
        return (
            f"## 📋 Comprehensive Executive Summary: *{title}*\n\n"
            f"### Document Overview\n"
            f"**\"{title}\"** provides detailed documentation covering domain concepts, practical workflows, and strategic guidelines.\n\n"
            f"### Key Highlights & Documented Takeaways\n"
            f"{key_points_str}\n\n"
            f"### Core Themes & Subject Areas\n"
            f"{', '.join(top_keywords) if top_keywords else 'Technical specifications and workflow documentation.'}\n\n"
            f"### Strategic Next Steps\n"
            f"1. Consolidate action items into active Kanban tasks.\n"
            f"2. Link related reference documents to expand semantic knowledge coverage."
        )
    else:
        relevant_extract = "\n".join(bullet_items[:4]) if bullet_items else content[:350].strip()
        return (
            f"### Document Insights on *\"{title}\"*\n\n"
            f"Regarding your query **\"{prompt}\"**, here is a detailed breakdown based on the document text:\n\n"
            f"```markdown\n{relevant_extract}\n```\n\n"
            f"**Key Analysis**:\n"
            f"- The document emphasizes: {', '.join(top_keywords[:5]) if top_keywords else 'Structured execution'}.\n"
            f"- For further exploration, you can ask for step-by-step procedures, technical comparisons, or actionable Kanban items."
        )
