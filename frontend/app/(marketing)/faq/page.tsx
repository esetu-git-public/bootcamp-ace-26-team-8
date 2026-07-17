import type { Metadata } from "next";
import { FaqAccordion } from "@/components/marketing/FaqAccordion";

export const metadata: Metadata = { title: "Frequently asked questions" };

export default function FaqPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-16">
      <span className="text-brand text-sm font-medium">FAQ</span>
      <h1 className="font-display font-semibold text-4xl text-ink mt-2">Frequently asked questions</h1>
      <p className="text-ink-muted mt-4 max-w-xl">
        If you don't see your question answered here, reach out through our contact page.
      </p>
      <div className="mt-10">
        <FaqAccordion />
      </div>
    </div>
  );
}