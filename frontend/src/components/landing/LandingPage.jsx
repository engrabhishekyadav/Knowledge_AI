import React, { useState } from 'react';
import {
  Sparkles,
  ArrowRight,
  Zap,
  FileText,
  Kanban,
  Share2,
  Target,
  Bot,
  Database,
  CheckCircle2,
  Brain,
  Cpu,
  Sun,
  Moon
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { AuthModal } from '../auth/AuthModal';

export const LandingPage = () => {
  const { enterDemoMode, theme, toggleTheme } = useApp();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  const openAuth = (mode = 'login') => {
    setAuthMode(mode);
    setIsAuthModalOpen(true);
  };


  const featureCards = [
    {
      icon: FileText,
      color: 'from-indigo-500 to-cyan-400',
      title: 'Split Markdown Engine',
      description: 'Distraction-free Markdown editor with instant live preview, table of contents, and syntax highlighting.'
    },
    {
      icon: Kanban,
      color: 'from-purple-500 to-pink-500',
      title: 'Interactive Kanban Board',
      description: 'Organize execution with To Do, In Progress, and Done with confetti celebrations.'
    },
    {
      icon: Target,
      color: 'from-amber-500 to-orange-500',
      title: 'Document AI & Interview Coach',
      description: 'Upload PDF and Word documents to automatically generate technical & behavioral interview questions with model answers.'
    },
    {
      icon: Share2,
      color: 'from-emerald-500 to-teal-400',
      title: 'Semantic Knowledge Graph',
      description: 'Visual 2D relationship network that maps interconnected documents and concept clusters automatically.'
    },
    {
      icon: Bot,
      color: 'from-blue-500 to-indigo-600',
      title: 'Persistent AI Copilot',
      description: 'Server-Sent Events (SSE) streaming assistant that preserves chat history per document in PostgreSQL.'
    },
    {
      icon: Database,
      color: 'from-rose-500 to-red-600',
      title: 'Semantic Hybrid Search',
      description: 'Dense 384-dim semantic embeddings combined with PostgreSQL full-text search for sub-10ms recall.'
    }
  ];

  const highlights = [
    'Zero-latency local NLP task extractor',
    'PostgreSQL 18 + asyncpg resilience engine',
    'OpenRouter Nemotron LLM integration',
    'Multi-format PDF, Word & Markdown ingestion',
    'Document-scoped persistent AI chat threads',
    'Global Ctrl+K Command Palette navigation'
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white flex flex-col font-sans overflow-x-hidden">
      {/* Background Ambient Glows */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-10%] left-[20%] w-[600px] h-[600px] rounded-full bg-indigo-600/15 blur-[140px]" />
        <div className="absolute top-[35%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple-600/10 blur-[130px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full bg-cyan-500/10 blur-[150px]" />
      </div>

      {/* Top Navigation */}
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-400 p-0.5 shadow-md shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
            </div>
            <div>
              <span className="text-base font-bold tracking-tight bg-gradient-to-r from-slate-100 via-slate-200 to-slate-400 bg-clip-text text-transparent">
                KnowledgeAI
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Light / Dark Mode Toggle */}
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

            <button
              onClick={enterDemoMode}
              className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/60 text-xs text-slate-300 hover:text-white transition-all font-medium"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Explore Demo</span>
            </button>

            <button
              onClick={() => openAuth('login')}
              className="px-4 py-1.5 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
            >
              Sign In
            </button>

            <button
              onClick={() => openAuth('signup')}
              className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/25 transition-all active:scale-95 flex items-center gap-1.5"
            >
              <span>Get Started</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 z-10">
        {/* Hero Section */}
        <section className="pt-20 pb-16 px-6 max-w-5xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium animate-in fade-in slide-in-from-bottom-3 duration-500">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-spin" style={{ animationDuration: '6s' }} />
            <span>Next-Generation AI Productivity & Career Operating System</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] text-slate-100 max-w-4xl mx-auto">
            Your Autonomous{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Second Brain
            </span>{' '}
            & Task Workspace
          </h1>

          <p className="text-sm sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Combine Split-View Markdown, Interactive Kanban, 2D Semantic Knowledge Graphs, and an AI Copilot that prepares you for interviews and executes tasks automatically.
          </p>

          {/* CTA Group */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <button
              onClick={() => openAuth('signup')}
              className="px-7 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold shadow-xl shadow-indigo-600/30 flex items-center gap-2 transition-all hover:scale-105 active:scale-95"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={enterDemoMode}
              className="px-6 py-3.5 rounded-2xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 text-slate-200 hover:text-white text-sm font-semibold flex items-center gap-2 transition-all active:scale-95 shadow-md"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Launch Interactive Demo</span>
            </button>
          </div>

          {/* Architecture Badges */}
          <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400 border-t border-slate-900/80">
            <div className="flex items-center gap-1.5">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>PostgreSQL 18 Database</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>FastAPI Async Engine</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Brain className="w-4 h-4 text-purple-400" />
              <span>OpenRouter Nemotron LLM</span>
            </div>
          </div>
        </section>

        {/* Feature Grid Section */}
        <section className="py-20 px-6 max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-14 space-y-3">
            <h2 className="text-2xl sm:text-4xl font-bold text-slate-100">
              Engineered for Deep Work & Fast Execution
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Everything you need to write structured documentation, track deliverables, map relationships, and prepare for interviews.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featureCards.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  className="p-6 rounded-3xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-500/5 group"
                >
                  <div className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${feat.color} p-0.5 shadow-md mb-5 group-hover:scale-110 transition-transform`}>
                    <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                      <Icon className="w-6 h-6 text-slate-100" />
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-slate-100 mb-2">
                    {feat.title}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                    {feat.description}
                  </p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Capabilities Checklist */}
        <section className="py-16 px-6 max-w-5xl mx-auto bg-slate-900/30 border border-slate-800/80 rounded-3xl mb-20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center p-4 sm:p-8">
            <div className="space-y-4">
              <span className="text-[11px] font-mono uppercase tracking-wider text-indigo-400">
                Enterprise Foundations
              </span>
              <h3 className="text-2xl sm:text-3xl font-bold text-slate-100">
                Built from the ground up with resilient architecture
              </h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Connect seamlessly to your PostgreSQL server with native pgvector cosine indexing and hybrid search.
              </p>
              <div className="pt-2">
                <button
                  onClick={enterDemoMode}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 transition-all active:scale-95 shadow-md shadow-indigo-600/20"
                >
                  <span>Launch Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {highlights.map((item, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-2xl bg-slate-950/60 border border-slate-800/60 text-xs sm:text-sm text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-8 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-slate-300">KnowledgeAI Platform</span>
            <span>• Full-Stack AI Second Brain</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <button onClick={enterDemoMode} className="hover:text-slate-200 transition-colors">Demo Mode</button>
            <button onClick={() => openAuth('login')} className="hover:text-slate-200 transition-colors">Sign In</button>
            <button onClick={() => openAuth('signup')} className="hover:text-slate-200 transition-colors">Sign Up</button>
          </div>
        </div>
      </footer>

      {/* Auth Modal Popup */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode={authMode}
      />
    </div>
  );
};
