import Link from "next/link";
import type { ReactNode } from "react";
import { ROUTES, APP_NAME } from "@/lib/constants";

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  footerPrompt: string;
  footerLinkLabel: string;
  footerLinkHref: string;
}

/**
 * Shared split-screen shell for /login, /register, /forgot-password, and
 * /reset-password — a quiet ledger-branded panel on the left (the
 * product's visual signature, echoed from the marketing hero) and the
 * form itself on the right, stacking on mobile.
 */
export function AuthLayout({
  title,
  subtitle,
  children,
  footerPrompt,
  footerLinkLabel,
  footerLinkHref,
}: AuthLayoutProps) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex flex-col justify-between bg-navy text-white p-12 relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.06] [background-image:linear-gradient(transparent_31px,rgba(255,255,255,0.5)_32px),linear-gradient(90deg,transparent_31px,rgba(255,255,255,0.5)_32px)] [background-size:32px_32px]" />
        <Link href={ROUTES.home} className="relative flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded bg-white text-navy font-display font-bold text-sm">
            L
          </span>
          <span className="font-display font-semibold text-lg">{APP_NAME}</span>
        </Link>

        <div className="relative">
          <p className="font-display text-3xl leading-tight max-w-sm">
            Every application, weighed the same way, every time.
          </p>
          <p className="text-white/60 text-sm mt-4 max-w-sm">
            A single model scores every applicant identically — no reviewer sees a different
            standard than the last. Officers decide; the ledger never forgets why.
          </p>
        </div>

        <p className="relative text-xs text-white/40">
          © {new Date().getFullYear()} {APP_NAME}. All entries are final once submitted.
        </p>
      </div>

      <div className="flex flex-col justify-center px-6 py-12 sm:px-12 lg:px-20">
        <div className="mx-auto w-full max-w-sm animate-fade-in">
          <Link href={ROUTES.home} className="lg:hidden flex items-center gap-2 mb-10">
            <span className="flex h-8 w-8 items-center justify-center rounded bg-navy text-white font-display font-bold text-sm">
              L
            </span>
            <span className="font-display font-semibold text-lg text-ink">{APP_NAME}</span>
          </Link>

          <h1 className="font-display font-semibold text-2xl text-ink">{title}</h1>
          <p className="text-sm text-ink-muted mt-1.5 mb-8">{subtitle}</p>

          {children}

          <p className="text-sm text-ink-muted mt-8 text-center">
            {footerPrompt}{" "}
            <Link href={footerLinkHref} className="text-brand font-medium hover:text-brand-hover">
              {footerLinkLabel}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}