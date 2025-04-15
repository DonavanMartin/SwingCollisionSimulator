import * as THREE from 'three';
import { Ball } from './types';
import { LENGTH_SWING, PLATFORM_WIDTH } from '../../simulation/constants';

export const setupScene = () => {
  // Scene
  const scene = new THREE.Scene();

  // Camera
  const windowWidth = 600;
  const windowHeight = 450;
  const left = -5;
  const right = 5;
  const bottom = -2;
  const top = 5;
  const camera = new THREE.OrthographicCamera(left, right, top, bottom, 0.1, 1000);
  camera.position.set(0, 0, 10);
  camera.lookAt(0, 0, 0);

  // Renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 3)); // Cap DPR for performance
  renderer.setSize(windowWidth, windowHeight);

  // Background
  const textureLoader = new THREE.TextureLoader();
  textureLoader.load('/assets/background.jpg', (texture) => {
    const bgGeometry = new THREE.PlaneGeometry(10, 7);
    const bgMaterial = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
    const bgMesh = new THREE.Mesh(bgGeometry, bgMaterial);
    bgMesh.position.set(0, 1.5, -5);
    scene.add(bgMesh);
  }, undefined, (error) => {
    console.error('Error loading background texture:', error);
    const bgGeometry = new THREE.PlaneGeometry(10, 7);
    const bgMaterial = new THREE.MeshBasicMaterial({ color: 0x008000 });
    const bgMesh = new THREE.Mesh(bgGeometry, bgMaterial);
    bgMesh.position.set(0, 1.5, -5);
    scene.add(bgMesh);
  });

  // Grid
  const gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x888888);
  gridHelper.position.set(0, -2, -1);
  scene.add(gridHelper);

  // Pivots
  const pivotGeometry = new THREE.SphereGeometry(0.05, 16, 16);
  const pivotMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const pivot1 = new THREE.Mesh(pivotGeometry, pivotMaterial);
  const pivot2 = new THREE.Mesh(pivotGeometry, pivotMaterial);
  pivot1.position.set(-2.0, LENGTH_SWING, 0);
  pivot2.position.set(2.0, LENGTH_SWING, 0);
  scene.add(pivot1, pivot2);

  // Swings
  const ropeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
  const platformGeometry = new THREE.PlaneGeometry(PLATFORM_WIDTH*2, 0.1);
  const platform1Material = new THREE.MeshBasicMaterial({ color: 0x0000ff, side: THREE.DoubleSide });
  const platform2Material = new THREE.MeshBasicMaterial({ color: 0xff0000, side: THREE.DoubleSide });

  // Rope 1
  const rope1Geometry = new THREE.BufferGeometry();
  const rope1Vertices = new Float32Array(6);
  rope1Geometry.setAttribute('position', new THREE.BufferAttribute(rope1Vertices, 3));
  const rope1 = new THREE.Line(rope1Geometry, ropeMaterial);
  scene.add(rope1);

  // Platform 1
  const platform1 = new THREE.Mesh(platformGeometry, platform1Material);
  scene.add(platform1);

  // Rope 2
  const rope2Geometry = new THREE.BufferGeometry();
  const rope2Vertices = new Float32Array(6);
  rope2Geometry.setAttribute('position', new THREE.BufferAttribute(rope2Vertices, 3));
  const rope2 = new THREE.Line(rope2Geometry, ropeMaterial);
  scene.add(rope2);

  // Platform 2
  const platform2 = new THREE.Mesh(platformGeometry, platform2Material);
  scene.add(platform2);

  // Balls
  const ball1: Ball = {
    rope: rope1,
    platform: platform1,
    pivot: pivot1,
    theta: 0,
    mass: 0,
    velocity: 0,
    platformMaterial: platform1Material,
  };
  const ball2: Ball = {
    rope: rope2,
    platform: platform2,
    pivot: pivot2,
    theta: 0,
    mass: 0,
    velocity: 0,
    platformMaterial: platform2Material,
  };

  return { scene, camera, renderer, ball1, ball2 };
};