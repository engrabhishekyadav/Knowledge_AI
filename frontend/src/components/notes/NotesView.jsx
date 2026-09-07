import React, { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { NoteList } from './NoteList';
import { NoteMetadataBar } from './NoteMetadataBar';
import { EditorToolbar } from './EditorToolbar';
import { MarkdownEditor } from './MarkdownEditor';
import { MarkdownPreview } from './MarkdownPreview';
import { FileText, Plus } from 'lucide-react';
import { Button } from '../common/Button';

export const NotesView = () => {
  const { activeNote, updateNote, createNote } = useApp();
  const [viewMode, setViewMode] = useState('split'); // 'split' | 'editor' | 'preview'
  const editorRef = useRef(null);

  const handleContentChange = (e) => {
    if (activeNote) {
      updateNote(activeNote.id, { content: e.target.value });
    }
  };

  const handleInsertMarkdown = (prefix, suffix = '') => {
    if (!editorRef.current || !activeNote) return;
    const textarea = editorRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selection = text.substring(start, end);

    const replacement = prefix + (selection || 'text') + suffix;
    const newContent = text.substring(0, start) + replacement + text.substring(end);

    updateNote(activeNote.id, { content: newContent });

    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        start + prefix.length + (selection ? selection.length : 4)
      );
    }, 10);
  };

  return (
    <div className="h-full flex rounded-3xl border border-slate-800 bg-slate-950/60 backdrop-blur-xl overflow-hidden shadow-2xl">
      {/* Left Column: Note List */}
      <NoteList />

      {/* Main Column: Editor & Preview */}
      {activeNote ? (
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {/* Note Metadata Bar */}
          <NoteMetadataBar />

          {/* Formatting & AI Action Toolbar */}
          <EditorToolbar
            onInsertMarkdown={handleInsertMarkdown}
            viewMode={viewMode}
            setViewMode={setViewMode}
          />

          {/* Split / Editor / Preview Body */}
          <div className="flex-1 grid grid-cols-1 overflow-hidden relative">
            {viewMode === 'split' && (
              <div className="grid grid-cols-1 md:grid-cols-2 h-full divide-y md:divide-y-0 md:divide-x divide-slate-800 overflow-hidden">
                <MarkdownEditor
                  ref={editorRef}
                  value={activeNote.content}
                  onChange={handleContentChange}
                />
                <MarkdownPreview content={activeNote.content} />
              </div>
            )}

            {viewMode === 'editor' && (
              <MarkdownEditor
                ref={editorRef}
                value={activeNote.content}
                onChange={handleContentChange}
              />
            )}

            {viewMode === 'preview' && (
              <MarkdownPreview content={activeNote.content} />
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
          <div className="w-16 h-16 rounded-3xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mb-4">
            <FileText className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-slate-200 mb-2">No Document Selected</h3>
          <p className="text-sm text-slate-400 max-w-sm mb-6">
            Choose an existing document from the left list or create a new markdown note.
          </p>
          <Button icon={Plus} onClick={() => createNote()}>
            Create First Document
          </Button>
        </div>
      )}
    </div>
  );
};
