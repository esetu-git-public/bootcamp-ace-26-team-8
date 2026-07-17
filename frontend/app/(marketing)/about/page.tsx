import type { Metadata } from "next";
import { Database, Cpu, ShieldCheck, Server } from "lucide-react";

export const metadata: Metadata = { title: "About" };

const steps = [
  {
    icon: Database,
    title: "255,347 historical applications",
    description:
      "The model was trained on a cleaned, de-duplicated dataset of real loan outcomes, with roughly 1 in 9 ending in default.",
  },
  {
    icon: Cpu,
    title: "A single scikit-learn pipeline",
    description:
      "Feature engineering, encoding, and a tuned logistic regression classifier are bundled into one artifact, so training-time and inference-time transforms can never drift apart.",
  },
  {
    icon: Server,
    title: "Scored inside one backend",
    description:
      "FastAPI is the only service that ever loads the model or talks to the database. The browser never touches either directly.",
  },
  {
    icon: ShieldCheck,
    title: "Reviewed by a person, always",
    description:
      "The prediction informs a loan officer's decision — it never makes one on its own, and every status change carries a documented reviewer note.",
  },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-16">
      <span className="text-brand text-sm font-medium">About</span>
      <h1 className="font-display font-semibold text-4xl text-ink mt-2">
        How a loan application becomes a number
      </h1>
      <p className="text-ink-muted mt-4 leading-relaxed max-w-2xl">
        This system exists to answer one question quickly and consistently: given what an
        applicant has told us, how likely are they to default? Here's what happens between your
        submission and that answer.
      </p>

      <div className="mt-12 space-y-8">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div key={step.title} className="flex gap-5">
              <div className="flex flex-col items-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-subtle text-brand shrink-0">
                  <Icon className="h-5 w-5" />
                </div>
                {index < steps.length - 1 && <div className="w-px flex-1 bg-border mt-2" />}
              </div>
              <div className="pb-8">
                <h2 className="font-display font-medium text-lg text-ink">{step.title}</h2>
                <p className="text-sm text-ink-muted mt-1.5 leading-relaxed max-w-xl">
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 grid sm:grid-cols-3 gap-5 border-t border-border pt-10">
        <div>
          <p className="figure text-2xl font-medium text-ink">69.1%</p>
          <p className="text-xs text-ink-muted mt-1">Test accuracy</p>
        </div>
        <div>
          <p className="figure text-2xl font-medium text-ink">69.7%</p>
          <p className="text-xs text-ink-muted mt-1">Recall on defaults</p>
        </div>
        <div>
          <p className="figure text-2xl font-medium text-ink">0.761</p>
          <p className="text-xs text-ink-muted mt-1">ROC-AUC</p>
        </div>
      </div>
    </div>
  );
}