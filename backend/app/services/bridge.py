from copy import deepcopy
from threading import RLock
from uuid import uuid4
from datetime import datetime, timezone
from app.simulation.engine import make_baseline, aggregate, advance_state, history_point, condition
from app.optimization.planner import candidates, optimize, summarize, apply_actions
from app.config import DISCLAIMER

class BridgeService:
    def __init__(self,repo,predictor):
        self.repo=repo; self.predictor=predictor; self.lock=RLock(); self.cache=None
        state,rev=repo.get_state()
        if state is None: repo.save_state(make_baseline(),0)

    def raw(self): return self.repo.get_state()

    def view(self):
        with self.lock:
            state,revision=self.raw()
            if self.cache and self.cache['revision']==revision: return deepcopy(self.cache)
            view=deepcopy(state)
            forecast=self.predictor.forecast(state['components'],state['environment_base'],5)
            anomalies=self.predictor.anomalies(state['components'],state['environment'])
            for c,a in zip(view['components'],anomalies):
                c['anomaly_status']=a['status']; c['anomaly_score']=a['score']
                for y in [1,3,5]: c[f'predicted_health_{y}y']=forecast['points'][y]['components'][c['component_id']]
                c['primary_risk_factors']=['Maintenance interval' if c['last_maintenance_years']>4 else 'Environmental exposure', 'Accumulated loading']
            view['summary']=aggregate(state['components'])
            view['summary'].update({f'predicted_health_{y}y':forecast['points'][y]['health_score'] for y in [1,3,5]})
            view['predictions']=forecast['points']
            view['revision']=revision
            view['metadata'].update({'disclaimer':DISCLAIMER,'model_status':self.predictor.card['status'],
                                     'forecast_method':forecast['method'],'anomaly_note':'Anomalies indicate unusual model inputs, not confirmed structural damage.'})
            view['recent_activity']=[{k:r.get(k) for k in ['id','name','created_at','kind','horizon','revision']} for r in self.repo.list('simulation_run',6)]
            self.cache=view
            return deepcopy(view)

    def save(self,state,revision):
        state['metadata']['updated_at']=datetime.now(timezone.utc).isoformat()
        self.repo.save_state(state,revision); self.cache=None
        return self.view()

    def tick(self,months):
        with self.lock:
            state,rev=self.raw()
            if state['simulation']['month']+months>240: raise ValueError('The demo timeline ends in 2046. Reset to start again.')
            state=advance_state(state,months)
            for c in state['components']: c['data_source']='SIMULATION'
            return self.save(state,rev)

    def reset(self):
        with self.lock:
            _,rev=self.raw()
            return self.save(make_baseline(),rev)

    def scenario(self,p):
        with self.lock:
            state,rev=self.raw()
            env=deepcopy(state['environment_base'])
            for key,change,cap in [('traffic_load',p.traffic_change,100),('heavy_vehicle_percentage',p.heavy_vehicle_change,100),('environmental_exposure',p.environmental_change,1)]:
                env[key]=min(cap,max(0,env[key]*(1+change/100)))
            env['temperature']+=p.temperature_change; env['maintenance_delay']+=p.maintenance_delay
            baseline=self.predictor.forecast(state['components'],state['environment_base'],p.horizon)
            scenario=self.predictor.forecast(state['components'],env,p.horizon)
            run={'id':str(uuid4()),'kind':'what-if','name':p.name,'revision':rev,'created_at':datetime.now(timezone.utc).isoformat(),
                 'horizon':p.horizon,'inputs':p.model_dump(),'effective_environment':env,
                 'baseline':baseline['points'],'scenario':scenario['points'], 'final_components':scenario['final_components'],
                 'difference':round(scenario['points'][-1]['health_score']-baseline['points'][-1]['health_score'],2),
                 'data_source':'SIMULATION','source_month':state['simulation']['month']}
            self.repo.put('simulation_run',run['id'],run); self.cache=None
            return run

    def apply_scenario(self,run_id):
        with self.lock:
            run=self.repo.get(run_id)
            if not run or run.get('kind')!='what-if': raise ValueError('Simulation run was not found.')
            state,rev=self.raw()
            if run['revision']!=rev: raise RuntimeError('The bridge state changed. Run the scenario again before applying it.')
            # Apply scenario operating inputs NOW; do not silently jump the clock by the forecast horizon.
            state['environment_base']=run['effective_environment']; state['environment']=run['effective_environment']
            state['simulation']['scenario']=run['name']; state['metadata']['data_source']='SIMULATION'
            return self.save(state,rev)

    def actions(self): return candidates(self.raw()[0]['components'])

    def optimize(self,p):
        state,rev=self.raw()
        result=optimize(state['components'],p.budget)
        result.update({'revision':rev,'horizon':p.horizon})
        return result

    def simulate_plan(self,p):
        with self.lock:
            state,rev=self.raw()
            lookup={a['id']:a for a in candidates(state['components'])}
            if len(set(p.action_ids))!=len(p.action_ids): raise ValueError('Duplicate maintenance actions are not allowed.')
            if any(i not in lookup for i in p.action_ids): raise ValueError('An action is not valid for the current bridge.')
            selected=[lookup[i] for i in p.action_ids]
            if len({a['component_id'] for a in selected})!=len(selected): raise ValueError('Select at most one action per component.')
            plan=summarize(state['components'],selected,p.budget)
            if not plan['within_budget']: raise ValueError('This plan exceeds the available budget.')
            repaired=apply_actions(state['components'],selected)
            no=self.predictor.forecast(state['components'],state['environment_base'],p.horizon)
            yes=self.predictor.forecast(repaired,state['environment_base'],p.horizon)
            run={'id':str(uuid4()),'kind':'maintenance','name':'Maintenance counterfactual','revision':rev,
                 'created_at':datetime.now(timezone.utc).isoformat(),'horizon':p.horizon,'plan':plan,
                 'baseline':no['points'],'maintenance':yes['points'],'data_source':'SIMULATION'}
            self.repo.put('simulation_run',run['id'],run); self.cache=None
            if p.apply:
                state['components']=repaired
                for a in selected:
                    state['maintenance_history'].append({'year':state['simulation']['year'],'component_id':a['component_id'],'action':a['name'],'cost':a['cost'],'data_source':'SIMULATION'})
                state['history'].append(history_point(state,'SIMULATION'))
                state['metadata']['data_source']='SIMULATION'
                run['state']=self.save(state,rev)
            return run
