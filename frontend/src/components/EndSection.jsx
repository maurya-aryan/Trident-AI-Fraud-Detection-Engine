import React, { useEffect, useRef, useState, useMemo } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function EndSection() {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const scene1Ref = useRef(null);
  const scene2Ref = useRef(null);
  const githubContentRef = useRef(null);
  const footerRef = useRef(null);
  const [loaded, setLoaded] = useState(0);
  const [loading, setLoading] = useState(true);

  const frameCount = 104;

  // Create an array of image objects
  const images = useMemo(() => {
    const imgs = [];
    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      img.src = `/footer-sequence/ezgif-frame-${String(i).padStart(3, '0')}.jpg`;
      imgs.push(img);
    }
    return imgs;
  }, [frameCount]);

  useEffect(() => {
    let loadedCount = 0;

    // Safety timeout in case images fail to load
    const fallbackTimeout = setTimeout(() => {
      if (loading) setLoading(false);
    }, 5000);

    const handleLoad = () => {
      loadedCount++;
      setLoaded(loadedCount);
      if (loadedCount === frameCount) {
        setLoading(false);
        clearTimeout(fallbackTimeout);
      }
    };

    images.forEach(img => {
      if (img.complete) {
        handleLoad();
      } else {
        img.addEventListener('load', handleLoad);
        // Error handling as well just in case
        img.addEventListener('error', handleLoad);
      }
    });

    return () => {
      clearTimeout(fallbackTimeout);
      images.forEach(img => {
        img.removeEventListener('load', handleLoad);
        img.removeEventListener('error', handleLoad);
      });
    };
  }, [images, frameCount, loading]);

  useEffect(() => {
    if (loading) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d');

    // Set canvas dimensions
    const updateCanvasDimensions = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      renderFrame(0);
    };

    const renderFrame = (index) => {
      if (!images[index] || !images[index].complete) return;
      const img = images[index];

      // Calculate object-fit: cover
      const hRatio = canvas.width / img.width;
      const vRatio = canvas.height / img.height;
      const ratio = Math.max(hRatio, vRatio);

      const centerShift_x = (canvas.width - img.width * ratio) / 2;
      const centerShift_y = (canvas.height - img.height * ratio) / 2;

      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(img, 0, 0, img.width, img.height,
        centerShift_x, centerShift_y, img.width * ratio, img.height * ratio);
    };

    window.addEventListener('resize', updateCanvasDimensions);
    updateCanvasDimensions(); // Initial draw

    // GSAP ScrollTrigger Sequence
    const frameObj = { frame: 0 };

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top top',
          end: 'bottom bottom',
          scrub: 1.3, // Increased lag to slow dow smooth scrubbing momentum
        }
      });

      // Frame scrubbing
      tl.to(frameObj, {
        frame: frameCount - 1,
        snap: 'frame',
        ease: 'none',
        onUpdate: () => renderFrame(Math.round(frameObj.frame)),
        duration: 1
      }, 0);

      // UI Animations synced to scroll

      // Initial state hide
      gsap.set([scene1Ref.current, scene2Ref.current], { opacity: 0, y: 30 });
      gsap.set(githubContentRef.current, { opacity: 0, y: 30, scale: 0.98 });
      gsap.set(footerRef.current, { opacity: 0, y: 20 });

      // Scene 1: The Surface
      tl.to(scene1Ref.current, { opacity: 1, y: 0, duration: 0.1, ease: "power2.out" }, 0.05)
        .to(scene1Ref.current, { opacity: 0, y: -30, duration: 0.1, ease: "power2.in" }, 0.25);

      // Scene 2: Deep Inspection
      tl.to(scene2Ref.current, { opacity: 1, y: 0, duration: 0.1, ease: "power2.out" }, 0.35)
        .to(scene2Ref.current, { opacity: 0, y: -30, duration: 0.1, ease: "power2.in" }, 0.55);

      // Scene 3: GitHub CTA Open Source
      tl.to(githubContentRef.current, { opacity: 1, y: 0, scale: 1, duration: 0.15, ease: "power2.out" }, 0.65)
        .to(githubContentRef.current, { opacity: 1, duration: 0.2 }, 0.80);

      // Fade in footer at the very end
      tl.to(footerRef.current, { opacity: 1, y: 0, duration: 0.1, ease: "power2.out" }, 0.85);

    }, containerRef);

    return () => {
      window.removeEventListener('resize', updateCanvasDimensions);
      ctx.revert();
    };
  }, [loading, images]);

  return (
    <div ref={containerRef} className="relative w-full h-[250vh] bg-black">
      <div className="sticky top-0 w-full h-[100vh] overflow-hidden">

        {/* Loading overlay */}
        {loading && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black">
            <div className="text-white text-xl font-mono flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin" />
              <span className="text-white/60 tracking-widest text-sm uppercase mt-4">Loaded {Math.round((loaded / frameCount) * 100)}%</span>
            </div>
          </div>
        )}

        {/* Canvas Background */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full object-cover z-0"
        />

        {/* Background Gradients for legibility */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#020a14] via-transparent to-[#020a14]/60 pointer-events-none z-0" />
        <div className="absolute inset-0 bg-black/50 pointer-events-none z-0" />

        {/* Scene 1 Overlay */}
        <div ref={scene1Ref} className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center px-4 w-full max-w-4xl mx-auto pointer-events-none">
          <div className="bg-white/5 border border-white/10 backdrop-blur-md rounded-3xl p-10 shadow-2xl">
            <h2 className="text-3xl md:text-5xl font-black mb-4 text-white tracking-tight">
              The Surface
            </h2>
            <p className="text-lg md:text-xl text-blue-200/70 font-light">
              Monitoring the vast ocean of digital transactions.
            </p>
          </div>
        </div>

        {/* Scene 2 Overlay */}
        <div ref={scene2Ref} className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center px-4 w-full max-w-4xl mx-auto pointer-events-none">
          <div className="flex flex-col items-start w-full md:pl-20">
            <h2 className="text-4xl md:text-6xl font-black mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-white tracking-widest uppercase">
              Deep Inspection
            </h2>
            <p className="text-xl md:text-2xl text-blue-100/60 font-mono border-l-2 border-blue-500 pl-6 text-left max-w-lg">
              Penetrating below the surface to uncover hidden threats.
            </p>
          </div>
        </div>

        {/* Scene 3 / GitHub Content Overlay */}
        <div ref={githubContentRef} className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center px-4 w-full max-w-4xl mx-auto pointer-events-none pt-10 pb-20">
          <div className="pointer-events-auto">
            <h2 className="text-4xl md:text-6xl font-black mb-4 bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-400 tracking-tight drop-shadow-2xl">
              Open Source Security
            </h2>
            <p className="text-lg md:text-xl text-white/70 mb-8 max-w-2xl mx-auto font-light">
              Examine the underlying architecture. Help us build a more secure future by contributing to our codebase.
            </p>
            <a
              href="https://github.com/maurya-aryan/Trident-AI-Fraud-Detection-Engine.git"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full bg-white/10 border border-white/30 text-white font-bold text-lg hover:bg-white hover:text-black transition-all duration-300 backdrop-blur-md shadow-[0_0_40px_rgba(255,255,255,0.15)] hover:shadow-[0_0_60px_rgba(255,255,255,0.6)] transform hover:scale-105"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="28" height="28" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              >
                <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
                <path d="M9 18c-4.51 2-5-2-7-2" />
              </svg>
              <span>View on GitHub</span>
            </a>
          </div>
        </div>

        {/* Footer */}
        <footer ref={footerRef} className="absolute bottom-6 w-full px-12 flex flex-col md:flex-row justify-between items-center text-xs text-white/40 font-mono z-40 gap-4">
          <div className="flex gap-6 pointer-events-auto">
            <a href="#architecture" className="hover:text-accent transition-colors duration-200">Architecture</a>
            <a href="#detection" className="hover:text-accent transition-colors duration-200">Detection</a>
            <a href="#terminal" className="hover:text-accent transition-colors duration-200">Terminal</a>
          </div>
          <div className="text-center">
            <p>System Online. Copyright © 2026 TRIDENT AI Engine.</p>
          </div>
        </footer>

      </div>
    </div>
  );
}

export default EndSection;
