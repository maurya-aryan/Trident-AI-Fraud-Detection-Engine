import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function EndSection() {
  const canvasRef = useRef(null);
  const sectionRef = useRef(null);
  const originalContentRef = useRef(null);
  const githubContentRef = useRef(null);

  const frameCount = 104;
  const images = useRef([]);

  useEffect(() => {
    // Preload images
    const currentFrame = index => `/footer-sequence/ezgif-frame-${(index + 1).toString().padStart(3, '0')}.jpg`;
    
    let loadedCount = 0;
    for (let i = 0; i < frameCount; i++) {
        const img = new Image();
        img.src = currentFrame(i);
        images.current.push(img);
        img.onload = () => {
            loadedCount++;
            if (loadedCount === 1) {
                renderFrame(0);
            }
        };
    }

    const playhead = { frame: 0 };

    const renderFrame = (index) => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (!ctx || !images.current[index]) return;

      const img = images.current[index];
      if (img.width === 0 || img.height === 0) return;

      const r1 = img.width / img.height;
      const r2 = canvas.width / canvas.height;
      let drawWidth, drawHeight, offsetX, offsetY;
      
      if (r1 < r2) {
          drawWidth = canvas.width;
          drawHeight = canvas.width / r1;
          offsetX = 0;
          offsetY = (canvas.height - drawHeight) / 2;
      } else {
          drawWidth = canvas.height * r1;
          drawHeight = canvas.height;
          offsetX = (canvas.width - drawWidth) / 2;
          offsetY = 0;
      }
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
    };

    const handleResize = () => {
      if (canvasRef.current && sectionRef.current) {
         canvasRef.current.width = window.innerWidth;
         canvasRef.current.height = window.innerHeight;
         renderFrame(Math.round(playhead.frame));
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: 'top top',
        end: '+=400%', // Scroll for 4 screens for smooth scrubbing
        pin: true,
        scrub: 0.5,
      }
    });

    // 1. Fade out original content quickly (first 15% of scroll)
    tl.to(originalContentRef.current, {
        opacity: 0,
        y: -50,
        duration: 0.15,
        ease: 'power2.inOut'
    }, 0);

    // 2. Play the frames (104 total), taking the entire scroll timeline
    tl.to(playhead, {
      frame: frameCount - 1,
      snap: 'frame',
      ease: 'none',
      onUpdate: () => renderFrame(Math.round(playhead.frame)),
      duration: 1
    }, 0);

    // 3. Fade in the GitHub content near the end (last 25% of scroll)
    tl.fromTo(githubContentRef.current, 
      { opacity: 0, y: 50, scale: 0.95 }, 
      { opacity: 1, y: 0, scale: 1, duration: 0.25, ease: 'power2.out' }, 
      0.75
    );

    return () => {
      window.removeEventListener('resize', handleResize);
      if (tl.scrollTrigger) tl.scrollTrigger.kill();
      tl.kill();
    };
  }, []);

  return (
    <section ref={sectionRef} className="relative w-full h-screen bg-black overflow-hidden flex flex-col items-center justify-center border-t border-accent/10">
      <canvas ref={canvasRef} className="absolute inset-0 z-0 h-full w-full object-cover opacity-80" />
      
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent pointer-events-none z-10" />

      {/* Original Content */}
      <div ref={originalContentRef} className="absolute z-20 text-center max-w-2xl px-6 flex flex-col items-center justify-center">
        <h2 className="text-4xl md:text-5xl font-black mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
          Secure your entire ecosystem.
        </h2>
        <p className="text-lg text-white/60 mb-10">
          Trident AI. Built for scale, forged for protection.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button className="px-8 py-3 rounded-full bg-accent text-background font-bold hover:bg-white transition-colors duration-300 shadow-[0_0_20px_rgba(0,214,255,0.3)]">
            Initialize Trident
          </button>
          <button className="px-8 py-3 rounded-full bg-transparent border border-white/20 text-white/80 font-medium hover:border-white/50 hover:text-white transition-colors duration-300">
            View Engine Specs
          </button>
        </div>
      </div>

      {/* GitHub Content */}
      <div ref={githubContentRef} className="absolute z-30 flex flex-col items-center justify-center text-center px-6 opacity-0 pointer-events-none w-full max-w-4xl mx-auto">
        <h2 className="text-5xl md:text-7xl font-black mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-400 tracking-tight drop-shadow-2xl">
          Open Source Security
        </h2>
        <p className="text-xl md:text-2xl text-white/70 mb-12 max-w-2xl mx-auto font-light">
          Examine the underlying architecture. Help us build a more secure future by contributing to our codebase.
        </p>
        <a 
          href="https://github.com/maurya-aryan/Trident-AI-Fraud-Detection-Engine.git" 
          target="_blank" 
          rel="noopener noreferrer"
          className="pointer-events-auto flex items-center justify-center gap-4 px-10 py-5 rounded-full bg-white/10 border border-white/30 text-white font-bold text-xl hover:bg-white hover:text-black transition-all duration-300 backdrop-blur-md shadow-[0_0_40px_rgba(255,255,255,0.15)] hover:shadow-[0_0_60px_rgba(255,255,255,0.6)] transform hover:scale-105"
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

      <footer className="absolute bottom-6 w-full px-12 flex flex-col md:flex-row justify-between items-center text-xs text-white/40 font-mono z-40 gap-4">
        <div className="flex gap-6">
          <a href="#architecture" className="hover:text-accent transition-colors duration-200">Architecture</a>
          <a href="#detection" className="hover:text-accent transition-colors duration-200">Detection</a>
          <a href="#terminal" className="hover:text-accent transition-colors duration-200">Terminal</a>
        </div>
        <div className="text-center">
          <p>System Online. Copyright © 2026 TRIDENT AI Engine.</p>
        </div>
        <div className="flex gap-3 items-center">
          <span className="text-white/20">Built by</span>
          <span className="text-white/70 hover:text-accent transition-colors">Aryan Maurya</span>
          <span className="text-white/20">&</span>
          <span className="text-white/70 hover:text-accent transition-colors">Iyad</span>
        </div>
      </footer>
    </section>
  );
}

export default EndSection;
