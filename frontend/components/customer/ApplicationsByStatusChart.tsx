"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { LoanApplicationRecord } from "@/types/loan";
import { STATUS_LABELS } from "@/lib/constants";

const COLORS: Record<string, string> = {
  submitted: "#98a2b3",
  under_review: "#1f8a70",
  approved: "#1f8a70",
  rejected: "#b3261e",
  review_requested: "#b1740f",
};

export function ApplicationsByStatusChart({ applications }: { applications: LoanApplicationRecord[] }) {
  const counts = applications.reduce<Record<string, number>>((acc, app) => {
    acc[app.status] = (acc[app.status] ?? 0) + 1;
    return acc;
  }, {});

  const data = Object.entries(counts).map(([status, value]) => ({
    name: STATUS_LABELS[status as keyof typeof STATUS_LABELS],
    value,
    status,
  }));

  if (data.length === 0) {
    return <p className="text-sm text-ink-muted text-center py-12">No applications yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={80} paddingAngle={2}>
          {data.map((entry) => (
            <Cell key={entry.status} fill={COLORS[entry.status]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number) => [value, "Applications"]}
          contentStyle={{
            borderRadius: 8,
            border: "1px solid var(--color-border)",
            fontSize: 12,
          }}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value) => <span className="text-xs text-ink-muted">{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}