from typing import List
from datetime import datetime, timezone
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException, Response, status

from ...api.deps import require_admin
from ...container import bmi_service, planning_service, profile_repository
from ...core.domain.enums import Goal
from ...core.domain.models import (
    BmiCheckRequest,
    BmiCheckResult,
    PlanCreateResult,
    ProfileInDB,
    ProfileUpdate,
    UserRegister,
    WorkoutPlan,
)
from ...utils.bmi import calculate_bmi
from ...utils.security import hash_password
from ..deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _forbidden() -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def _not_found(detail: str = "Profil nie istnieje") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _can_access_profile(current_user: ProfileInDB, profile_id: int) -> bool:
    if current_user.email.strip().lower() == "admin@gmail.com":
        return True
    return current_user.id == profile_id



@router.post("/register", response_model=PlanCreateResult)
async def register_user(payload: UserRegister):
    email = payload.email.strip().lower()

    existing = await profile_repository.get_profile_by_email(email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    bmi = calculate_bmi(payload.weight_kg, payload.height_cm)

    profile_dict = payload.model_dump(exclude={"password"})
    profile_dict["email"] = email
    profile_dict["password_hash"] = hash_password(payload.password)
    profile_dict["bmi"] = bmi
    profile_dict["goal"] = payload.goal.value

    try:
        profile = await profile_repository.create_profile(profile_dict)
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    await bmi_service.register_initial_bmi(profile)

    plan = await planning_service.create_initial_plan(
        profile_id=profile.id,
        goal=profile.goal,
        goal_months=payload.goal_months,
        preferred_from_hour=None,
        preferred_to_hour=None,
    )

    return PlanCreateResult(profile=profile, plan=plan)


@router.put("/{profile_id}", response_model=ProfileInDB)
async def update_profile(profile_id: int, payload: ProfileUpdate, current_user=Depends(get_current_user)):
    if not _can_access_profile(current_user, profile_id):
        raise _forbidden()

    data = payload.model_dump(exclude_none=True)
    if "height_cm" in data and data["height_cm"] <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="height_cm must be > 0")

    profile = await profile_repository.get_profile(profile_id)
    if not profile:
        raise _not_found()

    return await profile_repository.update_profile(profile_id, data)


@router.post("/{profile_id}/restart-program", response_model=WorkoutPlan)
async def restart_program(profile_id: int, goal: Goal, months: int, current_user=Depends(get_current_user)):
    if not _can_access_profile(current_user, profile_id):
        raise _forbidden()

    profile = await profile_repository.get_profile(profile_id)
    if not profile:
        raise _not_found()

    now = datetime.now(timezone.utc)
    await profile_repository.update_profile(
        profile_id,
        {
            "goal": goal.value,
            "goal_months": months,
            "program_started_at": now,
            "last_bmi_check_at": now,
            "needs_bmi_update": False,
        },
    )

    plan = await planning_service.create_initial_plan(
        profile_id=profile_id,
        goal=goal,
        goal_months=months,
        preferred_from_hour=profile.preferred_from_hour,
        preferred_to_hour=profile.preferred_to_hour,
    )

    return plan


@router.get("/", response_model=List[ProfileInDB])
async def list_profiles(admin=Depends(require_admin)):
    return await profile_repository.list_profiles()


@router.get("/{profile_id}", response_model=ProfileInDB)
async def get_profile(profile_id: int, current_user=Depends(get_current_user)):
    if not _can_access_profile(current_user, profile_id):
        raise _forbidden()

    profile = await profile_repository.get_profile(profile_id)
    if not profile:
        raise _not_found()

    return profile


@router.get("/{profile_id}/plan", response_model=WorkoutPlan)
async def get_latest_plan(profile_id: int, current_user=Depends(get_current_user)):
    if not _can_access_profile(current_user, profile_id):
        raise _forbidden()

    profile = await profile_repository.get_profile(profile_id)
    if not profile:
        raise _not_found("Profile not found")

    plan = await profile_repository.get_latest_plan(profile_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    return plan


@router.post("/{profile_id}/bmi-check", response_model=BmiCheckResult)
async def bmi_check(profile_id: int, payload: BmiCheckRequest, current_user=Depends(get_current_user)):
    if not _can_access_profile(current_user, profile_id):
        raise _forbidden()

    profile = await profile_repository.get_profile(profile_id)
    if not profile:
        raise _not_found()

    return await bmi_service.check_bmi(profile, payload.weight_kg)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, admin=Depends(require_admin)):
    profile = await profile_repository.get_profile(profile_id)
    if not profile:
        raise _not_found()

    await profile_repository.soft_delete_profile(profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
