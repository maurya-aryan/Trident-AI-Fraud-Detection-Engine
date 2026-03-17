import { useState, useEffect } from 'react';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav 
      className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 flex items-center justify-center
        ${scrolled ? 'py-4 opacity-100' : 'py-6 opacity-0 translate-y-[-10px] pointer-events-none'}`}
    >
      <div className="w-[90%] max-w-5xl bg-background/70 backdrop-blur-xl border border-white/10 rounded-full px-6 py-3 flex items-center justify-between shadow-lg">
        {/* Logo left */}
        <div className="text-white/90 font-bold tracking-widest text-sm uppercase">
          Trident AI
        </div>
        
        {/* Center links - Hidden on small screens */}
        <div className="hidden md:flex items-center gap-8 text-xs font-medium text-white/60">
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
          <a href="#detection" className="hover:text-white transition-colors">Detection</a>
          <a href="#terminal" className="hover:text-white transition-colors">Terminal</a>
        </div>
        
        {/* Right CTA */}
        <div>
          <button className="text-xs font-bold text-background bg-gradient-to-r from-accent to-blue-400 px-4 py-2 rounded-full hover:scale-105 transition-transform">
            Deploy Engine
          </button>
        </div>
      </div>
    </nav>
  )
}
