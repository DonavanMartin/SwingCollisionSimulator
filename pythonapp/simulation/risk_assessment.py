# simulation/risk_assessment.py
from .constants import (
    ANTHROPOMETRIC_DATA, DECAPITATION_THRESHOLD, CERVICAL_FRACTURE_THRESHOLD, CONCUSSION_ACCELERATION_THRESHOLD
)
from .models import RiskLevel


def assess_decapitation_risk(pressure_mpa, age):
    vertebrae_strength = ANTHROPOMETRIC_DATA[age]["vertebrae_strength_mpa"]
    threshold_min, threshold_max = DECAPITATION_THRESHOLD
    if pressure_mpa < threshold_min:
        return RiskLevel.IMPROBABLE
    elif threshold_min <= pressure_mpa <= threshold_max:
        if pressure_mpa < vertebrae_strength[0]:
            return RiskLevel.IMPROBABLE
        elif pressure_mpa <= vertebrae_strength[1]:
            return RiskLevel.POSSIBLE
        else:
            return RiskLevel.PROBABLE
    else:
        return RiskLevel.TRES_PROBABLE


def assess_cervical_fracture_risk(pressure_mpa, age):
    vertebrae_strength = ANTHROPOMETRIC_DATA[age]["vertebrae_strength_mpa"]
    threshold_min, threshold_max = CERVICAL_FRACTURE_THRESHOLD
    if pressure_mpa < threshold_min:
        return RiskLevel.IMPROBABLE
    elif threshold_min <= pressure_mpa <= threshold_max:
        if pressure_mpa < vertebrae_strength[0]:
            return RiskLevel.IMPROBABLE
        elif pressure_mpa <= vertebrae_strength[1]:
            return RiskLevel.POSSIBLE
        else:
            return RiskLevel.PROBABLE
    else:
        return RiskLevel.TRES_PROBABLE


def assess_concussion_risk(acceleration_ms2, age):
    acceleration_g = acceleration_ms2 / 9.81
    if acceleration_g < CONCUSSION_ACCELERATION_THRESHOLD * 0.8:
        return RiskLevel.IMPROBABLE
    elif acceleration_g < CONCUSSION_ACCELERATION_THRESHOLD:
        return RiskLevel.POSSIBLE
    else:
        return RiskLevel.PROBABLE