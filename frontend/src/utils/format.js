export const num = (n, digits = 1) => Number.isFinite(Number(n)) && n !== null ? Number(n).toFixed(digits) : '—';
export const money = (n) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n || 0);
export const compactMoney = (n) => n >= 100000 ? `₹${num(n / 100000, 1)}L` : money(n);
export const color = (risk) => ({ Healthy: '#36b991', Moderate: '#daa741', 'High risk': '#ea8950', Critical: '#e2606c' }[risk] || '#879bae');
export const riskOf = (h) => h >= 80 ? 'Healthy' : h >= 60 ? 'Moderate' : h >= 40 ? 'High risk' : 'Critical';
export const titleCase = (text) => text.replaceAll('_', ' ').replace(/\b\w/g, x => x.toUpperCase());
export const dateLabel = (state) => new Date(Date.UTC(2026, state.simulation.month, 1)).toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
