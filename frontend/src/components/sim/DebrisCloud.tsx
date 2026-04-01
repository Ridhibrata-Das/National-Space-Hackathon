'use client';

import React, { useRef, useEffect, useMemo } from 'react';
import * as THREE from 'three';

const EARTH_RADIUS_KM = 6371;

function llaToVec3(lat: number, lon: number, alt: number): [number, number, number] {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  const r = EARTH_RADIUS_KM + alt;
  return [
    -r * Math.sin(phi) * Math.cos(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.sin(theta)
  ];
}

const DEBRIS_COLOR_SAFE = new THREE.Color('#2A3A50');
const DEBRIS_COLOR_WARNING = new THREE.Color('#FF3B30');

export function DebrisCloud({ debris, cdmDebrisIds = new Set() }: { debris: any[], cdmDebrisIds?: Set<string> }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  useEffect(() => {
    if (!meshRef.current || !debris.length) return;

    debris.forEach(([id, lat, lon, alt], i) => {
      const [x, y, z] = llaToVec3(lat, lon, alt);
      dummy.position.set(x, y, z);
      dummy.updateMatrix();
      meshRef.current?.setMatrixAt(i, dummy.matrix);

      const color = cdmDebrisIds.has(id) ? DEBRIS_COLOR_WARNING : DEBRIS_COLOR_SAFE;
      meshRef.current?.setColorAt(i, color);
    });

    meshRef.current.instanceMatrix.needsUpdate = true;
    if (meshRef.current.instanceColor) {
      meshRef.current.instanceColor.needsUpdate = true;
    }
  }, [debris, cdmDebrisIds, dummy]);

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, debris.length || 1]}
      frustumCulled={false}
    >
      <sphereGeometry args={[15, 4, 4]} />
      <meshBasicMaterial vertexColors />
    </instancedMesh>
  );
}
