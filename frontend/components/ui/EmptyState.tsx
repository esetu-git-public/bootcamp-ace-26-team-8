import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-4">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-inset text-ink-faint mb-4">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="font-display font-medium text-ink">{title}</h3>
      <p className="text-sm text-ink-muted mt-1.5 max-w-xs">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}