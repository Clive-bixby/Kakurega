import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ProgressBar } from "../components/ProgressBar";
import { READING_STATUS_OPTIONS, StatusBadge } from "../components/StatusBadge";
import { EmptyState } from "../shared/EmptyState";
import { PageHeader } from "../shared/PageHeader";
import { formatDate } from "../shared/format";
import {
  createMember,
  deleteMember,
  fetchMembers,
  fetchReading,
  Member,
  ReadingEntry,
  ReadingStatus,
  updateMember,
} from "../services/api";

export function ReadingPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [entries, setEntries] = useState<ReadingEntry[]>([]);
  const [memberFilter, setMemberFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loadingMembers, setLoadingMembers] = useState(true);
  const [loadingEntries, setLoadingEntries] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newMember, setNewMember] = useState("");
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState<{ id: number; name: string } | null>(
    null,
  );

  const loadMembers = useCallback(async () => {
    const list = await fetchMembers();
    setMembers(list);
    return list;
  }, []);

  const loadEntries = useCallback(async () => {
    const list = await fetchReading({
      member_id: memberFilter ? Number(memberFilter) : undefined,
      status: statusFilter ? (statusFilter as ReadingStatus) : undefined,
    });
    setEntries(list);
    return list;
  }, [memberFilter, statusFilter]);

  useEffect(() => {
    loadMembers()
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoadingMembers(false));
  }, [loadMembers]);

  useEffect(() => {
    setLoadingEntries(true);
    loadEntries()
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoadingEntries(false));
  }, [loadEntries]);

  async function handleAddMember(e: React.FormEvent) {
    e.preventDefault();
    const name = newMember.trim();
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await createMember(name);
      setNewMember("");
      await loadMembers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add member");
    } finally {
      setBusy(false);
    }
  }

  async function handleRename(e: React.FormEvent) {
    e.preventDefault();
    if (!editing) return;
    const name = editing.name.trim();
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await updateMember(editing.id, name);
      setEditing(null);
      await loadMembers();
      await loadEntries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to rename member");
    } finally {
      setBusy(false);
    }
  }

  async function handleRemoveMember(member: Member) {
    if (
      !confirm(
        `Remove ${member.name}? Their reading entries will be deleted too.`,
      )
    ) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await deleteMember(member.id);
      if (editing?.id === member.id) setEditing(null);
      if (memberFilter === String(member.id)) setMemberFilter("");
      await loadMembers();
      await loadEntries();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove member");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Household"
        title="Reading"
        description="Who is reading what, and how far along they are. Entries are recorded from each book's page."
      />

      {error && (
        <p className="form-message" role="alert">
          {error}
        </p>
      )}

      <div className="split-layout">
        <section className="panel" aria-labelledby="members-heading">
          <div className="panel-header">
            <h2 id="members-heading">Members</h2>
            <span className="muted tabular">{members.length}</span>
          </div>

          {loadingMembers ? (
            <p className="muted">Loading members...</p>
          ) : (
            <>
              {members.length === 0 ? (
                <EmptyState title="No members yet">
                  Add the people whose reading you want to track.
                </EmptyState>
              ) : (
                <ul className="member-list">
                  {members.map((member) => (
                    <li key={member.id} className="member-row">
                      {editing?.id === member.id ? (
                        <form className="member-edit" onSubmit={handleRename}>
                          <label className="sr-only" htmlFor="member-name">
                            Member name
                          </label>
                          <input
                            id="member-name"
                            value={editing.name}
                            onChange={(e) =>
                              setEditing({ ...editing, name: e.target.value })
                            }
                            autoFocus
                            required
                          />
                          <button
                            type="submit"
                            className="primary"
                            disabled={busy}
                          >
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditing(null)}
                            disabled={busy}
                          >
                            Cancel
                          </button>
                        </form>
                      ) : (
                        <>
                          <span className="member-name">{member.name}</span>
                          <div className="member-actions">
                            <button
                              type="button"
                              onClick={() =>
                                setEditing({ id: member.id, name: member.name })
                              }
                              disabled={busy}
                            >
                              Rename
                            </button>
                            <button
                              type="button"
                              onClick={() => handleRemoveMember(member)}
                              disabled={busy}
                            >
                              Remove
                            </button>
                          </div>
                        </>
                      )}
                    </li>
                  ))}
                </ul>
              )}

              <form className="member-add" onSubmit={handleAddMember}>
                <label htmlFor="new-member">Add a member</label>
                <div className="member-add-row">
                  <input
                    id="new-member"
                    value={newMember}
                    onChange={(e) => setNewMember(e.target.value)}
                    placeholder="e.g. Maya"
                    autoComplete="off"
                  />
                  <button
                    type="submit"
                    className="primary"
                    disabled={busy || !newMember.trim()}
                  >
                    Add member
                  </button>
                </div>
              </form>
            </>
          )}
        </section>

        <section className="panel" aria-labelledby="activity-heading">
          <div className="panel-header">
            <h2 id="activity-heading">Reading activity</h2>
            <span className="muted tabular">
              {entries.length} {entries.length === 1 ? "entry" : "entries"}
            </span>
          </div>

          <div className="filters" role="group" aria-label="Reading filters">
            <label>
              Member
              <select
                value={memberFilter}
                onChange={(e) => setMemberFilter(e.target.value)}
              >
                <option value="">Everyone</option>
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Status
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">All statuses</option>
                {READING_STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loadingEntries ? (
            <p className="muted">Loading reading activity...</p>
          ) : entries.length === 0 ? (
            <EmptyState title="No reading entries match">
              Open a book and record who is reading it, or clear the filters.
            </EmptyState>
          ) : (
            <ul className="entry-list">
              {entries.map((entry) => (
                <li key={entry.id} className="entry-card">
                  <div className="entry-heading">
                    <Link
                      to={`/library/${entry.book_id}`}
                      className="entry-title"
                    >
                      {entry.book_title}
                    </Link>
                    <StatusBadge status={entry.status} />
                  </div>
                  <p className="entry-meta">
                    {entry.member_name}
                    <span aria-hidden="true"> · </span>
                    updated {formatDate(entry.updated_at)}
                  </p>
                  <ProgressBar
                    current={entry.current_page}
                    total={entry.book_pages}
                    label={`${entry.member_name}'s progress in ${entry.book_title}`}
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
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
