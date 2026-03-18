import { useState, useEffect } from 'react';
import logo from '../assets/TRIDENT_BGLess_Logo.png';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [activeLink, setActiveLink] = useState('Terminal');

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
      
      // Basic scroll spy logic
      const sections = ['terminal', 'architecture', 'detection'];
      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 100 && rect.bottom >= 100) {
            setActiveLink(section.charAt(0).toUpperCase() + section.slice(1));
            break;
          }
        }
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Architecture', href: '#architecture' },
    { name: 'Terminal', href: '#terminal' },
    { name: 'Detection', href: '#detection' },
  ];

  return (
    <nav 
      className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-700 flex items-center justify-center
        ${scrolled ? 'py-4 opacity-100' : 'py-6 opacity-0 translate-y-[-10px] pointer-events-none'}`}
    >
      <div className="w-[90%] max-w-[860px] bg-[#050b18]/75 backdrop-blur-3xl border border-white/7 rounded-full px-6 py-2.5 flex items-center justify-between shadow-2xl">
        {/* Logo left */}
        <div className="flex items-center">
          <img src={logo} alt="Trident AI" className="h-6 w-auto hover:opacity-80 transition-opacity cursor-pointer" />
        </div>
        
        {/* Center links - reordered: Terminal, Architecture, Detection */}
        <div className="hidden md:flex items-center gap-1 font-inter">
          {navLinks.map((link) => (
            <a 
              key={link.name}
              href={link.href}
              onClick={() => setActiveLink(link.name)}
              className={`relative px-4 py-2 text-[13px] font-[400] transition-all duration-300 rounded-[7px]
                ${activeLink === link.name 
                  ? 'text-[#e2e4ee] bg-white/5' 
                  : 'text-[#565c76] hover:text-[#a0a5be] hover:bg-white/[0.04]'}`}
            >
              {link.name}
              {activeLink === link.name && (
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-[1.5px] bg-[#2dd4a0] rounded-full" />
              )}
            </a>
          ))}
        </div>
        
        {/* Right side - version and status */}
        <div className="flex items-center gap-6 font-jetbrains">
          <span className="text-[10px] text-[#2a2f42] tracking-tight select-none">
            v2.1.0
          </span>
          <div className="flex items-center gap-2 px-[11px] py-[5px] bg-[#2dd4a0]/[0.05] border border-[#2dd4a0]/[0.12] rounded-[5px] select-none">
            <div className="w-1.5 h-1.5 rounded-full bg-[#2dd4a0] animate-status-pulse" />
            <span className="text-[10px] text-[#2dd4a0] font-bold tracking-wider">
              IMAP LIVE
            </span>
          </div>
        </div>
      </div>
    </nav>
  )
}
