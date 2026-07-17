import type { HTMLAttributes } from "react";
import { CheckCircle2, AlertCircle, Info, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type AlertTone = "success" | "danger" | "warning" | "info";

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  tone?: AlertTone;
  title?: string;
}

const toneConfig: Record<AlertTone, { classes: string; Icon: typeof Info }> = {
  success: { classes: "bg-success-subtle text-success border-success/20", Icon: CheckCircle2 },
  danger: { classes: "bg-danger-subtle text-danger border-danger/20", Icon: XCircle },
  warning: { classes: "bg-warning-subtle text-warning border-warning/20", Icon: AlertCircle },
  info: { classes: "bg-brand-subtle text-brand border-brand/20", Icon: Info },
};

export function Alert({ className, tone = "info", title, children, ...props }: AlertProps) {
  const { classes, Icon } = toneConfig[tone];
  return (
    <div
      role="alert"
      className={cn("flex gap-3 rounded border px-4 py-3 text-sm animate-fade-in", classes, className)}
      {...props}
    >
      <Icon className="h-4 w-4 shrink-0 mt-0.5" aria-hidden="true" />
      <div>
        {title && <p className="font-medium mb-0.5">{title}</p>}
        <div className="text-ink-muted [&:not(:only-child)]:text-current">{children}</div>
      </div>
    </div>
  );
}