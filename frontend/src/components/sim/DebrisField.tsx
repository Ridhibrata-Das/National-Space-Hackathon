'use client';

import React, { useMemo } from 'react';
import * as THREE from 'three';
import { DebrisObject } from '@/types/sim';

export function DebrisField({ debris }: { debris: DebrisObject[] }) {
  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(debris.length * 3);
    const col = new Float32Array(debris.length * 3);
    
    let validCount = 0;
    debris.forEach((d) => {
      if (d && d.r) {
        pos[validCount * 3] = d.r.x;
        pos[validCount * 3 + 1] = d.r.y;
        pos[validCount * 3 + 2] = d.r.z;
        
        col[validCount * 3] = 0.5;
        col[validCount * 3 + 1] = 0.5;
        col[validCount * 3 + 2] = 0.5;
        validCount++;
      }
    });

    return [pos, col];
  }, [debris]);

  if (debris.length === 0) return null;

  return (
    <points frustumCulled={false}>
      <bufferGeometry attach="geometry">
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={30}
        sizeAttenuation={true}
        vertexColors={true}
        transparent={false}
        opacity={1.0}
        blending={THREE.NormalBlending}
      />
    </points>
  );
}
