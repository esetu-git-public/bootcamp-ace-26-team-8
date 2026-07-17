"use client";

import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "ledger-theme";

/** Persists the user's theme choice and applies the `.dark` class Tailwind's
 * darkMode: "class" config (tailwind.config.js, Milestone 1) reads from. */
export function useDarkMode() {
  const [isDark, setIsDark] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const shouldUseDark = stored ? stored === "dark" : prefersDark;
    setIsDark(shouldUseDark);
    document.documentElement.classList.toggle("dark", shouldUseDark);
    setIsHydrated(true);
  }, []);

  const toggle = useCallback(() => {
    setIsDark((prev) => {
      const next = !prev;
      document.documentElement.classList.toggle("dark", next);
      localStorage.setItem(STORAGE_KEY, next ? "dark" : "light");
      return next;
    });
  }, []);

  return { isDark, toggle, isHydrated };
}