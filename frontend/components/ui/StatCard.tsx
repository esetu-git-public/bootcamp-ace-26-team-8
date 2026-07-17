import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  tone?: "neutral" | "success" | "warning" | "danger" | "brand";
  trend?: string;
}

const toneClasses = {
  neutral: "bg-surface-inset text-ink-muted",
  success: "bg-success-subtle text-success",
  warning: "bg-warning-subtle text-warning",
  danger: "bg-danger-subtle text-danger",
  brand: "bg-brand-subtle text-brand",
};

export function StatCard({ label, value, icon: Icon, tone = "neutral", trend }: StatCardProps) {
  return (
    <div className="bg-surface border border-border rounded-lg p-5 shadow-card">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-ink-muted uppercase tracking-wide">{label}</p>
        <div className={cn("flex h-8 w-8 items-center justify-center rounded", toneClasses[tone])}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className="figure text-2xl font-medium text-ink mt-3">{value}</p>
      {trend && <p className="text-xs text-ink-muted mt-1">{trend}</p>}
    </div>
  );
}