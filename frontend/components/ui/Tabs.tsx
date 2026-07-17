"use client";

import { cn } from "@/lib/utils";

interface Tab {
  label: string;
  value: string;
  count?: number;
}

interface TabsProps {
  tabs: Tab[];
  activeValue: string;
  onChange: (value: string) => void;
}

export function Tabs({ tabs, activeValue, onChange }: TabsProps) {
  return (
    <div className="flex items-center gap-1 border-b border-border overflow-x-auto">
      {tabs.map((tab) => {
        const isActive = tab.value === activeValue;
        return (
          <button
            key={tab.value}
            onClick={() => onChange(tab.value)}
            className={cn(
              "relative px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors focus-ring",
              isActive ? "text-brand" : "text-ink-muted hover:text-ink"
            )}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className="figure ml-1.5 text-xs text-ink-faint">({tab.count})</span>
            )}
            {isActive && <span className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-brand rounded-full" />}
          </button>
        );
      })}
    </div>
  );
}