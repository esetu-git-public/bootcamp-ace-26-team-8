import { supabase } from "@/lib/supabaseClient";
import { apiClient } from "@/services/apiClient";
import type { SessionResponse } from "@/types/user";

/**
 * Thin wrapper around Supabase Auth (client-side sign-in/sign-up/sign-out)
 * plus the backend's session-verification endpoint. Per blueprint Section
 * 2.6: login/register happen client-side against Supabase Auth; FastAPI's
 * POST /auth/session only confirms an already-issued token and reports
 * back the verified role, which authService exposes for AuthContext.
 */
export const authService = {
  async signInWithPassword(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  },

  async signUpWithPassword(email: string, password: string, fullName: string, role: "customer" | "officer") {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role,
        },
      },
    });
    if (error) throw error;
    return data;
  },

  async sendPasswordResetEmail(email: string) {
    const redirectTo =
      typeof window !== "undefined" ? `${window.location.origin}/reset-password` : undefined;
    const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo });
    if (error) throw error;
  },

  async signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },

  async getSession() {
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    return data.session;
  },

  /** Calls POST /api/v1/auth/session — the backend's verified source of truth for role. */
  async verifySession(): Promise<SessionResponse> {
    return apiClient.post<SessionResponse>("/auth/session");
  },
};