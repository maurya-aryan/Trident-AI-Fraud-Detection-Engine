import { useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import AboutSection from './components/AboutSection';
import PipelineSection from './components/PipelineSection';
import TerminalSection from './components/TerminalSection';
import EndSection from './components/EndSection';

// Register GSAP plugins once at the top level
gsap.registerPlugin(ScrollTrigger);

function App() {
  useEffect(() => {
    // Refresh ScrollTrigger after all content mounts
    ScrollTrigger.refresh();
  }, []);

  return (
    <div className="w-full bg-background text-white/60 font-sans min-h-screen selection:bg-accent/30 selection:text-white">
      <Navbar />
      
      <main className="relative flex flex-col w-full">
        <div id="architecture">
          <HeroSection />
        </div>
        
        <AboutSection />
        
        <div id="pipeline">
          <PipelineSection />
        </div>

        <div id="terminal">
          <TerminalSection />
        </div>

        <EndSection />
      </main>
    </div>
  );
}

export default App;
