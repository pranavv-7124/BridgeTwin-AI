"""Run from the project root: python scripts/research_experiment.py."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.simulation.engine import make_baseline,aggregate
from app.ml.predictor import Predictor
from app.optimization.planner import optimize,apply_actions,horizon_candidates
root=Path(__file__).resolve().parents[1]
out=root/'research';out.mkdir(exist_ok=True)
s=make_baseline();p=Predictor();records=[]
for budget in [0,500000,1000000,2500000,5000000]:
 for horizon in [1,5,10]:
  start=time.perf_counter();plan=optimize(s['components'],budget,p,s['environment_base'],horizon)
  legacy=optimize(s['components'],budget)
  catalog={a['id']:a for a in horizon_candidates(s['components'],p,s['environment_base'],horizon)}
  old_objective=sum(catalog[a['id']]['objective_benefit'] for a in legacy['actions'])
  fixed=apply_actions(s['components'],plan['actions'])
  records.append({'budget':budget,'horizon':horizon,'cost':plan['total_cost'],'actions':[a['id'] for a in plan['actions']],
                  'objective':plan.get('objective_value',0),'legacy_plan_evaluated_on_same_objective':old_objective,
                  'future_no_repair':p.forecast(s['components'],s['environment_base'],horizon)['points'][-1]['health_score'],
                  'future_repair':p.forecast(fixed,s['environment_base'],horizon)['points'][-1]['health_score'],
                  'elapsed_seconds':time.perf_counter()-start})
result={'model_card':p.card,'initial_health':aggregate(s['components'])['health_score'],'planning_experiments':records,
        'scope':'Deterministic fictional bridge and synthetic data only; timing includes both optimizers and evaluation.'}
(out/'experiment_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='model_card'},indent=2))
