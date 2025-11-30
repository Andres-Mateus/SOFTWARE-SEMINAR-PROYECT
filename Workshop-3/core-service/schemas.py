from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SlotOut(BaseModel):
    code: str
    occupied: bool
    plate: Optional[str] = None

    class Config:
        orm_mode = True


class SessionOut(BaseModel):
    plate: str
    slot_code: str
    check_in_at: datetime
    check_out_at: Optional[datetime] = None
    amount: Optional[float] = None


class StatsOut(BaseModel):
    occupied: int
    free: int
    activeVehicles: int
    occupancyPercent: float
    currentRatePerMinute: float


class EntryRequest(BaseModel):
    plate: str


class ExitRequest(BaseModel):
    plate: str


class EntryResponse(BaseModel):
    plate: str
    slot_code: str
    check_in_at: datetime


class ExitResponse(BaseModel):
    plate: str
    slot_code: str
    minutes: int
    amount: float
    check_out_at: datetime
