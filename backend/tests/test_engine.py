from copy import deepcopy
import pytest
from app.simulation.engine import make_baseline,advance_component,advance_state,deterioration_rate,risk,aggregate
from app.ml.synthetic import generate
from app.ml.training import split_groups
from app.ml.predictor import Predictor

@pytest.mark.parametrize('health,expected',[(100,'Healthy'),(80,'Healthy'),(79.99,'Moderate'),(60,'Moderate'),(59.99,'High risk'),(40,'High risk'),(39.99,'Critical'),(0,'Critical')])
def test_risk_boundaries(health,expected): assert risk(health)==expected

def test_deterioration_load_and_maintenance_relationships():
    s=make_baseline(); c=s['components'][0]; env=s['environment']
    normal=advance_component(c,env,5)
    stressed=advance_component(c,{**env,'traffic_load':100,'heavy_vehicle_percentage':60,'maintenance_delay':6},5)
    protected=advance_component({**c,'last_maintenance_years':0,'protection':1},env,5)
    assert 0<=stressed['health_score']<normal['health_score']<protected['health_score']<=c['health_score']

def test_monthly_integrator_and_no_mutation():
    s=make_baseline(); before=deepcopy(s)
    next_state=advance_state(s,12)
    assert s==before
    assert next_state['simulation']['year']==2027
    assert aggregate(next_state['components'])['health_score']<aggregate(s['components'])['health_score']
    assert next_state['components'][0]['age']==pytest.approx(s['components'][0]['age']+1)

def test_generator_is_deterministic_and_has_relationships():
    a=generate(n_bridges=4,years=3,seed=42); b=generate(n_bridges=4,years=3,seed=42)
    assert a.equals(b)
    assert a.health_score.between(0,100).all()
    assert (a.target_health_1y<=a.health_score).all()
    assert set(a.data_source)=={'SYNTHETIC'}
    assert a.groupby(['bridge_id','component_id']).health_score.apply(lambda x:x.is_monotonic_decreasing).all()

def test_no_bridge_leakage_between_splits():
    df=generate(n_bridges=40,years=1)
    splits=split_groups(df)
    groups={k:set(df.iloc[v].bridge_id) for k,v in splits.items()}
    for a in groups:
        for b in groups:
            if a!=b: assert groups[a].isdisjoint(groups[b])

def test_prediction_starts_at_authoritative_state_and_is_bounded():
    s=make_baseline(); predictor=Predictor()
    f=predictor.forecast(s['components'],s['environment'],5)
    assert f['points'][0]['health_score']==aggregate(s['components'])['health_score']
    assert len(f['points'])==6
    for a,b in zip(f['points'],f['points'][1:]):
        assert b['health_score']<=a['health_score']
        assert 0<=b['lower']<=b['health_score']<=b['upper']<=100
    assert f['points'][1]['data_source']=='PREDICTION'
