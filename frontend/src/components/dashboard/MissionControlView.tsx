'use client';

import React from 'react';
import { FuelGauge } from './FuelGauge';
import { BullseyePlot } from './BullseyePlot';
import { EventLog } from './EventLog';
import { SnapshotData, ConjunctionWarning, SatelliteData } from '../../types/sim';

export function MissionControlView({ 
  snapshot, 
  events, 
  onSatSelect, 
  selectedSatId 
}: { 
  snapshot: SnapshotData | null, 
  events: any[], 
  onSatSelect: (id: string) => void, 
  selectedSatId: string | null 
}) {

  return (
    <div className="flex-1 p-6 grid grid-cols-12 grid-rows-6 gap-6 bg-[#05060b] relative">
      {/* 4 PANEL GRID (Block 5/6 style) */}
      
      {/* LEFT: GROUND TRACK */}
      <div className="col-span-8 row-span-4 bg-zinc-900/20 backdrop-blur-md rounded-sm border border-white/5 flex flex-col p-5 shadow-2xl">
          <div className="text-[10px] font-mono text-cyan-400 mb-3 uppercase tracking-[0.2em] font-bold">Orbit Trajectory Multi-Vector Analysis</div>
          <div className="flex-1 bg-black/40 rounded-sm border border-white/5 flex items-center justify-center text-zinc-800 font-mono text-xs relative overflow-hidden">
              <div className="absolute inset-0 opacity-10 bg-[linear-gradient(rgba(0,242,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,242,255,0.1)_1px,transparent_1px)] bg-[size:20px_20px]" />
              [ GEOSPATIAL_ENGINE_OFFLINE ]
          </div>
      </div>

      {/* RIGHT TOP: BULLSEYE */}
      <div className="col-span-4 row-span-3 bg-zinc-900/20 backdrop-blur-md rounded-sm border border-white/5 flex flex-col p-5 shadow-2xl">
          <div className="text-[10px] font-mono text-cyan-400 mb-2 uppercase tracking-[0.2em] font-bold">Conjunction Risk Bullseye</div>
          <div className="flex-1">
              <BullseyePlot cdmWarnings={snapshot?.cdm_warnings || []} selectedSatId={selectedSatId} />
          </div>
      </div>

      {/* RIGHT BOTTOM: ACTIONABLE DECISIONS */}
      <div className="col-span-4 row-span-3 bg-zinc-900/20 backdrop-blur-md rounded-sm border border-white/5 flex flex-col p-5 shadow-2xl overflow-hidden">
          <div className="text-[10px] font-mono text-cyan-400 mb-2 uppercase tracking-[0.2em] font-bold">Actionable Decisions</div>
          <div className="flex-1 overflow-y-auto custom-scrollbar space-y-3">
              {snapshot?.cdm_warnings?.filter((c: ConjunctionWarning) => c.status === 'PENDING_APPROVAL').map((cdm: ConjunctionWarning) => (
                  <div key={`${cdm.sat_id}_${cdm.debris_id}`} className="bg-black/60 border border-white/5 p-3 rounded-sm space-y-2">
                      <div className="flex justify-between items-start">
                          <span className="text-white font-bold text-xs">{cdm.sat_id} <span className="text-zinc-500">vs</span> {cdm.debris_id}</span>
                          <span className="text-[10px] text-red-400 font-mono">Miss: {cdm.miss_distance_km.toFixed(2)}km</span>
                      </div>
                      <div className="flex gap-2">
                          <button 
                            onClick={() => fetch('http://localhost:8000/api/maneuver/approve', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ sat_id: cdm.sat_id, deb_id: cdm.debris_id, approve: true })
                            })}
                            className="flex-1 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/50 text-cyan-400 text-[9px] py-1.5 font-bold uppercase"
                          >
                              Approve
                          </button>
                          <button 
                            onClick={() => fetch('http://localhost:8000/api/maneuver/approve', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ sat_id: cdm.sat_id, deb_id: cdm.debris_id, approve: true, automate: true })
                            })}
                            className="bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 text-[9px] px-3 py-1.5 font-bold uppercase"
                          >
                              Auto
                          </button>
                      </div>
                  </div>
              ))}
              {snapshot?.cdm_warnings?.filter((c: any) => c.status === 'PENDING_APPROVAL').length === 0 && (
                  <div className="h-full flex items-center justify-center text-zinc-600 font-mono text-[10px]">
                      [ NO_PENDING_ACTIONS ]
                  </div>
              )}
          </div>
      </div>

      {/* BOTTOM LEFT: FLEET STATUS */}
      <div className="col-span-8 row-span-2 bg-zinc-900/20 backdrop-blur-md rounded-sm border border-white/5 flex flex-col p-5 shadow-2xl">
          <div className="text-[10px] font-mono text-cyan-400 mb-4 uppercase tracking-[0.2em] font-bold flex justify-between">
              <span>Constellation Health Matrix</span>
              <span className="text-zinc-500">{snapshot?.satellites?.length || 0} Assets Online</span>
          </div>
          <div className="flex gap-5 overflow-x-auto pb-2 custom-scrollbar">
              {snapshot?.satellites?.map((sat: SatelliteData) => (
                  <FuelGauge 
                      key={sat.id}
                      fuelKg={sat.fuel_kg}
                      fuelMaxKg={sat.fuel_max_kg || 50}
                      dvConsumed={sat.dv_consumed_ms || 0}
                      satId={sat.id}
                      status={sat.status}
                      onClick={onSatSelect}
                  />
              ))}
          </div>
      </div>

      {/* HUD OVERLAY: EVENT LOG */}
      <div className="fixed bottom-10 right-10 w-80 bg-zinc-950/90 backdrop-blur border border-zinc-800 p-4 shadow-2xl">
          <div className="text-[9px] font-mono text-zinc-500 mb-2 uppercase tracking-widest">Mission Event Log</div>
          <EventLog events={events} />
      </div>
    </div>
  );
}
