import { Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { BookCover } from "../shared/BookCover";
import { EmptyState } from "../shared/EmptyState";
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
      <PageHeader
        eyebrow="Find anything"
        title="Search"
        description="Search across titles, authors, publishers, descriptions, and ISBNs."
      />

      <form className="search-bar" role="search" onSubmit={handleSubmit}>
        <Search size={18} aria-hidden="true" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search title, author, or ISBN..."
          aria-label="Search books"
        />
        <button type="submit" className="primary" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {searched && results.length === 0 && (
        <EmptyState title="No results">
          Nothing in the library matches “{query}”. Try a different title,
          author, or ISBN.
        </EmptyState>
      )}

      {searched && results.length > 0 && (
        <>
          <div className="section-head">
            <h2>
              {total} {total === 1 ? "result" : "results"} for “{query}”
            </h2>
            <Link to={`/library?q=${encodeURIComponent(query)}`} className="text-link">
              Open in library
            </Link>
          </div>
          <ul className="book-grid">
            {results.map((book) => (
              <li key={book.id} className="book-card">
                <Link to={`/library/${book.id}`} className="book-card-link">
                  <BookCover
                    title={book.title}
                    coverUrl={book.cover_url}
                    decorative
                  />
                  <div>
                    <h3 className="book-card-title">{book.title}</h3>
                    <p className="book-card-meta">
                      {book.author_names.length > 0
                        ? book.author_names.join(", ")
                        : "Unknown author"}
                      {book.published_year ? ` · ${book.published_year}` : ""}
                    </p>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
