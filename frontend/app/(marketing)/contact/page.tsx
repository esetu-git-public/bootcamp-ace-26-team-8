import type { Metadata } from "next";
import { Mail, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { ContactForm } from "@/components/marketing/ContactForm";

export const metadata: Metadata = { title: "Contact us" };

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-16 grid lg:grid-cols-5 gap-10">
      <div className="lg:col-span-2">
        <span className="text-brand text-sm font-medium">Contact</span>
        <h1 className="font-display font-semibold text-3xl text-ink mt-2">Get in touch</h1>
        <p className="text-ink-muted mt-4 leading-relaxed">
          Questions about an application, a decision, or the platform itself — we'll route it to
          the right team.
        </p>

        <div className="mt-8 space-y-4">
          <Card>
            <CardContent className="flex items-start gap-3 pt-5">
              <Mail className="h-4 w-4 text-brand mt-0.5" />
              <div>
                <p className="text-sm font-medium text-ink">Email</p>
                <p className="text-sm text-ink-muted">support@ledger.app</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-start gap-3 pt-5">
              <Clock className="h-4 w-4 text-brand mt-0.5" />
              <div>
                <p className="text-sm font-medium text-ink">Response time</p>
                <p className="text-sm text-ink-muted">Within 1 business day</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card className="lg:col-span-3">
        <CardContent className="pt-6">
          <ContactForm />
        </CardContent>
      </Card>
    </div>
  );
}