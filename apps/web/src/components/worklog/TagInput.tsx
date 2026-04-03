"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { getTags } from "@/lib/worklog";
import type { Tag } from "@/types";

interface TagInputProps {
  selected: Tag[];
  onChange: (tags: Tag[]) => void;
}

export function TagInput({ selected, onChange }: TagInputProps) {
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    getTags().then(setAllTags).catch(() => {});
  }, []);

  const filtered = allTags.filter(
    (t) =>
      t.name.toLowerCase().includes(query.toLowerCase()) &&
      !selected.some((s) => s.id === t.id),
  );

  const add = (tag: Tag) => {
    onChange([...selected, tag]);
    setQuery("");
    setOpen(false);
  };

  const remove = (id: string) => {
    onChange(selected.filter((t) => t.id !== id));
  };

  return (
    <div className="relative">
      <div className="flex min-h-10 flex-wrap items-center gap-1.5 rounded-md border border-input bg-background px-3 py-2">
        {selected.map((tag) => (
          <span
            key={tag.id}
            className="flex items-center gap-1 rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium"
          >
            {tag.name}
            <button type="button" onClick={() => remove(tag.id)}>
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <input
          className="flex-1 min-w-20 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          placeholder={selected.length === 0 ? "태그 검색..." : ""}
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
        />
      </div>

      {open && filtered.length > 0 && (
        <ul className="absolute z-10 mt-1 w-full rounded-md border bg-card shadow-md">
          {filtered.slice(0, 8).map((tag) => (
            <li key={tag.id}>
              <button
                type="button"
                className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
                onMouseDown={() => add(tag)}
              >
                {tag.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
