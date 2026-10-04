import React, { createContext, useContext, useState, useEffect } from 'react';
import { getStoredNotes, saveStoredNotes } from '../services/mockStorage';
import { fetchNotes, createNoteApi, updateNoteApi, deleteNoteApi, uploadDocumentApi } from '../services/api/index.js';
import { INITIAL_NOTES } from '../data/mockData';
import { useAuth } from './AuthContext';
import { useUI } from './UIContext';

const NotesContext = createContext(null);

export const NotesProvider = ({ children }) => {
  const { currentUser, isDemoMode, showLandingPage, registerAuthListener } = useAuth();
  const { showToast, triggerConfetti, setActiveTab } = useUI();

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
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);

  // Sync to LocalStorage
  useEffect(() => {
    if (!showLandingPage) {
      saveStoredNotes(notes, currentUser, isDemoMode);
    }
  }, [notes, currentUser, isDemoMode, showLandingPage]);

  // Initial load from live backend if user is logged in
  useEffect(() => {
    const loadFromBackend = async () => {
      if (!currentUser || isDemoMode) return;
      try {
        const backendNotes = await fetchNotes();
        if (backendNotes !== null && Array.isArray(backendNotes)) {
          setNotes(backendNotes);
          if (backendNotes.length > 0) {
            setActiveNoteId(prev => {
              if (!prev || !backendNotes.find(n => n.id === prev)) {
                return backendNotes[0].id;
              }
              return prev;
            });
          } else {
            setActiveNoteId(null);
          }
        }
      } catch (err) {
        console.warn('Backend sync notes note:', err.message);
      }
    };

    loadFromBackend();
  }, [currentUser, isDemoMode]);

  // Listen for auth state changes (login, signup, logout, demo)
  useEffect(() => {
    const unregister = registerAuthListener((action, user) => {
      if (action === 'login') {
        const userNotes = getStoredNotes(user, false);
        setNotes(userNotes);
        setActiveNoteId(userNotes.length > 0 ? userNotes[0].id : null);
      } else if (action === 'signup') {
        setNotes([]);
        setActiveNoteId(null);
      } else if (action === 'logout') {
        setNotes([]);
        setActiveNoteId(null);
      } else if (action === 'demo') {
        const demoNotes = getStoredNotes(null, true);
        setNotes(demoNotes);
        setActiveNoteId(demoNotes.length > 0 ? demoNotes[0].id : null);
      } else if (action === 'reset_demo') {
        setNotes(INITIAL_NOTES);
        setActiveNoteId(INITIAL_NOTES[0].id);
      } else if (action === 'reset_private') {
        setNotes([]);
        setActiveNoteId(null);
      }
    });

    return unregister;
  }, [registerAuthListener]);

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

  return (
    <NotesContext.Provider
      value={{
        notes,
        setNotes,
        activeNote,
        activeNoteId,
        setActiveNoteId,
        createNote,
        updateNote,
        deleteNote,
        toggleFavoriteNote,
        uploadDocument,
        isUploadingDoc
      }}
    >
      {children}
    </NotesContext.Provider>
  );
};

export const useNotes = () => {
  const context = useContext(NotesContext);
  if (!context) {
    throw new Error('useNotes must be used within a NotesProvider');
  }
  return context;
};
