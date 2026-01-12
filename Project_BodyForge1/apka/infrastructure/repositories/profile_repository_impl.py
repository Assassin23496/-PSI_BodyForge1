import json
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import insert, select, update, delete


from ...db import database, profiles, bmi_records, workout_plans
from ...core.domain.models import ProfileAuth, ProfileInDB, WorkoutPlan, BmiRecord
from ...core.domain.enums import Goal
from ...core.repositories.profile_repository import AbstractProfileRepository


class ProfileRepositoryImpl(AbstractProfileRepository):
    def __init__(self):
        self.db = database

    async def create_profile(self, profile: dict) -> ProfileInDB:
        query = (
            insert(profiles)
            .values(**profile)
            .returning(profiles)
        )
        row = await self.db.fetch_one(query)
        return ProfileInDB(**dict(row))

    async def get_profile(self, profile_id: int):
        query = (
            profiles
            .select()
            .where(
                (profiles.c.id == profile_id) &
                (profiles.c.is_active == True)
            )
        )
        row = await self.db.fetch_one(query)
        if row:
            return ProfileInDB(**dict(row))
        return None

    async def list_profiles(self) -> List[ProfileInDB]:
        query = (
            select(profiles)
            .where(profiles.c.is_active == True)
            .order_by(profiles.c.id)
        )
        rows = await self.db.fetch_all(query)
        return [ProfileInDB(**dict(r)) for r in rows]

    async def add_bmi_record(
        self, profile_id: int, weight_kg: float, bmi: float
    ) -> BmiRecord:
        query = (
            insert(bmi_records)
            .values(profile_id=profile_id, weight_kg=weight_kg, bmi=bmi)
            .returning(bmi_records)
        )
        row = await self.db.fetch_one(query)
        return BmiRecord(**dict(row))

    async def get_latest_bmi_record(self, profile_id: int) -> Optional[BmiRecord]:
        query = (
            select(bmi_records)
            .where(bmi_records.c.profile_id == profile_id)
            .order_by(bmi_records.c.created_at.desc())
            .limit(1)
        )
        row = await self.db.fetch_one(query)
        if row:
            return BmiRecord(**dict(row))
        return None

    async def save_plan(
        self, profile_id: int, goal: str, duration_weeks: int, plan_json: str
    ) -> WorkoutPlan:
        query = (
            insert(workout_plans)
            .values(
                profile_id=profile_id,
                goal=goal,
                duration_weeks=duration_weeks,
                plan_json=plan_json,
            )
            .returning(workout_plans)
        )
        row = await self.db.fetch_one(query)
        data = dict(row)
        # parsujemy JSON na listę dni
        plan_days = json.loads(data["plan_json"])
        return WorkoutPlan(
            id=data["id"],
            profile_id=data["profile_id"],
            goal=data["goal"],
            plan_json=data["plan_json"],
            duration_weeks=data["duration_weeks"],
            days=plan_days,
            created_at=data["created_at"],
        )

    async def get_latest_plan(self, profile_id: int) -> Optional[WorkoutPlan]:
        query = (
            select(workout_plans)
            .where(workout_plans.c.profile_id == profile_id)
            .order_by(workout_plans.c.created_at.desc())
            .limit(1)
        )
        row = await self.db.fetch_one(query)
        if row:
            data = dict(row)
            plan_days = json.loads(data["plan_json"])
            return WorkoutPlan(
                id=data["id"],
                profile_id=data["profile_id"],
                goal=data["goal"],
                duration_weeks=data["duration_weeks"],
                plan_json=data["plan_json"],
                days=plan_days,
                created_at=data["created_at"],
            )
        return None

    async def mark_all_need_bmi_update(self) -> None:
        query = update(profiles).values(needs_bmi_update=True)
        await self.db.execute(query)

    async def clear_need_bmi_update(self, profile_id: int) -> None:
        query = (
            update(profiles)
            .where(profiles.c.id == profile_id)
            .values(needs_bmi_update=False)
        )
        await self.db.execute(query)

    async def soft_delete_profile(self, profile_id: int) -> None:
        query = (
            update(profiles)
            .where(profiles.c.id == profile_id)
            .values(is_active=False)
        )
        await self.db.execute(query)

    async def set_program_started(self, profile_id: int, started_at: datetime) -> None:
        query = (
            update(profiles)
            .where(profiles.c.id == profile_id)
            .values(program_started_at=started_at, last_bmi_check_at=started_at)
        )
        await self.db.execute(query)

    async def update_last_bmi_check(self, profile_id: int, check_time: datetime) -> None:
        query = (
            update(profiles)
            .where(profiles.c.id == profile_id)
            .values(last_bmi_check_at=check_time)
        )
        await self.db.execute(query)

    async def update_profile(self, profile_id: int, data: dict) -> ProfileInDB:
        query = (
            update(profiles)
            .where(profiles.c.id == profile_id)
            .values(**data)
            .returning(profiles)
        )
        row = await self.db.fetch_one(query)
        return ProfileInDB(**dict(row))

    async def get_profile_by_email(self, email: str):
        query = (
            select(profiles)
            .where(
                (profiles.c.email == email) &
                (profiles.c.is_active.is_(True))
            )
            .limit(1)
        )
        row = await self.db.fetch_one(query)
        if row:
            return ProfileAuth(**dict(row))
        return None

    async def update_weight_and_bmi(self, profile_id: int, weight_kg: float, bmi: float, check_time: datetime) -> None:
        query = (
            update(profiles)
            .where(profiles.c.id == profile_id)
            .values(
                weight_kg=weight_kg,
                bmi=bmi,
                last_bmi_check_at=check_time,
                needs_bmi_update=False,
            )
        )
        await self.db.execute(query)

    async def update_goal_and_months(
            self,
            profile_id: int,
            goal: Goal | None,
            goal_months: int | None,
    ) -> ProfileInDB | None:
        values: dict = {}
        if goal is not None:
            # в БД храним строковое значение энума
            values["goal"] = goal.value if hasattr(goal, "value") else str(goal)
        if goal_months is not None:
            values["goal_months"] = goal_months

        if values:
            q = (
                profiles.update()
                .where(profiles.c.id == profile_id)
                .values(**values)
                .returning(*profiles.c)
            )
            row = await self.db.fetch_one(q)
        else:
            row = await self.db.fetch_one(
                select(profiles).where(profiles.c.id == profile_id)
            )

        if not row:
            return None
        return ProfileInDB(**dict(row))