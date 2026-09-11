import React from 'react';

interface Props {
  method?: string;
  confidence?: number;
}

export const ProvenanceBadge: React.FC<Props> = ({ method = 'estimated_energy', confidence }) => {
  let label = 'Estimated Energy';
  let badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  let desc = 'Calculated via parameter-scaled active & idle power equations';

  switch (method?.toLowerCase()) {
    case 'measured_energy':
      label = 'MEASURED ENERGY';
      badgeColor = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 font-semibold';
      desc = 'Hardware telemetry from physical CPU/GPU counters (RAPL/NVML/PDU)';
      break;
    case 'estimated_carbon':
      label = 'ESTIMATED CARBON';
      badgeColor = 'bg-teal-500/10 text-teal-300 border-teal-500/30';
      desc = 'Energy (kWh) × Datacenter PUE × Regional Diurnal Grid Factor';
      break;
    case 'simulated_carbon':
      label = 'SIMULATED CARBON';
      badgeColor = 'bg-purple-500/10 text-purple-300 border-purple-500/30';
      desc = 'Synthesized regional grid simulation profile';
      break;
    case 'externally_supplied':
      label = 'EXTERNALLY SUPPLIED';
      badgeColor = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
      desc = 'Live API emission factor from electricity grid balancing authority';
      break;
  }

  return (
    <div className="inline-flex items-center gap-1.5" title={desc}>
      <span className={`px-2 py-0.5 text-xs rounded-full border ${badgeColor} tracking-wider`}>
        {label}
      </span>
      {confidence !== undefined && (
        <span className="text-[10px] text-slate-400 font-mono">
          ({Math.round(confidence * 100)}% conf)
        </span>
      )}
    </div>
  );
};
