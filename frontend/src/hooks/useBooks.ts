import { useEffect, useState } from "react";

import { BookListParams, BookPage, fetchBooks } from "../services/api";

export function useBooks(params: BookListParams = {}) {
  const [page, setPage] = useState<BookPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { q, genre_id, year_from, year_to, member_id, status, sort, limit, offset } =
    params;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchBooks({
      q,
      genre_id,
      year_from,
      year_to,
      member_id,
      status,
      sort,
      limit,
      offset,
    })
      .then((data) => {
        if (!cancelled) setPage(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [q, genre_id, year_from, year_to, member_id, status, sort, limit, offset]);

  return { page, books: page?.items ?? [], total: page?.total ?? 0, loading, error };
}
