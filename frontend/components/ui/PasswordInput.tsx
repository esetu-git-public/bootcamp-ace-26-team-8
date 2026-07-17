"use client";

import { forwardRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Input } from "@/components/ui/Input";
import type { InputHTMLAttributes } from "react";

interface PasswordInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  error?: string;
  hint?: string;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ label, error, hint, ...props }, ref) => {
    const [isVisible, setIsVisible] = useState(false);

    return (
      <div className="relative">
        <Input
          ref={ref}
          type={isVisible ? "text" : "password"}
          label={label}
          error={error}
          hint={hint}
          className="pr-10"
          {...props}
        />
        <button
          type="button"
          onClick={() => setIsVisible((prev) => !prev)}
          className={`absolute right-3 text-ink-faint hover:text-ink-muted transition-colors focus-ring rounded ${
            label ? "top-[34px]" : "top-1/2 -translate-y-1/2"
          }`}
          aria-label={isVisible ? "Hide password" : "Show password"}
          tabIndex={-1}
        >
          {isVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";