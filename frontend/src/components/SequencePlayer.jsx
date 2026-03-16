import { useRef, useEffect, useCallback, forwardRef, useImperativeHandle } from 'react';

/**
 * SequencePlayer — Fixed <canvas> that draws the current frame.
 * Handles cover-fit drawing logic and exposes setFrame via ref.
 */
const SequencePlayer = forwardRef(function SequencePlayer({ frames, width, height }, ref) {
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

    // Cover-fit logic
    const scale = Math.max(cw / iw, ch / ih);
    const sw = iw * scale;
    const sh = ih * scale;
    const sx = (cw - sw) / 2;
    const sy = (ch - sh) / 2;

    ctx.clearRect(0, 0, cw, ch);
    ctx.drawImage(img, sx, sy, sw, sh);
  }, [frames]);

  useImperativeHandle(ref, () => ({
    setFrame: (n) => {
      const idx = Math.max(0, Math.min(Math.floor(n), (frames?.length || 1) - 1));
      currentFrameRef.current = idx;
      drawFrame(idx);
    },
    getCanvas: () => canvasRef.current,
  }), [frames, drawFrame]);

  // Resize canvas to window
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      drawFrame(currentFrameRef.current);
    };

    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [drawFrame]);

  return (
    <canvas
      ref={canvasRef}
      className="sequence-canvas"
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
