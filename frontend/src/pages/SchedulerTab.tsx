import React, { useState } from 'react';
import { Calendar, Clock, AlertTriangle, ShieldCheck, ArrowRight, CheckCircle2 } from 'lucide-react';
import { ProvenanceBadge } from '../components/ProvenanceBadge';

export const SchedulerTab: React.FC = () => {
  const [priority, setPriority] = useState('CRITICAL');
  const [userBlocking, setUserBlocking] = useState(true);
  const [allowDelay, setAllowDelay] = useState(true);
  const [deadlineSeconds, setDeadlineSeconds] = useState(10);

  // Invariant logic
  const isEmergency = priority === 'EMERGENCY' || priority === 'CRITICAL';
  const actionMandate = (isEmergency || userBlocking || deadlineSeconds <= 10)
    ? 'EXECUTE_NOW (Delay Strictly Forbidden)'
    : allowDelay && deadlineSeconds >= 1800
    ? 'DELAY (Postpone to Daytime Solar Peak)'
    : 'MOVE_REGION (Spatial Shift to EU-North)';

  const scheduledTimeline = [
    { id: 'job-901', name: 'Emergency Cardiac Triage', priority: 'EMERGENCY', action: 'EXECUTE_NOW', region: 'us-east', delay: '0s', status: 'COMPLETED' },
    { id: 'job-902', name: 'Active Ransomware Revocation', priority: 'CRITICAL', action: 'EXECUTE_NOW', region: 'us-east', delay: '0s', status: 'COMPLETED' },
    { id: 'job-903', name: 'Weekly Compliance Report', priority: 'LOW', action: 'DELAY', region: 'us-east', delay: '+4.5 hours', status: 'SCHEDULED' },
    { id: 'job-904', name: 'Document Summarization Batch', priority: 'NORMAL', action: 'MOVE_REGION', region: 'eu-north', delay: '0s', status: 'IN_PROGRESS' },
    { id: 'job-905', name: 'Interactive Chatbot Query', priority: 'NORMAL', action: 'USE_CACHE', region: 'us-east', delay: '0s', status: 'COMPLETED' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Carbon-Aware Scheduler & Dispatcher</h2>
          <p className="text-xs text-slate-400">
            Temporal time-shifting and spatial routing with non-negotiable safety invariant enforcement.
          </p>
        </div>
        <ProvenanceBadge method="simulated_carbon" confidence={0.92} />
      </div>

      {/* Safety Invariant Box */}
      <div className="glass-panel p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
        <div className="text-xs text-slate-300">
          <span className="font-bold text-amber-300 block mb-1">Non-Negotiable Safety Invariant:</span>
          Emergency, critical, safety-sensitive, or user-blocking workloads must NEVER be delayed automatically, regardless of carbon intensity or financial cost. The scheduler automatically forces immediate local dispatch or zero-latency spatial transfer.
        </div>
      </div>

      {/* Interactive Invariant Simulator */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 mb-1">Scheduling Action Resolver Simulator</h3>
        <p className="text-xs text-slate-400 mb-4">Test how priority, latency, and blocking status dictate scheduling behavior</p>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs mb-4">
          <div>
            <label className="block text-slate-300 font-medium mb-1">Priority</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-2.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
            >
              <option value="LOW">LOW</option>
              <option value="NORMAL">NORMAL</option>
              <option value="HIGH">HIGH</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="EMERGENCY">EMERGENCY</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">User Blocking?</label>
            <select
              value={userBlocking ? 'yes' : 'no'}
              onChange={(e) => setUserBlocking(e.target.value === 'yes')}
              className="w-full px-2.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
            >
              <option value="yes">Yes (Human Waiting)</option>
              <option value="no">No (Async / Batch)</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Allow Delay Policy?</label>
            <select
              value={allowDelay ? 'yes' : 'no'}
              onChange={(e) => setAllowDelay(e.target.value === 'yes')}
              className="w-full px-2.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
            >
              <option value="yes">Allowed</option>
              <option value="no">Forbidden</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-300 font-medium">Deadline</span>
              <span className="text-emerald-400 font-mono">{deadlineSeconds}s</span>
            </div>
            <input
              type="range"
              min={2}
              max={3600}
              step={10}
              value={deadlineSeconds}
              onChange={(e) => setDeadlineSeconds(Number(e.target.value))}
              className="w-full accent-emerald-500 mt-2"
            />
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center justify-between">
          <span className="text-xs text-slate-400">Resolved Scheduling Decision:</span>
          <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold border ${
            actionMandate.includes('Forbidden')
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
          }`}>
            {actionMandate}
          </span>
        </div>
      </div>

      {/* Scheduled Timeline Table */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800/80">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Live Task Dispatch Queue</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 border-b border-slate-800 font-medium">
              <tr>
                <th className="py-2.5 px-3">Job ID</th>
                <th className="py-2.5 px-3">Workload Name</th>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Assigned Region</th>
                <th className="py-2.5 px-3">Delay Offset</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono text-[11px]">
              {scheduledTimeline.map((item) => (
                <tr key={item.id} className="hover:bg-slate-900/40">
                  <td className="py-2.5 px-3 text-slate-400">{item.id}</td>
                  <td className="py-2.5 px-3 font-sans text-slate-200 font-medium">{item.name}</td>
                  <td className="py-2.5 px-3">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                      item.priority === 'EMERGENCY' || item.priority === 'CRITICAL'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : 'bg-slate-800 text-slate-300'
                    }`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-emerald-400 font-semibold">{item.action}</td>
                  <td className="py-2.5 px-3 text-teal-300">{item.region}</td>
                  <td className="py-2.5 px-3 text-slate-300">{item.delay}</td>
                  <td className="py-2.5 px-3 text-blue-400">{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
