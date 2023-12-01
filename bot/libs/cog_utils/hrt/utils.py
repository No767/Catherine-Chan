from .structs import EResults, ProgResults, ProlacResults, TResults

ESTRADIOL = 3.6712337
PROGESTERONE = 3.18
PROLACTIN = 21.2765957446809
TESTOSTERONE = 0.0346703

# Current measurements:
# E: pmol/L, pg/mL
# Prog: nmol/L, ng/dL (convert to ng/mL, which is ng/dl * 0.01 = ng/mL)
# T: nmol/L, ng/dL


def calc_e(amount: int, unit: str) -> EResults:
    output = EResults(pmol_l=0.0, pg_ml=0.0)
    output[unit] = amount

    if unit == "pmol_l":
        output["pg_ml"] = amount / ESTRADIOL
    elif unit == "pg_ml":
        output["pmol_l"] = amount * ESTRADIOL

    return output


def calc_prolac(amount: int, unit: str) -> ProlacResults:
    output = ProlacResults(miu_l=0.0, ng_ml=0.0)

    output[unit] = amount

    if unit == "miu_l":
        output["ng_ml"] = amount / PROLACTIN
    elif unit == "ng_ml":
        output["miu_l"] = amount * PROLACTIN

    return output


def calc_t(amount: int, unit: str) -> TResults:
    output = TResults(nmol_l=0.0, ng_dl=0.0)
    output[unit] = amount

    if unit == "nmol_l":
        output["ng_dl"] = amount / TESTOSTERONE
    elif unit == "ng_dl":
        output["nmol_l"] = amount * TESTOSTERONE

    return output


def calc_prog(amount: int, unit: str) -> ProgResults:
    output = ProgResults(nmol_l=0.0, ng_ml=0.0)
    output[unit] = amount

    if unit == "nmol_l":
        # Since apparently Triona's code converts ng/dL to ng/mL, the conversion rate is basically ng/dl * 0.01 = ng/mL
        output["ng_ml"] = amount / PROGESTERONE
    elif unit == "ng_ml":
        output["nmol_l"] = amount * PROGESTERONE

    return output
