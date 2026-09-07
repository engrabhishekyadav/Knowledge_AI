import React from 'react';
import { Plus } from 'lucide-react';
import { TaskCard } from './TaskCard';

export const KanbanColumn = ({ column, tasks, onAddTask, onEditTask, onMoveTask }) => {
  const statusColorMap = {
    todo: 'bg-indigo-500',
    in_progress: 'bg-amber-500',
    done: 'bg-emerald-500'
  };

  return (
    <div className="flex flex-col h-full min-w-[280px] sm:min-w-[320px] flex-1 rounded-3xl bg-slate-950/40 border border-slate-800/80 p-3.5 backdrop-blur-xl shrink-0">
      {/* Column Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${statusColorMap[column.id] || 'bg-slate-500'}`} />
          <h3 className="text-sm font-bold text-slate-200">{column.title}</h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 font-semibold text-slate-400">
            {tasks.length}
          </span>
        </div>

        <button
          onClick={() => onAddTask(column.id)}
          className="p-1 rounded-lg text-slate-400 hover:text-indigo-300 hover:bg-slate-800 transition-colors"
          title={`Add task to ${column.title}`}
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Task Cards Container */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {tasks.length === 0 ? (
          <div className="h-32 rounded-2xl border border-dashed border-slate-800/80 flex flex-col items-center justify-center text-slate-600 text-xs">
            <span>No tasks in this column</span>
          </div>
        ) : (
          tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onEdit={onEditTask}
              onMove={onMoveTask}
            />
          ))
        )}
      </div>
    </div>
  );
};
