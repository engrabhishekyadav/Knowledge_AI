import React from 'react';
import { 
  FileText, 
  CheckSquare, 
  Sparkles 
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { MetricCard } from './MetricCard';
import { SmartBriefingCard } from './SmartBriefingCard';
import { RecentNotesGrid } from './RecentNotesGrid';
import { UpcomingTasksWidget } from './UpcomingTasksWidget';

export const DashboardView = ({ onOpenNewTaskModal }) => {
  const { notes, tasks, aiMessages } = useApp();

  const completedTasks = tasks.filter(t => t.status === 'done').length;
  const taskProgress = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12 animate-in fade-in duration-200">
      {/* Top Smart Briefing */}
      <SmartBriefingCard />

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Total Documents"
          value={notes.length}
          change="+2 this week"
          icon={FileText}
          color="indigo"
        />
        <MetricCard
          title="Task Completion"
          value={`${taskProgress}%`}
          change={`${completedTasks}/${tasks.length} done`}
          icon={CheckSquare}
          color="emerald"
        />
        <MetricCard
          title="AI Interactions"
          value={aiMessages.length}
          change="Real-time Copilot"
          icon={Sparkles}
          color="amber"
        />
      </div>

      {/* Main Content Split: Recent Notes & Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentNotesGrid />
        <UpcomingTasksWidget onOpenNewTaskModal={onOpenNewTaskModal} />
      </div>
    </div>
  );
};
