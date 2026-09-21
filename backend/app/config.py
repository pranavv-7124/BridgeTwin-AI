"""Transparent prototype assumptions, not calibrated structural coefficients."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{ROOT / 'data' / 'bridgetwin.db'}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    auto_train: bool = True
    api_write_token: str = ""
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')

settings = Settings()
RISK_THRESHOLDS = [(80, 'Healthy'), (60, 'Moderate'), (40, 'High risk'), (0, 'Critical')]
BASE_RATES = {'deck': .65, 'pier': .55, 'bearing': .9, 'joint': .85}
TYPE_CODES = {'deck': 0, 'pier': 1, 'bearing': 2, 'joint': 3}
FEATURES = ['age', 'traffic_load', 'heavy_vehicle_percentage', 'temperature', 'rainfall',
            'environmental_exposure', 'cumulative_load', 'last_maintenance_years',
            'maintenance_delay', 'previous_health', 'material_factor', 'protection', 'type_code']
DISCLAIMER = ('BridgeTwin AI is an academic decision-support prototype. Model outputs and '
              'simulations are not substitutes for certified structural inspection or engineering assessment.')
MODEL_PATH = ROOT / 'models_saved' / 'health_model.joblib'
MODEL_CARD_PATH = ROOT / 'models_saved' / 'model_card.json'
DATA_PATH = ROOT / 'data' / 'synthetic' / 'bridge_trajectories.csv'

