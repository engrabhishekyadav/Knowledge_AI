import React, { createContext, useContext, useState } from 'react';
import { loginApi, signupApi } from '../services/api/index.js';
import {
  saveStoredNotes,
  saveStoredTasks,
  saveStoredAiMessages
} from '../services/mockStorage';
import { INITIAL_NOTES, INITIAL_TASKS, INITIAL_AI_MESSAGES } from '../data/mockData';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
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

  // Callbacks for notifying dependent contexts (Notes, Tasks, AI) on auth switch
  const [authChangeListeners, setAuthChangeListeners] = useState([]);

  const registerAuthListener = (listener) => {
    setAuthChangeListeners(prev => [...prev, listener]);
    return () => setAuthChangeListeners(prev => prev.filter(l => l !== listener));
  };

  const login = async (email, password) => {
    const data = await loginApi(email, password);
    setToken(data.accessToken);
    setCurrentUser(data.user);
    setIsDemoMode(false);
    setShowLandingPage(false);
    localStorage.setItem('knowledge_ai_token', data.accessToken);
    localStorage.setItem('knowledge_ai_user', JSON.stringify(data.user));
    localStorage.removeItem('knowledge_ai_demo_mode');

    // Notify listeners with new user state
    authChangeListeners.forEach(fn => fn('login', data.user));
    return data.user;
  };

  const signup = async (email, password, fullName) => {
    const data = await signupApi(email, password, fullName);
    setToken(data.accessToken);
    setCurrentUser(data.user);
    setIsDemoMode(false);
    setShowLandingPage(false);
    localStorage.setItem('knowledge_ai_token', data.accessToken);
    localStorage.setItem('knowledge_ai_user', JSON.stringify(data.user));
    localStorage.removeItem('knowledge_ai_demo_mode');

    // Brand new user starts clean
    saveStoredNotes([], data.user, false);
    saveStoredTasks([], data.user, false);
    saveStoredAiMessages([], data.user, false);

    authChangeListeners.forEach(fn => fn('signup', data.user));
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

    authChangeListeners.forEach(fn => fn('logout', null));
  };

  const enterDemoMode = () => {
    setIsDemoMode(true);
    setCurrentUser(null);
    setShowLandingPage(false);
    localStorage.setItem('knowledge_ai_demo_mode', 'true');
    localStorage.removeItem('knowledge_ai_user');
    localStorage.removeItem('knowledge_ai_token');

    authChangeListeners.forEach(fn => fn('demo', null));
  };

  const returnToLanding = () => {
    setShowLandingPage(true);
  };

  const resetDemoData = () => {
    if (isDemoMode || !currentUser) {
      saveStoredNotes(INITIAL_NOTES, null, true);
      saveStoredTasks(INITIAL_TASKS, null, true);
      saveStoredAiMessages(INITIAL_AI_MESSAGES, null, true);
      authChangeListeners.forEach(fn => fn('reset_demo', null));
    } else {
      saveStoredNotes([], currentUser, false);
      saveStoredTasks([], currentUser, false);
      authChangeListeners.forEach(fn => fn('reset_private', currentUser));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        setCurrentUser,
        token,
        setToken,
        isAuthenticated: !!currentUser,
        isDemoMode,
        setIsDemoMode,
        showLandingPage,
        setShowLandingPage,
        login,
        signup,
        logout,
        enterDemoMode,
        returnToLanding,
        resetDemoData,
        registerAuthListener
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
