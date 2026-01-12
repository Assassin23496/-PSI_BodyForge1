from datetime import datetime, date
from typing import List

from pydantic import BaseModel, Field

from .enums import Gender, Goal


class ProfileBase(BaseModel):
    name: str = Field(..., example="Jan")
    gender: Gender
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    goal: Goal
    goal_months: int = Field(..., gt=0, le=12)
    preferred_from_hour: int | None = Field(None, ge=0, le=23)
    preferred_to_hour: int | None = Field(None, ge=0, le=23)


class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    height_cm: float | None = None
    birth_date: date | None = None

class ProfileAuth(BaseModel):
    id: int
    email: str
    password_hash: str
    is_active: bool

    class Config:
        from_attributes = True


class ProfileInDB(ProfileBase):
    id: int
    email: str
    bmi: float
    needs_bmi_update: bool
    program_started_at: datetime | None = None
    last_bmi_check_at: datetime | None = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class CurrentUser(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True

class BmiRecord(BaseModel):
    id: int
    profile_id: int
    weight_kg: float
    bmi: float
    created_at: datetime

    class Config:
        from_attributes = True


class BmiCheckRequest(BaseModel):
    weight_kg: float = Field(..., gt=0)


class PlanDay(BaseModel):
    date: date
    workout: str
    food_tips: str
    preferred_hours: str
    note: str | None = None


class WorkoutPlan(BaseModel):
    id: int
    profile_id: int
    goal: Goal
    plan_json: str
    duration_weeks: int
    days: List[PlanDay]
    created_at: datetime

    class Config:
        from_attributes = True


class PlanCreateResult(BaseModel):
    profile: ProfileInDB
    plan: WorkoutPlan


class BmiCheckResult(BaseModel):
    profile: ProfileInDB
    latest_bmi: float
    message: str
    plan_changed: bool

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    gender: Gender
    birth_date: date | None = None
    height_cm: float = Field(...,gt=1)
    weight_kg: float = Field(...,gt=1)
    goal: Goal
    goal_months: int



