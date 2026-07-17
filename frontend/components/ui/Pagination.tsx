"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
  onPageSelect?: (page: number) => void;
}

export function Pagination({ page, totalPages, onPrev, onNext, onPageSelect }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1).filter(
    (p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1
  );

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-border">
      <p className="text-xs text-ink-muted">
        Page <span className="figure">{page}</span> of <span className="figure">{totalPages}</span>
      </p>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm" onClick={onPrev} disabled={page === 1} aria-label="Previous page">
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {onPageSelect &&
          pages.map((p, i) => (
            <span key={p} className="flex items-center">
              {i > 0 && pages[i - 1] !== p - 1 && <span className="px-1 text-ink-faint text-xs">…</span>}
              <button
                onClick={() => onPageSelect(p)}
                className={`figure h-8 w-8 rounded text-xs font-medium transition-colors focus-ring ${
                  p === page ? "bg-brand text-white" : "text-ink-muted hover:bg-surface-inset"
                }`}
                aria-current={p === page ? "page" : undefined}
              >
                {p}
              </button>
            </span>
          ))}
        <Button variant="ghost" size="sm" onClick={onNext} disabled={page === totalPages} aria-label="Next page">
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}