from datetime import datetime, timezone, date

from ..domain.models import BmiCheckResult, ProfileInDB
from ..repositories.profile_repository import AbstractProfileRepository
from ...utils.bmi import calculate_bmi, is_better_bmi
from .planning_service import PlanningService


MSG_FIRST = "To pierwszy zapis BMI."
MSG_OK = "Progres jest OK — kontynuujemy bez zmian."
MSG_NO_PROGRESS = "Brak progresu — aktualizuję plan od dzisiaj i zwiększam obciążenie."


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _update_profile(profile: ProfileInDB, **updates) -> ProfileInDB:

    if hasattr(profile, "model_copy"):
        return profile.model_copy(update=updates)

    data = profile.model_dump() if hasattr(profile, "model_dump") else dict(profile)
    data.update(updates)
    return ProfileInDB(**data)


class BMIService:
    def __init__(self, repo: AbstractProfileRepository, planning_service: PlanningService):
        self.repo = repo
        self.planning_service = planning_service

    async def register_initial_bmi(self, profile: ProfileInDB) -> None:
        await self.repo.add_bmi_record(
            profile_id=profile.id,
            weight_kg=profile.weight_kg,
            bmi=profile.bmi,
        )

        now = _utc_now()
        await self.repo.set_program_started(profile.id, now)
        await self.repo.update_last_bmi_check(profile.id, now)

    async def check_bmi(self, profile: ProfileInDB, new_weight_kg: float) -> BmiCheckResult:
        new_bmi = calculate_bmi(new_weight_kg, profile.height_cm)
        latest_record = await self.repo.get_latest_bmi_record(profile.id)

        # zapis do historii
        await self.repo.add_bmi_record(
            profile_id=profile.id,
            weight_kg=new_weight_kg,
            bmi=new_bmi,
        )

        now = _utc_now()

        # aktualizacja profilu (waga, BMI, czas pomiaru)
        await self.repo.update_weight_and_bmi(
            profile_id=profile.id,
            weight_kg=new_weight_kg,
            bmi=new_bmi,
            check_time=now,
        )

        plan_changed = False
        message = ""

        if latest_record is None:
            message = MSG_FIRST
        else:
            goal_value = getattr(profile.goal, "value", profile.goal)
            progress_ok = is_better_bmi(latest_record.bmi, new_bmi, goal_value)

            if progress_ok:
                message = MSG_OK
            else:
                message = MSG_NO_PROGRESS
                plan_changed = True

                await self.planning_service.rebuild_plan_with_more_load(
                    profile_id=profile.id,
                    goal=profile.goal,
                    preferred_from_hour=profile.preferred_from_hour,
                    preferred_to_hour=profile.preferred_to_hour,
                    start_date=date.today(),
                )

        updated_profile = _update_profile(
            profile,
            weight_kg=new_weight_kg,
            bmi=new_bmi,
            last_bmi_check_at=now,
            needs_bmi_update=False,
        )

        return BmiCheckResult(
            profile=updated_profile,
            latest_bmi=new_bmi,
            message=message,
            plan_changed=plan_changed,
        )
