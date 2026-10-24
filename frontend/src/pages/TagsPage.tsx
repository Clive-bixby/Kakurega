import { useCallback, useEffect, useState } from "react";

import { EmptyState } from "../shared/EmptyState";
import { PageHeader } from "../shared/PageHeader";
import {
  createTaxonomy,
  deleteTag,
  fetchTags,
  renameTag,
  TagSummary,
} from "../services/api";

export function TagsPage() {
  const [tags, setTags] = useState<TagSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [newTag, setNewTag] = useState("");
  const [editing, setEditing] = useState<{ id: number; name: string } | null>(
    null,
  );

  const load = useCallback(async () => {
    setTags(await fetchTags(500));
  }, []);

  useEffect(() => {
    load()
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [load]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const name = newTag.trim();
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await createTaxonomy("tags", name);
      setNewTag("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create tag");
    } finally {
      setBusy(false);
    }
  }

  async function handleRename(event: React.FormEvent) {
    event.preventDefault();
    if (!editing) return;
    const name = editing.name.trim();
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await renameTag(editing.id, name);
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to rename tag");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(tag: TagSummary) {
    const detail =
      tag.book_count === 1
        ? "It will be removed from 1 book."
        : `It will be removed from ${tag.book_count} books.`;
    if (!confirm(`Delete the tag “${tag.name}”? ${detail}`)) return;

    setBusy(true);
    setError(null);
    try {
      await deleteTag(tag.id);
      if (editing?.id === tag.id) setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete tag");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Organise"
        title="Tags"
        description="Tags are shared across the household. Renaming a tag updates every book that uses it."
      />

      {error && (
        <p className="form-message" role="alert">
          {error}
        </p>
      )}

      <section className="panel" aria-labelledby="tag-list-heading">
        <div className="panel-header">
          <h2 id="tag-list-heading">All tags</h2>
          <span className="muted tabular">
            {tags.length} {tags.length === 1 ? "tag" : "tags"}
          </span>
        </div>

        {loading ? (
          <p className="muted">Loading tags...</p>
        ) : tags.length === 0 ? (
          <EmptyState title="No tags yet">
            Add tags here, or create them while editing a book.
          </EmptyState>
        ) : (
          <ul className="tag-grid">
            {tags.map((tag) => (
              <li key={tag.id} className="tag-card">
                {editing?.id === tag.id ? (
                  <form className="tag-edit" onSubmit={handleRename}>
                    <label className="sr-only" htmlFor="tag-name">
                      Tag name
                    </label>
                    <input
                      id="tag-name"
                      value={editing.name}
                      onChange={(event) =>
                        setEditing({ ...editing, name: event.target.value })
                      }
                      autoFocus
                      required
                    />
                    <button
                      type="submit"
                      className="primary"
                      disabled={busy || !editing.name.trim()}
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
                    <div className="tag-card-head">
                      <span className="tag-card-name">{tag.name}</span>
                      <span className="tag-count">
                        {tag.book_count}{" "}
                        {tag.book_count === 1 ? "book" : "books"}
                      </span>
                    </div>
                    <div className="tag-card-actions">
                      <button
                        type="button"
                        onClick={() =>
                          setEditing({ id: tag.id, name: tag.name })
                        }
                        disabled={busy}
                      >
                        Rename
                      </button>
                      <button
                        type="button"
                        className="ghost"
                        onClick={() => handleDelete(tag)}
                        disabled={busy}
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}

        <form className="tag-add" onSubmit={handleCreate}>
          <label htmlFor="new-tag">
            New tag
            <input
              id="new-tag"
              value={newTag}
              onChange={(event) => setNewTag(event.target.value)}
              placeholder="e.g. Signed"
              autoComplete="off"
            />
          </label>
          <button
            type="submit"
            className="primary"
            disabled={busy || !newTag.trim()}
          >
            Add tag
          </button>
        </form>
      </section>
    </div>
  );
}
