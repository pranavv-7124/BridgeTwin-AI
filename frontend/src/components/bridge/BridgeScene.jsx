import React, { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Grid, Html, Line, Edges } from '@react-three/drei';
import { Color, Vector3 } from 'three';
import { Maximize2, RotateCcw, Focus, Layers3, Box, Move, AlertTriangle } from 'lucide-react';
import { useBridge } from '../../store/bridgeStore';
import { color, num } from '../../utils/format';
import SoftwareTwin, { canRenderWebGL } from './SoftwareTwin';

const POSITIONS = { DECK_01: [0, 4.8, 0], PIER_01: [-11,2.2,0], PIER_02: [-4,2.2,0], PIER_03: [4,2.2,0], PIER_04: [11,2.2,0], BEARING_01: [4,4.15,0], JOINT_01: [-14.7,4.8,0], JOINT_02: [14.7,4.8,0] };

class SceneBoundary extends React.Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}

function BoxMesh({ position, size, tint = '#647587', ...props }) { return <mesh position={position} castShadow receiveShadow {...props}><boxGeometry args={size}/><meshStandardMaterial color={tint} roughness={.68} metalness={.12}/></mesh>; }

function ComponentPart({ data, selected, onSelect, mode, children }) {
  const [hover, setHover] = useState(false);
  const tint = useMemo(() => mode === 'structure' ? '#abb8c5' : new Color('#72868c').lerp(new Color(color(data.risk_level)), .78).getStyle(), [data.risk_level, mode]);
  return <group onClick={e => { e.stopPropagation(); onSelect(data.component_id); }} onPointerOver={e => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; }} onPointerOut={() => { setHover(false); document.body.style.cursor = ''; }}>
    {children(tint, selected || hover)}
    {(hover || selected) && <Html position={[...POSITIONS[data.component_id].slice(0,1), POSITIONS[data.component_id][1] + 1.7, 0]} center distanceFactor={34} zIndexRange={[40,0]} style={{ pointerEvents: 'none' }}><div className="mesh-label"><span>{data.name}</span><b style={{ color: color(data.risk_level) }}>{num(data.health_score)} <small>/ 100</small></b><em>{data.risk_level}</em></div></Html>}
  </group>;
}
function StructuralBox({ position, size, tint, active }) { return <mesh position={position} castShadow receiveShadow><boxGeometry args={size}/><meshStandardMaterial color={tint} emissive={active ? '#67edda' : '#000'} emissiveIntensity={active ? .16 : 0} roughness={.6} metalness={.22}/>{active && <Edges color="#c3fff2"/>}</mesh>; }

function Vehicle({ offset, lane, speed, truck = false, tint }) {
  const ref = useRef();
  useFrame(({ clock }) => { if (ref.current) ref.current.position.x = ((clock.elapsedTime * speed + offset + 18) % 36) - 18; });
  return <group ref={ref} position={[offset,5.11,lane]} rotation={[0,speed<0 ? Math.PI : 0,0]}>
    <BoxMesh position={[0,.18,0]} size={[truck?1.65:.92,.3,.46]} tint={tint}/>
    <BoxMesh position={[truck?-.2:-.07,.43,0]} size={[truck?1.04:.48,truck?.42:.25,.41]} tint={truck?'#d5dce3':'#879fac'}/>
    {[-.28,.28].map(x => [-.24,.24].map(z => <mesh key={`${x}${z}`} position={[x,.06,z]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.11,.11,.065,8]}/><meshStandardMaterial color="#172530"/></mesh>))}
  </group>;
}

