import React, { useState, useRef } from 'react';
import { 
  Search, 
  Plus, 
  Star, 
  Trash2, 
  FileText,
  Upload,
  Loader2,
  FileUp
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const NoteList = () => {
  const {
    notes = [],
    activeNoteId,
    setActiveNoteId,
    createNote,
    deleteNote,
    toggleFavoriteNote,
    uploadDocument,
    isUploadingDoc
  } = useApp();

  const [search, setSearch] = useState('');
  const [selectedTag, setSelectedTag] = useState('ALL');
  const fileInputRef = useRef(null);

  const safeNotes = notes || [];

  // Extract all unique tags safely
  const allTags = ['ALL', ...Array.from(new Set(safeNotes.flatMap(n => n.tags || [])))];

  const filteredNotes = safeNotes.filter(note => {
    const title = note.title || '';
    const content = note.content || '';
    const tags = note.tags || [];
    const matchesSearch = 
      title.toLowerCase().includes(search.toLowerCase()) ||
      content.toLowerCase().includes(search.toLowerCase());
    const matchesTag = selectedTag === 'ALL' || tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadDocument(file);
      e.target.value = '';
    }
  };

  return (
    <div className="w-full md:w-80 h-full flex flex-col border-r border-slate-800 bg-slate-950/40 shrink-0">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.docx,.doc,.txt,.md"
        className="hidden"
      />

      {/* Search & Create Header */}
      <div className="p-3.5 border-b border-slate-800 space-y-2.5">
        <div className="flex items-center justify-between gap-1.5">
          <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Documents ({filteredNotes.length})</span>
          </h3>

          <div className="flex items-center gap-1.5">
            {/* Upload Doc Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploadingDoc}
              className="p-1.5 px-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 text-xs flex items-center gap-1 shadow-sm transition-all disabled:opacity-50"
              title="Upload PDF, Word Docx, or Text document"
            >
              {isUploadingDoc ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
              ) : (
                <Upload className="w-3.5 h-3.5 text-indigo-400" />
              )}
              <span className="hidden sm:inline">Upload</span>
            </button>

            {/* New Note Button */}
            <button
              onClick={() => createNote()}
              className="p-1.5 px-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs flex items-center gap-1 shadow-sm transition-all"
              title="Create New Document"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New</span>
            </button>
          </div>
        </div>

        {/* Uploading Banner Indicator */}
        {isUploadingDoc && (
          <div className="p-2 rounded-xl bg-indigo-950/50 border border-indigo-500/30 text-indigo-200 text-xs flex items-center gap-2 animate-pulse">
            <FileUp className="w-4 h-4 text-indigo-400 animate-bounce" />
            <span className="text-[11px]">Parsing PDF/DOCX into note...</span>
          </div>
        )}

        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter documents..."
            className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Tag Filters Pill List */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar text-xs">
          {allTags.slice(0, 6).map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-2 py-0.5 rounded-lg text-[11px] font-medium transition-colors shrink-0 ${
                selectedTag === tag
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {tag === 'ALL' ? 'All' : `#${tag}`}
            </button>
          ))}
        </div>
      </div>

      {/* Note Items List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {filteredNotes.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">
            No documents found. Click "Upload" or "New" to start!
          </div>
        ) : (
          filteredNotes.map((note) => {
            const isActive = note.id === activeNoteId;
            const isDoc = (note.tags || []).includes('Document') || (note.tags || []).includes('InterviewPrep');

            return (
              <div
                key={note.id}
                onClick={() => setActiveNoteId(note.id)}
                className={`p-3 rounded-2xl cursor-pointer transition-all group relative border ${
                  isActive
                    ? 'bg-indigo-600/15 border-indigo-500/40 text-slate-100 shadow-sm'
                    : 'bg-slate-900/40 border-slate-800/60 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="flex items-start justify-between gap-1.5 mb-1.5">
                  <div className="flex items-center gap-1.5 truncate flex-1">
                    {isDoc && (
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" title="Imported Document"></span>
                    )}
                    <h4 className={`text-xs font-semibold truncate ${isActive ? 'text-indigo-300' : 'text-slate-200'}`}>
                      {note.title}
                    </h4>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFavoriteNote(note.id);
                      }}
                      className="text-slate-500 hover:text-amber-400 p-0.5 transition-colors"
                    >
                      <Star className={`w-3.5 h-3.5 ${note.isFavorite ? 'text-amber-400 fill-amber-400' : ''}`} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNote(note.id);
                      }}
                      className="text-slate-500 hover:text-rose-400 p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-2">
                  {(note.content || '').replace(/[#*`>]/g, '').slice(0, 90)}...
                </p>

                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/40">
                  <div className="flex items-center gap-1 truncate">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                      {note.category || 'General'}
                    </span>
                    {isDoc && (
                      <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-[9px] font-mono">
                        DOC
                      </span>
                    )}
                  </div>
                  <span>{note.updatedAt ? new Date(note.updatedAt).toLocaleDateString() : 'Recent'}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
