'use client';

import React from 'react';

interface HeaderProps {
  timestamp: string | null;
  satCount: number;
  cdmCount: number;
  collisions: number;
  mode: '3D' | 'DATA';
  onModeSwitch: (mode: '3D' | 'DATA') => void;
}

export function Header({ timestamp, satCount, cdmCount, collisions, mode, onModeSwitch }: HeaderProps) {
  return (
    <header className="flex h-16 items-center justify-between px-6 bg-zinc-950 border-b border-zinc-900">
      <div className="flex items-center gap-8">
        <div className="text-xl font-black tracking-tighter text-white">ORBITAL INSIGHT</div>
        <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex flex-col">
                <span className="text-zinc-500 uppercase text-[9px]">Mission Clock</span>
                <span className="text-emerald-400">{timestamp ? new Date(timestamp).toISOString().slice(11, 23) : '00:00:00.000'}</span>
            </div>
            <div className="h-6 w-px bg-zinc-800" />
            <div className="flex gap-6">
                <Stat label="FLT" value={satCount} color="text-zinc-100" />
                <Stat label="CDM" value={cdmCount} color={cdmCount > 0 ? "text-red-500" : "text-zinc-500"} />
                <Stat label="COL" value={collisions} color={collisions > 0 ? "text-red-600" : "text-zinc-500"} />
            </div>
        </div>
      </div>

      <div className="flex bg-zinc-900 p-1 rounded-sm gap-1">
        <ModeButton active={mode === '3D'} onClick={() => onModeSwitch('3D')} label="3D SIM" />
        <ModeButton active={mode === 'DATA'} onClick={() => onModeSwitch('DATA')} label="MISSION CONTROL" />
      </div>
    </header>
  );
}

function Stat({ label, value, color }: { label: string, value: number, color: string }) {
    return (
        <div className="flex gap-1.5 items-baseline">
            <span className="text-zinc-600 text-[9px]">{label}</span>
            <span className={`font-bold ${color}`}>{value}</span>
        </div>
    );
}

function ModeButton({ active, onClick, label }: { active: boolean, onClick: () => void, label: string }) {
    return (
        <button 
            onClick={onClick}
            className={`px-4 py-1.5 text-[10px] font-bold transition-all ${active ? 'bg-emerald-500 text-black' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
            {label}
        </button>
    );
}
