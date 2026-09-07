import React, { useState } from 'react';
import { Plus, X, Folder, Check } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const NoteMetadataBar = () => {
  const { activeNote, updateNote } = useApp();
  const [newTagInput, setNewTagInput] = useState('');
  const [isAddingTag, setIsAddingTag] = useState(false);

  if (!activeNote) return null;

  const categories = ['Architecture', 'Productivity', 'Design', 'Security', 'Research', 'General'];

  const handleTitleChange = (e) => {
    updateNote(activeNote.id, { title: e.target.value });
  };

  const handleCategoryChange = (e) => {
    updateNote(activeNote.id, { category: e.target.value });
  };

  const handleAddTag = (e) => {
    e.preventDefault();
    const tag = newTagInput.trim().replace(/^#/, '');
    const currentTags = activeNote.tags || [];
    if (tag && !currentTags.includes(tag)) {
      updateNote(activeNote.id, {
        tags: [...currentTags, tag]
      });
      setNewTagInput('');
      setIsAddingTag(false);
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    const currentTags = activeNote.tags || [];
    updateNote(activeNote.id, {
      tags: currentTags.filter(t => t !== tagToRemove)
    });
  };

  const wordsCount = activeNote.content ? activeNote.content.trim().split(/\s+/).filter(Boolean).length : 0;
  const charsCount = activeNote.content ? activeNote.content.length : 0;
  const safeTags = activeNote.tags || [];

  return (
    <div className="p-4 border-b border-slate-800 bg-slate-950/60 space-y-3">
      {/* Note Title Input */}
      <div className="flex items-center justify-between gap-4">
        <input
          type="text"
          value={activeNote.title || ''}
          onChange={handleTitleChange}
          placeholder="Untitled Note..."
          className="text-xl font-bold bg-transparent text-slate-100 placeholder-slate-600 focus:outline-none flex-1 truncate"
        />
        
        {/* Saved Status Indicator */}
        <div className="flex items-center gap-1.5 text-xs text-slate-400 shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>Saved</span>
        </div>
      </div>

      {/* Category, Tags, Word Count Row */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          {/* Category Selector */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <Folder className="w-3.5 h-3.5 text-indigo-400" />
            <select
              value={activeNote.category || 'General'}
              onChange={handleCategoryChange}
              className="bg-transparent text-xs text-slate-300 focus:outline-none cursor-pointer"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-slate-900 text-slate-200">
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Tags Chips */}
          {safeTags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs"
            >
              <span>#{tag}</span>
              <button
                onClick={() => handleRemoveTag(tag)}
                className="hover:text-rose-400 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}

          {/* Add Tag Inline Form */}
          {isAddingTag ? (
            <form onSubmit={handleAddTag} className="inline-flex items-center gap-1">
              <input
                type="text"
                autoFocus
                value={newTagInput}
                onChange={(e) => setNewTagInput(e.target.value)}
                placeholder="tag name"
                className="px-2 py-0.5 rounded bg-slate-900 border border-indigo-500 text-xs text-slate-200 focus:outline-none w-20"
              />
              <button type="submit" className="text-emerald-400 hover:text-emerald-300">
                <Check className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setIsAddingTag(false)}
                className="text-slate-500 hover:text-slate-300"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </form>
          ) : (
            <button
              onClick={() => setIsAddingTag(true)}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Tag</span>
            </button>
          )}
        </div>

        {/* Word and Character Count */}
        <div className="flex items-center gap-3 text-slate-400 text-[11px] font-mono">
          <span>{wordsCount} words</span>
          <span>•</span>
          <span>{charsCount} chars</span>
        </div>
      </div>
    </div>
  );
};
