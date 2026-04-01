'use client';

import React from 'react';

interface TelemetryHUDProps {
  sat: any;
  onClose: () => void;
}

export function TelemetryHUD({ sat, onClose }: TelemetryHUDProps) {
  if (!sat) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
      <div className="w-[450px] bg-zinc-950/80 backdrop-blur-xl border border-cyan-500/30 p-8 rounded-sm shadow-[0_0_50px_rgba(0,242,255,0.1)] pointer-events-auto relative overflow-hidden">
        {/* Scanline effect */}
        <div className="absolute inset-0 pointer-events-none opacity-5 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[size:100%_4px]" />
        
        <div className="flex justify-between items-start mb-8 relative">
          <div>
            <div className="text-[10px] font-mono text-cyan-500/70 tracking-[0.3em] uppercase mb-1">Satellite Identifier</div>
            <div className="text-3xl font-black tracking-tighter text-white">
              {sat.id}
              <span className="ml-3 text-xs font-mono text-cyan-400 bg-cyan-400/10 px-2 py-0.5 rounded-full border border-cyan-400/20">
                {sat.status}
              </span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-zinc-500 hover:text-white transition-colors p-2"
          >
            ✕
          </button>
        </div>

        <div className="grid grid-cols-2 gap-y-6 gap-x-12 relative">
          <DataPoint label="Latitude" value={`${sat.lat.toFixed(4)}°`} />
          <DataPoint label="Longitude" value={`${sat.lon.toFixed(4)}°`} />
          <DataPoint label="Altitude" value={`${sat.alt_km.toFixed(1)} km`} />
          <DataPoint label="Fuel Reserves" value={`${(sat.fuel_kg).toFixed(1)} kg`} color="text-emerald-400" />
          <DataPoint label="System Status" value="OPTIONAL" color="text-cyan-400" />
          <DataPoint label="Encryption" value="AES-256" color="text-zinc-500" />
        </div>

        <div className="mt-10 pt-6 border-t border-white/5 flex justify-between items-center relative">
          <div className="flex gap-2">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <div className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest">Live Telemetry Link Active</div>
          </div>
          <div className="text-[9px] font-mono text-zinc-600">CMD_SOURCE: GROUND_STATION_01</div>
        </div>
      </div>
    </div>
  );
}

function DataPoint({ label, value, color = "text-white" }: { label: string, value: string | number, color?: string }) {
  return (
    <div className="flex flex-col border-l border-zinc-800 pl-4 py-1">
      <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest mb-1">{label}</span>
      <span className={`text-lg font-mono tracking-tight font-bold ${color}`}>{value}</span>
    </div>
  );
}
