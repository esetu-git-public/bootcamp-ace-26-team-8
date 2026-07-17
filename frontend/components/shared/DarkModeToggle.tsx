"use client";

import { Moon, Sun } from "lucide-react";
import { useDarkMode } from "@/hooks/useDarkMode";

export function DarkModeToggle() {
  const { isDark, toggle, isHydrated } = useDarkMode();

  if (!isHydrated) return <div className="h-9 w-9" aria-hidden="true" />;

  return (
    <button
      onClick={toggle}
      className="flex h-9 w-9 items-center justify-center rounded text-ink-muted hover:bg-surface-inset hover:text-ink transition-colors focus-ring"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-pressed={isDark}
    >
      {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}