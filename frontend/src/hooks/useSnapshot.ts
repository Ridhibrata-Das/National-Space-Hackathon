import { useEffect, useRef, useState, useCallback } from 'react';
import { SnapshotData } from '@/types/sim';

export function useSnapshot(intervalMs = 1000) {
  const [data, setData] = useState<SnapshotData | null>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [fps, setFps] = useState(0);
  const prevRef = useRef<SnapshotData | null>(null);
  const frameRef = useRef(0);
  const lastFrameTime = useRef(performance.now());

  const poll = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/visualization/snapshot');
      if (!res.ok) throw new Error('Network response was not ok');
      const newData = await res.json();
      const prev = prevRef.current;

      // Event Detection (Diffing)
      if (prev) {
        // Detect new CDM warnings
        const newCDMs = (newData.cdm_warnings?.length ?? 0) - (prev.cdm_warnings?.length ?? 0);
        if (newCDMs > 0) {
          setEvents(e => [...e.slice(-19), {
            type: 'NEW_CDM', 
            count: newCDMs, 
            time: newData.timestamp || new Date().toISOString()
          }]);
        }

        // Detect Status Changes
        newData.satellites?.forEach(sat => {
          const old = prev.satellites?.find(s => s.id === sat.id);
          if (old && old.status !== sat.status) {
            setEvents(e => [...e.slice(-19), {
              type: 'STATUS_CHANGE',
              satId: sat.id,
              from: old.status,
              to: sat.status,
              time: newData.timestamp || new Date().toISOString()
            }]);
          }
        });
      }

      prevRef.current = newData;
      setData(newData);

      // FPS tracking (conceptual for UI)
      const now = performance.now();
      frameRef.current++;
      if (now - lastFrameTime.current >= 1000) {
        setFps(frameRef.current);
        frameRef.current = 0;
        lastFrameTime.current = now;
      }
    } catch (err) {
      console.error('Snapshot poll error:', err);
    }
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, intervalMs);
    return () => clearInterval(id);
  }, [poll, intervalMs]);

  return { data, events, fps };
}
