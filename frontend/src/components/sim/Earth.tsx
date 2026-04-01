'use client';

import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useTexture } from '@react-three/drei';

const EARTH_RADIUS_KM = 6371;

export function Earth({ simTime }: { simTime: string | undefined }) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Load NASA Textures
  const [colorMap, normalMap, lightsMap] = useTexture([
    'https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg',
    'https://threejs.org/examples/textures/planets/earth_normal_2048.jpg',
    'https://threejs.org/examples/textures/planets/earth_lights_2048.png'
  ]);

  useFrame(({ clock }) => {
    if (!meshRef.current || !simTime) return;
    const epochS = new Date(simTime).getTime() / 1000;
    // J2000 rotation approx: 1 rotation = 86164s (sidereal day)
    const OMEGA_E = 7.2921150e-5;
    meshRef.current.rotation.y = (epochS * OMEGA_E) % (Math.PI * 2);
  });

  return (
    <group>
      {/* Atmosphere Glow */}
      <mesh scale={[1.02, 1.02, 1.02]}>
        <sphereGeometry args={[EARTH_RADIUS_KM, 64, 64]} />
        <meshStandardMaterial
          color="#4ca9ff"
          transparent
          opacity={0.15}
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      
      {/* Main Earth sphere */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[EARTH_RADIUS_KM, 64, 64]} />
        <meshStandardMaterial 
          map={colorMap}
          normalMap={normalMap}
          emissiveMap={lightsMap}
          emissive="#ffffff"
          emissiveIntensity={0.2}
          roughness={0.8} 
          metalness={0.1}
        />
      </mesh>
    </group>
  );
}
