import { Upload } from "lucide-react";
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
      <PageHeader
        eyebrow="Bring your shelf"
        title="Import"
        description="Upload a CSV with a header row. Goodreads exports and Kakurega column names are both accepted. Importing never contacts an external metadata service."
      />

      {error && (
        <p className="form-message" role="alert">
          {error}
        </p>
      )}

      <section className="panel" aria-labelledby="upload-heading">
        <div className="panel-header">
          <h2 id="upload-heading">Upload a file</h2>
          <span className="muted">.csv</span>
        </div>

        <form onSubmit={handleSubmit}>
          <label className="dropzone">
            <Upload size={22} aria-hidden="true" />
            <strong>
              {file ? file.name : "Choose a CSV file to import"}
            </strong>
            <span>
              {file
                ? `${Math.max(1, Math.round(file.size / 1024))} KB · ready to import`
                : "Click to browse. Columns are matched automatically."}
            </span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              aria-label="CSV file"
            />
          </label>

          <div className="import-options">
            <label>
              <input
                type="checkbox"
                checked={updateExisting}
                onChange={(e) => setUpdateExisting(e.target.checked)}
              />{" "}
              Fill blanks on books that already exist
            </label>
            <button
              type="submit"
              className="primary"
              disabled={!file || importing}
            >
              {importing ? "Importing..." : "Import CSV"}
            </button>
          </div>
        </form>
      </section>

      {result && (
        <section className="panel" aria-label="Import results">
          <div className="panel-header">
            <h2>Import results</h2>
            <Link to="/library" className="text-link">
              Open the library
            </Link>
          </div>

          <div className="result-grid">
            <div className="result-card">
              <span className="stat-value tabular">{result.created}</span>
              <span className="stat-label">Created</span>
            </div>
            <div className="result-card">
              <span className="stat-value tabular">{result.updated}</span>
              <span className="stat-label">Updated</span>
            </div>
            <div className="result-card">
              <span className="stat-value tabular">
                {result.skipped_duplicates}
              </span>
              <span className="stat-label">Duplicates skipped</span>
            </div>
            <div className="result-card">
              <span className="stat-value tabular">
                {result.failed.length}
              </span>
              <span className="stat-label">Failed rows</span>
            </div>
            <div className="result-card">
              <span className="stat-value tabular">
                {result.warnings.length}
              </span>
              <span className="stat-label">Warnings</span>
            </div>
          </div>

          {result.failed.length > 0 && (
            <>
              <h3 className="form-heading">Failed rows</h3>
              <ul className="problem-list">
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
              <h3 className="form-heading">Warnings</h3>
              <ul className="problem-list">
                {result.warnings.map((problem, index) => (
                  <li key={`warning-${problem.row}-${index}`}>
                    Row {problem.row}: {problem.reason}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.ignored_columns.length > 0 && (
            <p className="muted">
              Ignored columns: {result.ignored_columns.join(", ")}
            </p>
          )}
        </section>
      )}
    </div>
  );
}
