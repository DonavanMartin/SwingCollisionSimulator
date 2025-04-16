import * as THREE from 'three';

export interface SimulationParams {
  age: number;
  collisionTime: number;
  maxHeight: number;
  mass1Lbs: number;
  mass2Lbs: number;
  vInit1: number;
  vInit2: number;
  impactType: 'frontal' | 'concentré';
}

export interface Ball {
  rope: THREE.Line;
  platform: THREE.Mesh;
  pivot: THREE.Mesh;
  theta: number;
  mass: number;
  velocity: number; // Angular velocity (rad/s)
  platformMaterial: THREE.MeshBasicMaterial;
}

export interface CollisionResults {
  age: number;
  maxHeight: number;
  mass1Lbs: number;
  mass1Kg: number;
  mass2Lbs: number;
  mass2Kg: number;
  vInit1: number;
  vInit2: number;
  angleHorizontal1: number;
  angleHorizontal2: number;
  impactType: string;
  velocity1: number;
  velocity2: number;
  relativeVelocity: number;
  force: number;
  surfaceCm2: number;
  pressureMPa: number;
  decapitationRisk: string;
  cervicalFractureRisk: string;
  concussionRisk: string;
  hic:number;
  peakAcceleration:number;
  accelerationMs2:number;
  isSafe:boolean;
}

export interface SimulationCanvasProps {
  params: SimulationParams;
  running: boolean;
  onCollision: (results: CollisionResults) => void;
  setIsRunning: (running: boolean) => void;
}