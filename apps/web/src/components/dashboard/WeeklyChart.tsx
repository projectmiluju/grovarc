"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { format, parseISO } from "date-fns";
import { ko } from "date-fns/locale";

interface WeeklyChartProps {
  data: { date: string; count: number }[];
}

export function WeeklyChart({ data }: WeeklyChartProps) {
  const chartData = data.map((d) => ({
    ...d,
    label: format(parseISO(d.date), "M/d", { locale: ko }),
  }));

  return (
    <div className="rounded-lg border bg-card p-5">
      <h3 className="mb-4 text-sm font-medium">최근 7일 작성 현황</h3>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
          <XAxis dataKey="label" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 12 }} allowDecimals={false} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ fill: "hsl(var(--accent))" }}
            contentStyle={{
              background: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "6px",
              fontSize: "12px",
            }}
            formatter={(v: number) => [`${v}개`, "로그"]}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.count > 0 ? "hsl(var(--primary))" : "hsl(var(--muted))"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