function BridgeModel({ components, selectedId, onSelect, mode }) {
  const map = Object.fromEntries(components.map(c => [c.component_id,c]));
  const Part = ({ id, children }) => <ComponentPart data={map[id]} selected={id===selectedId} onSelect={onSelect} mode={mode}>{children}</ComponentPart>;
  return <group>
    <Part id="DECK_01">{(t,a) => <group><StructuralBox position={[0,4.6,0]} size={[36,.58,4.5]} tint={t} active={a}/><BoxMesh position={[0,4.95,0]} size={[36,.14,3.75]} tint="#3e4b58"/>{[-1.65,1.65].map(z => <BoxMesh key={z} position={[0,5.07,z]} size={[36,.035,.045]} tint="#d4e2df"/>)}{Array.from({length:24},(_,i) => <BoxMesh key={i} position={[-17+i*1.5,5.07,0]} size={[.72,.035,.055]} tint="#e1d7b6"/>)}{[-1.7,0,1.7].map(z => <BoxMesh key={z} position={[0,4.05,z]} size={[35,.6,.22]} tint={t}/>)}</group>}</Part>
    {[-11,-4,4,11].map((x,i) => <Part key={i} id={`PIER_0${i+1}`}>{(t,a) => <group><StructuralBox position={[x,2.1,0]} size={[1.05,3.7,2.8]} tint={t} active={a}/><StructuralBox position={[x,3.9,0]} size={[1.6,.4,4.1]} tint={t} active={a}/><BoxMesh position={[x,.28,0]} size={[2.2,.65,3.5]} tint="#526879"/></group>}</Part>)}
    <Part id="BEARING_01">{(t,a) => <group>{[-11,-4,4,11].map(x => [-1.5,0,1.5].map(z => <StructuralBox key={`${x}${z}`} position={[x,4.23,z]} size={[.62,.25,.55]} tint={t} active={a}/>))}</group>}</Part>
    {[-14.7,14.7].map((x,i) => <Part key={i} id={`JOINT_0${i+1}`}>{(t,a) => <StructuralBox position={[x,5.065,0]} size={[.28,.075,4.42]} tint={t} active={a}/>}</Part>)}
    {[-2.08,2.08].map(z => <group key={z}>
      {[5.4,5.68].map(y => <BoxMesh key={y} position={[0,y,z]} size={[36,.055,.055]} tint="#b0c1ce"/>)}
      {Array.from({length:37},(_,i) => <BoxMesh key={i} position={[-18+i,5.34,z]} size={[.045,.66,.045]} tint="#8ba6b7"/>)}
    </group>)}
    {[-17,17].map(x => <group key={x}><BoxMesh position={[x,2.25,0]} size={[1.7,4.35,4.9]} tint="#7e8e99"/><BoxMesh position={[x>0?20:-20,4.55,0]} size={[4,.6,4.5]} tint="#738c94"/><BoxMesh position={[x>0?20:-20,4.9,0]} size={[4,.15,3.75]} tint="#3e4b58"/></group>)}
    {[-14,-7,0,7,14].map(x => <group key={x}><BoxMesh position={[x,6.42,-2.02]} size={[.055,2.65,.055]} tint="#8299ad"/><BoxMesh position={[x,7.72,-1.72]} size={[.055,.045,.64]} tint="#8eabba"/><mesh position={[x,7.69,-1.44]}><boxGeometry args={[.16,.07,.23]}/><meshStandardMaterial color="#ffe0a0" emissive="#ffe0a0" emissiveIntensity={1}/></mesh></group>)}
    <Vehicle offset={0} lane={.85} speed={1.3} tint="#e2c27e"/><Vehicle offset={15} lane={.85} speed={1.1} tint="#c0d5dc" truck/><Vehicle offset={20} lane={-.85} speed={1.6} tint="#819bdc"/><Vehicle offset={-10} lane={-.85} speed={1.4} tint="#c9dbdf"/>
  </group>;
}
function Environment() {
  return <group><mesh rotation={[-Math.PI/2,0,0]} position={[0,-.15,0]} receiveShadow><planeGeometry args={[140,120]}/><meshStandardMaterial color="#162a39" roughness={.9}/></mesh>
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,.08,0]} receiveShadow><planeGeometry args={[30,90]}/><meshStandardMaterial color="#174c60" roughness={.28} metalness={.55} transparent opacity={.9}/></mesh>
    {[-21,21].map(x => <BoxMesh key={x} position={[x,.12,0]} size={[12,.45,85]} tint="#253e44"/>)}
    {Array.from({length:16},(_,i) => <Line key={i} points={[[-14,.12,-35+i*4.5],[14,.12,-34+i*4.5]]} color="#317183" lineWidth={.65} transparent opacity={.35}/>)}
    <Grid position={[0,-.02,0]} args={[110,100]} cellSize={2} cellThickness={.4} cellColor="#466079" sectionSize={10} sectionThickness={.6} sectionColor="#456274" fadeDistance={90} fadeStrength={1}/>
    <Line points={[[-18,.65,5],[-18,.65,6],[18,.65,6],[18,.65,5]]} color="#5c8293" lineWidth={1} dashed dashSize={.4} gapSize={.3}/>
    <Html position={[0,.6,6]} center distanceFactor={40} zIndexRange={[10,0]}><div className="dimension-label">180 m / 5 spans</div></Html>
  </group>;
}
function CameraRig({ command, selectedId }) {
  const controls=useRef(); const {camera,size}=useThree(); const destination=useRef(null); const target=useRef(new Vector3(0,2,0));
  useEffect(() => {
    const scale=Math.max(1,size.height/size.width*1.75); let pos=[21*scale,14*scale,25*scale], look=[0,2,0];
    if (command.type==='top') { pos=[0,44,.1]; look=[0,0,0]; }
    if (command.type==='side') { pos=[0,9,44]; look=[0,3,0]; }
    if (command.type==='focus') { look=POSITIONS[selectedId]||[0,3,0]; pos=[look[0]+10,look[1]+8,look[2]+14]; }
    destination.current=new Vector3(...pos); target.current=new Vector3(...look);
  },[command,selectedId]);
  useFrame((_,dt) => { if (destination.current && controls.current) { const a=1-Math.exp(-5*dt); camera.position.lerp(destination.current,a); controls.current.target.lerp(target.current,a); controls.current.update(); if(camera.position.distanceTo(destination.current)<.02) destination.current=null; } });
  return <OrbitControls ref={controls} makeDefault minDistance={7} maxDistance={75} maxPolarAngle={Math.PI/2-.03} onStart={() => {destination.current=null;}} enableDamping dampingFactor={.08}/>;
}

