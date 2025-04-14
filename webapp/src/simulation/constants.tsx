// src/simulation/constants.tsx

import { RiskLevel } from './models';

// Physical constants
export const G: number = 9.81; // Acceleration due to gravity (m/s²)
export const COLLISION_TIME: number = 0.05; // Collision duration (s)
export const LENGTH_SWING: number = 2.25; // Swing length (m)
export const LBS_TO_KG: number = 0.453592; // Conversion factor (lbs to kg)
export const FLASH_TIME: number = 1; // Flash time (s)
export const REEL_PLATFORM_WIDTH: number = 1; // Real platform width (m)
export const PLATFORM_WIDTH: number = REEL_PLATFORM_WIDTH / 2; // Effective platform width (m)

// Anthropometric data interface
interface AnthropometricData {
  circumference_mm: number;
  neck_height_mm: number;
  vertebrae_strength_mpa: [number, number]; // Tuple for min/max strength (MPa)
  head_mass_kg: number;
}

// Anthropometric data by age
export const ANTHROPOMETRIC_DATA: { [age: number]: AnthropometricData } = {
  1: {
    circumference_mm: 200,
    neck_height_mm: 45,
    vertebrae_strength_mpa: [4, 8],
    head_mass_kg: 3.0,
  },
  2: {
    circumference_mm: 210,
    neck_height_mm: 50,
    vertebrae_strength_mpa: [4.5, 8.5],
    head_mass_kg: 3.2,
  },
  3: {
    circumference_mm: 225,
    neck_height_mm: 60,
    vertebrae_strength_mpa: [5, 9],
    head_mass_kg: 3.5,
  },
  4: {
    circumference_mm: 235,
    neck_height_mm: 65,
    vertebrae_strength_mpa: [5, 9.5],
    head_mass_kg: 3.7,
  },
  5: {
    circumference_mm: 245,
    neck_height_mm: 70,
    vertebrae_strength_mpa: [5, 10],
    head_mass_kg: 4.0,
  },
};

// Risk thresholds
export const DECAPITATION_THRESHOLD: [number, number] = [5, 10]; // MPa
export const CERVICAL_FRACTURE_THRESHOLD: [number, number] = [3, 6]; // MPa
export const CONCUSSION_ACCELERATION_THRESHOLD: number = 784; // m/s² (80g ≈ 784 m/s²)