"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { Loader2, TrendingUp } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { requestCoaching } from "@/lib/coaching";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";
import type { CoachingResult } from "@/types";

export default function CoachingPage() {
  const user = useAuthStore((s) => s.user);
  const [history, setHistory] = useState<CoachingResult[]>([]);
  const [current, setCurrent] = useState<CoachingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);

  const handleRequest = async () => {
    if (!user) return;
    setLoading(true);
    setError("");
    try {
      const result = await requestCoaching(user.id);
      setHistory((prev) => [result, ...prev]);
      setCurrent(result);
      setSelectedIdx(0);
    } catch {
      setError("코칭 분석에 실패했습니다. 잠시 후 다시 시도하세요.");
    } finally {
      setLoading(false);
    }
  };

  const displayed = current ?? history[selectedIdx] ?? null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">성장 코칭</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            최근 3개월 작업 로그를 분석해 개인화된 8주 학습 로드맵을 제공합니다.
          </p>
        </div>
        <Button onClick={handleRequest} disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              분석 중...
            </>
          ) : (
            <>
              <TrendingUp className="mr-2 h-4 w-4" />
              코칭 요청
            </>
          )}
        </Button>
      </div>

      {error && (
        <p className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </p>
      )}

      {loading && (
        <div className="flex flex-col items-center gap-3 rounded-lg border bg-card py-16">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            최근 3개월 로그를 분석하고 있습니다...
          </p>
          <p className="text-xs text-muted-foreground">최대 1~2분 소요될 수 있습니다.</p>
        </div>
      )}

      {!loading && displayed && (
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          {/* 히스토리 사이드바 */}
          {history.length > 1 && (
            <aside className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                이전 코칭
              </p>
              {history.map((h, i) => (
                <button
                  key={h.mongoDocId ?? i}
                  onClick={() => { setSelectedIdx(i); setCurrent(h); }}
                  className={cn(
                    "w-full rounded-lg border p-3 text-left text-sm transition-colors",
                    i === selectedIdx
                      ? "border-primary bg-primary/5"
                      : "bg-card hover:bg-accent",
                  )}
                >
                  <p className="font-medium">코칭 #{history.length - i}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {format(new Date(h.createdAt), "M월 d일 HH:mm", { locale: ko })}
                  </p>
                </button>
              ))}
            </aside>
          )}

          {/* 코칭 결과 */}
          <div className="space-y-5">
            {/* 부족 스택 */}
            {displayed.weakStacks.length > 0 && (
              <div className="rounded-lg border bg-card p-5">
                <h2 className="mb-3 text-sm font-semibold">학습 추천 기술 스택</h2>
                <div className="flex flex-wrap gap-2">
                  {displayed.weakStacks.map((stack) => (
                    <span
                      key={stack}
                      className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary"
                    >
                      {stack}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 학습 로드맵 */}
            <div className="rounded-lg border bg-card p-5">
              <h2 className="mb-4 text-sm font-semibold">8주 학습 로드맵</h2>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{displayed.roadmap}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !displayed && (
        <div className="flex flex-col items-center gap-3 rounded-lg border bg-card py-20">
          <TrendingUp className="h-10 w-10 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            코칭 요청 버튼을 눌러 성장 분석을 시작하세요.
          </p>
        </div>
      )}
    </div>
  );
}
