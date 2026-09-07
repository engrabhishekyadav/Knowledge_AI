import React from 'react';

export const MetricCard = ({ title, value, change, icon: Icon, color = 'indigo' }) => {
  const colorMap = {
    indigo: 'from-indigo-500/20 to-purple-500/10 border-indigo-500/30 text-indigo-400',
    cyan: 'from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-400',
    emerald: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400',
    amber: 'from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400'
  };

  const style = colorMap[color] || colorMap.indigo;

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br ${style} border backdrop-blur-md relative overflow-hidden group hover:scale-[1.01] transition-all duration-200`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-4 flex items-baseline justify-between">
        <span className="text-3xl font-bold text-slate-100 tracking-tight">{value}</span>
        {change && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-900/60 text-slate-300 border border-slate-800">
            {change}
          </span>
        )}
      </div>
    </div>
  );
};
