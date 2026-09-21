from itertools import product
import pytest
from app.optimization.planner import optimize,candidates,apply_actions
from app.simulation.engine import make_baseline
from app.ml.predictor import Predictor

def test_optimizer_matches_exhaustive_small_problem():
    cs=make_baseline()['components'][1:3]; budget=800000
    groups=[[None]+[a for a in candidates(cs) if a['component_id']==c['component_id']] for c in cs]
    possible=[[a for a in choice if a] for choice in product(*groups)]
    optimum=max(sum(a['objective_benefit'] for a in plan) for plan in possible if sum(a['cost'] for a in plan)<=budget)
    result=optimize(cs,budget)
    assert sum(a['objective_benefit'] for a in result['actions'])==pytest.approx(optimum)
    assert result['total_cost']<=budget
    assert len({a['component_id'] for a in result['actions']})==len(result['actions'])

def test_zero_budget_is_feasible_and_inspection_does_not_heal():
    s=make_baseline()
    assert optimize(s['components'],0)['total_cost']==0
    inspections=[a for a in candidates(s['components']) if a['name']=='Detailed inspection']
    assert apply_actions(s['components'],inspections)==s['components']

def test_repair_improves_future_condition():
    s=make_baseline(); p=Predictor(); plan=optimize(s['components'],2500000)
    fixed=apply_actions(s['components'],plan['actions'])
    no=p.forecast(s['components'],s['environment'],5)
    yes=p.forecast(fixed,s['environment'],5)
    assert yes['points'][-1]['health_score']>no['points'][-1]['health_score']
