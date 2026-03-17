import { useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import Matter from 'matter-js';

const { Engine, Runner, Bodies, Body, Composite, Events } = Matter;

/**
 * PhysicsPipeline — Scene 3: Matter.js engine overlaying the Y-funnel image.
 * Invisible static bodies aligned to the pipeline.jpeg glass edges.
 * Email bodies spawn at top, gravity splits them into fraud (left) / safe (right).
 */
const PhysicsPipeline = forwardRef(function PhysicsPipeline({ onFraudClick }, ref) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const engineRef = useRef(null);
  const runnerRef = useRef(null);
  const spawnedRef = useRef(false);

  const spawnEmails = () => {
    if (!engineRef.current || !canvasRef.current) return;

    const engine = engineRef.current;
    const canvas = canvasRef.current;
    const w = canvas.width;
    const h = canvas.height;

    const emailLabels = [
      { label: 'fraud', color: '#ff4444' },
      { label: 'safe', color: '#44ff88' },
      { label: 'fraud', color: '#ff4444' },
      { label: 'safe', color: '#44ff88' },
      { label: 'fraud', color: '#ff6644' },
      { label: 'safe', color: '#44ff88' },
      { label: 'fraud', color: '#ff4444' },
      { label: 'fraud', color: '#ff4444' },
      { label: 'safe', color: '#44ffaa' },
      { label: 'fraud', color: '#ff4444' },
      { label: 'safe', color: '#44ff88' },
      { label: 'fraud', color: '#ff6644' },
    ];

    let spawnIndex = 0;
    const interval = setInterval(() => {
      if (spawnIndex >= emailLabels.length) {
        clearInterval(interval);
        return;
      }
      const { label, color } = emailLabels[spawnIndex];
      const x = w * 0.35 + Math.random() * w * 0.3;
      const emailBody = Bodies.rectangle(x, -30, 28, 20, {
        restitution: 0.3,
        friction: 0.05,
        frictionAir: 0.01,
        label: label,
        render: {
          fillStyle: color,
          strokeStyle: label === 'fraud' ? '#ff0000' : '#00ff66',
          lineWidth: 1,
        },
      });
      emailBody.fraudType = label;
      Composite.add(engine.world, emailBody);
      spawnIndex++;
    }, 500);
  };

  // Expose activate/deactivate via ref
  useImperativeHandle(ref, () => ({
    activate: () => {
      if (!spawnedRef.current) {
        spawnedRef.current = true;
        spawnEmails();
      }
    },
  }));

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const w = container.clientWidth;
    const h = container.clientHeight;

    // Create engine
    const engine = Engine.create({ gravity: { x: 0, y: 0.6 } });
    engineRef.current = engine;

    // Setup canvas
    const canvas = canvasRef.current;
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');

    // Build invisible boundaries matching the Y-funnel shape
    const cx = w * 0.5;
    const splitY = h * 0.55;

    // Left funnel wall (angled)
    const leftWall = Bodies.rectangle(cx - w * 0.12, h * 0.23, w * 0.04, h * 0.35, {
      isStatic: true,
      angle: Math.PI * 0.05,
      render: { visible: false },
    });

    // Right funnel wall (angled)
    const rightWall = Bodies.rectangle(cx + w * 0.12, h * 0.23, w * 0.04, h * 0.35, {
      isStatic: true,
      angle: -Math.PI * 0.05,
      render: { visible: false },
    });

    // Narrow channel walls
    const leftNarrow = Bodies.rectangle(cx - w * 0.04, h * 0.47, w * 0.025, h * 0.18, {
      isStatic: true,
      render: { visible: false },
    });
    const rightNarrow = Bodies.rectangle(cx + w * 0.04, h * 0.47, w * 0.025, h * 0.18, {
      isStatic: true,
      render: { visible: false },
    });

    // Diverter triangle at the split point
    const diverter = Bodies.polygon(cx, splitY + h * 0.04, 3, w * 0.03, {
      isStatic: true,
      angle: Math.PI,
      render: { visible: false },
    });

    // Left branch walls
    const leftOuterWall = Bodies.rectangle(cx - w * 0.16, h * 0.75, w * 0.025, h * 0.3, {
      isStatic: true,
      angle: Math.PI / 7,
      render: { visible: false },
    });
    const leftInnerWall = Bodies.rectangle(cx - w * 0.06, h * 0.72, w * 0.025, h * 0.28, {
      isStatic: true,
      angle: Math.PI / 7,
      render: { visible: false },
    });

    // Right branch walls
    const rightOuterWall = Bodies.rectangle(cx + w * 0.16, h * 0.75, w * 0.025, h * 0.3, {
      isStatic: true,
      angle: -Math.PI / 7,
      render: { visible: false },
    });
    const rightInnerWall = Bodies.rectangle(cx + w * 0.06, h * 0.72, w * 0.025, h * 0.28, {
      isStatic: true,
      angle: -Math.PI / 7,
      render: { visible: false },
    });

    Composite.add(engine.world, [
      leftWall, rightWall,
      leftNarrow, rightNarrow,
      diverter,
      leftOuterWall, leftInnerWall,
      rightOuterWall, rightInnerWall,
    ]);

    // Force-based splitting at diverter
    Events.on(engine, 'beforeUpdate', () => {
      const bodies = Composite.allBodies(engine.world);
      bodies.forEach((body) => {
        if (body.isStatic) return;
        if (body.position.y > splitY - 10 && body.position.y < splitY + h * 0.1) {
          const force = body.fraudType === 'fraud' ? -0.0005 : 0.0005;
          Body.applyForce(body, body.position, { x: force, y: 0 });
        }
        if (body.position.y > h + 50) {
          Composite.remove(engine.world, body);
        }
      });
    });

    // Run engine & custom render loop
    const runner = Runner.create();
    runnerRef.current = runner;

    let animId;
    const renderLoop = () => {
      ctx.clearRect(0, 0, w, h);

      const bodies = Composite.allBodies(engine.world);
      bodies.forEach((body) => {
        if (body.isStatic) return;

        const { vertices } = body;
        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        for (let j = 1; j < vertices.length; j++) {
          ctx.lineTo(vertices[j].x, vertices[j].y);
        }
        ctx.closePath();

        // Glow effect
        ctx.shadowColor = body.render.fillStyle;
        ctx.shadowBlur = 12;
        ctx.fillStyle = body.render.fillStyle;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Envelope outline
        ctx.strokeStyle = 'rgba(255,255,255,0.6)';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Draw envelope flap
        const cx2 = body.position.x;
        const cy2 = body.position.y;
        ctx.beginPath();
        ctx.moveTo(cx2 - 8, cy2 - 5);
        ctx.lineTo(cx2, cy2 + 2);
        ctx.lineTo(cx2 + 8, cy2 - 5);
        ctx.strokeStyle = 'rgba(255,255,255,0.5)';
        ctx.stroke();
      });

      animId = requestAnimationFrame(renderLoop);
    };

    Runner.run(runner, engine);
    renderLoop();

    return () => {
      cancelAnimationFrame(animId);
      Runner.stop(runner);
      Engine.clear(engine);
    };
  }, []);

  return (
    <div className="physics-pipeline" ref={containerRef}>
      <img
        src="/images/y-funnel-base.jpg"
        alt="TRIDENT Detection Pipeline"
        className="physics-bg-layer"
      />
      <canvas
        ref={canvasRef}
        className="physics-canvas"
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
      />
      {/* Clickable hitbox for the fraud output */}
      <div
        className="fraud-box-hitbox"
        onClick={onFraudClick}
        title="Inspect detected threats"
      >
        <span className="hitbox-label">🔍 Inspect Threats</span>
      </div>
      {/* Labels */}
      <div className="pipeline-label pipeline-label-fraud">⚠️ FRAUD</div>
      <div className="pipeline-label pipeline-label-safe">✅ SAFE</div>
    </div>
  );
});

export default PhysicsPipeline;
