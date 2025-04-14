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
    console.log(accelerationMs2)
    const accelerationG = accelerationMs2 / 9.81;
    const threshold = age < 14 ? 50 : 80; // 50g pour enfants, 80g pour adultes
    if (accelerationG < threshold * 0.8) {
      return RiskLevel.IMPROBABLE;
    } else if (accelerationG < threshold) {
      return RiskLevel.POSSIBLE;
    } else {
      return RiskLevel.PROBABLE;
    }
  }