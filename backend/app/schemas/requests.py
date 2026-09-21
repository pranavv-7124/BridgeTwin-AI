from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)

class ScenarioRequest(StrictModel):
    name: str = Field(default='Custom stress scenario', min_length=1, max_length=100)
    traffic_change: float = Field(default=30, ge=-80, le=100)
    heavy_vehicle_change: float = Field(default=20, ge=-80, le=100)
    environmental_change: float = Field(default=15, ge=-80, le=100)
    temperature_change: float = Field(default=3, ge=-20, le=20)
    maintenance_delay: float = Field(default=2, ge=0, le=15)
    horizon: int = Field(default=5, ge=1, le=20)

class ClockRequest(StrictModel):
    months: int = Field(default=1, ge=1, le=120)

class ApplyRequest(StrictModel):
    run_id: str

class PlanRequest(StrictModel):
    budget: float = Field(default=2500000, ge=0, le=100000000)
    horizon: int = Field(default=5, ge=1, le=20)

class PlanSimulationRequest(PlanRequest):
    action_ids: list[str] = Field(default_factory=list, max_length=8)
    apply: bool = False
