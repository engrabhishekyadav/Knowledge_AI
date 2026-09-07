import React from 'react';

export const Badge = ({ children, variant = 'default', className = '', onClick }) => {
  const variants = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    primary: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
    success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
    purple: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
    cyan: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
  };

  const Component = onClick ? 'button' : 'span';

  return (
    <Component
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${variants[variant] || variants.default} ${className}`}
    >
      {children}
    </Component>
  );
};

export const PriorityBadge = ({ priority }) => {
  const map = {
    urgent: { label: 'Urgent', variant: 'danger' },
    high: { label: 'High', variant: 'warning' },
    medium: { label: 'Medium', variant: 'primary' },
    low: { label: 'Low', variant: 'default' }
  };
  const conf = map[priority?.toLowerCase()] || map.medium;

  return <Badge variant={conf.variant}>{conf.label}</Badge>;
};
