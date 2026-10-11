/**
 * Normalizes API base URL across local dev, Render cloud deployments, and custom domains.
 */
export function normalizeApiBase(rawUrl?: string): string {
  let url = (rawUrl !== undefined ? rawUrl : (import.meta as any).env?.VITE_API_URL) || '';
  if (!url) return '';
  url = url.trim();
  // Strip trailing slashes
  url = url.replace(/\/+$/, '');

  const isLocal = url.includes('localhost') || url.includes('127.0.0.1');

  // If provided as an internal hostname without dots or localhost (e.g. Render host "greenquest-api-mhjr"),
  // append .onrender.com to form a valid public URL.
  if (!isLocal && !url.includes('.') && !url.includes(':') && !url.startsWith('http')) {
    url = `${url}.onrender.com`;
  }

  // Prepend protocol scheme if omitted
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = isLocal ? `http://${url}` : `https://${url}`;
  }
  return url;
}

