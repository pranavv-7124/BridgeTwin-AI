from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture()
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(settings,'database_url',f'sqlite:///{tmp_path / "test.db"}')
    monkeypatch.setattr(settings,'auto_train',False)
    with TestClient(app) as c: yield c

def test_read_endpoints_and_synchronized_component(client):
    s=client.get('/api/bridge').json(); c=client.get('/api/components/PIER_02').json()
    assert c['health_score']==next(x for x in s['components'] if x['component_id']=='PIER_02')['health_score']
    for route in ['/api/health','/api/analytics','/api/datasets','/api/model-info','/api/report','/api/history/PIER_02','/api/predictions/PIER_02','/api/explanations/PIER_02']:
        assert client.get(route).status_code==200
    assert client.get('/api/components/UNKNOWN').status_code==404

def test_scenario_comparison_does_not_overwrite_source_and_apply_is_consistent(client):
    before=client.get('/api/bridge').json()
    r=client.post('/api/simulate',json={'traffic_change':30,'heavy_vehicle_change':20,'horizon':5}).json()
    after=client.get('/api/bridge').json()
    assert before['components']==after['components']
    assert r['scenario'][-1]['health_score']<r['baseline'][-1]['health_score']
    applied=client.post('/api/simulate/apply',json={'run_id':r['id']}).json()
    assert applied['environment']['traffic_load']==pytest.approx(before['environment']['traffic_load']*1.3)
    assert applied['summary']['health_score']==before['summary']['health_score']
    assert applied['summary']['predicted_health_5y']<before['summary']['predicted_health_5y']
    assert client.post('/api/simulate/apply',json={'run_id':r['id']}).status_code==409
    reset=client.post('/api/simulate/reset').json()
    assert reset['summary']['health_score']==before['summary']['health_score']

def test_invalid_input_and_duplicate_plan(client):
    assert client.post('/api/simulate',json={'traffic_change':1000}).status_code==422
    assert client.post('/api/simulate/future',json={'months':-2}).status_code==422
    assert client.post('/api/maintenance/optimize',json={'budget':-1}).status_code==422
    assert client.post('/api/maintenance/simulate',json={'action_ids':['PIER_01:1','PIER_01:2']}).status_code==422
    assert client.post('/api/maintenance/simulate',json={'budget':0,'action_ids':['PIER_01:2']}).status_code==422

def test_real_import_does_not_enter_training_or_simulation(client):
    content='bridge_id,component_id,timestamp,health_score\nREAL-TEST,DECK,2026-01-01,71\n'
    before=client.get('/api/bridge').json()
    response=client.post('/api/data/upload',files={'file':('observations.csv',content,'text/csv')},data={'source':'REAL'})
    assert response.status_code==200
    result=response.json()
    assert result['source']=='REAL' and result['record_count']==1
    assert not result['training_eligible'] and result['training_usage'].startswith('Not used')
    assert client.get('/api/bridge').json()['components']==before['components']
    assert client.get('/api/model-info').json()['real_records']==0

@pytest.mark.parametrize('name,content',[
    ('bad.exe','anything'),('bad.csv','foo,bar\n1,2'),
    ('bad.csv','bridge_id,component_id,timestamp,health_score\nX,Y,invalid,50'),
    ('bad.csv','bridge_id,component_id,timestamp,health_score\nX,Y,2026-01-01,500'),
    ('bad.csv','bridge_id,component_id,timestamp,health_score\nX,Y,2026-01-01,inf'),
    ('bad.csv','bridge_id,component_id,timestamp,health_score\nX,Y,2026-01-01,50\nX,Y,2026-01-01,60'),
])
def test_invalid_csv(client,name,content):
    assert client.post('/api/data/upload',files={'file':(name,content)},data={'source':'REAL'}).status_code==422

def test_plan_api_and_persisted_state(client):
    plan=client.post('/api/maintenance/optimize',json={'budget':2500000}).json()
    payload={'budget':2500000,'action_ids':[a['id'] for a in plan['actions']]}
    run=client.post('/api/maintenance/simulate',json=payload).json()
    assert run['maintenance'][-1]['health_score']>run['baseline'][-1]['health_score']
    result=client.post('/api/maintenance/simulate',json={**payload,'apply':True}).json()
    assert result['state']['summary']['health_score']>run['baseline'][0]['health_score']
    assert client.get('/api/bridge').json()['revision']==result['state']['revision']
