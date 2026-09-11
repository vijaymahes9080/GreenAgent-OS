import React, { useState } from 'react';
import { Globe, Sun, Wind, ArrowRight, ShieldCheck, Info } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { ProvenanceBadge } from '../components/ProvenanceBadge';
import { RegionCarbon } from '../api/client';

interface Props {
  regions: RegionCarbon[];
}

export const CarbonTab: React.FC<Props> = ({ regions }) => {
  const [sourceRegion, setSourceRegion] = useState('us-east');
  const [targetRegion, setTargetRegion] = useState('eu-north');
  const [tokensCount, setTokensCount] = useState(50000);

  // Generate 24-hour diurnal curves for visual comparison
  const diurnalData = Array.from({ length: 24 }).map((_, h) => {
    // Sinusoidal solar peak at 13:00 UTC
    const solarFactor = Math.max(0, Math.sin(((h - 6) / 24) * 2 * Math.PI));
    return {
      hour: `${h.toString().padStart(2, '0')}:00`,
      'us-east': Math.round(375 - solarFactor * 60),
      'us-west': Math.round(185 - solarFactor * 50),
      'eu-central': Math.round(310 - solarFactor * 75),
      'eu-north': Math.round(42 - solarFactor * 10),
      'ap-south': Math.round(610 - solarFactor * 90),
    };
  });

  // Calculate Spatial Arbitrage Savings
  const sourceProf = regions.find((r) => r.region_id === sourceRegion) || { current_intensity_g_kwh: 345, datacenter_pue: 1.25 };
  const targetProf = regions.find((r) => r.region_id === targetRegion) || { current_intensity_g_kwh: 42, datacenter_pue: 1.15 };

  // Joules estimate: 0.15 J/token average
  const totalJoules = tokensCount * 0.15;
  const energyKwh = totalJoules / 3600000.0;

  const sourceCarbonGrams = energyKwh * sourceProf.datacenter_pue * sourceProf.current_intensity_g_kwh;
  const targetCarbonGrams = energyKwh * targetProf.datacenter_pue * targetProf.current_intensity_g_kwh;
  const savedGrams = Math.max(0, sourceCarbonGrams - targetCarbonGrams);
  const savedPct = sourceCarbonGrams > 0 ? ((sourceCarbonGrams - targetCarbonGrams) / sourceCarbonGrams) * 100 : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Grid Carbon Intensity & Temporal Dynamics</h2>
          <p className="text-xs text-slate-400">
            Multi-region carbon emission factors, diurnal solar/wind valleys, and datacenter PUE modeling.
          </p>
        </div>
        <ProvenanceBadge method="simulated_carbon" confidence={0.88} />
      </div>

      {/* Regional Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {regions.map((r) => (
          <div key={r.region_id} className="glass-panel p-4 rounded-xl border border-slate-800/80">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-xs text-slate-200">{r.region_name}</span>
              <span className="text-[10px] text-slate-400 font-mono">{r.country}</span>
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400 mb-1">
              {r.current_intensity_g_kwh} <span className="text-xs font-normal text-slate-400">gCO₂e/kWh</span>
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 pt-2 border-t border-slate-800">
              <span>Datacenter PUE:</span>
              <span className="font-mono text-slate-200">{r.datacenter_pue}</span>
            </div>
          </div>
        ))}
      </div>

      {/* 24-Hour Diurnal Grid Curve Chart */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">24-Hour Diurnal Carbon Intensity Curves</h3>
            <p className="text-xs text-slate-400">Solar generation drops grid intensity during daylight hours</p>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className="flex items-center gap-1"><Sun className="w-3.5 h-3.5 text-amber-400" /> Peak Solar Abatement</span>
            <span className="flex items-center gap-1"><Wind className="w-3.5 h-3.5 text-teal-400" /> Baseload Wind</span>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={diurnalData}>
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} unit="g" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Line type="monotone" dataKey="us-east" name="US East (g/kWh)" stroke="#f97316" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="us-west" name="US West (g/kWh)" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="eu-central" name="EU Central (g/kWh)" stroke="#a855f7" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="eu-north" name="EU North (Cleanest)" stroke="#10b981" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Interactive Spatial & Temporal Arbitrage Calculator */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 mb-1">Spatial Arbitrage Emission Simulator</h3>
        <p className="text-xs text-slate-400 mb-4">
          Calculate the exact avoided CO₂e grams by shifting workloads from high-carbon to renewable grids.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs mb-4">
          <div>
            <label className="block text-slate-300 font-medium mb-1">Source Region</label>
            <select
              value={sourceRegion}
              onChange={(e) => setSourceRegion(e.target.value)}
              className="w-full px-2.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
            >
              {regions.map((r) => (
                <option key={r.region_id} value={r.region_id}>{r.region_name} ({r.current_intensity_g_kwh}g)</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Target Clean Region</label>
            <select
              value={targetRegion}
              onChange={(e) => setTargetRegion(e.target.value)}
              className="w-full px-2.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
            >
              {regions.map((r) => (
                <option key={r.region_id} value={r.region_id}>{r.region_name} ({r.current_intensity_g_kwh}g)</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Workload Token Volume</label>
            <input
              type="number"
              value={tokensCount}
              onChange={(e) => setTokensCount(Number(e.target.value))}
              step={5000}
              min={1000}
              className="w-full px-2.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 font-mono text-xs"
            />
          </div>
        </div>

        {/* Calculation Result Box */}
        <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-slate-400">Avoided Greenhouse Gas Emissions:</span>
              <span className="text-xl font-bold text-emerald-400 font-mono">
                {savedGrams.toFixed(4)} g CO₂e
              </span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold font-mono">
                -{savedPct.toFixed(1)}%
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Formula: (Energy: {(energyKwh * 1000).toFixed(3)} Wh) × PUE × Δ(Grid Intensity: {sourceProf.current_intensity_g_kwh - targetProf.current_intensity_g_kwh} g/kWh)
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 font-mono">{sourceRegion}</span>
            <ArrowRight className="w-4 h-4 text-emerald-400" />
            <span className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono font-bold">
              {targetRegion}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
