from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
import pandas as pd
from app.ml.training import train
from app.ml.synthetic import save_dataset
from app.config import DATA_PATH,FEATURES
from app.services.datasets import inspect_csv
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Train and compare models; never loads uploaded executable model files.')
    p.add_argument('--real-csv',type=Path,help='Optional normalized REAL dataset. Requires 20+ independent bridges and one-year targets.')
    args=p.parse_args()
    data=pd.read_csv(DATA_PATH) if DATA_PATH.exists() else save_dataset()
    if args.real_csv:
        real,info=inspect_csv(args.real_csv.read_bytes(),args.real_csv.name,'REAL')
        if not info['training_eligible']: p.error('Real data must contain all complete features plus target_health_1y. See docs/DATA_GUIDE.md.')
        if set(real.bridge_id)&set(data.bridge_id): p.error('Real and synthetic bridge identifiers overlap. Use distinct IDs.')
        data=pd.concat([data,real],ignore_index=True)
    result=train(data)
    print(json.dumps({k:result[k] for k in ['name','evaluation_source','training_records','real_records','test_metrics','raw_ml_test_metrics']},indent=2))
    print('Restart the API to load this version. Synthetic evaluation is not real-world validation.')
