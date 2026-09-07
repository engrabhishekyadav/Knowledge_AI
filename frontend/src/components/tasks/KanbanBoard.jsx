import React, { useState } from 'react';
import { KanbanColumn } from './KanbanColumn';
import { TaskModal } from './TaskModal';
import { useApp } from '../../context/AppContext';

export const KanbanBoard = ({ searchQuery, priorityFilter, tagFilter }) => {
  const { tasks, createTask, updateTask, moveTaskStatus } = useApp();
  
  const [editingTask, setEditingTask] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [defaultStatusForNew, setDefaultStatusForNew] = useState('todo');

  const columns = [
    { id: 'todo', title: 'To Do' },
    { id: 'in_progress', title: 'In Progress' },
    { id: 'done', title: 'Done' }
  ];

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = 
      !searchQuery || 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesPriority = 
      priorityFilter === 'ALL' || 
      task.priority?.toLowerCase() === priorityFilter.toLowerCase();

    const matchesTag = 
      tagFilter === 'ALL' || 
      task.tags?.includes(tagFilter);

    return matchesSearch && matchesPriority && matchesTag;
  });

  const handleOpenAdd = (statusId) => {
    setDefaultStatusForNew(statusId);
    setEditingTask(null);
    setIsModalOpen(true);
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleSave = (taskData) => {
    if (editingTask) {
      updateTask(editingTask.id, taskData);
    } else {
      createTask({ ...taskData, status: defaultStatusForNew });
    }
    setIsModalOpen(false);
  };

  return (
    <div className="flex-1 flex gap-4 overflow-x-auto pb-4 pt-1 h-[calc(100vh-210px)]">
      {columns.map((col) => {
        const colTasks = filteredTasks.filter(t => t.status === col.id);
        return (
          <KanbanColumn
            key={col.id}
            column={col}
            tasks={colTasks}
            onAddTask={handleOpenAdd}
            onEditTask={handleEdit}
            onMoveTask={moveTaskStatus}
          />
        );
      })}

      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        initialTask={editingTask}
      />
    </div>
  );
};
