import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import {
  calculatePendulumMotion,
  calculateCollision,
  calculateVelocity,
  calculateForce,
  calculatePressure,
  calculateImpactSurface,
  calculateAcceleration,
  calculateMaxAngle,
} from '../simulation/calculations';
import { getRiskLevelDisplayName } from '../simulation/models';
import { LBS_TO_KG, LENGTH_SWING, ANTHROPOMETRIC_DATA } from '../simulation/constants';
import { assessDecapitationRisk, assessCervicalFractureRisk, assessConcussionRisk } from '../simulation/risk_assessment';

interface SimulationParams {
  age: number;
  maxHeight: number;
  mass1Lbs: number;
  mass2Lbs: number;
  vInit1: number;
  vInit2: number;
  impactType: 'frontal' | 'concentré';
}

interface Ball {
  theta: number;
  mass: number;
  velocity: number; // Angular velocity (rad/s)
  mesh: THREE.Mesh;
}

interface CollisionResults {
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
}

interface SimulationCanvasProps {
  params: SimulationParams;
  running: boolean;
  onCollision: (results: CollisionResults) => void;
}

const SimulationCanvas: React.FC<SimulationCanvasProps> = ({ params, running, onCollision }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.OrthographicCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const ball1Ref = useRef<Ball | null>(null);
  const ball2Ref = useRef<Ball | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const isMountedRef = useRef<boolean>(true);

  useEffect(() => {
    isMountedRef.current = true;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    const textureLoader = new THREE.TextureLoader();
    textureLoader.load('/background.jpg', (texture) => {
      if (isMountedRef.current && sceneRef.current) {
        sceneRef.current.background = texture;
      }
    }, undefined, (error) => {
      console.error('Error loading background texture:', error);
    });

    // Camera
    const aspect = 800 / 600;
    const frustumSize = 600;
    const camera = new THREE.OrthographicCamera(
      (-frustumSize * aspect) / 2,
      (frustumSize * aspect) / 2,
      frustumSize / 2,
      -frustumSize / 2,
      0.1,
      1000
    );
    camera.position.set(0, 0, 100);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(800, 600);
    if (mountRef.current) {
      mountRef.current.appendChild(renderer.domElement);
    }
    rendererRef.current = renderer;

    // Balls
    const geometry = new THREE.SphereGeometry(10, 32, 32);
    const material1 = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const material2 = new THREE.MeshBasicMaterial({ color: 0x0000ff });
    const mesh1 = new THREE.Mesh(geometry, material1);
    const mesh2 = new THREE.Mesh(geometry, material2);

    // Initialize
    let mass1Kg: number, mass2Kg: number, maxAngleRad: number;
    try {
      mass1Kg = params.mass1Lbs * LBS_TO_KG;
      mass2Kg = params.mass2Lbs * LBS_TO_KG;
      maxAngleRad = calculateMaxAngle(params.maxHeight);
    } catch (error) {
      console.error('Initialization error:', error);
      return;
    }

    const { theta1, theta2, theta1Dot, theta2Dot } = calculatePendulumMotion(
      maxAngleRad,
      params.vInit1,
      params.vInit2,
      mass1Kg,
      mass2Kg,
      -2.0,
      LENGTH_SWING,
      2.0,
      LENGTH_SWING
    );

    ball1Ref.current = {
      theta: theta1,
      mass: mass1Kg,
      velocity: theta1Dot,
      mesh: mesh1,
    };
    ball2Ref.current = {
      theta: theta2,
      mass: mass2Kg,
      velocity: theta2Dot,
      mesh: mesh2,
    };

    scene.add(mesh1);
    scene.add(mesh2);

    // Animation loop
    const animate = () => {
      if (!isMountedRef.current || !ball1Ref.current || !ball2Ref.current || !rendererRef.current || !sceneRef.current || !cameraRef.current) {
        return;
      }

      if (running) {
        // Update positions
        const x1 = -2.0 + LENGTH_SWING * Math.sin(ball1Ref.current.theta) * 100;
        const y1 = LENGTH_SWING - LENGTH_SWING * Math.cos(ball1Ref.current.theta) * 100;
        const x2 = 2.0 + LENGTH_SWING * Math.sin(ball2Ref.current.theta) * 100;
        const y2 = LENGTH_SWING - LENGTH_SWING * Math.cos(ball2Ref.current.theta) * 100;

        ball1Ref.current.mesh.position.set(x1, -y1, 0);
        ball2Ref.current.mesh.position.set(x2, -y2, 0);

        // Collision results
        try {
          const { v1Prime, v2Prime } = calculateCollision(
            ball1Ref.current.velocity,
            ball2Ref.current.velocity,
            ball1Ref.current.mass,
            ball2Ref.current.mass
          );

          const velocity1 = calculateVelocity(ball1Ref.current.theta, LENGTH_SWING, v1Prime * LENGTH_SWING);
          const velocity2 = calculateVelocity(ball2Ref.current.theta, LENGTH_SWING, v2Prime * LENGTH_SWING);
          const force = calculateForce(velocity1, ball1Ref.current.mass);
          const surfaceCm2 = calculateImpactSurface(params.age, params.impactType === 'frontal' ? 'frontal' : 'lateral');
          const pressureMPa = calculatePressure(force, surfaceCm2);
          const acceleration = calculateAcceleration(force, ANTHROPOMETRIC_DATA[params.age]?.head_mass_kg || 3.5);

          const results: CollisionResults = {
            age: params.age,
            maxHeight: params.maxHeight,
            mass1Lbs: params.mass1Lbs,
            mass1Kg,
            mass2Lbs: params.mass2Lbs,
            mass2Kg,
            vInit1: params.vInit1,
            vInit2: params.vInit2,
            angleHorizontal1: THREE.MathUtils.radToDeg(ball1Ref.current.theta),
            angleHorizontal2: THREE.MathUtils.radToDeg(ball2Ref.current.theta),
            impactType: params.impactType,
            velocity1,
            velocity2,
            relativeVelocity: Math.abs(velocity1 - velocity2),
            force,
            surfaceCm2,
            pressureMPa,
            decapitationRisk: getRiskLevelDisplayName(assessDecapitationRisk(pressureMPa, params.age)),
            cervicalFractureRisk: getRiskLevelDisplayName(assessCervicalFractureRisk(pressureMPa, params.age)),
            concussionRisk: getRiskLevelDisplayName(assessConcussionRisk(acceleration, params.age)),
          };

          ball1Ref.current.velocity = v1Prime;
          ball2Ref.current.velocity = v2Prime;

          if (isMountedRef.current) {
            onCollision(results);
          }
        } catch (error) {
          console.error('Collision calculation error:', error);
        }
      }

      rendererRef.current.render(sceneRef.current, cameraRef.current);
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    if (isMountedRef.current) {
      animate();
    }

    // Cleanup
    return () => {
      isMountedRef.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      if (mountRef.current && rendererRef.current) {
        try {
          mountRef.current.removeChild(rendererRef.current.domElement);
        } catch (e) {
          console.warn('Error removing renderer:', e);
        }
      }
      if (rendererRef.current) {
        rendererRef.current.dispose();
        rendererRef.current = null;
      }
    };
  }, [running, params, onCollision]);

  return <div ref={mountRef} style={{ width: '800px', height: '600px' }} />;
};

export default SimulationCanvas;