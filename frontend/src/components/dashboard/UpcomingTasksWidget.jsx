import React from 'react';
import { CheckSquare, ArrowRight, Circle, Clock, Plus } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { PriorityBadge } from '../common/Badge';

export const UpcomingTasksWidget = ({ onOpenNewTaskModal }) => {
  const { tasks, updateTask, setActiveTab } = useApp();

  const activeTasks = tasks.filter(t => t.status !== 'done').slice(0, 5);

  const toggleTaskStatus = (task) => {
    updateTask(task.id, {
      status: task.status === 'done' ? 'todo' : 'done'
    });
  };

  return (
    <div className="glass-panel p-6 rounded-3xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckSquare className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-slate-100">Active Action Items</h3>
        </div>
        <button
          onClick={() => setActiveTab('tasks')}
          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
        >
          <span>Open Kanban</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-2.5">
        {activeTasks.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            🎉 All caught up! No active tasks pending.
          </div>
        ) : (
          activeTasks.map((task) => (
            <div
              key={task.id}
              className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 flex items-center justify-between gap-3 group transition-all"
            >
              <div className="flex items-center gap-3 truncate">
                <button
                  onClick={() => toggleTaskStatus(task)}
                  className="text-slate-500 hover:text-emerald-400 transition-colors shrink-0"
                >
                  <Circle className="w-4 h-4" />
                </button>
                <div className="truncate">
                  <p className="text-sm font-medium text-slate-200 truncate group-hover:text-slate-100">
                    {task.title}
                  </p>
                  {task.linkedNoteTitle && (
                    <p className="text-[11px] text-slate-400 truncate">
                      Linked: {task.linkedNoteTitle}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2.5 shrink-0">
                <PriorityBadge priority={task.priority} />
                <div className="flex items-center gap-1 text-[11px] text-slate-400">
                  <Clock className="w-3 h-3" />
                  <span>{task.dueDate}</span>
                </div>
              </div>
            </div>
          ))
        )}

        <button
          onClick={onOpenNewTaskModal}
          className="w-full py-2.5 rounded-2xl border border-dashed border-slate-700/80 hover:border-indigo-500/60 text-xs font-semibold text-slate-400 hover:text-indigo-300 hover:bg-indigo-950/20 flex items-center justify-center gap-2 transition-all"
        >
          <Plus className="w-4 h-4" />
          Add Quick Task
        </button>
      </div>
    </div>
  );
};
