"use client";

import { BarChart3 } from "lucide-react";
import { useOfficerApplications } from "@/hooks/useOfficerApplications";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBreakdownChart, RiskDistributionChart } from "@/components/officer/AnalyticsCharts";
import { Spinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { exportAnalyticsToPdf } from "@/lib/pdfExport";

export default function OfficerAnalyticsPage() {
  const { applications, total, isLoading, error } = useOfficerApplications({ pageSize: 100 });

  const approved = applications.filter((a) => a.status === "approved").length;
  const approvalRate = applications.length > 0 ? approved / applications.length : 0;
  const avgProbability =
    applications.length > 0
      ? applications.reduce((sum, a) => sum + a.probability, 0) / applications.length
      : 0;
  const avgLoanAmount =
    applications.length > 0
      ? applications.reduce((sum, a) => sum + a.loan_amount, 0) / applications.length
      : 0;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="font-display font-semibold text-2xl text-ink">Analytics</h1>
          <p className="text-sm text-ink-muted mt-1">Aggregate view across the current page of loaded applications.</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => exportAnalyticsToPdf(applications)}
          disabled={isLoading || applications.length === 0}
        >
          <Download className="h-4 w-4" />
          Download PDF
        </Button>
      </div>

      {error && (
        <Alert tone="danger" className="mb-6">
          {error}
        </Alert>
      )}

      {isLoading ? (
        <div className="py-16 flex justify-center">
          <Spinner size="lg" label="Crunching numbers…" />
        </div>
      ) : (
        <>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard label="Applications loaded" value={String(total)} icon={BarChart3} tone="brand" />
            <StatCard label="Approval rate" value={`${(approvalRate * 100).toFixed(0)}%`} icon={BarChart3} tone="success" />
            <StatCard label="Avg. default probability" value={formatPercent(avgProbability)} icon={BarChart3} tone="warning" />
            <StatCard label="Avg. loan amount" value={formatCurrency(avgLoanAmount)} icon={BarChart3} tone="neutral" />
          </div>

          <div className="grid lg:grid-cols-2 gap-5">
            <Card>
              <CardHeader>
                <CardTitle>Status breakdown</CardTitle>
                <CardDescription>Distribution of applications by workflow status.</CardDescription>
              </CardHeader>
              <CardContent>
                <StatusBreakdownChart applications={applications} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Risk distribution</CardTitle>
                <CardDescription>Applications grouped by predicted default probability.</CardDescription>
              </CardHeader>
              <CardContent>
                <RiskDistributionChart applications={applications} />
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}