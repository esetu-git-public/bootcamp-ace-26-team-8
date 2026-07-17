import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

const PUBLIC_PATHS = ["/", "/login", "/register", "/forgot-password", "/reset-password", "/about", "/faq", "/contact"];

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((path) => pathname === path) || pathname.startsWith("/_next");
}

function extractRole(user: { app_metadata?: Record<string, unknown>; user_metadata?: Record<string, unknown> } | null): "customer" | "officer" | null {
  if (!user) return null;
  const appRole = user.app_metadata?.role;
  const userRole = user.user_metadata?.role;
  const role = (appRole ?? userRole) as string | undefined;
  return role === "customer" || role === "officer" ? role : null;
}

/**
 * Route protection. Real authorization is always enforced server-side by
 * FastAPI (blueprint Section 2.6) — this middleware only improves UX by
 * redirecting unauthenticated users to /login and mismatched-role users
 * to their correct dashboard before a page ever renders.
 *
 * NOTE: /customer/* and /officer/* segment prefixes are used here rather
 * than the blueprint's literal (customer)/(officer) route-group paths,
 * pending resolution of the /dashboard + /applications path collision
 * between those two groups (see Milestone 1 handoff note).
 */
export async function middleware(request: NextRequest) {
  const response = NextResponse.next();

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
    {
      cookies: {
        get: (name) => request.cookies.get(name)?.value,
        set: (name, value, options) => {
          response.cookies.set({ name, value, ...options });
        },
        remove: (name, options) => {
          response.cookies.set({ name, value: "", ...options });
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { pathname } = request.nextUrl;

  if (isPublicPath(pathname)) {
    return response;
  }

  if (!user) {
    const redirectUrl = new URL("/login", request.url);
    redirectUrl.searchParams.set("redirectTo", pathname);
    return NextResponse.redirect(redirectUrl);
  }

  const role = extractRole(user);

  if (pathname.startsWith("/customer") && role !== "customer") {
    return NextResponse.redirect(new URL(role === "officer" ? "/officer/dashboard" : "/login", request.url));
  }

  if (pathname.startsWith("/officer") && role !== "officer") {
    return NextResponse.redirect(new URL(role === "customer" ? "/customer/dashboard" : "/login", request.url));
  }

  return response;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};