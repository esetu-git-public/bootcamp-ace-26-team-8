import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ROUTES } from "@/lib/constants";

/**
 * Signature hero visual: an animated risk gauge — the same dial motif
 * used throughout the product's prediction result screens — sweeping
 * from low to elevated risk, grounding the abstract "ML model" promise
 * in the one concrete thing the product actually produces.
 */
function RiskGauge() {
  return (
    <svg viewBox="0 0 240 140" className="w-full max-w-sm mx-auto lg:mx-0" aria-hidden="true">
      <path
        d="M 20 120 A 100 100 0 0 1 220 120"
        fill="none"
        stroke="var(--color-surface-inset)"
        strokeWidth="18"
        strokeLinecap="round"
      />
      <path
        d="M 20 120 A 100 100 0 0 1 220 120"
        fill="none"
        stroke="url(#gaugeGradient)"
        strokeWidth="18"
        strokeLinecap="round"
        strokeDasharray="314"
        strokeDashoffset="80"
      />
      <defs>
        <linearGradient id="gaugeGradient" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="var(--color-success)" />
          <stop offset="55%" stopColor="var(--color-warning)" />
          <stop offset="100%" stopColor="var(--color-danger)" />
        </linearGradient>
      </defs>
      <g style={{ transformOrigin: "120px 120px" }} className="animate-[spin_0s]">
        <line
          x1="120"
          y1="120"
          x2="120"
          y2="38"
          stroke="var(--color-ink)"
          strokeWidth="3"
          strokeLinecap="round"
          style={{
            transformOrigin: "120px 120px",
            transform: "rotate(-38deg)",
            transition: "transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)",
          }}
        />
      </g>
      <circle cx="120" cy="120" r="7" fill="var(--color-ink)" />
      <text x="120" y="106" textAnchor="middle" className="figure" fill="var(--color-ink)" fontSize="20" fontWeight="600">
        11.6%
      </text>
      <text x="120" y="123" textAnchor="middle" fill="var(--color-ink-muted)" fontSize="9">
        DEFAULT PROBABILITY
      </text>
    </svg>
  );
}

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-navy text-white">
      <div className="absolute inset-0 opacity-[0.05] [background-image:linear-gradient(transparent_31px,rgba(255,255,255,0.5)_32px),linear-gradient(90deg,transparent_31px,rgba(255,255,255,0.5)_32px)] [background-size:32px_32px]" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 lg:py-28 grid lg:grid-cols-2 gap-12 items-center">
        <div className="animate-fade-in">
          <span className="inline-flex items-center gap-2 text-xs font-medium text-white/70 bg-white/10 rounded-full px-3 py-1 mb-6">
            Recall-optimized · 255K applications trained
          </span>
          <h1 className="font-display font-semibold text-4xl sm:text-5xl leading-[1.1]">
            An instant read on default risk, before the loan ever leaves your desk.
          </h1>
          <p className="text-white/70 text-lg mt-6 max-w-xl">
            Submit an application and get a model-backed probability of default in seconds —
            then let your officers decide, with the full record and reasoning always on hand.
          </p>
          <div className="flex flex-wrap gap-3 mt-8">
            <Link href={ROUTES.register}>
              <Button size="lg" variant="primary">
                Apply for a loan
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href={ROUTES.about}>
              <Button size="lg" variant="outline" className="bg-transparent border-white/20 text-white hover:bg-white/10">
                How it works
              </Button>
            </Link>
          </div>
        </div>

        <div className="animate-fade-in [animation-delay:150ms] flex justify-center">
          <div className="bg-white/5 border border-white/10 rounded-xl p-8 backdrop-blur-sm w-full max-w-md">
            <RiskGauge />
            <div className="grid grid-cols-3 gap-4 mt-6 text-center">
              <div>
                <p className="figure text-lg font-medium">0.76</p>
                <p className="text-[11px] text-white/50 mt-0.5">ROC-AUC</p>
              </div>
              <div>
                <p className="figure text-lg font-medium">0.70</p>
                <p className="text-[11px] text-white/50 mt-0.5">Recall</p>
              </div>
              <div>
                <p className="figure text-lg font-medium">&lt;1s</p>
                <p className="text-[11px] text-white/50 mt-0.5">Response</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}