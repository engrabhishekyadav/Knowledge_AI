import { INITIAL_NOTES, INITIAL_TASKS, INITIAL_AI_MESSAGES } from '../data/mockData';

const getStorageKey = (type, user) => {
  if (!user || user === 'guest') {
    return `knowledge_ai_guest_${type}`;
  }
  const rawKey = typeof user === 'object' ? (user.email || user.id) : user;
  const safeKey = String(rawKey || '').trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
  return `knowledge_ai_user_${safeKey}_${type}`;
};

export const getStoredNotes = (user = null, isDemoMode = false) => {
  const isGuest = isDemoMode || !user;
  if (isGuest) {
    const key = getStorageKey('notes', 'guest');
    try {
      const data = localStorage.getItem(key);
      if (data !== null) {
        return JSON.parse(data);
      }
      return INITIAL_NOTES;
    } catch {
      return INITIAL_NOTES;
    }
  }

  // Authenticated user: strictly private data only, never dummy notes
  const key = getStorageKey('notes', user);
  try {
    const data = localStorage.getItem(key);
    if (data !== null) {
      return JSON.parse(data);
    }
    return [];
  } catch {
    return [];
  }
};

export const saveStoredNotes = (notes, user = null, isDemoMode = false) => {
  const isGuest = isDemoMode || !user;
  const key = getStorageKey('notes', isGuest ? 'guest' : user);
  try {
    localStorage.setItem(key, JSON.stringify(notes || []));
  } catch (err) {
    console.error('Failed to persist notes:', err);
  }
};

export const getStoredTasks = (user = null, isDemoMode = false) => {
  const isGuest = isDemoMode || !user;
  if (isGuest) {
    const key = getStorageKey('tasks', 'guest');
    try {
      const data = localStorage.getItem(key);
      if (data !== null) {
        return JSON.parse(data);
      }
      return INITIAL_TASKS;
    } catch {
      return INITIAL_TASKS;
    }
  }

  // Authenticated user: strictly private tasks only, never dummy tasks
  const key = getStorageKey('tasks', user);
  try {
    const data = localStorage.getItem(key);
    if (data !== null) {
      return JSON.parse(data);
    }
    return [];
  } catch {
    return [];
  }
};

export const saveStoredTasks = (tasks, user = null, isDemoMode = false) => {
  const isGuest = isDemoMode || !user;
  const key = getStorageKey('tasks', isGuest ? 'guest' : user);
  try {
    localStorage.setItem(key, JSON.stringify(tasks || []));
  } catch (err) {
    console.error('Failed to persist tasks:', err);
  }
};

export const getStoredAiMessages = (user = null, isDemoMode = false) => {
  const isGuest = isDemoMode || !user;
  if (isGuest) {
    const key = getStorageKey('ai_messages', 'guest');
    try {
      const data = localStorage.getItem(key);
      if (data !== null) {
        return JSON.parse(data);
      }
      return INITIAL_AI_MESSAGES;
    } catch {
      return INITIAL_AI_MESSAGES;
    }
  }

  // Authenticated user: private messages
  const key = getStorageKey('ai_messages', user);
  try {
    const data = localStorage.getItem(key);
    if (data !== null) {
      return JSON.parse(data);
    }
    const userName = typeof user === 'object' && user.fullName ? user.fullName.split(' ')[0] : 'there';
    return [
      {
        id: 'welcome-user-' + Date.now(),
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `👋 Hello ${userName}! Welcome to your private workspace.\n\nCreate a note, upload a PDF/Docx document, or add Kanban tasks to start organizing your knowledge.`,
        actions: []
      }
    ];
  } catch {
    return [];
  }
};

export const saveStoredAiMessages = (messages, user = null, isDemoMode = false) => {
  const isGuest = isDemoMode || !user;
  const key = getStorageKey('ai_messages', isGuest ? 'guest' : user);
  try {
    localStorage.setItem(key, JSON.stringify(messages || []));
  } catch (err) {
    console.error('Failed to persist AI messages:', err);
  }
};

export const getStoredSettings = () => {
  const defaultSettings = {
    theme: 'dark',
    accentColor: 'indigo',
    editorViewMode: 'split',
    showWordCount: true,
    autoSaveIndicator: true,
    defaultTaskPriority: 'medium',
    enableConfetti: true,
    enableNotifications: true,
    enableSoundEffects: false
  };
  try {
    const data = localStorage.getItem('knowledge_ai_settings');
    return data ? { ...defaultSettings, ...JSON.parse(data) } : defaultSettings;
  } catch {
    return defaultSettings;
  }
};

export const saveStoredSettings = (settings) => {
  try {
    localStorage.setItem('knowledge_ai_settings', JSON.stringify(settings));
  } catch (err) {
    console.error('Failed to persist settings:', err);
  }
};

