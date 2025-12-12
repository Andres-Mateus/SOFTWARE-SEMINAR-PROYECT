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
    slot: str | None = None
    check_in_at: datetime
    check_in: datetime | None = None
    check_out_at: Optional[datetime] = None
    check_out: Optional[datetime] = None
    amount: Optional[float] = None


class StatsOut(BaseModel):
    occupied: int
    free: int
    activeVehicles: int
    active_sessions: int
    occupancyPercent: float
    occupancy_percent: float
    currentRatePerMinute: float
    rate_per_minute: float
    rate_per_hour: float


class EntryRequest(BaseModel):
    plate: str


class ExitRequest(BaseModel):
    plate: str


class EntryResponse(BaseModel):
    plate: str
    slot_code: str
    slot: str | None = None
    check_in_at: datetime
    check_in: datetime | None = None


class ExitResponse(BaseModel):
    plate: str
    slot_code: str
    slot: str | None = None
    check_in_at: datetime
    check_in: datetime | None = None
    minutes: int
    amount: float
    rate_per_minute: float
    rate_per_hour: float
    check_out_at: datetime
    check_out: datetime | None = None
