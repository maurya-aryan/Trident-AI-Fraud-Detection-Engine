import { useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import useFrameLoader from '../hooks/useFrameLoader';
import SequencePlayer from './SequencePlayer';

gsap.registerPlugin(ScrollTrigger);

const FRAME_COUNT = 200;
const FRAME_PATH = '/sequences/trident';

export default function TridentHero() {
  const playerRef = useRef(null);
  const sectionRef = useRef(null);

  const { frames, loaded, progress } = useFrameLoader(FRAME_PATH, FRAME_COUNT, {
    prefix: '',
    extension: 'jpg',
    padLength: 4,
  });

  // Setup GSAP Hybrid Animation
  useEffect(() => {
    if (!loaded || !playerRef.current) return;

    // Start at frame 20 as requested
    playerRef.current.setFrame(20);

    // This object tracks where the scrollbar *wants* the frame to be
    const scrollProxy = { frame: 20 };
    let isAutoPlaying = false;
    let autoPlayFinished = false;

    // The scroll timeline maps the full scroll distance to frames 20-199
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.1,
        onEnter: () => {
          // When the user starts scrolling down into this 900vh section, intercept the playback!
          if (!isAutoPlaying && !autoPlayFinished) {
            isAutoPlaying = true;
            
            // This detached Tween forces the canvas to play like a video from frame 20 to 176, ignoring the scrollbar
            const autoProxy = { frame: 20 };
            gsap.to(autoProxy, {
              frame: 176,
              duration: 3.5, // Automated playback takes 3.5 seconds
              ease: "power2.inOut",
              onUpdate: () => {
                playerRef.current?.setFrame(Math.round(autoProxy.frame));
              },
              onComplete: () => {
                isAutoPlaying = false;
                autoPlayFinished = true;
              }
            });
          }
        }
      },
    });

    // Map the scrollbar entirely from 20 to 199
    tl.to(scrollProxy, {
      frame: FRAME_COUNT - 1,
      ease: 'none',
      onUpdate: () => {
        // If the auto-play video is running, ignore the scrollbar
        // If the auto-play finished, let the scrollbar control the frames, but snap it to at least frame 176
        if (!isAutoPlaying && autoPlayFinished) {
          const currentScrollF = Math.max(176, Math.round(scrollProxy.frame));
          playerRef.current?.setFrame(currentScrollF);
        }
      },
    }, 0);

    return () => {
      tl.kill();
      ScrollTrigger.getAll().forEach(st => st.kill());
    };
  }, [loaded, frames]);

  return (
    <>
      {/* Loading State */}
      {!loaded && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#000000]">
          <div className="w-64 h-[1px] bg-white/10 relative overflow-hidden mb-6">
            <div 
              className="absolute left-0 top-0 h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${Math.round(progress * 100)}%` }}
            />
          </div>
        </div>
      )}

      {/* Frame Renderer */}
      <SequencePlayer 
        ref={playerRef} 
        frames={frames} 
        bgColor="#000000" 
      />
      
      {/* The 900vh Scroll Container gives roughly 300vh per scene so no frames are skipped by scrolling too fast */}
      <section ref={sectionRef} className="relative w-full" style={{ height: '900vh' }}>
        {/* The pinned viewport - intentionally empty to just show frames */}
        <div className="sticky top-0 h-screen w-full pointer-events-none z-[20]">
        </div>
      </section>
    </>
  );
}
