import { useRef, useEffect, useCallback, forwardRef, useImperativeHandle } from 'react';

/**
 * SequencePlayer — Fixed <canvas> that draws the current frame.
 * Handles cover-fit drawing logic and exposes setFrame via ref.
 */
const SequencePlayer = forwardRef(function SequencePlayer({ frames, bgColor = '#050505' }, ref) {
  const canvasRef = useRef(null);
  const currentFrameRef = useRef(0);

  const drawFrame = useCallback((frameIndex) => {
    const canvas = canvasRef.current;
    if (!canvas || !frames || !frames[frameIndex]) return;

    const ctx = canvas.getContext('2d');
    const img = frames[frameIndex];
    if (!img.complete || !img.naturalWidth) return;

    const cw = canvas.width;
    const ch = canvas.height;
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;

    // Fill background to avoid transparency flicker
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, cw, ch);

    // Force the image to over-fill the screen horizontally to crop the bottom (width-based scaling)
    // Multiplying by 1.05 zooms the image in an extra 5%
    const scale = (cw / iw);
    const sw = iw * scale;
    const sh = ih * scale;

    // Center it horizontally
    const sx = (cw - sw) / 2;
    // Push the image down slightly so the extra 5% falls off the bottom edge, hiding the watermark
    const sy = ((ch - sh) / 2) - 20;

    ctx.drawImage(img, sx, sy, sw, sh);
  }, [frames, bgColor]);

  useImperativeHandle(ref, () => ({
    setFrame: (n) => {
      const idx = Math.max(0, Math.min(Math.floor(n), (frames?.length || 1) - 1));
      if (currentFrameRef.current === idx) return; // skip redundant draws
      currentFrameRef.current = idx;
      requestAnimationFrame(() => drawFrame(idx));
    },
    getCanvas: () => canvasRef.current,
  }), [frames, drawFrame]);

  // Resize canvas to window
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      drawFrame(currentFrameRef.current);
    };

    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [drawFrame]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
});

export default SequencePlayer;
