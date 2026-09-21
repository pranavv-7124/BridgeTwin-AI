import { create } from 'zustand';
import { api, post } from '../services/api';

export const useBridge = create((set, get) => ({
  state: null, model: null, datasets: [], page: location.hash.slice(1) || 'overview', selectedId: 'PIER_02',
  busy: false, loading: true, error: null, toast: null, playing: false, speed: 1,
  scenario: null, plan: null, planComparison: null,
  navigate: (page) => { location.hash = page; set({ page }); },
  select: (selectedId) => set({ selectedId }),
  setPlaying: (playing) => set({ playing }), setSpeed: (speed) => set({ speed }),
  dismissError: () => set({ error: null }),
  notify: (text) => { set({ toast: text }); setTimeout(() => set({ toast: null }), 4500); },
  load: async () => {
    set({ loading: true, error: null });
    try { const [state, model, datasets] = await Promise.all([api('/bridge'), api('/model-info'), api('/datasets')]); set({ state, model, datasets, loading: false }); }
    catch (e) { set({ error: e.message, loading: false }); }
  },
  refresh: async () => { const state = await api('/bridge'); set({ state }); },
  task: async (work) => {
    if (get().busy) return;
    set({ busy: true, error: null });
    try { return await work(); } catch (e) { set({ error: e.message, playing: false }); } finally { set({ busy: false }); }
  },
  tick: async (months = 1) => get().task(async () => {
    const remaining = 240 - get().state.simulation.month;
    if (remaining <= 0) { set({ playing: false }); get().notify('The timeline has reached 2046. Reset to explore again.'); return; }
    const state = await post('/simulate/future', { months: Math.min(months, remaining) });
    set({ state, plan: null, planComparison: null, ...(state.simulation.month === 240 ? { playing: false } : {}) });
  }),
  reset: async () => get().task(async () => {
    set({ playing: false }); const state = await post('/simulate/reset');
    set({ state, scenario: null, plan: null, planComparison: null }); get().notify('Original synthetic baseline restored.');
  }),
  runScenario: async (inputs) => get().task(async () => {
    set({ playing: false }); const scenario = await post('/simulate', inputs); set({ scenario }); await get().refresh(); get().notify('Scenario calculated. Compare the projected condition below.');
  }),
  applyScenario: async () => get().task(async () => {
    const state = await post('/simulate/apply', { run_id: get().scenario.id });
    set({ state, plan: null, planComparison: null }); get().notify('Scenario inputs applied. Play the timeline to watch the bridge evolve.');
  }),
  optimize: async (budget, horizon = 5) => get().task(async () => {
    set({ playing: false }); const plan = await post('/maintenance/optimize', { budget, horizon }); set({ plan, planComparison: null }); get().notify('Maintenance budget optimized.');
  }),
  simulatePlan: async (action_ids, budget, apply = false, horizon = 5) => get().task(async () => {
    set({ playing: false }); const result = await post('/maintenance/simulate', { action_ids, budget, apply, horizon });
    set({ planComparison: result, ...(result.state ? { state: result.state, plan: null } : {}) });
    if (!result.state) await get().refresh(); get().notify(apply ? 'Maintenance applied to the simulated bridge.' : 'Repair and no-maintenance futures calculated.');
  }),
  upload: async (file, source) => get().task(async () => {
    const body = new FormData(); body.append('file', file); body.append('source', source);
    await api('/data/upload', { method: 'POST', body }); const datasets = await api('/datasets'); set({ datasets });
    get().notify('Dataset imported. Original observations are preserved.');
  }),
}));
window.addEventListener('hashchange', () => useBridge.setState({ page: location.hash.slice(1) || 'overview' }));
