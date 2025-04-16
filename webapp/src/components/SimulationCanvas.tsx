import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { Ball, SimulationCanvasProps } from './simulationCanvas/types';
import { setupScene } from './simulationCanvas/sceneSetup';
import { updatePhysicsAndCollision } from './simulationCanvas/physics';
import { createTextSprite } from './simulationCanvas/spriteUtils';
import { calculateMaxAngle } from '../simulation/calculations';
import { LENGTH_SWING, LBS_TO_KG } from '../simulation/constants';

interface ExtendedSimulationCanvasProps extends SimulationCanvasProps {
  resetSignal?: boolean;
}

const SimulationCanvas: React.FC<ExtendedSimulationCanvasProps> = ({
  params,
  running,
  onCollision,
  setIsRunning,
  resetSignal = false,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.OrthographicCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const ball1Ref = useRef<Ball | null>(null);
  const ball2Ref = useRef<Ball | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const isMountedRef = useRef<boolean>(true);
  const flashTimeRef = useRef<number>(0);
  const collisionOccurredRef = useRef<boolean>(false);
  const fpsRef = useRef<{ count: number; lastTime: number; value: number }>({
    count: 0,
    lastTime: Date.now(),
    value: 0,
  });
  const angle1SpriteRef = useRef<THREE.Sprite | null>(null);
  const speed1SpriteRef = useRef<THREE.Sprite | null>(null);
  const angle2SpriteRef = useRef<THREE.Sprite | null>(null);
  const speed2SpriteRef = useRef<THREE.Sprite | null>(null);
  const fpsSpriteRef = useRef<THREE.Sprite | null>(null);
  const angle1ValueRef = useRef<number>(0);
  const speed1ValueRef = useRef<number>(0);
  const angle2ValueRef = useRef<number>(0);
  const speed2ValueRef = useRef<number>(0);
  const fpsValueRef = useRef<number>(0);
  const finalV1Ref = useRef<number>(0);
  const finalV2Ref = useRef<number>(0);
  const hasInitializedRef = useRef<boolean>(false);

  // Handle window resize
  const updateRendererSize = () => {
    if (mountRef.current && rendererRef.current && cameraRef.current) {
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      rendererRef.current.setSize(width, height);
      const aspectRatio = width / height;
      const baseWidth = 10;
      const baseHeight = baseWidth / aspectRatio;
      cameraRef.current.left = -baseWidth / 2;
      cameraRef.current.right = baseWidth / 2;
      cameraRef.current.top = baseHeight / 2;
      cameraRef.current.bottom = -baseHeight / 2;
      cameraRef.current.updateProjectionMatrix();
    }
  };

  const resetSimulation = () => {
    if (ball1Ref.current && ball2Ref.current) {
      const maxAngleRad = THREE.MathUtils.degToRad(calculateMaxAngle(params.maxHeight));
      ball1Ref.current.theta = -maxAngleRad;
      ball1Ref.current.velocity = params.vInit1 / LENGTH_SWING || 0;
      ball2Ref.current.theta = maxAngleRad;
      ball2Ref.current.velocity = -params.vInit2 / LENGTH_SWING || 0;
      ball1Ref.current.mass = params.mass1Lbs * LBS_TO_KG;
      ball2Ref.current.mass = params.mass2Lbs * LBS_TO_KG;

      const x1 = -LENGTH_SWING * Math.sin(ball1Ref.current.theta);
      const y1 = LENGTH_SWING * Math.cos(ball1Ref.current.theta);
      const x2 = LENGTH_SWING * Math.sin(ball2Ref.current.theta);
      const y2 = LENGTH_SWING * Math.cos(ball2Ref.current.theta);

      const rope1Pos = ball1Ref.current.rope.geometry.attributes.position.array as Float32Array;
      rope1Pos.set([-2.0, LENGTH_SWING, 0, x1, y1, 0]);
      ball1Ref.current.rope.geometry.attributes.position.needsUpdate = true;
      ball1Ref.current.platform.position.set(x1, y1, 0);
      ball1Ref.current.platform.rotation.z = ball1Ref.current.theta;

      const rope2Pos = ball2Ref.current.rope.geometry.attributes.position.array as Float32Array;
      rope2Pos.set([2.0, LENGTH_SWING, 0, x2, y2, 0]);
      ball2Ref.current.rope.geometry.attributes.position.needsUpdate = true;
      ball2Ref.current.platform.position.set(x2, y2, 0);
      ball2Ref.current.platform.rotation.z = ball2Ref.current.theta;

      ball1Ref.current.platformMaterial.color.set(0x0000ff);
      ball2Ref.current.platformMaterial.color.set(0xff0000);

      if (angle1SpriteRef.current) {
        angle1SpriteRef.current.material.map?.dispose();
        angle1SpriteRef.current.material.map = createTextSprite(
          `Angle 1: ${THREE.MathUtils.radToDeg(ball1Ref.current.theta).toFixed(1)}°`
        ).material.map;
        angle1SpriteRef.current.material.map!.needsUpdate = true;
      }
      if (speed1SpriteRef.current) {
        speed1SpriteRef.current.material.map?.dispose();
        speed1SpriteRef.current.material.map = createTextSprite(
          `Vitesse 1: ${(Math.abs(ball1Ref.current.velocity * LENGTH_SWING)).toFixed(2)} m/s`
        ).material.map;
        speed1SpriteRef.current.material.map!.needsUpdate = true;
      }
      if (angle2SpriteRef.current) {
        angle2SpriteRef.current.material.map?.dispose();
        angle2SpriteRef.current.material.map = createTextSprite(
          `Angle 2: ${THREE.MathUtils.radToDeg(ball2Ref.current.theta).toFixed(1)}°`
        ).material.map;
        angle2SpriteRef.current.material.map!.needsUpdate = true;
      }
      if (speed2SpriteRef.current) {
        speed2SpriteRef.current.material.map?.dispose();
        speed2SpriteRef.current.material.map = createTextSprite(
          `Vitesse 2: ${(Math.abs(ball2Ref.current.velocity * LENGTH_SWING)).toFixed(2)} m/s`
        ).material.map;
        speed2SpriteRef.current.material.map!.needsUpdate = true;
      }
      if (fpsSpriteRef.current) {
        fpsSpriteRef.current.material.map?.dispose();
        fpsSpriteRef.current.material.map = createTextSprite('FPS: 0').material.map;
        fpsSpriteRef.current.material.map!.needsUpdate = true;
      }

      angle1ValueRef.current = THREE.MathUtils.radToDeg(ball1Ref.current.theta);
      speed1ValueRef.current = Math.abs(ball1Ref.current.velocity * LENGTH_SWING);
      angle2ValueRef.current = THREE.MathUtils.radToDeg(ball2Ref.current.theta);
      speed2ValueRef.current = Math.abs(ball2Ref.current.velocity * LENGTH_SWING);
      fpsValueRef.current = 0;
      finalV1Ref.current = 0;
      finalV2Ref.current = 0;
      collisionOccurredRef.current = false;
    }
  };

  // Initial setup
  useEffect(() => {
    isMountedRef.current = true;

    try {
      if (mountRef.current) {
        const { scene, camera, renderer, ball1, ball2 } = setupScene(mountRef.current);
        sceneRef.current = scene;
        cameraRef.current = camera;
        rendererRef.current = renderer;
        ball1Ref.current = ball1;
        ball2Ref.current = ball2;

        if (mountRef.current && renderer) {
          mountRef.current.appendChild(renderer.domElement);
        }

        // Initialize sprites with dynamic positions
        angle1SpriteRef.current = createTextSprite('Angle 1: 0.0°');
        angle1SpriteRef.current.position.set(-2.5, 2.75, 1);
        scene.add(angle1SpriteRef.current);

        speed1SpriteRef.current = createTextSprite('Vitesse 1: 0.00 m/s');
        speed1SpriteRef.current.position.set(-2.5, 3.05, 1);
        scene.add(speed1SpriteRef.current);

        angle2SpriteRef.current = createTextSprite('Angle 2: 0.0°');
        angle2SpriteRef.current.position.set(1.5, 2.75, 1);
        scene.add(angle2SpriteRef.current);
 
        speed2SpriteRef.current = createTextSprite('Vitesse 2: 0.00 m/s');
        speed2SpriteRef.current.position.set(1.5, 3.05, 1);
        scene.add(speed2SpriteRef.current);

        fpsSpriteRef.current = createTextSprite('FPS: 0');
        fpsSpriteRef.current.position.set(-4, 4.5, 1);
        scene.add(fpsSpriteRef.current);

        hasInitializedRef.current = true;

        // Set up resize handler
        const handleResize = () => {
          updateRendererSize();
        };
        window.addEventListener('resize', handleResize);
        updateRendererSize(); // Initial sizing

        return () => {
          window.removeEventListener('resize', handleResize);
        };
      }
    } catch (err) {
      console.error('Failed to initialize scene:', err);
    }

    return () => {
      isMountedRef.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      [angle1SpriteRef, speed1SpriteRef, angle2SpriteRef, speed2SpriteRef, fpsSpriteRef].forEach((ref) => {
        if (ref.current && sceneRef.current) {
          sceneRef.current.remove(ref.current);
          ref.current.material.map?.dispose();
          ref.current.material.dispose();
        }
      });
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
      sceneRef.current = null;
      cameraRef.current = null;
    };
  }, []);

  // Update physics params and reset
  useEffect(() => {
    if (hasInitializedRef.current && ball1Ref.current && ball2Ref.current) {
      if (resetSignal) {
        resetSimulation();
      } else if (!collisionOccurredRef.current && !running) {
        const maxAngleRad = THREE.MathUtils.degToRad(calculateMaxAngle(params.maxHeight));
        ball1Ref.current.theta = -maxAngleRad;
        ball1Ref.current.velocity = params.vInit1 / LENGTH_SWING || 0;
        ball2Ref.current.theta = maxAngleRad;
        ball2Ref.current.velocity = -params.vInit2 / LENGTH_SWING || 0;
        ball1Ref.current.mass = params.mass1Lbs * LBS_TO_KG;
        ball2Ref.current.mass = params.mass2Lbs * LBS_TO_KG;

        const x1 = -LENGTH_SWING * Math.sin(ball1Ref.current.theta);
        const y1 = LENGTH_SWING * Math.cos(ball1Ref.current.theta);
        const x2 = LENGTH_SWING * Math.sin(ball2Ref.current.theta);
        const y2 = LENGTH_SWING * Math.cos(ball2Ref.current.theta);

        const rope1Pos = ball1Ref.current.rope.geometry.attributes.position.array as Float32Array;
        rope1Pos.set([-2.0, LENGTH_SWING, 0, x1, y1, 0]);
        ball1Ref.current.rope.geometry.attributes.position.needsUpdate = true;
        ball1Ref.current.platform.position.set(x1, y1, 0);
        ball1Ref.current.platform.rotation.z = ball1Ref.current.theta;

        const rope2Pos = ball2Ref.current.rope.geometry.attributes.position.array as Float32Array;
        rope2Pos.set([2.0, LENGTH_SWING, 0, x2, y2, 0]);
        ball2Ref.current.rope.geometry.attributes.position.needsUpdate = true;
        ball2Ref.current.platform.position.set(x2, y2, 0);
        ball2Ref.current.platform.rotation.z = ball2Ref.current.theta;
      }
    }
  }, [params, resetSignal, running]);

  // Animation loop
  useEffect(() => {
    if (!running || !rendererRef.current || !sceneRef.current || !cameraRef.current) {
      return;
    }

    const animate = () => {
      if (
        !isMountedRef.current ||
        !ball1Ref.current ||
        !ball2Ref.current ||
        !rendererRef.current ||
        !sceneRef.current ||
        !cameraRef.current
      ) {
        return;
      }

      fpsRef.current.count += 1;
      const currentTime = Date.now();
      const elapsedTime = (currentTime - fpsRef.current.lastTime) / 1000;
      if (elapsedTime >= 1) {
        fpsRef.current.value = fpsRef.current.count / elapsedTime;
        fpsRef.current.count = 0;
        fpsRef.current.lastTime = currentTime;
      }

      const { finalV1, finalV2 } = updatePhysicsAndCollision(
        ball1Ref.current,
        ball2Ref.current,
        params,
        collisionOccurredRef,
        flashTimeRef,
        currentTime,
        onCollision,
        setIsRunning
      );
      finalV1Ref.current = finalV1;
      finalV2Ref.current = finalV2;

      const angle1Deg = THREE.MathUtils.radToDeg(ball1Ref.current.theta);
      const angle2Deg = THREE.MathUtils.radToDeg(ball2Ref.current.theta);
      const speed1Ms = Math.abs(ball1Ref.current.velocity * LENGTH_SWING);
      const speed2Ms = Math.abs(ball2Ref.current.velocity * LENGTH_SWING);
      const displaySpeed1 = collisionOccurredRef.current ? finalV1Ref.current : speed1Ms;
      const displaySpeed2 = collisionOccurredRef.current ? finalV2Ref.current : speed2Ms;

      if (!collisionOccurredRef.current || (collisionOccurredRef.current && displaySpeed1 !== 0 && displaySpeed2 !==0)) {
  
        if (angle1SpriteRef.current && angle1Deg !== angle1ValueRef.current) {
          angle1SpriteRef.current.material.map?.dispose();
          angle1SpriteRef.current.material.map = createTextSprite(`Angle 1: ${(angle1Deg%360).toFixed(1)}°`).material.map;
          angle1SpriteRef.current.material.map!.needsUpdate = true;
          angle1ValueRef.current = angle1Deg;
        }
        if (speed1SpriteRef.current && displaySpeed1 !== speed1ValueRef.current) {
          speed1SpriteRef.current.material.map?.dispose();
          speed1SpriteRef.current.material.map = createTextSprite(
            `Vitesse 1: ${displaySpeed1.toFixed(2)} m/s`
          ).material.map;
          speed1SpriteRef.current.material.map!.needsUpdate = true;
          speed1ValueRef.current = displaySpeed1;
        }
        if (angle2SpriteRef.current && angle2Deg !== angle2ValueRef.current) {
          angle2SpriteRef.current.material.map?.dispose();
          angle2SpriteRef.current.material.map = createTextSprite(`Angle 2: ${(angle2Deg%360).toFixed(1)}°`).material.map;
          angle2SpriteRef.current.material.map!.needsUpdate = true;
          angle2ValueRef.current = angle2Deg;
        }
        if (speed2SpriteRef.current && displaySpeed2 !== speed2ValueRef.current) {
          speed2SpriteRef.current.material.map?.dispose();
          speed2SpriteRef.current.material.map = createTextSprite(
            `Vitesse 2: ${displaySpeed2.toFixed(2)} m/s`
          ).material.map;
          speed2SpriteRef.current.material.map!.needsUpdate = true;
          speed2ValueRef.current = displaySpeed2;
        }
        if (fpsSpriteRef.current && fpsRef.current.value !== fpsValueRef.current) {
          fpsSpriteRef.current.material.map?.dispose();
          fpsSpriteRef.current.material.map = createTextSprite(`FPS: ${Math.round(fpsRef.current.value)}`).material.map;
          fpsSpriteRef.current.material.map!.needsUpdate = true;
          fpsValueRef.current = fpsRef.current.value;
        }
      }

      rendererRef.current.render(sceneRef.current, cameraRef.current);
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [running, params, onCollision, setIsRunning]);

  return (
    <div
      ref={mountRef}
      style={{
        width: '100%',
        height: '100%',
        minHeight: '400px', // Ensure minimum height for mobile
        position: 'relative',
        overflow: 'hidden',
      }}
    />
  );
};

export default SimulationCanvas;