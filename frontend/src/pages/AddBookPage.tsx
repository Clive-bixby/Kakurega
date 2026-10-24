import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { BookForm, BookFormInitial } from "../components/BookForm";
import { PageHeader } from "../shared/PageHeader";
import {
  ApiError,
  BookInput,
  createBook,
  decodeBarcode,
  fetchBookByIsbn,
  lookupMetadata,
} from "../services/api";

function cleanIsbn(value: string): string {
  return value.replace(/[^0-9Xx]/g, "").toUpperCase();
}

function manualInitial(isbn: string): BookFormInitial {
  const cleaned = cleanIsbn(isbn);
  return {
    title: "",
    isbn10: cleaned.length === 10 ? cleaned : null,
    isbn13: cleaned.length === 13 ? cleaned : null,
    authors: [],
    genres: [],
    tags: [],
  };
}

export function AddBookPage() {
  const navigate = useNavigate();
  const [isbn, setIsbn] = useState("");
  const [initial, setInitial] = useState<BookFormInitial | null>(null);
  const [formKey, setFormKey] = useState(0);
  const [existingId, setExistingId] = useState<number | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [looking, setLooking] = useState(false);

  function showForm(values: BookFormInitial) {
    setInitial(values);
    setFormKey((key) => key + 1);
  }

  async function lookup(value: string) {
    const cleaned = value.trim();
    if (!cleaned) return;

    setLooking(true);
    setError(null);
    setNotice(null);
    setExistingId(null);
    setInitial(null);

    try {
      const metadata = await lookupMetadata({ isbn: cleaned });
      const digits = cleanIsbn(cleaned);
      showForm({
        title: metadata.title,
        isbn10:
          metadata.isbn10 ?? (digits.length === 10 ? digits : null),
        isbn13:
          metadata.isbn13 ?? (digits.length === 13 ? digits : null),
        description: metadata.description,
        pages: metadata.pages,
        published_year: metadata.published_year,
        cover_url: metadata.cover_url,
        authors: metadata.authors.map((name) => ({ id: null, name })),
        publisher: metadata.publisher
          ? { id: null, name: metadata.publisher }
          : null,
        genres: [],
        tags: [],
      });

      const lookupIsbn = metadata.isbn13 ?? metadata.isbn10 ?? cleaned;
      try {
        const existing = await fetchBookByIsbn(lookupIsbn);
        setExistingId(existing.id);
      } catch (err) {
        if (!(err instanceof ApiError) || err.status !== 404) throw err;
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        showForm(manualInitial(cleaned));
        setNotice("No metadata found. Enter the details manually.");
      } else {
        setError(
          err instanceof Error ? err.message : "Metadata lookup failed",
        );
      }
    } finally {
      setLooking(false);
    }
  }

  async function handleBarcode(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLooking(true);
    setError(null);
    setNotice(null);
    try {
      const decoded = await decodeBarcode(file);
      setIsbn(decoded.isbn);
      await lookup(decoded.isbn);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Barcode not found");
    } finally {
      setLooking(false);
    }
  }

  async function handleCreate(input: BookInput) {
    const book = await createBook(input);
    navigate(`/library/${book.id}`);
  }

  return (
    <div>
      <PageHeader title="Add Book" />
      <p>
        Type an ISBN and look it up, photograph the barcode, or enter the book
        by hand. Every prefilled field stays editable.
      </p>

      <form
        className="lookup-form"
        onSubmit={(e) => {
          e.preventDefault();
          void lookup(isbn);
        }}
      >
        <label>
          ISBN
          <input
            value={isbn}
            onChange={(e) => setIsbn(e.target.value)}
            placeholder="9780140328721"
            aria-label="ISBN"
          />
        </label>
        <button type="submit" disabled={looking || !isbn.trim()}>
          {looking ? "Looking up..." : "Look up"}
        </button>
        <label>
          Barcode photo
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            capture="environment"
            onChange={handleBarcode}
            aria-label="Barcode photo"
          />
        </label>
        <button
          type="button"
          onClick={() => {
            setExistingId(null);
            setNotice(null);
            showForm(manualInitial(isbn));
          }}
        >
          Enter manually
        </button>
      </form>

      {notice && <p role="status">{notice}</p>}
      {error && <p role="alert">{error}</p>}

      {existingId && (
        <p role="status">
          This ISBN is already in your library.{" "}
          <Link to={`/library/${existingId}`}>Open the existing book</Link>.
        </p>
      )}

      {initial && !existingId && (
        <BookForm
          key={formKey}
          initial={initial}
          submitLabel="Add book"
          onSubmit={handleCreate}
        />
      )}
    </div>
  );
}
