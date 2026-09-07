import React, { useState } from 'react';
import { KanbanBoard } from './KanbanBoard';
import { Search, Plus, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';
import { useApp } from '../../context/AppContext';

export const TasksView = ({ onOpenNewTaskModal }) => {
  const { tasks, setIsAiDrawerOpen, sendAiMessage } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const pendingCount = tasks.filter(t => t.status !== 'done').length;
  const doneCount = tasks.filter(t => t.status === 'done').length;

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Top Filter and Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-3xl glass-panel">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Input */}
          <div className="relative w-64">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tasks..."
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Priority Filter */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
            {['ALL', 'URGENT', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                  priorityFilter === p
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Right Stats & Quick Actions */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-slate-400">
            <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-amber-400">
              {pendingCount} Active
            </span>
            <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-emerald-400">
              {doneCount} Done
            </span>
          </div>

          <Button
            variant="ai"
            size="sm"
            icon={Sparkles}
            onClick={() => {
              setIsAiDrawerOpen(true);
              sendAiMessage("Prioritize and plan my active Kanban tasks based on deadlines.");
            }}
          >
            AI Prioritize
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={onOpenNewTaskModal}
          >
            Add Task
          </Button>
        </div>
      </div>

      {/* Kanban Board Container */}
      <div className="flex-1 overflow-hidden">
        <KanbanBoard
          searchQuery={searchQuery}
          priorityFilter={priorityFilter}
          tagFilter="ALL"
        />
      </div>
    </div>
  );
};
