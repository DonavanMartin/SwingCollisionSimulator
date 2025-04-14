// src/simulation/constants.tsx

import { RiskLevel } from './models';

// Physical constants
export const G: number = 9.81; // Acceleration due to gravity (m/s²)
export const COLLISION_TIME: number = 0.01; // 10 ms, typique pour collisions rigides // Plage : 5–20 ms (0.005–0.020 s) selon la rigidité.
// TODO: export const COLLISION_TIME_MIN: number = 0.005; // 5 ms pour impacts rigides
// TODO:export const COLLISION_TIME_MAX: number = 0.05; // 50 ms pour impacts amortis
export const LENGTH_SWING: number = 2.25; // Swing length (m)
export const LBS_TO_KG: number = 0.453592; // Conversion factor (lbs to kg)
export const FLASH_TIME: number = 1; // Flash time (s)
export const REEL_PLATFORM_WIDTH: number = 1; // Real platform width (m)
export const PLATFORM_WIDTH: number = REEL_PLATFORM_WIDTH / 2; // Effective platform width (m)

// CSAZ614-20 safety thresholds
export const HIC_THRESHOLD: number = 1000; // Maximum Head Injury Criterion for critical falls, per CSAZ614-20
export const PEAK_ACCELERATION_THRESHOLD: number = 200 * G; // Maximum peak acceleration for critical falls (200 g in m/s²), per CSAZ614-20

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
export const DECAPITATION_THRESHOLD: [number, number] = [5, 10]; // MPa - Extreme stress on neck leading to catastrophic failure
export const CERVICAL_FRACTURE_THRESHOLD: [number, number] = [3, 6]; // MPa - Stress causing cervical spine fracture
export const CONCUSSION_ACCELERATION_THRESHOLD: number = 784; // m/s² (80g ≈ 784 m/s²) - Acceleration causing brain injury risk

// Default simulation parameters
export const DEFAULT_AGE: number = 3;
export const DEFAULT_MAXHEIGHT: number = 1.5;
export const DEFAULT_MASS1LBS: number = 40;
export const DEFAULT_MASS2LBS: number = 40;
export const DEFAULT_VINIT1: number = 0;
export const DEFAULT_VINIT2: number = 0;
export const DEFAULT_IMPACTTYPE: 'frontal' | 'concentré' = 'concentré';

// HIC calculation function
// Calculates HIC15 (maximized over 15 ms windows) based on an acceleration profile
// Parameters:
// - accelerationProfile: Array of { time_s: number, acceleration_ms2: number } representing head acceleration over time
// - maxWindowMs: Maximum time window for HIC calculation (default 15 ms for HIC15)
// Returns: HIC value, or -1 if input is invalid
export function calculateHIC(
  accelerationProfile: { time_s: number; acceleration_ms2: number }[],
  maxWindowMs: number = 15
): number {
  // Input validation
  if (!accelerationProfile || accelerationProfile.length < 2) {
    console.warn('Invalid acceleration profile: must have at least 2 points');
    return -1;
  }

  const maxWindowS = maxWindowMs / 1000; // Convert ms to seconds
  let maxHIC = 0;

  // Sort and validate profile
  const sortedProfile = [...accelerationProfile].sort((a, b) => a.time_s - b.time_s);
  if (sortedProfile[0].time_s === sortedProfile[sortedProfile.length - 1].time_s) {
    console.warn('All timestamps are identical');
    return -1;
  }

  // Interpolate profile to ensure points within maxWindowS
  const interpolatedProfile: { time_s: number; acceleration_ms2: number }[] = [];
  const minTime = sortedProfile[0].time_s;
  const maxTime = sortedProfile[sortedProfile.length - 1].time_s;
  const step = maxWindowS / 2; // Sample at half the window for resolution

  for (let t = minTime; t <= maxTime; t += step) {
    const accel = interpolateAcceleration(sortedProfile, t);
    interpolatedProfile.push({ time_s: t, acceleration_ms2: accel });
  }

  // Ensure at least two points
  if (interpolatedProfile.length < 2) {
    console.warn('Interpolated profile too short');
    return -1;
  }

  // Iterate over possible start times
  for (let i = 0; i < interpolatedProfile.length - 1; i++) {
    const t1 = interpolatedProfile[i].time_s;

    // Find end times within maxWindowS
    for (let j = i + 1; j < interpolatedProfile.length; j++) {
      const t2 = interpolatedProfile[j].time_s;
      const dt = t2 - t1;

      // Skip invalid or out-of-window intervals
      if (dt <= 0 || dt > maxWindowS) {
        continue;
      }

      // Calculate integral using trapezoidal rule over [t1, t2]
      let integral = 0;
      for (let k = i; k < j && k + 1 < interpolatedProfile.length; k++) {
        const a1 = interpolatedProfile[k].acceleration_ms2;
        const a2 = interpolatedProfile[k + 1].acceleration_ms2;
        const dt_k = interpolatedProfile[k + 1].time_s - interpolatedProfile[k].time_s;

        // Skip if dt_k is invalid
        if (dt_k <= 0) {
          console.warn(`Invalid time step at index ${k}: dt_k = ${dt_k}`);
          continue;
        }

        integral += (a1 + a2) * dt_k / 2; // Trapezoidal rule
      }

      // Compute average acceleration
      const avgAcceleration = dt > 0 ? integral / dt : 0;

      // Calculate HIC for this window
      if (avgAcceleration > 0) {
        const hic = Math.pow(avgAcceleration / G, 2.5) * dt;
        maxHIC = Math.max(maxHIC, hic);
        // console.log(`Window [${t1}, ${t2}]: avgAccel = ${avgAcceleration.toFixed(2)}, HIC = ${hic.toFixed(2)}`);
      }
    }
  }

  // If no valid HIC, use full profile as fallback (e.g., for collision time)
  if (maxHIC === 0 && sortedProfile.length >= 2) {
    console.warn('No valid HIC within 15ms window; using full profile as fallback');
    const t1 = sortedProfile[0].time_s;
    const t2 = sortedProfile[sortedProfile.length - 1].time_s;
    const dt = t2 - t1;

    if (dt > 0 && dt <= COLLISION_TIME) {
      let integral = 0;
      for (let k = 0; k < sortedProfile.length - 1; k++) {
        const a1 = sortedProfile[k].acceleration_ms2;
        const a2 = sortedProfile[k + 1].acceleration_ms2;
        const dt_k = sortedProfile[k + 1].time_s - sortedProfile[k].time_s;
        if (dt_k > 0) {
          integral += (a1 + a2) * dt_k / 2;
        }
      }

      const avgAcceleration = integral / dt;
      if (avgAcceleration > 0) {
        maxHIC = Math.pow(avgAcceleration / G, 2.5) * dt;
      }
    }
  }

  if (maxHIC === 0) {
    console.warn('HIC calculation returned 0. Possible issues: zero accelerations or no valid time windows.', {
      originalProfile: accelerationProfile,
      interpolatedProfile,
      maxWindowS,
    });
  }

  return maxHIC;
}

