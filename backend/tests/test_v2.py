from itertools import product
import pytest
from app.simulation.engine import make_baseline
from app.optimization.planner import optimize,horizon_candidates
from app.ml.predictor import Predictor
from app.services.datasets import inspect_csv

def test_horizon_optimizer_matches_exhaustive():
    s=make_baseline();cs=s['components'][1:3];p=Predictor();budget=800000
    options=horizon_candidates(cs,p,s['environment_base'],5)
    groups=[[None]+[a for a in options if a['component_id']==c['component_id']] for c in cs]
    best=max(sum(a['objective_benefit'] for a in plan if a) for plan in product(*groups) if sum(a['cost'] for a in plan if a)<=budget)
    result=optimize(cs,budget,p,s['environment_base'],5)
    assert result['objective_value']==pytest.approx(best)
    assert result['within_budget']
    short=optimize(cs,budget,p,s['environment_base'],1)
    assert short['objective_value']!=pytest.approx(result['objective_value'])

@pytest.mark.parametrize('body',[
 'X,Y,2026-01-01,50\n X ,Y,2026-01-01T00:00:00Z,60',
 ' ,Y,2026-01-01,50',
])
def test_normalized_import_identifiers(body):
    with pytest.raises(ValueError):inspect_csv(('bridge_id,component_id,timestamp,health_score\n'+body).encode(),'x.csv','REAL')

def test_import_profile_and_fractional_type_rejected():
    _,info=inspect_csv(b'bridge_id,component_id,timestamp,health_score\nX,Y,2026-01-01,55','x.csv','REAL')
    assert info['profile']['condition_counts']['High risk']==1
    with pytest.raises(ValueError):inspect_csv(b'bridge_id,component_id,timestamp,health_score,type_code\nX,Y,2026-01-01,55,1.5','x.csv','REAL')
