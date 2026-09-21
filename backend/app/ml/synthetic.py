"""Reproducible longitudinal data: controlled noise around shared deterioration equations."""
import numpy as np
import pandas as pd
from app.simulation.engine import advance_component, features
from app.config import DATA_PATH

SCENARIOS = ['Normal operation','High traffic','Heavy vehicles','Environmental stress','Aging',
             'Delayed maintenance','Moderate deterioration','Severe deterioration','Combined stress','Post-maintenance recovery']

def generate(n_bridges=160, years=12, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for b in range(n_bridges):
        scenario = SCENARIOS[b % len(SCENARIOS)]
        env = {'traffic_load': float(rng.uniform(25, 90)), 'heavy_vehicle_percentage': float(rng.uniform(5, 35)),
               'temperature': float(rng.uniform(10, 38)), 'rainfall': float(rng.uniform(350, 2400)),
               'environmental_exposure': float(rng.uniform(.15,.85)), 'maintenance_delay': 0.}
        if scenario in ['High traffic','Combined stress']: env['traffic_load'] = float(rng.uniform(85, 100))
        if scenario in ['Heavy vehicles','Combined stress']: env['heavy_vehicle_percentage'] = float(rng.uniform(35, 70))
        if scenario in ['Environmental stress','Combined stress']: env.update(environmental_exposure=.95, rainfall=2800., temperature=42.)
        if scenario in ['Delayed maintenance','Combined stress']: env['maintenance_delay'] = 6.
        age = float(rng.uniform(1, 30) + (15 if scenario in ['Aging','Severe deterioration'] else 0))
        for j, typ in enumerate(['deck','pier','pier','pier','pier','bearing','joint','joint']):
            c = {'type': typ,'age': 0.,'health_score': 100.,'material_factor': float(rng.uniform(.65,1.6)),
                 'last_maintenance_years':0.,'cumulative_load':0.,'protection':0.}
            c = advance_component(c,env,age)
            for year in range(years):
                local = {**env, 'traffic_load': float(np.clip(env['traffic_load'] + 3*np.sin(year/2), 0,100))}
                if (scenario=='Post-maintenance recovery' and year in [0,5]) or (year==6 and b%4==0):
                    c['health_score'] = min(98, c['health_score']+22)
                    c['last_maintenance_years'] = 0.
                    c['protection'] = .9
                x = features(c, local)
                nxt = advance_component(c,local,1,noise=float(rng.normal(0,.06)))
                rows.append({'bridge_id':f'SYN-{b:04}', 'component_id':f'{typ.upper()}_{j}',
                             'timestamp':f'{2010+year}-01-01', 'scenario':scenario,'data_source':'SYNTHETIC',
                             **x, 'health_score':round(c['health_score'],5),
                             'target_health_1y':round(nxt['health_score'],5)})
                c = nxt
    return pd.DataFrame(rows)

def save_dataset(n_bridges=160, seed=42):
    df=generate(n_bridges=n_bridges,seed=seed)
    df.to_csv(DATA_PATH,index=False)
    return df
