import { useState, useEffect, useRef } from 'react';

/**
 * Preloads a sequence of image frames into Image() objects.
 * @param {string} basePath - e.g. "/sequences/hero-rise"
 * @param {number} frameCount - total number of frames
 * @param {object} options - { prefix, extension, padLength }
 * @returns {{ frames: Image[], loaded: boolean, progress: number }}
 */
export default function useFrameLoader(basePath, frameCount, options = {}) {
  const { prefix = '', extension = 'jpg', padLength = 4 } = options;
  const [loaded, setLoaded] = useState(false);
  const [progress, setProgress] = useState(0);
  const framesRef = useRef([]);

  useEffect(() => {
    const images = [];
    let loadedCount = 0;

    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      const num = String(i).padStart(padLength, '0');
      img.src = `${basePath}/${prefix}${num}.${extension}`;
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
  }, [basePath, frameCount, prefix, extension, padLength]);

  return { frames: framesRef.current, loaded, progress };
}
