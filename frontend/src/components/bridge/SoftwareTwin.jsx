/** A genuine Three.js scene projected by SVGRenderer when WebGL is unavailable.
 * Orbit, pan, zoom and component picking all operate in 3D; this is not an image.
 */
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { SVGRenderer } from 'three/addons/renderers/SVGRenderer.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { color, num } from '../../utils/format';

const centers={DECK_01:[0,5,0],PIER_01:[-11,2.5,0],PIER_02:[-4,2.5,0],PIER_03:[4,2.5,0],PIER_04:[11,2.5,0],BEARING_01:[4,4.3,0],JOINT_01:[-14.7,5,0],JOINT_02:[14.7,5,0]};
export function canRenderWebGL(){try{const canvas=document.createElement('canvas');const gl=canvas.getContext('webgl2');if(gl){gl.getExtension('WEBGL_lose_context')?.loseContext();return true;}return false;}catch{return false;}}

export default function SoftwareTwin({components,selectedId,onSelect,mode,command}){
  const host=useRef();const engine=useRef();const pick=useRef(onSelect);pick.current=onSelect;
  const [hover,setHover]=useState(null);const [label,setLabel]=useState(null);
  useEffect(()=>{
    const mount=host.current;if(!mount)return;
    const scene=new THREE.Scene();scene.background=new THREE.Color('#122330');
    const camera=new THREE.PerspectiveCamera(39,1,.1,200);const scale=Math.max(1,mount.clientHeight/Math.max(1,mount.clientWidth)*1.75);camera.position.set(21*scale,14*scale,25*scale);camera.lookAt(0,2,0);
    const renderer=new SVGRenderer();renderer.setQuality('high');renderer.setClearColor('#122330');
    renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label','Interactive 3D bridge. Drag to orbit; scroll to zoom; click a structural component.');
    renderer.domElement.style.touchAction='none';mount.appendChild(renderer.domElement);
    const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,2,0);controls.minDistance=7;controls.maxDistance=85;controls.maxPolarAngle=Math.PI/2-.04;controls.enableDamping=false;
    scene.add(new THREE.AmbientLight('#c9e8ef',.9));const sun=new THREE.DirectionalLight('#ffffff',1.5);sun.position.set(8,24,14);scene.add(sun);
    const back=new THREE.DirectionalLight('#8bd0e2',.8);back.position.set(-10,8,-14);scene.add(back);
    const meshes=[];const map=Object.fromEntries(components.map(c=>[c.component_id,c]));
    const materials=[];
    function box(pos,size,tint,id,condition=false){const material=new THREE.MeshLambertMaterial({color:tint});const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),material);mesh.position.set(...pos);scene.add(mesh);materials.push(material);if(id){mesh.userData.componentId=id;mesh.userData.base=tint;mesh.userData.condition=condition;meshes.push(mesh);}return mesh;}
    function line(points,tint,opacity=1){const geometry=new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p)));const material=new THREE.LineBasicMaterial({color:tint,transparent:opacity<1,opacity});scene.add(new THREE.Line(geometry,material));materials.push(material);}
    const tint=id=>mode==='structure'?'#9fb2bc':new THREE.Color('#77939c').lerp(new THREE.Color(color(map[id].risk_level)),.83).getStyle();
    // Ground, river, banks and a measured engineering grid.
    function surface(x,y,width,length,tint){const g=new THREE.PlaneGeometry(width,length,Math.ceil(width/3),Math.ceil(length/4));g.rotateX(-Math.PI/2);const m=new THREE.MeshBasicMaterial({color:tint});materials.push(m);const plane=new THREE.Mesh(g,m);plane.position.set(x,y,0);scene.add(plane);}
    surface(0,-.1,29,85,'#1b4659');
    [-22,22].forEach(x=>surface(x,.15,14,80,'#284441'));
    for(let i=-40;i<=40;i+=5){line([[-45,.245,i],[45,.245,i]],'#36515c',.38);line([[i,.245,-40],[i,.245,40]],'#36515c',.38);}
    for(let z=-35;z<=35;z+=4){line([[-13,.03,z],[13,.03,z+.7]],'#47788a',.5);}
    // Deck, road, beam members, markings, four piers, and bearings.
    box([0,4.6,0],[36,.58,4.5],tint('DECK_01'),'DECK_01',true);box([0,4.95,0],[36,.14,3.75],'#455260','DECK_01');
    [-1.7,0,1.7].forEach(z=>box([0,4.05,z],[35,.58,.23],tint('DECK_01'),'DECK_01',true));
    [-1.65,1.65].forEach(z=>box([0,5.035,z],[36,.025,.045],'#d1e0df','DECK_01'));
    for(let x=-17;x<=17;x+=1.5)box([x,5.04,0],[.72,.025,.06],'#dccf9c','DECK_01');
    [-11,-4,4,11].forEach((x,i)=>{const id=`PIER_0${i+1}`;box([x,2.1,0],[1.05,3.7,2.8],tint(id),id,true);box([x,3.9,0],[1.6,.4,4.1],tint(id),id,true);box([x,.25,0],[2.2,.6,3.5],'#697b86',id);[-1.5,0,1.5].forEach(z=>box([x,4.23,z],[.62,.25,.55],tint('BEARING_01'),'BEARING_01',true));});
    [-14.7,14.7].forEach((x,i)=>box([x,5.07,0],[.3,.07,4.45],tint(`JOINT_0${i+1}`),`JOINT_0${i+1}`,true));
    [-2.08,2.08].forEach(z=>{[5.4,5.68].forEach(y=>line([[-18,y,z],[18,y,z]],'#aabec9'));for(let x=-18;x<=18;x+=1)line([[x,5.02,z],[x,5.69,z]],'#9bb3c0');});
    [-17,17].forEach(x=>{box([x,2.25,0],[1.7,4.35,4.9],'#8899a2');box([x>0?20:-20,4.6,0],[4,.6,4.5],'#849997');box([x>0?20:-20,4.95,0],[4,.15,3.75],'#455260');});
    [-14,-7,0,7,14].forEach(x=>{line([[x,5,-2.02],[x,7.7,-2.02],[x,7.7,-1.5]],'#9bb4c1');box([x,7.67,-1.45],[.18,.06,.22],'#ecd39b');});
    [[-10,.85,'#d4b172'],[1,.85,'#d4dfe4'],[10,-.85,'#83aad1'],[-4,-.85,'#b5c9d3']].forEach(([x,z,c])=>{box([x,5.24,z],[1.1,.27,.48],c);box([x-.1,5.47,z],[.57,.22,.4],'#95acb9');});
    line([[-18,.6,5],[-18,.6,6],[18,.6,6],[18,.6,5]],'#6d96a7',.9);
    let active=selectedId;let over=null;
    const draw=()=>{renderer.render(scene,camera);const id=over||active;if(id&&centers[id]){const p=new THREE.Vector3(...centers[id]);p.y+=1.65;p.project(camera);setLabel(Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&p.z<1?{id,x:(p.x*.5+.5)*mount.clientWidth,y:(-p.y*.5+.5)*mount.clientHeight}:null);}else setLabel(null);};
    const highlight=()=>meshes.forEach(m=>m.material.color.set(m.userData.base).lerp(new THREE.Color('#ceffea'),m.userData.componentId===(over||active)?0.23:0));
    function select(id){active=id;highlight();draw();}
    function update(nextComponents,nextMode){const nextMap=Object.fromEntries(nextComponents.map(c=>[c.component_id,c]));meshes.forEach(m=>{if(m.userData.condition){const component=nextMap[m.userData.componentId];m.userData.base=nextMode==='structure'?'#9fb2bc':new THREE.Color('#77939c').lerp(new THREE.Color(color(component.risk_level)),.83).getStyle();}});highlight();draw();}
    const resize=()=>{const w=mount.clientWidth,h=mount.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);draw();};
    const observer=new ResizeObserver(resize);observer.observe(mount);controls.addEventListener('change',draw);
    const raycaster=new THREE.Raycaster();const pointer=new THREE.Vector2();let start={x:0,y:0};
    function hit(e){const rect=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(pointer,camera);return raycaster.intersectObjects(meshes,false)[0]?.object.userData.componentId;}
    const down=e=>{start={x:e.clientX,y:e.clientY};};
    const up=e=>{if(Math.hypot(e.clientX-start.x,e.clientY-start.y)<5){const id=hit(e);if(id)pick.current(id);}};
    const move=e=>{if(e.buttons)return;const id=hit(e);if(id!==over){over=id;setHover(id);mount.style.cursor=id?'pointer':'grab';highlight();draw();}};
    const leave=()=>{over=null;setHover(null);highlight();draw();};
    renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerleave',leave);
    engine.current={camera,controls,draw,select,update};controls.update();select(selectedId);resize();
    return()=>{observer.disconnect();controls.removeEventListener('change',draw);controls.dispose();renderer.domElement.removeEventListener('pointerdown',down);renderer.domElement.removeEventListener('pointerup',up);renderer.domElement.removeEventListener('pointermove',move);renderer.domElement.removeEventListener('pointerleave',leave);renderer.domElement.remove();scene.traverse(o=>{o.geometry?.dispose();});materials.forEach(m=>m.dispose());engine.current=null;};
  },[]);
  useEffect(()=>{engine.current?.update(components,mode);},[components,mode]);
  useEffect(()=>{engine.current?.select(selectedId);},[selectedId]);
  useEffect(()=>{const e=engine.current;if(!e)return;const scale=Math.max(1,host.current.clientHeight/host.current.clientWidth*1.75);let p=[21*scale,14*scale,25*scale],t=[0,2,0];if(command.type==='top'){p=[0,44,.1];t=[0,0,0];}if(command.type==='side'){p=[0,9,44];t=[0,3,0];}if(command.type==='focus'){t=centers[selectedId]||[0,2,0];p=[t[0]+10,t[1]+8,t[2]+14];}e.camera.position.set(...p);e.controls.target.set(...t);e.controls.update();e.draw();},[command,selectedId]);
  const c=components.find(c=>c.component_id===(hover||selectedId));
  return <div ref={host} className="software-twin">{label&&c&&<div className="software-label mesh-label" style={{left:label.x,top:label.y}}><span>{c.name}</span><b style={{color:color(c.risk_level)}}>{num(c.health_score)} <small>/100</small></b><em>{c.risk_level}</em></div>}<span className="compatibility-mode">Interactive 3D · compatibility mode</span></div>;
}
