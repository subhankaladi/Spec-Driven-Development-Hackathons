"use client";

import { cn } from "@/lib/utils";

interface TaskFilterProps {
  currentFilter: boolean | null;
  onFilterChange: (filter: boolean | null) => void;
}

const filters = [
  { label: "All", value: null },
  { label: "Active", value: false },
  { label: "Completed", value: true },
] as const;

export function TaskFilter({ currentFilter, onFilterChange }: TaskFilterProps) {
  return (
    <div className="flex gap-2 mb-6">
      {filters.map((filter) => (
        <button
          key={String(filter.value)}
          onClick={() => onFilterChange(filter.value)}
          className={cn(
            "px-3 py-1.5 text-sm font-medium rounded-lg transition-colors",
            currentFilter === filter.value
              ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
              : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
          )}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
