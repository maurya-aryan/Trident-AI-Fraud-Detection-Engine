import { useEffect, useRef, useState } from "react";
import Matter from "matter-js";

// ─── Geometry (CSS pixels) ────────────────────────────────────────────────────
const CW = 520, CH = 680, CX = CW / 2;
const PR = 45;                      // pipe radius (half-width of neck)
const AR = 30;                      // arm radius (half-width of each Y arm)
const FTY = CH * 0.06;              // funnel top Y
const FLX = CW * 0.08;              // funnel mouth left X
const FRX = CW * 0.92;              // funnel mouth right X
const NTY = CH * 0.47;              // neck top Y
const NBY = CH * 0.59;              // neck bottom Y (Y-split starts here)
const ENY = CH * 0.87;              // end Y (bottom of arms)
const LEX = CW * 0.21;              // left endpoint X
const REX = CW * 0.79;              // right endpoint X
const NLX = CX - PR;                // neck left X
const NRX = CX + PR;                // neck right X
const BALL_R = 11.5;                // ball radius for Matter.js
const CYAN = "rgba(0,212,255,";
const BALL_IMAGE_URL = "/gmail-ball.png"; // Place the user-provided icon in frontend-test/public
const ENDPOINT_BOX_W = 128;
const ENDPOINT_BOX_H = 42;
const ENDPOINT_BOX_OFFSET_Y = 26;
const SPAWN_BATCH_SIZE = 4;         // Change this to control how many balls spawn per cycle
const SPAWN_SEQUENCE_GAP_MS = 800;  // Gap between balls in one wave
const SPAWN_CYCLE_MS = SPAWN_BATCH_SIZE * SPAWN_SEQUENCE_GAP_MS;
const ROUTE_FORCE_SCALE = 0.000045;
const ABSORB_DURATION_MS = 320;
const PULSE_DURATION_MS = 520;
const BRANCH_LOCK_Y = NBY + 8;      // Approximate the marked red reference line
const BRANCH_LOCK_MIN_X_OFFSET = AR * 0.34;

// ─── Helpers ──────────────────────────────────────────────────────────────────
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y); ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r); ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function easeOutCubic(t) {
  return 1 - (1 - t) ** 3;
}

