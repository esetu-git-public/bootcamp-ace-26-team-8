"use client";

import { useLoanApplications } from "@/hooks/useLoanApplications";
import { ApplicationHistoryTable } from "@/components/customer/ApplicationHistoryTable";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";

export default function ApplicationsPage() {
  const { applications, isLoading, error } = useLoanApplications();

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display font-semibold text-2xl text-ink">My applications</h1>
        <p className="text-sm text-ink-muted mt-1">Every application you've submitted, and its current status.</p>
      </div>

      {error && (
        <Alert tone="danger" className="mb-6">
          {error}
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Application history</CardTitle>
          <CardDescription>Search, filter, or export any application as a PDF record.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-16 flex justify-center">
              <Spinner size="lg" label="Loading applications…" />
            </div>
          ) : (
            <ApplicationHistoryTable applications={applications} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}