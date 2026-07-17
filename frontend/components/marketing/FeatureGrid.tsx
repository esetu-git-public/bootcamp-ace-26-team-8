import { Gauge, ShieldCheck, ClipboardCheck, LineChart } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";

interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    icon: Gauge,
    title: "Instant scoring",
    description:
      "Every application is run through the same trained pipeline the moment it's submitted — no queue, no manual triage before a first read.",
  },
  {
    icon: ShieldCheck,
    title: "One gateway, one standard",
    description:
      "All decisioning logic lives behind a single backend. No shortcut bypasses validation, and no two applicants are scored differently.",
  },
  {
    icon: ClipboardCheck,
    title: "A defensible record",
    description:
      "Officers see the full applicant profile alongside the prediction — never just a number — so every decision has context behind it.",
  },
  {
    icon: LineChart,
    title: "Built for recall",
    description:
      "The model is tuned to catch real defaulters, not just to look accurate on paper — missing a risky loan costs more than a false alarm.",
  },
];

export function FeatureGrid() {
  return (
    <section className="bg-surface-muted py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="max-w-xl mb-12">
          <h2 className="font-display font-semibold text-3xl text-ink">Built like a ledger, not a black box</h2>
          <p className="text-ink-muted mt-3">
            Every number the system produces is traceable to a submitted application and a
            documented review — nothing is inferred silently.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card
                key={feature.title}
                className="animate-fade-in hover:shadow-raised transition-shadow"
                style={{ animationDelay: `${index * 75}ms` }}
              >
                <CardContent className="pt-5">
                  <div className="flex h-10 w-10 items-center justify-center rounded bg-brand-subtle text-brand mb-4">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-display font-medium text-ink">{feature.title}</h3>
                  <p className="text-sm text-ink-muted mt-2 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}