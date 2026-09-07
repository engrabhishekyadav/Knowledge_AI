import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AiDrawer } from './AiDrawer';
import { CommandPalette } from './CommandPalette';
import { Toast } from '../common/Toast';
import { TaskModal } from '../tasks/TaskModal';
import { LogoutConfirmModal } from '../common/LogoutConfirmModal';
import { useApp } from '../../context/AppContext';

import { DashboardView } from '../dashboard/DashboardView';
import { NotesView } from '../notes/NotesView';
import { TasksView } from '../tasks/TasksView';
import { GraphView } from '../graph/GraphView';
import { SettingsView } from '../settings/SettingsView';

export const AppLayout = () => {
  const { 
    activeTab, 
    createTask, 
    isLogoutModalOpen, 
    setIsLogoutModalOpen, 
    confirmLogout,
    currentUser,
    isDemoMode
  } = useApp();
  const [isNewTaskModalOpen, setIsNewTaskModalOpen] = useState(false);

  const handleSaveNewTask = (taskData) => {
    createTask(taskData);
    setIsNewTaskModalOpen(false);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">
      {/* Collapsible Left Sidebar */}
      <Sidebar />

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header onOpenNewTaskModal={() => setIsNewTaskModalOpen(true)} />

        <main className="flex-1 overflow-y-auto relative p-6 bg-radial-gradient">
          {activeTab === 'dashboard' && <DashboardView onOpenNewTaskModal={() => setIsNewTaskModalOpen(true)} />}
          {activeTab === 'notes' && <NotesView />}
          {activeTab === 'tasks' && <TasksView onOpenNewTaskModal={() => setIsNewTaskModalOpen(true)} />}
          {activeTab === 'graph' && <GraphView />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>

      {/* Slide-over AI Copilot Drawer */}
      <AiDrawer />

      {/* Global Ctrl+K Command Palette */}
      <CommandPalette />

      {/* Global Notifications */}
      <Toast />

      {/* Global New Task Modal */}
      <TaskModal
        isOpen={isNewTaskModalOpen}
        onClose={() => setIsNewTaskModalOpen(false)}
        onSave={handleSaveNewTask}
      />

      {/* Logout Confirmation Modal */}
      <LogoutConfirmModal
        isOpen={isLogoutModalOpen}
        onClose={() => setIsLogoutModalOpen(false)}
        onConfirm={confirmLogout}
        userName={currentUser?.fullName}
        isDemo={isDemoMode}
      />
    </div>
  );
};
