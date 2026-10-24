import { ArrowRight, BookOpen, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ProgressBar } from "../components/ProgressBar";
import { BookCover } from "../shared/BookCover";
import { EmptyState } from "../shared/EmptyState";
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

  const current = insights?.currently_reading[0];
  const percent =
    current?.pages != null && current.pages > 0
      ? Math.min(
          100,
          Math.round(((current.current_page ?? 0) / current.pages) * 100),
        )
      : null;

  return (
    <div>
      <header className="welcome">
        <h1>Welcome back.</h1>
        <p>
          {current
            ? percent != null
              ? `You are ${percent}% through ${current.book_title}.`
              : `${current.member_name} is reading ${current.book_title}.`
            : "Your shelves are quiet. Pick up a book to begin."}
        </p>
      </header>

      {loading && <p className="muted">Loading your library...</p>}
      {error && <p role="alert">{error}</p>}

      {insights && (
        <>
          <section
            className={current ? "hero" : "hero hero-empty"}
            aria-labelledby="hero-heading"
          >
            {current && (
              <div className="hero-cover">
                <BookCover
                  title={current.book_title}
                  coverUrl={current.cover_url}
                  decorative
                />
              </div>
            )}
            <div className="hero-body">
              <span className="hero-eyebrow">
                <BookOpen size={13} aria-hidden="true" />
                {current ? "Currently reading" : "Start a book"}
              </span>

              {current ? (
                <>
                  <h2 id="hero-heading" className="hero-title">
                    <Link to={`/library/${current.book_id}`}>
                      {current.book_title}
                    </Link>
                  </h2>
                  <p className="hero-byline">
                    by {current.author_name ?? "Unknown author"}
                    <span aria-hidden="true"> · </span>
                    {current.member_name}
                  </p>
                  <div className="hero-progress">
                    <div className="hero-progress-line">
                      <span>
                        Page{" "}
                        <strong className="tabular">
                          {current.current_page ?? 0}
                        </strong>
                        {current.pages ? ` of ${current.pages}` : ""}
                      </span>
                      {percent != null && (
                        <span className="tabular">{percent}%</span>
                      )}
                    </div>
                    <ProgressBar
                      current={current.current_page}
                      total={current.pages}
                      label={`${current.member_name}'s progress in ${current.book_title}`}
                    />
                  </div>
                  <div className="hero-actions">
                    <Link
                      to={`/library/${current.book_id}`}
                      className="btn-primary"
                    >
                      Resume reading
                      <ArrowRight size={16} aria-hidden="true" />
                    </Link>
                    <Link to="/reading" className="text-link">
                      All reading activity
                    </Link>
                  </div>
                </>
              ) : (
                <>
                  <h2 id="hero-heading" className="hero-title">
                    Your next book is waiting.
                  </h2>
                  <p className="hero-byline">
                    Add a book to the library, then record who is reading it.
                  </p>
                  <div className="hero-actions">
                    <Link to="/add-book" className="btn-primary">
                      <Plus size={16} aria-hidden="true" />
                      Add a book
                    </Link>
                    <Link to="/library" className="text-link">
                      Browse library
                    </Link>
                  </div>
                </>
              )}
            </div>
          </section>

          <div className="stat-grid">
            <div className="stat-card">
              <span className="stat-label">In the library</span>
              <span className="stat-value tabular">
                {insights.total_books}
              </span>
              <Link to="/library" className="text-link">
                Browse library
                <ArrowRight size={14} aria-hidden="true" />
              </Link>
            </div>
            <div className="stat-card">
              <span className="stat-label">Reading now</span>
              <span className="stat-value tabular">
                {insights.currently_reading.length}
              </span>
              <Link to="/reading" className="text-link">
                Reading activity
                <ArrowRight size={14} aria-hidden="true" />
              </Link>
            </div>
            <div className="stat-card">
              <span className="stat-label">Household members</span>
              <span className="stat-value tabular">
                {insights.total_members}
              </span>
              <Link to="/reading" className="text-link">
                Manage members
                <ArrowRight size={14} aria-hidden="true" />
              </Link>
            </div>
          </div>

          <div className="section-head">
            <h2>Recently added</h2>
            <Link to="/library" className="text-link">
              View all
              <ArrowRight size={14} aria-hidden="true" />
            </Link>
          </div>

          {insights.recently_added.length === 0 ? (
            <EmptyState title="No books yet">
              Add a book by ISBN or <Link to="/import">import a shelf</Link>.
            </EmptyState>
          ) : (
            <ul className="recent-grid">
              {insights.recently_added.map((book) => (
                <li key={book.book_id} className="book-card">
                  <Link
                    to={`/library/${book.book_id}`}
                    className="book-card-link"
                  >
                    <BookCover
                      title={book.title}
                      coverUrl={book.cover_url}
                      decorative
                    />
                    <div>
                      <h3 className="book-card-title">{book.title}</h3>
                      <p className="book-card-meta">
                        {book.author_name ?? `Added ${formatDate(book.created_at)}`}
                      </p>
                    </div>
                  </Link>
                </li>
              ))}
              <li>
                <Link to="/library" className="browse-tile">
                  <BookOpen size={22} aria-hidden="true" />
                  <span>
                    Browse the
                    <br />
                    full library
                  </span>
                </Link>
              </li>
            </ul>
          )}

          <section className="panel" aria-labelledby="reading-now-heading">
            <div className="panel-header">
              <h2 id="reading-now-heading">Reading now</h2>
              <Link to="/reading" className="text-link">
                All activity
                <ArrowRight size={14} aria-hidden="true" />
              </Link>
            </div>

            {insights.currently_reading.length === 0 ? (
              <EmptyState title="Nothing in progress">
                Open a book and record who is reading it to see it here.
              </EmptyState>
            ) : (
              <ul className="reading-list">
                {insights.currently_reading.map((item) => (
                  <li
                    key={`${item.book_id}-${item.member_id}`}
                    className="reading-row"
                  >
                    <div className="reading-row-main">
                      <div className="reading-row-head">
                        <Link
                          to={`/library/${item.book_id}`}
                          className="reading-row-title"
                        >
                          {item.book_title}
                        </Link>
                        <span className="chip">{item.member_name}</span>
                      </div>
                      <ProgressBar
                        current={item.current_page}
                        total={item.pages}
                        label={`${item.member_name}'s progress in ${item.book_title}`}
                      />
                    </div>
                    <Link
                      to={`/library/${item.book_id}`}
                      className="text-link"
                    >
                      Open
                      <ArrowRight size={14} aria-hidden="true" />
                    </Link>
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
