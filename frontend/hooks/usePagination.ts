"use client";

import { useMemo, useState } from "react";

interface UsePaginationOptions {
  pageSize?: number;
}

/** Simple client-side pagination over an in-memory array (customer's own
 * history is small enough not to need server-side paging, unlike the
 * officer queue in Milestone 4 which paginates via the API). */
export function usePagination<T>(items: T[], { pageSize = 10 }: UsePaginationOptions = {}) {
  const [page, setPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const safePage = Math.min(page, totalPages);

  const pageItems = useMemo(() => {
    const start = (safePage - 1) * pageSize;
    return items.slice(start, start + pageSize);
  }, [items, safePage, pageSize]);

  return {
    page: safePage,
    totalPages,
    pageItems,
    setPage,
    nextPage: () => setPage((p) => Math.min(p + 1, totalPages)),
    prevPage: () => setPage((p) => Math.max(p - 1, 1)),
  };
}