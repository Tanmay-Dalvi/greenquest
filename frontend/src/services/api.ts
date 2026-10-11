import {
  MissionPreferenceRequest,
  MissionResponse,
} from '../types/mission';
import { generateClientFallbackMission } from './fallbackMissions';

function getApiBase(): string {
  let url = (import.meta as any).env?.VITE_API_URL || '';
  if (!url) return '';
  url = url.trim();
  // Strip trailing slashes
  url = url.replace(/\/+$/, '');
  // If protocol is missing (e.g. Render 'host' property provides 'app.onrender.com'), prepend https://
  if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`;
  }
  return url;
}

const API_BASE = getApiBase();

export async function requestMission(
  preferences: MissionPreferenceRequest
): Promise<{ mission: MissionResponse; usedClientOfflineFallback: boolean }> {
  try {
    const controller = new AbortController();
    // 35s timeout to allow local open-weight model (Gemma 3 1B on CPU takes ~20-25s) before triggering fallback
    const timeoutId = setTimeout(() => controller.abort(), 35000);

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
    // 8s timeout to accommodate Render cloud cold starts and TLS negotiation latency
    const timeoutId = setTimeout(() => controller.abort(), 8000);
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
