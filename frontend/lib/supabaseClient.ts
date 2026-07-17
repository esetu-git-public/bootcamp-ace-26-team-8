import { createBrowserClient } from "@supabase/ssr";
import { SUPABASE_ANON_KEY, SUPABASE_URL } from "@/lib/constants";

/**
 * Browser-side Supabase client. Used exclusively for Auth (sign-in,
 * sign-up, session, sign-out) per blueprint Section 2.5/2.6 — this
 * client never queries application tables directly; all business data
 * flows exclusively through services/apiClient.ts to FastAPI.
 */
export function createSupabaseBrowserClient() {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY. " +
        "Copy .env.local.example to .env.local and fill in your Supabase project values."
    );
  }
  return createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY);
}

export const supabase = createSupabaseBrowserClient();