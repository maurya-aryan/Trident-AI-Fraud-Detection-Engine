import { useRef, useEffect, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import SequencePlayer from './components/SequencePlayer';
import FeatureRow from './components/FeatureRow';
import PhysicsPipeline from './components/PhysicsPipeline';
import InboxOverlay from './components/InboxOverlay';
import InteractiveTerminal from './components/InteractiveTerminal';
import useFrameLoader from './hooks/useFrameLoader';

gsap.registerPlugin(ScrollTrigger);

const SCENE1_FRAMES = 91;
const SCENE2_FRAMES = 120;
const SCENE3_FRAMES = 15;

export default function App() {
  const sequenceRef = useRef(null);
  const scene1Ref = useRef(null);
  const scene2Ref = useRef(null);
  const scene3Ref = useRef(null);
  const scene5Ref = useRef(null);
  const scene6Ref = useRef(null);
  const physicsPipelineRef = useRef(null);
  const [inboxOpen, setInboxOpen] = useState(false);
  const [activeSequence, setActiveSequence] = useState('hero-rise');
  const [canvasOpacity, setCanvasOpacity] = useState(0);

  // Preload all frame sequences
  const heroRise = useFrameLoader('/sequences/hero-rise', SCENE1_FRAMES);
  const heroRight = useFrameLoader('/sequences/hero-right', SCENE2_FRAMES);
  const heroHover = useFrameLoader('/sequences/hero-hover', SCENE3_FRAMES);

  // Get the current active frames
  const getActiveFrames = () => {
    switch (activeSequence) {
      case 'hero-rise': return heroRise.frames;
      case 'hero-right': return heroRight.frames;
      case 'hero-hover': return heroHover.frames;
      default: return heroRise.frames;
    }
  };

  // Scene 1 — Auto-play on load
  useEffect(() => {
    if (!heroRise.loaded || !sequenceRef.current) return;

    setActiveSequence('hero-rise');
    const frameObj = { frame: 0 };

    // Reveal canvas
    gsap.to({}, {
      duration: 0.5,
      onComplete: () => setCanvasOpacity(1),
    });

    // Auto-play frames
    gsap.to(frameObj, {
      frame: SCENE1_FRAMES - 1,
      snap: 'frame',
      duration: 3,
      ease: 'power2.out',
      onUpdate: () => {
        sequenceRef.current?.setFrame(frameObj.frame);
      },
    });

    // Fade in hero UI
    gsap.to('.hero-ui-layer', {
      opacity: 1,
      y: 0,
      delay: 2,
      duration: 1,
      ease: 'power2.out',
    });

    gsap.to('.hero-subtitle', {
      opacity: 1,
      y: 0,
      delay: 2.5,
      duration: 0.8,
    });

    gsap.to('.hero-scroll-hint', {
      opacity: 1,
      delay: 3.5,
      duration: 1,
    });
  }, [heroRise.loaded]);

  // Scene 2 — Scroll-driven
  useEffect(() => {
    if (!heroRight.loaded || !scene2Ref.current || !sequenceRef.current) return;

    const frameObj = { frame: 0 };

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: scene2Ref.current,
        start: 'top top',
        end: '+=200%',
        scrub: 0.5,
        pin: true,
        onEnter: () => setActiveSequence('hero-right'),
        onLeaveBack: () => setActiveSequence('hero-rise'),
      },
    });

    tl.to(frameObj, {
      frame: SCENE2_FRAMES - 1,
      snap: 'frame',
      onUpdate: () => {
        if (activeSequence === 'hero-right' || true) {
          sequenceRef.current?.setFrame(frameObj.frame);
        }
      },
    }, 0);

    tl.fromTo('.feature-row',
      { opacity: 0, x: -50 },
      { opacity: 1, x: 0, stagger: 0.1 },
      0.2,
    );

    return () => {
      tl.kill();
    };
  }, [heroRight.loaded]);

  // Scene 3 — Physics pipeline
  useEffect(() => {
    if (!scene3Ref.current) return;

    ScrollTrigger.create({
      trigger: scene3Ref.current,
      start: 'top 80%',
      onEnter: () => {
        setCanvasOpacity(0);
        gsap.to('.physics-pipeline', { opacity: 1, duration: 0.5 });
        physicsPipelineRef.current?.activate();
      },
      onLeaveBack: () => {
        setCanvasOpacity(1);
        gsap.to('.physics-pipeline', { opacity: 0, duration: 0.5 });
      },
    });
  }, []);

  // Scene 5 — Terminal entrance
  useEffect(() => {
    if (!scene5Ref.current) return;

    gsap.fromTo('.terminal-container',
      { y: 100, opacity: 0 },
      {
        y: 0, opacity: 1,
        scrollTrigger: {
          trigger: scene5Ref.current,
          start: 'top 80%',
        },
      },
    );
  }, []);

  // Scene 6 — Final CTA with looping video
  useEffect(() => {
    if (!heroHover.loaded || !scene6Ref.current || !sequenceRef.current) return;

    let loopAnim;

    ScrollTrigger.create({
      trigger: scene6Ref.current,
      start: 'top center',
      onEnter: () => {
        gsap.to('.terminal-container', { opacity: 0, y: 50, duration: 0.5 });
        setActiveSequence('hero-hover');
        setCanvasOpacity(1);

        // Start looping
        const frameObj = { frame: 0 };
        loopAnim = gsap.to(frameObj, {
          frame: SCENE3_FRAMES - 1,
          snap: 'frame',
          duration: SCENE3_FRAMES / 15,
          ease: 'none',
          repeat: -1,
          onUpdate: () => {
            sequenceRef.current?.setFrame(frameObj.frame);
          },
        });

        gsap.to('.final-cta-layer', {
          opacity: 1,
          y: 0,
          delay: 0.5,
          duration: 0.8,
        });
      },
      onLeaveBack: () => {
        if (loopAnim) loopAnim.kill();
        setCanvasOpacity(0);
        gsap.to('.final-cta-layer', { opacity: 0, duration: 0.3 });
      },
    });
  }, [heroHover.loaded]);

  // Handle inbox open from physics
  const handleFraudClick = (e) => {
    gsap.to('.physics-pipeline', {
      scale: 25,
      transformOrigin: `${e?.clientX || '50%'}px ${e?.clientY || '50%'}px`,
      filter: 'blur(10px) brightness(0.4)',
      duration: 0.8,
      ease: 'power3.inOut',
    });
    setTimeout(() => setInboxOpen(true), 400);
  };

  const handleInboxClose = () => {
    setInboxOpen(false);
    gsap.to('.physics-pipeline', {
      scale: 1,
      filter: 'none',
      duration: 0.6,
      ease: 'power3.out',
    });
  };

  // Loading screen
  const allLoaded = heroRise.loaded;
  if (!allLoaded) {
    const progress = Math.round(heroRise.progress * 100);
    return (
      <div className="loading-screen">
        <div className="loading-trident">TRIDENT</div>
        <div className="loading-bar-track">
          <div className="loading-bar-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="loading-text">Loading assets... {progress}%</div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Fixed canvas for all frame sequences */}
      <SequencePlayer
        ref={sequenceRef}
        frames={getActiveFrames()}
        style={{ opacity: canvasOpacity }}
      />
      {/* Override canvas opacity via inline style */}
      <style>{`.sequence-canvas { opacity: ${canvasOpacity}; transition: opacity 0.5s ease; }`}</style>

      {/* Scene 1 — Hero */}
      <section className="scene scene-1" ref={scene1Ref}>
        <div className="hero-ui-layer">
          <h1 className="hero-title">TRIDENT</h1>
          <p className="hero-subtitle">Detect. Explain. Act.</p>
          <p className="hero-tagline">Fraud defense built for modern transactions.</p>
        </div>
        <div className="hero-scroll-hint">
          <span className="scroll-arrow">↓</span>
          <span>Scroll to explore</span>
        </div>
      </section>

      {/* Scene 2 — Arsenal */}
      <section className="scene scene-2-container" ref={scene2Ref}>
        <div className="scene-2-content">
          <h2 className="section-title">The Arsenal</h2>
          <p className="section-subtitle">9 specialized modules. One unified threat score.</p>
          <FeatureRow />
        </div>
      </section>

      {/* Scene 3 — Physics Pipeline */}
      <section className="scene scene-3-container" ref={scene3Ref}>
        <div className="scene-3-header">
          <h2 className="section-title">The Detection Pipeline</h2>
          <p className="section-subtitle">Watch emails flow through the TRIDENT engine in real-time.</p>
        </div>
        <PhysicsPipeline ref={physicsPipelineRef} onFraudClick={handleFraudClick} />
      </section>

      {/* Scene 4 — Inbox Overlay (mounted on click) */}
      <InboxOverlay isOpen={inboxOpen} onClose={handleInboxClose} />

      {/* Scene 5 — Terminal */}
      <section className="scene scene-5-container" ref={scene5Ref}>
        <h2 className="section-title">The Engine Room</h2>
        <p className="section-subtitle">Execute a live detection against the TRIDENT backend.</p>
        <InteractiveTerminal />
      </section>

      {/* Scene 6 — Final CTA */}
      <section className="scene scene-6-container" ref={scene6Ref}>
        <div className="final-cta-layer">
          <h2 className="cta-title">Ready to Defend?</h2>
          <p className="cta-subtitle">TRIDENT — AI-powered fraud detection at scale.</p>
          <button className="cta-button">Get Started</button>
        </div>
      </section>
    </div>
  );
}
