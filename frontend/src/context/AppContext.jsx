import React, { createContext, useContext, useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  getStoredNotes,
  saveStoredNotes,
  getStoredTasks,
  saveStoredTasks,
  getStoredAiMessages,
  saveStoredAiMessages,
  getStoredSettings,
  saveStoredSettings
} from '../services/mockStorage';
import { 
  fetchNotes, 
  createNoteApi, 
  updateNoteApi, 
  deleteNoteApi,
  fetchTasks,
  createTaskApi,
  createTasksBatchApi,
  updateTaskStatusApi,
  deleteTaskApi,
  streamAiChat,
  fetchChatHistoryApi,
  clearChatHistoryApi,
  uploadDocumentApi,
  signupApi,
  loginApi
} from '../services/api';
import { INITIAL_NOTES, INITIAL_TASKS, INITIAL_AI_MESSAGES } from '../data/mockData';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Auth State
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('knowledge_ai_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('knowledge_ai_token') || '');
  const [isDemoMode, setIsDemoMode] = useState(() => localStorage.getItem('knowledge_ai_demo_mode') === 'true');
  const [showLandingPage, setShowLandingPage] = useState(() => {
    const savedUser = localStorage.getItem('knowledge_ai_user');
    const isDemo = localStorage.getItem('knowledge_ai_demo_mode') === 'true';
    return !savedUser && !isDemo;
  });

  const [theme, setTheme] = useState(() => localStorage.getItem('knowledge_ai_theme') || 'dark');

  const [activeTab, setActiveTab] = useState('dashboard');
  const [notes, setNotes] = useState(() => {
    try {
      const savedUser = localStorage.getItem('knowledge_ai_user');
      const isDemo = localStorage.getItem('knowledge_ai_demo_mode') === 'true';
      return getStoredNotes(savedUser ? JSON.parse(savedUser) : null, isDemo);
    } catch {
      return [];
    }
  });
  const [activeNoteId, setActiveNoteId] = useState(() => notes.length > 0 ? notes[0].id : null);
  const [tasks, setTasks] = useState(() => {
    try {
      const savedUser = localStorage.getItem('knowledge_ai_user');
      const isDemo = localStorage.getItem('knowledge_ai_demo_mode') === 'true';
      return getStoredTasks(savedUser ? JSON.parse(savedUser) : null, isDemo);
    } catch {
      return [];
    }
  });
  const [aiMessages, setAiMessages] = useState(() => {
    try {
      const savedUser = localStorage.getItem('knowledge_ai_user');
      const isDemo = localStorage.getItem('knowledge_ai_demo_mode') === 'true';
      return getStoredAiMessages(savedUser ? JSON.parse(savedUser) : null, isDemo);
    } catch {
      return [];
    }
  });
  const [isLoadingChatHistory, setIsLoadingChatHistory] = useState(false);
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);
  const [settings, setSettings] = useState(getStoredSettings);

  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
    localStorage.setItem('knowledge_ai_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const [isAiDrawerOpen, setIsAiDrawerOpen] = useState(false);
  const [isCmdKOpen, setIsCmdKOpen] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [toast, setToast] = useState(null);
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);

  const requestLogout = () => {
    setIsLogoutModalOpen(true);
  };

  const confirmLogout = () => {
    setIsLogoutModalOpen(false);
    if (isDemoMode) {
      returnToLanding();
    } else {
      logout();
    }
  };


  // Initial Load from Live Backend if user is logged in
  useEffect(() => {
    const loadFromBackend = async () => {
      // Demo mode always stays local with dummy data; do not query backend
      if (!currentUser || isDemoMode) return;

      try {
        const backendNotes = await fetchNotes();
        if (backendNotes !== null && Array.isArray(backendNotes)) {
          setNotes(backendNotes);
          if (backendNotes.length > 0) {
            if (!activeNoteId || !backendNotes.find(n => n.id === activeNoteId)) {
              setActiveNoteId(backendNotes[0].id);
            }
          } else {
            setActiveNoteId(null);
          }
        }

        const backendTasks = await fetchTasks();
        if (backendTasks !== null && Array.isArray(backendTasks)) {
          setTasks(backendTasks);
        }
      } catch (err) {
        console.warn('Backend sync note:', err.message);
      }
    };
    loadFromBackend();
  }, [currentUser, isDemoMode]);

  // Note-Scoped Dynamic AI Chat History Loading
  useEffect(() => {
    const loadNoteChatHistory = async () => {
      if (!activeNoteId) return;
      setIsLoadingChatHistory(true);
      try {
        const history = await fetchChatHistoryApi(activeNoteId);
        if (history && history.length > 0) {
          setAiMessages(history);
        } else {
          // If no history in DB yet for this note, give helpful contextual starter
          const currentNote = notes.find(n => n.id === activeNoteId);
          setAiMessages([
            {
              id: 'init-msg-' + (activeNoteId || 'workspace'),
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              text: currentNote 
                ? `👋 Hello! I am your AI Copilot. I have loaded context for **"${currentNote.title}"**.\n\nYou can ask me to summarize it, extract tasks to Kanban, or generate interview questions!`
                : `👋 Hello! I am your AI Copilot. Ask me anything about your workspace notes and tasks.`,
              actions: []
            }
          ]);
        }
      } catch (err) {
        console.warn('Failed to fetch chat history:', err);
      } finally {
        setIsLoadingChatHistory(false);
      }
    };

    loadNoteChatHistory();
  }, [activeNoteId]);


  // Sync to LocalStorage
  useEffect(() => {
    if (!showLandingPage) {
      saveStoredNotes(notes, currentUser, isDemoMode);
    }
  }, [notes, currentUser, isDemoMode, showLandingPage]);

  useEffect(() => {
    if (!showLandingPage) {
      saveStoredTasks(tasks, currentUser, isDemoMode);
    }
  }, [tasks, currentUser, isDemoMode, showLandingPage]);

  useEffect(() => {
    if (!showLandingPage) {
      saveStoredAiMessages(aiMessages, currentUser, isDemoMode);
    }
  }, [aiMessages, currentUser, isDemoMode, showLandingPage]);

  useEffect(() => {
    saveStoredSettings(settings);
  }, [settings]);

  // Global Ctrl + K Keyboard Shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsCmdKOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const showToast = (message, type = 'info') => {
    setToast({ message, type, id: Date.now() });
    setTimeout(() => {
      setToast(null);
    }, 3200);
  };

  const triggerConfetti = () => {
    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.85 }
      });
    } catch {}
  };

  // Note Handlers
  const activeNote = notes.find(n => n.id === activeNoteId) || notes[0] || null;

  const createNote = async (title = 'Untitled Note', content = '') => {
    const notePayload = {
      title: title || 'Untitled Note',
      category: 'General',
      tags: ['New'],
      isFavorite: false,
      content: content || '# ' + (title || 'Untitled Note') + '\n\nStart writing markdown here...'
    };

    // Optimistic local update
    const tempId = 'note-' + Math.random().toString(36).substr(2, 9);
    const newNote = { ...notePayload, id: tempId, updatedAt: new Date().toISOString() };
    setNotes(prev => [newNote, ...prev]);
    setActiveNoteId(newNote.id);
    setActiveTab('notes');
    showToast(`Created note "${newNote.title}"`, 'success');

    // Async Backend Sync
    const created = await createNoteApi(notePayload);
    if (created && created.id) {
      setNotes(prev => prev.map(n => n.id === tempId ? created : n));
      setActiveNoteId(created.id);
    }
    return newNote;
  };

  const updateNote = async (id, updates) => {
    setNotes(prev => prev.map(note => {
      if (note.id === id) {
        return {
          ...note,
          ...updates,
          updatedAt: new Date().toISOString()
        };
      }
      return note;
    }));

    // Debounced or direct backend update
    await updateNoteApi(id, updates);
  };

  const deleteNote = async (id) => {
    const noteToDelete = notes.find(n => n.id === id);
    const updated = notes.filter(n => n.id !== id);
    setNotes(updated);
    if (activeNoteId === id) {
      setActiveNoteId(updated.length > 0 ? updated[0].id : null);
    }
    showToast(`Deleted "${noteToDelete?.title || 'note'}"`, 'info');
    await deleteNoteApi(id);
  };

  const toggleFavoriteNote = async (id) => {
    const target = notes.find(n => n.id === id);
    if (target) {
      const newFav = !target.isFavorite;
      setNotes(prev => prev.map(n => n.id === id ? { ...n, isFavorite: newFav } : n));
      await updateNoteApi(id, { isFavorite: newFav });
    }
  };

  // Task Handlers
  const createTask = async (taskData) => {
    const taskPayload = {
      title: taskData.title || 'New Task',
      description: taskData.description || '',
      status: taskData.status || 'todo',
      priority: taskData.priority || 'medium',
      dueDate: taskData.dueDate || new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString().split('T')[0],
      linkedNoteId: taskData.linkedNoteId || (activeNote ? activeNote.id : null),
      linkedNoteTitle: taskData.linkedNoteTitle || (activeNote ? activeNote.title : null),
      tags: taskData.tags || ['Task']
    };

    const tempId = 'task-' + Math.random().toString(36).substr(2, 9);
    const newTask = { ...taskPayload, id: tempId };
    setTasks(prev => [newTask, ...prev]);
    showToast(`Task created: "${newTask.title}"`, 'success');

    const created = await createTaskApi(taskPayload);
    if (created && created.id) {
      setTasks(prev => prev.map(t => t.id === tempId ? created : t));
    }
    return newTask;
  };

  const updateTask = async (id, updates) => {
    setTasks(prev => prev.map(t => {
      if (t.id === id) {
        const updated = { ...t, ...updates };
        if (updates.status === 'done' && t.status !== 'done') {
          triggerConfetti();
          showToast(`Completed task: "${t.title}" 🎉`, 'success');
        }
        return updated;
      }
      return t;
    }));

    if (updates.status) {
      await updateTaskStatusApi(id, updates.status);
    }
  };

  const deleteTask = async (id) => {
    setTasks(prev => prev.filter(t => t.id !== id));
    showToast('Task removed', 'info');
    await deleteTaskApi(id);
  };

  const moveTaskStatus = async (id, newStatus) => {
    updateTask(id, { status: newStatus });
  };

  const addExtractedTasks = async (newTasksList) => {
    if (!newTasksList || newTasksList.length === 0) return;
    setTasks(prev => [...newTasksList, ...prev]);
    triggerConfetti();
    showToast(`Added ${newTasksList.length} tasks to Kanban board!`, 'success');
    await createTasksBatchApi(newTasksList);
  };

  // AI Assistant Handlers with SSE Streaming
  const sendAiMessage = async (userText) => {
    if (!userText.trim() || isStreaming) return;

    const userMsg = {
      id: 'msg-' + Date.now(),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: userText,
      actions: []
    };

    const updatedMessages = [...aiMessages, userMsg];
    setAiMessages(updatedMessages);
    setIsStreaming(true);

    const botMsgId = 'msg-ai-' + Date.now();
    const botInitialMsg = {
      id: botMsgId,
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: 'Thinking...',
      actions: []
    };

    setAiMessages([...updatedMessages, botInitialMsg]);

    try {
      const { text, actions } = await streamAiChat(
        userText,
        activeNote,
        (partialText) => {
          setAiMessages(prev => prev.map(m => m.id === botMsgId ? { ...m, text: partialText } : m));
        },
        (newAction) => {
          setAiMessages(prev => prev.map(m => {
            if (m.id === botMsgId) {
              const existingActions = m.actions || [];
              return { ...m, actions: [...existingActions, newAction] };
            }
            return m;
          }));
        }
      );

      setAiMessages(prev => prev.map(m => m.id === botMsgId ? { ...m, text, actions } : m));
    } catch {
      setAiMessages(prev => prev.map(m => m.id === botMsgId ? { ...m, text: 'Error generating AI response.' } : m));
    } finally {
      setIsStreaming(false);
    }
  };

  const uploadDocument = async (file, category = 'Interview Prep') => {
    if (!file) return;
    setIsUploadingDoc(true);
    showToast(`Parsing document "${file.name}"...`, 'info');
    try {
      const createdNote = await uploadDocumentApi(file, category);
      if (createdNote && createdNote.id) {
        setNotes(prev => [createdNote, ...prev.filter(n => n.id !== createdNote.id)]);
        setActiveNoteId(createdNote.id);
        setActiveTab('notes');
        triggerConfetti();
        showToast(`Document "${createdNote.title}" imported!`, 'success');
        return createdNote;
      }
    } catch (err) {
      showToast(`Upload failed: ${err.message || 'Error parsing document'}`, 'error');
    } finally {
      setIsUploadingDoc(false);
    }
  };

  const generateInterviewPrepForActiveNote = () => {
    if (!activeNote) {
      showToast('Please select or upload a note first', 'error');
      return;
    }
    setIsAiDrawerOpen(true);
    sendAiMessage(`Generate 5 comprehensive technical and behavioral interview questions with model answers and key preparation points for the document "${activeNote.title}".`);
  };

  const extractTasksFromActiveNote = async () => {

    if (!activeNote) {
      showToast('Please open a note first', 'error');
      return;
    }
    setIsAiDrawerOpen(true);
    sendAiMessage(`Extract actionable tasks from note "${activeNote.title}"`);
  };

  const summarizeActiveNote = () => {
    if (!activeNote) {
      showToast('Please open a note first', 'error');
      return;
    }
    setIsAiDrawerOpen(true);
    sendAiMessage(`Summarize note "${activeNote.title}"`);
  };

  const executeAiAction = (action) => {
    if (action.type === 'ADD_TASKS') {
      addExtractedTasks(action.payload);
    } else if (action.type === 'INSERT_SUMMARY') {
      if (activeNote) {
        const updatedContent = action.payload + activeNote.content;
        updateNote(activeNote.id, { content: updatedContent });
        showToast('Summary inserted into note!', 'success');
      }
    }
  };

  const clearAiChatHistory = async () => {
    await clearChatHistoryApi(activeNoteId);
    const currentNote = notes.find(n => n.id === activeNoteId);
    setAiMessages([
      {
        id: 'init-msg-' + Date.now(),
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: currentNote 
          ? `Chat history cleared. Context is set to **"${currentNote.title}"**. How can I help you?`
          : `Chat history cleared. How can I assist you with your workspace?`,
        actions: []
      }
    ]);
    showToast('Chat history cleared', 'info');
  };

  const saveChatAsNote = async () => {
    if (!aiMessages || aiMessages.length === 0) {
      showToast('No messages to save', 'warning');
      return;
    }
    const currentNote = notes.find(n => n.id === activeNoteId);
    const noteTitle = `AI Discussion - ${currentNote ? currentNote.title : 'Workspace'} (${new Date().toLocaleDateString()})`;
    
    let markdownContent = `# ${noteTitle}\n\n`;
    markdownContent += `> **Source Context**: ${currentNote ? currentNote.title : 'Workspace General'}\n`;
    markdownContent += `> **Date**: ${new Date().toLocaleString()}\n\n---\n\n`;

    aiMessages.forEach((msg) => {
      const isUser = msg.sender === 'user';
      markdownContent += `### ${isUser ? '👤 User' : '🤖 AI Copilot'} (${msg.timestamp || ''})\n\n`;
      markdownContent += `${msg.text}\n\n`;
    });

    const created = await createNote(noteTitle, markdownContent);
    showToast(`Saved conversation as note "${created.title}"`, 'success');
  };

  // Auth Handlers
  const login = async (email, password) => {
    const data = await loginApi(email, password);
    setToken(data.accessToken);
    setCurrentUser(data.user);
    setIsDemoMode(false);
    setShowLandingPage(false);
    setActiveTab('dashboard');
    localStorage.setItem('knowledge_ai_token', data.accessToken);
    localStorage.setItem('knowledge_ai_user', JSON.stringify(data.user));
    localStorage.removeItem('knowledge_ai_demo_mode');

    // Load registered user's private data (clean/empty if new user)
    const userNotes = getStoredNotes(data.user, false);
    const userTasks = getStoredTasks(data.user, false);
    const userAiMsgs = getStoredAiMessages(data.user, false);
    setNotes(userNotes);
    setActiveNoteId(userNotes.length > 0 ? userNotes[0].id : null);
    setTasks(userTasks);
    setAiMessages(userAiMsgs);

    showToast(`Welcome back, ${data.user.fullName}! 👋`, 'success');
    return data.user;
  };

  const signup = async (email, password, fullName) => {
    const data = await signupApi(email, password, fullName);
    setToken(data.accessToken);
    setCurrentUser(data.user);
    setIsDemoMode(false);
    setShowLandingPage(false);
    setActiveTab('dashboard');
    localStorage.setItem('knowledge_ai_token', data.accessToken);
    localStorage.setItem('knowledge_ai_user', JSON.stringify(data.user));
    localStorage.removeItem('knowledge_ai_demo_mode');

    // Brand new user starts with 0 dummy notes/tasks
    const userNotes = [];
    const userTasks = [];
    const userAiMsgs = getStoredAiMessages(data.user, false);
    saveStoredNotes(userNotes, data.user, false);
    saveStoredTasks(userTasks, data.user, false);
    saveStoredAiMessages(userAiMsgs, data.user, false);

    setNotes(userNotes);
    setActiveNoteId(null);
    setTasks(userTasks);
    setAiMessages(userAiMsgs);

    triggerConfetti();
    showToast(`Account created! Welcome, ${data.user.fullName} 🎉`, 'success');
    return data.user;
  };

  const logout = () => {
    setToken('');
    setCurrentUser(null);
    setIsDemoMode(false);
    setShowLandingPage(true);
    localStorage.removeItem('knowledge_ai_token');
    localStorage.removeItem('knowledge_ai_user');
    localStorage.removeItem('knowledge_ai_demo_mode');
    setNotes([]);
    setTasks([]);
    setActiveNoteId(null);
    showToast('Signed out of workspace', 'info');
  };

  const enterDemoMode = () => {
    setIsDemoMode(true);
    setCurrentUser(null);
    setShowLandingPage(false);
    setActiveTab('dashboard');
    localStorage.setItem('knowledge_ai_demo_mode', 'true');
    localStorage.removeItem('knowledge_ai_user');
    localStorage.removeItem('knowledge_ai_token');

    // Guest gets rich demo dummy data
    const demoNotes = getStoredNotes(null, true);
    const demoTasks = getStoredTasks(null, true);
    const demoMessages = getStoredAiMessages(null, true);
    setNotes(demoNotes);
    setActiveNoteId(demoNotes.length > 0 ? demoNotes[0].id : null);
    setTasks(demoTasks);
    setAiMessages(demoMessages);

    showToast('Entered Guest Demo Mode ✨', 'info');
  };

  const returnToLanding = () => {
    setShowLandingPage(true);
  };

  const resetDemoData = () => {
    if (isDemoMode || !currentUser) {
      setNotes(INITIAL_NOTES);
      setActiveNoteId(INITIAL_NOTES[0].id);
      setTasks(INITIAL_TASKS);
      setAiMessages(INITIAL_AI_MESSAGES);
      saveStoredNotes(INITIAL_NOTES, null, true);
      saveStoredTasks(INITIAL_TASKS, null, true);
      saveStoredAiMessages(INITIAL_AI_MESSAGES, null, true);
      showToast('Reset guest demo workspace', 'info');
    } else {
      setNotes([]);
      setActiveNoteId(null);
      setTasks([]);
      saveStoredNotes([], currentUser, false);
      saveStoredTasks([], currentUser, false);
      showToast('Cleared private workspace data', 'info');
    }
  };

  return (
    <AppContext.Provider
      value={{
        currentUser,
        token,
        isAuthenticated: !!currentUser,
        isDemoMode,
        showLandingPage,
        setShowLandingPage,
        login,
        signup,
        logout,
        enterDemoMode,
        returnToLanding,
        activeTab,
        setActiveTab,
        notes,
        setNotes,
        activeNote,
        activeNoteId,
        setActiveNoteId,
        createNote,
        updateNote,
        deleteNote,
        toggleFavoriteNote,
        tasks,
        setTasks,
        createTask,
        updateTask,
        deleteTask,
        moveTaskStatus,
        addExtractedTasks,
        aiMessages,
        isLoadingChatHistory,
        isUploadingDoc,
        isStreaming,
        sendAiMessage,
        clearAiChatHistory,
        saveChatAsNote,
        uploadDocument,
        generateInterviewPrepForActiveNote,
        extractTasksFromActiveNote,
        summarizeActiveNote,
        executeAiAction,
        isAiDrawerOpen,
        setIsAiDrawerOpen,
        isCmdKOpen,
        setIsCmdKOpen,
        sidebarCollapsed,
        setSidebarCollapsed,
        isLogoutModalOpen,
        setIsLogoutModalOpen,
        requestLogout,
        confirmLogout,
        theme,
        toggleTheme,
        settings,
        setSettings,
        resetDemoData,
        toast,
        showToast
      }}
    >
      {children}
    </AppContext.Provider>
  );
};




export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

