import { useEffect } from 'react';
import { useBridge } from '../store/bridgeStore';
export function useWebTools() {
  useEffect(() => {
    const context = document.modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    const entries = [
      { name: 'read_bridge_state', description: 'Read the active bridge condition and provenance. Does not modify the simulation.', inputSchema: { type: 'object', properties: {}, additionalProperties: false }, annotations: { readOnlyHint: true, untrustedContentHint: false }, execute(input) { if (Object.keys(input || {}).length) throw new Error('No parameters accepted.'); const s=useBridge.getState().state; if(!s)throw new Error('Bridge state is not loaded.'); return {bridge:s.bridge,summary:s.summary,components:s.components,revision:s.revision,source:s.metadata.data_source}; } },
      { name: 'inspect_bridge_component', description: 'Open the Digital Twin and select a component for inspection. Does not alter condition data.', inputSchema: { type: 'object', properties: { component_id: { type: 'string' } }, required: ['component_id'], additionalProperties: false }, annotations: { readOnlyHint: false, untrustedContentHint: false }, execute(input) { const store=useBridge.getState(); if(!input || Object.keys(input).some(k=>k!=='component_id'))throw new Error('Supply only component_id.'); const c=store.state?.components.find(c=>c.component_id===input.component_id); if(!c)throw new Error('Unknown component.'); store.select(c.component_id);store.navigate('twin');return {selected_component:c.component_id,page:'twin'}; } }
    ];
    entries.forEach(entry => { try { Promise.resolve(context.registerTool(entry,{signal:lifecycle.signal})).catch(()=>{}); } catch {} });
    return()=>lifecycle.abort();
  },[]);
}
