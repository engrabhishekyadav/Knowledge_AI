import React, { createContext, useContext, useState, useEffect } from 'react';
import { getStoredAiMessages, saveStoredAiMessages } from '../services/mockStorage';
import { streamAiChat, fetchChatHistoryApi, clearChatHistoryApi } from '../services/api/index.js';
import { INITIAL_AI_MESSAGES } from '../data/mockData';
import { useAuth } from './AuthContext';
import { useUI } from './UIContext';
import { useNotes } from './NotesContext';
import { useTasks } from './TasksContext';

const AiContext = createContext(null);

export const AiProvider = ({ children }) => {
  const { currentUser, isDemoMode, showLandingPage, registerAuthListener } = useAuth();
  const { showToast, setIsAiDrawerOpen } = useUI();
  const { activeNote, activeNoteId, notes, createNote, updateNote } = useNotes();
  const { addExtractedTasks } = useTasks();

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
  const [isStreaming, setIsStreaming] = useState(false);

  // Sync to LocalStorage
  useEffect(() => {
    if (!showLandingPage) {
      saveStoredAiMessages(aiMessages, currentUser, isDemoMode);
    }
  }, [aiMessages, currentUser, isDemoMode, showLandingPage]);

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
  }, [activeNoteId, notes]);

  // Listen for auth changes
  useEffect(() => {
    const unregister = registerAuthListener((action, user) => {
      if (action === 'login') {
        const userAiMsgs = getStoredAiMessages(user, false);
        setAiMessages(userAiMsgs);
      } else if (action === 'signup') {
        setAiMessages(getStoredAiMessages(user, false));
      } else if (action === 'logout') {
        setAiMessages([]);
      } else if (action === 'demo') {
        const demoMessages = getStoredAiMessages(null, true);
        setAiMessages(demoMessages);
      } else if (action === 'reset_demo') {
        setAiMessages(INITIAL_AI_MESSAGES);
      } else if (action === 'reset_private') {
        setAiMessages([]);
      }
    });

    return unregister;
  }, [registerAuthListener]);

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

  return (
    <AiContext.Provider
      value={{
        aiMessages,
        setAiMessages,
        isLoadingChatHistory,
        isStreaming,
        sendAiMessage,
        clearAiChatHistory,
        saveChatAsNote,
        generateInterviewPrepForActiveNote,
        extractTasksFromActiveNote,
        summarizeActiveNote,
        executeAiAction
      }}
    >
      {children}
    </AiContext.Provider>
  );
};

export const useAi = () => {
  const context = useContext(AiContext);
  if (!context) {
    throw new Error('useAi must be used within an AiProvider');
  }
  return context;
};
