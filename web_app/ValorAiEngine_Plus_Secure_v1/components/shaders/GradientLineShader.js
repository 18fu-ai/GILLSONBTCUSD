import * as THREE from 'three';

// GradientLineShader.js  (place in /shaders)
export const GradientLineShader = {
  uniforms: {
    colorStart: { value: new THREE.Color(0x00c6ff) }, // blue-cyan
    colorEnd:   { value: new THREE.Color(0x0072ff) }, // deep-blue
    time:       { value: 0.0 }                        // ripple phase
  },
  vertexShader: /* glsl */`
    varying float vUvY;
    void main () {
      vUvY = position.y;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
    }`,
  fragmentShader: /* glsl */`
    uniform vec3  colorStart;
    uniform vec3  colorEnd;
    uniform float time;
    varying float vUvY;
    void main () {
      float ripple = 0.5 + 0.5 * sin( (vUvY * 10.0 - time) * 6.283 );
      vec3  grad   = mix(colorStart, colorEnd, ripple);
      gl_FragColor = vec4(grad, 1.0);
    }`
};