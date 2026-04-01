'use client';

import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { PolarArea } from 'react-chartjs-2';

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend);

export function BullseyePlot({ cdmWarnings, selectedSatId }: { cdmWarnings: any[], selectedSatId: string | null }) {
  const relevant = cdmWarnings?.filter(c => !selectedSatId || c.sat_id === selectedSatId) || [];

  const data = {
    labels: relevant.map(c => c.deb_id),
    datasets: [{
      data: relevant.map(c => Math.min(c.tca_s / 3600, 24)), // hours to TCA
      backgroundColor: relevant.map(c => 
        c.miss_km < 0.1 ? 'rgba(255, 59, 48, 0.8)' :
        c.miss_km < 1.0 ? 'rgba(255, 107, 53, 0.7)' :
        'rgba(246, 201, 14, 0.6)'
      ),
      borderColor: 'transparent',
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        grid: { color: '#27272a' },
        angleLines: { color: '#27272a' },
        ticks: { display: false },
        min: 0,
        max: 24
      }
    },
    plugins: {
      legend: { display: false }
    }
  };

  if (relevant.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-600 font-mono text-sm">
        NO TARGETS DETECTED
      </div>
    );
  }

  return (
    <div className="p-4 h-full">
      <PolarArea data={data} options={options} />
    </div>
  );
}
