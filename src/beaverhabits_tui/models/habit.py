from __future__ import annotations

from pydantic import BaseModel


class HabitRecordData(BaseModel):
    day: str
    done: bool
    text: str | None = None


class HabitRecord(BaseModel):
    data: HabitRecordData


class HabitPeriod(BaseModel):
    period_type: str
    period_count: int
    target_count: int


class HabitDetail(BaseModel):
    id: str
    name: str
    star: bool
    records: list[HabitRecord] = []
    status: str
    period: HabitPeriod | None = None
    tags: list[str] = []


class HabitLite(BaseModel):
    id: str
    name: str