// ─── Create Physics Walls ─────────────────────────────────────────────────────
function createFunnelWalls() {
  const { Bodies } = Matter;
  const walls = [];

  // Wall options - invisible but solid
  const wallOptions = {
    isStatic: true,
    friction: 0.1,
    restitution: 0.3,
    render: { visible: false }
  };

  // Left funnel wall (angled trapezoid side)
  const leftFunnelAngle = Math.atan2(NTY - FTY, NLX - FLX);
  const leftFunnelLength = Math.sqrt((NTY - FTY) ** 2 + (NLX - FLX) ** 2);
  walls.push(Bodies.rectangle(
    (FLX + NLX) / 2,
    (FTY + NTY) / 2,
    leftFunnelLength,
    4,
    { ...wallOptions, angle: leftFunnelAngle }
  ));

  // Right funnel wall (angled trapezoid side)
  const rightFunnelAngle = Math.atan2(NTY - FTY, FRX - NRX);
  const rightFunnelLength = Math.sqrt((NTY - FTY) ** 2 + (FRX - NRX) ** 2);
  walls.push(Bodies.rectangle(
    (FRX + NRX) / 2,
    (FTY + NTY) / 2,
    rightFunnelLength,
    4,
    { ...wallOptions, angle: -rightFunnelAngle }
  ));

  // Neck walls (vertical sides)
  walls.push(Bodies.rectangle(NLX, (NTY + NBY) / 2, 4, NBY - NTY, wallOptions)); // left neck
  walls.push(Bodies.rectangle(NRX, (NTY + NBY) / 2, 4, NBY - NTY, wallOptions)); // right neck

  // Left Y-arm outer wall (curved path approximated with segments)
  const leftArmSegments = 8;
  for (let i = 0; i < leftArmSegments; i++) {
    const t1 = i / leftArmSegments;
    const t2 = (i + 1) / leftArmSegments;
    const y1 = lerp(NBY, ENY, t1);
    const y2 = lerp(NBY, ENY, t2);
    const x1 = lerp(NLX, LEX - AR, t1 ** 0.7);
    const x2 = lerp(NLX, LEX - AR, t2 ** 0.7);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    walls.push(Bodies.rectangle(
      (x1 + x2) / 2, (y1 + y2) / 2,
      length, 4,
      { ...wallOptions, angle }
    ));
  }

  // Left Y-arm inner wall
  for (let i = 0; i < leftArmSegments; i++) {
    const t1 = i / leftArmSegments;
    const t2 = (i + 1) / leftArmSegments;
    const y1 = lerp(NBY, ENY, t1);
    const y2 = lerp(NBY, ENY, t2);
    const x1 = lerp(CX, LEX + AR, t1 ** 0.7);
    const x2 = lerp(CX, LEX + AR, t2 ** 0.7);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    walls.push(Bodies.rectangle(
      (x1 + x2) / 2, (y1 + y2) / 2,
      length, 4,
      { ...wallOptions, angle }
    ));
  }

  // Right Y-arm outer wall
  for (let i = 0; i < leftArmSegments; i++) {
    const t1 = i / leftArmSegments;
    const t2 = (i + 1) / leftArmSegments;
    const y1 = lerp(NBY, ENY, t1);
    const y2 = lerp(NBY, ENY, t2);
    const x1 = lerp(NRX, REX + AR, t1 ** 0.7);
    const x2 = lerp(NRX, REX + AR, t2 ** 0.7);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    walls.push(Bodies.rectangle(
      (x1 + x2) / 2, (y1 + y2) / 2,
      length, 4,
      { ...wallOptions, angle }
    ));
  }

  // Right Y-arm inner wall
  for (let i = 0; i < leftArmSegments; i++) {
    const t1 = i / leftArmSegments;
    const t2 = (i + 1) / leftArmSegments;
    const y1 = lerp(NBY, ENY, t1);
    const y2 = lerp(NBY, ENY, t2);
    const x1 = lerp(CX, REX - AR, t1 ** 0.7);
    const x2 = lerp(CX, REX - AR, t2 ** 0.7);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    walls.push(Bodies.rectangle(
      (x1 + x2) / 2, (y1 + y2) / 2,
      length, 4,
      { ...wallOptions, angle }
    ));
  }

  // Bottom catchers (at endpoints so balls don't fall forever)
  walls.push(Bodies.rectangle(LEX, ENY + 10, AR * 2, 10, wallOptions));
  walls.push(Bodies.rectangle(REX, ENY + 10, AR * 2, 10, wallOptions));

  return walls;
}

function createSinkSensors() {
  const { Bodies } = Matter;
  return [
    Bodies.circle(LEX, ENY, 28, {
      isStatic: true,
      isSensor: true,
      label: "left-sink",
      render: { visible: false }
    }),
    Bodies.circle(REX, ENY, 28, {
      isStatic: true,
      isSensor: true,
      label: "right-sink",
      render: { visible: false }
    }),
    Bodies.rectangle(LEX, ENY + ENDPOINT_BOX_OFFSET_Y + ENDPOINT_BOX_H / 2, ENDPOINT_BOX_W + 10, ENDPOINT_BOX_H + 10, {
      isStatic: true,
      isSensor: true,
      label: "left-box-sink",
      render: { visible: false }
    }),
    Bodies.rectangle(REX, ENY + ENDPOINT_BOX_OFFSET_Y + ENDPOINT_BOX_H / 2, ENDPOINT_BOX_W + 10, ENDPOINT_BOX_H + 10, {
      isStatic: true,
      isSensor: true,
      label: "right-box-sink",
      render: { visible: false }
    })
  ];
}

