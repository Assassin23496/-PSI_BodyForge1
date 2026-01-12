
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..domain.models import BmiRecord, ProfileInDB, WorkoutPlan
from ..domain.enums import Goal

class AbstractProfileRepository(ABC):

    @abstractmethod
    async def create_profile(self, profile: dict) -> ProfileInDB:
        ...

    @abstractmethod
    async def get_profile(self, profile_id: int) -> Optional[ProfileInDB]:
        ...

    @abstractmethod
    async def get_profile_by_email(self, email: str) -> Optional[ProfileInDB]:
        ...

    @abstractmethod
    async def list_profiles(self) -> List[ProfileInDB]:
        ...

    @abstractmethod
    async def update_profile(self, profile_id: int, data: dict) -> ProfileInDB:
        ...

    @abstractmethod
    async def soft_delete_profile(self, profile_id: int) -> None:
        ...

    @abstractmethod
    async def set_program_started(self, profile_id: int, started_at: datetime) -> None:
        ...

    @abstractmethod
    async def update_last_bmi_check(self, profile_id: int, check_time: datetime) -> None:
        ...

    @abstractmethod
    async def mark_all_need_bmi_update(self) -> None:
        ...

    @abstractmethod
    async def clear_need_bmi_update(self, profile_id: int) -> None:
        ...

    @abstractmethod
    async def add_bmi_record(self, profile_id: int, weight_kg: float, bmi: float) -> BmiRecord:
        ...

    @abstractmethod
    async def get_latest_bmi_record(self, profile_id: int) -> Optional[BmiRecord]:
        ...

    @abstractmethod
    async def update_weight_and_bmi(
        self,
        profile_id: int,
        weight_kg: float,
        bmi: float,
        check_time: datetime,
    ) -> None:
        ...

    @abstractmethod
    async def save_plan(
        self,
        profile_id: int,
        goal: str,
        duration_weeks: int,
        plan_json: str,
    ) -> WorkoutPlan:
        ...

    @abstractmethod
    async def get_latest_plan(self, profile_id: int) -> Optional[WorkoutPlan]:
        ...

    @abstractmethod
    async def update_goal_and_months(
            self,
            profile_id: int,
            goal: Goal | None,
            goal_months: int | None,
    ) -> ProfileInDB | None:
        ...