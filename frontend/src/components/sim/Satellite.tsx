'use client';

import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Line } from '@react-three/drei';
import * as THREE from 'three';

const EARTH_RADIUS_KM = 6371;

function llaToXYZ(lat: number, lon: number, alt: number) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  const r = EARTH_RADIUS_KM + alt;
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.sin(theta)
  );
}

const STATUS_COLORS: Record<string, string> = {
  'NOMINAL': '#00FF41',
  'EVADING': '#F6C90E',
  'CRITICAL': '#FF3B30',
  'GRAVEYARD': '#7F8C8D',
  'BLACKOUT': '#5A6A8A',
};

export function Satellite({ data, onSelect, selected }: { data: any, onSelect: (id: string) => void, selected: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [path, setPath] = useState<[number, number, number][]>([]);

  useEffect(() => {
    if (selected) {
      fetch(`http://localhost:8000/api/simulate/path/${data.id}`)
        .then(res => res.json())
        .then(json => {
            if (json.path) setPath(json.path);
        });
    }
  }, [selected, data.id]);

  const pos = llaToXYZ(data.lat, data.lon, data.alt_km);
  const color = STATUS_COLORS[data.status] || '#00FF41';

  const trailPositions = (data.trail_points || []).map(
    ([lat, lon, alt]: [number, number, number]) => llaToXYZ(lat, lon, alt).toArray()
  );

  useFrame(({ clock }) => {
    if (meshRef.current) {
      if (data.status === 'NOMINAL') {
        const pulse = 1 + Math.sin(clock.elapsedTime * 2) * 0.1;
        meshRef.current.scale.setScalar(pulse);
      }
    }
    if (ringRef.current && selected) {
        ringRef.current.scale.setScalar(1 + Math.sin(clock.elapsedTime * 5) * 0.2);
        ringRef.current.rotation.z += 0.01;
    }
  });

  return (
    <group position={pos}>
      {/* Orbital Path (Future Prediction) */}
      {selected && path.length > 1 && (
        <Line
          points={path.map(([lat, lon, alt]) => llaToXYZ(lat, lon, alt).toArray())}
          color={color}
          lineWidth={2}
          transparent
          opacity={0.6}
        />
      )}

      {/* Technical Selection Ring */}
      {selected && (
        <mesh ref={ringRef} rotation-x={Math.PI / 2}>
            <ringGeometry args={[80, 90, 32]} />
            <meshBasicMaterial color={color} transparent opacity={0.4} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Satellite Icon (HTML for crispness) */}
      <Html distanceFactor={2000} position={[0, 0, 0]}>
        <div 
          onClick={(e) => {
            e.stopPropagation();
            onSelect(data.id);
          }}
          className={`cursor-pointer transition-all duration-300 transform ${selected ? 'scale-150' : 'scale-100'} ${hovered ? 'opacity-100' : 'opacity-80'}`}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill={color} className="drop-shadow-[0_0_12px_rgba(0,242,255,0.6)]">
            {/* Satellite Body & Solar Panels */}
            <path d="M12 8L12 16" stroke={color} strokeWidth="1.5" />
            <rect x="10" y="10" width="4" height="4" rx="1" fill={color} />
            <path d="M2 10H10V14H2V10Z" fill={color} opacity="0.6" />
            <path d="M14 10H22V14H22V10Z" fill={color} opacity="0.6" />
            <circle cx="12" cy="7" r="1.5" fill={color} />
          </svg>
          {selected && (
             <div className="absolute top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black/80 text-[10px] font-mono px-2 py-0.5 border border-white/10 rounded">
                {data.id}
             </div>
          )}
        </div>
      </Html>

      {trailPositions.length > 1 && (
        <Line
          points={trailPositions}
          color={color}
          lineWidth={1}
          transparent
          opacity={0.4}
        />
      )}
    </group>
  );
}
