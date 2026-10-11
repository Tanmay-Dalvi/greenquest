import {
  MissionPreferenceRequest,
  MissionResponse,
} from '../types/mission';
import { generateClientFallbackMission } from './fallbackMissions';

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

export async function requestMission(
  preferences: MissionPreferenceRequest
): Promise<{ mission: MissionResponse; usedClientOfflineFallback: boolean }> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000); // 12s client timeout

    const res = await fetch(`${API_BASE}/api/missions/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data: MissionResponse = await res.json();
    return { mission: data, usedClientOfflineFallback: false };
  } catch (err) {
    console.warn('Backend API request failed or offline; triggering client fallback:', err);
    // Seamless client-side deterministic fallback
    const offlineMission = generateClientFallbackMission(preferences);
    return { mission: offlineMission, usedClientOfflineFallback: true };
  }
}

export async function checkBackendHealth(): Promise<{ online: boolean; message?: string }> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(`${API_BASE}/api/health`, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      return { online: true };
    }
    return { online: false, message: `HTTP ${res.status}` };
  } catch {
    return { online: false, message: 'Unreachable / Offline' };
  }
}
