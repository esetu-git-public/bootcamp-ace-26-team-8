import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  label?: string;
}

const sizeMap = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-10 w-10" };

export function Spinner({ size = "md", className, label }: SpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2" role="status">
      <Loader2 className={cn("animate-spin text-brand", sizeMap[size], className)} aria-hidden="true" />
      {label && <span className="text-sm text-ink-muted">{label}</span>}
      <span className="sr-only">Loading…</span>
    </div>
  );
}

export function FullPageSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex min-h-[60vh] w-full items-center justify-center">
      <Spinner size="lg" label={label} />
    </div>
  );
}