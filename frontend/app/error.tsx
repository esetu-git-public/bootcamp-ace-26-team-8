"use client";

import { useEffect } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/Button";

/** Next.js App Router special file — catches errors thrown during
 * rendering within a route segment (distinct from ErrorBoundary, which
 * covers client-side runtime errors after hydration). */
export default function RouteError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("[route error]", error);
  }, [error]);

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center px-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-danger-subtle text-danger mb-5">
        <AlertTriangle className="h-7 w-7" />
      </div>
      <h1 className="font-display font-medium text-xl text-ink">This page hit a snag</h1>
      <p className="text-sm text-ink-muted mt-2 max-w-sm">
        {error.message || "Something went wrong loading this page."}
        {error.digest && <span className="block text-xs text-ink-faint mt-1 figure">Ref: {error.digest}</span>}
      </p>
      <Button className="mt-6" onClick={reset}>
        <RotateCcw className="h-4 w-4" />
        Try again
      </Button>
    </div>
  );
}