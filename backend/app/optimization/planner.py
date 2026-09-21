"""Multiple-choice knapsack as a mixed integer program, with one action/component."""
from copy import deepcopy
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from app.simulation.engine import condition, aggregate

# Illustrative INR assumptions, not contractor estimates. All benefits are condition points.
CATALOG = {
    'deck': [('Preventive maintenance',240000,8,.65,5),('Deck resurfacing',850000,22,.85,21),('Structural rehabilitation',1900000,38,.95,60)],
    'pier': [('Preventive maintenance',160000,7,.6,4),('Pier strengthening',650000,25,.85,28),('Structural rehabilitation',1400000,40,.95,60)],
    'bearing': [('Preventive maintenance',140000,7,.6,3),('Bearing replacement',480000,34,.95,14)],
    'joint': [('Preventive maintenance',90000,6,.6,2),('Joint replacement',260000,30,.95,7)],
}

def candidates(components):
    actions=[]
    for c in components:
        choices=[('Detailed inspection',45000,0,0,2)]+CATALOG[c['type']]
        for idx,(name,cost,gain,protection,duration) in enumerate(choices):
            # Inspection gives information, not fictitious physical recovery.
            benefit=min(gain,max(0,98-c['health_score']))
            before=(100-c['health_score'])**2/100
            after=(100-c['health_score']-benefit)**2/100
            reduction=max(0,before-after)
            actions.append({'id':f"{c['component_id']}:{idx}", 'component_id':c['component_id'],'component_name':c['name'],
                            'name':name,'cost':cost,'health_gain':round(benefit,2),'risk_reduction':round(reduction,3),
                            'objective_benefit':reduction*c['weight'],'protection':protection,'duration_days':duration,
                            'priority':'Urgent' if c['health_score']<40 else 'High' if c['health_score']<60 else 'Medium' if c['health_score']<80 else 'Routine',
                            'current_health':round(c['health_score'],2),'suggested_timeline':'Within 1 month' if c['health_score']<40 else 'Within 3 months' if c['health_score']<60 else 'Within 12 months',
                            'applicable_condition':'Information only' if idx==0 else 'Condition below 98',
                            'estimate_source':'Configured academic assumption'})
    return actions

def apply_actions(components, actions):
    out=deepcopy(components)
    for c in out:
        action=next((a for a in actions if a['component_id']==c['component_id']),None)
        if action and action['health_gain']>0:
            c['health_score']=min(98,c['health_score']+action['health_gain'])
            c['last_maintenance_years']=0.
            c['protection']=max(c.get('protection',0),action['protection'])
            c['data_source']='SIMULATION'
            condition(c)
    return out

def summarize(components, actions, budget):
    treated=apply_actions(components,actions)
    before=aggregate(components); after=aggregate(treated)
    total=sum(a['cost'] for a in actions)
    return {'actions':actions,'total_cost':total,'remaining_budget':budget-total,
            'components_treated':sum(a['health_gain']>0 for a in actions),
            'health_improvement':round(after['health_score']-before['health_score'],2),
            'risk_reduction':round(before['risk_index']-after['risk_index'],2),
            'budget':budget,'within_budget':total<=budget}

def optimize(components,budget):
    options=[a for a in candidates(components) if a['health_gain']>0 and a['cost']<=budget]
    if not options: return {**summarize(components,[],budget),'solver':'SciPy HiGHS MILP','status':'Optimal · no affordable beneficial action'}
    ids=[c['component_id'] for c in components]
    A=np.array([[a['cost'] for a in options]]+[[int(a['component_id']==cid) for a in options] for cid in ids],dtype=float)
    upper=np.array([budget]+[1]*len(ids))
    solved=milp(c=-np.array([a['objective_benefit'] for a in options]),
                integrality=np.ones(len(options)),bounds=Bounds(0,1),
                constraints=LinearConstraint(A,np.zeros(len(upper)),upper),options={'time_limit':10})
    if not solved.success: raise ValueError('Optimizer could not prove an optimal solution. Reduce the action set or try again.')
    selected=[a for a,v in zip(options,solved.x) if v>.5]
    return {**summarize(components,selected,budget),'solver':'SciPy HiGHS MILP','status':'Optimal',
            'objective':'Maximize component-weighted reduction in quadratic condition-deficit index; at most one action per component.'}
