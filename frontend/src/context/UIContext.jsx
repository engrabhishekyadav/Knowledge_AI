import React, { createContext, useContext, useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { getStoredSettings, saveStoredSettings } from '../services/mockStorage';
import { useAuth } from './AuthContext';

const UIContext = createContext(null);

export const UIProvider = ({ children }) => {
  const { isDemoMode, returnToLanding, logout } = useAuth();

  const [theme, setTheme] = useState(() => localStorage.getItem('knowledge_ai_theme') || 'dark');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAiDrawerOpen, setIsAiDrawerOpen] = useState(false);
  const [isCmdKOpen, setIsCmdKOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [toast, setToast] = useState(null);
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);
  const [settings, setSettings] = useState(getStoredSettings);

  // Theme synchronization
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

  // Persist settings
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
    } catch {
      // Confetti optional
    }
  };

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

  return (
    <UIContext.Provider
      value={{
        theme,
        toggleTheme,
        activeTab,
        setActiveTab,
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
        toast,
        showToast,
        triggerConfetti,
        settings,
        setSettings
      }}
    >
      {children}
    </UIContext.Provider>
  );
};

export const useUI = () => {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};
