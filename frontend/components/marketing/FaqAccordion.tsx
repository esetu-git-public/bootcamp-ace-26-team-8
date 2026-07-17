"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface FaqItem {
  question: string;
  answer: string;
}

const faqItems: FaqItem[] = [
  {
    question: "How is my default probability calculated?",
    answer:
      "A logistic regression pipeline, trained on 255,347 historical loan applications, scores your submitted profile — income, credit score, employment history, and loan terms — the instant you apply. The same pipeline scores every applicant identically.",
  },
  {
    question: "Does applying affect my credit score?",
    answer:
      "No. This system runs entirely on the information you provide in the application form; it never performs a credit bureau pull or reports back to any bureau.",
  },
  {
    question: "What happens after I submit an application?",
    answer:
      "You'll see your prediction immediately. A loan officer then reviews the full application — not just the score — and approves, rejects, or requests further review. You can track the status from your dashboard at any time.",
  },
  {
    question: "Can a rejected application be reconsidered?",
    answer:
      "Yes. An officer can move a rejected application to 'review requested' to reopen it for a closer look, but it can never be re-approved directly from rejected — that extra step is required for every reversal.",
  },
  {
    question: "Who can see my application?",
    answer:
      "Only you and authenticated loan officers can view your full application detail. All access is verified server-side on every request — no data is ever exposed directly from the database.",
  },
  {
    question: "How is my data stored?",
    answer:
      "Your application, prediction, and every subsequent status change are stored as one auditable record, timestamped and attributed to the reviewing officer, and never altered after the fact except for that workflow status.",
  },
];

export function FaqAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="divide-y divide-border border border-border rounded-lg bg-surface">
      {faqItems.map((item, index) => {
        const isOpen = openIndex === index;
        return (
          <div key={item.question}>
            <button
              className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left focus-ring"
              onClick={() => setOpenIndex(isOpen ? null : index)}
              aria-expanded={isOpen}
              aria-controls={`faq-panel-${index}`}
            >
              <span className="font-medium text-ink text-sm sm:text-base">{item.question}</span>
              <ChevronDown
                className={cn(
                  "h-4 w-4 shrink-0 text-ink-faint transition-transform duration-200",
                  isOpen && "rotate-180"
                )}
              />
            </button>
            <div
              id={`faq-panel-${index}`}
              className={cn(
                "grid transition-[grid-template-rows] duration-200 ease-out",
                isOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
              )}
            >
              <div className="overflow-hidden">
                <p className="px-5 pb-4 text-sm text-ink-muted leading-relaxed">{item.answer}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}