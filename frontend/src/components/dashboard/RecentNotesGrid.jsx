import React from 'react';
import { FileText, ArrowRight, Star, Clock, Plus } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';

export const RecentNotesGrid = () => {
  const { notes = [], setActiveNoteId, setActiveTab, createNote } = useApp();

  const handleSelectNote = (id) => {
    setActiveNoteId(id);
    setActiveTab('notes');
  };

  const safeNotes = notes || [];
  const recent = [...safeNotes].slice(0, 4);

  return (
    <div className="glass-panel p-6 rounded-3xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-slate-100">Recent Knowledge Documents</h3>
        </div>
        <button
          onClick={() => setActiveTab('notes')}
          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recent.map((note) => (
          <div
            key={note.id}
            onClick={() => handleSelectNote(note.id)}
            className="glass-card p-4 rounded-2xl cursor-pointer hover:scale-[1.01] transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="text-sm font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors line-clamp-1">
                  {note.title}
                </h4>
                {note.isFavorite && <Star className="w-4 h-4 text-amber-400 fill-amber-400 shrink-0" />}
              </div>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-3">
                {(note.content || '').replace(/[#*`]/g, '').slice(0, 140)}...
              </p>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px] text-slate-500">
              <div className="flex items-center gap-1.5 flex-wrap">
                <Badge variant="primary">{note.category || 'General'}</Badge>
                {(note.tags || []).slice(0, 2).map((t, idx) => (
                  <span key={idx} className="text-slate-400">#{t}</span>
                ))}
              </div>
              <div className="flex items-center gap-1 text-[11px]">
                <Clock className="w-3 h-3" />
                <span>{note.updatedAt ? new Date(note.updatedAt).toLocaleDateString() : 'Recent'}</span>
              </div>
            </div>
          </div>
        ))}

        {/* Quick Add Note Card */}
        <div
          onClick={() => createNote()}
          className="p-4 rounded-2xl border border-dashed border-slate-700/80 hover:border-indigo-500/60 bg-slate-900/30 hover:bg-indigo-950/20 cursor-pointer flex flex-col items-center justify-center text-center gap-2 transition-all group min-h-[140px]"
        >
          <div className="w-9 h-9 rounded-xl bg-slate-800 group-hover:bg-indigo-600/30 flex items-center justify-center text-slate-400 group-hover:text-indigo-300 transition-colors">
            <Plus className="w-5 h-5" />
          </div>
          <span className="text-xs font-semibold text-slate-300 group-hover:text-indigo-300">
            Create New Document
          </span>
        </div>
      </div>
    </div>
  );
};
