import{j as e}from"./three-c9_KBiux.js";import{c as l,u as h,i as u}from"./index-BrGT4Wub.js";import{P as x}from"./play-DyLkcKTX.js";import{R as j}from"./BridgeScene-C-RjfyiF.js";/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const p=[["path",{d:"M12 6a2 2 0 0 1 3.414-1.414l6 6a2 2 0 0 1 0 2.828l-6 6A2 2 0 0 1 12 18z",key:"b19h5q"}],["path",{d:"M2 6a2 2 0 0 1 3.414-1.414l6 6a2 2 0 0 1 0 2.828l-6 6A2 2 0 0 1 2 18z",key:"h7h5ge"}]],b=l("fast-forward",p);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const y=[["rect",{x:"14",y:"3",width:"5",height:"18",rx:"1",key:"kaeet6"}],["rect",{x:"5",y:"3",width:"5",height:"18",rx:"1",key:"1wsw3u"}]],k=l("pause",y);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const N=[["path",{d:"M21 4v16",key:"7j8fe9"}],["path",{d:"M6.029 4.285A2 2 0 0 0 3 6v12a2 2 0 0 0 3.029 1.715l9.997-5.998a2 2 0 0 0 .003-3.432z",key:"zs4d6"}]],f=l("skip-forward",N);function P({full:n=!1}){const{state:t,playing:i,setPlaying:o,speed:r,setSpeed:c,tick:d,reset:m,busy:a}=h();return e.jsxs("div",{className:`timeline ${n?"timeline-full":""}`,children:[e.jsxs("div",{className:"timeline-controls",children:[e.jsx("button",{className:"play-button","aria-label":i?"Pause simulation":"Play simulation",onClick:()=>o(!i),disabled:a&&!i,children:i?e.jsx(k,{size:18}):e.jsx(x,{size:18})}),e.jsx("button",{className:"icon-button","aria-label":"Step forward one month",disabled:a||i,onClick:()=>d(1),children:e.jsx(f,{size:17})}),e.jsx("button",{className:"icon-button","aria-label":"Reset simulation to 2026",disabled:a,onClick:m,children:e.jsx(j,{size:16})})]}),e.jsxs("div",{className:"timeline-date",children:[e.jsx("span",{children:"SIMULATION CLOCK"}),e.jsx("b",{children:u(t)})]}),e.jsxs("div",{className:"timeline-track",children:[e.jsxs("div",{className:"timeline-line",children:[e.jsx("div",{style:{width:`${t.simulation.month/240*100}%`}}),e.jsx("i",{style:{left:`${t.simulation.month/240*100}%`}})]}),e.jsx("div",{className:"timeline-years",children:[2026,2030,2035,2040,2046].map(s=>e.jsx("span",{children:s},s))})]}),e.jsx("div",{className:"speed-control","aria-label":"Simulation speed",children:[1,5,10].map(s=>e.jsxs("button",{className:r===s?"active":"",onClick:()=>c(s),children:[s,"×"]},s))}),n&&e.jsxs("button",{className:"btn primary future-button",onClick:()=>{c(10),o(!0)},disabled:i||a,children:[e.jsx(b,{size:16}),"Play future"]})]})}export{b as F,P as T};
