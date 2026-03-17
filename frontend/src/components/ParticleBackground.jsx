import { useEffect, useRef } from "react";

const COUNT = 90;
const CONNECT_DIST = 110;
const MOUSE_DIST = 140;
const MOUSE_REPEL = 0.018;

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

function getColor(type, alpha) {
  if (type === "cyan") return `rgba(0,255,231,${alpha})`;
  if (type === "blue") return `rgba(80,160,255,${alpha})`;
  return `rgba(200,240,255,${alpha})`;
}

function createParticle(W, H) {
  const types = ["cyan", "cyan", "cyan", "cyan", "cyan", "blue", "blue", "white"];
  return {
    x: rand(0, W),
    y: rand(0, H),
    vx: rand(-0.25, 0.25),
    vy: rand(-0.25, 0.25),
    r: rand(1.2, 2.8),
    pulse: rand(0, Math.PI * 2),
    pulseSpeed: rand(0.015, 0.04),
    color: types[Math.floor(Math.random() * types.length)],
  };
}

export default function ParticleBackground({ children }) {
  const canvasRef = useRef(null);
  const wrapRef = useRef(null);
  const mouseRef = useRef({ x: -9999, y: -9999 });
  const particlesRef = useRef([]);
  const rafRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const wrap = wrapRef.current;
    const ctx = canvas.getContext("2d");

    let W, H;

    function resize() {
      W = canvas.width = wrap.offsetWidth;
      H = canvas.height = wrap.offsetHeight;
    }

    function init() {
      resize();
      particlesRef.current = Array.from({ length: COUNT }, () =>
        createParticle(W, H)
      );
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      const particles = particlesRef.current;
      const mouse = mouseRef.current;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Pulse
        p.pulse += p.pulseSpeed;
        const glow = 0.55 + 0.45 * Math.sin(p.pulse);

        // Mouse repulsion
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const md = Math.sqrt(dx * dx + dy * dy);
        if (md < MOUSE_DIST && md > 0) {
          const force = (MOUSE_DIST - md) / MOUSE_DIST;
          p.vx -= (dx / md) * force * MOUSE_REPEL;
          p.vy -= (dy / md) * force * MOUSE_REPEL;
        }

        // Damping + movement
        p.vx *= 0.998;
        p.vy *= 0.998;
        p.x += p.vx;
        p.y += p.vy;

        // Wrap edges
        if (p.x < 0) p.x = W;
        else if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H;
        else if (p.y > H) p.y = 0;

        // Draw particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * glow, 0, Math.PI * 2);
        ctx.fillStyle = getColor(p.color, 0.7 * glow);
        ctx.shadowBlur = 8;
        ctx.shadowColor = getColor(p.color, 0.5);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Particle-to-particle connections
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j];
          const ex = q.x - p.x;
          const ey = q.y - p.y;
          const dist = Math.sqrt(ex * ex + ey * ey);
          if (dist < CONNECT_DIST) {
            const a = (1 - dist / CONNECT_DIST) * 0.18;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = `rgba(0,255,231,${a})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }

        // Particle-to-mouse connection
        const mdMouse = Math.sqrt(
          (mouse.x - p.x) ** 2 + (mouse.y - p.y) ** 2
        );
        if (mdMouse < MOUSE_DIST) {
          const a = (1 - mdMouse / MOUSE_DIST) * 0.45;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(0,255,231,${a})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }

      rafRef.current = requestAnimationFrame(draw);
    }

    function onMouseMove(e) {
      const rect = wrap.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    }

    function onMouseLeave() {
      mouseRef.current = { x: -9999, y: -9999 };
    }

    function onResize() {
      resize();
    }

    init();
    draw();

    wrap.addEventListener("mousemove", onMouseMove);
    wrap.addEventListener("mouseleave", onMouseLeave);
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(rafRef.current);
      wrap.removeEventListener("mousemove", onMouseMove);
      wrap.removeEventListener("mouseleave", onMouseLeave);
      window.removeEventListener("resize", onResize);
    };
  }, []);

  return (
    <div
      ref={wrapRef}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: "100vh",
        background: "#050b18",
        overflow: "hidden",
      }}
    >
      {/* Canvas layer */}
      <canvas
        ref={canvasRef}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          zIndex: 0,
        }}
      />

      {/* Scanline overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,255,231,0.012) 3px, rgba(0,255,231,0.012) 4px)",
          pointerEvents: "none",
          zIndex: 1,
        }}
      />

      {/* Corner brackets */}
      {["tl", "tr", "bl", "br"].map((pos) => (
        <div
          key={pos}
          style={{
            position: "absolute",
            width: 18,
            height: 18,
            opacity: 0.35,
            top: pos.includes("t") ? 14 : "auto",
            bottom: pos.includes("b") ? 14 : "auto",
            left: pos.includes("l") ? 14 : "auto",
            right: pos.includes("r") ? 14 : "auto",
            borderTop: pos.includes("t") ? "1.5px solid #00ffe7" : "none",
            borderBottom: pos.includes("b") ? "1.5px solid #00ffe7" : "none",
            borderLeft: pos.includes("l") ? "1.5px solid #00ffe7" : "none",
            borderRight: pos.includes("r") ? "1.5px solid #00ffe7" : "none",
            pointerEvents: "none",
            zIndex: 2,
          }}
        />
      ))}

      {/* Content slot */}
      <div
        style={{
          position: "relative",
          zIndex: 3,
          width: "100%",
          height: "100%",
        }}
      >
        {children}
      </div>
    </div>
  );
}
