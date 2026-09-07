import React, { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useApp } from '../../context/AppContext';

export const TaskModal = ({ isOpen, onClose, onSave, initialTask = null }) => {
  const { notes, activeNote } = useApp();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('todo');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [linkedNoteId, setLinkedNoteId] = useState('');

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title || '');
      setDescription(initialTask.description || '');
      setStatus(initialTask.status || 'todo');
      setPriority(initialTask.priority || 'medium');
      setDueDate(initialTask.dueDate || '');
      setLinkedNoteId(initialTask.linkedNoteId || '');
    } else {
      setTitle('');
      setDescription('');
      setStatus('todo');
      setPriority('medium');
      setDueDate(new Date(Date.now() + 1000 * 60 * 60 * 24 * 5).toISOString().split('T')[0]);
      setLinkedNoteId(activeNote ? activeNote.id : '');
    }
  }, [initialTask, isOpen, activeNote]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const selectedNote = notes.find(n => n.id === linkedNoteId);

    const taskData = {
      ...(initialTask ? { id: initialTask.id } : {}),
      title: title.trim(),
      description: description.trim(),
      status,
      priority,
      dueDate,
      linkedNoteId: selectedNote ? selectedNote.id : null,
      linkedNoteTitle: selectedNote ? selectedNote.title : null,
      tags: initialTask?.tags || ['Task']
    };

    onSave(taskData);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialTask ? 'Edit Action Item' : 'Create New Action Item'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
            Task Title *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Optimize hybrid search latency"
            className="w-full glass-input px-3.5 py-2.5 rounded-xl text-sm placeholder-slate-500"
          />
        </div>

        {/* Description Textarea */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
            Description & Context
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add any extra specifications or context..."
            className="w-full glass-input px-3.5 py-2.5 rounded-xl text-sm placeholder-slate-500 resize-none"
          />
        </div>

        {/* Status & Priority Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Column Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full glass-input px-3.5 py-2.5 rounded-xl text-sm"
            >
              <option value="todo" className="bg-slate-900">To Do</option>
              <option value="in_progress" className="bg-slate-900">In Progress</option>
              <option value="done" className="bg-slate-900">Done</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full glass-input px-3.5 py-2.5 rounded-xl text-sm"
            >
              <option value="urgent" className="bg-slate-900 text-rose-300">Urgent</option>
              <option value="high" className="bg-slate-900 text-amber-300">High</option>
              <option value="medium" className="bg-slate-900 text-indigo-300">Medium</option>
              <option value="low" className="bg-slate-900 text-slate-300">Low</option>
            </select>
          </div>
        </div>

        {/* Due Date & Linked Document Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full glass-input px-3.5 py-2.5 rounded-xl text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Linked Document
            </label>
            <select
              value={linkedNoteId}
              onChange={(e) => setLinkedNoteId(e.target.value)}
              className="w-full glass-input px-3.5 py-2.5 rounded-xl text-sm"
            >
              <option value="" className="bg-slate-900">None</option>
              {notes.map((n) => (
                <option key={n.id} value={n.id} className="bg-slate-900">
                  {n.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary">
            {initialTask ? 'Save Changes' : 'Create Task'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
