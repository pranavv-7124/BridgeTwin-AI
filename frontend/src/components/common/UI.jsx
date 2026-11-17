import { ArrowUpRight, LoaderCircle, Info, X } from 'lucide-react';
import { color, num } from '../../utils/format';

export function Badge({ risk, children, className = '' }) { return <span className={`badge ${className}`} style={risk ? { color: color(risk), background: `${color(risk)}13` } : {}}>{risk && <span className="square" style={{ background: color(risk) }} />}{children || risk}</span>; }
export function Source({ children }) { return <span className={`source source-${String(children).toLowerCase()}`}>{children}</span>; }
export function Button({ children, icon: Icon, variant = '', loading, ...props }) { return <button className={`btn ${variant}`} {...props}>{loading ? <LoaderCircle size={16} className="spin" /> : Icon && <Icon size={16} />}{children}</button>; }
export function Panel({ title, eyebrow, action, children, className = '' }) { return <section className={`panel ${className}`}><div className="panel-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h3>{title}</h3></div>{action}</div>{children}</section>; }
export function PageTitle({ eyebrow = 'INFRASTRUCTURE INTELLIGENCE', title, description, children }) { return <div className="page-title"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description && <p>{description}</p>}</div><div className="page-actions">{children}</div></div>; }
export function Metric({ label, value, unit, note, icon: Icon, accent = false, children }) { return <div className={`metric ${accent ? 'metric-accent' : ''}`}><div className="metric-label">{label}{Icon && <Icon size={17} />}</div><div className="metric-value">{value}<span>{unit}</span></div><div className="metric-note">{note}{children}</div></div>; }
export function HealthBar({ value, risk, label, onClick }) { const inner = <><span className="healthbar-label">{label}</span><div className="bar-track"><div style={{ width: `${value}%`, background: color(risk) }} /></div><b>{num(value)}</b></>; return onClick ? <button className="healthbar" onClick={onClick}>{inner}</button> : <div className="healthbar">{inner}</div>; }
export function Note({ children }) { return <div className="note"><Info size={16} /><span>{children}</span></div>; }
export function LinkButton({ children, onClick }) { return <button className="text-button" onClick={onClick}>{children}<ArrowUpRight size={15} /></button>; }
export function Empty({ title, children }) { return <div className="empty"><Info size={26} /><h3>{title}</h3><p>{children}</p></div>; }
export function ErrorNotice({ text, onClose }) { return <div className="error-notice" role="alert"><Info size={18}/><span>{text}</span><button aria-label="Dismiss error" onClick={onClose}><X size={18}/></button></div>; }
