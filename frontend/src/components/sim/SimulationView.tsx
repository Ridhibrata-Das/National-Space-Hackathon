'use client';

import React, { useState, useEffect } from 'react';
import * as THREE from 'three';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { Earth } from './Earth';
import { Satellite } from './Satellite';
import { DebrisField } from './DebrisField';

import { SnapshotData, SatelliteData } from '@/types/sim';

export function SimulationView({ snapshot, onSatSelect, selectedSatId }: { snapshot: SnapshotData | null, onSatSelect: (id: string) => void, selectedSatId: string | null }) {
  const [visMode, setVisMode] = useState<'ALL' | 'CUSTOM'>('ALL');
  const [multiSelectIds, setMultiSelectIds] = useState<string[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsReady(true), 1200);
    return () => clearTimeout(timer);
  }, []);

  const showDebris = isReady;

  return (
    <div className="flex-1 w-full h-full relative bg-black">
       {/* Visibility Toggle HUD */}
       <div className="absolute top-20 left-6 z-10 flex flex-col gap-2 max-h-[70vh] w-64">
          <div className="text-[10px] font-mono text-cyan-400 mb-2 tracking-widest uppercase opacity-70">Visibility Customization</div>
          <div className="flex gap-2 mb-2">
            <button
                onClick={() => setVisMode('ALL')}
                className={`flex-1 px-3 py-1.5 text-[10px] font-mono border ${visMode === 'ALL' ? 'bg-cyan-500/20 border-cyan-400 text-cyan-400' : 'bg-black/60 border-white/10 text-zinc-500 hover:border-white/30'}`}
            >
                SHOW ALL
            </button>
            <button
                onClick={() => setVisMode('CUSTOM')}
                className={`flex-1 px-3 py-1.5 text-[10px] font-mono border ${visMode === 'CUSTOM' ? 'bg-cyan-500/20 border-cyan-400 text-cyan-400' : 'bg-black/60 border-white/10 text-zinc-500 hover:border-white/30'}`}
            >
                CUSTOM
            </button>
          </div>
          
          {visMode === 'CUSTOM' && (
            <div className="bg-black/80 border border-white/10 p-3 flex flex-col gap-3 overflow-y-auto custom-scrollbar">
                <div className="text-[9px] text-zinc-500 uppercase tracking-wider mb-1">Select Targets (Paths Active)</div>
                {snapshot?.satellites.map(sat => (
                    <label key={sat.id} className="flex items-center gap-2 cursor-pointer group">
                        <input 
                            type="checkbox" 
                            checked={multiSelectIds.includes(sat.id)}
                            onChange={() => {
                                setMultiSelectIds(prev => 
                                    prev.includes(sat.id) ? prev.filter(i => i !== sat.id) : [...prev, sat.id]
                                )
                            }}
                            className="accent-cyan-500 opacity-50 group-hover:opacity-100"
                        />
                        <span className={`text-[10px] font-mono ${multiSelectIds.includes(sat.id) ? 'text-cyan-400' : 'text-zinc-500'}`}>
                            {sat.id}
                        </span>
                    </label>
                ))}
            </div>
          )}
       </div>

      <Canvas
        camera={{ position: [0, 0, 20000], fov: 45, near: 10, far: 500000 }}
        onCreated={({ scene }) => {
          scene.background = new THREE.Color('#000000');
        }}
        gl={{ 
          antialias: true,
          powerPreference: "high-performance"
        }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[150000, 0, 0]} intensity={1.2} color="#ffffff" />
        
        <Stars radius={200000} depth={100} count={5000} factor={6} fade />
        
        <Earth simTime={snapshot?.timestamp} />
        
        {snapshot?.satellites.filter((sat: SatelliteData) => visMode === 'ALL' || multiSelectIds.includes(sat.id)).map((sat: SatelliteData) => (
          <Satellite 
            key={sat.id} 
            data={sat} 
            onSelect={onSatSelect} 
            selected={selectedSatId === sat.id || multiSelectIds.includes(sat.id)} 
          />
        ))}
        
        {showDebris && snapshot && snapshot.debris_cloud && (
            <DebrisField 
              debris={snapshot.debris_cloud} 
            />
        )}
        
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          minDistance={7000}
          maxDistance={150000}
        />
      </Canvas>

      {/* BOTTOM SPEED CONTROLS */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-zinc-900/80 backdrop-blur-md px-6 py-3 rounded-sm border border-zinc-800 flex items-center gap-6">
          <div className="flex gap-4 text-xs font-mono text-zinc-400">
              <button className="hover:text-emerald-400">⏮</button>
              <button className="hover:text-emerald-400">⏸</button>
              <button className="text-emerald-400">▶ 1x</button>
              <button className="hover:text-emerald-400">⏩</button>
              <button className="hover:text-emerald-400">⏭</button>
          </div>
          <div className="h-4 w-px bg-zinc-700" />
          <select className="bg-transparent text-[10px] font-mono text-zinc-300 outline-none">
              <option>FREE CAMERA</option>
              {snapshot?.satellites.map((s: SatelliteData) => (
                  <option key={s.id} value={s.id}>{s.id}</option>
              ))}
          </select>
      </div>
    </div>
  );
}
