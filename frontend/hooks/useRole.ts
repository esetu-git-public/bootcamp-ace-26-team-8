"use client";

import { useAuth } from "@/hooks/useAuth";
import type { UserRole } from "@/types/user";

/** Convenience hook for role-gated rendering logic in components. */
export function useRole() {
  const { user, isLoading } = useAuth();

  const role: UserRole | null = user?.role ?? null;

  return {
    role,
    isLoading,
    isCustomer: role === "customer",
    isOfficer: role === "officer",
    isAuthenticated: user !== null,
  };
}