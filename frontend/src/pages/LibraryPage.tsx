import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { READING_STATUS_OPTIONS } from "../components/StatusBadge";
import { PageHeader } from "../shared/PageHeader";
import { EmptyState } from "../shared/EmptyState";
import { useBooks } from "../hooks/useBooks";
import { fetchMembers, Member, ReadingStatus } from "../services/api";

const PAGE_SIZE = 25;

export function LibraryPage() {
  const [offset, setOffset] = useState(0);
  const [members, setMembers] = useState<Member[]>([]);
  const [memberFilter, setMemberFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const { books, total, loading, error } = useBooks({
    limit: PAGE_SIZE,
    offset,
    member_id: memberFilter ? Number(memberFilter) : undefined,
    status: statusFilter ? (statusFilter as ReadingStatus) : undefined,
  });

  useEffect(() => {
    fetchMembers()
      .then(setMembers)
      .catch(() => setMembers([]));
  }, []);

  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);
  const canGoBack = offset > 0;
  const canGoForward = offset + PAGE_SIZE < total;
  const filtered = memberFilter !== "" || statusFilter !== "";

  function changeFilter(setter: (value: string) => void) {
    return (event: React.ChangeEvent<HTMLSelectElement>) => {
      setter(event.target.value);
      setOffset(0);
    };
  }

  return (
    <div>
      <PageHeader title="Library" />

      <div className="filters" role="group" aria-label="Library filters">
        <label>
          Member
          <select value={memberFilter} onChange={changeFilter(setMemberFilter)}>
            <option value="">Everyone</option>
            {members.map((member) => (
              <option key={member.id} value={member.id}>
                {member.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Reading status
          <select value={statusFilter} onChange={changeFilter(setStatusFilter)}>
            <option value="">Any status</option>
            {READING_STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p className="muted tabular">
        {from}–{to} of {total}
      </p>

      {loading && <p>Loading...</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && !error && books.length === 0 && (
        <EmptyState
          title={filtered ? "No books match these filters" : "Your library is empty"}
        >
          {filtered ? (
            "Clear the member or status filter to see every book."
          ) : (
            <>
              Add a book by ISBN or <Link to="/import">import a shelf</Link>.
            </>
          )}
        </EmptyState>
      )}

      <ul className="book-list">
        {books.map((book) => (
          <li key={book.id} className="book-list-item">
            <Link to={`/library/${book.id}`}>{book.title}</Link>
            {book.published_year ? (
              <span className="muted"> ({book.published_year})</span>
            ) : null}
          </li>
        ))}
      </ul>

      <div className="pager">
        <button
          type="button"
          disabled={!canGoBack || loading}
          onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
        >
          Previous
        </button>
        <button
          type="button"
          disabled={!canGoForward || loading}
          onClick={() => setOffset(offset + PAGE_SIZE)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
