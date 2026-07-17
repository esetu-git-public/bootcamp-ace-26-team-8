"use client";

import { useContext } from "react";
import { AuthContext } from "@/context/AuthContext";

/** Exposes session/user state and auth actions from AuthProvider. */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider (see app/layout.tsx)");
  }
  return context;
}