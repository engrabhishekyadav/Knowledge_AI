import React, { useState, useEffect } from 'react';
import { Database, WifiOff } from 'lucide-react';

export const ConnectionStatusBadge = () => {
  const [status, setStatus] = useState({
    online: false,
    dbEngine: 'checking',
    llmModel: ''
  });

  useEffect(() => {
    let isMounted = true;

    const checkHealth = async () => {
      try {
        const res = await fetch('/api/v1/health', { method: 'GET' });
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setStatus({
              online: true,
              dbEngine: data.dbEngine || 'active',
              llmModel: data.llmModel || ''
            });
          }
          return;
        }
      } catch {
        // Backend offline or local fallback
      }
      if (isMounted) {
        setStatus({
          online: false,
          dbEngine: 'local_storage',
          llmModel: 'local_generator'
        });
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div 
      title={
        status.online 
          ? `Backend Connected: PostgreSQL 16 + pgvector (${status.llmModel || 'Active'})`
          : 'Backend Offline: Ensure PostgreSQL & FastAPI Backend are running'
      }
      className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-900/90 border border-slate-800 text-[11px] font-mono cursor-default shadow-sm transition-all"
    >
      {status.online ? (
        <>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="flex items-center gap-1 text-emerald-400 font-medium">
            <Database className="w-3 h-3 text-emerald-400" />
            PostgreSQL pgvector
          </span>
        </>
      ) : (
        <>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
          <span className="flex items-center gap-1 text-amber-400 font-medium">
            <WifiOff className="w-3 h-3 text-amber-400" />
            Local
          </span>
        </>
      )}
    </div>
  );
};
