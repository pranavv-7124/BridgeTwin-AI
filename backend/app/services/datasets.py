from io import BytesIO
from uuid import uuid4
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np
from app.config import ROOT, FEATURES, DATA_PATH

LIMITS={'health_score':(0,100),'previous_health':(0,100),'target_health_1y':(0,100),'age':(0,150),
        'traffic_load':(0,100),'heavy_vehicle_percentage':(0,100),'temperature':(-60,70),'rainfall':(0,15000),
        'environmental_exposure':(0,1),'maintenance_delay':(0,100),'last_maintenance_years':(0,150),
        'cumulative_load':(0,1000),'material_factor':(.1,5),'protection':(0,1),'type_code':(0,3)}

def inspect_csv(content,filename,source):
    if not filename.lower().endswith('.csv'): raise ValueError('Upload a UTF-8 CSV file.')
    if len(content)>10*1024*1024: raise ValueError('CSV is larger than the 10 MB limit.')
    if b'\x00' in content: raise ValueError('CSV contains binary data.')
    try: df=pd.read_csv(BytesIO(content),encoding='utf-8-sig',nrows=50001)
    except Exception as e: raise ValueError('Could not parse this UTF-8 CSV. Check the header and delimiter.') from e
    if len(df)==0 or len(df)>50000: raise ValueError('Supply 1–50,000 observation rows.')
    required=['bridge_id','component_id','timestamp','health_score']
    missing=set(required)-set(df.columns)
    if missing: raise ValueError('Missing columns: '+', '.join(sorted(missing)))
    if df[required].isna().any().any(): raise ValueError('Required columns contain missing values.')
    if df.duplicated(['bridge_id','component_id','timestamp']).any(): raise ValueError('Duplicate bridge/component/timestamp observations found.')
    if 'data_source' in df and not df.data_source.eq(source).all(): raise ValueError('CSV source labels must match the selected source type.')
    try: dates=pd.to_datetime(df.timestamp,utc=True,errors='raise')
    except Exception as e: raise ValueError('Timestamps must be valid dates, preferably ISO 8601.') from e
    for col,(low,high) in LIMITS.items():
        if col in df:
            numeric=pd.to_numeric(df[col],errors='coerce')
            if (df[col].notna() & numeric.isna()).any() or np.isinf(numeric.fillna(0)).any(): raise ValueError(f'{col} contains non-numeric or infinite values.')
            if ((numeric<low)|(numeric>high)).any(): raise ValueError(f'{col} must be between {low} and {high}.')
            df[col]=numeric
    for col in ['bridge_id','component_id']:
        if df[col].astype(str).str.len().max()>100: raise ValueError(f'{col} values are too long.')
    df['timestamp']=dates.dt.strftime('%Y-%m-%dT%H:%M:%SZ'); df['data_source']=source
    eligible=all(f in df and df[f].notna().all() for f in FEATURES+['target_health_1y'])
    identifier=str(uuid4())
    info={'id':identifier,'name':Path(filename).name,'source':source,'record_count':len(df),'features':df.columns.tolist(),
          'missing_values':int(df.isna().sum().sum()),'missing_by_column':{k:int(v) for k,v in df.isna().sum().items() if v},
          'date_range':[df.timestamp.min(),df.timestamp.max()], 'training_usage':'Not used · explicit retraining required',
          'testing_usage':'Not used','training_eligible':eligible,'created_at':datetime.now(timezone.utc).isoformat(),
          'real_source_verified':False, 'preview':df.head(20).replace({np.nan:None}).to_dict('records'),
          'stored_filename':f'{identifier}.csv'}
    return df,info

def register_seed(repo,card):
    if not DATA_PATH.exists(): return
    df=pd.read_csv(DATA_PATH)
    repo.put('dataset','synthetic-v1',{'id':'synthetic-v1','name':'Bridge trajectories · seed 42','source':'SYNTHETIC',
             'record_count':len(df),'features':df.columns.tolist(),'missing_values':int(df.isna().sum().sum()),
             'date_range':[str(df.timestamp.min()),str(df.timestamp.max())],
             'training_usage':f"{card.get('split_counts',{}).get('train',0):,} training rows",
             'testing_usage':f"{card.get('split_counts',{}).get('test',0):,} independent test rows",
             'training_eligible':True,'preview':df.head(20).to_dict('records'), 'scenarios':sorted(df.scenario.unique().tolist())})