// ─── Canvas Drawing Functions ─────────────────────────────────────────────────
function drawArm(ctx, nStartX, endX, isLeft) {
  const owX0 = nStartX;
  const owXe = isLeft ? endX - AR : endX + AR;
  const iwX0 = CX;
  const iwXe = isLeft ? endX + AR : endX - AR;
  const cy = lerp(NBY, ENY, 0.55);
  const owCx = lerp(owX0, owXe, 0.42);
  const iwCx = lerp(iwX0, iwXe, 0.42);

  // Fill with gradient
  ctx.beginPath();
  ctx.moveTo(owX0, NBY);
  ctx.bezierCurveTo(owCx, cy, owXe, cy, owXe, ENY);
  ctx.lineTo(iwXe, ENY);
  ctx.bezierCurveTo(iwCx, cy, iwX0, cy, iwX0, NBY);
  ctx.closePath();
  const ag = ctx.createLinearGradient(0, NBY, 0, ENY);
  ag.addColorStop(0, `${CYAN}0.12)`);
  ag.addColorStop(0.5, `${CYAN}0.06)`);
  ag.addColorStop(1, `${CYAN}0.04)`);
  ctx.fillStyle = ag;
  ctx.fill();

  // Walls with glow
  ctx.save();
  ctx.shadowColor = "#00d4ff";
  ctx.shadowBlur = 8;
  ctx.strokeStyle = `${CYAN}0.55)`;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(owX0, NBY);
  ctx.bezierCurveTo(owCx, cy, owXe, cy, owXe, ENY);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(iwX0, NBY);
  ctx.bezierCurveTo(iwCx, cy, iwXe, cy, iwXe, ENY);
  ctx.stroke();
  ctx.shadowBlur = 0;
  ctx.strokeStyle = `${CYAN}0.25)`;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(owXe, ENY);
  ctx.lineTo(iwXe, ENY);
  ctx.stroke();
  ctx.restore();
}

function drawEndpoint(ctx, x, y, label, pulseStrength, palette) {
  // Radial glow
  const glowRadius = 60 + pulseStrength * 14;
  const rg = ctx.createRadialGradient(x, y, 0, x, y, glowRadius);
  rg.addColorStop(0, `${palette.glowCore}${0.2 + pulseStrength * 0.22})`);
  rg.addColorStop(1, `${palette.glowCore}0)`);
  ctx.beginPath();
  ctx.arc(x, y, glowRadius, 0, Math.PI * 2);
  ctx.fillStyle = rg;
  ctx.fill();

  // Label box
  const bw = ENDPOINT_BOX_W, bh = ENDPOINT_BOX_H, bx = x - bw / 2, by = y + ENDPOINT_BOX_OFFSET_Y;
  ctx.save();
  ctx.shadowColor = palette.shadow;
  ctx.shadowBlur = 10;
  roundRect(ctx, bx, by, bw, bh, 4);
  ctx.fillStyle = `${palette.fill}0.18)`;
  ctx.fill();
  ctx.strokeStyle = `${palette.stroke}${0.85 + pulseStrength * 0.12})`;
  ctx.lineWidth = 1.4;
  ctx.stroke();
  ctx.restore();
  ctx.fillStyle = `${palette.text}0.96)`;
  ctx.font = "bold 12px 'Courier New',monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(label, x, by + bh / 2);

  // Circle
  ctx.save();
  ctx.shadowColor = palette.shadow;
  ctx.shadowBlur = 20 + pulseStrength * 18;
  ctx.beginPath();
  ctx.arc(x, y, 24, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(0,8,22,${0.92 - pulseStrength * 0.18})`;
  ctx.fill();
  ctx.strokeStyle = `${palette.stroke}${0.9 + pulseStrength * 0.1})`;
  ctx.lineWidth = 2 + pulseStrength * 1.5;
  ctx.stroke();
  ctx.restore();

  if (pulseStrength > 0.01) {
    ctx.save();
    ctx.strokeStyle = `${palette.ring}${pulseStrength * 0.62})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x, y, 28 + pulseStrength * 10, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  ctx.fillStyle = `${palette.stroke}1)`;
  ctx.font = "bold 14px 'Courier New',monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("✓", x, y);
}

function drawAbsorbEffects(ctx, image, effects, now) {
  if (!image) return;

  effects.forEach((effect) => {
    const progress = clamp((now - effect.startedAt) / ABSORB_DURATION_MS, 0, 1);
    const eased = easeOutCubic(progress);
    const x = lerp(effect.startX, effect.targetX, eased);
    const y = lerp(effect.startY, effect.targetY, eased);
    const scale = lerp(1, 0.2, eased);
    const alpha = 1 - eased;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    ctx.shadowColor = "#6edbff";
    ctx.shadowBlur = 18 * alpha;
    ctx.drawImage(image, -BALL_R, -BALL_R, BALL_R * 2, BALL_R * 2);
    ctx.restore();
  });
}

