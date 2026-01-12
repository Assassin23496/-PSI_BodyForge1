def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    if height_m <= 0:
        raise ValueError("Wzrost musi być dodatni")
    return round(weight_kg / (height_m ** 2), 2)


def is_better_bmi(old_bmi: float, new_bmi: float, goal: str) -> bool:
    """
    Sprawdza, czy BMI idzie w dobrą stronę:
    - 'lose_weight' -> BMI powinno spadać
    - 'gain_muscle' lub 'recomposition' -> BMI może lekko rosnąć albo zostać
    """
    if goal == "lose_weight":
        return new_bmi < old_bmi
    elif goal in {"gain_muscle", "recomposition"}:
        # bardzo proste – jeśli nie poszło drastycznie w górę, uznajemy za ok
        return new_bmi <= old_bmi + 0.5
    return False
