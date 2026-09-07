import React, { useState, useRef, useEffect } from 'react';
import { 
  Sparkles, 
  X, 
  Send, 
  Bot, 
  User, 
  ListPlus, 
  FileText, 
  Zap, 
  Trash2,
  BookmarkPlus,
  Copy,
  Check,
  ArrowDownToLine,
  Brain,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Button } from '../common/Button';
import { marked } from 'marked';

export const AiDrawer = () => {
  const {
    isAiDrawerOpen,
    setIsAiDrawerOpen,
    aiMessages,
    isLoadingChatHistory,
    isStreaming,
    sendAiMessage,
    clearAiChatHistory,
    saveChatAsNote,
    activeNote,
    updateNote,
    executeAiAction,
    showToast
  } = useApp();

  const [inputPrompt, setInputPrompt] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isAiDrawerOpen) {
      scrollToBottom();
    }
  }, [aiMessages, isAiDrawerOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isStreaming) return;
    sendAiMessage(inputPrompt);
    setInputPrompt('');
  };

  const handleCopyText = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    showToast('Copied to clipboard', 'info');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleInsertIntoNote = (text) => {
    if (!activeNote) {
      showToast('No active note selected', 'warning');
      return;
    }
    const updatedContent = activeNote.content + '\n\n' + text;
    updateNote(activeNote.id, { content: updatedContent });
    showToast(`Inserted AI response into "${activeNote.title}"`, 'success');
  };

  const quickPrompts = [
    { 
      label: '🎯 Top Interview Questions', 
      prompt: activeNote 
        ? `Analyze "${activeNote.title}" and generate 10 targeted interview questions with clear, structured model answers and key takeaways.` 
        : 'Generate 10 top technical interview questions with clear model answers.' 
    },
    { 
      label: '📋 Extract Action Items', 
      prompt: activeNote 
        ? `Extract all actionable tasks, deliverables, and next steps from "${activeNote.title}" for Kanban.` 
        : 'Extract actionable tasks from my current notes.' 
    },
    { 
      label: '📝 Comprehensive Summary', 
      prompt: activeNote 
        ? `Provide a comprehensive, in-depth breakdown and executive summary of "${activeNote.title}".` 
        : 'Summarize my workspace notes in detail.' 
    },
    { 
      label: '💡 Knowledge Assessment', 
      prompt: activeNote 
        ? `Create an in-depth self-assessment quiz with detailed solutions based on "${activeNote.title}".` 
        : 'Create a conceptual knowledge quiz with detailed solutions.' 
    }
  ];

  if (!isAiDrawerOpen) return null;

  return (
    <>
      {/* Backdrop overlay when expanded to large mode */}
      {isExpanded && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 transition-opacity animate-in fade-in duration-200"
          onClick={() => setIsExpanded(false)}
        />
      )}

      <div 
        className={`fixed inset-y-0 right-0 z-50 bg-slate-950/95 border-l border-slate-800 shadow-2xl backdrop-blur-2xl flex flex-col transition-all duration-300 ease-in-out ${
          isExpanded 
            ? 'w-full md:w-[85vw] lg:w-[75vw] xl:w-[70vw] max-w-[1250px]' 
            : 'w-full sm:w-[480px]'
        }`}
      >
        {/* Drawer Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/70 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 p-0.5 shadow-md shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[6px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-slate-100">AI Copilot</h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 font-mono flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                  Gemini Flash
                </span>
                {isExpanded && (
                  <span className="hidden sm:inline-flex text-[10px] px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-medium">
                    Expanded View
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 truncate max-w-[210px] sm:max-w-xs flex items-center gap-1">
                <FileText className="w-3 h-3 text-indigo-400 shrink-0" />
                <span>{activeNote ? activeNote.title : 'Workspace General'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            {/* Maximize / Minimize Button */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? "Collapse to small size" : "Expand screen (Large view)"}
              className={`p-1.5 rounded-lg transition-colors ${
                isExpanded 
                  ? 'text-cyan-400 bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30' 
                  : 'text-slate-400 hover:text-indigo-300 hover:bg-slate-800'
              }`}
            >
              {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={saveChatAsNote}
              title="Save conversation as new Markdown Note"
              className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-300 hover:bg-slate-800 transition-colors"
            >
              <BookmarkPlus className="w-4 h-4" />
            </button>
            <button
              onClick={clearAiChatHistory}
              title="Clear Chat History for this Document"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setIsAiDrawerOpen(false);
                setIsExpanded(false);
              }}
              title="Close Drawer"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
          <div className={`space-y-4 ${isExpanded ? 'max-w-4xl mx-auto w-full' : 'w-full'}`}>
            {isLoadingChatHistory ? (
          <div className="space-y-4 py-8">
            <div className="flex items-center justify-center gap-2 text-xs text-indigo-300 animate-pulse">
              <Brain className="w-4 h-4 animate-spin text-indigo-400" />
              <span>Loading conversation history...</span>
            </div>
            <div className="h-16 rounded-xl bg-slate-900/60 border border-slate-800 animate-pulse"></div>
            <div className="h-24 rounded-xl bg-slate-900/60 border border-slate-800 animate-pulse"></div>
          </div>
        ) : (
          aiMessages.map((msg) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-xs font-semibold ${
                    isUser
                      ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                      : 'bg-gradient-to-tr from-purple-600 to-cyan-500 text-white shadow-sm shadow-purple-500/20'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div className="max-w-[85%] space-y-2">
                  <div
                    className={`p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                      isUser
                        ? 'bg-indigo-600 text-white rounded-tr-sm shadow-md'
                        : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-sm shadow-sm'
                    }`}
                  >
                    <div
                      className="markdown-body prose prose-invert text-xs sm:text-sm"
                      dangerouslySetInnerHTML={{ __html: marked.parse(msg.text || '') }}
                    />

                    {/* Footer Controls & Timestamp */}
                    <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-800/40 text-[10px]">
                      <div className="flex items-center gap-1">
                        {!isUser && (
                          <>
                            <button
                              onClick={() => handleCopyText(msg.id, msg.text)}
                              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1"
                              title="Copy text"
                            >
                              {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                              <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                            </button>
                            {activeNote && (
                              <button
                                onClick={() => handleInsertIntoNote(msg.text)}
                                className="p-1 rounded hover:bg-slate-800 text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
                                title="Insert directly into active note"
                              >
                                <ArrowDownToLine className="w-3 h-3" />
                                <span>Insert to Note</span>
                              </button>
                            )}
                          </>
                        )}
                      </div>
                      <span className={isUser ? 'text-indigo-200' : 'text-slate-500'}>
                        {msg.timestamp}
                      </span>
                    </div>
                  </div>

                  {/* Interactive Action Preview Cards */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="space-y-2 pt-1">
                      {msg.actions.map((act, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-xs text-slate-200 space-y-2"
                        >
                          <div className="flex items-center gap-1.5 text-indigo-300 font-semibold">
                            <Zap className="w-3.5 h-3.5" />
                            <span>Action Ready</span>
                          </div>
                          {act.type === 'ADD_TASKS' && (
                            <div className="space-y-1">
                              {act.payload.slice(0, 3).map((t, idx) => (
                                <div key={idx} className="flex items-center gap-1.5 text-[11px] text-slate-300">
                                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                                  <span className="truncate">{t.title}</span>
                                </div>
                              ))}
                              {act.payload.length > 3 && (
                                <p className="text-[10px] text-slate-400">
                                  + {act.payload.length - 3} more items
                                </p>
                              )}
                            </div>
                          )}
                          <Button
                            variant="ai"
                            size="sm"
                            icon={ListPlus}
                            className="w-full text-xs"
                            onClick={() => executeAiAction(act)}
                          >
                            {act.label}
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Prompts Chips */}
      <div className="px-4 sm:px-6 py-2 border-t border-slate-800/80 bg-slate-900/40">
        <div className={`flex items-center gap-2 overflow-x-auto no-scrollbar ${isExpanded ? 'max-w-4xl mx-auto' : ''}`}>
          {quickPrompts.map((qp, idx) => (
            <button
              key={idx}
              disabled={isStreaming}
              onClick={() => sendAiMessage(qp.prompt)}
              className="whitespace-nowrap px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-[11px] text-slate-300 hover:text-white border border-slate-700/60 transition-all shrink-0 active:scale-95 disabled:opacity-50"
            >
              {qp.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-4 sm:p-6 border-t border-slate-800 bg-slate-900/60">
        <div className={`flex items-center gap-2 ${isExpanded ? 'max-w-4xl mx-auto' : ''}`}>
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            disabled={isStreaming}
            placeholder={isStreaming ? "AI is reasoning & typing..." : "Ask AI or generate interview questions..."}
            className="flex-1 glass-input px-3.5 py-2.5 rounded-xl text-xs sm:text-sm placeholder-slate-500 focus:outline-none"
          />
          <Button
            type="submit"
            variant="ai"
            size="md"
            disabled={!inputPrompt.trim() || isStreaming}
            icon={Send}
            className="shrink-0"
          />
        </div>
      </form>
    </div>
  </>
);
};