function drawScene(ctx, now, endpointPulseTimestamps) {
  ctx.clearRect(0, 0, CW, CH);

  // Funnel trapezoid fill with enhanced gradient
  ctx.beginPath();
  ctx.moveTo(FLX, FTY);
  ctx.lineTo(FRX, FTY);
  ctx.lineTo(NRX, NTY);
  ctx.lineTo(NLX, NTY);
  ctx.closePath();
  const fg = ctx.createLinearGradient(0, FTY, 0, NTY);
  fg.addColorStop(0, `${CYAN}0.05)`);
  fg.addColorStop(0.5, `${CYAN}0.12)`);
  fg.addColorStop(1, `${CYAN}0.14)`);
  ctx.fillStyle = fg;
  ctx.fill();

  // Neck fill
  const ng = ctx.createLinearGradient(0, NTY, 0, NBY);
  ng.addColorStop(0, `${CYAN}0.14)`);
  ng.addColorStop(1, `${CYAN}0.10)`);
  ctx.fillStyle = ng;
  ctx.fillRect(NLX, NTY, PR * 2, NBY - NTY);

  // Y arms
  drawArm(ctx, NLX, LEX, true);
  drawArm(ctx, NRX, REX, false);

  // Funnel walls with enhanced 3D effect
  ctx.save();
  ctx.shadowColor = "#00d4ff";
  ctx.shadowBlur = 10;
  ctx.strokeStyle = `${CYAN}0.65)`;
  ctx.lineWidth = 2.5;
  [
    [FLX, FTY, NLX, NTY],
    [FRX, FTY, NRX, NTY],
    [NLX, NTY, NLX, NBY],
    [NRX, NTY, NRX, NBY]
  ].forEach(([x0, y0, x1, y1]) => {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
  });
  ctx.strokeStyle = `${CYAN}0.28)`;
  ctx.shadowBlur = 3;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(FLX, FTY);
  ctx.lineTo(FRX, FTY);
  ctx.stroke();
  ctx.restore();

  // Endpoint circles + labels
  const leftPulseStrength = endpointPulseTimestamps.left
    ? 1 - clamp((now - endpointPulseTimestamps.left) / PULSE_DURATION_MS, 0, 1)
    : 0;
  const rightPulseStrength = endpointPulseTimestamps.right
    ? 1 - clamp((now - endpointPulseTimestamps.right) / PULSE_DURATION_MS, 0, 1)
    : 0;

  const fraudPalette = {
    glowCore: "rgba(255,60,60,",
    fill: "rgba(255,40,40,",
    stroke: "rgba(255,72,72,",
    text: "rgba(255,96,96,",
    shadow: "#ff3b3b",
    ring: "rgba(255,160,160,"
  };
  const safePalette = {
    glowCore: "rgba(50,255,120,",
    fill: "rgba(40,220,90,",
    stroke: "rgba(84,255,144,",
    text: "rgba(150,255,190,",
    shadow: "#2bff7a",
    ring: "rgba(170,255,200,"
  };

  drawEndpoint(ctx, LEX, ENY, "FRAUD", leftPulseStrength, fraudPalette);
  drawEndpoint(ctx, REX, ENY, "SAFE", rightPulseStrength, safePalette);
}

