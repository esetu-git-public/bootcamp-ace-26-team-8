"use client";

import { DecisionActionBar } from "@/components/officer/DecisionActionBar";
import { ApplicationStatusTimeline } from "@/components/customer/ApplicationStatusTimeline";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { formatCurrency, formatPercent } from "@/lib/utils";
import type { LoanApplicationRecord, OfficerStatusUpdateRequest, OfficerStatusUpdateResponse } from "@/types/loan";

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-ink-muted uppercase tracking-wide">{label}</p>
      <p className="figure text-sm text-ink mt-1">{value}</p>
    </div>
  );
}

interface ApplicationDetailPanelProps {
  application: LoanApplicationRecord;
  onUpdate: (applicationId: string, payload: OfficerStatusUpdateRequest) => Promise<OfficerStatusUpdateResponse>;
}

export function ApplicationDetailPanel({ application, onUpdate }: ApplicationDetailPanelProps) {
  return (
    <div className="grid lg:grid-cols-3 gap-5">
      <Card className="lg:col-span-2">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>{application.application_id}</CardTitle>
          <div className="flex gap-2">
            <RiskBadge prediction={application.prediction} />
            <StatusBadge status={application.status} />
          </div>
        </CardHeader>
        <CardContent className="grid sm:grid-cols-2 gap-5">
          <Field label="Applicant" value={application.applicant_name} />
          <Field label="Contact" value={`${application.email} · ${application.phone}`} />
          <Field label="Default probability" value={formatPercent(application.probability)} />
          <Field label="Loan amount" value={formatCurrency(application.loan_amount)} />
          <Field label="Credit score" value={String(application.credit_score)} />
          <Field label="Annual income" value={formatCurrency(application.income)} />
          <Field label="Interest rate" value={`${application.interest_rate}%`} />
          <Field label="Loan term" value={`${application.loan_term} months`} />
          <Field label="Employment" value={`${application.employment_type} · ${application.months_employed} mo.`} />
          <Field label="Debt-to-income ratio" value={String(application.dti_ratio)} />
          <Field label="Loan purpose" value={application.loan_purpose} />
          <Field label="Marital status" value={application.marital_status} />
          <Field label="Mortgage / Dependents / Co-signer" value={`${application.has_mortgage} / ${application.has_dependents} / ${application.has_co_signer}`} />
          <Field label="Education" value={application.education} />
        </CardContent>
      </Card>

      <div className="flex flex-col gap-5">
        <Card>
          <CardHeader>
            <CardTitle>Decision</CardTitle>
          </CardHeader>
          <CardContent>
            <DecisionActionBar
              applicationId={application.application_id}
              currentStatus={application.status}
              onUpdate={onUpdate}
            />
          </CardContent>
        </Card>

        <Card>
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