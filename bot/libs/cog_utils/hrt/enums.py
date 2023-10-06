from enum import Enum


class HRTType(Enum):
    Estradiol = "Estradiol"
    Progesterone = "Progesterone"
    Testosterone = "Testosterone"


class HRTUnit(Enum):
    POML_L = "pmol/L"
    PG_ML = "pg/mL"
    NMOL_L = "nmol/L"
    NG_DL = "ng/dL"
    NG_ML = "ng/mL"
