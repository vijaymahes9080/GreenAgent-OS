import React, { useState } from 'react';
import { Settings as SettingsIcon, Key, Shield, Server, RefreshCw, CheckCircle2, Lock } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';

export const SettingsTab: React.FC = () => {
  const [apiKey, setApiKey] = useState('ga-dev-test-key-2026');
  const [pue, setPue] = useState(1.25);
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">System Settings & Governance</h2>
          <p className="text-xs text-slate-400">
            Configure authentication credentials, API endpoints, datacenter PUE parameters, and RBAC tiers.
          </p>
        </div>
        <ProvenanceBadge method="estimated_carbon" />
      </div>

      <form onSubmit={handleSave} className="space-y-6 text-xs">
        {/* API Authentication & RBAC */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 space-y-4">
          <div className="flex items-center gap-2 text-slate-200 font-semibold">
            <Key className="w-4 h-4 text-emerald-400" />
            <span>API Security & Access Keys</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Active X-API-Key</label>
              <input
                type="text"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 font-mono text-xs focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Active Role</label>
              <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-emerald-400 font-mono text-xs flex items-center justify-between">
                <span>ROLE_ADMIN</span>
                <Lock className="w-3.5 h-3.5 text-slate-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Inference & Hardware Model */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 space-y-4">
          <div className="flex items-center gap-2 text-slate-200 font-semibold">
            <Server className="w-4 h-4 text-teal-400" />
            <span>Inference Host & Local Execution</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Ollama Local Endpoint</label>
              <input
                type="text"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 font-mono text-xs focus:outline-none focus:border-teal-500"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">
                Local inference requires zero cloud credentials and operates CPU-only without a GPU.
              </span>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 font-medium">Default Datacenter PUE</span>
                <span className="text-teal-400 font-mono">{pue.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={1.05}
                max={1.80}
                step={0.01}
                value={pue}
                onChange={(e) => setPue(Number(e.target.value))}
                className="w-full accent-teal-500"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">
                Power Usage Effectiveness multiplier applied to server IT electrical draw.
              </span>
            </div>
          </div>
        </div>

        {/* Integration Status Cards */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800/80 space-y-3">
          <div className="flex items-center gap-2 text-slate-200 font-semibold">
            <Shield className="w-4 h-4 text-purple-400" />
            <span>Connected Automation Adapters</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200 block">n8n Community Edition</span>
                <span className="text-[11px] text-slate-400 font-mono">POST /api/v1/integrations/n8n/workload</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">READY</span>
            </div>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200 block">Model Context Protocol (MCP)</span>
                <span className="text-[11px] text-slate-400 font-mono">3 Audited Tools Active</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">READY</span>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-all flex items-center gap-2 shadow-md shadow-emerald-500/20"
        >
          {saved ? (
            <>
              <CheckCircle2 className="w-4 h-4" /> Preferences Saved!
            </>
          ) : (
            'Save Configuration Changes'
          )}
        </button>
      </form>
    </div>
  );
};
