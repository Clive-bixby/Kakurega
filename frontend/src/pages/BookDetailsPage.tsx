import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { BookForm, BookFormInitial } from "../components/BookForm";
import { ReadingPanel } from "../components/ReadingPanel";
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
        <PageHeader title="Book Details" />
        <p>Loading...</p>
      </div>
    );
  }

  if (!book) {
    return (
      <div>
        <PageHeader title="Book Details" />
        <p role="alert">{error ?? "Book not found"}</p>
        <Link to="/library">Back to library</Link>
      </div>
    );
  }

  return (
    <div>
      <PageHeader title={editing ? "Edit Book" : book.title} />

      {error && <p role="alert">{error}</p>}

      {editing ? (
        <BookForm
          initial={initialFromBook(book)}
          submitLabel="Save changes"
          onSubmit={handleSave}
          onCancel={() => {
            setEditing(false);
            setError(null);
          }}
        />
      ) : (
        <div className="book-detail">
          <div className="book-detail-cover">
            {book.cover_url ? (
              <img src={book.cover_url} alt={`Cover of ${book.title}`} />
            ) : (
              <div className="cover-preview cover-preview-empty">No cover</div>
            )}
          </div>

          <div className="book-detail-body">
            {book.subtitle && <p className="book-subtitle">{book.subtitle}</p>}

            <dl className="detail-list">
              <dt>Authors</dt>
              <dd>{book.authors.map((a) => a.name).join(", ") || "—"}</dd>
              <dt>Publisher</dt>
              <dd>{book.publisher?.name ?? "—"}</dd>
              <dt>Published</dt>
              <dd>{book.published_year ?? "—"}</dd>
              <dt>Pages</dt>
              <dd>{book.pages ?? "—"}</dd>
              <dt>Language</dt>
              <dd>{book.language ?? "—"}</dd>
              <dt>ISBN-10</dt>
              <dd>{book.isbn10 ?? "—"}</dd>
              <dt>ISBN-13</dt>
              <dd>{book.isbn13 ?? "—"}</dd>
              <dt>Genres</dt>
              <dd>
                {book.genres.length > 0 ? (
                  <ul className="chips">
                    {book.genres.map((genre) => (
                      <li key={genre.id} className="chip">
                        {genre.name}
                      </li>
                    ))}
                  </ul>
                ) : (
                  "—"
                )}
              </dd>
              <dt>Tags</dt>
              <dd>
                {book.tags.length > 0 ? (
                  <ul className="chips">
                    {book.tags.map((tag) => (
                      <li key={tag.id} className="chip">
                        {tag.name}
                      </li>
                    ))}
                  </ul>
                ) : (
                  "—"
                )}
              </dd>
              <dt>Added</dt>
              <dd>{formatDate(book.created_at)}</dd>
            </dl>

            {book.description && (
              <section>
                <h3>Description</h3>
                <p className="prose">{book.description}</p>
              </section>
            )}

            {book.notes && (
              <section>
                <h3>Notes</h3>
                <p className="prose">{book.notes}</p>
              </section>
            )}

            <ReadingPanel bookId={book.id} bookPages={book.pages} />

            <div className="form-actions">
              <button type="button" className="primary" onClick={() => setEditing(true)}>
                Edit
              </button>
              <button type="button" onClick={handleDelete}>
                Delete
              </button>
              <Link to="/library">Back to library</Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
