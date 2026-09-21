export const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
export async function api(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  const form = options.body instanceof FormData;
  try {
    const response = await fetch(`${API_BASE}/api${path}`, { ...options, signal: controller.signal,
      headers: { ...(!form && options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(import.meta.env.VITE_API_WRITE_TOKEN ? { 'X-Write-Token': import.meta.env.VITE_API_WRITE_TOKEN } : {}), ...options.headers },
      body: options.body && !form ? JSON.stringify(options.body) : options.body });
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : data.detail?.map(d => `${d.loc.at(-1)}: ${d.msg}`).join('; ') || 'The request could not be completed.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The calculation took too long. Please try again.');
    if (error instanceof TypeError) throw new Error('Cannot reach the backend. Start the BridgeTwin API and retry.');
    throw error;
  } finally { clearTimeout(timeout); }
}
export const post = (path, body = {}) => api(path, { method: 'POST', body });
