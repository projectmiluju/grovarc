"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getRetrospective, updateRetrospective, publishRetrospective } from "@/lib/retrospective";
import { cn } from "@/lib/utils";
import type { Retrospective } from "@/types";

export default function RetrospectiveDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [retro, setRetro] = useState<Retrospective | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    getRetrospective(id).then((data) => {
      setRetro(data);
      setTitle(data.title);
      setContent(data.content);
    });
  }, [id]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateRetrospective(id, { title, content });
      setRetro(updated);
      setIsEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!confirm("회고를 발행할까요? 발행 후에는 수정이 제한됩니다.")) return;
    setPublishing(true);
    try {
      const updated = await publishRetrospective(id);
      setRetro(updated);
    } finally {
      setPublishing(false);
    }
  };

  if (!retro) return <div className="h-64 animate-pulse rounded-lg bg-muted" />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* 헤더 */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "rounded-full px-2.5 py-0.5 text-xs font-medium",
                retro.status === "PUBLISHED"
                  ? "bg-primary/10 text-primary"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {retro.status === "PUBLISHED" ? "발행됨" : "초안"}
            </span>
            <span className="text-sm text-muted-foreground">
              {format(new Date(retro.periodFrom), "M월 d일", { locale: ko })} ~{" "}
              {format(new Date(retro.periodTo), "M월 d일", { locale: ko })}
            </span>
          </div>
        </div>

        <div className="flex shrink-0 gap-2">
          {retro.status === "DRAFT" && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing((v) => !v)}
              >
                {isEditing ? "취소" : "수정"}
              </Button>
              <Button size="sm" onClick={handlePublish} disabled={publishing}>
                {publishing ? "발행 중..." : "발행"}
              </Button>
            </>
          )}
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            뒤로
          </Button>
        </div>
      </div>

      {/* 내용 */}
      {isEditing ? (
        <div className="space-y-4">
          <div className="space-y-1.5">
            <Label>제목</Label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>내용 (마크다운)</Label>
            <textarea
              rows={20}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "저장 중..." : "저장"}
          </Button>
        </div>
      ) : (
        <div className="rounded-lg border bg-card p-6">
          <h1 className="mb-6 text-2xl font-bold">{retro.title}</h1>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown>{retro.content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
