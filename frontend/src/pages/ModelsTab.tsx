import React, { useState } from 'react';
import { Cpu, Zap, DollarSign, Clock, CheckCircle2, Shield, Layers } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { ModelProfile } from '../api/client';

interface Props {
  models: ModelProfile[];
}

export const ModelsTab: React.FC<Props> = ({ models }) => {
  const [selectedComplexity, setSelectedComplexity] = useState('MEDIUM');
  const [minQuality, setMinQuality] = useState(0.70);

  // Filter candidates matching interactive selector
  const candidates = models.filter(
    (m) => m.supported_complexity?.includes(selectedComplexity) && m.capability_score >= minQuality
  );
  const recommended = candidates.sort((a, b) => a.energy_estimate_j_per_token - b.energy_estimate_j_per_token)[0];

  const chartData = models.map((m) => ({
    name: m.name.replace(':7b', '').replace(':8b', '').replace(':14b', '').replace(':8x7b', '').replace(':1b', '-1B').replace(':3b', '-3B'),
    energyPerToken: m.energy_estimate_j_per_token,
    capability: Math.round(m.capability_score * 100),
    latencyMs: m.latency_estimate_ms
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Model Registry & Catalog</h2>
          <p className="text-xs text-slate-400">
            Hardware-calibrated local and open-source models with verified energy and latency baselines.
          </p>
        </div>
        <ProvenanceBadge method="estimated_energy" confidence={0.91} />
      </div>

      {/* Model Comparison Matrix Table */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Model Energy & Capability Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-medium">
              <tr>
                <th className="py-2.5 px-3">Model Name</th>
                <th className="py-2.5 px-3">Provider</th>
                <th className="py-2.5 px-3">Capability</th>
                <th className="py-2.5 px-3">Energy (J/token)</th>
                <th className="py-2.5 px-3">Cost ($/1k)</th>
                <th className="py-2.5 px-3">Latency Baseline</th>
                <th className="py-2.5 px-3">Context</th>
                <th className="py-2.5 px-3">Supported Tiers</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {models.map((m) => (
                <tr key={m.name} className="hover:bg-slate-900/40">
                  <td className="py-2.5 px-3 font-semibold text-emerald-400 font-mono">{m.name}</td>
                  <td className="py-2.5 px-3 text-slate-400 uppercase text-[10px] font-mono">{m.provider}</td>
                  <td className="py-2.5 px-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full"
                          style={{ width: `${m.capability_score * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-[11px]">{(m.capability_score * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-teal-300">{m.energy_estimate_j_per_token.toFixed(3)} J</td>
                  <td className="py-2.5 px-3 font-mono text-slate-300">${m.cost_estimate_per_1k_tokens.toFixed(4)}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-300">{m.latency_estimate_ms} ms</td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">{(m.context_window / 1024).toFixed(0)}k</td>
                  <td className="py-2.5 px-3">
                    <div className="flex flex-wrap gap-1">
                      {m.supported_complexity?.map((tier) => (
                        <span key={tier} className="px-1.5 py-0.5 text-[9px] rounded bg-slate-800 text-slate-300 font-mono">
                          {tier}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Bar Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <h3 className="text-sm font-semibold text-slate-200 mb-1">Energy Footprint per Generated Token</h3>
          <p className="text-xs text-slate-400 mb-4">Joules consumed per output token</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} unit="J" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="energyPerToken" name="Energy (J/token)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
          <h3 className="text-sm font-semibold text-slate-200 mb-1">Deterministic Model Selector Tool</h3>
          <p className="text-xs text-slate-400 mb-4">Simulate routing choices before runtime execution</p>
          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Target Complexity Tier</label>
              <div className="grid grid-cols-4 gap-2">
                {['EASY', 'MEDIUM', 'HARD', 'CRITICAL'].map((c) => (
                  <button
                    key={c}
                    onClick={() => setSelectedComplexity(c)}
                    className={`py-1.5 rounded-lg font-mono text-xs border ${
                      selectedComplexity === c
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold'
                        : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">Quality Floor Constraint</span>
                <span className="text-emerald-400 font-mono">{(minQuality * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min={0.4}
                max={0.95}
                step={0.05}
                value={minQuality}
                onChange={(e) => setMinQuality(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-[11px] block mb-1">Deterministic Selection:</span>
              {recommended ? (
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-bold text-emerald-400 text-sm font-mono">{recommended.name}</span>
                    <span className="text-slate-400 text-xs block">
                      Capability: {(recommended.capability_score * 100).toFixed(0)}% | Latency: {recommended.latency_estimate_ms}ms
                    </span>
                  </div>
                  <span className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 text-xs font-mono font-semibold">
                    {recommended.energy_estimate_j_per_token} J/token
                  </span>
                </div>
              ) : (
                <span className="text-amber-400 text-xs">No candidate satisfies both tier and quality constraint.</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
