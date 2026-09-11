import React, { useState } from 'react';
import { Database, Trash2, Zap, Globe, Sparkles, CheckCircle2 } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { CacheStats } from '../api/client';

interface Props {
  cacheStats: CacheStats;
  onRefresh: () => void;
}

export const CacheTab: React.FC<Props> = ({ cacheStats, onRefresh }) => {
  const [threshold, setThreshold] = useState(0.90);
  const [invalidating, setInvalidating] = useState(false);

  const handleInvalidate = async () => {
    setInvalidating(true);
    try {
      await fetch('/api/v1/cache/invalidate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': 'ga-dev-test-key-2026' }
      });
      onRefresh();
    } catch (err: any) {
      alert('Failed to invalidate: ' + err.message);
    } finally {
      setInvalidating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Semantic Cache Management</h2>
          <p className="text-xs text-slate-400">
            Exact and vector similarity caching with provenance tracking and safety guardrails.
          </p>
        </div>
        <ProvenanceBadge method="estimated_energy" confidence={0.95} />
      </div>

      {/* Aggregate Savings KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Total Cache Hits</span>
          <span className="text-2xl font-bold font-mono text-emerald-400">
            {cacheStats.aggregate_hits}
          </span>
          <span className="text-[11px] text-slate-500 block mt-1">Zero inference calls</span>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Tokens Saved</span>
          <span className="text-2xl font-bold font-mono text-teal-300">
            {cacheStats.total_tokens_saved.toLocaleString()}
          </span>
          <span className="text-[11px] text-slate-500 block mt-1">Eliminated tokens</span>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Joules Avoided</span>
          <span className="text-2xl font-bold font-mono text-blue-300">
            {cacheStats.total_joules_saved.toFixed(1)} J
          </span>
          <span className="text-[11px] text-slate-500 block mt-1">Prevented compute draw</span>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <span className="text-xs text-slate-400 block mb-1">Emissions Avoided</span>
          <span className="text-2xl font-bold font-mono text-purple-300">
            {cacheStats.total_co2e_grams_saved.toFixed(4)} g
          </span>
          <span className="text-[11px] text-slate-500 block mt-1">CO₂e greenhouse gases</span>
        </div>
      </div>

      {/* Controls Strip */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4 w-full sm:w-auto">
          <div>
            <div className="flex justify-between items-center mb-1 text-xs">
              <span className="text-slate-300 font-medium">Similarity Cosine Threshold</span>
              <span className="text-emerald-400 font-mono">{(threshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min={0.75}
              max={0.98}
              step={0.01}
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-48 accent-emerald-500"
            />
          </div>
        </div>

        <button
          onClick={handleInvalidate}
          disabled={invalidating}
          className="px-3 py-2 rounded-lg bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/40 text-xs font-semibold flex items-center gap-1.5 transition-all"
        >
          <Trash2 className="w-3.5 h-3.5" /> Invalidate Expired Entries
        </button>
      </div>

      {/* Cache Entries Inspector */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Active Cache Key Store & Provenance</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 border-b border-slate-800 font-medium">
              <tr>
                <th className="py-2.5 px-3">Key Hash</th>
                <th className="py-2.5 px-3">Prompt Snippet</th>
                <th className="py-2.5 px-3">Cached Model</th>
                <th className="py-2.5 px-3">Hit Count</th>
                <th className="py-2.5 px-3">Tokens Saved</th>
                <th className="py-2.5 px-3">Energy Saved</th>
                <th className="py-2.5 px-3">Expires At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono text-[11px]">
              {cacheStats.entries?.map((e) => (
                <tr key={e.id} className="hover:bg-slate-900/40">
                  <td className="py-2.5 px-3 text-slate-400">{e.key_hash.substring(0, 10)}...</td>
                  <td className="py-2.5 px-3 font-sans text-slate-200">{e.prompt_snippet}</td>
                  <td className="py-2.5 px-3 text-emerald-400">{e.model}</td>
                  <td className="py-2.5 px-3 font-bold text-teal-300">{e.hit_count}</td>
                  <td className="py-2.5 px-3 text-slate-300">{e.tokens_saved}</td>
                  <td className="py-2.5 px-3 text-blue-300">{e.energy_saved_joules?.toFixed(1)} J</td>
                  <td className="py-2.5 px-3 text-slate-400">
                    {e.expires_at ? new Date(e.expires_at).toLocaleTimeString() : 'N/A'}
                  </td>
                </tr>
              ))}
              {(!cacheStats.entries || cacheStats.entries.length === 0) && (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500 font-sans">
                    No active cache entries found. Workload prompts will populate this store upon execution.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
