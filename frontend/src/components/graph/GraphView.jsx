import React, { useState, useMemo } from 'react';
import { Network, Sparkles, ArrowRight } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Button } from '../common/Button';

export const GraphView = () => {
  const { notes = [], tasks = [], setActiveNoteId, setActiveTab } = useApp();
  const [selectedNode, setSelectedNode] = useState(null);

  // Generate nodes & links safely
  const { nodesData, linksData } = useMemo(() => {
    const nodes = [];
    const links = [];

    const safeNotes = notes || [];
    const safeTasks = tasks || [];

    // Note nodes (center circle)
    safeNotes.forEach((note, idx) => {
      const angle = safeNotes.length > 0 ? (idx / safeNotes.length) * 2 * Math.PI : 0;
      const radius = 180;
      nodes.push({
        id: note.id,
        title: note.title,
        type: 'note',
        category: note.category || 'General',
        x: 400 + radius * Math.cos(angle),
        y: 280 + radius * Math.sin(angle),
        raw: note
      });
    });

    // Task nodes (outer ring)
    safeTasks.forEach((task, idx) => {
      const angle = safeTasks.length > 0 ? (idx / safeTasks.length) * 2 * Math.PI + 0.3 : 0;
      const radius = 310;
      const taskNodeId = 'node-' + task.id;
      nodes.push({
        id: taskNodeId,
        title: task.title,
        type: 'task',
        priority: task.priority || 'medium',
        x: 400 + radius * Math.cos(angle),
        y: 280 + radius * Math.sin(angle),
        raw: task
      });

      // Link to note if linked
      if (task.linkedNoteId) {
        links.push({
          source: taskNodeId,
          target: task.linkedNoteId,
          type: 'task-link'
        });
      }
    });

    // Note-to-Note dynamic Jaccard tag similarity and category affinity links
    for (let i = 0; i < safeNotes.length; i++) {
      for (let j = i + 1; j < safeNotes.length; j++) {
        const tagsA = safeNotes[i].tags || [];
        const tagsB = safeNotes[j].tags || [];
        const sharedTags = tagsA.filter(t => tagsB.includes(t));
        const allTags = Array.from(new Set([...tagsA, ...tagsB]));
        const categoryMatch = Boolean(safeNotes[i].category && safeNotes[i].category === safeNotes[j].category);

        if (sharedTags.length > 0 || categoryMatch) {
          const jaccard = allTags.length > 0 ? sharedTags.length / allTags.length : 0;
          const dynamicSim = Math.min(0.95, (categoryMatch ? 0.30 : 0.0) + (jaccard * 0.65) + 0.05);
          links.push({
            source: safeNotes[i].id,
            target: safeNotes[j].id,
            type: 'similarity',
            similarity: parseFloat(dynamicSim.toFixed(2))
          });
        }
      }
    }

    return { nodesData: nodes, linksData: links };
  }, [notes, tasks]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);
  };

  const handleOpenLinkedItem = (node) => {
    if (node.type === 'note') {
      setActiveNoteId(node.raw.id);
      setActiveTab('notes');
    } else if (node.type === 'task') {
      setActiveTab('tasks');
    }
  };

  return (
    <div className="h-full flex flex-col lg:flex-row gap-6">
      {/* Interactive SVG Graph Canvas */}
      <div className="flex-1 glass-panel rounded-3xl p-6 relative overflow-hidden flex flex-col">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-2">
          <div className="flex items-center gap-2.5">
            <Network className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-semibold text-slate-100">Semantic & Relationship Graph</h3>
              <p className="text-xs text-slate-400">Semantic concept clusters & document connections</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
              Notes ({(notes || []).length})
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              Tasks ({(tasks || []).length})
            </span>
          </div>
        </div>

        {/* SVG Graph Viewport */}
        <div className="flex-1 w-full h-[520px] bg-slate-950/60 rounded-2xl border border-slate-900 flex items-center justify-center overflow-auto relative">
          {nodesData.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-200">
              <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 mb-3 shadow-inner">
                <Network className="w-7 h-7" />
              </div>
              <h4 className="text-sm font-semibold text-slate-200 mb-1">Knowledge Graph is Clean</h4>
              <p className="text-xs text-slate-400 max-w-sm mb-4">
                Create markdown notes or add Kanban tasks to generate your semantic knowledge network.
              </p>
              <Button size="sm" onClick={() => setActiveTab('notes')}>
                Create First Document
              </Button>
            </div>
          ) : (
          <svg viewBox="0 0 800 560" className="w-full h-full min-w-[600px] select-none">
            <defs>
              <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.3" />
              </linearGradient>
            </defs>

            {/* Links */}
            {linksData.map((link, idx) => {
              const src = nodesData.find(n => n.id === link.source);
              const tgt = nodesData.find(n => n.id === link.target);
              if (!src || !tgt) return null;

              const isHighlighted = 
                selectedNode && (selectedNode.id === src.id || selectedNode.id === tgt.id);

              return (
                <line
                  key={idx}
                  x1={src.x}
                  y1={src.y}
                  x2={tgt.x}
                  y2={tgt.y}
                  stroke={isHighlighted ? '#6366f1' : 'rgba(71, 85, 105, 0.35)'}
                  strokeWidth={isHighlighted ? 2.5 : 1.2}
                  strokeDasharray={link.type === 'similarity' ? '4 3' : undefined}
                  className="transition-all duration-200"
                />
              );
            })}

            {/* Nodes */}
            {nodesData.map((node) => {
              const isNote = node.type === 'note';
              const isSelected = selectedNode?.id === node.id;
              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => handleNodeClick(node)}
                  className="cursor-pointer group"
                >
                  <circle
                    r={isNote ? (isSelected ? 22 : 18) : (isSelected ? 16 : 12)}
                    fill={isNote ? '#4f46e5' : '#d97706'}
                    stroke={isSelected ? '#ffffff' : (isNote ? '#818cf8' : '#fbbf24')}
                    strokeWidth={isSelected ? 3 : 1.5}
                    className="transition-all duration-200 hover:scale-125"
                  />
                  <text
                    y={isNote ? 30 : 24}
                    textAnchor="middle"
                    className="text-[10px] font-medium fill-slate-300 pointer-events-none group-hover:fill-white font-sans"
                  >
                    {(node.title || '').slice(0, 16)}...
                  </text>
                </g>
              );
            })}
          </svg>
          )}
        </div>
      </div>

      {/* Node Inspector Sidebar */}
      <div className="w-full lg:w-80 glass-panel rounded-3xl p-5 flex flex-col justify-between shrink-0">
        <div>
          <h4 className="text-sm font-semibold text-slate-100 mb-3 flex items-center gap-2 pb-2 border-b border-slate-800">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Entity Inspector</span>
          </h4>

          {selectedNode ? (
            <div className="space-y-4 animate-in fade-in duration-150">
              <div>
                <span className="text-[10px] uppercase font-mono tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  {selectedNode.type === 'note' ? 'Document Node' : 'Task Node'}
                </span>
                <h5 className="text-base font-bold text-slate-100 mt-2">
                  {selectedNode.title}
                </h5>
              </div>

              {selectedNode.type === 'note' && (
                <div className="space-y-2 text-xs text-slate-300">
                  <p><strong className="text-slate-400">Category:</strong> {selectedNode.raw?.category || 'General'}</p>
                  <p><strong className="text-slate-400">Tags:</strong> {(selectedNode.raw?.tags || []).join(', ')}</p>
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 text-xs line-clamp-4">
                    {(selectedNode.raw?.content || '').replace(/[#*`]/g, '')}
                  </div>
                </div>
              )}

              {selectedNode.type === 'task' && (
                <div className="space-y-2 text-xs text-slate-300">
                  <p><strong className="text-slate-400">Priority:</strong> {selectedNode.raw?.priority}</p>
                  <p><strong className="text-slate-400">Status:</strong> {selectedNode.raw?.status}</p>
                  <p><strong className="text-slate-400">Due:</strong> {selectedNode.raw?.dueDate || 'None'}</p>
                  {selectedNode.raw?.linkedNoteTitle && (
                    <p><strong className="text-slate-400">Source:</strong> {selectedNode.raw.linkedNoteTitle}</p>
                  )}
                </div>
              )}

              <Button
                variant="primary"
                size="sm"
                icon={ArrowRight}
                className="w-full mt-4"
                onClick={() => handleOpenLinkedItem(selectedNode)}
              >
                Open {selectedNode.type === 'note' ? 'Document' : 'Kanban Board'}
              </Button>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 text-xs">
              Click on any node in the canvas to inspect its semantic properties and connections.
            </div>
          )}
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-[11px] text-slate-400 font-medium">
          💡 Nodes cluster together based on shared topics and semantic relationships.
        </div>
      </div>
    </div>
  );
};
