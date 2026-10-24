import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../shared/EmptyState";
import { formatDate } from "../shared/format";
import {
  deleteReading,
  fetchBookReading,
  fetchMembers,
  Member,
  ReadingEntry,
  ReadingStatus,
  upsertReading,
} from "../services/api";
import { ProgressBar } from "./ProgressBar";
import { READING_STATUS_OPTIONS, StatusBadge } from "./StatusBadge";

type Props = {
  bookId: number;
  bookPages: number | null;
};

type FormState = {
  memberId: string;
  status: ReadingStatus;
  currentPage: string;
  startedOn: string;
  finishedOn: string;
  note: string;
};

const EMPTY_FORM: FormState = {
  memberId: "",
  status: "reading",
  currentPage: "",
  startedOn: "",
  finishedOn: "",
  note: "",
};

function fromEntry(entry: ReadingEntry): FormState {
  return {
    memberId: String(entry.member_id),
    status: entry.status,
    currentPage: entry.current_page != null ? String(entry.current_page) : "",
    startedOn: entry.started_on ?? "",
    finishedOn: entry.finished_on ?? "",
    note: entry.note ?? "",
  };
}

export function ReadingPanel({ bookId, bookPages }: Props) {
  const [members, setMembers] = useState<Member[]>([]);
  const [entries, setEntries] = useState<ReadingEntry[]>([]);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    const [memberList, entryList] = await Promise.all([
      fetchMembers(),
      fetchBookReading(bookId),
    ]);
    setMembers(memberList);
    setEntries(entryList);
  }, [bookId]);

  useEffect(() => {
    load()
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [load]);

  const selected = members.find((member) => String(member.id) === form.memberId);
  const existing = entries.find(
    (entry) => String(entry.member_id) === form.memberId,
  );

  function handleMemberChange(value: string) {
    setError(null);
    setMessage(null);
    const match = entries.find((entry) => String(entry.member_id) === value);
    setForm(match ? fromEntry(match) : { ...EMPTY_FORM, memberId: value });
  }

  function handleEdit(entry: ReadingEntry) {
    setError(null);
    setMessage(null);
    setForm(fromEntry(entry));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!form.memberId) {
      setError("Choose a member first.");
      return;
    }
    const page = form.currentPage.trim() === "" ? null : Number(form.currentPage);
    if (page !== null && !Number.isFinite(page)) {
      setError("Current page must be a number.");
      return;
    }

    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const saved = await upsertReading(bookId, Number(form.memberId), {
        status: form.status,
        current_page: page,
        started_on: form.startedOn || null,
        finished_on: form.finishedOn || null,
        note: form.note.trim() || null,
      });
      setForm(fromEntry(saved));
      setEntries(await fetchBookReading(bookId));
      setMessage("Reading entry saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  async function handleRemove(entry: ReadingEntry) {
    if (!confirm(`Remove ${entry.member_name}'s reading entry?`)) return;
    setError(null);
    setMessage(null);
    try {
      await deleteReading(bookId, entry.member_id);
      setEntries(await fetchBookReading(bookId));
      if (existing?.id === entry.id) {
        setForm({ ...EMPTY_FORM, memberId: String(entry.member_id) });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove");
    }
  }

  return (
    <section className="book-reading" aria-labelledby="reading-heading">
      <div className="panel-header">
        <h2 id="reading-heading">Reading</h2>
        <span className="muted tabular">
          {entries.length} {entries.length === 1 ? "reader" : "readers"}
        </span>
      </div>

      {loading ? (
        <p>Loading reading...</p>
      ) : members.length === 0 ? (
        <EmptyState title="No household members yet">
          Add members on the <Link to="/reading">Reading page</Link>, then
          record who is reading this book.
        </EmptyState>
      ) : (
        <>
          {entries.length > 0 && (
            <ul className="book-entry-list">
              {entries.map((entry) => (
                <li key={entry.id} className="book-entry">
                  <div className="book-entry-head">
                    <span className="member-name">{entry.member_name}</span>
                    <StatusBadge status={entry.status} />
                  </div>
                  <ProgressBar
                    current={entry.current_page}
                    total={entry.book_pages}
                    label={`${entry.member_name}'s progress in this book`}
                  />
                  {(entry.started_on || entry.finished_on) && (
                    <p className="entry-dates">
                      {entry.started_on && (
                        <span>Started {formatDate(entry.started_on)}</span>
                      )}
                      {entry.started_on && entry.finished_on && (
                        <span aria-hidden="true"> · </span>
                      )}
                      {entry.finished_on && (
                        <span>Finished {formatDate(entry.finished_on)}</span>
                      )}
                    </p>
                  )}
                  {entry.note && <p className="entry-note">{entry.note}</p>}
                  <div className="book-entry-actions">
                    <button type="button" onClick={() => handleEdit(entry)}>
                      Edit
                    </button>
                    <button type="button" onClick={() => handleRemove(entry)}>
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          <h3 className="form-heading">
            {existing && selected
              ? `Update ${selected.name}'s reading`
              : "Record reading"}
          </h3>
          <form className="reading-form" onSubmit={handleSave}>
            <div className="form-field">
              <label htmlFor="reading-member">Member</label>
              <select
                id="reading-member"
                value={form.memberId}
                onChange={(e) => handleMemberChange(e.target.value)}
              >
                <option value="">Choose a member</option>
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label htmlFor="reading-status">Status</label>
              <select
                id="reading-status"
                value={form.status}
                onChange={(e) =>
                  setForm({ ...form, status: e.target.value as ReadingStatus })
                }
              >
                {READING_STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label htmlFor="reading-page">
                Current page{bookPages ? ` (of ${bookPages})` : ""}
              </label>
              <input
                id="reading-page"
                type="number"
                min={0}
                max={bookPages ?? undefined}
                inputMode="numeric"
                value={form.currentPage}
                onChange={(e) =>
                  setForm({ ...form, currentPage: e.target.value })
                }
              />
            </div>
            <div className="form-field">
              <label htmlFor="reading-started">Started on</label>
              <input
                id="reading-started"
                type="date"
                value={form.startedOn}
                onChange={(e) =>
                  setForm({ ...form, startedOn: e.target.value })
                }
              />
            </div>
            <div className="form-field">
              <label htmlFor="reading-finished">Finished on</label>
              <input
                id="reading-finished"
                type="date"
                value={form.finishedOn}
                onChange={(e) =>
                  setForm({ ...form, finishedOn: e.target.value })
                }
              />
            </div>
            <div className="form-field form-field-wide">
              <label htmlFor="reading-note">Note</label>
              <textarea
                id="reading-note"
                rows={2}
                value={form.note}
                onChange={(e) => setForm({ ...form, note: e.target.value })}
              />
            </div>

            {error && (
              <p className="form-message" role="alert">
                {error}
              </p>
            )}
            {message && (
              <p className="form-message" role="status">
                {message}
              </p>
            )}

            <div className="form-actions">
              <button
                type="submit"
                className="primary"
                disabled={saving || !form.memberId}
              >
                {saving ? "Saving..." : "Save reading"}
              </button>
              {existing && (
                <button
                  type="button"
                  onClick={() =>
                    setForm({ ...EMPTY_FORM, memberId: form.memberId })
                  }
                  disabled={saving}
                >
                  Clear form
                </button>
              )}
            </div>
          </form>
        </>
      )}
    </section>
  );
}
