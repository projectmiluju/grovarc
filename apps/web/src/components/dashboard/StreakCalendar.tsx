"use client";

import { useMemo } from "react";
import { eachDayOfInterval, subDays, format, isSameDay } from "date-fns";
import { cn } from "@/lib/utils";

interface StreakCalendarProps {
  activeDates: string[]; // "YYYY-MM-DD" 배열
}

export function StreakCalendar({ activeDates }: StreakCalendarProps) {
  const today = new Date();
  const days = useMemo(
    () => eachDayOfInterval({ start: subDays(today, 6 * 7 - 1), end: today }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const activeSet = useMemo(() => new Set(activeDates), [activeDates]);

  // 7행(요일) x N열(주) 그리드
  const weeks: Date[][] = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }

  return (
    <div className="rounded-lg border bg-card p-5">
      <h3 className="mb-4 text-sm font-medium">최근 6주 활동</h3>
      <div className="flex gap-1">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((day) => {
              const key = format(day, "yyyy-MM-dd");
              const active = activeSet.has(key);
              const isToday = isSameDay(day, today);
              return (
                <div
                  key={key}
                  title={key}
                  className={cn(
                    "h-4 w-4 rounded-sm",
                    active ? "bg-primary" : "bg-muted",
                    isToday && !active && "ring-1 ring-primary",
                  )}
                />
              );
            })}
          </div>
        ))}
      </div>
      <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
        <div className="h-3 w-3 rounded-sm bg-muted" />
        <span>없음</span>
        <div className="h-3 w-3 rounded-sm bg-primary" />
        <span>작성</span>
      </div>
    </div>
  );
}
