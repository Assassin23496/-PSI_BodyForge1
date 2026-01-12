from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class Goal(str, Enum):
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
    recomposition = "recomposition"
