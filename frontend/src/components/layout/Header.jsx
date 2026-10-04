import React from 'react';
import { 
  Search, 
  Sparkles, 
  Plus, 
  CheckSquare, 
  Command,
  LogOut,
  Home,
  Zap,
  Sun,
  Moon
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Button } from '../common/Button';
import { ConnectionStatusBadge } from '../common/ConnectionStatusBadge';

export const Header = ({ onOpenNewTaskModal }) => {
  const { 
    activeTab, 
    createNote, 
    isAiDrawerOpen, 
    setIsAiDrawerOpen, 
    setIsCmdKOpen,
    currentUser,
    requestLogout,
    theme,
    toggleTheme
  } = useApp();

  const titleMap = {
    dashboard: 'Workspace Overview',
    notes: 'Knowledge Base & Notes',
    tasks: 'Productivity & Kanban',
    graph: 'Semantic Knowledge Graph',
    settings: 'System & Model Settings'
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-xl px-6 flex items-center justify-between z-10">
      {/* Left: Page Title */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold text-slate-100 tracking-tight">
          {titleMap[activeTab] || 'Knowledge AI'}
        </h1>
      </div>

      {/* Middle: Command Palette Quick Search Button */}
      <div className="flex-1 max-w-md mx-6 hidden sm:block">
        <button
          onClick={() => setIsCmdKOpen(true)}
          className="w-full flex items-center justify-between px-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 text-sm text-slate-400 transition-all group shadow-inner"
        >
          <div className="flex items-center gap-2.5">
            <Search className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
            <span className="truncate">Search notes, tasks, or ask AI...</span>
          </div>
          <div className="flex items-center gap-1 text-[11px] font-mono bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/50 text-slate-400">
            <Command className="w-3 h-3" />
            <span>K</span>
          </div>
        </button>
      </div>

      {/* Right Actions & User Profile */}
      <div className="flex items-center gap-2.5">
        {/* Backend & Database Health Status Indicator */}
        <ConnectionStatusBadge />

        {/* Light / Dark Mode Toggle Button */}
        <button
          onClick={toggleTheme}
          title={theme === 'dark' ? "Switch to Light Mode" : "Switch to Dark Mode"}
          className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-amber-300 transition-all active:scale-95 flex items-center justify-center"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400 animate-in spin-in-90 duration-300" />
          ) : (
            <Moon className="w-4 h-4 text-indigo-500 animate-in spin-in-90 duration-300" />
          )}
        </button>

        <Button
          variant="secondary"
          size="sm"
          icon={Plus}
          onClick={() => createNote()}
          className="hidden sm:inline-flex"
        >
          Note
        </Button>

        <Button
          variant="secondary"
          size="sm"
          icon={CheckSquare}
          onClick={onOpenNewTaskModal}
          className="hidden sm:inline-flex"
        >
          Task
        </Button>

        {/* AI Copilot Drawer Trigger */}
        <button
          onClick={() => setIsAiDrawerOpen(!isAiDrawerOpen)}
          className={`relative flex items-center gap-2 px-3.5 py-1.5 rounded-xl font-medium text-sm transition-all duration-200 shadow-md ${
            isAiDrawerOpen
              ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 text-white shadow-indigo-500/25 ring-2 ring-indigo-400/50'
              : 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 hover:text-white border border-indigo-500/40'
          }`}
        >
          <Sparkles className="w-4 h-4 text-indigo-300 animate-spin-slow" />
          <span className="hidden sm:inline">AI Copilot</span>
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
        </button>

        {/* User Account / Sign Out / Home Controls */}
        <div className="flex items-center gap-1.5 pl-2 border-l border-slate-800">
          {currentUser ? (
            <div className="flex items-center gap-2">
              <div 
                title={`${currentUser.fullName} (${currentUser.email})`}
                className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 p-0.5 shadow-sm shrink-0"
              >
                <div className="w-full h-full bg-slate-900 rounded-[10px] flex items-center justify-center text-xs font-bold text-indigo-300">
                  {currentUser.fullName.charAt(0).toUpperCase()}
                </div>
              </div>
              <button
                onClick={requestLogout}
                title="Sign Out"
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-900 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-1">
              <span className="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[10px] font-mono">
                <Zap className="w-3 h-3 text-amber-400" />
                Demo Guest
              </span>
              <button
                onClick={requestLogout}
                title="Back to Landing Page"
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors flex items-center gap-1 text-xs"
              >
                <Home className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
