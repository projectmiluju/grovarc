"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AiDraftModal } from "./AiDraftModal";
import { getRetrospectives } from "@/lib/retrospective";
import { cn } from "@/lib/utils";
import type { Retrospective, RetroStatus } from "@/types";

const TABS: { label: string; value: RetroStatus | "ALL" }[] = [
  { label: "전체", value: "ALL" },
  { label: "발행됨", value: "PUBLISHED" },
  { label: "초안", value: "DRAFT" },
];

export default function RetrospectivesPage() {
  const [tab, setTab] = useState<RetroStatus | "ALL">("ALL");
  const [retros, setRetros] = useState<Retrospective[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchRetros = async (status?: RetroStatus) => {
    setLoading(true);
    try {
      const res = await getRetrospectives({ size: 50, status });
      setRetros(res.content);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRetros(tab === "ALL" ? undefined : tab);
  }, [tab]);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">회고</h1>
        <Button size="sm" onClick={() => setShowModal(true)}>
          <Sparkles className="mr-1.5 h-4 w-4" />
          AI 회고 초안 생성
        </Button>
      </div>

      {/* 탭 */}
      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
          <button
            key={t.value}
            onClick={() => setTab(t.value)}
            className={cn(
              "px-4 py-2 text-sm font-medium transition-colors",
              tab === t.value
                ? "border-b-2 border-primary text-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* 목록 */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      ) : retros.length === 0 ? (
        <p className="py-12 text-center text-muted-foreground">회고가 없습니다.</p>
      ) : (
        <ul className="space-y-2">
          {retros.map((retro) => (
            <li key={retro.id}>
              <Link
                href={`/retrospectives/${retro.id}`}
                className="flex items-start justify-between rounded-lg border bg-card p-4 hover:bg-accent/50 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-xs font-medium",
                        retro.status === "PUBLISHED"
                          ? "bg-primary/10 text-primary"
                          : "bg-muted text-muted-foreground",
                      )}
                    >
                      {retro.status === "PUBLISHED" ? "발행됨" : "초안"}
                    </span>
                    <span className="font-medium">{retro.title}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {format(new Date(retro.periodFrom), "M월 d일", { locale: ko })} ~{" "}
                    {format(new Date(retro.periodTo), "M월 d일", { locale: ko })}
                  </p>
                </div>
                <span className="ml-4 shrink-0 text-xs text-muted-foreground">
                  {format(new Date(retro.createdAt), "M/d")}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {showModal && (
        <AiDraftModal
          onClose={() => setShowModal(false)}
          onCreated={() => { setShowModal(false); fetchRetros(); }}
        />
      )}
    </div>
  );
}
