// frontend/src/shared/hooks/useMediaQuery.ts
import { useState, useEffect } from 'react';

/**
 * Hook to check if a media query matches
 */
export function useMediaQuery(query: string): boolean {
  const getMatches = (query: string): boolean => {
    // Prevents SSR issues
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  };

  const [matches, setMatches] = useState<boolean>(getMatches(query));

  useEffect(() => {
    function handleChange() {
      setMatches(getMatches(query));
    }

    const matchMedia = window.matchMedia(query);

    // Initial check
    handleChange();

    // Listen for changes
    if (matchMedia.addListener) {
      // For older browsers
      matchMedia.addListener(handleChange);
    } else {
      // Modern approach
      matchMedia.addEventListener('change', handleChange);
    }

    return () => {
      if (matchMedia.removeListener) {
        // For older browsers
        matchMedia.removeListener(handleChange);
      } else {
        // Modern approach
        matchMedia.removeEventListener('change', handleChange);
      }
    };
  }, [query]);

  return matches;
}