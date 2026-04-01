'use client';

import React from 'react';

interface FuelGaugeProps {
  fuelKg: number;
  fuelMaxKg: number;
  dvConsumed: number;
  satId: string;
  status: string;
  onClick: (id: string) => void;
}

const STATUS_COLORS: Record<string, string> = {
  'NOMINAL': '#00FF41',
  'EVADING': '#F6C90E',
  'CRITICAL': '#FF3B30',
  'GRAVEYARD': '#7F8C8D',
};

export function FuelGauge({ fuelKg, fuelMaxKg, dvConsumed, satId, status, onClick }: FuelGaugeProps) {
  const pct = fuelMaxKg > 0 ? fuelKg / fuelMaxKg : 0;
  const radius = 28;
  const circ = 2 * Math.PI * radius;
  const offset = circ * (1 - pct);

  const color = 
    pct > 0.5 ? '#00FF41' :
    pct > 0.2 ? '#F6C90E' :
    pct > 0.1 ? '#FF6B35' : '#FF3B30';

  const borderColor = STATUS_COLORS[status] || '#1E2A3E';

  return (
    <div
      onClick={() => onClick(satId)}
      className="flex flex-col items-center p-2 rounded-lg cursor-pointer bg-zinc-900/50 hover:bg-zinc-800 transition-colors w-24 border"
      style={{ borderColor: `${borderColor}44` }}
    >
      <svg width="64" height="64" viewBox="0 0 64 64" className="mb-1">
        <circle cx="32" cy="32" r={radius} fill="none" stroke="#1E2A3E" strokeWidth="4" />
        <circle
          cx="32" cy="32" r={radius}
          fill="none" stroke={color} strokeWidth="4"
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 32 32)"
          className="transition-all duration-700 ease-out"
        />
        <text 
          x="32" y="38" 
          textAnchor="middle" 
          fontSize="10" 
          fontFamily="JetBrains Mono" 
          fill={color}
          className="font-bold"
        >
          {(pct * 100).toFixed(0)}%
        </text>
      </svg>
      <div className="text-[10px] text-zinc-400 font-mono">{fuelKg.toFixed(1)}kg</div>
      <div className="text-[10px] font-bold text-zinc-100 truncate w-full text-center">{satId}</div>
      <div className="text-[9px] text-zinc-500">ΔV {dvConsumed.toFixed(1)}m/s</div>
    </div>
  );
}
