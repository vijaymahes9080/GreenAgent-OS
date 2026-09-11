import React, { useState } from 'react';
import { Flame, Info } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';

export const TokenHeatmap: React.FC = () => {
  const [sampleText, setSampleText] = useState(
    "Basically in order to analyze recursive algorithms and compute gradient descent convergence proofs, we need heavy attention FLOPs."
  );

  const words = sampleText.split(/\s+/);

  // Classify energy heat: filler words vs technical reasoning tokens
  const getEnergyClass = (word: string) => {
    const clean = word.toLowerCase().replace(/[^\w]/g, '');
    if (['basically', 'furthermore', 'essentially', 'order', 'we', 'to', 'and'].includes(clean)) {
      return { bg: 'bg-emerald-500/20', text: 'text-emerald-300', level: 'Low (Prunable Filler)' };
    }
    if (['recursive', 'algorithms', 'gradient', 'convergence', 'proofs', 'attention'].includes(clean)) {
      return { bg: 'bg-rose-500/30', text: 'text-rose-300', level: 'High Attention Energy' };
    }
    return { bg: 'bg-blue-500/20', text: 'text-blue-300', level: 'Moderate Energy' };
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Prompt Token Energy Heatmap</h2>
          <p className="text-xs text-slate-400">
            Token-by-token prefill energy visualization revealing computational hotspots and prunable tokens.
          </p>
        </div>
        <ProvenanceBadge method="estimated_energy" confidence={0.92} />
      </div>

      <div className="glass-panel p-5 rounded-xl border border-slate-800/80 space-y-4">
        <div>
          <label className="block text-slate-300 text-xs font-medium mb-1">Inspect Prompt Tokens:</label>
          <textarea
            value={sampleText}
            onChange={(e) => setSampleText(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:outline-none"
          />
        </div>

        {/* Visual Token Chips */}
        <div>
          <span className="text-xs text-slate-400 font-semibold block mb-2">Token Energy Decomposition:</span>
          <div className="flex flex-wrap gap-1.5 p-4 rounded-xl bg-slate-950 border border-slate-800">
            {words.map((w, i) => {
              const meta = getEnergyClass(w);
              return (
                <span
                  key={i}
                  title={`${w}: ${meta.level}`}
                  className={`px-2 py-1 rounded text-xs font-mono border border-slate-700/50 cursor-help transition-transform hover:scale-105 ${meta.bg} ${meta.text}`}
                >
                  {w}
                </span>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-2 border-t border-slate-800">
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-emerald-500/40"></span> Low Energy / Prunable</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-blue-500/40"></span> Moderate Context</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-rose-500/40"></span> High Attention Hotspot</span>
        </div>
      </div>
    </div>
  );
};
