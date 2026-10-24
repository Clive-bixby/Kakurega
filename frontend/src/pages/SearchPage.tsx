import { useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";
import { BookListItem, searchBooks } from "../services/api";

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<BookListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const page = await searchBooks(query.trim());
      setResults(page.items);
      setTotal(page.total);
      setSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader title="Search" />
      <form onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search title, author, ISBN..."
          aria-label="Search books"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      {searched && results.length === 0 && <p>No results</p>}
      {searched && results.length > 0 && <p>{total} results</p>}
      <ul>
        {results.map((book) => (
          <li key={book.id}>
            <Link to={`/library/${book.id}`}>{book.title}</Link>
            {book.published_year ? ` (${book.published_year})` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
