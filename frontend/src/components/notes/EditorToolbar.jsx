import React from 'react';
import { 
  Bold, 
  Italic, 
  Heading1, 
  Heading2, 
  Heading3, 
  Code, 
  List, 
  CheckSquare, 
  Quote, 
  Table, 
  Sparkles, 
  ListPlus, 
  Columns2, 
  Eye, 
  Edit3,
  Target
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const EditorToolbar = ({ onInsertMarkdown, viewMode, setViewMode }) => {
  const { 
    summarizeActiveNote, 
    extractTasksFromActiveNote,
    generateInterviewPrepForActiveNote
  } = useApp();

  const formatButtons = [
    { icon: Bold, title: 'Bold', action: () => onInsertMarkdown('**', '**') },
    { icon: Italic, title: 'Italic', action: () => onInsertMarkdown('*', '*') },
    { icon: Heading1, title: 'Heading 1', action: () => onInsertMarkdown('\n# ', '') },
    { icon: Heading2, title: 'Heading 2', action: () => onInsertMarkdown('\n## ', '') },
    { icon: Heading3, title: 'Heading 3', action: () => onInsertMarkdown('\n### ', '') },
    { icon: CheckSquare, title: 'Task Checkbox', action: () => onInsertMarkdown('\n- [ ] ', '') },
    { icon: List, title: 'Bullet List', action: () => onInsertMarkdown('\n- ', '') },
    { icon: Quote, title: 'Quote', action: () => onInsertMarkdown('\n> ', '') },
    { icon: Code, title: 'Code Block', action: () => onInsertMarkdown('\n```javascript\n', '\n```\n') },
    { icon: Table, title: 'Table', action: () => onInsertMarkdown('\n| Column 1 | Column 2 |\n| :--- | :--- |\n| Item 1 | Item 2 |\n', '') },
  ];

  return (
    <div className="px-4 py-2 border-b border-slate-800 bg-slate-950/80 flex flex-wrap items-center justify-between gap-2">
      {/* Markdown Format Buttons */}
      <div className="flex items-center gap-1 overflow-x-auto no-scrollbar">
        {formatButtons.map((btn, idx) => {
          const Icon = btn.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={btn.action}
              title={btn.title}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors"
            >
              <Icon className="w-4 h-4" />
            </button>
          );
        })}
      </div>

      {/* Right: AI Actions & View Mode Toggle */}
      <div className="flex items-center gap-2">
        {/* AI Action Pills */}
        <div className="hidden sm:flex items-center gap-1.5 border-r border-slate-800 pr-2 mr-1">
          {/* Interview Prep Action Button */}
          <button
            onClick={generateInterviewPrepForActiveNote}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gradient-to-r from-amber-500/15 to-orange-500/15 hover:from-amber-500/25 hover:to-orange-500/25 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-all active:scale-95 shadow-sm shadow-amber-500/10"
            title="Generate custom interview questions and model answers based on this document"
          >
            <Target className="w-3.5 h-3.5 text-amber-400" />
            <span>🎯 Interview Prep</span>
          </button>

          <button
            onClick={summarizeActiveNote}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition-all active:scale-95"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Summarize</span>
          </button>

          <button
            onClick={extractTasksFromActiveNote}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-medium transition-all active:scale-95"
          >
            <ListPlus className="w-3.5 h-3.5" />
            <span>Extract Tasks</span>
          </button>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center bg-slate-900 border border-slate-800 p-0.5 rounded-lg text-xs">
          <button
            onClick={() => setViewMode('editor')}
            title="Editor Only"
            className={`p-1 rounded ${viewMode === 'editor' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Edit3 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setViewMode('split')}
            title="Split View (Editor & Live Preview)"
            className={`p-1 rounded ${viewMode === 'split' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Columns2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setViewMode('preview')}
            title="Preview Only"
            className={`p-1 rounded ${viewMode === 'preview' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Eye className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
