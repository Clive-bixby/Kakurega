import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ProgressBar } from "../components/ProgressBar";
import { EmptyState } from "../shared/EmptyState";
import { PageHeader } from "../shared/PageHeader";
import { formatDate } from "../shared/format";
import { Insights, fetchInsights } from "../services/api";

export function DashboardPage() {
  const [insights, setInsights] = useState<Insights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInsights()
      .then(setInsights)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader title="Dashboard" />
      {loading && <p>Loading...</p>}
      {error && <p role="alert">{error}</p>}
      {insights && (
        <>
          <div className="stat-grid">
            <div className="stat-card">
              <span className="stat-label">Books</span>
              <span className="stat-value tabular">{insights.total_books}</span>
              <Link to="/library" className="text-link">
                Browse library
              </Link>
            </div>
            <div className="stat-card">
              <span className="stat-label">Household members</span>
              <span className="stat-value tabular">{insights.total_members}</span>
              <Link to="/reading" className="text-link">
                Reading activity
              </Link>
            </div>
            <div className="stat-card">
              <span className="stat-label">In progress</span>
              <span className="stat-value tabular">
                {insights.currently_reading.length}
              </span>
              <Link to="/reading" className="text-link">
                Who is reading what
              </Link>
            </div>
          </div>

          <section className="panel" aria-labelledby="currently-reading-heading">
            <div className="panel-header">
              <h2 id="currently-reading-heading">Currently reading</h2>
            </div>

            {insights.currently_reading.length === 0 ? (
              <EmptyState title="Nothing in progress">
                Open a book and record who is reading it to see it here.
              </EmptyState>
            ) : (
              <ul className="entry-list">
                {insights.currently_reading.map((item) => (
                  <li
                    key={`${item.book_id}-${item.member_id}`}
                    className="entry-card"
                  >
                    <div className="entry-heading">
                      <Link
                        to={`/library/${item.book_id}`}
                        className="entry-title"
                      >
                        {item.book_title}
                      </Link>
                      <span className="muted">{item.member_name}</span>
                    </div>
                    <ProgressBar
                      current={item.current_page}
                      total={item.pages}
                      label={`${item.member_name}'s progress in ${item.book_title}`}
                    />
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="panel" aria-labelledby="recently-added-heading">
            <div className="panel-header">
              <h2 id="recently-added-heading">Recently added</h2>
              <Link to="/library" className="text-link">
                View all
              </Link>
            </div>

            {insights.recently_added.length === 0 ? (
              <EmptyState title="No books yet">
                Add a book by ISBN or <Link to="/import">import a shelf</Link>.
              </EmptyState>
            ) : (
              <ul className="recent-list">
                {insights.recently_added.map((book) => (
                  <li key={book.book_id} className="recent-item">
                    {book.cover_url ? (
                      <img
                        className="recent-cover"
                        src={book.cover_url}
                        alt=""
                        loading="lazy"
                      />
                    ) : (
                      <div className="recent-cover recent-cover-empty" aria-hidden="true" />
                    )}
                    <div>
                      <Link
                        to={`/library/${book.book_id}`}
                        className="book-list-title"
                      >
                        {book.title}
                      </Link>
                      <p className="book-list-meta">
                        Added {formatDate(book.created_at)}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
