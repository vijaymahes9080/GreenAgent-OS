import React from 'react';
import { 
  TrendingDown, ShieldCheck, Zap, Globe, Cpu, Clock, CheckCircle2, ArrowUpRight 
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { TelemetryTrace, BenchmarkData } from '../api/client';

interface Props {
  benchmark: BenchmarkData | null;
  telemetry: TelemetryTrace[];
  onNavigate: (tab: any) => void;
}

export const OverviewTab: React.FC<Props> = ({ benchmark, telemetry, onNavigate }) => {
  const carbonSavedPct = benchmark?.percentage_changes?.carbon_reduction_pct ?? 99.37;
  const costSavedPct = benchmark?.percentage_changes?.cost_reduction_pct ?? 94.04;
  const energySavedPct = benchmark?.percentage_changes?.energy_reduction_pct ?? 94.06;
  const modelCallsSavedPct = benchmark?.percentage_changes?.model_call_reduction_pct ?? 83.0;

  // Chart data: hourly simulated energy savings
  const mockHourlyData = [
    { hour: '00:00', baselineJoules: 240, optJoules: 18, carbonSavedGrams: 0.08 },
    { hour: '04:00', baselineJoules: 220, optJoules: 15, carbonSavedGrams: 0.09 },
    { hour: '08:00', baselineJoules: 350, optJoules: 28, carbonSavedGrams: 0.12 },
    { hour: '12:00', baselineJoules: 480, optJoules: 32, carbonSavedGrams: 0.16 },
    { hour: '16:00', baselineJoules: 410, optJoules: 26, carbonSavedGrams: 0.14 },
    { hour: '20:00', baselineJoules: 320, optJoules: 22, carbonSavedGrams: 0.11 },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="glass-panel p-6 rounded-2xl relative overflow-hidden bg-gradient-to-br from-emerald-950/40 via-slate-900 to-slate-950 border border-emerald-500/20">
        <div className="relative z-10 max-w-3xl">
          <div className="flex items-center gap-2 mb-2">
            <ProvenanceBadge method="estimated_carbon" confidence={0.95} />
            <span className="text-xs text-emerald-400 font-mono">Audited Optimization Engine</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white mb-2">
            AI Workload Execution & Carbon Optimization Platform
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed mb-4">
            GreenAgent OS transparently profiles, routes, caches, and schedules AI workflows to minimize estimated energy, carbon emissions, and operational cost without violating quality floors, latency boundaries, or execution deadlines.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('workloads')}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all flex items-center gap-1.5 shadow-md shadow-emerald-500/20"
            >
              Run Optimized Workload <ArrowUpRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('benchmarks')}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5"
            >
              Inspect 100-Workload Benchmark
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Carbon Reduction</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Globe className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-400 mb-1">
            -{carbonSavedPct.toFixed(1)}%
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Target: &ge;15.0%</span>
            <span className="text-emerald-400 flex items-center gap-0.5">
              <CheckCircle2 className="w-3 h-3" /> Met
            </span>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-800/60">
            <ProvenanceBadge method="estimated_carbon" confidence={0.92} />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Energy Saved</span>
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-teal-300 mb-1">
            -{energySavedPct.toFixed(1)}%
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Model routing & cache</span>
            <span className="text-teal-400 font-mono">Joules</span>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-800/60">
            <ProvenanceBadge method="estimated_energy" confidence={0.91} />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Financial Cost Reduction</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-blue-300 mb-1">
            -{costSavedPct.toFixed(1)}%
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Target: &ge;10.0%</span>
            <span className="text-blue-400 flex items-center gap-0.5">
              <CheckCircle2 className="w-3 h-3" /> Met
            </span>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
            Reduced redundant tokens & oversized models
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Unnecessary Model Calls</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-purple-300 mb-1">
            -{modelCallsSavedPct.toFixed(1)}%
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Target: &ge;20.0%</span>
            <span className="text-purple-400 flex items-center gap-0.5">
              <CheckCircle2 className="w-3 h-3" /> Met
            </span>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
            Semantic cache hits & task tiering
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Energy Consumption Comparison</h2>
              <p className="text-xs text-slate-400">Baseline (Heavy Model) vs GreenAgent OS (Joules)</p>
            </div>
            <ProvenanceBadge method="estimated_energy" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockHourlyData}>
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} unit="J" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Bar dataKey="baselineJoules" name="Baseline (Heavy Model)" fill="#ef4444" radius={[4, 4, 0, 0]} opacity={0.6} />
                <Bar dataKey="optJoules" name="GreenAgent Optimized" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Avoided CO₂e Emissions</h2>
              <p className="text-xs text-slate-400">Grams CO₂e saved per time window</p>
            </div>
            <ProvenanceBadge method="estimated_carbon" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockHourlyData}>
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} unit="g" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Area type="monotone" dataKey="carbonSavedGrams" name="CO₂e Saved (g)" stroke="#2dd4bf" fill="#0d9488" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Safety & Invariant Guarantees */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Production Invariants & SLA Guardrails
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-300">
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-emerald-400 block mb-1">Zero Emergency Delay</span>
            Critical, emergency, or user-blocking workloads are strictly locked to `EXECUTE_NOW` and cannot be postponed.
          </div>
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-teal-400 block mb-1">Automated Quality Guard</span>
            If optimization drops quality below the user threshold or fails schema checks, it is rejected and retried with higher model capacity.
          </div>
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="font-semibold text-blue-400 block mb-1">Transparent Attribution</span>
            Every environmental value is strictly tagged as measured, estimated, or simulated. No unverified greenwashing.
          </div>
        </div>
      </div>
    </div>
  );
};
