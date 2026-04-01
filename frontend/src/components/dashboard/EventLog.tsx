'use client';

import React from 'react';

const EVENT_STYLES: Record<string, { color: string, icon: string }> = {
  'NEW_CDM': { color: '#FF3B30', icon: '⚠' },
  'COLLISION': { color: '#FF3B30', icon: '✕' },
  'STATUS_CHANGE': { color: '#00A3FF', icon: '↻' },
  'SLOT_RECOVERED': { color: '#00FF41', icon: '✓' },
  'BURN_FIRED': { color: '#7B68EE', icon: '🔥' },
};

export function EventLog({ events }: { events: any[] }) {
  return (
    <div className="flex flex-col gap-1 overflow-y-auto max-h-[180px] scrollbar-thin scrollbar-thumb-zinc-700">
      {[...events].reverse().map((ev, i) => {
        const style = EVENT_STYLES[ev.type] || { color: '#8A9BBF', icon: 'ℹ' };
        return (
          <div key={i} className="flex gap-3 py-1 border-b border-zinc-800 items-baseline font-mono text-[11px]">
            <span style={{ color: style.color }}>{style.icon}</span>
            <span className="text-zinc-600">
              {new Date(ev.time).toISOString().slice(11, 23)}
            </span>
            <span className="text-zinc-100 font-bold">{ev.satId || ''}</span>
            <span style={{ color: style.color }}>
              {ev.type === 'STATUS_CHANGE' ? `${ev.from} → ${ev.to}` :
               ev.type === 'NEW_CDM' ? `COLLISION RISK: +${ev.count} WARNING` :
               ev.type === 'COLLISION' ? `SATELLITE LOSS DETECTED` :
               ev.type}
            </span>
          </div>
        );
      })}
      {events.length === 0 && (
        <div className="text-zinc-700 italic text-center py-4">No active mission events.</div>
      )}
    </div>
  );
}
