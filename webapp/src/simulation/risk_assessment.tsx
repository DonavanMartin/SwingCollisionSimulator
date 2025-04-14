// src/simulation/risk_assessment.tsx

import {
    ANTHROPOMETRIC_DATA,
    DECAPITATION_THRESHOLD,
    CERVICAL_FRACTURE_THRESHOLD,
    CONCUSSION_ACCELERATION_THRESHOLD,
  } from './constants';
  import { RiskLevel } from './models';
  
  export function assessDecapitationRisk(pressureMPa: number, age: number): RiskLevel {
    const vertebraeStrength = ANTHROPOMETRIC_DATA[age]?.vertebrae_strength_mpa;
    if (!vertebraeStrength) {
      throw new Error(`No anthropometric data for age ${age}`);
    }
    const [thresholdMin, thresholdMax] = DECAPITATION_THRESHOLD;
  
    if (pressureMPa < thresholdMin) {
      return RiskLevel.IMPROBABLE;
    } else if (thresholdMin <= pressureMPa && pressureMPa <= thresholdMax) {
      if (pressureMPa < vertebraeStrength[0]) {
        return RiskLevel.IMPROBABLE;
      } else if (pressureMPa <= vertebraeStrength[1]) {
        return RiskLevel.POSSIBLE;
      } else {
        return RiskLevel.PROBABLE;
      }
    } else {
      return RiskLevel.TRES_PROBABLE;
    }
  }
  
  export function assessCervicalFractureRisk(pressureMPa: number, age: number): RiskLevel {
    const vertebraeStrength = ANTHROPOMETRIC_DATA[age]?.vertebrae_strength_mpa;
    if (!vertebraeStrength) {
      throw new Error(`No anthropometric data for age ${age}`);
    }
    const [thresholdMin, thresholdMax] = CERVICAL_FRACTURE_THRESHOLD;
  
    if (pressureMPa < thresholdMin) {
      return RiskLevel.IMPROBABLE;
    } else if (thresholdMin <= pressureMPa && pressureMPa <= thresholdMax) {
      if (pressureMPa < vertebraeStrength[0]) {
        return RiskLevel.IMPROBABLE;
      } else if (pressureMPa <= vertebraeStrength[1]) {
        return RiskLevel.POSSIBLE;
      } else {
        return RiskLevel.PROBABLE;
      }
    } else {
      return RiskLevel.TRES_PROBABLE;
    }
  }
  
  export function assessConcussionRisk(accelerationMs2: number, age: number): RiskLevel {
    const accelerationG = accelerationMs2 / 9.81;
    if (accelerationG < CONCUSSION_ACCELERATION_THRESHOLD * 0.8) {
      return RiskLevel.IMPROBABLE;
    } else if (accelerationG < CONCUSSION_ACCELERATION_THRESHOLD) {
      return RiskLevel.POSSIBLE;
    } else {
      return RiskLevel.PROBABLE;
    }
  }