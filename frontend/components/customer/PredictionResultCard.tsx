"use client";

import Link from "next/link";
import { AlertTriangle, CheckCircle2, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatPercent } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";

interface PredictionResultCardProps {
  applicationId: string;
  prediction: 0 | 1;
  probability: number;
}

/** Shown immediately after POST /loan/apply — data comes from FastAPI's
 * response only, never computed client-side (blueprint Section 7). */
export function PredictionResultCard({ applicationId, prediction, probability }: PredictionResultCardProps) {
  const isHighRisk = prediction === 1;

  return (
    <Card className="max-w-lg mx-auto animate-fade-in">
      <CardContent className="pt-8 text-center">
        <div
          className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full ${
            isHighRisk ? "bg-danger-subtle text-danger" : "bg-success-subtle text-success"
          }`}
        >
          {isHighRisk ? <AlertTriangle className="h-8 w-8" /> : <CheckCircle2 className="h-8 w-8" />}
        </div>

        <h1 className="font-display font-semibold text-2xl text-ink mt-5">
          {isHighRisk ? "Elevated default risk" : "Low default risk"}
        </h1>
        <p className="text-sm text-ink-muted mt-2">
          Application <span className="figure">{applicationId}</span> has been submitted and is
          now awaiting officer review.
        </p>

        <div className="mt-6 rounded-lg bg-surface-muted border border-border p-6">
          <p className="text-xs text-ink-muted uppercase tracking-wide">Default probability</p>
          <p className={`figure text-4xl font-semibold mt-1 ${isHighRisk ? "text-danger" : "text-success"}`}>
            {formatPercent(probability)}
          </p>
        </div>

        <p className="text-xs text-ink-faint mt-4 max-w-sm mx-auto">
          This is a model estimate, not a final lending decision. A loan officer will review your
          full application before any status change takes effect.
        </p>

        <div className="flex flex-col sm:flex-row gap-2 mt-7">
          <Link href={`${ROUTES.customerApplications}/${applicationId}`} className="flex-1">
            <Button variant="outline" className="w-full">
              View full application
            </Button>
          </Link>
          <Link href={ROUTES.customerDashboard} className="flex-1">
            <Button className="w-full">
              Go to dashboard
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}