from test_api import client

def test_stale_maintenance_is_rejected(client):
    state=client.get('/api/bridge').json()
    plan=client.post('/api/maintenance/optimize',json={'budget':2500000,'horizon':3}).json()
    payload={'budget':2500000,'horizon':3,'action_ids':[a['id'] for a in plan['actions']]}
    run=client.post('/api/maintenance/simulate',json=payload).json()
    client.post('/api/simulate/future',json={'months':1})
    assert client.post('/api/maintenance/simulate',json={**payload,'apply':True,'expected_revision':run['revision']}).status_code==409
    assert client.post('/api/maintenance/simulate',json={**payload,'apply':True}).status_code==409

def test_import_profile_download(client):
    response=client.post('/api/data/upload',files={'file':('x.csv','bridge_id,component_id,timestamp,health_score\n X ,Y,2026-01-01,55')},data={'source':'REAL'})
    assert response.status_code==200
    result=response.json()
    assert result['profile']['health_mean']==55
    download=client.get('/api/datasets/'+result['id']+'/download')
    assert download.status_code==200 and 'X,Y,' in download.text
