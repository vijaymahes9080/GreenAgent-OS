import React from 'react';
import { 
  Leaf, Activity, Layers, Cpu, Globe, Zap, Sliders, Calendar, Database, Award, Settings 
} from 'lucide-react';

export type TabType = 
  | 'overview' 
  | 'workloads' 
  | 'models' 
  | 'carbon' 
  | 'energy' 
  | 'optimization' 
  | 'scheduler' 
  | 'cache' 
  | 'benchmarks' 
  | 'settings';

interface Props {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  systemStatus: string;
}

export const Navbar: React.FC<Props> = ({ activeTab, setActiveTab, systemStatus }) => {
  const navItems: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <Activity className="w-4 h-4" /> },
    { id: 'workloads', label: 'Workloads', icon: <Layers className="w-4 h-4" /> },
    { id: 'models', label: 'Models', icon: <Cpu className="w-4 h-4" /> },
    { id: 'carbon', label: 'Carbon', icon: <Globe className="w-4 h-4" /> },
    { id: 'energy', label: 'Energy', icon: <Zap className="w-4 h-4" /> },
    { id: 'optimization', label: 'Optimization', icon: <Sliders className="w-4 h-4" /> },
    { id: 'scheduler', label: 'Scheduler', icon: <Calendar className="w-4 h-4" /> },
    { id: 'cache', label: 'Cache', icon: <Database className="w-4 h-4" /> },
    { id: 'benchmarks', label: 'Benchmarks', icon: <Award className="w-4 h-4" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-emerald-400 bg-clip-text text-transparent">
                GREENAGENT OS
              </span>
              <span className="px-1.5 py-0.2 text-[10px] uppercase font-mono tracking-widest bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">
                v1.0.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Carbon-Aware AI Infrastructure</p>
          </div>
        </div>

        {/* System Pulse Indicator */}
        <div className="hidden lg:flex items-center gap-2 text-xs px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-slate-300 font-mono">Status: {systemStatus}</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400 text-[11px]">Zero GPU Req</span>
        </div>
      </div>

      {/* Navigation Pills */}
      <nav className="max-w-7xl mx-auto mt-3 flex items-center gap-1 overflow-x-auto pb-1 border-t border-slate-800/40 pt-2">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg transition-all whitespace-nowrap ${
                isActive
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};
