// src/simulation/calculations.tsx

import * as THREE from 'three';
import {
  G,
  COLLISION_TIME,
  LENGTH_SWING,
  LBS_TO_KG,
  ANTHROPOMETRIC_DATA,
  PLATFORM_WIDTH,
} from './constants';
import {
  assessDecapitationRisk,
  assessCervicalFractureRisk,
  assessConcussionRisk,
} from './risk_assessment';

export function calculateMaxAngle(height: number, length: number = LENGTH_SWING): number {
  if (height > length) {
    throw new Error('Swing height cannot exceed swing length.');
  }
  const cosTheta: number = 1 - height / length;
  return THREE.MathUtils.radToDeg(Math.acos(cosTheta));
}

export function calculateVelocity(
  thetaRad: number,
  length: number = LENGTH_SWING,
  initialVelocity: number = 0
): number {
  const h: number = length * (1 - Math.cos(thetaRad));
  const velocityFromHeight: number = Math.sqrt(2 * G * h);
  return velocityFromHeight + initialVelocity;
}

export function calculateForce(
  velocity: number,
  mass: number,
  collisionTime: number = COLLISION_TIME
): number {
  return (mass * velocity) / collisionTime;
}

export function calculateAcceleration(force: number, headMassKg: number): number {
  // Validate inputs
  if (headMassKg <= 0) {
    console.warn(`Invalid headMassKg: ${headMassKg}. Must be positive.`);
    return 0;
  }
  if (force < 0) {
    console.warn(`Negative force: ${force}. Using absolute value for acceleration.`);
    return Math.abs(force) / headMassKg;
  }
  
  return force / headMassKg;
}

export function calculateNeckDiameter(circumferenceMm: number): number {
  return circumferenceMm / Math.PI;
}

export function calculateImpactSurface(age: number, impactType: 'frontal' | 'lateral'): number {
  const data = ANTHROPOMETRIC_DATA[age];
  if (!data) {
    throw new Error(`No anthropometric data for age ${age}`);
  }
  const neckDiameterMm: number = calculateNeckDiameter(data.circumference_mm);
  const neckHeightMm: number = data.neck_height_mm;
  const impactHeightMm: number = neckHeightMm * (2 / 3);
  let surfaceMm2: number;
  if (impactType === 'frontal') {
    surfaceMm2 = neckDiameterMm * impactHeightMm;
  } else {
    surfaceMm2 = 20 * impactHeightMm;
  }
  return surfaceMm2 / 100; // Convert mm² to cm²
}

export function calculatePressure(forceNewton: number, surfaceCm2: number): number {
  if (surfaceCm2 <= 0) {
    throw new Error('Impact surface must be greater than zero.');
  }
  const surfaceMm2: number = surfaceCm2 * 100; // Convert cm² to mm²
  return forceNewton / surfaceMm2; // Pressure in N/mm² = MPa
}

