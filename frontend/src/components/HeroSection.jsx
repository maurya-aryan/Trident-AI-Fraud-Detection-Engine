import { useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import useFrameLoader from '../hooks/useFrameLoader';
import SequencePlayer from './SequencePlayer';

gsap.registerPlugin(ScrollTrigger);

const FRAME_COUNT = 192;
const FRAME_PATH = '/sequences/hero-rise';

export default function HeroSection() {
  const playerRef = useRef(null);
  const sectionRef = useRef(null);
  const overlayRefs = useRef([]);

  const { frames, loaded, progress } = useFrameLoader(FRAME_PATH, FRAME_COUNT, {
    prefix: '',
    extension: 'jpg',
    padLength: 4,
  });

  // Wire GSAP ScrollTrigger → frame scrubbing
  useEffect(() => {
    if (!loaded || !playerRef.current) return;

    // Draw the first frame immediately
    playerRef.current.setFrame(0);

    const frameObj = { frame: 0 };

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.3,
      },
    });

    // Scrub frames 0 → 191
    tl.to(frameObj, {
      frame: FRAME_COUNT - 1,
      snap: 'frame',
      ease: 'none',
      onUpdate: () => {
        playerRef.current?.setFrame(frameObj.frame);
      },
    }, 0);

    // Text overlay animations — synced to timeline progress
    // Overlay 0: "TRIDENT AI" title — fades in at 25%, out at 55%
    tl.fromTo(overlayRefs.current[0],
      { opacity: 0, y: 40 },
      { opacity: 1, y: 0, duration: 0.1, ease: 'power2.out' },
      0.20
    );
    tl.to(overlayRefs.current[0],
      { opacity: 0, y: -20, duration: 0.1, ease: 'power2.in' },
      0.50
    );

    // Overlay 1: Tagline — fades in at 50%, out at 75%
    tl.fromTo(overlayRefs.current[1],
      { opacity: 0, y: 40 },
      { opacity: 1, y: 0, duration: 0.1, ease: 'power2.out' },
      0.45
    );
    tl.to(overlayRefs.current[1],
      { opacity: 0, y: -20, duration: 0.1, ease: 'power2.in' },
      0.70
    );

    // Overlay 2: CTA — fades in at 80%, stays
    tl.fromTo(overlayRefs.current[2],
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.15, ease: 'power2.out' },
      0.78
    );

    return () => {
      tl.kill();
      ScrollTrigger.getAll().forEach(st => st.kill());
    };
  }, [loaded, frames]);

  return (
    <>
      {/* Loading overlay */}
      {!loaded && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background">
          <div className="relative w-48 h-1 bg-white/10 rounded-full overflow-hidden mb-4">
            <div
              className="absolute inset-y-0 left-0 bg-accent rounded-full transition-all duration-200"
              style={{ width: `${Math.round(progress * 100)}%` }}
            />
          </div>
          <p className="text-xs tracking-[0.25em] uppercase text-white/30">
            Loading TRIDENT · {Math.round(progress * 100)}%
          </p>
        </div>
      )}

      {/* The canvas layer — fixed behind everything */}
      <SequencePlayer ref={playerRef} frames={frames} bgColor="#050505" />
      
      {/* Vignette overlay to seamlessly blend the off-black frames into the background */}
      <div className="fixed inset-0 z-10 vignette-overlay" />

      {/* Scroll spacer — creates the scroll length for scrubbing */}
      <section ref={sectionRef} className="relative w-full" style={{ height: '500vh' }}>
        {/* Pinned viewport — overlay text container */}
        <div className="sticky top-0 h-screen w-full flex items-center justify-center pointer-events-none" style={{ zIndex: 20 }}>

          {/* Overlay 0: TRIDENT AI title */}
          <div
            ref={(el) => (overlayRefs.current[0] = el)}
            className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
            style={{ opacity: 0 }}
          >
            <h1 className="text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-black tracking-tight leading-none"
                style={{
                  background: 'linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(0,214,255,0.8) 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  filter: 'drop-shadow(0 0 40px rgba(0, 214, 255, 0.3))',
                }}>
              TRIDENT AI
            </h1>
          </div>

          {/* Overlay 1: Tagline */}
          <div
            ref={(el) => (overlayRefs.current[1] = el)}
            className="absolute inset-0 flex flex-col items-center justify-end pb-32 text-center px-6"
            style={{ opacity: 0 }}
          >
            <p className="text-lg sm:text-xl md:text-2xl font-semibold tracking-[0.15em] uppercase"
               style={{ color: 'rgba(0, 214, 255, 0.9)' }}>
              Absolute security. Zero compromise.
            </p>
            <p className="mt-3 text-sm md:text-base text-white/50 max-w-lg">
              Next-generation multimodal fraud detection, engineered for the speed of modern finance.
            </p>
          </div>

          {/* Overlay 2: Scroll CTA */}
          <div
            ref={(el) => (overlayRefs.current[2] = el)}
            className="absolute bottom-16 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
            style={{ opacity: 0 }}
          >
            <span className="text-xs tracking-[0.25em] uppercase text-white/40">
              Scroll to explore
            </span>
            <div className="w-px h-10 bg-gradient-to-b from-white/40 to-transparent" />
          </div>
        </div>
      </section>
    </>
  );
}
