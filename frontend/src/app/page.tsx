'use client';

import React, { useState } from 'react';
import { useSnapshot } from '@/hooks/useSnapshot';
import dynamic from 'next/dynamic';
import { Header } from '@/components/dashboard/Header';
import { MissionControlView } from '@/components/dashboard/MissionControlView';
import { TelemetryHUD } from '@/components/dashboard/TelemetryHUD';

const SimulationView = dynamic(
  () => import('@/components/sim/SimulationView').then(mod => mod.SimulationView),
  { ssr: false }
);

export default function Home() {
  const { data: snapshot, events } = useSnapshot(1000);
  const [mode, setMode] = useState<'3D' | 'DATA'>('3D');
  const [selectedSatId, setSelectedSatId] = useState<string | null>(null);

  // Stats for header
  const satCount = snapshot?.satellites?.length || 0;
  const cdmCount = snapshot?.cdm_warnings?.length || 0;
  const collisions = snapshot?.collisions_total || 0;

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-black text-white selection:bg-emerald-500/30">
      <Header 
        timestamp={snapshot?.timestamp || null}
        satCount={satCount}
        cdmCount={cdmCount}
        collisions={collisions}
        mode={mode}
        onModeSwitch={setMode}
      />
      
      <main className="flex-1 flex overflow-hidden relative">
        {mode === '3D' ? (
          <SimulationView 
            snapshot={snapshot} 
            onSatSelect={setSelectedSatId}
            selectedSatId={selectedSatId}
          />
        ) : (
          <MissionControlView 
            snapshot={snapshot} 
            events={events}
            onSatSelect={setSelectedSatId}
            selectedSatId={selectedSatId}
          />
        )}

        {/* Cinematic Technical HUD Overlay (V3) */}
        {selectedSatId && (
            <TelemetryHUD 
                sat={snapshot?.satellites.find(s => s.id === selectedSatId)} 
                onClose={() => setSelectedSatId(null)} 
            />
        )}
      </main>

    </div>
  );
}
