import React, { useRef, useMemo, useEffect, Component } from 'react';
import { Canvas, useLoader, useFrame } from '@react-three/fiber';
import { useGLTF, Center } from '@react-three/drei';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, errorInfo) { console.error("Canvas Error:", error, errorInfo); }
  render() {
    if (this.state.hasError) return <div className="text-red-500 z-50 p-10 bg-black absolute inset-0">Canvas Error: {this.state.error?.message}</div>;
    return this.props.children;
  }
}

// --- 3D Components ---

function ProceduralCity() {
  const obj = useLoader(OBJLoader, '/models/buildings.obj');
  const meshRef = useRef();

  const gridSize = 40;
  const boxSize = 3;
  const count = gridSize * gridSize;

  // Extract the geometry from the loaded OBJ
  const geometry = useMemo(() => {
    let geo;
    if (obj) {
      obj.traverse((child) => {
        if (child.isMesh && !geo) {
          geo = child.geometry;
        }
      });
    }
    return geo;
  }, [obj]);

  // Cybersecurity Material (Dark grey base, high metalness, neon red/cyan emissive)
  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: '#161616',
      metalness: 0.8,
      roughness: 0.2,
      emissive: '#0a0a0a', // very subtle glow base
    });
  }, []);

  // Compute transformation matrices for each building instance
  const matrices = useMemo(() => {
    const dummy = new THREE.Object3D();
    const mats = [];
    const minScale = 0.001;
    const maxScale = 0.009;

    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        dummy.position.set(i * boxSize, 0, j * boxSize);
        // Random height scale based on original app.js logic
        dummy.scale.set(0.01, Math.random() * (maxScale - minScale) + minScale, 0.01);
        dummy.updateMatrix();
        mats.push(dummy.matrix.clone());
      }
    }
    return mats;
  }, [gridSize, boxSize]);

  useEffect(() => {
    if (meshRef.current && matrices.length > 0) {
      matrices.forEach((mat, i) => {
        meshRef.current.setMatrixAt(i, mat);
      });
      meshRef.current.instanceMatrix.needsUpdate = true;
    }
  }, [matrices]);

  if (!geometry) return null;

  return (
    <instancedMesh ref={meshRef} args={[geometry, material, count]} position={[-gridSize - 10, -14, -gridSize - 10]} />
  );
}

function TridentModel() {
  const { scene } = useGLTF('/models/trident.glb');
  const meshRef = useRef();
  
  // Slowly rotate the trident continually
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005;
    }
  });

  // We wrap the original scene in a Center component because the original 
  // model has an extreme internal offset that places it WAY off camera.
  // The model's native size is also massive, so we drastically reduce the scale here.
  return (
    <group ref={meshRef} position={[0, -25, 0]} scale={0.005}>
      <Center>
        <primitive object={scene} />
      </Center>
    </group>
  );
}
useGLTF.preload('/models/trident.glb');

