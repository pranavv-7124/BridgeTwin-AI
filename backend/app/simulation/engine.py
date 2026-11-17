"""Monthly, stateful, engineering-inspired condition model. See docs/METHODOLOGY.md."""
from copy import deepcopy
import math
from datetime import datetime, timezone
from app.config import BASE_RATES, TYPE_CODES, RISK_THRESHOLDS

def risk(health):
    return next(label for threshold, label in RISK_THRESHOLDS if health >= threshold)

def condition(c):
    c['health_score'] = round(max(0., min(100., c['health_score'])), 4)
    c['risk_level'] = risk(c['health_score'])
    c['deterioration_index'] = round(1 - c['health_score'] / 100, 4)
    c['maintenance_status'] = ('Prioritize intervention' if c['health_score'] < 60 else
                               'Schedule preventive care' if c['health_score'] < 80 else 'Routine monitoring')
    return c

def rate_terms(c, env):
    """All terms dimensionless except base, in health points/year. Not stress/FEA."""
    return {
        'base': BASE_RATES[c['type']],
        'age': 1 + .018 * c['age'],
        'loading': 1 + .65 * (env['traffic_load'] / 100)**1.4 + 1.1 * (env['heavy_vehicle_percentage'] / 100)**1.6,
        'exposure': 1 + .45 * env['environmental_exposure'] + .12 * env['rainfall'] / 2000 + .1 * abs(env['temperature'] - 22) / 25,
        'delay': 1 + .055 * max(0, c['last_maintenance_years'] - 4) + .09 * env.get('maintenance_delay', 0),
        'fatigue': 1 + .008 * c['cumulative_load'],
        'material': c['material_factor'],
        'protection': 1 - .4 * c.get('protection', 0),
    }

def deterioration_rate(c, env):
    return math.prod(rate_terms(c, env).values())

def features(c, env):
    return {**{k: env[k] for k in ['traffic_load','heavy_vehicle_percentage','temperature','rainfall','environmental_exposure']},
            'age': c['age'], 'cumulative_load': c['cumulative_load'],
            'last_maintenance_years': c['last_maintenance_years'],
            'maintenance_delay': env.get('maintenance_delay', 0),
            'previous_health': c['health_score'], 'material_factor': c['material_factor'],
            'protection': c.get('protection', 0), 'type_code': TYPE_CODES[c['type']]}

def advance_component(c, env, years, noise=0.):
    c = deepcopy(c)
    steps = max(1, int(math.ceil(years * 12)))
    dt = years / steps
    for _ in range(steps):
        loss = max(0, deterioration_rate(c, env) * (1 + noise)) * dt
        c['health_score'] = max(0., c['health_score'] - loss)
        c['age'] += dt
        c['last_maintenance_years'] += dt
        c['cumulative_load'] += env['traffic_load'] / 100 * (1 + 2 * env['heavy_vehicle_percentage'] / 100) * dt
        c['protection'] = max(0., c.get('protection', 0) - .08 * dt)
    return condition(c)

def aggregate(components):
    total = sum(c['weight'] for c in components)
    health = sum(c['health_score'] * c['weight'] for c in components) / total
    high = [c for c in components if c['health_score'] < 60]
    worst = min(components, key=lambda c: c['health_score'])
    return {'health_score': round(health, 2), 'risk_level': risk(health),
            'high_risk_count': len(high), 'component_count': len(components),
            'worst_component': worst['name'], 'priority': 'Urgent review' if worst['health_score'] < 40 else 'Plan intervention' if high else 'Preventive care',
            'risk_index': round(sum((100-c['health_score'])**2 / 100 * c['weight'] for c in components) / total, 2)}

