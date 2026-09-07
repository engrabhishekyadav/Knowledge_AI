import React from 'react';
import { 
  LayoutDashboard, 
  FileText, 
  CheckSquare, 
  Network, 
  Settings, 
  Sparkles, 
  ChevronLeft, 
  ChevronRight,
  LogOut,
  Plus
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const Sidebar = () => {
  const { 
    activeTab, 
    setActiveTab, 
    sidebarCollapsed, 
    setSidebarCollapsed,
    notes,
    tasks,
    createNote,
    currentUser,
    isDemoMode,
    requestLogout
  } = useApp();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'notes', label: 'Notes & Docs', icon: FileText, badge: notes.length },
    { id: 'tasks', label: 'Kanban Tasks', icon: CheckSquare, badge: tasks.filter(t => t.status !== 'done').length },
    { id: 'graph', label: 'Knowledge Graph', icon: Network, badge: null },
    { id: 'settings', label: 'Settings', icon: Settings, badge: null },
  ];

  return (
    <aside 
      className={`relative flex flex-col h-screen transition-all duration-300 ease-in-out border-r border-slate-800/80 bg-slate-950/80 backdrop-blur-xl z-20 ${
        sidebarCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between px-4 h-16 border-b border-slate-800/80">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 shrink-0">
            <div className="flex items-center justify-center w-full h-full bg-slate-950 rounded-[10px]">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          {!sidebarCollapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight bg-gradient-to-r from-indigo-300 via-purple-300 to-cyan-300 bg-clip-text text-transparent truncate">
                KnowledgeAI
              </span>
              <span className="text-[11px] text-slate-400 font-medium truncate">
                Workspace OS
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Quick Action */}
      {!sidebarCollapsed && (
        <div className="p-3">
          <button
            onClick={() => createNote()}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all duration-150 active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            New Document
          </button>
        </div>
      )}

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-2 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              title={sidebarCollapsed ? item.label : undefined}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60 border border-transparent'
              } ${sidebarCollapsed ? 'justify-center px-0' : ''}`}
            >
              <Icon className={`w-5 h-5 shrink-0 transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
              {!sidebarCollapsed && (
                <>
                  <span className="truncate flex-1 text-left">{item.label}</span>
                  {item.badge !== null && item.badge > 0 && (
                    <span className={`text-[11px] px-2 py-0.5 rounded-full font-semibold ${
                      isActive ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom User Profile & Collapse Footer */}
      <div className="p-3 border-t border-slate-800/80 space-y-2">
        {!sidebarCollapsed ? (
          <div className="p-2 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="relative w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-cyan-500 p-0.5 shadow-sm shrink-0">
                <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center text-xs font-bold text-indigo-300">
                  {currentUser?.fullName ? currentUser.fullName.charAt(0).toUpperCase() : (isDemoMode ? 'G' : 'U')}
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-slate-950"></span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-200 truncate" title={currentUser?.fullName || (isDemoMode ? 'Guest Demo User' : 'Workspace User')}>
                  {currentUser?.fullName || (isDemoMode ? 'Guest Demo User' : 'Workspace User')}
                </p>
                <p className="text-[10px] text-slate-400 truncate">
                  {currentUser?.email || (isDemoMode ? 'Demo Workspace' : 'Online')}
                </p>
              </div>
            </div>
            <button
              onClick={requestLogout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors shrink-0"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex justify-center">
            <button
              onClick={requestLogout}
              title={`Logged in as ${currentUser?.fullName || (isDemoMode ? 'Guest User' : 'Workspace User')} - Click to Sign Out`}
              className="relative w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-cyan-500 p-0.5 shadow-sm hover:scale-105 transition-transform"
            >
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center text-xs font-bold text-indigo-300">
                {currentUser?.fullName ? currentUser.fullName.charAt(0).toUpperCase() : (isDemoMode ? 'G' : 'U')}
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-slate-950"></span>
            </button>
          </div>
        )}

        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="w-full flex items-center justify-center p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors"
          title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
};
