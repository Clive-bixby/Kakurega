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

  const decades = new Map<number, number>();
  for (const [year, count] of Object.entries(
    insights?.by_published_year ?? {},
  )) {
    const decade = Math.floor(Number(year) / 10) * 10;
    if (Number.isFinite(decade)) {
      decades.set(decade, (decades.get(decade) ?? 0) + count);
    }
  }
  const eras = [...decades.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([decade, count]) => ({ label: `${decade}s`, value: count }));

  return (
    <div>
      <div className="insights-hero">
        <PageHeader
          eyebrow="Insights"
          title="Your reading journey."
          description="A reflection of what the household has collected, across years, genres, authors, and languages."
        />
      </div>

      {loading && <p className="muted">Loading insights...</p>}
      {error && <p role="alert">{error}</p>}

      {insights && (
        <>
          <div className="milestone-grid">
            <div className="milestone">
              <span className="milestone-value tabular">
                {insights.total_books}
              </span>
              <p className="milestone-label">Books catalogued</p>
              <p className="milestone-note">
                {years.length > 0
                  ? `${years.length} publication ${
                      years.length === 1 ? "year" : "years"
                    } represented`
                  : "Add publication years to chart the eras"}
              </p>
            </div>
            <div className="milestone">
              <span className="milestone-value tabular">
                {insights.currently_reading.length}
              </span>
              <p className="milestone-label">Reading now</p>
              <p className="milestone-note">
                {insights.total_members}{" "}
                {insights.total_members === 1 ? "member" : "members"} in the
                household
              </p>
            </div>
            <div className="milestone">
              <span className="milestone-value tabular">
                {insights.by_author.length}
              </span>
              <p className="milestone-label">Authors on the shelf</p>
              <p className="milestone-note">
                {insights.by_author[0]
                  ? `Most collected: ${insights.by_author[0].name}`
                  : "Add authors to see them here"}
              </p>
            </div>
          </div>

          <div className="insights-grid">
            <section className="panel" aria-labelledby="genres-heading">
              <div className="panel-header">
                <h2 id="genres-heading">Themes &amp; genres</h2>
                <span className="muted tabular">
                  {insights.by_genre.length}{" "}
                  {insights.by_genre.length === 1 ? "genre" : "genres"}
                </span>
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
                <h2 id="authors-heading">Most collected authors</h2>
                <span className="muted tabular">
                  {insights.by_author.length} total
                </span>
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

            <section className="panel" aria-labelledby="eras-heading">
              <div className="panel-header">
                <h2 id="eras-heading">Publication eras</h2>
                <span className="muted tabular">
                  {eras.length} {eras.length === 1 ? "decade" : "decades"}
                </span>
              </div>
              <BarList
                items={eras}
                label="Books by publication decade"
                emptyText="No publication years recorded yet."
              />
            </section>

            <section className="panel" aria-labelledby="languages-heading">
              <div className="panel-header">
                <h2 id="languages-heading">Languages</h2>
                <span className="muted tabular">
                  {Object.keys(insights.by_language).length}{" "}
                  {Object.keys(insights.by_language).length === 1
                    ? "language"
                    : "languages"}
                </span>
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
        </>
      )}
    </div>
  );
}
