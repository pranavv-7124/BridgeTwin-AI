from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
from app.database.repository import Repository
from app.simulation.engine import make_baseline
from app.ml.predictor import Predictor
from app.services.datasets import register_seed
p=argparse.ArgumentParser(description='Initialize a demo database without overwriting existing simulation state.')
p.add_argument('--reset',action='store_true',help='Explicitly reset active simulation to the synthetic baseline.')
args=p.parse_args();repo=Repository();state,revision=repo.get_state()
if state is None or args.reset: repo.save_state(make_baseline(),revision)
register_seed(repo,Predictor().card)
print('Database initialized. Original observations and prior simulation runs were retained.')
