import React from 'react';
import { 
  Settings, 
  User, 
  Palette, 
  Sun, 
  Moon, 
  CheckCircle2
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const SettingsView = () => {
  const { 
    notes, 
    tasks, 
    currentUser, 
    theme, 
    toggleTheme 
  } = useApp();

  const completedTasksCount = tasks.filter(t => t.status === 'done').length;
  const activeTasksCount = tasks.filter(t => t.status !== 'done').length;
  const docsCount = notes.filter(n => (n.tags || []).includes('Document')).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl glass-panel flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2.5">
            <Settings className="w-5 h-5 text-indigo-400" />
            <span>Settings</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage your personal profile and appearance preferences in one place.
          </p>
        </div>

        {/* User Status Badge */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>{currentUser ? currentUser.fullName : 'Active User'}</span>
        </div>
      </div>

      {/* 1. Account & Profile */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel space-y-6">
        <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <User className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Account & Profile</h3>
            <p className="text-xs text-slate-400">Your profile credentials and workspace activity overview.</p>
          </div>
        </div>

        {/* User Identity Card */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 shrink-0">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-xl font-bold text-indigo-300">
                {currentUser ? currentUser.fullName.charAt(0).toUpperCase() : 'U'}
              </div>
            </div>
            <div>
              <h4 className="text-base font-bold text-slate-100">
                {currentUser ? currentUser.fullName : 'Workspace User'}
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">
                {currentUser ? currentUser.email : 'user@knowledgeai.workspace'}
              </p>
              <span className="inline-block mt-2 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-[10px] font-mono">
                {currentUser ? 'Authenticated Member' : 'Local Workspace'}
              </span>
            </div>
          </div>
        </div>

        {/* Workspace Activity Overview */}
        <div>
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Workspace Activity Overview
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <p className="text-[11px] text-slate-400">Total Notes</p>
              <p className="text-xl font-bold text-slate-100">{notes.length}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <p className="text-[11px] text-slate-400">Active Tasks</p>
              <p className="text-xl font-bold text-indigo-300">{activeTasksCount}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <p className="text-[11px] text-slate-400">Completed Tasks</p>
              <p className="text-xl font-bold text-emerald-400">{completedTasksCount}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <p className="text-[11px] text-slate-400">Uploaded Docs</p>
              <p className="text-xl font-bold text-cyan-400">{docsCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Color Theme */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel space-y-6">
        <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
          <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <Palette className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Color Theme</h3>
            <p className="text-xs text-slate-400">Choose between dark slate and clean light modes for your workspace.</p>
          </div>
        </div>

        {/* Theme Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Dark Mode Card */}
          <div 
            onClick={() => { if (theme !== 'dark') toggleTheme(); }}
            className={`p-5 rounded-2xl border cursor-pointer transition-all ${
              theme === 'dark'
                ? 'bg-slate-900 border-indigo-500 ring-2 ring-indigo-500/20 shadow-md'
                : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Moon className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-semibold text-slate-200">Dark Slate</span>
              </div>
              {theme === 'dark' && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
            </div>
            <div className="h-16 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center p-2 gap-2">
              <div className="w-5 h-5 rounded bg-indigo-600"></div>
              <div className="w-16 h-2 rounded bg-slate-800"></div>
              <div className="w-10 h-2 rounded bg-slate-700"></div>
            </div>
            <p className="text-xs text-slate-400 mt-3">Deep slate dark mode tailored for focus and late-night productivity.</p>
          </div>

          {/* Light Mode Card */}
          <div 
            onClick={() => { if (theme !== 'light') toggleTheme(); }}
            className={`p-5 rounded-2xl border cursor-pointer transition-all ${
              theme === 'light'
                ? 'bg-white border-indigo-500 ring-2 ring-indigo-500/20 shadow-md'
                : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sun className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-semibold text-slate-800">Clean Light</span>
              </div>
              {theme === 'light' && <CheckCircle2 className="w-4 h-4 text-indigo-600" />}
            </div>
            <div className="h-16 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center p-2 gap-2">
              <div className="w-5 h-5 rounded bg-indigo-600"></div>
              <div className="w-16 h-2 rounded bg-slate-300"></div>
              <div className="w-10 h-2 rounded bg-slate-200"></div>
            </div>
            <p className="text-xs text-slate-500 mt-3">High-contrast, crisp daylight theme optimized for daytime reading.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