// ─── React Component ──────────────────────────────────────────────────────────
export default function EmailFunnel() {
  const canvasRef = useRef(null);
  const sectionRef = useRef(null);
  const engineRef = useRef(null);
  const runnerRef = useRef(null);
  const ballBodiesRef = useRef([]);
  const absorbEffectsRef = useRef([]);
  const endpointPulseRef = useRef({ left: 0, right: 0 });
  const gmailImageRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [isDocumentVisible, setIsDocumentVisible] = useState(!document.hidden);

  // Load Gmail icon as Image
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      gmailImageRef.current = img;
    };
    img.onerror = () => {
      gmailImageRef.current = null;
      console.warn(`Ball image failed to load at ${BALL_IMAGE_URL}`);
    };
    img.src = BALL_IMAGE_URL;
    return () => {
      gmailImageRef.current = null;
    };
  }, []);

  // Init canvas + draw static scene
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = CW * dpr;
    canvas.height = CH * dpr;
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    drawScene(ctx, performance.now(), endpointPulseRef.current);
  }, []);

  // IntersectionObserver — run animation only while at least 20% visible
  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => {
        setIsVisible(e.isIntersecting && e.intersectionRatio >= 0.2);
      },
      { threshold: 0.2 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsDocumentVisible(!document.hidden);
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  // Matter.js Physics Engine
  useEffect(() => {
    if (!isVisible || !isDocumentVisible) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const { Engine, Runner, World, Bodies, Body, Events } = Matter;

    // Create engine
    const engine = Engine.create({
      gravity: { x: 0, y: 0.25 }
    });
    engine.positionIterations = 8;
    engine.velocityIterations = 6;
    engineRef.current = engine;

    // Add walls to world
    const walls = createFunnelWalls();
    const sinks = createSinkSensors();
    World.add(engine.world, [...walls, ...sinks]);

    const spawnBallAtIndex = (index) => {
      const laneOffset = SPAWN_BATCH_SIZE === 1 ? 0 : (index - (SPAWN_BATCH_SIZE - 1) / 2) * (BALL_R * 2.6);
      const startX = CX + laneOffset + (Math.random() - 0.5) * 10;
      const route = index < SPAWN_BATCH_SIZE / 2 ? -1 : 1;
      const ball = Bodies.circle(startX, -32, BALL_R, {
        restitution: 0.1,
        friction: 0.02,
        frictionAir: 0.0038,
        density: 0.001,
        label: "email-ball",
        render: { visible: false }
      });
      ball.plugin.route = route;
      World.add(engine.world, ball);
      ballBodiesRef.current.push(ball);
    };

    const seedTimeouts = [];
    const scheduleSequence = (delayOffset = 0) => {
      for (let index = 0; index < SPAWN_BATCH_SIZE; index++) {
        seedTimeouts.push(setTimeout(() => spawnBallAtIndex(index), delayOffset + index * SPAWN_SEQUENCE_GAP_MS));
      }
    };

    scheduleSequence(0);
    const spawnInterval = setInterval(() => scheduleSequence(0), SPAWN_CYCLE_MS);

    Events.on(engine, "beforeUpdate", () => {
      ballBodiesRef.current.forEach((body) => {
        const { x, y } = body.position;

        // Once a ball is below the lock line and clearly inside a branch,
        // keep the branch it already entered to prevent roll-back switching.
        if (y > BRANCH_LOCK_Y && Math.abs(x - CX) > BRANCH_LOCK_MIN_X_OFFSET) {
          const branchSide = x < CX ? -1 : 1;
          if (!body.plugin.routeLocked && branchSide !== (body.plugin.route || 1)) {
            body.plugin.route = branchSide;
            body.plugin.routeLocked = true;
          }
        }

        if (y > NBY - 16 && y < ENY + 20) {
          const progress = clamp((y - NBY) / (ENY - NBY), 0, 1);
          const route = body.plugin.route || 1;
          const endpointX = route < 0 ? LEX : REX;
          const innerStartX = CX + route * (AR * 0.35);
          const targetX = lerp(innerStartX, endpointX, progress ** 0.72);
          const horizontalError = targetX - x;
          const horizontalForce = clamp(horizontalError * ROUTE_FORCE_SCALE, -0.00022, 0.00022);
          Body.applyForce(body, body.position, { x: horizontalForce, y: 0.00001 });
        }
      });
    });

    Events.on(engine, "collisionStart", (event) => {
      event.pairs.forEach(({ bodyA, bodyB }) => {
        const isBallA = bodyA.label === "email-ball";
        const isBallB = bodyB.label === "email-ball";
        const isSinkA = bodyA.label === "left-sink" || bodyA.label === "right-sink" || bodyA.label === "left-box-sink" || bodyA.label === "right-box-sink";
        const isSinkB = bodyB.label === "left-sink" || bodyB.label === "right-sink" || bodyB.label === "left-box-sink" || bodyB.label === "right-box-sink";

        if ((isBallA && isSinkB) || (isBallB && isSinkA)) {
          const ball = isBallA ? bodyA : bodyB;
          const sink = isSinkA ? bodyA : bodyB;
          const side = sink.label.startsWith("left") ? "left" : "right";
          const targetX = side === "left" ? LEX : REX;
          const targetY = ENY;

          absorbEffectsRef.current.push({
            startX: ball.position.x,
            startY: ball.position.y,
            targetX,
            targetY,
            startedAt: performance.now()
          });
          endpointPulseRef.current[side] = performance.now();
          World.remove(engine.world, ball);
          ballBodiesRef.current = ballBodiesRef.current.filter((b) => b.id !== ball.id);
        }
      });
    });

    // Start physics runner — configure it to prevent maxUpdates errors
    // when the browser tab is hidden and delta times become huge.
    const runner = Runner.create({
      isFixed: true,
      delta: 1000 / 60
    });
    runnerRef.current = runner;
    Runner.run(runner, engine);

    // Animation loop for rendering
    const ctx = canvas.getContext("2d");
    let animationId;

    function animate() {
      const now = performance.now();
      absorbEffectsRef.current = absorbEffectsRef.current.filter(
        (effect) => now - effect.startedAt < ABSORB_DURATION_MS
      );

      drawScene(ctx, now, endpointPulseRef.current);

      // Draw balls as Gmail icons
      ballBodiesRef.current.forEach((body) => {
        if (!gmailImageRef.current) return;

        const { x, y } = body.position;
        const angle = body.angle;

        // Only draw if ball is within canvas bounds (with margin)
        if (y > -50 && y < CH + 50) {
          ctx.save();
          ctx.translate(x, y);
          ctx.rotate(angle);

          // Glow effect
          ctx.shadowColor = "#4285F4";
          ctx.shadowBlur = 15;

          // Draw Gmail icon
          ctx.drawImage(
            gmailImageRef.current,
            -BALL_R,
            -BALL_R,
            BALL_R * 2,
            BALL_R * 2
          );

          ctx.restore();
        }
      });

      drawAbsorbEffects(ctx, gmailImageRef.current, absorbEffectsRef.current, now);

      animationId = requestAnimationFrame(animate);
    }

    animate();

    // Cleanup
    return () => {
      seedTimeouts.forEach(clearTimeout);
      clearInterval(spawnInterval);
      if (animationId) cancelAnimationFrame(animationId);
      if (runnerRef.current) Runner.stop(runnerRef.current);
      if (engineRef.current) {
        World.clear(engineRef.current.world, false);
        Engine.clear(engineRef.current);
      }
      absorbEffectsRef.current = [];
      ballBodiesRef.current = [];
    };
  }, [isVisible, isDocumentVisible]);

  return (
    <section
      ref={sectionRef}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 16px",
        position: "relative",
        overflow: "hidden",
        perspective: "1200px" // 3D perspective
      }}
    >


      {/* Canvas card with 3D transform */}
      <div
        style={{
          zIndex: 1,
          borderRadius: "16px",
          overflow: "hidden",
          border: "1px solid rgba(0,212,255,0.15)",
          background: "rgba(0,212,255,0.02)",
          boxShadow: "0 0 100px rgba(0,212,255,0.055), 0 20px 60px rgba(0,0,0,0.5)",
          transform: "rotateX(2deg) rotateY(-1deg)", // Subtle 3D tilt
          transformStyle: "preserve-3d",
          transition: "transform 0.3s ease",
          width: "100%",
          maxWidth: `${CW}px`
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "rotateX(0deg) rotateY(0deg) scale(1.02)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "rotateX(2deg) rotateY(-1deg)";
        }}
      >
        <canvas
          ref={canvasRef}
          style={{
            display: "block",
            width: "100%",
            height: "auto",
            aspectRatio: `${CW}/${CH}`
          }}
        />
      </div>

    </section>
  );
}
