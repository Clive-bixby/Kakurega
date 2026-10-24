import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";
import { Book, deleteBook, fetchBook, updateBook } from "../services/api";

export function BookDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState("");

  useEffect(() => {
    if (!id) return;
    fetchBook(Number(id))
      .then((b) => {
        setBook(b);
        setTitle(b.title);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSave() {
    if (!book) return;
    try {
      const updated = await updateBook(book.id, { title });
      setBook(updated);
      setEditing(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    }
  }

  async function handleDelete() {
    if (!book || !confirm("Delete this book?")) return;
    try {
      await deleteBook(book.id);
      navigate("/library");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    }
  }

  return (
    <div>
      <PageHeader title="Book Details" />
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {book && (
        <div>
          {editing ? (
            <>
              <input value={title} onChange={(e) => setTitle(e.target.value)} />
              <button onClick={handleSave}>Save</button>
              <button onClick={() => setEditing(false)}>Cancel</button>
            </>
          ) : (
            <>
              <h2>{book.title}</h2>
              {book.subtitle && <p>{book.subtitle}</p>}
              {book.description && <p>{book.description}</p>}
              <button onClick={() => setEditing(true)}>Edit</button>
              <button onClick={handleDelete}>Delete</button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
