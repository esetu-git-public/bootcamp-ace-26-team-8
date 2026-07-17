import jsPDF from "jspdf";
import type { LoanApplicationRecord } from "@/types/loan";
import { formatCurrency, formatDateTime, formatPercent } from "@/lib/utils";
import { STATUS_LABELS } from "@/lib/constants";

/**
 * Builds a formatted PDF record of a single loan application directly
 * with jsPDF's text/line primitives (not a screenshot of the DOM), so
 * the exported document stays crisp and text-selectable.
 */
export function exportApplicationToPdf(application: LoanApplicationRecord): void {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const marginX = 48;
  let y = 56;

  const line = (label: string, value: string, opts?: { bold?: boolean }) => {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.setTextColor(90, 96, 110);
    doc.text(label.toUpperCase(), marginX, y);
    doc.setFont("helvetica", opts?.bold ? "bold" : "normal");
    doc.setFontSize(11);
    doc.setTextColor(16, 24, 40);
    doc.text(value, marginX, y + 14);
    y += 38;
  };

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(16, 24, 40);
  doc.text("Loan Application Record", marginX, y);
  y += 10;
  doc.setDrawColor(227, 230, 235);
  doc.line(marginX, y + 10, 547, y + 10);
  y += 40;

  line("Application ID", application.application_id);
  line("Status", STATUS_LABELS[application.status], { bold: true });
  line("Applicant", `${application.applicant_name}  ·  ${application.email}  ·  ${application.phone}`);

  const colX = marginX + 250;
  const startY = y;
  line("Loan amount", formatCurrency(application.loan_amount));
  const afterFirstCol = y;
  y = startY;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(90, 96, 110);
  doc.text("DEFAULT PROBABILITY", colX, y);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(application.prediction === 1 ? 179 : 31, application.prediction === 1 ? 38 : 138, application.prediction === 1 ? 30 : 112);
  doc.text(formatPercent(application.probability), colX, y + 14);
  y = afterFirstCol;

  line("Credit score", String(application.credit_score));
  line("Annual income", formatCurrency(application.income));
  line("Interest rate / Term", `${application.interest_rate}%  ·  ${application.loan_term} months`);
  line("Employment", `${application.employment_type}  ·  ${application.months_employed} months employed`);
  line("Loan purpose", application.loan_purpose);
  line("Submitted", formatDateTime(application.submitted_date));

  if (application.reviewed_by) {
    line("Reviewed", formatDateTime(application.reviewed_date));
  }
  if (application.review_note) {
    line("Reviewer note", application.review_note);
  }

  doc.setFontSize(8);
  doc.setTextColor(152, 162, 179);
  doc.text(
    "Generated from the Loan Default Prediction System. Prediction is a model output and does not constitute a final lending decision.",
    marginX,
    780
  );

  doc.save(`application-${application.application_id}.pdf`);
}
/**
 * Builds a formatted PDF summary of the officer Analytics page: headline
 * stats, status breakdown counts, and risk distribution counts. Built with
 * jsPDF's text/line primitives (not a DOM screenshot), matching
 * exportApplicationToPdf's approach so text stays crisp and selectable.
 */
export function exportAnalyticsToPdf(applications: LoanApplicationRecord[]): void {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const marginX = 48;
  let y = 56;

  const line = (label: string, value: string, opts?: { bold?: boolean }) => {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.setTextColor(90, 96, 110);
    doc.text(label.toUpperCase(), marginX, y);
    doc.setFont("helvetica", opts?.bold ? "bold" : "normal");
    doc.setFontSize(11);
    doc.setTextColor(16, 24, 40);
    doc.text(value, marginX, y + 14);
    y += 38;
  };

  const sectionHeader = (title: string) => {
    y += 6;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.setTextColor(16, 24, 40);
    doc.text(title, marginX, y);
    y += 10;
    doc.setDrawColor(227, 230, 235);
    doc.line(marginX, y + 6, 547, y + 6);
    y += 30;
  };

  // --- Header ---
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(16, 24, 40);
  doc.text("Analytics Report", marginX, y);
  y += 10;
  doc.setDrawColor(227, 230, 235);
  doc.line(marginX, y + 10, 547, y + 10);
  y += 40;

  line("Generated", formatDateTime(new Date().toISOString()));
  line("Applications covered", String(applications.length));

  // --- Headline stats ---
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

  sectionHeader("Summary");
  line("Approval rate", `${(approvalRate * 100).toFixed(0)}%`, { bold: true });
  line("Avg. default probability", formatPercent(avgProbability));
  line("Avg. loan amount", formatCurrency(avgLoanAmount));

  // --- Status breakdown ---
  sectionHeader("Status breakdown");
  const statusCounts = applications.reduce<Record<string, number>>((acc, app) => {
    acc[app.status] = (acc[app.status] ?? 0) + 1;
    return acc;
  }, {});
  Object.entries(statusCounts).forEach(([status, count]) => {
    const label = STATUS_LABELS[status as keyof typeof STATUS_LABELS] ?? status;
    const pct = applications.length > 0 ? (count / applications.length) * 100 : 0;
    line(label, `${count} (${pct.toFixed(0)}%)`);
  });

  // --- Risk distribution ---
  sectionHeader("Risk distribution");
  const buckets = [
    { label: "0–20% (Low risk)", min: 0, max: 0.2 },
    { label: "20–40%", min: 0.2, max: 0.4 },
    { label: "40–60%", min: 0.4, max: 0.6 },
    { label: "60–80%", min: 0.6, max: 0.8 },
    { label: "80–100% (Default risk)", min: 0.8, max: 1.01 },
  ];
  buckets.forEach((bucket) => {
    const count = applications.filter(
      (a) => a.probability >= bucket.min && a.probability < bucket.max
    ).length;
    line(bucket.label, String(count));
  });

  // --- Footer ---
  doc.setFontSize(8);
  doc.setTextColor(152, 162, 179);
  doc.text(
    "Generated from the Loan Default Prediction System. Aggregated across currently loaded applications only.",
    marginX,
    780
  );

  doc.save(`analytics-report-${new Date().toISOString().slice(0, 10)}.pdf`);
}