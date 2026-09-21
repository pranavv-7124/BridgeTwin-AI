import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings, MODEL_PATH, ROOT, FEATURES, DISCLAIMER
from app.database.repository import Repository
from app.ml.training import train
from app.ml.predictor import Predictor
from app.services.bridge import BridgeService
from app.services.datasets import inspect_csv,register_seed
from app.schemas.requests import ScenarioRequest,ClockRequest,ApplyRequest,PlanRequest,PlanSimulationRequest
from app.simulation.engine import aggregate

@asynccontextmanager
async def lifespan(app):
    if not MODEL_PATH.exists() and settings.auto_train: train()
    app.state.repo=Repository()
    app.state.predictor=Predictor()
    register_seed(app.state.repo,app.state.predictor.card)
    app.state.bridge=BridgeService(app.state.repo,app.state.predictor)
    yield

app=FastAPI(title='BridgeTwin AI',version='1.0.0',description=DISCLAIMER,lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',')],allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Write-Token'])

@app.exception_handler(ValueError)
async def invalid(request,exc): return JSONResponse(status_code=422,content={'detail':str(exc)})
@app.exception_handler(RuntimeError)
async def conflict(request,exc): return JSONResponse(status_code=409,content={'detail':str(exc)})
@app.exception_handler(SQLAlchemyError)
async def database_error(request,exc):
    logging.exception('Database operation failed',exc_info=exc)
    return JSONResponse(status_code=503,content={'detail':'The database is unavailable. Check the backend log and retry.'})

def svc(request:Request): return request.app.state.bridge
def write_access(request:Request):
    if settings.api_write_token and not secrets.compare_digest(request.headers.get('x-write-token',''),settings.api_write_token):
        raise HTTPException(401,'A valid write token is required.')

@app.get('/api/health')
def health(request:Request): return {'status':'ok','model':request.app.state.predictor.card['status'],'data_mode':'SYNTHETIC / SIMULATION'}
@app.get('/api/bridge')
def bridge(s=Depends(svc)): return s.view()
@app.get('/api/components')
def components(s=Depends(svc)): return s.view()['components']
@app.get('/api/components/{component_id}')
def component(component_id:str,s=Depends(svc)):
    c=next((c for c in s.view()['components'] if c['component_id']==component_id),None)
    if not c: raise HTTPException(404,'Component not found.')
    return c
@app.get('/api/history/{component_id}')
def history(component_id:str,s=Depends(svc)):
    component(component_id,s)
    return [{'year':h['year'],'health_score':h['components'][component_id],'data_source':h['data_source']} for h in s.view()['history']]
@app.get('/api/predictions/{component_id}')
def predictions(component_id:str,s=Depends(svc)):
    component(component_id,s)
    return [{'horizon':p['horizon'],'health_score':p['components'][component_id],'data_source':p['data_source']} for p in s.view()['predictions']]
@app.get('/api/explanations/{component_id}')
def explanations(component_id:str,s=Depends(svc)):
    return s.predictor.explain(component(component_id,s),s.view()['environment_base'])
@app.get('/api/analytics')
def analytics(s=Depends(svc)):
    state=s.view()
    return {'history':state['history'],'predictions':state['predictions'],'components':state['components'],
            'risk_distribution':[{ 'name':r,'value':sum(c['risk_level']==r for c in state['components'])} for r in ['Healthy','Moderate','High risk','Critical']],
            'maintenance_history':state['maintenance_history']}
@app.get('/api/model-info')
def model_info(request:Request): return request.app.state.predictor.card
@app.get('/api/datasets')
def datasets(request:Request): return request.app.state.repo.list('dataset')
@app.get('/api/simulation-runs')
def runs(request:Request): return request.app.state.repo.list('simulation_run',30)
@app.post('/api/simulate',dependencies=[Depends(write_access)])
def simulate(p:ScenarioRequest,s=Depends(svc)): return s.scenario(p)
@app.post('/api/simulate/future',dependencies=[Depends(write_access)])
def future(p:ClockRequest,s=Depends(svc)): return s.tick(p.months)
@app.post('/api/simulate/apply',dependencies=[Depends(write_access)])
def apply(p:ApplyRequest,s=Depends(svc)): return s.apply_scenario(p.run_id)
@app.post('/api/simulate/reset',dependencies=[Depends(write_access)])
def reset(s=Depends(svc)): return s.reset()
@app.get('/api/maintenance/actions')
def actions(s=Depends(svc)): return s.actions()
@app.post('/api/maintenance/optimize',dependencies=[Depends(write_access)])
def optimize(p:PlanRequest,s=Depends(svc)): return s.optimize(p)
@app.post('/api/maintenance/simulate',dependencies=[Depends(write_access)])
def maintenance(p:PlanSimulationRequest,s=Depends(svc)): return s.simulate_plan(p)
@app.post('/api/data/upload',dependencies=[Depends(write_access)])
async def upload(request:Request,file:UploadFile=File(...),source:str=Form('REAL')):
    if source not in ['REAL','SYNTHETIC']: raise HTTPException(422,'Choose REAL or SYNTHETIC observations.')
    content=await file.read(10*1024*1024+1)
    df,info=inspect_csv(content,file.filename or '',source)
    df.to_csv(ROOT/'data'/'raw'/info['stored_filename'],index=False)
    request.app.state.repo.put('dataset',info['id'],info)
    # Original observations never replace the active simulation or train silently.
    request.app.state.repo.add_observations(df.astype(object).where(df.notna(),None).to_dict('records'))
    return info
@app.get('/api/data/template')
def template():
    from fastapi.responses import Response
    cols=['bridge_id','component_id','timestamp','health_score']+FEATURES+['target_health_1y']
    return Response(','.join(cols)+'\n',media_type='text/csv',headers={'Content-Disposition':'attachment; filename=bridge-observation-template.csv'})
@app.get('/api/report')
def report(s=Depends(svc)):
    return {'bridge':s.view(),'model':s.predictor.card,'datasets':s.repo.list('dataset'),
            'recommended_actions':s.actions(),'runs':s.repo.list('simulation_run',10),'disclaimer':DISCLAIMER}

# Optional single-server production/offline build, with all assets served locally.
DIST=ROOT.parent/'frontend'/'dist'
if DIST.exists():
    app.mount('/assets',StaticFiles(directory=DIST/'assets'),name='assets')
    @app.get('/{path:path}',include_in_schema=False)
    def frontend(path:str):
        if path.startswith('api/'): raise HTTPException(404,'API endpoint not found.')
        candidate=(DIST/path).resolve()
        if candidate.is_relative_to(DIST.resolve()) and candidate.is_file(): return FileResponse(candidate)
        return FileResponse(DIST/'index.html')
