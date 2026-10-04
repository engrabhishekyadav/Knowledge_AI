import React, { createContext, useContext, useState, useEffect } from 'react';
import { getStoredTasks, saveStoredTasks } from '../services/mockStorage';
import { fetchTasks, createTaskApi, updateTaskStatusApi, deleteTaskApi, createTasksBatchApi } from '../services/api/index.js';
import { INITIAL_TASKS } from '../data/mockData';
import { useAuth } from './AuthContext';
import { useUI } from './UIContext';
import { useNotes } from './NotesContext';

const TasksContext = createContext(null);

export const TasksProvider = ({ children }) => {
  const { currentUser, isDemoMode, showLandingPage, registerAuthListener } = useAuth();
  const { showToast, triggerConfetti } = useUI();
  const { activeNote } = useNotes();

  const [tasks, setTasks] = useState(() => {
    try {
      const savedUser = localStorage.getItem('knowledge_ai_user');
      const isDemo = localStorage.getItem('knowledge_ai_demo_mode') === 'true';
      return getStoredTasks(savedUser ? JSON.parse(savedUser) : null, isDemo);
    } catch {
      return [];
    }
  });

  // Sync to LocalStorage
  useEffect(() => {
    if (!showLandingPage) {
      saveStoredTasks(tasks, currentUser, isDemoMode);
    }
  }, [tasks, currentUser, isDemoMode, showLandingPage]);

  // Initial load from live backend if user is logged in
  useEffect(() => {
    const loadFromBackend = async () => {
      if (!currentUser || isDemoMode) return;
      try {
        const backendTasks = await fetchTasks();
        if (backendTasks !== null && Array.isArray(backendTasks)) {
          setTasks(backendTasks);
        }
      } catch (err) {
        console.warn('Backend sync tasks note:', err.message);
      }
    };

    loadFromBackend();
  }, [currentUser, isDemoMode]);

  // Listen for auth state changes
  useEffect(() => {
    const unregister = registerAuthListener((action, user) => {
      if (action === 'login') {
        const userTasks = getStoredTasks(user, false);
        setTasks(userTasks);
      } else if (action === 'signup') {
        setTasks([]);
      } else if (action === 'logout') {
        setTasks([]);
      } else if (action === 'demo') {
        const demoTasks = getStoredTasks(null, true);
        setTasks(demoTasks);
      } else if (action === 'reset_demo') {
        setTasks(INITIAL_TASKS);
      } else if (action === 'reset_private') {
        setTasks([]);
      }
    });

    return unregister;
  }, [registerAuthListener]);

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

  return (
    <TasksContext.Provider
      value={{
        tasks,
        setTasks,
        createTask,
        updateTask,
        deleteTask,
        moveTaskStatus,
        addExtractedTasks
      }}
    >
      {children}
    </TasksContext.Provider>
  );
};

export const useTasks = () => {
  const context = useContext(TasksContext);
  if (!context) {
    throw new Error('useTasks must be used within a TasksProvider');
  }
  return context;
};
