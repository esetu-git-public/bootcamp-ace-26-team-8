import Link from "next/link";
import { ROUTES, APP_NAME } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="border-t border-border bg-surface mt-auto">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-navy text-white font-display font-bold text-xs">
            L
          </span>
          <span className="text-sm text-ink-muted">
            © {new Date().getFullYear()} {APP_NAME}. A model-backed loan decisioning demo.
          </span>
        </div>
        <div className="flex items-center gap-6 text-sm text-ink-muted">
          <Link href={ROUTES.about} className="hover:text-ink transition-colors">
            About
          </Link>
          <Link href={ROUTES.faq} className="hover:text-ink transition-colors">
            FAQ
          </Link>
          <Link href={ROUTES.contact} className="hover:text-ink transition-colors">
            Contact
          </Link>
        </div>
      </div>
    </footer>
  );
}