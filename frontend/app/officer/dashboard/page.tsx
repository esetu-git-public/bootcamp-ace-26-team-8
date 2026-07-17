"use client";

import Link from "next/link";
import { ClipboardList, AlertTriangle, CheckCircle2, Clock } from "lucide-react";
import { useOfficerApplications } from "@/hooks/useOfficerApplications";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";

export default function OfficerDashboardPage() {
  const { applications, total, isLoading, error } = useOfficerApplications({ pageSize: 50 });

  const pending = applications.filter((a) => ["submitted", "under_review", "review_requested"].includes(a.status));
  const approved = applications.filter((a) => a.status === "approved").length;
  const rejected = applications.filter((a) => a.status === "rejected").length;
  const approvalRate = applications.length > 0 ? approved / applications.length : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display font-semibold text-2xl text-ink">Officer dashboard</h1>
          <p className="text-sm text-ink-muted mt-1">A snapshot of the current review queue.</p>
        </div>
        <Link href={ROUTES.officerApplications}>
          <Button>
            <ClipboardList className="h-4 w-4" />
            Go to queue
          </Button>
        </Link>
      </div>

      {error && (
        <Alert tone="danger" className="mb-6">
          {error}
        </Alert>
      )}

      {isLoading ? (
        <div className="py-16 flex justify-center">
          <Spinner size="lg" label="Loading queue…" />
        </div>
      ) : (
        <>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard label="Total applications" value={String(total)} icon={ClipboardList} tone="brand" />
            <StatCard label="Awaiting decision" value={String(pending.length)} icon={Clock} tone="warning" />
            <StatCard
              label="Approval rate"
              value={`${(approvalRate * 100).toFixed(0)}%`}
              icon={CheckCircle2}
              tone="success"
            />
            <StatCard label="Rejected" value={String(rejected)} icon={AlertTriangle} tone="danger" />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Needs attention</CardTitle>
            </CardHeader>
            <CardContent>
              {pending.length === 0 ? (
                <p className="text-sm text-ink-muted py-8 text-center">The queue is clear — nothing pending review.</p>
              ) : (
                <ul className="divide-y divide-border -mx-5">
                  {pending.slice(0, 8).map((app) => (
                    <li key={app.application_id} className="px-5 py-3 flex items-center justify-between gap-3">
                      <div>
                        <Link
                          href={`${ROUTES.officerApplications}/${app.application_id}`}
                          className="text-sm font-medium text-ink hover:text-brand"
                        >
                          {app.applicant_name}
                        </Link>
                        <p className="text-xs text-ink-muted mt-0.5">
                          {formatCurrency(app.loan_amount)} · {formatDate(app.submitted_date)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <RiskBadge prediction={app.prediction} />
                        <StatusBadge status={app.status} />
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}