import React from 'react';
import { Sparkles, Zap } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Button } from '../common/Button';

export const SmartBriefingCard = () => {
  const { notes, tasks, setIsAiDrawerOpen, sendAiMessage } = useApp();

  const pendingTasks = tasks.filter(t => t.status !== 'done');
  const urgentTasks = tasks.filter(t => t.priority === 'urgent' && t.status !== 'done');

  return (
    <div className="relative p-6 rounded-3xl bg-gradient-to-r from-indigo-950/70 via-slate-900/90 to-purple-950/60 border border-indigo-500/30 backdrop-blur-xl shadow-xl overflow-hidden">
      {/* Background glow orb */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI Workspace Morning Briefing</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">
            You have {pendingTasks.length} active tasks and {notes.length} synchronized knowledge documents.
          </h2>
          <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
            {urgentTasks.length > 0 ? (
              <span className="text-rose-300 font-medium">
                ⚠️ Attention: {urgentTasks.length} urgent task ({urgentTasks[0].title}) requires immediate focus.
              </span>
            ) : (
              'All tasks and knowledge documents are progressing smoothly.'
            )}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <Button
            variant="ai"
            size="md"
            icon={Zap}
            onClick={() => {
              setIsAiDrawerOpen(true);
              sendAiMessage("Give me a comprehensive productivity roadmap for today based on my active tasks and notes.");
            }}
          >
            Generate Daily Roadmap
          </Button>
        </div>
      </div>
    </div>
  );
};
