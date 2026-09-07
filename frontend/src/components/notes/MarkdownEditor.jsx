import React, { forwardRef } from 'react';

export const MarkdownEditor = forwardRef(({ value, onChange, onKeyDown }, ref) => {
  return (
    <div className="h-full flex flex-col bg-slate-950/30">
      <textarea
        ref={ref}
        value={value}
        onChange={onChange}
        onKeyDown={onKeyDown}
        placeholder="Start writing in Markdown..."
        className="w-full h-full p-6 bg-transparent text-slate-200 placeholder-slate-600 font-mono text-sm leading-relaxed resize-none focus:outline-none focus:ring-0 selection:bg-indigo-500/30"
        spellCheck="false"
      />
    </div>
  );
});

MarkdownEditor.displayName = 'MarkdownEditor';
