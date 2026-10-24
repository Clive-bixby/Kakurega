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
  publisher: TaxonomyItem | null;
  authors: TaxonomyItem[];
  genres: TaxonomyItem[];
  tags: TaxonomyItem[];
  author_ids: number[];
  genre_ids: number[];
  tag_ids: number[];
  created_at: string;
};

export type BookListItem = Omit<
  Book,
  "description" | "notes" | "publisher" | "authors" | "genres" | "tags"
>;

export type BookPage = {
  items: BookListItem[];
  total: number;
  limit: number;
  offset: number;
};

export type BookInput = Partial<
  Omit<
    Book,
    "id" | "created_at" | "publisher" | "authors" | "genres" | "tags"
  >
> & { title: string };

export class ApiError extends Error {
  status: number;
  bookId?: number;

  constructor(message: string, status: number, bookId?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.bookId = bookId;
  }
}

async function readError(res: Response, fallback: string): Promise<ApiError> {
  let message = fallback;
  let bookId: number | undefined;
  try {
    const body = await res.json();
    const detail = body?.detail;
    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = "Validation failed";
    } else if (detail && typeof detail === "object") {
      if (typeof detail.message === "string") message = detail.message;
      if (typeof detail.book_id === "number") bookId = detail.book_id;
    }
  } catch {
    // Keep the fallback when the body is not JSON.
  }
  return new ApiError(message, res.status, bookId);
}

export type BookListParams = {
  q?: string;
  genre_id?: number;
  tag?: string;
  year_from?: number;
  year_to?: number;
  member_id?: number;
  status?: ReadingStatus;
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
  total_members: number;
  by_published_year: Record<string, number>;
  by_genre: NamedCount[];
  by_author: NamedCount[];
  by_language: Record<string, number>;
  currently_reading: {
    book_id: number;
    book_title: string;
    member_id: number;
    member_name: string;
    current_page: number | null;
    pages: number | null;
  }[];
  recently_added: {
    book_id: number;
    title: string;
    cover_url: string | null;
    created_at: string;
  }[];
};

export type NamedCount = {
  id: number;
  name: string;
  count: number;
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
  if (!res.ok) throw await readError(res, "Failed to update book");
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
  if (!res.ok) throw await readError(res, "Failed to create book");
  return res.json();
}

export type ImportProblem = {
  row: number;
  reason: string;
};

export type ImportResult = {
  created: number;
  updated: number;
  skipped_duplicates: number;
  failed: ImportProblem[];
  warnings: ImportProblem[];
  ignored_columns: string[];
};

