"use client";

import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabaseClient";
import { authService } from "@/services/authService";
import type { AuthUser, UserRole } from "@/types/user";

interface AuthContextValue {
  user: AuthUser | null;
  session: Session | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName: string, role: UserRole) => Promise<void>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function extractRole(session: Session | null): UserRole | null {
  if (!session?.user) return null;
  const appRole = (session.user.app_metadata as Record<string, unknown> | undefined)?.role;
  const userRole = (session.user.user_metadata as Record<string, unknown> | undefined)?.role;
  const role = (appRole ?? userRole) as UserRole | undefined;
  return role === "customer" || role === "officer" ? role : null;
}

function toAuthUser(session: Session | null): AuthUser | null {
  if (!session?.user) return null;
  const fullName =
    (session.user.user_metadata as Record<string, unknown> | undefined)?.full_name;
  return {
    id: session.user.id,
    email: session.user.email ?? null,
    role: extractRole(session),
    fullName: typeof fullName === "string" ? fullName : null,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSession(data.session);
      setIsLoading(false);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      setIsLoading(false);
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    await authService.signInWithPassword(email, password);
  }, []);

  const signUp = useCallback(
    async (email: string, password: string, fullName: string, role: UserRole) => {
      await authService.signUpWithPassword(email, password, fullName, role);
    },
    []
  );

  const signOut = useCallback(async () => {
    await authService.signOut();
    setSession(null);
  }, []);

  const refresh = useCallback(async () => {
    const current = await authService.getSession();
    setSession(current);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: toAuthUser(session),
      session,
      isLoading,
      signIn,
      signUp,
      signOut,
      refresh,
    }),
    [session, isLoading, signIn, signUp, signOut, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}