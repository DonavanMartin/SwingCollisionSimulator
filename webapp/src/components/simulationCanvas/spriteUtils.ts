import * as THREE from 'three';

export const createTextSprite = (text: string, fontSize: number = 24): THREE.Sprite => {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d')!;
  context.font = `${fontSize}px Arial`;
  const metrics = context.measureText(text);
  canvas.width = metrics.width + 10; // 5px padding each side
  canvas.height = fontSize + 4; // 2px padding top/bottom
  context.fillStyle = 'rgba(0, 0, 0, 0.5)';
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = 'white';
  context.font = `${fontSize}px Arial`;
  context.fillText(text, 5, fontSize + 2);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(canvas.width / 100, canvas.height / 100, 1);
  return sprite;
};