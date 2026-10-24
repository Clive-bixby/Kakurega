import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";
import { createBook, uploadImage } from "../services/api";

export function AddBookPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [coverUrl, setCoverUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

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
    if (!title.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await createBook({ title, subtitle: null, isbn10: null, isbn13: null, description: null, pages: null, language: null, published_year: null, cover_url: coverUrl, google_books_id: null, openlibrary_id: null });
      navigate("/library");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <PageHeader title="Add Book" />
      <form onSubmit={handleSubmit}>
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" aria-label="Title" />
        <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handleCoverChange} aria-label="Cover image" />
        {uploading && <p>Uploading cover...</p>}
        {coverUrl && <img src={coverUrl} alt="Cover preview" width={120} />}
        <button type="submit" disabled={saving || uploading}>
          {saving ? "Saving..." : "Save"}
        </button>
        {error && <p role="alert">{error}</p>}
      </form>
    </div>
  );
}
