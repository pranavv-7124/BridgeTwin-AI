"""Bridge-group train/validation/calibration/test splits; test is never used for selection."""
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import sklearn
import joblib
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.config import FEATURES, MODEL_PATH, MODEL_CARD_PATH, DATA_PATH, TYPE_CODES
from app.ml.synthetic import save_dataset
from app.ml.estimators import ResidualHealthRegressor
from app.simulation.engine import advance_component

def metrics(y, pred):
    return {'mae':float(mean_absolute_error(y,pred)), 'rmse':float(np.sqrt(mean_squared_error(y,pred))), 'r2':float(r2_score(y,pred))}

def split_groups(df):
    train, rest = next(GroupShuffleSplit(n_splits=1, test_size=.4,random_state=42).split(df,groups=df.bridge_id))
    remainder=df.iloc[rest]
    val, hold = next(GroupShuffleSplit(n_splits=1,test_size=.625,random_state=43).split(remainder,groups=remainder.bridge_id))
    hold_frame=remainder.iloc[hold]
    cal, test=next(GroupShuffleSplit(n_splits=1,test_size=.6,random_state=44).split(hold_frame,groups=hold_frame.bridge_id))
    return {'train':train,'validation':rest[val],'calibration':rest[hold[cal]],'test':rest[hold[test]]}

def physical_targets(df):
    types={v:k for k,v in TYPE_CODES.items()}
    out=[]
    for row in df.to_dict('records'):
        c={'type':types[int(row['type_code'])], 'age':row['age'], 'health_score':row['previous_health'],
           'material_factor':row['material_factor'],'protection':row['protection'],
           'last_maintenance_years':row['last_maintenance_years'],'cumulative_load':row['cumulative_load']}
        out.append(advance_component(c,row,1)['health_score'])
    return np.array(out)

def hybrid(model, df, physical):
    learned=np.clip(model.predict(df[FEATURES]),0,df.previous_health.to_numpy())
    return .65*physical+.35*learned

def train(df=None):
    if df is None:
        df=pd.read_csv(DATA_PATH) if DATA_PATH.exists() else save_dataset()
    # Real rows are opt-in through the CLI. Reserve whole real bridges for all held-out sets.
    real=df[df.data_source=='REAL']
    if len(real):
        if real.bridge_id.nunique()<20:
            raise ValueError('Hybrid training requires at least 20 independent real bridges. Keep fewer observations for exploration, not claimed validation.')
        rparts=split_groups(real)
        real_positions=np.flatnonzero(df.data_source.eq('REAL').to_numpy())
        synthetic_positions=np.flatnonzero(df.data_source.eq('SYNTHETIC').to_numpy())
        splits={k:real_positions[v] for k,v in rparts.items()}
        splits['train']=np.concatenate([splits['train'], synthetic_positions])
    else:
        splits=split_groups(df)
    tr=df.iloc[splits['train']]; va=df.iloc[splits['validation']]
    ca=df.iloc[splits['calibration']]; te=df.iloc[splits['test']]
    models={'Random Forest':ResidualHealthRegressor(RandomForestRegressor(n_estimators=90,max_depth=16,min_samples_leaf=3,n_jobs=2,random_state=42)),
            'Gradient Boosting':ResidualHealthRegressor(GradientBoostingRegressor(n_estimators=150,max_depth=3,learning_rate=.08,loss='huber',random_state=42))}
    comparisons=[]
    for name,model in models.items():
        model.fit(tr[FEATURES],tr.target_health_1y)
        comparisons.append({'name':name,'validation':metrics(va.target_health_1y, model.predict(va[FEATURES]))})
    best=min(comparisons,key=lambda x:x['validation']['mae'])['name']
    model=models[best]
    cal_pred=hybrid(model,ca,physical_targets(ca))
    test_physics=physical_targets(te)
    test_pred=hybrid(model,te,test_physics)
    scores=np.abs(ca.target_health_1y.to_numpy()-cal_pred)
    q=float(np.quantile(scores,min(1.,np.ceil((len(scores)+1)*.9)/len(scores)),method='higher'))
    anomaly=IsolationForest(n_estimators=80,contamination=.03,random_state=42,n_jobs=2).fit(tr[FEATURES])
    card={'status':'Trained','version':'BT-1.0','trained_at':datetime.now(timezone.utc).isoformat(),
          'name':best, 'algorithm':type(model.estimator_).__name__,'sklearn_version':sklearn.__version__,
          'prediction_target':'One-year health reconstructed from learned annual deterioration, with physical bounds.',
          'features':FEATURES,'total_records':len(df),'training_records':len(tr),
          'real_records':int((df.data_source=='REAL').sum()),'synthetic_records':int((df.data_source=='SYNTHETIC').sum()),
          'validation_strategy':'Independent bridge groups: 60% train / 15% validation / 10% calibration / 15% test (rounded by bridge count). Real holdouts when real data are supplied.',
          'evaluation_source':'REAL' if len(real) else 'SYNTHETIC',
          'split_counts':{k:len(v) for k,v in splits.items()},
          'split_bridges':{k:sorted(df.iloc[v].bridge_id.unique().tolist()) for k,v in splits.items()},
          'comparisons':comparisons,'test_metrics':metrics(te.target_health_1y,test_pred),
          'raw_ml_test_metrics':metrics(te.target_health_1y,model.predict(te[FEATURES])),
          'persistence_baseline':metrics(te.target_health_1y,te.previous_health),
          'physics_baseline':metrics(te.target_health_1y,test_physics),
          'interval':{'level':.9,'one_year_absolute_residual':q,'test_coverage':float(np.mean(np.abs(te.target_health_1y.to_numpy()-test_pred)<=q)),
                      'method':'Split calibration residual band; group dependence limits coverage claims. Multi-year bands widen by sqrt(years) and are illustrative, not calibrated.'},
          'importance':[{'feature':f,'importance':float(v)} for f,v in sorted(zip(FEATURES,model.feature_importances_),key=lambda x:-x[1])],
          'training_medians':{k:float(v) for k,v in tr[FEATURES].median().items()},
          'training_ranges':{f:[float(tr[f].min()),float(tr[f].max())] for f in FEATURES},
          'limitations':['Synthetic test performance measures fit to this generator, not real bridge accuracy.',
                         'Health is a dimensionless condition proxy; risk is not failure probability.',
                         'Physics-inspired coefficients and maintenance costs are uncalibrated demo assumptions.',
                         'Shared generator and physics baseline make this a controlled experiment, not independent engineering validation.',
                         'Global impurity importance is not a local causal explanation.']}
    joblib.dump({'model':model,'anomaly':anomaly,'card':card},MODEL_PATH,compress=3)
    MODEL_CARD_PATH.write_text(json.dumps(card,indent=2),encoding='utf-8')
    return card
