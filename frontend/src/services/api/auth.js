import { API_BASE } from './client.js';

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
