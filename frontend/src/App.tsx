import React, { useState, useEffect } from 'react';
import { Navbar, TabType } from './components/Navbar';
import { OverviewTab } from './pages/OverviewTab';
import { WorkloadsTab } from './pages/WorkloadsTab';
import { ModelsTab } from './pages/ModelsTab';
import { CarbonTab } from './pages/CarbonTab';
import { EnergyTab } from './pages/EnergyTab';
import { OptimizationTab } from './pages/OptimizationTab';
import { SchedulerTab } from './pages/SchedulerTab';
import { CacheTab } from './pages/CacheTab';
import { BenchmarksTab } from './pages/BenchmarksTab';
import { SettingsTab } from './pages/SettingsTab';
import { api, ModelProfile, TelemetryTrace, RegionCarbon, CacheStats, BenchmarkData } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [systemStatus, setSystemStatus] = useState<string>('Online');
  const [models, setModels] = useState<ModelProfile[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryTrace[]>([]);
  const [regions, setRegions] = useState<RegionCarbon[]>([]);
  const [cacheStats, setCacheStats] = useState<CacheStats>({
    total_entries: 0, aggregate_hits: 0, total_tokens_saved: 0, total_joules_saved: 0, total_co2e_grams_saved: 0, entries: []
  });
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);

  const loadData = async () => {
    try {
      const [h, m, t, r, c, b] = await Promise.all([
        api.getHealth(),
        api.getModels(),
        api.getTelemetry(),
        api.getRegions(),
        api.getCacheStats(),
        api.getLatestBenchmark()
      ]);
      setSystemStatus(h.status === 'healthy' ? 'Operational' : 'Degraded');
      setModels(m);
      setTelemetry(t);
      setRegions(r);
      setCacheStats(c);
      setBenchmark(b);
    } catch {
      setSystemStatus('Simulated Mode');
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      api.getTelemetry().then(setTelemetry).catch(() => {});
      api.getCacheStats().then(setCacheStats).catch(() => {});
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} systemStatus={systemStatus} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'overview' && (
          <OverviewTab benchmark={benchmark} telemetry={telemetry} onNavigate={setActiveTab} />
        )}
        {activeTab === 'workloads' && (
          <WorkloadsTab telemetry={telemetry} onRefreshTelemetry={loadData} />
        )}
        {activeTab === 'models' && (
          <ModelsTab models={models} />
        )}
        {activeTab === 'carbon' && (
          <CarbonTab regions={regions} />
        )}
        {activeTab === 'energy' && (
          <EnergyTab />
        )}
        {activeTab === 'optimization' && (
          <OptimizationTab />
        )}
        {activeTab === 'scheduler' && (
          <SchedulerTab />
        )}
        {activeTab === 'cache' && (
          <CacheTab cacheStats={cacheStats} onRefresh={loadData} />
        )}
        {activeTab === 'benchmarks' && (
          <BenchmarksTab benchmark={benchmark} onBenchmarkUpdated={setBenchmark} />
        )}
        {activeTab === 'settings' && (
          <SettingsTab />
        )}
      </main>

      <footer className="glass-panel border-t border-slate-800/60 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>GREENAGENT OS — Production-Quality AI Optimization Infrastructure</span>
          <span className="font-mono text-[11px] text-slate-400">
            Open-Source • Zero GPU Mandate • Transparent Hardware Provenance
          </span>
        </div>
      </footer>
    </div>
  );
};
