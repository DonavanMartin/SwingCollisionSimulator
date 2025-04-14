import * as THREE from 'three';
import {
  calculateCollision,
  calculateForce,
  calculatePressure,
  calculateImpactSurface,
  calculateAcceleration,
  checkPlatformCollision
} from '../../simulation/calculations';
import { getRiskLevelDisplayName } from '../../simulation/models';
import {
  assessDecapitationRisk,
  assessCervicalFractureRisk,
  assessConcussionRisk,
} from '../../simulation/risk_assessment';
import { Ball, SimulationParams, CollisionResults } from './types';
import { G, LENGTH_SWING, ANTHROPOMETRIC_DATA } from '../../simulation/constants';

export const updatePhysicsAndCollision = (
  ball1: Ball,
  ball2: Ball,
  params: SimulationParams,
  collisionOccurredRef: React.MutableRefObject<boolean>,
  flashTimeRef: React.MutableRefObject<number>,
  currentTime: number,
  onCollision: (results: CollisionResults) => void,
  setIsRunning: (running: boolean) => void
): { finalV1: number; finalV2: number } => {
  let finalV1 = 0;
  let finalV2 = 0;

  const dt = 1 / 60;
  const dampingCoeff = 0.02;
  const e = 0.5;

  // Physics update
  const accel1 = -(G / LENGTH_SWING) * Math.sin(ball1.theta) - (dampingCoeff / ball1.mass) * ball1.velocity;
  const accel2 = -(G / LENGTH_SWING) * Math.sin(ball2.theta) - (dampingCoeff / ball2.mass) * ball2.velocity;
  ball1.velocity += accel1 * dt;
  ball2.velocity += accel2 * dt;
  ball1.theta += ball1.velocity * dt;
  ball2.theta += ball2.velocity * dt; // Fixed: Use velocity, not theta

  // Update positions
  const x1 = -2.0 + LENGTH_SWING * Math.sin(ball1.theta);
  const y1 = LENGTH_SWING - LENGTH_SWING * Math.cos(ball1.theta);
  const x2 = 2.0 + LENGTH_SWING * Math.sin(ball2.theta);
  const y2 = LENGTH_SWING - LENGTH_SWING * Math.cos(ball2.theta);

  // Update ropes
  const rope1Pos = ball1.rope.geometry.attributes.position.array as Float32Array;
  rope1Pos.set([-2.0, LENGTH_SWING, 0, x1, y1, 0]);
  ball1.rope.geometry.attributes.position.needsUpdate = true;

  const rope2Pos = ball2.rope.geometry.attributes.position.array as Float32Array;
  rope2Pos.set([2.0, LENGTH_SWING, 0, x2, y2, 0]);
  ball2.rope.geometry.attributes.position.needsUpdate = true;

  // Update platforms
  ball1.platform.position.set(x1, y1, 0);
  ball1.platform.rotation.z = ball1.theta;
  ball2.platform.position.set(x2, y2, 0);
  ball2.platform.rotation.z = ball2.theta;

  // Collision
  if (!collisionOccurredRef.current && checkPlatformCollision(
    ball1.theta,
    ball2.theta,
    -2.0,
    LENGTH_SWING,
    2.0,
    LENGTH_SWING,
    LENGTH_SWING
  )) {
    const v1 = ball1.velocity * LENGTH_SWING;
    const v2 = ball2.velocity * LENGTH_SWING;
    finalV1 = v1;
    finalV2 = v2;
    const { v1Prime, v2Prime } = calculateCollision(
      ball1.velocity,
      ball2.velocity,
      ball1.mass,
      ball2.mass,
      e
    );
    ball1.velocity = v1Prime / LENGTH_SWING;
    ball2.velocity = v2Prime / LENGTH_SWING;
    collisionOccurredRef.current = true;
    flashTimeRef.current = currentTime;

    // Compute results
    const velocity1 = v1;
    const velocity2 = v2;
    const relativeVelocity = Math.abs(velocity1) + Math.abs(velocity2);
    const reducedMass = (ball1.mass * ball2.mass) / (ball1.mass + ball2.mass) || ball1.mass;
    const force = calculateForce(relativeVelocity, reducedMass);
    const surfaceCm2 = calculateImpactSurface(params.age, params.impactType === 'frontal' ? 'frontal' : 'lateral');
    const pressureMPa = calculatePressure(force, surfaceCm2);
    const headMass = ANTHROPOMETRIC_DATA[params.age]?.head_mass_kg || 3.5;
    const accelerationMs2 = calculateAcceleration(force, headMass);

    const results: CollisionResults = {
      age: params.age,
      maxHeight: params.maxHeight,
      mass1Lbs: params.mass1Lbs,
      mass1Kg: ball1.mass,
      mass2Lbs: params.mass2Lbs,
      mass2Kg: ball2.mass,
      vInit1: params.vInit1,
      vInit2: params.vInit2,
      angleHorizontal1: THREE.MathUtils.radToDeg(ball1.theta),
      angleHorizontal2: THREE.MathUtils.radToDeg(ball2.theta),
      impactType: params.impactType,
      velocity1,
      velocity2,
      relativeVelocity,
      force,
      surfaceCm2,
      pressureMPa,
      decapitationRisk: getRiskLevelDisplayName(assessDecapitationRisk(pressureMPa, params.age)),
      cervicalFractureRisk: getRiskLevelDisplayName(assessCervicalFractureRisk(pressureMPa, params.age)),
      concussionRisk: getRiskLevelDisplayName(assessConcussionRisk(accelerationMs2, params.age)),
    };

    onCollision(results);
  }

  // Flash effect
  if (collisionOccurredRef.current && (currentTime - flashTimeRef.current) < 100) {
    const flashColor = params.impactType === 'frontal' ? 0xff0000 : 0xff8000;
    ball1.platformMaterial.color.set(flashColor);
    ball2.platformMaterial.color.set(flashColor);
  } else {
    ball1.platformMaterial.color.set(0x0000ff);
    ball2.platformMaterial.color.set(0xff0000);
    if (collisionOccurredRef.current) {
      setIsRunning(false);
    }
  }

  return { finalV1, finalV2 };
};