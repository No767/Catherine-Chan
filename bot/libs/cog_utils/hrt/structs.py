from typing import TypedDict


class ProgResults(TypedDict):
    nmol_l_output: float
    ng_ml_output: float


class TResults(TypedDict):
    nmol_l_output: float
    ng_dl_output: float


class EResults(TypedDict):
    pmol_l_output: float
    pg_ml_output: float
