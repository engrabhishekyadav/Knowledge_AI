import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  FileText, 
  CheckSquare, 
  Sparkles, 
  Plus, 
  ArrowRight, 
  X
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const CommandPalette = () => {
  const {
    isCmdKOpen,
    setIsCmdKOpen,
    notes,
    tasks,
    setActiveNoteId,
    setActiveTab,
    createNote,
    setIsAiDrawerOpen,
    sendAiMessage
  } = useApp();

  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isCmdKOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isCmdKOpen]);

  // Compute search results
  const lowerQ = query.toLowerCase().trim();

  const filteredNotes = notes.filter(n => 
    !lowerQ || 
    n.title.toLowerCase().includes(lowerQ) || 
    n.tags.some(t => t.toLowerCase().includes(lowerQ)) ||
    n.content.toLowerCase().includes(lowerQ)
  ).slice(0, 4);

  const filteredTasks = tasks.filter(t => 
    !lowerQ || 
    t.title.toLowerCase().includes(lowerQ) || 
    t.tags?.some(tag => tag.toLowerCase().includes(lowerQ))
  ).slice(0, 4);

  const staticActions = [
    {
      id: 'action-new-note',
      title: 'Create New Markdown Document',
      category: 'Actions',
      icon: Plus,
      run: () => {
        createNote(query ? query : 'New Document');
        setIsCmdKOpen(false);
      }
    },
    {
      id: 'action-ask-ai',
      title: `Ask AI Copilot: "${query || 'Help me organize my notes'}"`,
      category: 'Actions',
      icon: Sparkles,
      run: () => {
        setIsCmdKOpen(false);
        setIsAiDrawerOpen(true);
        if (query) sendAiMessage(query);
      }
    },
    {
      id: 'action-view-kanban',
      title: 'Open Kanban Task Board',
      category: 'Navigation',
      icon: CheckSquare,
      run: () => {
        setActiveTab('tasks');
        setIsCmdKOpen(false);
      }
    }
  ];

  const allItems = [
    ...filteredNotes.map(n => ({
      id: 'note-' + n.id,
      title: n.title,
      subtitle: n.category + ' • ' + n.tags.join(', '),
      category: 'Notes',
      icon: FileText,
      run: () => {
        setActiveNoteId(n.id);
        setActiveTab('notes');
        setIsCmdKOpen(false);
      }
    })),
    ...filteredTasks.map(t => ({
      id: 'task-' + t.id,
      title: t.title,
      subtitle: `Status: ${t.status} • Priority: ${t.priority}`,
      category: 'Tasks',
      icon: CheckSquare,
      run: () => {
        setActiveTab('tasks');
        setIsCmdKOpen(false);
      }
    })),
    ...staticActions
  ];

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % allItems.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + allItems.length) % allItems.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (allItems[selectedIndex]) {
        allItems[selectedIndex].run();
      }
    } else if (e.key === 'Escape') {
      setIsCmdKOpen(false);
    }
  };

  if (!isCmdKOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-150">
      <div 
        className="fixed inset-0" 
        onClick={() => setIsCmdKOpen(false)} 
      />
      <div 
        className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden z-10 animate-in zoom-in-95 duration-150"
        onKeyDown={handleKeyDown}
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-800 bg-slate-950/60">
          <Search className="w-5 h-5 text-indigo-400 shrink-0 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command or search notes, tasks, tags..."
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none"
          />
          <button
            onClick={() => setIsCmdKOpen(false)}
            className="p-1 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors ml-2"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {allItems.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-sm">
              No matching notes or actions found.
            </div>
          ) : (
            allItems.map((item, idx) => {
              const Icon = item.icon;
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={item.run}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-indigo-600/25 border border-indigo-500/40 text-slate-100'
                      : 'hover:bg-slate-800/60 text-slate-300 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 truncate">
                    <div className={`p-2 rounded-lg shrink-0 ${
                      isSelected ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <p className="text-sm font-medium truncate">{item.title}</p>
                      {item.subtitle && (
                        <p className="text-xs text-slate-500 truncate">{item.subtitle}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 shrink-0 ml-2">
                    <span className="text-[10px] uppercase font-mono tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/50">
                      {item.category}
                    </span>
                    {isSelected && <ArrowRight className="w-4 h-4 text-indigo-400" />}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="px-4 py-2 border-t border-slate-800 bg-slate-950/60 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Navigate with <kbd className="font-mono bg-slate-800 px-1 rounded text-slate-400">↑</kbd> <kbd className="font-mono bg-slate-800 px-1 rounded text-slate-400">↓</kbd></span>
          <span>Select <kbd className="font-mono bg-slate-800 px-1 rounded text-slate-400">Enter</kbd></span>
          <span>Close <kbd className="font-mono bg-slate-800 px-1 rounded text-slate-400">Esc</kbd></span>
        </div>
      </div>
    </div>
  );
};
