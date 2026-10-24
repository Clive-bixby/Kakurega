import { useState } from "react";
import { Link } from "react-router-dom";

import {
  ApiError,
  BookInput,
  createTaxonomy,
  uploadImage,
} from "../services/api";
import { SelectedOption, TaxonomyPicker } from "./TaxonomyPicker";

export type BookFormInitial = {
  title?: string;
  subtitle?: string | null;
  isbn10?: string | null;
  isbn13?: string | null;
  description?: string | null;
  notes?: string | null;
  pages?: number | null;
  language?: string | null;
  published_year?: number | null;
  cover_url?: string | null;
  publisher?: SelectedOption | null;
  authors?: SelectedOption[];
  genres?: SelectedOption[];
  tags?: SelectedOption[];
};

type Props = {
  initial?: BookFormInitial;
  submitLabel: string;
  onSubmit: (input: BookInput) => Promise<void>;
  onCancel?: () => void;
};

async function resolveIds(
  kind: "authors" | "genres" | "tags",
  options: SelectedOption[],
): Promise<number[]> {
  const ids: number[] = [];
  for (const option of options) {
    ids.push(option.id ?? (await createTaxonomy(kind, option.name)).id);
  }
  return ids;
}

function toNumber(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const number = Number(trimmed);
  return Number.isFinite(number) ? number : null;
}

export function BookForm({ initial, submitLabel, onSubmit, onCancel }: Props) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [subtitle, setSubtitle] = useState(initial?.subtitle ?? "");
  const [isbn10, setIsbn10] = useState(initial?.isbn10 ?? "");
  const [isbn13, setIsbn13] = useState(initial?.isbn13 ?? "");
  const [pages, setPages] = useState(
    initial?.pages != null ? String(initial.pages) : "",
  );
  const [language, setLanguage] = useState(initial?.language ?? "");
  const [year, setYear] = useState(
    initial?.published_year != null ? String(initial.published_year) : "",
  );
  const [description, setDescription] = useState(initial?.description ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [coverUrl, setCoverUrl] = useState(initial?.cover_url ?? "");
  const [publisher, setPublisher] = useState<SelectedOption[]>(
    initial?.publisher ? [initial.publisher] : [],
  );
  const [authors, setAuthors] = useState<SelectedOption[]>(
    initial?.authors ?? [],
  );
  const [genres, setGenres] = useState<SelectedOption[]>(initial?.genres ?? []);
  const [tags, setTags] = useState<SelectedOption[]>(initial?.tags ?? []);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [duplicateId, setDuplicateId] = useState<number | null>(null);

  async function handleCoverChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const uploaded = await uploadImage(file);
      setCoverUrl(uploaded.path);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setSaving(true);
    setError(null);
    setDuplicateId(null);
    try {
      const [authorIds, genreIds, tagIds] = await Promise.all([
        resolveIds("authors", authors),
        resolveIds("genres", genres),
        resolveIds("tags", tags),
      ]);
      const publisherId = publisher[0]
        ? (publisher[0].id ??
          (await createTaxonomy("publishers", publisher[0].name)).id)
        : null;

      await onSubmit({
        title: title.trim(),
        subtitle: subtitle.trim() || null,
        isbn10: isbn10.trim() || null,
        isbn13: isbn13.trim() || null,
        description: description.trim() || null,
        notes: notes.trim() || null,
        pages: toNumber(pages),
        language: language.trim() || null,
        published_year: toNumber(year),
        cover_url: coverUrl.trim() || null,
        publisher_id: publisherId,
        author_ids: authorIds,
        genre_ids: genreIds,
        tag_ids: tagIds,
      });
    } catch (err) {
      if (err instanceof ApiError && err.bookId) {
        setDuplicateId(err.bookId);
      }
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="book-form" onSubmit={handleSubmit}>
      <label className="form-field">
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label className="form-field">
        Subtitle
        <input value={subtitle} onChange={(e) => setSubtitle(e.target.value)} />
      </label>
      <label className="form-field">
        ISBN-10
        <input value={isbn10} onChange={(e) => setIsbn10(e.target.value)} />
      </label>
      <label className="form-field">
        ISBN-13
        <input value={isbn13} onChange={(e) => setIsbn13(e.target.value)} />
      </label>

      <div className="form-field">
        <TaxonomyPicker
          label="Authors"
          kind="authors"
          selected={authors}
          onChange={setAuthors}
        />
      </div>
      <div className="form-field">
        <TaxonomyPicker
          label="Publisher"
          kind="publishers"
          selected={publisher}
          onChange={setPublisher}
          multiple={false}
        />
      </div>
      <div className="form-field">
        <TaxonomyPicker
          label="Genres"
          kind="genres"
          selected={genres}
          onChange={setGenres}
        />
      </div>
      <div className="form-field">
        <TaxonomyPicker
          label="Tags"
          kind="tags"
          selected={tags}
          onChange={setTags}
        />
      </div>

      <label className="form-field">
        Pages
        <input
          type="number"
          min={1}
          value={pages}
          onChange={(e) => setPages(e.target.value)}
        />
      </label>
      <label className="form-field">
        Published year
        <input
          type="number"
          min={1000}
          value={year}
          onChange={(e) => setYear(e.target.value)}
        />
      </label>
      <label className="form-field">
        Language
        <input value={language} onChange={(e) => setLanguage(e.target.value)} />
      </label>
      <label className="form-field">
        Cover URL
        <input value={coverUrl} onChange={(e) => setCoverUrl(e.target.value)} />
      </label>

      <div className="form-field form-field-wide">
        <span className="field-label">Cover image</span>
        <div className="cover-row">
          {coverUrl ? (
            <img className="cover-preview" src={coverUrl} alt="Cover preview" />
          ) : (
            <div className="cover-preview cover-preview-empty" aria-hidden="true">
              No cover
            </div>
          )}
          <div className="cover-actions">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleCoverChange}
              aria-label="Upload cover image"
            />
            {uploading && <span>Uploading cover...</span>}
            {coverUrl && (
              <button type="button" onClick={() => setCoverUrl("")}>
                Remove cover
              </button>
            )}
          </div>
        </div>
      </div>

      <label className="form-field form-field-wide">
        Description
        <textarea
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </label>
      <label className="form-field form-field-wide">
        Notes
        <textarea
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </label>

      {duplicateId && (
        <p className="form-message" role="alert">
          A book with this ISBN already exists.{" "}
          <Link to={`/library/${duplicateId}`}>Open the existing book</Link>.
        </p>
      )}
      {error && (
        <p className="form-message" role="alert">
          {error}
        </p>
      )}

      <div className="form-actions">
        <button type="submit" className="primary" disabled={saving || uploading}>
          {saving ? "Saving..." : submitLabel}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} disabled={saving}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
