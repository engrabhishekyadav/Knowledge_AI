import React, { useMemo } from 'react';
import { marked } from 'marked';

// Configure marked options
marked.setOptions({
  gfm: true,
  breaks: true
});

export const MarkdownPreview = ({ content }) => {
  const renderedHtml = useMemo(() => {
    try {
      return marked.parse(content || '');
    } catch {
      return '<p class="text-rose-400">Error rendering Markdown preview.</p>';
    }
  }, [content]);

  return (
    <div className="h-full overflow-y-auto p-6 bg-slate-900/40">
      <div 
        className="markdown-body max-w-none prose prose-invert prose-indigo"
        dangerouslySetInnerHTML={{ __html: renderedHtml }}
      />
    </div>
  );
};
