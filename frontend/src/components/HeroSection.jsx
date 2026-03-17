import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { useGLTF, PerspectiveCamera, Environment, ContactShadows, Center, Clouds as DreiClouds, Cloud } from '@react-three/drei';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// --- Rain Component (adapted from user's example) ---

function Rain({ count = 3000 }) {
  const meshRef = useRef();
  const dummy = useMemo(() => new THREE.Object3D(), []);

  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < count; i++) {
      temp.push({
        x: (Math.random() - 0.5) * 200,
        y: Math.random() * 80 + 20,
        z: (Math.random() - 0.5) * 200 - 50,
        speed: Math.random() * 0.8 + 0.15,
      });
    }
    return temp;
  }, [count]);

  useFrame(() => {
    if (!meshRef.current) return;
    particles.forEach((particle, i) => {
      particle.y -= particle.speed;
      if (particle.y < -100) {
        particle.y = 80;
      }
      dummy.position.set(particle.x, particle.y, particle.z);
      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <cylinderGeometry args={[0.008, 0.008, 0.6, 4]} />
      <meshBasicMaterial color="#6699cc" transparent opacity={0.35} />
    </instancedMesh>
  );
}

// --- Storm Component (clouds + lightning) ---

function Storm() {
  const lightningLightRef = useRef();
  const lightningActive = useRef(false);

  useFrame(() => {
    // Lightning flash – random bursts illuminate the scene
    // Increased probability from 0.003 to 0.015 so it happens more often
    if (Math.random() < 0.03 && !lightningActive.current) {
      lightningActive.current = true;

      if (lightningLightRef.current) {
        const randomX = (Math.random() - 0.5) * 60;
        lightningLightRef.current.position.x = randomX;
        lightningLightRef.current.intensity = 120;

        setTimeout(() => {
          if (lightningLightRef.current)
            lightningLightRef.current.intensity = 0;
          lightningActive.current = false;
        }, 350);
      }
    }
  });

  return (
    <group>
      {/* Storm clouds above the Trident */}
      <DreiClouds material={THREE.MeshLambertMaterial}>
        <Cloud segments={60} bounds={[30, 4, 8]} volume={12} color="#3a4a5a" fade={100} speed={0.15} opacity={0.7} position={[-5, 12, -10]} />
        <Cloud segments={60} bounds={[30, 4, 8]} volume={12} color="#4a5a6a" fade={100} speed={0.12} opacity={0.6} position={[8, 10, -5]} />
        <Cloud segments={60} bounds={[25, 3, 6]} volume={10} color="#2a3a4a" fade={80} speed={0.2} opacity={0.8} position={[0, 14, -15]} />
        <Cloud segments={40} bounds={[20, 3, 5]} volume={8} color="#3a4a5a" fade={80} speed={0.18} opacity={0.5} position={[-10, 11, -20]} />
        <Cloud segments={40} bounds={[22, 3, 5]} volume={8} color="#4a5a6a" fade={80} speed={0.22} opacity={0.6} position={[12, 13, -8]} />
      </DreiClouds>

      {/* Clouds over the city area too */}
      <DreiClouds material={THREE.MeshLambertMaterial}>
        <Cloud segments={50} bounds={[60, 5, 30]} volume={15} color="#2a3545" fade={120} speed={0.1} opacity={0.5} position={[-30, -55, -120]} />
        <Cloud segments={50} bounds={[60, 5, 30]} volume={15} color="#3a4555" fade={120} speed={0.08} opacity={0.4} position={[10, -50, -140]} />
      </DreiClouds>

      <Rain count={3000} />

      {/* Lightning light - warm yellow flash that illuminates the entire scene including buildings */}
      <pointLight
        ref={lightningLightRef}
        position={[0, 15, -30]}
        intensity={0}
        color="#e6d8b3"
        distance={250}
        decay={0.5}
        castShadow
      />
    </group>
  );
}

// --- 3D Components ---

function Trident() {
  const { scene } = useGLTF('/assets/gold_trident.glb');
  const tridentRef = useRef();

  // GLB deep analysis: Node matrices contain hidden transforms:
  // - "handle" node: scale ~6.66x, translation (70, 158, 0)
  // - "Plane" node: scale ~66.6x, translation (74, 389, 0)
  // Actual rendered bounding box is ~750 units, NOT the raw 11 units from accessors.
  const TRIDENT_SCALE = 0.015;

  useFrame(() => {
    if (tridentRef.current) {
      tridentRef.current.rotation.y += 0.05;
    }
  });

  return (
    <group ref={tridentRef} position={[0, 0, 0]}>
      {/* Dedicated warm golden light for the trident */}
      <pointLight color="#ffcc66" intensity={25} distance={20} decay={2} position={[0, 3, 5]} />
      <pointLight color="#4488ff" intensity={8} distance={20} decay={2} position={[0, -3, -5]} />
      <Center>
        <primitive
          object={scene}
          scale={TRIDENT_SCALE}
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
    // Pure black buildings (like inspiration) - the blue glow comes from lighting, not material
    const meshParams = {
      color: '#000',
      metalness: 0,
      emissive: '#000',
      roughness: 0.77,
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

      // Zoom into the city skyline
      newTl.to(cameraRef.current.position, {
        x: 0,
        y: -75,
        z: -40, // Moved closer into the buildings (was -10)
        duration: 0.45,
        ease: "power2.inOut"
      }, 0.35);

      newTl.to(".scroll-indicator", {
        opacity: 0,
        duration: 0.1
      }, 0.35);

      newTl.to(cameraRef.current.rotation, {
        x: -0.15,
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

      {/* Deep midnight / obsidian blue background */}
      <color attach="background" args={['#020a14']} />

      {/* Fog: midnight blue atmosphere */}
      <fog attach="fog" args={['#020a14', 50, 220]} />

      {/* Ambient: dark blue ambient fill */}
      <ambientLight color="#0a0a2a" intensity={1} />

      {/* Blue spotlight from one side - creates the half-lit dramatic look */}
      <spotLight color="#0044ff" intensity={3} position={[641, -462, 509]} castShadow />

      {/* Blue directional moonlight from the left */}
      <directionalLight color="#2266cc" intensity={2} position={[-80, 30, 20]} />

      {/* Strong blue point light illuminating the city from above (like inspiration's #d3263a but blue) */}
      <pointLight color="#2244aa" intensity={8.2} position={[16, -10, -168]} />

      {/* Secondary blue glow from the opposite side - fainter, for depth */}
      <pointLight color="#1133aa" intensity={4} position={[-60, -75, -120]} distance={150} decay={2} />

      {/* Background Shape - deep midnight blue */}
      <mesh position={[0, -50, -250]}>
        <planeGeometry args={[400, 100]} />
        <meshPhysicalMaterial color="#020a14" />
      </mesh>

      {/* Floor - dark reflective */}
      <mesh position={[0, -90, -90]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[400, 400]} />
        <meshStandardMaterial color="#050a15" metalness={0.3} emissive="#010308" roughness={0.8} />
      </mesh>

      <Trident />
      <Storm />

      <React.Suspense fallback={null}>
        <ServerCity />
      </React.Suspense>

      <Environment preset="night" />
      <ContactShadows position={[0, -2, 0]} opacity={0.5} scale={60} blur={2} far={15} color="#001122" />
    </>
  );
}

// --- Main UI Component ---

const features = [
  "Credential Exposure", "Malware Scanner", "AI Text Detection",
  "Email Phishing", "URL Detection", "Prompt Injection",
  "Fusion Model", "Campaign Graph", "SHAP Explainer"
];

// Frame controller: continuously invalidates the canvas only while the hero is visible
function FrameController({ isVisible }) {
  useFrame(({ invalidate }) => {
    if (isVisible) invalidate();
  });
  return null;
}

export default function HeroSection() {
  const scrollRef = useRef(null);
  const [heroVisible, setHeroVisible] = useState(true);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setHeroVisible(entry.isIntersecting);
      },
      { threshold: 0 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="relative w-full overflow-hidden bg-black">
      {/* Scroll height driver — observed for visibility */}
      <div ref={scrollRef} className="scroll-height h-[400vh]" />

      {/* Fixed Background Canvas — hidden when scrolled past hero */}
      <div
        className="fixed inset-0 z-0 h-screen w-full pointer-events-none"
        style={{ display: heroVisible ? 'block' : 'none' }}
      >
        <Canvas shadows gl={{ antialias: true }} frameloop="demand">
          <FrameController isVisible={heroVisible} />
          <React.Suspense fallback={null}>
            <Experience />
          </React.Suspense>
        </Canvas>
      </div>

      {/* HTML UI Overlay — also hidden when hero is out of view */}
      <div
        className="fixed inset-0 z-10 flex flex-col items-center justify-center pointer-events-none p-10"
        style={{ display: heroVisible ? 'flex' : 'none' }}
      >

        {/* Phase 1 Title */}
        <div className="hero-title opacity-0 translate-y-10 text-center absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white uppercase italic">
            Trident <span className="text-blue-400">AI</span>
          </h1>
          <p className="text-xl md:text-2xl text-blue-200/60 font-light tracking-[0.3em] uppercase mt-4">
            Fraud Detection Engine
          </p>
        </div>

        {/* Phase 3 Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full">
          {features.map((feature, i) => (
            <div
              key={i}
              className="feature-card opacity-0 scale-90 p-8 border border-blue-400/10 bg-blue-950/20 backdrop-blur-xl rounded-2xl flex flex-col justify-between group hover:border-blue-400/40 transition-colors duration-500 pointer-events-auto cursor-pointer"
            >
              <div className="mb-4 text-xs font-mono text-blue-300/50 uppercase tracking-widest flex justify-between items-center">
                <span>Module {String(i + 1).padStart(2, '0')}</span>
                <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 leading-tight">
                {feature}
              </h3>
              <p className="text-sm text-blue-200/50 font-light leading-relaxed">
                Advanced multi-modal signal processing for {feature.toLowerCase()} insights.
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        className="scroll-indicator fixed bottom-10 left-1/2 -translate-x-1/2 z-20 pointer-events-none flex flex-col items-center"
        style={{ display: heroVisible ? 'flex' : 'none' }}
      >
        <span className="text-[10px] uppercase tracking-[0.5em] text-blue-300/40 mb-2">Initialize Scroll</span>
        <div className="w-[1px] h-12 bg-gradient-to-b from-blue-400 to-transparent animate-bounce" />
      </div>
    </div>
  );
}
