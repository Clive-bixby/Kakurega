import { Camera, PenLine, ScanBarcode } from "lucide-react";
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
      <PageHeader
        eyebrow="Library"
        title="Add a book"
        description="Look the book up by ISBN, scan its barcode, or enter the details yourself. Every prefilled field stays editable."
      />

      {notice && (
        <p className="form-message" role="status">
          {notice}
        </p>
      )}
      {error && (
        <p className="form-message" role="alert">
          {error}
        </p>
      )}
      {existingId && (
        <p className="form-message" role="status">
          This ISBN is already in your library.{" "}
          <Link to={`/library/${existingId}`}>Open the existing book</Link>.
        </p>
      )}

      <div className="add-grid">
        <section className="add-card" aria-labelledby="lookup-heading">
          <span className="add-card-icon" aria-hidden="true">
            <ScanBarcode size={22} />
          </span>
          <h2 id="lookup-heading">Look up an ISBN</h2>
          <p>
            Type the ISBN and we will fetch the title, author, cover, and page
            count from the metadata services.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void lookup(isbn);
            }}
          >
            <input
              value={isbn}
              onChange={(e) => setIsbn(e.target.value)}
              placeholder="9780140328721"
              aria-label="ISBN"
            />
            <button
              type="submit"
              className="primary"
              disabled={looking || !isbn.trim()}
            >
              {looking ? "Looking..." : "Look up"}
            </button>
          </form>
        </section>

        <section className="add-card" aria-labelledby="scan-heading">
          <span className="add-card-icon" aria-hidden="true">
            <Camera size={22} />
          </span>
          <h2 id="scan-heading">Scan the barcode</h2>
          <p>
            Photograph the barcode on the back of the book and let the scanner
            read the ISBN for you.
          </p>
          <label className="file-drop">
            <Camera size={18} aria-hidden="true" />
            <span>
              {looking ? "Reading barcode..." : "Upload a barcode photo"}
            </span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              capture="environment"
              onChange={handleBarcode}
              aria-label="Barcode photo"
            />
          </label>
        </section>

        <section className="add-card" aria-labelledby="manual-heading">
          <span className="add-card-icon" aria-hidden="true">
            <PenLine size={22} />
          </span>
          <h2 id="manual-heading">Enter it manually</h2>
          <p>
            Best for rare, uncatalogued, or self-published editions. Fill in as
            much or as little as you like.
          </p>
          <button
            type="button"
            className="primary"
            onClick={() => {
              setExistingId(null);
              setNotice(null);
              showForm(manualInitial(isbn));
            }}
          >
            Start a blank entry
          </button>
        </section>
      </div>

      {initial && !existingId && (
        <section className="panel" aria-labelledby="details-heading">
          <div className="panel-header">
            <h2 id="details-heading">Book details</h2>
            <span className="muted">Verify the metadata before saving</span>
          </div>
          <BookForm
            key={formKey}
            initial={initial}
            submitLabel="Add book"
            onSubmit={handleCreate}
          />
        </section>
      )}
    </div>
  );
}
