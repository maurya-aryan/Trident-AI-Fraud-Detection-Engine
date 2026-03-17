import { useCallback } from 'react';

export default function useScrollLock() {
  const lock = useCallback(() => {
    document.body.style.overflow = 'hidden';
  }, []);

  const unlock = useCallback(() => {
    document.body.style.overflow = '';
  }, []);

  return { lock, unlock };
}
