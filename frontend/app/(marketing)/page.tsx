import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { Hero } from "@/components/marketing/Hero";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { Button } from "@/components/ui/Button";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = {
  title: "Instant, model-backed loan default predictions",
};

export default function LandingPage() {
  return (
    <>
      <Hero />
      <FeatureGrid />

      <section className="py-20 bg-surface">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-flex items-center gap-2 text-brand text-sm font-medium mb-4">
              <ShieldCheck className="h-4 w-4" />
              For loan officers
            </span>
            <h2 className="font-display font-semibold text-3xl text-ink">
              Every prediction, backstopped by a human decision
            </h2>
            <p className="text-ink-muted mt-4 leading-relaxed">
              The model never has the final word. Officers review the complete applicant profile
              alongside the prediction, then approve, reject, or send it back for another look —
              with a mandatory note logged against every transition.
            </p>
            <Link href={ROUTES.register} className="inline-block mt-6">
              <Button variant="secondary" size="lg">
                Join as an officer
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="bg-surface-muted border border-border rounded-lg p-6">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <span className="text-xs font-medium text-ink-muted uppercase tracking-wide">
                Application #A-20481
              </span>
              <span className="text-xs font-medium text-warning bg-warning-subtle rounded-full px-2 py-0.5">
                Review Requested
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 py-4 text-sm">
              <div>
                <p className="text-ink-muted text-xs">Requested amount</p>
                <p className="figure text-ink mt-0.5">$22,000.00</p>
              </div>
              <div>
                <p className="text-ink-muted text-xs">Default probability</p>
                <p className="figure text-danger mt-0.5">41.0%</p>
              </div>
              <div>
                <p className="text-ink-muted text-xs">Credit score</p>
                <p className="figure text-ink mt-0.5">615</p>
              </div>
              <div>
                <p className="text-ink-muted text-xs">DTI ratio</p>
                <p className="figure text-ink mt-0.5">0.41</p>
              </div>
            </div>
            <p className="text-xs text-ink-muted pt-3 border-t border-border">
              "Income verification pending — requesting updated pay stubs before final decision."
            </p>
          </div>
        </div>
      </section>

      <section className="bg-navy text-white py-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-display font-semibold text-3xl">Ready to see your number?</h2>
          <p className="text-white/70 mt-3 max-w-xl mx-auto">
            It takes about two minutes to apply, and your result appears the moment you submit.
          </p>
          <Link href={ROUTES.register} className="inline-block mt-8">
            <Button size="lg" variant="primary">
              Apply for a loan
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </>
  );
}