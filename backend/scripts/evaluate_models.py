from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
from app.config import MODEL_CARD_PATH
if not MODEL_CARD_PATH.exists(): raise SystemExit('MODEL NOT TRAINED. Run scripts/train_models.py first.')
card=json.loads(MODEL_CARD_PATH.read_text())
print(json.dumps({k:card[k] for k in ['version','trained_at','evaluation_source','validation_strategy','comparisons','test_metrics','raw_ml_test_metrics','physics_baseline','persistence_baseline','interval','limitations']},indent=2))
