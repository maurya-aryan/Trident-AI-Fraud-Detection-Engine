import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, PerspectiveCamera, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// --- 3D Components ---

function Trident({ tl }) {
  const { scene } = useGLTF('/assets/trident.glb');
  const tridentRef = useRef();

  useEffect(() => {
    if (tl && tridentRef.current) {
      // Phase 1: Emergence
      tl.to(tridentRef.current.position, {
        y: 0,
        duration: 1,
        ease: "power2.out"
      }, 0);

      // Phase 2: Zoom & Interception
      tl.to(tridentRef.current.position, {
        y: 20,
        duration: 0.5,
        ease: "power2.in"
      }, 1.5);
    }
  }, [tl]);

  useFrame((state) => {
    if (tridentRef.current) {
      const t = state.clock.getElapsedTime();
      tridentRef.current.rotation.y += 0.005;
      tridentRef.current.position.y += Math.sin(t * 2) * 0.002;
    }
  });

  return (
    <primitive
      ref={tridentRef}
      object={scene}
      scale={8}
      position={[0, -10, 0]}
    />
  );
}

function ServerCity({ tl }) {
  const count = 40 * 40;
  const meshRef = useRef();
  const { nodes } = useGLTF('/assets/trident.glb'); // Reuse same asset for buildings if needed, but we have buildings.obj
  // Actually, we should load buildings.obj as per reference

  const dummy = useMemo(() => new THREE.Object3D(), []);
  const gridPositions = useMemo(() => {
    const pos = [];
    const spacing = 4;
    for (let i = 0; i < 40; i++) {
      for (let j = 0; j < 40; j++) {
        // Center the grid
        pos.push([
          (i - 20) * spacing,
          0,
          (j - 20) * spacing
        ]);
      }
    }
    return pos;
  }, []);

  useEffect(() => {
    if (!meshRef.current) return;

    gridPositions.forEach((pos, i) => {
      dummy.position.set(pos[0], -14, pos[2]); // Start below ground like reference
      const height = 0.5 + Math.random() * 2;
      dummy.scale.set(1, height, 1);
      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;

    if (tl) {
      // Reveal buildings from bottom up like reference
      tl.to(meshRef.current.position, {
        y: 1, // Move entire group up slightly
        duration: 1,
        ease: "power2.out"
      }, 0);
    }
  }, [dummy, gridPositions, tl]);

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <boxGeometry args={[2, 1, 2]} />
      <meshStandardMaterial
        color="#0a0a0a"
        metalness={0.9}
        roughness={0.1}
        emissive="#330000"
        emissiveIntensity={0.2}
      />
    </instancedMesh>
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

    // Phase 1: Emergence
    newTl.to(".hero-title", {
      opacity: 1,
      y: 0,
      duration: 0.5
    }, 0.2);

    // Phase 2: Zoom - Camera moves INTO the city
    if (cameraRef.current) {
      newTl.to(".hero-title", {
        opacity: 0,
        duration: 0.3
      }, 1.3);

      newTl.to(cameraRef.current.position, {
        z: 30, // Don't hide the buildings, zoom INTO them
        y: 8,
        duration: 2,
        ease: "power1.inOut"
      }, 1.5);

      newTl.to(cameraRef.current.rotation, {
        x: -0.2, // Look down slightly at the city
        duration: 2,
        ease: "power1.inOut"
      }, 1.5);
    }

    // Phase 3: Arsenal Reveal - Background stays visible
    newTl.to(".feature-card", {
      opacity: 1,
      scale: 1,
      stagger: 0.1,
      duration: 0.8,
      ease: "back.out(1.2)"
    }, 3.5);

    return () => {
      if (newTl.scrollTrigger) newTl.scrollTrigger.kill();
      newTl.kill();
    };
  }, []);

  return (
    <>
      <PerspectiveCamera ref={cameraRef} makeDefault position={[0, 40, 180]} fov={30} />
      <color attach="background" args={['#000']} />
      <fog attach="fog" args={['#000', 40, 220]} />

      <ambientLight intensity={0.4} />
      <spotLight position={[50, 60, 50]} angle={0.3} penumbra={1} intensity={6} castShadow />
      <directionalLight position={[-20, 30, 20]} intensity={3} color="#f14f58" />

      <Trident tl={tl} />
      <ServerCity tl={tl} />

      <Environment preset="night" />
      <ContactShadows position={[0, -2, 0]} opacity={0.6} scale={60} blur={1} far={15} />
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
      <div className="fixed inset-0 z-10 flex flex-col items-center justify-center pointer-events-none p-10">

        {/* Phase 1 Title */}
        <div className="hero-title opacity-0 translate-y-10 text-center mb-20 px-4">
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
              className="feature-card opacity-0 scale-90 p-8 border border-white/10 bg-white/5 backdrop-blur-xl rounded-2xl flex flex-col justify-between group hover:border-red-500/50 transition-colors duration-500"
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
      <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-20 pointer-events-none flex flex-col items-center">
        <span className="text-[10px] uppercase tracking-[0.5em] text-gray-500 mb-2">Initialize Scroll</span>
        <div className="w-[1px] h-12 bg-gradient-to-b from-red-600 to-transparent animate-bounce" />
      </div>
    </div>
  );
}
