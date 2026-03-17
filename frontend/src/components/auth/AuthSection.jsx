/**
 * AuthSection — full-viewport wrapper that hosts AuthPanel.
 *
 * Responsibilities:
 *  1. Occupies 100vh at the very top of the page (before HeroSection).
 *  2. Fully transparent — the Three.js fixed canvas bleeds through.
 *  3. GSAP ScrollTrigger: fades + scales the panel out as the user scrolls
 *     past the auth screen into the Hero section.
 *
 * Integration (App.jsx):
 *   import AuthSection from './components/auth';
 *   // Place it as the first child of <main>, before <HeroSection />
 *
 * Peer dependency: gsap (already installed in this project).
 */
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import AuthPanel from './AuthPanel';

gsap.registerPlugin(ScrollTrigger);

export default function AuthSection() {
  const sectionRef = useRef(null);
  const panelRef   = useRef(null);

  useEffect(() => {
    const section = sectionRef.current;
    const panel   = panelRef.current;
    if (!section || !panel) return;

    // Fade + scale out during the final 40% of the section's scroll.
    // start: '60% top' → animation begins when 60 % of the section has
    //                     scrolled past the top of the viewport (scrollY ≈ 60vh)
    // end:   'bottom top' → completes when the section is fully gone (scrollY = 100vh)
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        start: '60% top',
        end:   'bottom top',
        scrub: 0.7,
      },
    });

    tl.to(panel, { opacity: 0, scale: 0.92, y: -28, ease: 'power2.in' });

    return () => {
      tl.scrollTrigger?.kill();
      tl.kill();
    };
  }, []);

  return (
    <section
      ref={sectionRef}
      style={{
        position:       'relative',
        height:         '100vh',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'center',
        zIndex:         20,
        padding:        '0 12px',
        boxSizing:      'border-box',
        background:     'transparent', // canvas bleeds through
      }}
    >
      {/* panelRef wraps AuthPanel so GSAP animates the whole card */}
      <div ref={panelRef} style={{ width: '100%', maxWidth: '860px' }}>
        <AuthPanel />
      </div>
    </section>
  );
}
