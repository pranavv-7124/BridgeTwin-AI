import { Play, Pause, SkipForward, RotateCcw, FastForward } from 'lucide-react';
import { useBridge } from '../../store/bridgeStore';
import { dateLabel } from '../../utils/format';
export default function Timeline({ full = false }) {
  const { state, playing, setPlaying, speed, setSpeed, tick, reset, busy }=useBridge();
  return <div className={`timeline ${full?'timeline-full':''}`}>
    <div className="timeline-controls"><button className="play-button" aria-label={playing?'Pause simulation':'Play simulation'} onClick={()=>setPlaying(!playing)} disabled={busy&&!playing}>{playing?<Pause size={18}/>:<Play size={18}/>}</button><button className="icon-button" aria-label="Step forward one month" disabled={busy||playing} onClick={()=>tick(1)}><SkipForward size={17}/></button><button className="icon-button" aria-label="Reset simulation to 2026" disabled={busy} onClick={reset}><RotateCcw size={16}/></button></div>
    <div className="timeline-date"><span>SIMULATION CLOCK</span><b>{dateLabel(state)}</b></div>
    <div className="timeline-track"><div className="timeline-line"><div style={{width:`${state.simulation.month/240*100}%`}}/><i style={{left:`${state.simulation.month/240*100}%`}}/></div><div className="timeline-years">{[2026,2030,2035,2040,2046].map(y=><span key={y}>{y}</span>)}</div></div>
    <div className="speed-control" aria-label="Simulation speed">{[1,5,10].map(n=><button className={speed===n?'active':''} onClick={()=>setSpeed(n)} key={n}>{n}×</button>)}</div>
    {full && <button className="btn primary future-button" onClick={()=>{setSpeed(10);setPlaying(true);}} disabled={playing||busy}><FastForward size={16}/>Play future</button>}
  </div>;
}
