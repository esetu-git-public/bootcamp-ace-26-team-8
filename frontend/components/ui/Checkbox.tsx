"use client";

import { forwardRef, type InputHTMLAttributes } from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: React.ReactNode;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const checkboxId = id ?? props.name;
    return (
      <div className="flex flex-col gap-1">
        <label htmlFor={checkboxId} className="flex items-start gap-2.5 cursor-pointer select-none">
          <span className="relative flex h-5 w-5 shrink-0 items-center justify-center">
            <input
              ref={ref}
              id={checkboxId}
              type="checkbox"
              className={cn(
                "peer h-5 w-5 appearance-none rounded border border-border bg-surface",
                "checked:bg-brand checked:border-brand transition-colors focus-ring cursor-pointer",
                error && "border-danger",
                className
              )}
              {...props}
            />
            <Check className="pointer-events-none absolute h-3.5 w-3.5 text-white opacity-0 peer-checked:opacity-100" />
          </span>
          {label && <span className="text-sm text-ink-muted leading-5">{label}</span>}
        </label>
        {error && <p className="text-xs text-danger ml-7">{error}</p>}
      </div>
    );
  }
);

Checkbox.displayName = "Checkbox";