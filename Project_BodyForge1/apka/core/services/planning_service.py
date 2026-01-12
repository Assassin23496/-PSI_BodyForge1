import json
from datetime import date as date_type
from typing import Optional

from ..domain.enums import Goal
from ..domain.models import WorkoutPlan, PlanDay
from ..repositories.profile_repository import AbstractProfileRepository
from ...utils.planning import build_simple_plan


class PlanningService:
    def __init__(self, repo: AbstractProfileRepository):
        self.repo = repo

    async def create_initial_plan(
        self,
        profile_id: int,
        goal: Goal,
        goal_months: int,
        preferred_from_hour: Optional[int],
        preferred_to_hour: Optional[int],
    ) -> WorkoutPlan:
        weeks = max(4, goal_months * 4)

        plan_days = build_simple_plan(
            goal=goal,
            weeks=weeks,
            preferred_from_hour=preferred_from_hour,
            preferred_to_hour=preferred_to_hour,
            meals_offset_hint="2h po jedzeniu",
        )


        plan_json = json.dumps(
            [d.model_dump(mode="json") for d in plan_days],
            ensure_ascii=False,
        )

        plan = await self.repo.save_plan(
            profile_id=profile_id,
            goal=goal.value,
            duration_weeks=weeks,
            plan_json=plan_json,
        )

        plan.days = plan_days
        return plan

    async def rebuild_plan_with_more_load(
        self,
        profile_id: int,
        goal: Goal,
        preferred_from_hour: Optional[int],
        preferred_to_hour: Optional[int],
        start_date: date_type | None = None,
    ) -> WorkoutPlan:

        weeks = 8

        plan_days = build_simple_plan(
            goal=goal,
            weeks=weeks,
            preferred_from_hour=preferred_from_hour,
            preferred_to_hour=preferred_to_hour,
            meals_offset_hint="2h po jedzeniu",
            start_date=start_date,
        )


        for d in plan_days:
            d.workout += " (większe obciążenie / więcej powtórzeń)"

        plan_json = json.dumps(
            [d.model_dump(mode="json") for d in plan_days],
            ensure_ascii=False,
        )

        plan = await self.repo.save_plan(
            profile_id=profile_id,
            goal=goal.value,
            duration_weeks=weeks,
            plan_json=plan_json,
        )

        plan.days = plan_days
        return plan
