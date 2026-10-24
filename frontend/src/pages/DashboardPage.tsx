import { useEffect, useState } from "react";

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
      {error && <p>{error}</p>}
      {insights && (
        <div>
          <p>Total books: {insights.total_books}</p>
          <ul>
            {Object.entries(insights.by_published_year).map(([year, count]) => (
              <li key={year}>
                {year}: {count}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