def seasonal_environment(base, month):
    phase = 2 * math.pi * month / 12
    return {**base, 'traffic_load': max(0, min(100, base['traffic_load'] + 5 * math.sin(phase + .4))),
            'heavy_vehicle_percentage': max(0, min(100, base['heavy_vehicle_percentage'] + 2 * math.sin(phase + 1))),
            'temperature': base['temperature'] + 5 * math.sin(phase - .6),
            'rainfall': max(0, base['rainfall'] * (1 + .22 * math.sin(phase + 1.5)))}

def advance_state(state, months):
    state = deepcopy(state)
    for _ in range(months):
        state['simulation']['month'] += 1
        env = seasonal_environment(state['environment_base'], state['simulation']['month'])
        state['environment'] = env
        state['components'] = [advance_component(c, env, 1/12) for c in state['components']]
        state['bridge']['age'] += 1/12
        state['history'].append(history_point(state, 'SIMULATION'))
    state['simulation']['year'] = 2026 + state['simulation']['month'] / 12
    state['metadata']['data_source'] = 'SIMULATION'
    state['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()
    return state

def history_point(state, source):
    return {'year': round(2026 + state['simulation']['month'] / 12, 4),
            'health_score': aggregate(state['components'])['health_score'], 'data_source': source,
            'traffic_load': state['environment']['traffic_load'],
            'environmental_exposure': state['environment']['environmental_exposure'],
            'components': {c['component_id']: round(c['health_score'], 2) for c in state['components']}}

def make_baseline():
    env = {'traffic_load': 64., 'heavy_vehicle_percentage': 22., 'temperature': 27.,
           'rainfall': 1100., 'environmental_exposure': .55, 'maintenance_delay': 0.}
    specs = [('DECK_01','Main deck','deck',1.0,3.0),
             ('PIER_01','Pier 1','pier',.8,1.0), ('PIER_02','Pier 2','pier',1.55,1.0),
             ('PIER_03','Pier 3','pier',1.0,1.0), ('PIER_04','Pier 4','pier',.7,1.0),
             ('BEARING_01','Bearing group','bearing',1.18,1.0),
             ('JOINT_01','Expansion joint 1','joint',1.1,.5), ('JOINT_02','Expansion joint 2','joint',.82,.5)]
    components = [condition({'component_id': i, 'name': n, 'type': t, 'age': 0., 'health_score': 100.,
                   'last_maintenance_years': 0., 'cumulative_load': 0., 'material_factor': m,
                   'protection': 0., 'weight': w, 'data_source': 'SYNTHETIC'}) for i,n,t,m,w in specs]
    state = {'bridge': {'id': 'BT-PUNE-001', 'name': 'Mula River Bridge', 'location': 'Pune, Maharashtra · Fictional demonstration asset',
             'type': 'Reinforced concrete girder bridge', 'length_m': 180, 'width_m': 12, 'spans': 5,
             'commissioned': 2008, 'age': 18}, 'components': components,
             'environment': env, 'environment_base': env.copy(),
             'simulation': {'month': -216, 'year': 2008, 'scenario': 'Baseline operation', 'status': 'Paused'},
             'history': [], 'maintenance_history': [],
             'metadata': {'data_source': 'SYNTHETIC', 'real_sensors': False, 'seed': 42,
                          'updated_at': datetime.now(timezone.utc).isoformat()}}
    for year in range(19):
        state['simulation']['month'] = (year-18)*12
        if year:
            state['components'] = [advance_component(c, env, 1) for c in state['components']]
        if year in [8, 14]:
            for c in state['components']:
                if c['component_id'] in ['JOINT_02','PIER_04'] or (year==8 and c['type']=='deck'):
                    c['health_score'] = min(97., c['health_score'] + 7)
                    c['last_maintenance_years'] = 0
                    c['protection'] = .7
                    condition(c)
                    state['maintenance_history'].append({'year': 2008+year, 'component_id': c['component_id'], 'action': 'Preventive maintenance', 'data_source': 'SYNTHETIC'})
        state['history'].append(history_point(state, 'SYNTHETIC'))
    state['simulation'].update({'month': 0, 'year': 2026})
    return state
