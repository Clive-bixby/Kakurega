export type Book = {
  id: number;
  title: string;
  subtitle: string | null;
  isbn10: string | null;
  isbn13: string | null;
  description: string | null;
  pages: number | null;
  language: string | null;
  published_year: number | null;
  cover_url: string | null;
  google_books_id: string | null;
  openlibrary_id: string | null;
};

export async function searchBooks(q: string): Promise<Book[]> {
  const res = await fetch(`/api/v1/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}
export type Insights = {
  total_books: number;
  by_published_year: Record<string, number>;
};

export async function fetchInsights(): Promise<Insights> {
  const res = await fetch("/api/v1/insights");
  if (!res.ok) throw new Error("Failed to load insights");
  return res.json();
}
export async function fetchBooks(): Promise<Book[]> {
  const res = await fetch("/api/v1/books");
  if (!res.ok) throw new Error("Failed to load books");
  return res.json();
}

export async function fetchBook(id: number): Promise<Book> {
  const res = await fetch(`/api/v1/books/${id}`);
  if (!res.ok) throw new Error("Book not found");
  return res.json();
}

export async function updateBook(id: number, data: Partial<Omit<Book, "id">>): Promise<Book> {
  const res = await fetch(`/api/v1/books/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update book");
  return res.json();
}

export async function deleteBook(id: number): Promise<void> {
  const res = await fetch(`/api/v1/books/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete book");
}
export type UploadedImage = {
  image_id: string;
  path: string;
};

export async function uploadImage(file: File): Promise<UploadedImage> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/v1/upload/image", { method: "POST", body: form });
  if (!res.ok) throw new Error("Failed to upload image");
  return res.json();
}

export async function createBook(data: Omit<Book, "id">): Promise<Book> {
  const res = await fetch("/api/v1/books", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create book");
  return res.json();
}
