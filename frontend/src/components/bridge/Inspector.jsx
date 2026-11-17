import { useState, useEffect } from 'react';
import { ScanLine, ArrowUpRight, BrainCircuit } from 'lucide-react';
import { useBridge } from '../../store/bridgeStore';
import { api } from '../../services/api';
import { num, titleCase, color } from '../../utils/format';
import { Badge, Source, Note, Button } from '../common/UI';
import { TrendChart } from '../charts/Charts';

export default function Inspector() {
  const {state,selectedId,select,navigate}=useBridge();
  const [tab,setTab]=useState('Overview'); const [explanation,setExplanation]=useState(null); const [error,setError]=useState('');
  const c=state.components.find(c=>c.component_id===selectedId)||state.components[0];
  useEffect(()=>{ let active=true; setExplanation(null); setError(''); if(tab==='Risk factors') api(`/explanations/${c.component_id}`).then(x=>{if(active)setExplanation(x);}).catch(e=>{if(active)setError(e.message);}); return()=>{active=false;}; },[c.component_id,state.revision,tab]);
  const history=state.history.map(h=>({year:h.year,health_score:h.components[c.component_id]}));
  return <aside className="inspector panel"><div className="inspector-top"><span className="eyebrow"><ScanLine size={15}/> COMPONENT INSPECTOR</span><Source>{state.metadata.data_source}</Source></div>
    <label className="sr-only" htmlFor="component-select">Inspect a component</label><select id="component-select" className="component-select" value={c.component_id} onChange={e=>select(e.target.value)}>{state.components.map(c=><option key={c.component_id} value={c.component_id}>{c.name}</option>)}</select><p className="component-id">{c.component_id} <span>·</span> {titleCase(c.type)}</p>
    <div className="inspector-score"><div><b>{num(c.health_score)}</b><span>/ 100</span></div><Badge risk={c.risk_level}/></div><div className="score-track"><i style={{width:`${c.health_score}%`,background:color(c.risk_level)}}/></div>
    <div className="inspector-tabs" role="tablist">{['Overview','History','Prediction','Risk factors','Maintenance'].map(t=><button key={t} role="tab" aria-selected={tab===t} className={tab===t?'active':''} onClick={()=>setTab(t)}>{t}</button>)}</div>
    <div className="inspector-body">
      {tab==='Overview' && <><dl className="detail-grid"><div><dt>Component age</dt><dd>{num(c.age)} <small>years</small></dd></div><div><dt>Deterioration</dt><dd>{num(c.deterioration_index*100)}<small>%</small></dd></div><div><dt>Last maintenance</dt><dd>{num(c.last_maintenance_years)} <small>years ago</small></dd></div><div><dt>Anomaly status</dt><dd className="small-value">{c.anomaly_status}</dd></div></dl><div className="inspector-subheading">MODEL FORECAST</div><div className="mini-forecasts">{[1,3,5].map(y=><div key={y}><span>{y} year{y>1?'s':''}</span><b>{num(c[`predicted_health_${y}y`])}</b></div>)}</div><button className="explain-button" onClick={()=>setTab('Risk factors')}><BrainCircuit size={16}/>Why this prediction?<ArrowUpRight size={15}/></button><Note>Health is a condition proxy. Anomalies flag unusual inputs, not confirmed damage.</Note></>}
      {tab==='History' && <><p className="muted">Synthetic commissioning history and subsequent simulation.</p><TrendChart data={history} height={205}/><div className="mini-list">{state.maintenance_history.filter(h=>h.component_id===c.component_id).map((h,i)=><p key={i}>{h.year.toFixed(0)} · {h.action} <Source>{h.data_source}</Source></p>)}</div></>}
      {tab==='Prediction' && <><TrendChart data={state.predictions.map(p=>({horizon:p.horizon,health_score:p.components[c.component_id]}))} xKey="horizon" height={220}/><Note>Years from the active state. Estimated under unchanged operating inputs and no new maintenance.</Note></>}
      {tab==='Risk factors' && <>{error?<p className="field-error">{error}</p>:!explanation?<p>Calculating explanation…</p>:<><h4>Reference sensitivity</h4><p className="muted small">Change in 1-year health when one input is reset to its training median.</p>{explanation.sensitivities.map(s=><div className="sensitivity" key={s.feature}><span>{titleCase(s.feature)}</span><b>{s.health_point_change>0?'+':''}{num(s.health_point_change,3)} pts</b></div>)}<Note>{explanation.note}</Note>{explanation.out_of_range_features.length>0&&<p className="field-error">Outside training range: {explanation.out_of_range_features.map(titleCase).join(', ')}</p>}<h4>Global model importance</h4>{explanation.global_importance.slice(0,5).map(f=><div className="importance-row" key={f.feature}><span>{titleCase(f.feature)}</span><b>{num(f.importance,3)}</b><div style={{width:`${f.importance*100}%`}}/></div>)}<p className="muted small">Model-wide impurity importance; not local causal contributions.</p></>}</>}
      {tab==='Maintenance' && <><h4>{c.maintenance_status}</h4><p className="muted">Compare suitable interventions, their assumed costs, and their modeled benefits in the planner.</p><Button variant="primary" icon={ArrowUpRight} onClick={()=>navigate('maintenance')}>Open maintenance planner</Button><Note>Detailed inspection has no assumed health gain. Repairs restore a limited amount of condition and add temporary protection.</Note></>}
    </div>
  </aside>;
}