// Scene setup including Lights and Camera attached to GSAP ScrollTrigger
function Scene({ scrollContainerRef, titleRef, cardsContainerRef, cardsRef }) {
  const tridentRef = useRef(null);
  const cameraGroupRef = useRef(null);
  const cameraRef = useRef(null);

  const [targetScroll, setTargetScroll] = React.useState(0);
  const smoothScroll = useRef(0);
  const lerp = (a, b, n) => (1 - n) * a + n * b;

  useEffect(() => {
    // We use GSAP only to track the scroll position cleanly
    const st = ScrollTrigger.create({
      trigger: scrollContainerRef.current,
      start: 'top top',
      end: 'bottom bottom',
      onUpdate: (self) => {
        setTargetScroll(self.progress);
      }
    });

    return () => st.kill();
  }, [scrollContainerRef]);

  useFrame(() => {
    // The "Inertia Engine": closing 5% of the distance every frame
    smoothScroll.current = lerp(smoothScroll.current, targetScroll, 0.05);
    
    const s = smoothScroll.current;

    // --- STAGE 1 LOGIC (0.0 to 0.4 of scroll) ---
    if (tridentRef.current) {
      if (s < 0.2) {
        // 0.0 -> 0.2: Entrance (Rising from -25 to -10)
        const p = s / 0.2;
        tridentRef.current.position.y = -25 + (15 * p);
      } else if (s < 0.3) {
        // 0.2 -> 0.3: The Pause (Static @ -10)
        tridentRef.current.position.y = -10;
      } else if (s < 0.45) {
        // 0.3 -> 0.45: Exit (Shooting from -10 to 60)
        const p = (s - 0.3) / 0.15;
        // Cubic ease-in for the "shoot" effect
        const easeP = p * p * p;
        tridentRef.current.position.y = -10 + (70 * easeP);
      } else {
        // Past Stage 1: Keep it out of frame
        tridentRef.current.position.y = 60;
      }
    }

    // Camera Tilt & Alignment
    if (cameraRef.current) {
      cameraRef.current.lookAt(0, 0, 0);
    }
  });

  return (
    <>
      <ambientLight intensity={1.5} /> {/* Increased ambient light */}
      <spotLight position={[50, 100, 50]} color="#00d6ff" intensity={15000} castShadow /> {/* Brighter, cyan spot */}
      <spotLight position={[-50, 100, -50]} color="#ff0055" intensity={10000} castShadow /> {/* Neon red accent */}
      <pointLight position={[0, 20, 20]} color="#ffffff" intensity={200} /> {/* Center fill */}

      <group ref={cameraGroupRef}>
         <perspectiveCamera ref={cameraRef} makeDefault position={[0, 40, 120]} fov={35} /> {/* Moved closer, adjusted FOV */}
      </group>
      
      <React.Suspense fallback={null}>
        <ProceduralCity />
      </React.Suspense>
      
      <group ref={tridentRef} position={[0, -20, 0]}> {/* Starts lower */}
        <React.Suspense fallback={null}>
          <TridentModel />
        </React.Suspense>
      </group>
    </>
  );
}

// --- Main Page Component ---

export default function HeroSection() {
  const scrollContainerRef = useRef(null);
  
  // UI Refs
  const titleRef = useRef(null);
  const cardsContainerRef = useRef(null);
  const cardsRef = useRef([]);

  const setCardRef = (el, index) => {
    cardsRef.current[index] = el;
  };

  const featureCards = [
    "Credential Exposure", "Malware Scanner", "AI Text Detection",
    "Email Phishing", "URL Detection", "Prompt Injection",
    "Fusion Model", "Campaign Graph", "SHAP Explainer"
  ];

  return (
    <div ref={scrollContainerRef} className="relative w-full h-[800vh] bg-black">
      {/* Fixed Sticky Wrapper for Canvas and UI */}
      <div className="sticky top-0 h-screen w-full overflow-hidden">
        
        {/* ThreeJS Background Canvas */}
        <div className="absolute inset-0 z-0 bg-black">
          <ErrorBoundary>
            <Canvas gl={{ antialias: true, alpha: true }}>
              <color attach="background" args={['#000000']} />
              <fog attach="fog" args={['#000000', 1, 250]} />
              
              <Scene 
                scrollContainerRef={scrollContainerRef}
                titleRef={titleRef}
                cardsContainerRef={cardsContainerRef}
                cardsRef={cardsRef}
              />
            </Canvas>
          </ErrorBoundary>
        </div>

        {/* --- Phase 1 UI: Main Title (Temporarily hidden for Stage 1 testing) --- */}
        <div ref={titleRef} className="hidden absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none opacity-0">
            <h1 className="text-5xl md:text-7xl font-black text-white text-glow mb-4 text-center">TRIDENT</h1>
            <p className="text-xl md:text-2xl text-cyan-400 font-medium tracking-widest uppercase">AI Fraud Detection Engine</p>
        </div>

        {/* --- Phase 3 UI: The Arsenal Cards (Temporarily hidden for Stage 1 testing) --- */}
        <div ref={cardsContainerRef} className="hidden absolute inset-0 z-20 flex items-center justify-center pointer-events-none transition-colors duration-300">
           <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-[90%] max-w-6xl mx-auto p-4">
              {featureCards.map((title, i) => (
                <div 
                  key={i} 
                  ref={(el) => setCardRef(el, i)}
                  className="glass-panel p-6 rounded-xl border border-white/10 opacity-0 translate-y-10 flex items-center justify-center shadow-[0_0_30px_rgba(0,214,255,0.05)] hover:shadow-[0_0_30px_rgba(0,214,255,0.2)] hover:border-cyan-500/50 transition-all duration-300 transform"
                  style={{ pointerEvents: 'auto' }}
                >
                  <h3 className="text-lg md:text-xl font-semibold text-white/90 text-center">{title}</h3>
                </div>
              ))}
           </div>
        </div>

      </div>
    </div>
  );
}
