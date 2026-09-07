import React from 'react';
import { 
  Clock, 
  FileText, 
  Trash2, 
  Edit3, 
  ChevronRight, 
  ChevronLeft
} from 'lucide-react';
import { PriorityBadge } from '../common/Badge';
import { useApp } from '../../context/AppContext';

export const TaskCard = ({ task, onEdit, onMove }) => {
  const { deleteTask, setActiveNoteId, setActiveTab } = useApp();

  const handleJumpToNote = (e) => {
    e.stopPropagation();
    if (task.linkedNoteId) {
      setActiveNoteId(task.linkedNoteId);
      setActiveTab('notes');
    }
  };

  const columns = ['todo', 'in_progress', 'done'];
  const currentIndex = columns.indexOf(task.status);

  const canMoveLeft = currentIndex > 0;
  const canMoveRight = currentIndex < columns.length - 1;

  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && task.status !== 'done';

  return (
    <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800/80 hover:border-slate-700/80 shadow-md group transition-all duration-200 hover:scale-[1.01] flex flex-col justify-between gap-3">
      {/* Top Header: Priority & Quick Actions */}
      <div className="flex items-center justify-between gap-2">
        <PriorityBadge priority={task.priority} />
        
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(task)}
            className="p-1 rounded-lg text-slate-400 hover:text-indigo-300 hover:bg-slate-800 transition-colors"
            title="Edit Task"
          >
            <Edit3 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => deleteTask(task.id)}
            className="p-1 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
            title="Delete Task"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Title & Description */}
      <div>
        <h4 className={`text-sm font-semibold text-slate-200 leading-snug mb-1 ${task.status === 'done' ? 'line-through text-slate-500' : ''}`}>
          {task.title}
        </h4>
        {task.description && (
          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
            {task.description}
          </p>
        )}
      </div>

      {/* Linked Note Pill */}
      {task.linkedNoteTitle && (
        <button
          onClick={handleJumpToNote}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 text-[11px] font-medium border border-indigo-500/20 transition-colors truncate text-left"
          title={`Jump to note: ${task.linkedNoteTitle}`}
        >
          <FileText className="w-3 h-3 shrink-0" />
          <span className="truncate">{task.linkedNoteTitle}</span>
        </button>
      )}

      {/* Bottom Footer: Due Date & Column Move buttons */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px]">
        <div className={`flex items-center gap-1 font-mono ${isOverdue ? 'text-rose-400 font-semibold' : 'text-slate-400'}`}>
          <Clock className="w-3 h-3" />
          <span>{task.dueDate || 'No date'}</span>
        </div>

        {/* 1-Click Move Column Switchers */}
        <div className="flex items-center gap-1">
          {canMoveLeft && (
            <button
              onClick={() => onMove(task.id, columns[currentIndex - 1])}
              className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
              title="Move backward"
            >
              <ChevronLeft className="w-3 h-3" />
            </button>
          )}
          {canMoveRight && (
            <button
              onClick={() => onMove(task.id, columns[currentIndex + 1])}
              className="p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
              title="Move forward"
            >
              <ChevronRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
