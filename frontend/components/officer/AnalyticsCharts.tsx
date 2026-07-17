"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import type { LoanApplicationRecord } from "@/types/loan";
import { STATUS_LABELS } from "@/lib/constants";

const STATUS_COLORS: Record<string, string> = {
  submitted: "#98a2b3",
  under_review: "#1f8a70",
  approved: "#1f8a70",
  rejected: "#b3261e",
  review_requested: "#b1740f",
};

export function StatusBreakdownChart({ applications }: { applications: LoanApplicationRecord[] }) {
  const counts = applications.reduce<Record<string, number>>((acc, app) => {
    acc[app.status] = (acc[app.status] ?? 0) + 1;
    return acc;
  }, {});
  const data = Object.entries(counts).map(([status, value]) => ({
    name: STATUS_LABELS[status as keyof typeof STATUS_LABELS],
    value,
    status,
  }));

  return (
    <ResponsiveContainer width="100%" height={240} initialDimension={{ width: 520, height: 240 }}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
          {data.map((entry) => (
            <Cell key={entry.status} fill={STATUS_COLORS[entry.status]} />
          ))}
        </Pie>
        <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid var(--color-border)", fontSize: 12 }} />
        <Legend iconType="circle" iconSize={8} formatter={(v) => <span className="text-xs text-ink-muted">{v}</span>} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function RiskDistributionChart({ applications }: { applications: LoanApplicationRecord[] }) {
  const buckets = [
    { label: "0–20%", min: 0, max: 0.2 },
    { label: "20–40%", min: 0.2, max: 0.4 },
    { label: "40–60%", min: 0.4, max: 0.6 },
    { label: "60–80%", min: 0.6, max: 0.8 },
    { label: "80–100%", min: 0.8, max: 1.01 },
  ];

  const data = buckets.map((bucket) => ({
    label: bucket.label,
    count: applications.filter((a) => a.probability >= bucket.min && a.probability < bucket.max).length,
  }));

  return (
    <ResponsiveContainer width="100%" height={240} initialDimension={{ width: 520, height: 240 }}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: "var(--color-ink-muted)" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "var(--color-ink-muted)" }} axisLine={false} tickLine={false} allowDecimals={false} />
        <Tooltip
          cursor={{ fill: "var(--color-surface-inset)" }}
          contentStyle={{ borderRadius: 8, border: "1px solid var(--color-border)", fontSize: 12 }}
        />
        <Bar dataKey="count" fill="var(--color-brand)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}