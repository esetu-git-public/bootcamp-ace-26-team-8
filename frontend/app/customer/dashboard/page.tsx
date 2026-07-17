"use client";

import Link from "next/link";
import { FileText, ClipboardList, AlertTriangle, CheckCircle2 } from "lucide-react";
import { useLoanApplications } from "@/hooks/useLoanApplications";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { ApplicationsByStatusChart } from "@/components/customer/ApplicationsByStatusChart";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";
import { useAuth } from "@/hooks/useAuth";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";

export default function CustomerDashboardPage() {
  const { user } = useAuth();
  const { applications, isLoading, error } = useLoanApplications();

  const approved = applications.filter((a) => a.status === "approved").length;
  const pending = applications.filter((a) => ["submitted", "under_review", "review_requested"].includes(a.status)).length;
  const rejected = applications.filter((a) => a.status === "rejected").length;
  const recent = [...applications]
    .sort((a, b) => new Date(b.submitted_date).getTime() - new Date(a.submitted_date).getTime())
    .slice(0, 5);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display font-semibold text-2xl text-ink">
            Welcome back{user?.fullName ? `, ${user.fullName.split(" ")[0]}` : ""}
          </h1>
          <p className="text-sm text-ink-muted mt-1">Here's where your applications stand.</p>
        </div>
        <Link href={ROUTES.customerApply}>
          <Button>
            <FileText className="h-4 w-4" />
            Apply for a loan
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
          <Spinner size="lg" label="Loading your applications…" />
        </div>
      ) : (
        <>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard label="Total applications" value={String(applications.length)} icon={ClipboardList} tone="brand" />
            <StatCard label="Approved" value={String(approved)} icon={CheckCircle2} tone="success" />
            <StatCard label="Pending review" value={String(pending)} icon={FileText} tone="warning" />
            <StatCard label="Rejected" value={String(rejected)} icon={AlertTriangle} tone="danger" />
          </div>

          <div className="grid lg:grid-cols-5 gap-5">
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>Recent applications</CardTitle>
              </CardHeader>
              <CardContent>
                {recent.length === 0 ? (
                  <p className="text-sm text-ink-muted py-8 text-center">
                    You haven't applied for a loan yet.
                  </p>
                ) : (
                  <ul className="divide-y divide-border -mx-5">
                    {recent.map((app) => (
                      <li key={app.application_id} className="px-5 py-3 flex items-center justify-between gap-3">
                        <div>
                          <Link
                            href={`${ROUTES.customerApplications}/${app.application_id}`}
                            className="text-sm font-medium text-ink hover:text-brand"
                          >
                            {app.application_id}
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

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Applications by status</CardTitle>
              </CardHeader>
              <CardContent>
                <ApplicationsByStatusChart applications={applications} />
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}