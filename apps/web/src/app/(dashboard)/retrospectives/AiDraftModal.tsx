"use client";

import { useState } from "react";
import { format, subDays } from "date-fns";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { triggerAiDraft } from "@/lib/retrospective";
import { useAuthStore } from "@/store/authStore";

interface AiDraftModalProps {
  onClose: () => void;
  onCreated: () => void;
}

export function AiDraftModal({ onClose, onCreated }: AiDraftModalProps) {
  const user = useAuthStore((s) => s.user);
  const today = format(new Date(), "yyyy-MM-dd");
  const weekAgo = format(subDays(new Date(), 6), "yyyy-MM-dd");

  const [periodFrom, setPeriodFrom] = useState(weekAgo);
  const [periodTo, setPeriodTo] = useState(today);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!user) return;
    setLoading(true);
    setError("");
    try {
      await triggerAiDraft({
        userId: user.id,
        periodFrom,
        periodTo,
      });
      onCreated();
    } catch {
      setError("AI 회고 생성에 실패했습니다. 잠시 후 다시 시도하세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-xl border bg-card p-6 shadow-xl space-y-5">
        <div>
          <h2 className="text-lg font-semibold">AI 회고 초안 생성</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            기간을 선택하면 AI가 작업 로그를 분석해서 회고 초안을 작성해줍니다.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>시작일</Label>
            <Input
              type="date"
              value={periodFrom}
              max={periodTo}
              onChange={(e) => setPeriodFrom(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>종료일</Label>
            <Input
              type="date"
              value={periodTo}
              min={periodFrom}
              max={today}
              onChange={(e) => setPeriodTo(e.target.value)}
            />
          </div>
        </div>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="flex gap-3 pt-1">
          <Button className="flex-1" onClick={handleGenerate} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                생성 중...
              </>
            ) : (
              "생성하기"
            )}
          </Button>
          <Button variant="outline" className="flex-1" onClick={onClose} disabled={loading}>
            취소
          </Button>
        </div>
      </div>
    </div>
  );
}
