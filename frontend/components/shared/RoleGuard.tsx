"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useRole } from "@/hooks/useRole";
import { FullPageSpinner } from "@/components/ui/Spinner";
import { ROUTES } from "@/lib/constants";
import type { UserRole } from "@/types/user";

interface RoleGuardProps {
  allow: UserRole;
  children: ReactNode;
}

/**
 * Client-side UX guard for (customer)/(officer) route groups. This is a
 * convenience layer only — real enforcement always happens server-side in
 * FastAPI (blueprint Section 2.6); redirecting here just avoids a flash
 * of the wrong dashboard before middleware.ts's server-side check lands.
 */
export function RoleGuard({ allow, children }: RoleGuardProps) {
  const { user, isLoading } = useAuth();
  const { role } = useRole();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (!user) {
      router.replace(ROUTES.login);
      return;
    }
    if (role !== allow) {
      router.replace(role === "officer" ? ROUTES.officerDashboard : ROUTES.customerDashboard);
    }
  }, [isLoading, user, role, allow, router]);

  if (isLoading || !user || role !== allow) {
    return <FullPageSpinner label="Checking access…" />;
  }

  return <>{children}</>;
}