export function checkPlatformCollision(
  theta1: number,
  theta2: number,
  pivot1X: number = 0,
  pivot1Y: number = LENGTH_SWING,
  pivot2X: number = 0,
  pivot2Y: number = LENGTH_SWING,
  length: number = LENGTH_SWING
): boolean {
  const x1: number = pivot1X + length * Math.sin(theta1);
  const y1: number = pivot1Y - length * Math.cos(theta1);
  const x2: number = pivot2X + length * Math.sin(theta2);
  const y2: number = pivot2Y - length * Math.cos(theta2);

  const platform1X1: number = x1 - PLATFORM_WIDTH * Math.cos(theta1);
  const platform1Y1: number = y1 - PLATFORM_WIDTH * Math.sin(theta1);
  const platform1X2: number = x1 + PLATFORM_WIDTH * Math.cos(theta1);
  const platform1Y2: number = y1 + PLATFORM_WIDTH * Math.sin(theta1);

  const platform2X1: number = x2 - PLATFORM_WIDTH * Math.cos(theta2);
  const platform2Y1: number = y2 - PLATFORM_WIDTH * Math.sin(theta2);
  const platform2X2: number = x2 + PLATFORM_WIDTH * Math.cos(theta2);
  const platform2Y2: number = y2 + PLATFORM_WIDTH * Math.sin(theta2);

  function ccw(Ax: number, Ay: number, Bx: number, By: number, Cx: number, Cy: number): boolean {
    return (Cy - Ay) * (Bx - Ax) > (By - Ay) * (Cx - Ax);
  }

  function intersect(
    x1: number,
    y1: number,
    x2: number,
    y2: number,
    x3: number,
    y3: number,
    x4: number,
    y4: number
  ): boolean {
    return (
      ccw(x1, y1, x3, y3, x4, y4) !== ccw(x2, y2, x3, y3, x4, y4) &&
      ccw(x1, y1, x2, y2, x3, y3) !== ccw(x1, y1, x2, y2, x4, y4)
    );
  }

  if (
    intersect(
      platform1X1,
      platform1Y1,
      platform1X2,
      platform1Y2,
      platform2X1,
      platform2Y1,
      platform2X2,
      platform2Y2
    )
  ) {
    return true;
  }

  const minDistance: number = Math.min(
    Math.sqrt((platform1X1 - platform2X1) ** 2 + (platform1Y1 - platform2Y1) ** 2),
    Math.sqrt((platform1X1 - platform2X2) ** 2 + (platform1Y1 - platform2Y2) ** 2),
    Math.sqrt((platform1X2 - platform2X1) ** 2 + (platform1Y2 - platform2Y1) ** 2),
    Math.sqrt((platform1X2 - platform2X2) ** 2 + (platform1Y2 - platform2Y2) ** 2)
  );

  return minDistance < 0.01;
}

export function calculatePendulumMotion(
  maxAngleRad: number,
  vInit1: number,
  vInit2: number,
  mass1Kg: number,
  mass2Kg: number,
  pivot1X: number = -2.0,
  pivot1Y: number = LENGTH_SWING,
  pivot2X: number = 2.0,
  pivot2Y: number = LENGTH_SWING,
  dt: number = 1.0 / 60.0
): { theta1: number; theta2: number; theta1Dot: number; theta2Dot: number } {
  const dampingCoeff: number = 0.02;
  let theta1: number = maxAngleRad;
  let theta2: number = -maxAngleRad;
  let theta1Dot: number = vInit1 / LENGTH_SWING || 0;
  let theta2Dot: number = vInit2 / LENGTH_SWING || 0;
  let t: number = 0;

  while (true) {
    const accel1: number =
      -(G / LENGTH_SWING) * Math.sin(theta1) - (dampingCoeff / mass1Kg) * theta1Dot;
    const accel2: number =
      -(G / LENGTH_SWING) * Math.sin(theta2) - (dampingCoeff / mass2Kg) * theta2Dot;

    theta1Dot += accel1 * dt;
    theta2Dot += accel2 * dt;
    theta1 += theta1Dot * dt;
    theta2 += theta2Dot * dt;
    t += dt;

    if (
      checkPlatformCollision(theta1, theta2, pivot1X, pivot1Y, pivot2X, pivot2Y, LENGTH_SWING)
    ) {
      return { theta1, theta2, theta1Dot, theta2Dot };
    }

    if (t > 10) {
      return { theta1, theta2, theta1Dot, theta2Dot };
    }
  }
}

export function calculateCollision(
  theta1Dot: number,
  theta2Dot: number,
  mass1Kg: number,
  mass2Kg: number,
  e: number = 0.5
): { v1Prime: number; v2Prime: number } {
  const v1: number = theta1Dot * LENGTH_SWING;
  const v2: number = theta2Dot * LENGTH_SWING;
  const v1Prime: number =
    (mass1Kg * v1 + mass2Kg * v2 - mass2Kg * e * (v2 - v1)) / (mass1Kg + mass2Kg);
  const v2Prime: number =
    (mass1Kg * v1 + mass2Kg * v2 + mass1Kg * e * (v2 - v1)) / (mass1Kg + mass2Kg);
  return { v1Prime: v1Prime / LENGTH_SWING, v2Prime: v2Prime / LENGTH_SWING };
}