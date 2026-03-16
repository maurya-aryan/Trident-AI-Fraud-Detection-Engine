import { useState, useEffect, useRef } from 'react';

/**
 * Preloads a sequence of JPEG frames into Image() objects.
 * @param {string} basePath - e.g. "/sequences/hero-rise"
 * @param {number} frameCount - total number of frames
 * @param {string} prefix - filename prefix e.g. "ezgif-frame-"
 * @returns {{ frames: Image[], loaded: boolean, progress: number }}
 */
export default function useFrameLoader(basePath, frameCount, prefix = 'ezgif-frame-') {
  const [loaded, setLoaded] = useState(false);
  const [progress, setProgress] = useState(0);
  const framesRef = useRef([]);

  useEffect(() => {
    const images = [];
    let loadedCount = 0;

    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      const num = String(i).padStart(3, '0');
      img.src = `${basePath}/${prefix}${num}.jpg`;
      img.onload = () => {
        loadedCount++;
        setProgress(loadedCount / frameCount);
        if (loadedCount === frameCount) {
          setLoaded(true);
        }
      };
      img.onerror = () => {
        loadedCount++;
        setProgress(loadedCount / frameCount);
        if (loadedCount === frameCount) {
          setLoaded(true);
        }
      };
      images.push(img);
    }

    framesRef.current = images;
  }, [basePath, frameCount, prefix]);

  return { frames: framesRef.current, loaded, progress };
}
