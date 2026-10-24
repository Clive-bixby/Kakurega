import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ProgressBar } from "../components/ProgressBar";
import { EmptyState } from "../shared/EmptyState";
import { PageHeader } from "../shared/PageHeader";
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
          <section className="panel" aria-labelledby="currently-reading-heading">
            <div className="panel-header">
              <h2 id="currently-reading-heading">Currently reading</h2>
              <span className="muted tabular">
                {insights.currently_reading.length}
              </span>
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

          <section className="panel" aria-labelledby="collection-heading">
            <div className="panel-header">
              <h2 id="collection-heading">Collection</h2>
            </div>
            <p>
              Total books: <span className="tabular">{insights.total_books}</span>
            </p>
            <ul>
              {Object.entries(insights.by_published_year).map(
                ([year, count]) => (
                  <li key={year}>
                    <span className="tabular">{year}</span>:{" "}
                    <span className="tabular">{count}</span>
                  </li>
                ),
              )}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}
