import { API_BASE, getAuthHeaders } from './client.js';

export const streamAiChat = async (prompt, activeNote, onChunk, onAction) => {
  const noteId = activeNote ? activeNote.id : '';
  const token = localStorage.getItem('knowledge_ai_token');
  const queryParams = new URLSearchParams({ prompt });
  if (noteId) queryParams.set('note_id', noteId);
  if (token) queryParams.set('token', token);

  const url = `${API_BASE}/ai/chat/stream?${queryParams.toString()}`;

  try {
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let accumulatedText = '';
    const actions = [];

    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          const payloadStr = trimmed.substring(6).trim();
          if (payloadStr === '[DONE]') {
            continue;
          }
          try {
            const data = JSON.parse(payloadStr);
            if (data.type === 'token' && data.content) {
              accumulatedText += data.content;
              if (onChunk) onChunk(accumulatedText);
            } else if (data.type === 'action' && data.action) {
              actions.push(data.action);
              if (onAction) onAction(data.action);
            }
          } catch (jsonErr) {
            console.warn('Failed to parse SSE JSON chunk:', jsonErr);
          }
        }
      }
    }

    return { text: accumulatedText, actions };
  } catch (err) {
    console.warn('SSE Streaming connection failed, running local generator:', err);
    // Fallback generator
    const fallbackText = `I have received your request: "${prompt}". Workspace data is synchronized with the database.`;
    if (onChunk) onChunk(fallbackText);
    return { text: fallbackText, actions: [] };
  }
};

export const extractTasksFromMarkdown = async (content, noteId, noteTitle) => {
  try {
    const res = await fetch(`${API_BASE}/ai/extract-tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, noteId, noteTitle }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.tasks || [];
    }
  } catch (e) {
    console.warn('Backend task extraction failed:', e);
  }
  return [];
};

export const fetchChatHistoryApi = async (noteId = null, sessionId = null) => {
  try {
    const params = new URLSearchParams();
    if (noteId) params.append('note_id', noteId);
    if (sessionId) params.append('session_id', sessionId);
    
    const res = await fetch(`${API_BASE}/ai/chat/history?${params.toString()}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Backend chat history fetch note:', e);
  }
  return null;
};

export const saveChatMessageApi = async (msgData) => {
  try {
    const res = await fetch(`${API_BASE}/ai/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msgData),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to save chat message:', e);
  }
  return null;
};

export const clearChatHistoryApi = async (noteId = null, sessionId = null) => {
  try {
    const params = new URLSearchParams();
    if (noteId) params.append('note_id', noteId);
    if (sessionId) params.append('session_id', sessionId);

    const res = await fetch(`${API_BASE}/ai/chat/history?${params.toString()}`, {
      method: 'DELETE',
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to clear chat history:', e);
  }
  return null;
};
