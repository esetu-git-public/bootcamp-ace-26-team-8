/**
 * Mirrors backend/app/schemas/user_schema.py exactly.
 */

export type UserRole = "customer" | "officer";

export interface SessionResponse {
  user_id: string;
  role: UserRole;
  email: string | null;
}

export interface UserProfile {
  user_id: string;
  full_name: string | null;
  role: UserRole;
}

/** Supabase's own session user shape, as consumed by AuthContext. */
export interface AuthUser {
  id: string;
  email: string | null;
  role: UserRole | null;
  fullName: string | null;
}