from copy import deepcopy
import math
import numpy as np
import pandas as pd
import joblib
import logging
from app.config import MODEL_PATH, FEATURES
from app.simulation.engine import advance_component, features, aggregate, condition

class Predictor:
    def __init__(self):
        try:
            self.bundle = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
        except Exception:
            logging.exception('Model could not load. Use the documented training command to rebuild it.')
            self.bundle = None

    @property
    def card(self):
        return self.bundle['card'] if self.bundle else {'status':'MODEL NOT TRAINED','features':FEATURES}

    def next_year(self, components, env):
        out=[advance_component(c,env,1) for c in components]
        if self.bundle:
            frame=pd.DataFrame([features(c,env) for c in components])[FEATURES]
            predicted=self.bundle['model'].predict(frame)
            for c,nxt,p in zip(components,out,predicted):
                nxt['health_score']=.65*nxt['health_score']+.35*float(np.clip(p,0,c['health_score']))
                condition(nxt)
        return out

    def forecast(self, components, env, years=5):
        running=deepcopy(components)
        points=[]
        q=self.card.get('interval',{}).get('one_year_absolute_residual',0)
        for y in range(years+1):
            a=aggregate(running)
            width=q*math.sqrt(y)
            points.append({'horizon':y,'health_score':a['health_score'], 'risk_level':a['risk_level'],
                'lower':round(max(0,a['health_score']-width),2),'upper':round(min(100,a['health_score']+width),2),
                'components':{c['component_id']:round(c['health_score'],2) for c in running},
                'data_source':'PREDICTION' if y else 'CURRENT',
                'method':'Hybrid physics + ML' if self.bundle else 'Physics-only fallback'})
            if y<years: running=self.next_year(running,env)
        return {'points':points,'final_components':running,'method':points[-1]['method']}

    def anomalies(self, components, env):
        if not self.bundle: return [{'status':'Unavailable','score':None} for _ in components]
        frame=pd.DataFrame([features(c,env) for c in components])[FEATURES]
        scores=self.bundle['anomaly'].decision_function(frame)
        return [{'status':'Anomalous' if s<0 else 'Warning' if s<.03 else 'Normal','score':round(float(s),4)} for s in scores]

    def explain(self, component, env):
        if not self.bundle: return {'method':'Model unavailable','global_importance':[],'sensitivities':[], 'out_of_range_features':[], 'note':'Model unavailable. Forecasts use the documented physics-only fallback.'}
        current=self.next_year([component],env)[0]['health_score']
        values=features(component,env)
        items=[]
        for feature in ['traffic_load','heavy_vehicle_percentage','environmental_exposure','maintenance_delay','temperature']:
            changed={**env,feature:self.card['training_medians'][feature]}
            alternative=self.next_year([component],changed)[0]['health_score']
            items.append({'feature':feature,'current_value':values[feature], 'reference_value':changed[feature],
                          'health_point_change':round(alternative-current,4)})
        out_of_range=[f for f in FEATURES if not self.card['training_ranges'][f][0]<=values[f]<=self.card['training_ranges'][f][1]]
        return {'method':'Global model impurity importance + one-variable reference sensitivity',
                'global_importance':self.card['importance'], 'sensitivities':sorted(items,key=lambda x:-abs(x['health_point_change'])),
                'out_of_range_features':out_of_range,
                'note':'Sensitivities compare one-year predictions after replacing one input with its training median. They are not causal effects or additive contributions.'}
