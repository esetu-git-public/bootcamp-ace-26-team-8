"use client";

import Link from "next/link";
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell, TableEmptyState } from "@/components/ui/Table";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { Pagination } from "@/components/ui/Pagination";
import { Spinner } from "@/components/ui/Spinner";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";
import type { LoanApplicationRecord } from "@/types/loan";

interface ApplicationsQueueTableProps {
  applications: LoanApplicationRecord[];
  isLoading: boolean;
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
  onPageSelect: (page: number) => void;
}

export function ApplicationsQueueTable({
  applications,
  isLoading,
  page,
  totalPages,
  onPrev,
  onNext,
  onPageSelect,
}: ApplicationsQueueTableProps) {
  if (isLoading) {
    return (
      <div className="py-16 flex justify-center">
        <Spinner size="lg" label="Loading applications…" />
      </div>
    );
  }

  return (
    <div>
      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell>Application</TableHeaderCell>
            <TableHeaderCell>Applicant</TableHeaderCell>
            <TableHeaderCell>Amount</TableHeaderCell>
            <TableHeaderCell>Prediction</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Submitted</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {applications.length === 0 ? (
            <TableEmptyState colSpan={6} message="No applications match the current filters." />
          ) : (
            applications.map((app) => (
              <TableRow key={app.application_id}>
                <TableCell>
                  <Link
                    href={`${ROUTES.officerApplications}/${app.application_id}`}
                    className="text-brand font-medium hover:text-brand-hover"
                  >
                    {app.application_id}
                  </Link>
                </TableCell>
                <TableCell>
                  <p className="text-ink">{app.applicant_name}</p>
                  <p className="text-xs text-ink-muted">{app.loan_purpose}</p>
                </TableCell>
                <TableCell className="figure">{formatCurrency(app.loan_amount)}</TableCell>
                <TableCell>
                  <RiskBadge prediction={app.prediction} />
                </TableCell>
                <TableCell>
                  <StatusBadge status={app.status} />
                </TableCell>
                <TableCell className="text-ink-muted">{formatDate(app.submitted_date)}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <Pagination page={page} totalPages={totalPages} onPrev={onPrev} onNext={onNext} onPageSelect={onPageSelect} />
    </div>
  );
}