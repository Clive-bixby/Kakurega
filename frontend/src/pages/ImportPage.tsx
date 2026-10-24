import { useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";
import { ImportResult, importCsv } from "../services/api";

export function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [updateExisting, setUpdateExisting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setImporting(true);
    setError(null);
    setResult(null);
    try {
      setResult(await importCsv(file, updateExisting));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(false);
    }
  }

  return (
    <div>
      <PageHeader title="Import" />
      <p>
        Upload a CSV with a header row. Goodreads exports and Kakurega column
        names are both accepted. Importing never contacts an external metadata
        service.
      </p>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          aria-label="CSV file"
        />
        <label>
          <input
            type="checkbox"
            checked={updateExisting}
            onChange={(e) => setUpdateExisting(e.target.checked)}
          />{" "}
          Fill blanks on books that already exist
        </label>
        <button type="submit" disabled={!file || importing}>
          {importing ? "Importing..." : "Import"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {result && (
        <section aria-label="Import results">
          <h2>Import results</h2>
          <ul>
            <li>Created: {result.created}</li>
            <li>Updated: {result.updated}</li>
            <li>Skipped duplicates: {result.skipped_duplicates}</li>
            <li>Failed: {result.failed.length}</li>
            <li>Warnings: {result.warnings.length}</li>
          </ul>

          {result.failed.length > 0 && (
            <>
              <h3>Failed rows</h3>
              <ul>
                {result.failed.map((problem, index) => (
                  <li key={`failed-${problem.row}-${index}`}>
                    Row {problem.row}: {problem.reason}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.warnings.length > 0 && (
            <>
              <h3>Warnings</h3>
              <ul>
                {result.warnings.map((problem, index) => (
                  <li key={`warning-${problem.row}-${index}`}>
                    Row {problem.row}: {problem.reason}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.ignored_columns.length > 0 && (
            <p>Ignored columns: {result.ignored_columns.join(", ")}</p>
          )}

          <p>
            <Link to="/library">Open the library</Link>
          </p>
        </section>
      )}
    </div>
  );
}
