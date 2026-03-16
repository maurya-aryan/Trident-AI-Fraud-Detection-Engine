import { useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import useFrameLoader from '../hooks/useFrameLoader';
import SequencePlayer from './SequencePlayer';

gsap.registerPlugin(ScrollTrigger);

const FRAME_COUNT = 444;
const FRAME_PATH = '/sequences/trident';

export default function TridentHero() {
  const playerRef = useRef(null);
  const sectionRef = useRef(null);

  const { frames, loaded, progress } = useFrameLoader(FRAME_PATH, FRAME_COUNT, {
    prefix: '',
    extension: 'jpg',
    padLength: 4,
  });

  // Wire GSAP ScrollTrigger → frame scrubbing
  useEffect(() => {
    if (!loaded || !playerRef.current) return;

    playerRef.current.setFrame(0);

    const frameObj = { frame: 0 };

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.1, // Tight scrub for immediate response
      },
    });

    // 444 total frames mapped to the scroll
    // Scene 1: Frames 0-191 (Trident comes up)
    // Scene 2: Frames 192-383 (Trident goes up)
    // Scene 3: Frames 384-443 (Ocean starts moving)
    tl.to(frameObj, {
      frame: FRAME_COUNT - 1,
      ease: 'none',
      onUpdate: () => {
        // Round to nearest frame so we don't accidentally skip frames because of snapping logic
        const currentF = Math.round(frameObj.frame);
        playerRef.current?.setFrame(currentF);
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
