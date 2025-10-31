import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { GradientLineShader } from './shaders/GradientLineShader.js';

const QuantumFluxMatrix = () => {
    const mountRef = useRef(null);

    useEffect(() => {
        const currentMount = mountRef.current;
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, currentMount.clientWidth / currentMount.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
        currentMount.appendChild(renderer.domElement);

        const nodes = [];
        const connections = new THREE.Group();
        const gradientLines = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let intersected = null;
        const clock = new THREE.Clock();

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0x8a2be2, 0.8);
        directionalLight.position.set(1, 1, 1);
        scene.add(directionalLight);

        const createCoreNode = () => {
            const geometry = new THREE.IcosahedronGeometry(10, 3);
            const material = new THREE.MeshStandardMaterial({
                color: 0x00ffe0,
                emissive: 0x6633ff,
                metalness: 0.8,
                roughness: 0.2,
                flatShading: true,
                wireframe: true
            });
            const coreNode = new THREE.Mesh(geometry, material);
            const coreName = "$JAXX Guardian Core";
            coreNode.name = coreName;
            coreNode.userData = { id: 'CORE', name: coreName, children: [] };
            scene.add(coreNode);
            nodes.push(coreNode);
        };

        const createConnection = (nodeA, nodeB) => {
            const geometry = new THREE.BufferGeometry().setFromPoints([nodeA.position, nodeB.position]);
            const material = new THREE.ShaderMaterial(GradientLineShader);
            const line = new THREE.Line(geometry, material);
            connections.add(line);
            gradientLines.push({ line, base: { geometry: geometry.clone() } });
        };

        const addNode = (data, parent) => {
            const geometry = new THREE.SphereGeometry(3, 32, 32);
            const material = new THREE.MeshPhongMaterial({
                color: new THREE.Color(Math.random() * 0xffffff),
                shininess: 80
            });
            const node = new THREE.Mesh(geometry, material);

            node.position.set(
                (Math.random() - 0.5) * 150,
                (Math.random() - 0.5) * 150,
                (Math.random() - 0.5) * 150
            );

            const nodeId = data.id || `Node_${nodes.length}`;
            node.userData = { ...data, id: nodeId, parent: null, children: [] };
            node.name = data.name || nodeId;

            const parentNode = parent || nodes[0];
            node.userData.parent = parentNode.userData.id;
            if (parentNode.userData.children) {
                parentNode.userData.children.push(node.userData.id);
            } else {
                parentNode.userData.children = [node.userData.id];
            }
            createConnection(parentNode, node);

            scene.add(node);
            nodes.push(node);
            return node;
        };

        createCoreNode();
        const coreNode = nodes[0];
        addNode({ id: 'DONNY-001', name: 'DONNY' }, coreNode);
        addNode({ id: 'VALOR-AUX-002' }, coreNode);
        scene.add(connections);
        camera.position.z = 100;

        const onMouseMove = (event) => {
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        };

        const highlightConnections = (node) => {
            if (!node) {
                gradientLines.forEach(({line})=>{
                    line.material.uniforms.colorStart.value.set(0x6633ff);
                    line.material.uniforms.colorEnd.value.set(0x6633ff);
                    line.material.opacity = 0.2;
                });
                nodes.forEach(n => n.scale.set(1,1,1));
                return;
            }
            ValorAiPlusSequentialRipple(node);
        };

        const ValorAiPlusSequentialRipple = (node, visited = new Set(), depth = 0, delay = 0) => {
            if(visited.has(node)) return;
            visited.add(node);

            const businessFactor = node.userData.name === "DONNY" ? 1.5 : 1.0;
            const intensity = (1.0 - depth*0.15) * businessFactor;
            const baseColor = node.material.color.clone();

            setTimeout(() => {
              const color = baseColor.clone().multiplyScalar(intensity);

              if (node.userData.children) {
                  node.userData.children.forEach(childId => {
                    const child = nodes.find(n => n.userData.id === childId);
                    if(child){
                      gradientLines.forEach(({line, base})=>{
                        const pos = base.geometry.attributes.position.array;
                        const match =
                          (pos[0]===node.position.x && pos[1]===node.position.y && pos[2]===node.position.z &&
                           pos[3]===child.position.x && pos[4]===child.position.y && pos[5]===child.position.z) ||
                          (pos[3]===node.position.x && pos[4]===node.position.y && pos[5]===node.position.z &&
                           pos[0]===child.position.x && pos[1]===child.position.y && pos[2]===child.position.z);
                        if(match){
                          line.material.uniforms.colorStart.value.set(color);
                          line.material.uniforms.colorEnd.value.set(color);
                          line.material.opacity = 0.9 * businessFactor;
                        }
                      });
                    }
                  });
              }

              if(node.userData.parent){
                const parent = nodes.find(n=>n.userData.id===node.userData.parent);
                if(parent){
                  gradientLines.forEach(({line, base})=>{
                    const pos = base.geometry.attributes.position.array;
                    const match =
                      (pos[0]===node.position.x && pos[1]===node.position.y && pos[2]===node.position.z &&
                       pos[3]===parent.position.x && pos[4]===parent.position.y && pos[5]===parent.position.z) ||
                      (pos[3]===node.position.x && pos[4]===node.position.y && pos[5]===node.position.z &&
                       pos[0]===parent.position.x && pos[1]===parent.position.y && pos[2]===parent.position.z);
                    if(match){
                      line.material.uniforms.colorStart.value.set(color.multiplyScalar(0.7));
                      line.material.uniforms.colorEnd.value.set(color.multiplyScalar(0.7));
                      line.material.opacity = 0.7 * businessFactor;
                    }
                  });
                }
              }

              node.scale.setScalar(1 + 0.2 * intensity);

            }, delay);

            let childDelay = delay + 100;
            if (node.userData.children) {
                node.userData.children.forEach(childId=>{
                  const child = nodes.find(n => n.userData.id === childId);
                  if(child) ValorAiPlusSequentialRipple(child, visited, depth+1, childDelay);
                  childDelay += 100;
                });
            }
        };

        const animate = () => {
            requestAnimationFrame(animate);

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodes);

            if (intersects.length > 0) {
                if (intersected != intersects[0].object) {
                    if (intersected) intersected.material.emissive.setHex(intersected.currentHex);
                    intersected = intersects[0].object;
                    intersected.currentHex = intersected.material.emissive.getHex();
                    intersected.material.emissive.setHex(0xff0000);
                    highlightConnections(intersected);
                }
            } else {
                if (intersected) {
                    intersected.material.emissive.setHex(intersected.currentHex);
                    highlightConnections(null);
                }
                intersected = null;
            }

            const time = clock.getElapsedTime();
            connections.children.forEach(line => {
                if(line.material.uniforms.time) {
                    line.material.uniforms.time.value = time;
                }
            });

            const time_old = Date.now() * 0.0005;
            nodes.forEach((node, i) => {
                if (i > 0) {
                     node.position.x += Math.sin(time_old + i) * 0.1;
                     node.position.y += Math.cos(time_old + i) * 0.1;
                }
            });

            scene.rotation.y += 0.0005;
            renderer.render(scene, camera);
        };

        animate();

        currentMount.addEventListener('mousemove', onMouseMove);

        return () => {
            currentMount.removeEventListener('mousemove', onMouseMove);
            currentMount.removeChild(renderer.domElement);
        };
    }, []);

    return <div ref={mountRef} style={{ height: '500px', width: '100%' }} />;
};

export default QuantumFluxMatrix;