export async function importCsv(
  file: File,
  updateExisting = false,
): Promise<ImportResult> {
  const form = new FormData();
  form.append("file", file);
  const query = updateExisting ? "?update_existing=true" : "";
  const res = await fetch(`/api/v1/import/csv${query}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw await readError(res, "Failed to import");
  return res.json();
}

export type Metadata = {
  title: string;
  authors: string[];
  publisher: string | null;
  published_year: number | null;
  isbn10: string | null;
  isbn13: string | null;
  description: string | null;
  cover_url: string | null;
  pages: number | null;
  source: string;
  confidence: number;
};

export type MetadataQuery = {
  isbn?: string;
  title?: string;
  author?: string;
};

export async function lookupMetadata(query: MetadataQuery): Promise<Metadata> {
  const res = await fetch("/api/v1/lookup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(query),
  });
  if (!res.ok) throw await readError(res, "Metadata lookup failed");
  return res.json();
}

export async function decodeBarcode(file: File): Promise<{ isbn: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/v1/barcode", { method: "POST", body: form });
  if (!res.ok) throw await readError(res, "No barcode found");
  return res.json();
}

export async function fetchBookByIsbn(isbn: string): Promise<Book> {
  const res = await fetch(`/api/v1/books/isbn/${encodeURIComponent(isbn)}`);
  if (!res.ok) throw await readError(res, "Book not found");
  return res.json();
}

export type TaxonomyKind = "authors" | "publishers" | "genres" | "tags";

export type TaxonomyItem = {
  id: number;
  name: string;
  country?: string | null;
};

export async function searchTaxonomy(
  kind: TaxonomyKind,
  q = "",
  limit = 50,
): Promise<TaxonomyItem[]> {
  const search = new URLSearchParams();
  if (q.trim()) search.set("q", q.trim());
  search.set("limit", String(limit));
  const res = await fetch(`/api/v1/${kind}?${search.toString()}`);
  if (!res.ok) throw await readError(res, "Failed to load options");
  return res.json();
}

export async function createTaxonomy(
  kind: TaxonomyKind,
  name: string,
): Promise<TaxonomyItem> {
  const res = await fetch(`/api/v1/${kind}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw await readError(res, "Failed to create option");
  return res.json();
}

export type TagSummary = TaxonomyItem & {
  book_count: number;
};

export async function fetchTags(limit = 500): Promise<TagSummary[]> {
  const res = await fetch(`/api/v1/tags?limit=${limit}`);
  if (!res.ok) throw await readError(res, "Failed to load tags");
  return res.json();
}

export async function renameTag(id: number, name: string): Promise<TagSummary> {
  const res = await fetch(`/api/v1/tags/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw await readError(res, "Failed to rename tag");
  return res.json();
}

export async function deleteTag(id: number): Promise<void> {
  const res = await fetch(`/api/v1/tags/${id}`, { method: "DELETE" });
  if (!res.ok) throw await readError(res, "Failed to delete tag");
}

export type ReadingStatus =
  | "want_to_read"
  | "reading"
  | "finished"
  | "abandoned";

export type Member = {
  id: number;
  name: string;
  created_at: string;
};

export type ReadingEntry = {
  id: number;
  book_id: number;
  member_id: number;
  member_name: string;
  book_title: string;
  book_pages: number | null;
  status: ReadingStatus;
  current_page: number | null;
  started_on: string | null;
  finished_on: string | null;
  note: string | null;
  updated_at: string;
};

export type ReadingInput = {
  status: ReadingStatus;
  current_page?: number | null;
  started_on?: string | null;
  finished_on?: string | null;
  note?: string | null;
};

export async function fetchMembers(): Promise<Member[]> {
  const res = await fetch("/api/v1/members");
  if (!res.ok) throw await readError(res, "Failed to load household members");
  return res.json();
}

export async function createMember(name: string): Promise<Member> {
  const res = await fetch("/api/v1/members", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw await readError(res, "Failed to add member");
  return res.json();
}

export async function updateMember(id: number, name: string): Promise<Member> {
  const res = await fetch(`/api/v1/members/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw await readError(res, "Failed to rename member");
  return res.json();
}

export async function deleteMember(id: number): Promise<void> {
  const res = await fetch(`/api/v1/members/${id}`, { method: "DELETE" });
  if (!res.ok) throw await readError(res, "Failed to remove member");
}

export async function fetchBookReading(bookId: number): Promise<ReadingEntry[]> {
  const res = await fetch(`/api/v1/books/${bookId}/reading`);
  if (!res.ok) throw await readError(res, "Failed to load reading entries");
  return res.json();
}

export async function upsertReading(
  bookId: number,
  memberId: number,
  data: ReadingInput,
): Promise<ReadingEntry> {
  const res = await fetch(`/api/v1/books/${bookId}/reading/${memberId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw await readError(res, "Failed to save reading entry");
  return res.json();
}

export async function deleteReading(
  bookId: number,
  memberId: number,
): Promise<void> {
  const res = await fetch(`/api/v1/books/${bookId}/reading/${memberId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw await readError(res, "Failed to remove reading entry");
}

export type ReadingListParams = {
  member_id?: number;
  status?: ReadingStatus;
};

export async function fetchReading(
  params: ReadingListParams = {},
): Promise<ReadingEntry[]> {
  const search = new URLSearchParams();
  if (params.member_id !== undefined) {
    search.set("member_id", String(params.member_id));
  }
  if (params.status) search.set("status", params.status);
  const query = search.toString();
  const res = await fetch(`/api/v1/reading${query ? `?${query}` : ""}`);
  if (!res.ok) throw await readError(res, "Failed to load reading list");
  return res.json();
}
