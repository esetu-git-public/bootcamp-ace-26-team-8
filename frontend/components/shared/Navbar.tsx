"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, LogOut, LayoutDashboard } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useRole } from "@/hooks/useRole";
import { Button } from "@/components/ui/Button";
import { DarkModeToggle } from "@/components/shared/DarkModeToggle";
import { APP_NAME, ROUTES } from "@/lib/constants";
import { initials } from "@/lib/utils";

export function Navbar() {
  const { user, signOut } = useAuth();
  const { isCustomer, isOfficer } = useRole();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const dashboardHref = isOfficer ? ROUTES.officerDashboard : ROUTES.customerDashboard;

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-surface/90 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href={ROUTES.home} className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded bg-navy text-white font-display font-bold text-sm">
            L
          </span>
          <span className="font-display font-semibold text-lg text-ink">{APP_NAME}</span>
        </Link>

        <div className="hidden md:flex items-center gap-6">
          {!user && (
            <>
              <Link href={ROUTES.about} className="text-sm text-ink-muted hover:text-ink transition-colors">
                About
              </Link>
              <Link href={ROUTES.faq} className="text-sm text-ink-muted hover:text-ink transition-colors">
                FAQ
              </Link>
              <Link href={ROUTES.contact} className="text-sm text-ink-muted hover:text-ink transition-colors">
                Contact
              </Link>
            </>
          )}
        </div>

        <div className="hidden md:flex items-center gap-3">
          <DarkModeToggle />
          {user ? (
            <>
              <Link
                href={dashboardHref}
                className="inline-flex items-center gap-2 text-sm text-ink-muted hover:text-ink transition-colors"
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </Link>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-subtle text-brand text-xs font-semibold">
                {initials(user.fullName ?? user.email ?? "?")}
              </div>
              <Button variant="ghost" size="sm" onClick={() => void signOut()}>
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Link href={ROUTES.login}>
                <Button variant="ghost" size="sm">
                  Log in
                </Button>
              </Link>
              <Link href={ROUTES.register}>
                <Button variant="primary" size="sm">
                  Get started
                </Button>
              </Link>
            </>
          )}
        </div>

        <div className="flex md:hidden items-center gap-1">
          <DarkModeToggle />
          <button
            className="text-ink p-2 focus-ring rounded"
            onClick={() => setIsMenuOpen((prev) => !prev)}
            aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            aria-expanded={isMenuOpen}
          >
            {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      {isMenuOpen && (
        <div className="md:hidden border-t border-border bg-surface px-4 py-4 flex flex-col gap-3 animate-slide-in">
          {!user ? (
            <>
              <Link href={ROUTES.about} onClick={() => setIsMenuOpen(false)} className="text-sm text-ink-muted">
                About
              </Link>
              <Link href={ROUTES.faq} onClick={() => setIsMenuOpen(false)} className="text-sm text-ink-muted">
                FAQ
              </Link>
              <Link href={ROUTES.contact} onClick={() => setIsMenuOpen(false)} className="text-sm text-ink-muted">
                Contact
              </Link>
              <Link href={ROUTES.login} onClick={() => setIsMenuOpen(false)}>
                <Button variant="outline" size="sm" className="w-full">
                  Log in
                </Button>
              </Link>
              <Link href={ROUTES.register} onClick={() => setIsMenuOpen(false)}>
                <Button variant="primary" size="sm" className="w-full">
                  Get started
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Link href={dashboardHref} onClick={() => setIsMenuOpen(false)} className="text-sm text-ink">
                Dashboard
              </Link>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start"
                onClick={() => {
                  setIsMenuOpen(false);
                  void signOut();
                }}
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            </>
          )}
        </div>
      )}
    </header>
  );
}