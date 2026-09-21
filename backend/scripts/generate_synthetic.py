from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
from app.ml.synthetic import save_dataset
from app.config import DATA_PATH
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Create reproducible bridge component trajectories.')
    p.add_argument('--bridges',type=int,default=160);p.add_argument('--seed',type=int,default=42)
    args=p.parse_args()
    if not 40<=args.bridges<=10000: p.error('Choose 40–10,000 bridges.')
    data=save_dataset(args.bridges,args.seed)
    print(f'Saved {len(data):,} SYNTHETIC observations to {DATA_PATH}')
