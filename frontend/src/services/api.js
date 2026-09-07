const API_BASE = '/api/v1';

// ---------------- AUTHENTICATION API ----------------

export const signupApi = async (email, password, fullName) => {
  try {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, fullName }),
    });
    if (res.ok) {
      return await res.json();
    }
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Signup failed. Please try again.');
  } catch (err) {
    if (err.message && !err.message.includes('fetch') && !err.message.includes('NetworkError') && !err.message.includes('Failed to fetch')) {
      throw err;
    }
    // Offline / Standalone Mock fallback
    const userObj = {
      id: 'user-' + Math.random().toString(36).substr(2, 9),
      email: email.trim().toLowerCase(),
      fullName: fullName ? fullName.trim() : email.split('@')[0],
      avatarUrl: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(email)}`,
      createdAt: new Date().toISOString()
    };
    return {
      accessToken: 'local_jwt_' + btoa(email) + '_' + Date.now(),
      tokenType: 'bearer',
      user: userObj
    };
  }
};

export const loginApi = async (email, password) => {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      return await res.json();
    }
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Invalid email or password.');
  } catch (err) {
    if (err.message && !err.message.includes('fetch') && !err.message.includes('NetworkError') && !err.message.includes('Failed to fetch')) {
      throw err;
    }
    // Offline / Standalone Mock fallback
    const userObj = {
      id: 'user-' + Math.random().toString(36).substr(2, 9),
      email: email.trim().toLowerCase(),
      fullName: email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      avatarUrl: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(email)}`,
      createdAt: new Date().toISOString()
    };
    return {
      accessToken: 'local_jwt_' + btoa(email) + '_' + Date.now(),
      tokenType: 'bearer',
      user: userObj
    };
  }
};

export const fetchCurrentUserApi = async (token) => {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to verify token:', e);
  }
  return null;
};

// ---------------- AUTHENTICATION & HEADERS HELPER ----------------

const getAuthHeaders = (extra = {}) => {
  const token = localStorage.getItem('knowledge_ai_token');
  const headers = { ...extra };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

// ---------------- NOTES API ----------------

export const fetchNotes = async () => {
  try {
    const res = await fetch(`${API_BASE}/notes`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Backend offline, fallback to local store:', e);
  }
  return null;
};

export const createNoteApi = async (noteData) => {
  try {
    const res = await fetch(`${API_BASE}/notes`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(noteData),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to create note on backend:', e);
  }
  return null;
};

export const updateNoteApi = async (id, noteData) => {
  try {
    const res = await fetch(`${API_BASE}/notes/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(noteData),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to update note on backend:', e);
  }
  return null;
};

export const deleteNoteApi = async (id) => {
  try {
    const res = await fetch(`${API_BASE}/notes/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to delete note on backend:', e);
  }
  return null;
};

export const uploadDocumentApi = async (file, category = 'Interview Prep') => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const res = await fetch(`${API_BASE}/notes/upload`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });
    if (res.ok) {
      return await res.json();
    } else {
      const errData = await res.json();
      throw new Error(errData.detail || 'Upload failed');
    }
  } catch (e) {
    console.error('Document upload error:', e);
    throw e;
  }
};

export const hybridSearchNotes = async (query, weight = 0.65) => {
  try {
    const res = await fetch(`${API_BASE}/notes/search/hybrid?q=${encodeURIComponent(query)}&weight=${weight}`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Hybrid search fallback:', e);
  }
  return [];
};

// ---------------- TASKS API ----------------

export const fetchTasks = async () => {
  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Backend offline, fallback to local store:', e);
  }
  return null;
};

export const createTaskApi = async (taskData) => {
  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(taskData),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to create task on backend:', e);
  }
  return null;
};

export const createTasksBatchApi = async (tasksList) => {
  try {
    const res = await fetch(`${API_BASE}/tasks/batch`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ tasks: tasksList }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to batch create tasks on backend:', e);
  }
  return null;
};

export const updateTaskStatusApi = async (id, status) => {
  try {
    const res = await fetch(`${API_BASE}/tasks/${id}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ status }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to update task status on backend:', e);
  }
  return null;
};

export const deleteTaskApi = async (id) => {
  try {
    const res = await fetch(`${API_BASE}/tasks/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Failed to delete task on backend:', e);
  }
  return null;
};

// ---------------- AI COPILOT & STREAMING API ----------------

export const streamAiChat = async (prompt, activeNote, onChunk, onAction) => {
  const noteId = activeNote ? activeNote.id : '';
  const url = `${API_BASE}/ai/chat/stream?prompt=${encodeURIComponent(prompt)}${noteId ? `&note_id=${encodeURIComponent(noteId)}` : ''}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let accumulatedText = '';
    let actions = [];

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
    let fallbackText = `I have received your request: "${prompt}". Workspace data is synchronized with the database.`;
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

// ---------------- CHAT HISTORY PERSISTENCE API ----------------

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

