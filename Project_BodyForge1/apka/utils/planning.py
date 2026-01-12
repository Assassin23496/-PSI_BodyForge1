from datetime import date as date_type, timedelta
from typing import List, Optional
import random

from ..core.domain.enums import Goal
from ..core.domain.models import PlanDay


LOSE_WEIGHT_WORKOUTS = [
    "Szybki marsz 30–40 min + core (brzuch/plecy)",
    "HIIT 15–20 min + rozciąganie",
    "Trening obwodowy (własne ciężary) 25–35 min",
    "Lekki bieg/rower 30 min + mobility",
]

GAIN_MUSCLE_WORKOUTS = [
    "Góra ciała (klata + barki + triceps)",
    "Dół ciała (nogi + pośladki)",
    "Plecy + biceps",
    "Full body (umiarkowanie)",
]

RECOMP_WORKOUTS = [
    "Siła (full body) + 15 min cardio",
    "Obwód (siła + kondycja)",
    "Siła góra/dół (lżej) + spacer",
]

FOOD_TIPS = {
    Goal.lose_weight: "Więcej warzyw, białko w każdym posiłku, mniej słodyczy i napojów słodzonych.",
    Goal.gain_muscle: "Więcej kalorii + dużo białka (1.6–2.2 g/kg), węgle wokół treningu.",
    Goal.recomposition: "Zbilansowane posiłki, białko regularnie, kontrola słodyczy i podjadania.",
}


def _preferred_hours(from_hour: Optional[int], to_hour: Optional[int]) -> str:

    if from_hour is None or to_hour is None:
        return "10:00–18:00"
    return f"{from_hour:02d}:00–{to_hour:02d}:00"


def build_simple_plan(
    goal: Goal,
    weeks: int,
    preferred_from_hour: Optional[int] = None,
    preferred_to_hour: Optional[int] = None,
    meals_offset_hint: str = "2h po jedzeniu",
    start_date: Optional[date_type] = None,
) -> List[PlanDay]:

    if weeks <= 0:
        return []

    # Ustalenie puli treningów.
    if goal == Goal.lose_weight:
        workouts_pool = LOSE_WEIGHT_WORKOUTS
    elif goal == Goal.gain_muscle:
        workouts_pool = GAIN_MUSCLE_WORKOUTS
    else:
        workouts_pool = RECOMP_WORKOUTS

    if not workouts_pool:
        return []

    start = start_date if start_date is not None else date_type.today()
    total_days = weeks * 7
    hours = _preferred_hours(preferred_from_hour, preferred_to_hour)
    food_tip = FOOD_TIPS.get(goal, "")

    note = f"Najlepiej ćwiczyć w oknie {hours}, ~{meals_offset_hint}."

    days: List[PlanDay] = []
    for day_idx in range(total_days):
        current_date = start + timedelta(days=day_idx)
        workout = random.choice(workouts_pool)

        days.append(
            PlanDay(
                date=current_date,
                workout=workout,
                food_tips=food_tip,
                preferred_hours=hours,
                note=note,
            )
        )

    return days
