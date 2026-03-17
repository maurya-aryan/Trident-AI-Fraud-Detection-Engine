import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { useGLTF, PerspectiveCamera, Environment, ContactShadows, Center } from '@react-three/drei';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// --- 3D Components ---

function Trident({ tl }) {
  const { scene } = useGLTF('/assets/gold_trident.glb');
  const tridentRef = useRef();

  useFrame((state) => {
    if (tridentRef.current) {
      const t = state.clock.getElapsedTime();
      tridentRef.current.rotation.y += 0.005;
      // Fixed in place, only gentle bobbing
      tridentRef.current.position.y = Math.sin(t * 2) * 0.05;
    }
  });

  return (
    <group ref={tridentRef} position={[0, 0, 0]}>
      <Center>
        <primitive
          object={scene}
          scale={0.4} // Scaled down the Trident to fit perfectly on screen at (0,0,0)
        />
      </Center>
    </group>
  );
}

function ServerCity() {
  const obj = useLoader(OBJLoader, 'https://raw.githubusercontent.com/iondrimba/images/master/buildings.obj');
  const groupRef = useRef();

  useEffect(() => {
    if (!groupRef.current || !obj) return;
    const group = groupRef.current;

    const models = [...obj.children].map((m) => {
      const cloned = m.clone();
      cloned.scale.set(0.01, 0.01, 0.01);
      cloned.position.set(0, -14, 0);
      cloned.receiveShadow = true;
      cloned.castShadow = true;
      return cloned;
    });

    const gridSize = 40;
    const boxSize = 3;
    // Visually improved building materials: dark, reflective, with a faint red emissive
    const meshParams = {
      color: '#050505',
      metalness: 0.8,
      emissive: '#1a0000',
      roughness: 0.2,
    };
    const max = 0.009;
    const min = 0.001;
    const material = new THREE.MeshPhysicalMaterial(meshParams);

    let buildingsArr = [];
    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        const building = models[Math.floor(Math.random() * models.length)].clone();
        building.material = material;
        building.scale.y = Math.random() * (max - min) + min + 0.01;
        building.position.x = (i * boxSize);
        building.position.z = (j * boxSize);
        group.add(building);
        buildingsArr.push(building);
      }
    }

    // Sort and animate initial rise (Wave motion from app.js)
    buildingsArr.sort((a, b) => b.position.z - a.position.z);
    buildingsArr.forEach((building, index) => {
      gsap.to(building.position, {
        y: 1,
        ease: "power3.out",
        duration: 2,
        delay: 0.1 + (index / 3000)
      });
    });

    return () => {
      buildingsArr.forEach(b => group.remove(b));
    };
  }, [obj]);

  return (
    <group ref={groupRef} position={[-60, -90, -150]} />
  );
}

