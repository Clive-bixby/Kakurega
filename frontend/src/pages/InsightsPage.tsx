import { useEffect, useState } from "react";

import { BarList } from "../shared/BarList";
import { PageHeader } from "../shared/PageHeader";
import { Insights, fetchInsights } from "../services/api";

export function InsightsPage() {
  const [insights, setInsights] = useState<Insights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInsights()
      .then(setInsights)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const years = insights
    ? Object.entries(insights.by_published_year)
        .map(([year, count]) => ({ label: year, value: count }))
        .sort((a, b) => Number(a.label) - Number(b.label))
    : [];

  return (
    <div>
      <PageHeader title="Insights" />
      <p className="page-intro">
        What the household has collected, across years, genres, authors, and
        languages.
      </p>

      {loading && <p>Loading insights...</p>}
      {error && <p role="alert">{error}</p>}

      {insights && (
        <div className="insights-grid">
          <section className="panel" aria-labelledby="years-heading">
            <div className="panel-header">
              <h2 id="years-heading">By publication year</h2>
              <span className="muted tabular">{insights.total_books} books</span>
            </div>
            <BarList
              items={years}
              label="Books by publication year"
              emptyText="No publication years recorded yet."
            />
          </section>

          <section className="panel" aria-labelledby="genres-heading">
            <div className="panel-header">
              <h2 id="genres-heading">Top genres</h2>
            </div>
            <BarList
              items={insights.by_genre.map((item) => ({
                label: item.name,
                value: item.count,
              }))}
              label="Books by genre, top ten"
              emptyText="No genres recorded yet."
            />
          </section>

          <section className="panel" aria-labelledby="authors-heading">
            <div className="panel-header">
              <h2 id="authors-heading">Top authors</h2>
            </div>
            <BarList
              items={insights.by_author.map((item) => ({
                label: item.name,
                value: item.count,
              }))}
              label="Books by author, top ten"
              emptyText="No authors recorded yet."
            />
          </section>

          <section className="panel" aria-labelledby="languages-heading">
            <div className="panel-header">
              <h2 id="languages-heading">Languages</h2>
            </div>
            <BarList
              items={Object.entries(insights.by_language)
                .map(([language, count]) => ({ label: language, value: count }))
                .sort((a, b) => b.value - a.value)}
              label="Books by language"
              emptyText="No languages recorded yet."
            />
          </section>
        </div>
      )}
    </div>
  );
}
