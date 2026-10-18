import { useEffect, type RefObject } from 'react';

export function useContextMenuFocus(root: RefObject<HTMLDivElement | null>,
  anchor: { trigger: HTMLElement }, onClose: () => void) {
  useEffect(() => {
    const focusMenu = () => (root.current?.querySelector<HTMLElement>('button:not(:disabled)') ?? root.current)?.focus();
    const close = () => { onClose(); if (anchor.trigger.isConnected) anchor.trigger.focus(); };
    const key = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (event.key === 'Escape') { event.preventDefault(); close(); }
      if (event.key === 'Tab') {
        const controls = Array.from(root.current?.querySelectorAll<HTMLElement>('button:not(:disabled)') ?? []);
        const first = controls[0], last = controls.at(-1);
        if (!controls.length) { event.preventDefault(); focusMenu(); }
        else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    const outside = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node) && !anchor.trigger.contains(event.target as Node)) onClose();
    };
    const scroll = (event: Event) => { if (!root.current?.contains(event.target as Node)) onClose(); };
    focusMenu();
    document.addEventListener('keydown', key); document.addEventListener('pointerdown', outside);
    window.addEventListener('resize', close); window.addEventListener('scroll', scroll, true);
    return () => {
      document.removeEventListener('keydown', key); document.removeEventListener('pointerdown', outside);
      window.removeEventListener('resize', close); window.removeEventListener('scroll', scroll, true);
    };
  }, [anchor, root, onClose]);
}
