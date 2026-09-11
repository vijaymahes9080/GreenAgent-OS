import React, { useState } from 'react';
import { Play, Send, CheckCircle2, AlertTriangle, Layers, Clock, Zap, Globe, Sparkles } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { api, TelemetryTrace } from '../api/client';

interface Props {
  telemetry: TelemetryTrace[];
  onRefreshTelemetry: () => void;
}

export const WorkloadsTab: React.FC<Props> = ({ telemetry, onRefreshTelemetry }) => {
  const [name, setName] = useState('Customer Support Routing');
  const [prompt, setPrompt] = useState('Summarize this user issue: The mobile application crashes upon clicking export PDF.');
  const [priority, setPriority] = useState('NORMAL');
  const [deadline, setDeadline] = useState(60);
  const [allowCache, setAllowCache] = useState(true);
  const [allowDelay, setAllowDelay] = useState(true);
  const [allowRegionShift, setAllowRegionShift] = useState(true);
  const [safetySensitive, setSafetySensitive] = useState(false);
  const [format, setFormat] = useState('text');

  const [executing, setExecuting] = useState(false);
  const [lastResult, setLastResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setExecuting(true);
    try {
      const res = await api.executeWorkload({
        name,
        prompt,
        priority,
        deadline_seconds: deadline,
        allow_cache: allowCache,
        allow_delay: allowDelay,
        allow_region_shift: allowRegionShift,
        safety_sensitive: safetySensitive,
        expected_output_format: format,
        preferred_region: 'us-east'
      });
      setLastResult(res);
      onRefreshTelemetry();
    } catch (err: any) {
      alert('Workload execution error: ' + err.message);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Workload Execution Engine</h2>
          <p className="text-xs text-slate-400">
            Submit AI workloads to run through the GreenAgent multi-objective optimizer pipeline.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Input Form */}
        <div className="lg:col-span-1 glass-panel p-5 rounded-xl border border-slate-800/80">
          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Workload Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 focus:outline-none focus:border-emerald-500 font-mono text-xs"
                required
              />
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 focus:outline-none focus:border-emerald-500 text-xs"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none"
                >
                  <option value="LOW">LOW</option>
                  <option value="NORMAL">NORMAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="EMERGENCY">EMERGENCY</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Format</label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none"
                >
                  <option value="text">Plain Text</option>
                  <option value="json">JSON</option>
                  <option value="sql">SQL</option>
                  <option value="code">Code</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">Deadline (Seconds)</span>
                <span className="text-emerald-400 font-mono">{deadline}s</span>
              </div>
              <input
                type="range"
                min={2}
                max={300}
                value={deadline}
                onChange={(e) => setDeadline(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            {/* Policy Toggles */}
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowCache}
                  onChange={(e) => setAllowCache(e.target.checked)}
                  className="rounded accent-emerald-500"
                />
                <span className="text-slate-300">Allow Semantic Caching</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowDelay}
                  onChange={(e) => setAllowDelay(e.target.checked)}
                  className="rounded accent-emerald-500"
                />
                <span className="text-slate-300">Allow Temporal Delay for Carbon Valleys</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowRegionShift}
                  onChange={(e) => setAllowRegionShift(e.target.checked)}
                  className="rounded accent-emerald-500"
                />
                <span className="text-slate-300">Allow Spatial Region Shifting</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer text-amber-300">
                <input
                  type="checkbox"
                  checked={safetySensitive}
                  onChange={(e) => setSafetySensitive(e.target.checked)}
                  className="rounded accent-amber-500"
                />
                <span className="font-medium">Safety-Critical Invariant (Never Delay)</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={executing}
              className="w-full py-2.5 px-4 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-all flex items-center justify-center gap-2 shadow-md shadow-emerald-500/20 disabled:opacity-50"
            >
              {executing ? (
                <>Optimizing & Executing...</>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" /> Execute via GreenAgent OS
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right: Real-time Decision & Output Panel */}
        <div className="lg:col-span-2 space-y-4">
          {lastResult ? (
            <div className="glass-panel p-5 rounded-xl border border-emerald-500/30 space-y-4 animate-in fade-in duration-300">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="p-1 rounded bg-emerald-500/20 text-emerald-300">
                    <Sparkles className="w-4 h-4" />
                  </span>
                  <span className="font-semibold text-slate-100 text-sm">Execution Successful</span>
                </div>
                <div className="flex items-center gap-2">
                  {lastResult.cache_hit ? (
                    <span className="px-2.5 py-1 text-xs rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/30 font-semibold">
                      SEMANTIC CACHE HIT
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 text-xs rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 font-semibold font-mono">
                      {lastResult.model_used}
                    </span>
                  )}
                  <ProvenanceBadge method="estimated_energy" confidence={0.94} />
                </div>
              </div>

              {/* Metrics Summary Strip */}
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Latency</span>
                  <span className="font-semibold text-slate-200">{lastResult.latency_ms} ms</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Quality Score</span>
                  <span className="font-semibold text-emerald-400">
                    {lastResult.quality_score ? (lastResult.quality_score * 100).toFixed(0) + '%' : '100%'}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Cache Savings</span>
                  <span className="font-semibold text-teal-400">
                    {lastResult.energy_saved_joules ? `${lastResult.energy_saved_joules.toFixed(1)} J` : 'N/A'}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Status</span>
                  <span className="font-semibold text-blue-400">{lastResult.status}</span>
                </div>
              </div>

              {/* Optimization Rationale */}
              {lastResult.optimization_decision && (
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
                  <span className="text-slate-400 font-semibold block mb-1.5">Optimization Rationale:</span>
                  <ul className="list-disc list-inside space-y-1 text-slate-300">
                    {lastResult.optimization_decision.rationale?.map((r: string, i: number) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Response Text Box */}
              <div>
                <span className="text-slate-400 text-xs font-semibold block mb-1">Generated Output:</span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-200 whitespace-pre-wrap max-h-56 overflow-y-auto">
                  {lastResult.response}
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-10 rounded-xl border border-slate-800/80 text-center text-slate-500">
              <Layers className="w-8 h-8 mx-auto mb-2 opacity-40 text-slate-400" />
              <p className="text-sm font-medium text-slate-400">No Workload Submitted Yet</p>
              <p className="text-xs">Fill out the prompt on the left to observe automated optimization.</p>
            </div>
          )}

          {/* Telemetry Traces Table */}
          <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center justify-between">
              <span>Recent Execution Traces</span>
              <span className="text-xs text-slate-400 font-mono">{telemetry.length} total traces</span>
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/60 text-slate-400 border-b border-slate-800 font-medium">
                  <tr>
                    <th className="py-2 px-3">Workload ID</th>
                    <th className="py-2 px-3">Model</th>
                    <th className="py-2 px-3">Tokens</th>
                    <th className="py-2 px-3">Latency</th>
                    <th className="py-2 px-3">Energy (J)</th>
                    <th className="py-2 px-3">Carbon (g)</th>
                    <th className="py-2 px-3">Cache</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50 font-mono text-[11px]">
                  {telemetry.slice(0, 8).map((t) => (
                    <tr key={t.id} className="hover:bg-slate-900/40">
                      <td className="py-2 px-3 text-slate-400">{t.workload_id}</td>
                      <td className="py-2 px-3 text-emerald-400">{t.model}</td>
                      <td className="py-2 px-3">{t.total_tokens}</td>
                      <td className="py-2 px-3">{t.latency_ms.toFixed(0)}ms</td>
                      <td className="py-2 px-3 text-teal-300">{t.energy_joules?.toFixed(2)}</td>
                      <td className="py-2 px-3 text-slate-300">{t.carbon_co2e_grams?.toFixed(5)}</td>
                      <td className="py-2 px-3">
                        {t.cache_hit ? (
                          <span className="text-emerald-400 font-bold">HIT</span>
                        ) : (
                          <span className="text-slate-500">MISS</span>
                        )}
                      </td>
                    </tr>
                  ))}
                  {telemetry.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-4 text-center text-slate-500 font-sans">
                        No traces recorded yet. Run a workload above or trigger the benchmark.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
