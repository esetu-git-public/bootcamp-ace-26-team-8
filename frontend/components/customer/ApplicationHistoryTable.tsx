"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Download } from "lucide-react";
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell, TableEmptyState } from "@/components/ui/Table";
import { StatusBadge, RiskBadge } from "@/components/ui/Badge";
import { SearchInput } from "@/components/ui/SearchInput";
import { Select } from "@/components/ui/Select";
import { Pagination } from "@/components/ui/Pagination";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePagination } from "@/hooks/usePagination";
import { exportApplicationToPdf } from "@/lib/pdfExport";
import { formatCurrency, formatDate } from "@/lib/utils";
import { LOAN_STATUSES, STATUS_LABELS, ROUTES } from "@/lib/constants";
import type { LoanApplicationRecord } from "@/types/loan";
import { FileText } from "lucide-react";

export function ApplicationHistoryTable({ applications }: { applications: LoanApplicationRecord[] }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  const filtered = useMemo(() => {
    return applications.filter((app) => {
      const matchesSearch =
        !search ||
        app.application_id.toLowerCase().includes(search.toLowerCase()) ||
        app.loan_purpose.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = !statusFilter || app.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [applications, search, statusFilter]);

  const { page, totalPages, pageItems, setPage, nextPage, prevPage } = usePagination(filtered, { pageSize: 8 });

  if (applications.length === 0) {
    return (
      <EmptyState
        icon={FileText}
        title="No applications yet"
        description="Once you submit a loan application, it will show up here with its status and prediction."
        action={
          <Link href={ROUTES.customerApply}>
            <Button>Apply for a loan</Button>
          </Link>
        }
      />
    );
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by ID or purpose…" className="sm:max-w-xs" />
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          options={LOAN_STATUSES.map((s) => ({ label: STATUS_LABELS[s], value: s }))}
          placeholder="All statuses"
          className="sm:max-w-[200px]"
        />
      </div>

      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell>Application</TableHeaderCell>
            <TableHeaderCell>Amount</TableHeaderCell>
            <TableHeaderCell>Prediction</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Submitted</TableHeaderCell>
            <TableHeaderCell className="text-right">Actions</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {pageItems.length === 0 ? (
            <TableEmptyState colSpan={6} message="No applications match your filters." />
          ) : (
            pageItems.map((app) => (
              <TableRow key={app.application_id}>
                <TableCell>
                  <Link href={`${ROUTES.customerApplications}/${app.application_id}`} className="text-brand font-medium hover:text-brand-hover">
                    {app.application_id}
                  </Link>
                  <p className="text-xs text-ink-muted mt-0.5">{app.loan_purpose}</p>
                </TableCell>
                <TableCell className="figure">{formatCurrency(app.loan_amount)}</TableCell>
                <TableCell>
                  <RiskBadge prediction={app.prediction} />
                </TableCell>
                <TableCell>
                  <StatusBadge status={app.status} />
                </TableCell>
                <TableCell className="text-ink-muted">{formatDate(app.submitted_date)}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" onClick={() => exportApplicationToPdf(app)}>
                    <Download className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <Pagination page={page} totalPages={totalPages} onPrev={prevPage} onNext={nextPage} onPageSelect={setPage} />
    </div>
  );
}