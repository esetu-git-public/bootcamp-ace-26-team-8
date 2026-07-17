"use client";

import { use } from "react";
import { Download, Printer } from "lucide-react";
import { useApplicationDetail } from "@/hooks/useLoanApplications";
import { ApplicationStatusTimeline } from "@/components/customer/ApplicationStatusTimeline";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { FullPageSpinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";
import { exportApplicationToPdf } from "@/lib/pdfExport";
import { formatCurrency, formatPercent, formatDate } from "@/lib/utils";

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-ink-muted uppercase tracking-wide">{label}</p>
      <p className="figure text-sm text-ink mt-1">{value}</p>
    </div>
  );
}

export default function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { application, isLoading, error } = useApplicationDetail(id);

  if (isLoading) return <FullPageSpinner label="Loading application…" />;

  if (error || !application) {
    return (
      <Alert tone="danger" title="Couldn't load this application">
        {error ?? "This application couldn't be found."}
      </Alert>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-start justify-between mb-6 no-print">
        <div>
          <h1 className="font-display font-semibold text-2xl text-ink">{application.application_id}</h1>
          <p className="text-sm text-ink-muted mt-1">Submitted {formatDate(application.submitted_date)}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => window.print()}>
            <Printer className="h-4 w-4" />
            Print
          </Button>
          <Button variant="outline" size="sm" onClick={() => exportApplicationToPdf(application)}>
            <Download className="h-4 w-4" />
            Export PDF
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        <Card className="lg:col-span-2 print-surface">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Application details</CardTitle>
            <div className="flex gap-2">
              <RiskBadge prediction={application.prediction} />
              <StatusBadge status={application.status} />
            </div>
          </CardHeader>
          <CardContent className="grid sm:grid-cols-2 gap-5">
            <Field label="Applicant" value={application.applicant_name} />
            <Field label="Contact" value={`${application.email} · ${application.phone}`} />
            <Field label="Loan amount" value={formatCurrency(application.loan_amount)} />
            <Field label="Default probability" value={formatPercent(application.probability)} />
            <Field label="Credit score" value={String(application.credit_score)} />
            <Field label="Annual income" value={formatCurrency(application.income)} />
            <Field label="Interest rate" value={`${application.interest_rate}%`} />
            <Field label="Loan term" value={`${application.loan_term} months`} />
            <Field label="Employment" value={`${application.employment_type} · ${application.months_employed} mo.`} />
            <Field label="Debt-to-income ratio" value={String(application.dti_ratio)} />
            <Field label="Loan purpose" value={application.loan_purpose} />
            <Field label="Education" value={application.education} />
          </CardContent>
        </Card>

        <Card className="print-surface">
          <CardHeader>
            <CardTitle>Status timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <ApplicationStatusTimeline
              status={application.status}
              submittedDate={application.submitted_date}
              reviewedDate={application.reviewed_date}
              reviewNote={application.review_note}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}