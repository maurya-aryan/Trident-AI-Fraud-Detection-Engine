import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function EndSection() {
  const sectionRef = useRef(null);
  const githubContentRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {

      if (githubContentRef.current) {
        gsap.fromTo(githubContentRef.current, 
          { opacity: 0, y: 30, scale: 0.98 },
          {
            opacity: 1, 
            y: 0, 
            scale: 1,
            duration: 0.8, 
            delay: 0.2,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: githubContentRef.current,
              start: 'top 85%',
              toggleActions: 'play none none reverse'
            }
          }
        );
      }
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className="relative w-full min-h-screen bg-black overflow-hidden flex flex-col items-center justify-center py-32 gap-32 border-t border-accent/10">
      
      {/* Background Glow */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-accent/3 to-black pointer-events-none z-0" />


      {/* GitHub Content */}
      <div ref={githubContentRef} className="relative z-10 flex flex-col items-center justify-center text-center px-6 w-full max-w-4xl mx-auto">
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
