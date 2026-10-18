import { useLayoutEffect, useRef, useState } from 'react';

// Fixed, single-line data rows keep the native scrollbar aligned with original row IDs.
export const SOURCE_ROW_HEIGHT = 28;
const OVERSCAN = 8;

export function useSourceRowWindow(startRow: number, total: number, initialScrollTop = 0, initialScrollLeft = 0) {
  const viewport = useRef<HTMLDivElement>(null);
  const header = useRef<HTMLTableSectionElement>(null);
  const [scrollTop, setScrollTop] = useState(initialScrollTop);
  const [bodyHeight, setBodyHeight] = useState(260);
  useLayoutEffect(() => {
    if (viewport.current) {
      viewport.current.scrollTop = initialScrollTop;
      viewport.current.scrollLeft = initialScrollLeft;
    }
    const measure = () => {
      const available = (viewport.current?.clientHeight || 320) - (header.current?.offsetHeight || 60);
      setBodyHeight(Math.max(SOURCE_ROW_HEIGHT, available));
    };
    measure();
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(measure);
    if (viewport.current) observer?.observe(viewport.current);
    if (header.current) observer?.observe(header.current);
    return () => observer?.disconnect();
  }, []);
  const visibleCount = Math.ceil(bodyHeight / SOURCE_ROW_HEIGHT);
  const firstVisible = Math.max(0, Math.min(Math.floor(scrollTop / SOURCE_ROW_HEIGHT), total - visibleCount));
  const first = Math.max(0, firstVisible - OVERSCAN);
  const end = Math.min(total, firstVisible + visibleCount + OVERSCAN);
  return { viewport, header, setScrollTop,
    rows: Array.from({ length: end - first }, (_, index) => startRow + first + index),
    topPadding: first * SOURCE_ROW_HEIGHT, bottomPadding: (total - end) * SOURCE_ROW_HEIGHT };
}
