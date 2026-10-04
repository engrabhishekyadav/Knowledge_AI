import { API_BASE, getAuthHeaders } from './client.js';

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