// Linear interpolation helper
function interpolateAcceleration(
  profile: { time_s: number; acceleration_ms2: number }[],
  targetTime: number
): number {
  if (profile.length === 0) return 0;
  if (profile.length === 1) return profile[0].acceleration_ms2;

  for (let i = 0; i < profile.length - 1; i++) {
    const t1 = profile[i].time_s;
    const t2 = profile[i + 1].time_s;
    if (targetTime >= t1 && targetTime <= t2) {
      const a1 = profile[i].acceleration_ms2;
      const a2 = profile[i + 1].acceleration_ms2;
      const fraction = (targetTime - t1) / (t2 - t1);
      return a1 + fraction * (a2 - a1);
    }
  }

  // Extrapolate if outside bounds
  if (targetTime < profile[0].time_s) return profile[0].acceleration_ms2;
  return profile[profile.length - 1].acceleration_ms2;
}
// Possible risks associated with swing collision simulation
// These risks are derived from the simulation parameters, anthropometric data, and CSAZ614-20 safety thresholds.
export const RISKS: { name: string; description: string; riskLevel: string; causes: string[]; mitigation: string[] }[] = [
  {
    name: 'Concussion',
    description:
      'A traumatic brain injury caused by excessive head acceleration during a swing collision, potentially leading to symptoms like dizziness, nausea, or loss of consciousness.',
    riskLevel: 'High',
    causes: [
      `Head acceleration exceeding ${CONCUSSION_ACCELERATION_THRESHOLD} m/s² (80g) or HIC exceeding ${HIC_THRESHOLD} during collision.`,
      'High swing velocities (vInit1, vInit2 > 0) increasing impact force.',
      'Large maxHeight (> 1.5 m) causing greater swing amplitude and collision energy.',
      "Concentré impact type focusing force on a smaller area, increasing localized acceleration.",
      `Peak acceleration exceeding ${PEAK_ACCELERATION_THRESHOLD.toFixed(0)} m/s² (200g) in critical falls.`,
    ],
    mitigation: [
      `Limit maxHeight to ${DEFAULT_MAXHEIGHT} m or less for children aged 1–5 to reduce swing amplitude.`,
      'Ensure vInit1 and vInit2 are close to 0 for realistic playground scenarios.',
      'Use frontal impact type to distribute collision forces over a larger area.',
      `Install impact-absorbing surfaces meeting CSAZ614-20 requirements (HIC ≤ ${HIC_THRESHOLD}, peak acceleration < ${PEAK_ACCELERATION_THRESHOLD.toFixed(0)} m/s²).`,
      'Space swings to prevent collisions, per CSAZ614-20 clearance guidelines.',
    ],
  },
  {
    name: 'Cervical Fracture',
    description:
      'Fracture of the cervical spine due to excessive stress on the neck vertebrae, potentially causing severe injury or paralysis.',
    riskLevel: 'Critical',
    causes: [
      `Neck stress exceeding ${CERVICAL_FRACTURE_THRESHOLD[0]}–${CERVICAL_FRACTURE_THRESHOLD[1]} MPa during collision.`,
      'High mass (mass1Lbs, mass2Lbs > 120 lbs) increasing collision force.',
      'Younger age (1–3 years) with lower vertebrae strength (see ANTHROPOMETRIC_DATA).',
      'Sudden deceleration from concentrated impact amplifying neck strain.',
    ],
    mitigation: [
      `Restrict mass1Lbs and mass2Lbs to realistic child weights (e.g., 50–100 lbs for ages 1–5).`,
      `Limit maxHeight and velocities to reduce collision forces below cervical fracture thresholds.`,
      'Design swings with flexible seats to absorb impact energy.',
      'Ensure regular inspection of swing chains and seats per CSAZ614-20 to prevent unexpected failures.',
      'Use age-appropriate swing designs with lower heights for younger children.',
    ],
  },
  {
    name: 'Decapitation (Extreme Case)',
    description:
      'An extreme and rare injury involving catastrophic neck failure, included for worst-case analysis in high-force collisions.',
    riskLevel: 'Catastrophic',
    causes: [
      `Neck stress exceeding ${DECAPITATION_THRESHOLD[0]}–${DECAPITATION_THRESHOLD[1]} MPa, far beyond normal playground scenarios.`,
      'Extremely high swing velocities or masses (e.g., vInit > 5 m/s, mass > 200 lbs).',
      'Concentré impact type delivering force to a critical neck area.',
      'Improper swing design allowing excessive motion or entanglement.',
    ],
    mitigation: [
      `Enforce strict parameter limits: maxHeight ≤ ${LENGTH_SWING} m, vInit1/vInit2 ≤ 2 m/s, mass1Lbs/mass2Lbs ≤ 150 lbs.`,
      'Use CSAZ614-20-compliant swing spacing and anchorage to prevent extreme collisions.',
      'Implement safety harnesses or restraints for high-risk swing designs (not typical for playgrounds).',
      'Conduct regular maintenance to ensure swing integrity, per CSAZ614-20 Clause 13.',
    ],
  },
  {
    name: 'Head and Neck Entrapment',
    description:
      'Risk of a child’s head or neck becoming trapped in swing components or between swings, potentially causing strangulation or injury.',
    riskLevel: 'Moderate',
    causes: [
      'Improper swing spacing allowing collisions or entanglement.',
      'Openings in swing seats or chains between 89 mm and 230 mm, per CSAZ614-20 entrapment tests.',
      'Smaller neck dimensions in younger children (e.g., neck_height_mm < 60 mm for ages 1–3).',
    ],
    mitigation: [
      'Follow CSAZ614-20 Clause 10 for entrapment-free design (openings < 89 mm or > 230 mm).',
      'Ensure swings are spaced per CSAZ614-20 guidelines (e.g., 600 mm minimum between swings).',
      'Use smooth, rounded swing components to prevent catching on clothing or body parts.',
      'Supervise young children (ages 1–3) to prevent misuse of swings.',
    ],
  },
  {
    name: 'Impact Trauma (General)',
    description:
      'Bruising, lacerations, or fractures from direct impact between swings or with other playground elements, exacerbated by high HIC or acceleration.',
    riskLevel: 'Moderate',
    causes: [
      `Collision resulting in HIC > ${HIC_THRESHOLD} or peak acceleration > ${PEAK_ACCELERATION_THRESHOLD.toFixed(0)} m/s².`,
      'High collision energy from large maxHeight, mass, or velocity.',
      'Concentré impact type increasing localized pressure on the body.',
      'Collision between swings due to inadequate spacing or high initial velocities.',
    ],
    mitigation: [
      `Cap maxHeight at ${DEFAULT_MAXHEIGHT} m and velocities at ${DEFAULT_VINIT1} m/s for safe operation.`,
      'Use padded swing seats to reduce impact severity.',
      `Install CSAZ614-20-compliant surfacing to cushion falls (HIC ≤ ${HIC_THRESHOLD}, peak acceleration < ${PEAK_ACCELERATION_THRESHOLD.toFixed(0)} m/s²).`,
      'Design playground layouts to minimize swing-to-swing or swing-to-structure collisions.',
    ],
  },
];