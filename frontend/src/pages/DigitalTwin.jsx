import { Box, FastForward } from 'lucide-react';
import { useBridge } from '../store/bridgeStore';
import { PageTitle, Badge, Source } from '../components/common/UI';
import { num } from '../utils/format';
import BridgeScene from '../components/bridge/BridgeScene';
import Timeline from '../components/bridge/Timeline';
import Inspector from '../components/bridge/Inspector';
export default function DigitalTwin(){const {state,select,selectedId}=useBridge();return <><PageTitle eyebrow="INTERACTIVE STRUCTURAL WORKSPACE" title="The living bridge." description="Select a component to inspect its condition, history, and projected future."><Source>{state.metadata.data_source}</Source><Badge risk={state.summary.risk_level}/></PageTitle><div className="twin-workspace"><div className="twin-stage"><BridgeScene components={state.components}/><Timeline full/><div className="component-selector" aria-label="Bridge components">{state.components.map(c=><button key={c.component_id} className={selectedId===c.component_id?'active':''} onClick={()=>select(c.component_id)}><span>{c.name}</span><b>{num(c.health_score)}</b></button>)}</div></div><Inspector/></div><div className="twin-notes"><span><Box size={16}/>Geometry is illustrative; component IDs map directly to backend state.</span><span><FastForward size={16}/>Vehicles are visual context. The simulation clock controls deterioration.</span></div></>;}
