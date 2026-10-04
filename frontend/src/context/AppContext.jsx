import React from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import { UIProvider, useUI } from './UIContext';
import { NotesProvider, useNotes } from './NotesContext';
import { TasksProvider, useTasks } from './TasksContext';
import { AiProvider, useAi } from './AiContext';

/**
 * Composite AppProvider
 * Orchestrates modular domain contexts in dependency order:
 * Auth -> UI -> Notes -> Tasks -> AI
 */
export const AppProvider = ({ children }) => {
  return (
    <AuthProvider>
      <UIProvider>
        <NotesProvider>
          <TasksProvider>
            <AiProvider>
              {children}
            </AiProvider>
          </TasksProvider>
        </NotesProvider>
      </UIProvider>
    </AuthProvider>
  );
};

/**
 * Backward-Compatible useApp() Facade Hook
 * Combines all domain hooks into a single interface.
 * Existing components calling useApp() will continue to work with zero changes.
 */
export const useApp = () => {
  const auth = useAuth();
  const ui = useUI();
  const notes = useNotes();
  const tasks = useTasks();
  const ai = useAi();

  return {
    // Auth domain
    currentUser: auth.currentUser,
    setCurrentUser: auth.setCurrentUser,
    token: auth.token,
    setToken: auth.setToken,
    isAuthenticated: auth.isAuthenticated,
    isDemoMode: auth.isDemoMode,
    setIsDemoMode: auth.setIsDemoMode,
    showLandingPage: auth.showLandingPage,
    setShowLandingPage: auth.setShowLandingPage,
    login: auth.login,
    signup: auth.signup,
    logout: auth.logout,
    enterDemoMode: auth.enterDemoMode,
    returnToLanding: auth.returnToLanding,
    resetDemoData: auth.resetDemoData,

    // UI & Navigation domain
    theme: ui.theme,
    toggleTheme: ui.toggleTheme,
    activeTab: ui.activeTab,
    setActiveTab: ui.setActiveTab,
    isAiDrawerOpen: ui.isAiDrawerOpen,
    setIsAiDrawerOpen: ui.setIsAiDrawerOpen,
    isCmdKOpen: ui.isCmdKOpen,
    setIsCmdKOpen: ui.setIsCmdKOpen,
    sidebarCollapsed: ui.sidebarCollapsed,
    setSidebarCollapsed: ui.setSidebarCollapsed,
    isLogoutModalOpen: ui.isLogoutModalOpen,
    setIsLogoutModalOpen: ui.setIsLogoutModalOpen,
    requestLogout: ui.requestLogout,
    confirmLogout: ui.confirmLogout,
    toast: ui.toast,
    showToast: ui.showToast,
    triggerConfetti: ui.triggerConfetti,
    settings: ui.settings,
    setSettings: ui.setSettings,

    // Notes domain
    notes: notes.notes,
    setNotes: notes.setNotes,
    activeNote: notes.activeNote,
    activeNoteId: notes.activeNoteId,
    setActiveNoteId: notes.setActiveNoteId,
    createNote: notes.createNote,
    updateNote: notes.updateNote,
    deleteNote: notes.deleteNote,
    toggleFavoriteNote: notes.toggleFavoriteNote,
    uploadDocument: notes.uploadDocument,
    isUploadingDoc: notes.isUploadingDoc,

    // Tasks domain
    tasks: tasks.tasks,
    setTasks: tasks.setTasks,
    createTask: tasks.createTask,
    updateTask: tasks.updateTask,
    deleteTask: tasks.deleteTask,
    moveTaskStatus: tasks.moveTaskStatus,
    addExtractedTasks: tasks.addExtractedTasks,

    // AI Copilot domain
    aiMessages: ai.aiMessages,
    setAiMessages: ai.setAiMessages,
    isLoadingChatHistory: ai.isLoadingChatHistory,
    isStreaming: ai.isStreaming,
    sendAiMessage: ai.sendAiMessage,
    clearAiChatHistory: ai.clearAiChatHistory,
    saveChatAsNote: ai.saveChatAsNote,
    generateInterviewPrepForActiveNote: ai.generateInterviewPrepForActiveNote,
    extractTasksFromActiveNote: ai.extractTasksFromActiveNote,
    summarizeActiveNote: ai.summarizeActiveNote,
    executeAiAction: ai.executeAiAction
  };
};

// Re-export individual domain hooks for granular performance optimization
export { useAuth } from './AuthContext';
export { useUI } from './UIContext';
export { useNotes } from './NotesContext';
export { useTasks } from './TasksContext';
export { useAi } from './AiContext';
