import { useLayoutEffect, useRef, type ReactElement } from "react";

type MatrixAutoGrowTextareaProps = {
  ariaLabel: string;
  className?: string;
  errorMessage?: string;
  value: string;
  disabled?: boolean;
  onFocus?: () => void;
  onChange: (value: string) => void;
};

export function MatrixAutoGrowTextarea({
  ariaLabel,
  className,
  errorMessage,
  value,
  disabled = false,
  onFocus,
  onChange,
}: MatrixAutoGrowTextareaProps): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight + 4}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      aria-label={ariaLabel}
      className={
        className
          ? `matrix-editor-inline-textarea ${className}`
          : "matrix-editor-inline-textarea"
      }
      rows={1}
      disabled={disabled}
      title={errorMessage || undefined}
      value={value}
      onFocus={onFocus}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