export default function BridgeScene({ components, compact = false, label = 'CURRENT SIMULATED STATE', selected: overrideSelected, onSelect: overrideSelect }) {
  const selectedId=useBridge(s=>s.selectedId), select=useBridge(s=>s.select), navigate=useBridge(s=>s.navigate);
  const [mode,setMode]=useState('condition'); const [command,setCommand]=useState({type:'perspective',nonce:0});
  const [webgl,setWebgl]=useState(canRenderWebGL);
  const commandView=(type)=>setCommand({type,nonce:Date.now()});
  const choose=(id)=>{(overrideSelect||select)(id); if(!compact) commandView('focus');};
  return <div className={`bridge-scene ${compact?'compact':''}`}>
    <div className="scene-heading"><div><span className="scene-live">{label}</span><p>BT-PUNE-001 <span>/</span> Mula River Bridge</p></div><div className="scene-modes"><button className={mode==='condition'?'active':''} onClick={()=>setMode('condition')} title="Condition colors" aria-label="Condition colors"><Layers3 size={16}/></button><button className={mode==='structure'?'active':''} onClick={()=>setMode('structure')} title="Structural materials" aria-label="Structural materials"><Box size={16}/></button>{compact && <button aria-label="Open Digital Twin" onClick={()=>navigate('twin')}><Maximize2 size={16}/></button>}</div></div>
    {!webgl ? <SoftwareTwin components={components} selectedId={overrideSelected??selectedId} onSelect={choose} mode={mode} command={command}/> : <SceneBoundary fallback={<SoftwareTwin components={components} selectedId={overrideSelected??selectedId} onSelect={choose} mode={mode} command={command}/>}><Suspense fallback={<div className="scene-fallback">Preparing 3D workspace…</div>}><Canvas shadows dpr={[1,1.5]} camera={{position:[28,22,31],fov:39,near:.1,far:200}} gl={{antialias:true,alpha:false}} onCreated={({gl})=>{gl.setClearColor('#122330');gl.domElement.addEventListener('webglcontextlost',()=>setWebgl(false),{once:true});}}>
      <fog attach="fog" args={['#122330',65,130]}/><ambientLight intensity={1.15}/><hemisphereLight args={['#c4efff','#3a5662',1.5]}/><directionalLight position={[10,30,15]} intensity={2.4} castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-35} shadow-camera-right={35} shadow-camera-top={25} shadow-camera-bottom={-25} shadow-bias={-.0008}/><directionalLight position={[-20,12,-15]} color="#72bad4" intensity={1.2}/>
      <Environment/><BridgeModel components={components} selectedId={overrideSelected??selectedId} onSelect={choose} mode={mode}/><CameraRig command={command} selectedId={overrideSelected??selectedId}/>
    </Canvas></Suspense></SceneBoundary>}
    <div className="scene-bottom"><div className="scene-legend">{['Healthy','Moderate','High risk','Critical'].map(r=><span key={r}><i style={{background:color(r)}}/>{r}</span>)}</div><span className="scene-orbit"><Move size={13}/> Drag to orbit · Scroll to zoom</span></div>
    {!compact && <div className="camera-controls"><button onClick={()=>commandView('perspective')}><RotateCcw size={14}/> Reset</button><button onClick={()=>commandView('top')}>Top</button><button onClick={()=>commandView('side')}>Side</button><button onClick={()=>commandView('focus')}><Focus size={14}/> Focus</button></div>}
    <div className="compass"><span>N</span><i/>E</div>
  </div>;
}
