import { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import Matter from 'matter-js';

const MatterCanvas = forwardRef(function MatterCanvas({ active }, ref) {
  const sceneRef = useRef(null);
  const engineRef = useRef(null);
  const renderRef = useRef(null);
  const isRunningRef = useRef(false);

  useImperativeHandle(ref, () => ({
    spawnEmail: () => {
      if (!engineRef.current || !active) return;
      const { Bodies, Composite } = Matter;
      const xPos = window.innerWidth / 2 + (Math.random() * 400 - 200); // Randomly drop near center
      
      const email = Bodies.rectangle(xPos, -50, 60, 40, {
        restitution: 0.6,
        friction: 0.05,
        density: 0.04,
        render: {
          fillStyle: 'rgba(10, 10, 12, 0.9)',
          strokeStyle: 'rgba(0, 214, 255, 0.5)',
          lineWidth: 1
        }
      });
      Composite.add(engineRef.current.world, email);
    }
  }));

  useEffect(() => {
    if (!sceneRef.current) return;

    // Setup Matter.js Engine and World
    const Engine = Matter.Engine,
          Render = Matter.Render,
          Runner = Matter.Runner,
          Bodies = Matter.Bodies,
          Composite = Matter.Composite;

    const engine = Engine.create();
    engineRef.current = engine;
    
    // Adjust gravity for a slightly "underwater/cinematic" fall
    engine.world.gravity.y = 0.8; 

    // Setup Renderer
    const render = Render.create({
      element: sceneRef.current,
      engine: engine,
      options: {
        width: window.innerWidth,
        height: window.innerHeight,
        wireframes: false,
        background: 'transparent', // Crucial: must sit over the video playing below it
        pixelRatio: window.devicePixelRatio || 1
      }
    });
    renderRef.current = render;

    // Create the "Funnel" boundaries visually aligning with Scene 3
    const cw = window.innerWidth;
    const ch = window.innerHeight;
    
    // Funnel walls (invisible but physical)
    // Left slope
    const leftWall = Bodies.rectangle(cw * 0.35, ch - 150, 400, 20, { 
      isStatic: true, angle: Math.PI / 6, render: { visible: false } 
    });
    // Right slope
    const rightWall = Bodies.rectangle(cw * 0.65, ch - 150, 400, 20, { 
      isStatic: true, angle: -Math.PI / 6, render: { visible: false } 
    });
    // Bottom catcher
    const ground = Bodies.rectangle(cw / 2, ch + 25, cw, 50, { 
      isStatic: true, render: { visible: false } 
    });

    Composite.add(engine.world, [leftWall, rightWall, ground]);

    // Handle Resize
    const handleResize = () => {
      if (renderRef.current) {
        renderRef.current.canvas.width = window.innerWidth;
        renderRef.current.canvas.height = window.innerHeight;
        // In a complex app, we'd also reposition the funnel walls here
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      Render.stop(renderRef.current);
      Runner.stop(engineRef.current);
      Composite.clear(engineRef.current.world);
      Engine.clear(engineRef.current);
      if (renderRef.current.canvas) {
        renderRef.current.canvas.remove();
      }
      renderRef.current.canvas = null;
      renderRef.current.context = null;
      renderRef.current.textures = {};
    };
  }, []);

  // Control playback based on 'active' prop
  useEffect(() => {
    if (!engineRef.current || !renderRef.current) return;
    const Runner = Matter.Runner;
    const Render = Matter.Render;

    if (active && !isRunningRef.current) {
      Render.run(renderRef.current);
      const runner = Runner.create();
      Runner.run(runner, engineRef.current);
      isRunningRef.current = true;
    } 
    // We intentionally don't pause immediately to let things settle, 
    // but in a strict setup we could call Runner.stop() if !active.
  }, [active]);

  return (
    <div 
      ref={sceneRef} 
      className="absolute inset-0 pointer-events-none z-10"
      style={{ opacity: active ? 1 : 0, transition: 'opacity 0.5s ease' }}
    />
  );
});

export default MatterCanvas;
