export type Book = {
  id: number;
  title: string;
  subtitle: string | null;
  isbn10: string | null;
  isbn13: string | null;
  description: string | null;
  notes: string | null;
  pages: number | null;
  language: string | null;
  published_year: number | null;
  cover_url: string | null;
  google_books_id: string | null;
  openlibrary_id: string | null;
  publisher_id: number | null;
  author_ids: number[];
  genre_ids: number[];
  created_at: string;
};

export type BookListItem = Omit<Book, "description" | "notes">;

export type BookPage = {
  items: BookListItem[];
  total: number;
  limit: number;
  offset: number;
};

export type BookInput = Partial<Omit<Book, "id" | "created_at">> & { title: string };

export type BookListParams = {
  q?: string;
  genre_id?: number;
  year_from?: number;
  year_to?: number;
  sort?: "title" | "added" | "year";
  limit?: number;
  offset?: number;
};

export async function fetchBooks(params: BookListParams = {}): Promise<BookPage> {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  const res = await fetch(`/api/v1/books${query ? `?${query}` : ""}`);
  if (!res.ok) throw new Error("Failed to load books");
  return res.json();
}

export async function searchBooks(q: string, limit = 50): Promise<BookPage> {
  return fetchBooks({ q, limit });
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

export async function fetchBook(id: number): Promise<Book> {
  const res = await fetch(`/api/v1/books/${id}`);
  if (!res.ok) throw new Error("Book not found");
  return res.json();
}

export async function updateBook(id: number, data: BookInput): Promise<Book> {
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

export async function createBook(data: BookInput): Promise<Book> {
  const res = await fetch("/api/v1/books", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create book");
  return res.json();
}
