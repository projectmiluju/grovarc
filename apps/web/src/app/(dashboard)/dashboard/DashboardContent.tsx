"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { StatCard } from "@/components/dashboard/StatCard";
import { StreakCalendar } from "@/components/dashboard/StreakCalendar";
import { WeeklyChart } from "@/components/dashboard/WeeklyChart";
import api from "@/lib/api";
import type { DashboardStats, Retrospective } from "@/types";

export function DashboardContent() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentRetros, setRecentRetros] = useState<Retrospective[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<DashboardStats>("/api/v1/dashboard"),
      api.get<{ content: Retrospective[] }>("/api/v1/retrospectives?size=3&status=PUBLISHED"),
    ])
      .then(([statsRes, retrosRes]) => {
        setStats(statsRes.data);
        setRecentRetros(retrosRes.data.content);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) return null;

  // 스트릭 캘린더용 날짜 추출 (weeklyLogCounts에서)
  const activeDates = stats.weeklyLogCounts
    .filter((d) => d.count > 0)
    .map((d) => d.date);

  return (
    <div className="space-y-6">
      {/* 통계 카드 */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="총 로그" value={stats.totalLogs} sub="누적" />
        <StatCard label="총 회고" value={stats.totalRetrospectives} sub="누적" />
        <StatCard
          label="현재 스트릭"
          value={`${stats.currentStreak}일`}
          sub="연속 작성"
        />
        <StatCard
          label="최장 스트릭"
          value={`${stats.longestStreak}일`}
          sub="역대 최장"
        />
      </div>

      {/* 캘린더 + 차트 */}
      <div className="grid gap-4 md:grid-cols-2">
        <StreakCalendar activeDates={activeDates} />
        <WeeklyChart data={stats.weeklyLogCounts.slice(-7)} />
      </div>

      {/* 최근 회고 */}
      {recentRetros.length > 0 && (
        <div className="rounded-lg border bg-card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-medium">최근 회고</h3>
            <Link href="/retrospectives" className="text-xs text-muted-foreground hover:underline">
              전체 보기
            </Link>
          </div>
          <ul className="space-y-2">
            {recentRetros.map((retro) => (
              <li key={retro.id}>
                <Link
                  href={`/retrospectives/${retro.id}`}
                  className="flex items-center justify-between rounded-md p-2 hover:bg-accent"
                >
                  <span className="text-sm font-medium">{retro.title}</span>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(retro.periodFrom), "M/d")} ~{" "}
                    {format(new Date(retro.periodTo), "M/d")}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