function Experience() {
  const cameraRef = useRef();
  const [tl, setTl] = useState(null);

  useEffect(() => {
    const newTl = gsap.timeline({
      scrollTrigger: {
        trigger: ".scroll-height",
        start: "top top",
        end: "bottom bottom",
        scrub: 1,
      }
    });

    setTl(newTl);

    if (cameraRef.current) {
      newTl.to(cameraRef.current.position, {
        y: -15,
        duration: 0.25,
        ease: "power2.inOut"
      }, 0);

      newTl.to(".hero-title", {
        opacity: 1,
        y: 0,
        duration: 0.15,
      }, 0.05);

      newTl.to(".hero-title", {
        opacity: 1,
        duration: 0.1,
      }, 0.25);

      newTl.to(".hero-title", {
        opacity: 0,
        y: -50,
        duration: 0.1,
      }, 0.35);

      // Fixed Zoom level so it's not too far inside
      newTl.to(cameraRef.current.position, {
        x: 0,
        y: -70, // Just above the skyline
        z: -10, // Kept back out of the dense center mass
        duration: 0.45,
        ease: "power2.inOut"
      }, 0.35);

      newTl.to(".scroll-indicator", {
        opacity: 0,
        duration: 0.1
      }, 0.35);

      newTl.to(cameraRef.current.rotation, {
        x: -0.15, // Look slightly downwards at the city
        duration: 0.45,
        ease: "power2.inOut"
      }, 0.35);

      newTl.to(".feature-card", {
        opacity: 1,
        scale: 1,
        stagger: 0.02,
        duration: 0.25,
        ease: "back.out(1.2)"
      }, 0.75);
    }

    return () => {
      if (newTl.scrollTrigger) newTl.scrollTrigger.kill();
      newTl.kill();
    };
  }, []);

  return (
    <>
      <PerspectiveCamera ref={cameraRef} makeDefault position={[0, 0, 30]} fov={30} />
      <color attach="background" args={['#020000']} /> {/* Very dark red/black background */}

      {/* Atmosphere - matching the crimson vibe */}
      <fog attach="fog" args={['#050000', 20, 150]} />
      <ambientLight color="#220000" intensity={1} />

      {/* Main highlight coming from far right/top */}
      <spotLight color="#ff0000" intensity={2} position={[200, 100, 100]} castShadow angle={0.5} penumbra={1} />

      {/* Central glow simulating radiation out of the Trident / core */}
      <pointLight color="#ff1111" intensity={15} position={[0, -10, -50]} distance={150} decay={2} />

      {/* Background Shape */}
      <mesh position={[0, -50, -250]}>
        <planeGeometry args={[400, 100]} />
        <meshPhysicalMaterial color="#050000" />
      </mesh>

      {/* Floor */}
      <mesh position={[0, -90, -90]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[400, 400]} />
        <meshStandardMaterial color="#000000" metalness={0} emissive="#000000" roughness={1} />
      </mesh>

      <Trident tl={tl} />
      <React.Suspense fallback={null}>
        <ServerCity />
      </React.Suspense>

      <Environment preset="night" />
      <ContactShadows position={[0, -2, 0]} opacity={0.6} scale={60} blur={2} far={15} color="#000" />
    </>
  );
}

// --- Main UI Component ---

const features = [
  "Credential Exposure", "Malware Scanner", "AI Text Detection",
  "Email Phishing", "URL Detection", "Prompt Injection",
  "Fusion Model", "Campaign Graph", "SHAP Explainer"
];

export default function HeroSection() {
  return (
    <div className="relative w-full overflow-hidden bg-black">
      {/* Scroll height driver */}
      <div className="scroll-height h-[400vh]" />

      {/* Fixed Background Canvas */}
      <div className="fixed inset-0 z-0 h-screen w-full pointer-events-none">
        <Canvas shadows gl={{ antialias: true }}>
          <React.Suspense fallback={null}>
            <Experience />
          </React.Suspense>
        </Canvas>
      </div>

      {/* HTML UI Overlay */}
      <div className="fixed inset-0 z-10 flex flex-col items-center justify-center pointer-events-none p-10 mt-32">

        {/* Phase 1 Title */}
        <div className="hero-title opacity-0 translate-y-10 text-center absolute top-1/2 -translate-y-1/2">
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white uppercase italic">
            Trident <span className="text-red-600">AI</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 font-light tracking-[0.3em] uppercase mt-4">
            Fraud Detection Engine
          </p>
        </div>

        {/* Phase 3 Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full">
          {features.map((feature, i) => (
            <div
              key={i}
              className="feature-card opacity-0 scale-90 p-8 border border-white/10 bg-white/5 backdrop-blur-xl rounded-2xl flex flex-col justify-between group hover:border-red-500/50 transition-colors duration-500 pointer-events-auto cursor-pointer"
            >
              <div className="mb-4 text-xs font-mono text-gray-500 uppercase tracking-widest flex justify-between items-center">
                <span>Module {String(i + 1).padStart(2, '0')}</span>
                <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 leading-tight">
                {feature}
              </h3>
              <p className="text-sm text-gray-400 font-light leading-relaxed">
                Advanced multi-modal signal processing for {feature.toLowerCase()} insights.
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="scroll-indicator fixed bottom-10 left-1/2 -translate-x-1/2 z-20 pointer-events-none flex flex-col items-center">
        <span className="text-[10px] uppercase tracking-[0.5em] text-gray-500 mb-2">Initialize Scroll</span>
        <div className="w-[1px] h-12 bg-gradient-to-b from-red-600 to-transparent animate-bounce" />
      </div>
    </div>
  );
}

