from typing import TypedDict


class ProgResults(TypedDict):
    nmol_l: float
    ng_ml: float


class TResults(TypedDict):
    nmol_l: float
    ng_dl: float


class EResults(TypedDict):
    pmol_l: float
    pg_ml: float


class ProlacResults(TypedDict):
    miu_l: float
    ng_ml: float
