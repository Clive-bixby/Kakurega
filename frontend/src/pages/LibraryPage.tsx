import { useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";
import { useBooks } from "../hooks/useBooks";

const PAGE_SIZE = 25;

export function LibraryPage() {
  const [offset, setOffset] = useState(0);
  const { books, total, loading, error } = useBooks({ limit: PAGE_SIZE, offset });

  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);
  const canGoBack = offset > 0;
  const canGoForward = offset + PAGE_SIZE < total;

  return (
    <div>
      <PageHeader title="Library" />
      {loading && <p>Loading...</p>}
      {error && <p role="alert">{error}</p>}
      <p>
        {from}–{to} of {total}
      </p>
      <ul>
        {books.map((book) => (
          <li key={book.id}>
            <Link to={`/library/${book.id}`}>{book.title}</Link>
            {book.published_year ? ` (${book.published_year})` : ""}
          </li>
        ))}
      </ul>
      <div>
        <button
          type="button"
          disabled={!canGoBack || loading}
          onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
        >
          Previous
        </button>
        <button
          type="button"
          disabled={!canGoForward || loading}
          onClick={() => setOffset(offset + PAGE_SIZE)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
