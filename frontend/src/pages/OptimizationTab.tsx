import React, { useState } from 'react';
import { Sliders, CheckCircle2, ShieldAlert, Cpu, Sparkles, Scale } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';

export const OptimizationTab: React.FC = () => {
  const [alpha, setAlpha] = useState(0.25);  // Energy
  const [beta, setBeta] = useState(0.35);   // Carbon
  const [gamma, setGamma] = useState(0.20);  // Cost
  const [delta, setDelta] = useState(0.10);  // Latency
  const [epsilon, setEpsilon] = useState(0.10); // Quality loss

  const totalWeight = alpha + beta + gamma + delta + epsilon;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Multi-Objective Optimization Solver</h2>
          <p className="text-xs text-slate-400">
            Pareto-optimal candidate ranking balancing energy, emissions, cost, latency, and quality floors.
          </p>
        </div>
        <ProvenanceBadge method="estimated_energy" confidence={0.93} />
      </div>

      {/* Mathematical Formulation Header */}
      <div className="glass-panel p-5 rounded-xl border border-emerald-500/20 bg-slate-900/60">
        <div className="flex items-center gap-2 mb-2">
          <Scale className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-bold text-slate-200">Constrained Multi-Objective Loss Function</h3>
        </div>
        <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-300 mb-3 overflow-x-auto">
          min J = α·(E / E_norm) + β·(C / C_norm) + γ·(Cost / Cost_norm) + δ·(L / L_norm) + ε·(1 - Quality)
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-400">
          <span className="p-2 rounded bg-slate-900 border border-slate-800">Quality &ge; Q_min</span>
          <span className="p-2 rounded bg-slate-900 border border-slate-800">Latency &le; L_max</span>
          <span className="p-2 rounded bg-slate-900 border border-slate-800">Scheduled &le; Deadline</span>
          <span className="p-2 rounded bg-slate-900 border border-slate-800">Model.Available == True</span>
        </div>
      </div>

      {/* Interactive Sliders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">Objective Weight Calibration</h3>
            <span className={`text-xs font-mono px-2 py-0.5 rounded ${
              Math.abs(totalWeight - 1.0) < 0.01 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
            }`}>
              Sum: {totalWeight.toFixed(2)}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">α (Energy Consumption Weight)</span>
                <span className="text-emerald-400 font-mono">{alpha.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={alpha}
                onChange={(e) => setAlpha(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">β (Carbon Emissions Weight)</span>
                <span className="text-teal-400 font-mono">{beta.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={beta}
                onChange={(e) => setBeta(Number(e.target.value))}
                className="w-full accent-teal-500"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">γ (Financial Cost Weight)</span>
                <span className="text-blue-400 font-mono">{gamma.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={gamma}
                onChange={(e) => setGamma(Number(e.target.value))}
                className="w-full accent-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">δ (Execution Latency Weight)</span>
                <span className="text-purple-400 font-mono">{delta.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={delta}
                onChange={(e) => setDelta(Number(e.target.value))}
                className="w-full accent-purple-500"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">ε (Quality Preservation Weight)</span>
                <span className="text-rose-400 font-mono">{epsilon.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={epsilon}
                onChange={(e) => setEpsilon(Number(e.target.value))}
                className="w-full accent-rose-500"
              />
            </div>
          </div>
        </div>

        {/* Explainability / Preview Panel */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Decision Explainability & Trade-offs</h3>
            <p className="text-xs text-slate-400 mb-4">
              How the current weight distribution impacts real model selection and scheduling actions:
            </p>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-semibold text-emerald-400 block mb-1">High Carbon Weight (β &ge; 0.30)</span>
                <p className="text-slate-300">
                  Prioritizes spatial shifting to low-emission regions (e.g. EU North or US West hydro) and schedules non-critical tasks during solar noon valleys.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-semibold text-teal-400 block mb-1">High Energy Weight (α &ge; 0.25)</span>
                <p className="text-slate-300">
                  Favors smaller distilled architectures (Llama-3.2-1B/3B) for easy tasks and aggressively checks the semantic cache to eliminate redundant forward passes.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-semibold text-rose-400 block mb-1">High Quality Weight (ε &ge; 0.15)</span>
                <p className="text-slate-300">
                  Enforces strict quality floors. Any ambiguity in complexity routing defaults upwards to Llama-3.1-8B or Qwen-2.5-14B.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Deterministic Solver</span>
            <span className="font-mono text-emerald-400">&lt; 15ms resolution</span>
          </div>
        </div>
      </div>
    </div>
  );
};
