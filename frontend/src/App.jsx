import { useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import DetectionSection from './components/DetectionSection';
import TerminalSection from './components/TerminalSection';
import EndSection from './components/EndSection.jsx';
import { Routes, Route } from 'react-router-dom';
import { AlertsPage, AlertDetailPage } from './components/trident-funnel';

// Register GSAP plugins once at the top level
gsap.registerPlugin(ScrollTrigger);

function App() {
  useEffect(() => {
    // Force scroll to top on reload
    if ('scrollRestoration' in history) {
      history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);

    // Refresh ScrollTrigger after all content mounts
    ScrollTrigger.refresh();
  }, []);

  return (
    <div className="w-full bg-background text-white/60 font-sans min-h-screen selection:bg-accent/30 selection:text-white">
      <Routes>
        <Route path="/" element={
          <>
            <Navbar />
            
            <main className="relative flex flex-col w-full">
              <div id="architecture">
                <HeroSection />
              </div>

              <div id="terminal">
                <TerminalSection />
              </div>

              <div id="detection">
                <DetectionSection />
              </div>

              <EndSection />
            </main>
          </>
        } />
        
        <Route path="/alerts/:bucket" element={<AlertsPage />} />
        <Route path="/alerts/:bucket/:id" element={<AlertDetailPage />} />
      </Routes>
    </div>
  );
}

export default App;
