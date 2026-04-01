export interface Vector3D {
  x: number;
  y: number;
  z: number;
}

export interface SatelliteData {
  id: string;
  lat: number;
  lon: number;
  alt_km: number;
  status: string;
  fuel_kg: number;
  fuel_max_kg: number;
  dv_consumed_ms: number;
}

export interface DebrisObject {
  r: Vector3D;
}

export interface ConjunctionWarning {
  sat_id: string;
  debris_id: string;
  tca: string;
  miss_distance_km: number;
  status: 'PENDING_APPROVAL' | 'APPROVED' | 'EXECUTED' | 'IGNORED';
  auto_approve: boolean;
}

export interface SnapshotData {
  timestamp: string;
  satellites: SatelliteData[];
  debris_cloud: DebrisObject[];
  collisions_total?: number;
  cdm_warnings?: ConjunctionWarning[];
}
