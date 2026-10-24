import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { BookForm, BookFormInitial } from "../components/BookForm";
import { ReadingPanel } from "../components/ReadingPanel";
import { BookCover } from "../shared/BookCover";
import { PageHeader } from "../shared/PageHeader";
import { formatDate } from "../shared/format";
import { Book, BookInput, deleteBook, fetchBook, updateBook } from "../services/api";

function initialFromBook(book: Book): BookFormInitial {
  return {
    title: book.title,
    subtitle: book.subtitle,
    isbn10: book.isbn10,
    isbn13: book.isbn13,
    description: book.description,
    notes: book.notes,
    pages: book.pages,
    language: book.language,
    published_year: book.published_year,
    cover_url: book.cover_url,
    publisher: book.publisher
      ? { id: book.publisher.id, name: book.publisher.name }
      : null,
    authors: book.authors.map((author) => ({ id: author.id, name: author.name })),
    genres: book.genres.map((genre) => ({ id: genre.id, name: genre.name })),
    tags: book.tags.map((tag) => ({ id: tag.id, name: tag.name })),
  };
}

export function BookDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetchBook(Number(id))
      .then((loaded) => setBook(loaded))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSave(input: BookInput) {
    if (!book) return;
    const updated = await updateBook(book.id, input);
    setBook(updated);
    setEditing(false);
    setError(null);
  }

  async function handleDelete() {
    if (!book || !confirm(`Delete “${book.title}”?`)) return;
    try {
      await deleteBook(book.id);
      navigate("/library");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    }
  }

  if (loading) {
    return (
      <div>
        <Link to="/library" className="detail-back">
          <ArrowLeft size={16} aria-hidden="true" />
          Library
        </Link>
        <p className="muted">Loading book...</p>
      </div>
    );
  }

  if (!book) {
    return (
      <div>
        <Link to="/library" className="detail-back">
          <ArrowLeft size={16} aria-hidden="true" />
          Library
        </Link>
        <PageHeader title="Book not found" />
        <p role="alert">{error ?? "This book is no longer in your library."}</p>
      </div>
    );
  }

  if (editing) {
    return (
      <div>
        <Link to={`/library/${book.id}`} className="detail-back">
          <ArrowLeft size={16} aria-hidden="true" />
          Back to book
        </Link>
        <PageHeader
          eyebrow="Library"
          title="Edit book"
          description="Update the metadata, covers, and taxonomy for this entry."
        />
        {error && <p role="alert">{error}</p>}
        <div className="panel">
          <BookForm
            initial={initialFromBook(book)}
            submitLabel="Save changes"
            onSubmit={handleSave}
            onCancel={() => {
              setEditing(false);
              setError(null);
            }}
          />
        </div>
      </div>
    );
  }

  return (
    <div>
      <Link to="/library" className="detail-back">
        <ArrowLeft size={16} aria-hidden="true" />
        Library
      </Link>

      {error && <p role="alert">{error}</p>}

      <div className="detail-layout">
        <aside className="detail-rail">
          <BookCover
            title={book.title}
            coverUrl={book.cover_url}
            className="detail-cover"
          />
          <div className="detail-rail-actions">
            <button
              type="button"
              className="primary"
              onClick={() => setEditing(true)}
            >
              Edit book
            </button>
            <button type="button" className="danger" onClick={handleDelete}>
              Delete
            </button>
          </div>
        </aside>

        <div className="detail-body">
          <p className="detail-eyebrow">
            {book.genres.length > 0
              ? book.genres.map((genre) => genre.name).join(" · ")
              : "From your library"}
          </p>
          <h1 className="detail-title">{book.title}</h1>
          {book.subtitle && <p className="detail-subtitle">{book.subtitle}</p>}
          <p className="detail-author">
            by{" "}
            {book.authors.length > 0
              ? book.authors.map((author) => author.name).join(", ")
              : "Unknown author"}
          </p>

          <div className="detail-meta">
            <div className="meta-card">
              <span className="meta-label">Published</span>
              <span className="meta-value tabular">
                {book.published_year ?? "—"}
              </span>
            </div>
            <div className="meta-card">
              <span className="meta-label">Pages</span>
              <span className="meta-value tabular">{book.pages ?? "—"}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">Language</span>
              <span className="meta-value">{book.language ?? "—"}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">Publisher</span>
              <span className="meta-value">
                {book.publisher?.name ?? "—"}
              </span>
            </div>
            <div className="meta-card">
              <span className="meta-label">ISBN-10</span>
              <span className="meta-value tabular">{book.isbn10 ?? "—"}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">ISBN-13</span>
              <span className="meta-value tabular">{book.isbn13 ?? "—"}</span>
            </div>
          </div>

          {(book.genres.length > 0 || book.tags.length > 0) && (
            <div className="detail-tags">
              {book.genres.length > 0 && (
                <div className="detail-tag-group">
                  <span className="detail-tag-label">Genres</span>
                  <ul className="chips">
                    {book.genres.map((genre) => (
                      <li key={genre.id} className="chip">
                        {genre.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {book.tags.length > 0 && (
                <div className="detail-tag-group">
                  <span className="detail-tag-label">Tags</span>
                  <ul className="chips">
                    {book.tags.map((tag) => (
                      <li key={tag.id} className="chip">
                        {tag.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <section className="detail-section">
            <h2>Synopsis</h2>
            {book.description ? (
              <p className="prose">{book.description}</p>
            ) : (
              <p className="muted">
                No synopsis yet. Use “Edit book” to add one.
              </p>
            )}
          </section>

          <section className="detail-section">
            <h2>Reading notes</h2>
            {book.notes ? (
              <p className="prose">{book.notes}</p>
            ) : (
              <p className="muted">
                Nothing noted yet. Use “Edit book” to keep your own notes.
              </p>
            )}
          </section>

          <section className="detail-section">
            <h2>Catalogued</h2>
            <p className="muted">Added to the library {formatDate(book.created_at)}.</p>
          </section>

          <ReadingPanel bookId={book.id} bookPages={book.pages} />
        </div>
      </div>
    </div>
  );
}
