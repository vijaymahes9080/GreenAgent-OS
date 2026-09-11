import React, { useState } from 'react';
import { Globe, Zap, ArrowRight, ShieldCheck } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';

export const GlobalGridMap: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<string>('eu-north');

  const nodes = [
    { id: 'us-east', name: 'US East (N. Virginia)', cx: 270, cy: 190, intensity: 375, color: '#f97316', pue: 1.25 },
    { id: 'us-west', name: 'US West (Oregon)', cx: 180, cy: 170, intensity: 185, color: '#3b82f6', pue: 1.18 },
    { id: 'eu-north', name: 'Europe North (Stockholm)', cx: 520, cy: 120, intensity: 42, color: '#10b981', pue: 1.15 },
    { id: 'eu-central', name: 'Europe Central (Frankfurt)', cx: 500, cy: 170, intensity: 310, color: '#a855f7', pue: 1.22 },
    { id: 'ap-south', name: 'Asia Pacific (Mumbai)', cx: 680, cy: 240, intensity: 610, color: '#ef4444', pue: 1.35 },
  ];

  const active = nodes.find((n) => n.id === selectedNode) || nodes[2];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Global Carbon Grid Topography</h2>
          <p className="text-xs text-slate-400">
            Real-time geospatial visualization of datacenter nodes, carbon intensity halos, and spatial dispatch vectors.
          </p>
        </div>
        <ProvenanceBadge method="simulated_carbon" confidence={0.92} />
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 relative overflow-hidden">
        {/* SVG World Map Canvas */}
        <div className="relative w-full aspect-[2/1] max-h-96 bg-slate-950/80 rounded-xl border border-slate-900 overflow-hidden flex items-center justify-center">
          <svg viewBox="0 0 900 450" className="w-full h-full opacity-90">
            <defs>
              <linearGradient id="routeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f97316" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.9" />
              </linearGradient>
            </defs>

            {/* Simulated Continental Silhouettes */}
            <path
              d="M 150 120 Q 220 90 280 140 Q 300 220 220 280 Z M 460 110 Q 560 100 620 180 Q 520 240 450 160 Z M 640 180 Q 760 160 820 260 Q 720 320 650 240 Z"
              fill="#0f172a"
              stroke="#1e293b"
              strokeWidth="1.5"
            />

            {/* Active Routing Arc: US-East to EU-North */}
            <path
              d="M 270 190 Q 395 100 520 120"
              fill="none"
              stroke="url(#routeGrad)"
              strokeWidth="2.5"
              strokeDasharray="6,4"
            >
              <animate attributeName="stroke-dashoffset" values="40;0" dur="2s" repeatCount="indefinite" />
            </path>

            {/* Datacenter Nodes */}
            {nodes.map((n) => (
              <g
                key={n.id}
                onClick={() => setSelectedNode(n.id)}
                className="cursor-pointer transition-transform hover:scale-125"
              >
                {/* Ping ring */}
                <circle cx={n.cx} cy={n.cy} r="14" fill={n.color} opacity="0.2">
                  <animate attributeName="r" values="8;20;8" dur="3s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.4;0;0.4" dur="3s" repeatCount="indefinite" />
                </circle>
                <circle cx={n.cx} cy={n.cy} r="6" fill={n.color} stroke="#ffffff" strokeWidth="1.5" />
                <text x={n.cx} y={n.cy - 12} textAnchor="middle" fill="#94a3b8" fontSize="10" fontFamily="monospace">
                  {n.id} ({n.intensity}g)
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* Selected Node Panel */}
        <div className="mt-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
          <div>
            <span className="font-bold text-slate-200 text-sm block">{active.name}</span>
            <span className="text-slate-400 font-mono">
              Intensity: {active.intensity} gCO₂e/kWh | PUE: {active.pue}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold" style={{ backgroundColor: `${active.color}20`, color: active.color }}>
              {active.intensity <= 100 ? 'CLEAN RENEWABLE' : active.intensity <= 350 ? 'MODERATE' : 'CARBON INTENSIVE'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
