import { API_BASE, getAuthHeaders } from './client.js';

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
