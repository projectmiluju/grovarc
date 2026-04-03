"use client";

import { cn } from "@/lib/utils";
import type { Mood } from "@/types";

const MOODS: { value: Mood; emoji: string; label: string }[] = [
  { value: "GREAT", emoji: "🚀", label: "최고" },
  { value: "GOOD", emoji: "😊", label: "좋음" },
  { value: "NEUTRAL", emoji: "😐", label: "보통" },
  { value: "BAD", emoji: "😔", label: "나쁨" },
  { value: "TERRIBLE", emoji: "😩", label: "최악" },
];

interface MoodSelectorProps {
  value?: Mood;
  onChange: (mood: Mood) => void;
}

export function MoodSelector({ value, onChange }: MoodSelectorProps) {
  return (
    <div className="flex gap-2">
      {MOODS.map((m) => (
        <button
          key={m.value}
          type="button"
          onClick={() => onChange(m.value)}
          title={m.label}
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-full text-xl transition-all",
            value === m.value
              ? "ring-2 ring-primary ring-offset-2 scale-110"
              : "opacity-50 hover:opacity-100",
          )}
        >
          {m.emoji}
        </button>
      ))}
    </div>
  );
}
