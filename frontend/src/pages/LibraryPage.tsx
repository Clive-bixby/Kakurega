import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { X } from "lucide-react";

import { READING_STATUS_OPTIONS } from "../components/StatusBadge";
import { useBooks } from "../hooks/useBooks";
import { BookCover } from "../shared/BookCover";
import { EmptyState } from "../shared/EmptyState";
import { PageHeader } from "../shared/PageHeader";
import {
  fetchMembers,
  fetchTags,
  Member,
  ReadingStatus,
  searchTaxonomy,
  TagSummary,
  TaxonomyItem,
} from "../services/api";

const PAGE_SIZE = 24;
const NEXT_YEAR = new Date().getFullYear() + 1;

function parseYear(value: string): number | undefined {
  const number = Number(value);
  return Number.isInteger(number) && number >= 1000 ? number : undefined;
}

export function LibraryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlQuery = (searchParams.get("q") ?? "").trim();

  const [offset, setOffset] = useState(0);
  const [members, setMembers] = useState<Member[]>([]);
  const [genres, setGenres] = useState<TaxonomyItem[]>([]);
  const [tags, setTags] = useState<TagSummary[]>([]);

  const [genreId, setGenreId] = useState("");
  const [tagName, setTagName] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [memberId, setMemberId] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState<"title" | "added" | "year">("title");

  useEffect(() => {
    setOffset(0);
  }, [urlQuery, genreId, tagName, yearFrom, yearTo, memberId, status, sort]);

  useEffect(() => {
    Promise.all([
      fetchMembers(),
      searchTaxonomy("genres", "", 500),
      fetchTags(500),
    ])
      .then(([memberList, genreList, tagList]) => {
        setMembers(memberList);
        setGenres(genreList);
        setTags(tagList);
      })
      .catch(() => {
        setMembers([]);
        setGenres([]);
        setTags([]);
      });
  }, []);

  const { books, total, loading, error } = useBooks({
    limit: PAGE_SIZE,
    offset,
    q: urlQuery || undefined,
    genre_id: genreId ? Number(genreId) : undefined,
    tag: tagName || undefined,
    year_from: parseYear(yearFrom),
    year_to: parseYear(yearTo),
    member_id: memberId ? Number(memberId) : undefined,
    status: status ? (status as ReadingStatus) : undefined,
    sort,
  });

  const tagNames = useMemo(
    () => new Map(tags.map((tag) => [tag.id, tag.name])),
    [tags],
  );

  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);
  const canGoBack = offset > 0;
  const canGoForward = offset + PAGE_SIZE < total;
  const filtered =
    genreId !== "" ||
    tagName !== "" ||
    yearFrom !== "" ||
    yearTo !== "" ||
    memberId !== "" ||
    status !== "" ||
    sort !== "title";

  function clearFilters() {
    setGenreId("");
    setTagName("");
    setYearFrom("");
    setYearTo("");
    setMemberId("");
    setStatus("");
    setSort("title");
    if (urlQuery) setSearchParams({});
  }

  return (
    <div>
      <PageHeader
        title="Library"
        description={
          loading && total === 0
            ? "Loading your collection..."
            : `${total} ${total === 1 ? "book" : "books"} in your collection`
        }
        actions={
          <label className="sort-control">
            <span className="sr-only">Sort books</span>
            <select
              aria-label="Sort books"
              value={sort}
              onChange={(event) =>
                setSort(event.target.value as "title" | "added" | "year")
              }
            >
              <option value="title">Sort: Title</option>
              <option value="added">Sort: Recently added</option>
              <option value="year">Sort: Publication year</option>
            </select>
          </label>
        }
      />

      <section className="panel filter-panel" aria-label="Library filters">
        <div className="filter-grid">
          <label>
            Genre
            <select
              value={genreId}
              onChange={(event) => setGenreId(event.target.value)}
            >
              <option value="">All genres</option>
              {genres.map((genre) => (
                <option key={genre.id} value={genre.id}>
                  {genre.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Tag
            <select
              value={tagName}
              onChange={(event) => setTagName(event.target.value)}
            >
              <option value="">All tags</option>
              {tags.map((tag) => (
                <option key={tag.id} value={tag.name}>
                  {tag.name} ({tag.book_count})
                </option>
              ))}
            </select>
          </label>
          <label>
            Member
            <select
              value={memberId}
              onChange={(event) => setMemberId(event.target.value)}
            >
              <option value="">Everyone</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Reading status
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="">Any status</option>
              {READING_STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Published from
            <input
              type="number"
              min={1000}
              max={NEXT_YEAR}
              inputMode="numeric"
              value={yearFrom}
              onChange={(event) => setYearFrom(event.target.value)}
            />
          </label>
          <label>
            Published to
            <input
              type="number"
              min={1000}
              max={NEXT_YEAR}
              inputMode="numeric"
              value={yearTo}
              onChange={(event) => setYearTo(event.target.value)}
            />
          </label>
        </div>

        <div className="filter-actions">
          <span className="muted tabular">
            {from}–{to} of {total}
          </span>
          <div className="filter-buttons">
            <Link to="/tags" className="text-link">
              Manage tags
            </Link>
            <button
              type="button"
              onClick={clearFilters}
              disabled={!filtered && !urlQuery}
            >
              Clear filters
            </button>
          </div>
        </div>
      </section>

      {urlQuery && (
        <div className="query-chip-row">
          <span className="chip chip-accent">
            “{urlQuery}”
            <button
              type="button"
              onClick={() => setSearchParams({})}
              aria-label={`Clear search for ${urlQuery}`}
            >
              <X size={12} aria-hidden="true" />
            </button>
          </span>
        </div>
      )}

      {loading && <p className="muted">Loading books...</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && !error && books.length === 0 && (
        <EmptyState
          title={
            filtered || urlQuery
              ? "No books match these filters"
              : "Your library is empty"
          }
        >
          {filtered || urlQuery ? (
            "Try a different combination, or clear the filters."
          ) : (
            <>
              Add a book by ISBN or <Link to="/import">import a shelf</Link>.
            </>
          )}
        </EmptyState>
      )}

      {books.length > 0 && (
        <ul className="book-grid">
          {books.map((book) => (
            <li key={book.id} className="book-card">
              <Link to={`/library/${book.id}`} className="book-card-link">
                <BookCover
                  title={book.title}
                  coverUrl={book.cover_url}
                  decorative
                />
                <div>
                  <h2 className="book-card-title">{book.title}</h2>
                  <p className="book-card-meta">
                    {book.author_names.length > 0
                      ? book.author_names.join(", ")
                      : "Unknown author"}
                    {book.published_year ? ` · ${book.published_year}` : ""}
                  </p>
                </div>
              </Link>
              {book.tag_ids.length > 0 && (
                <ul className="chips book-card-tags" aria-label="Tags">
                  {book.tag_ids.slice(0, 3).map((tagId) => {
                    const name = tagNames.get(tagId);
                    return name ? (
                      <li key={tagId} className="chip">
                        {name}
                      </li>
                    ) : null;
                  })}
                  {book.tag_ids.length > 3 && (
                    <li className="chip">+{book.tag_ids.length - 3}</li>
                  )}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}

      {total > PAGE_SIZE && (
        <nav className="pager" aria-label="Library pages">
          <span className="muted tabular">
            {from}–{to} of {total}
          </span>
          <div className="pager-actions">
            <button
              type="button"
              disabled={!canGoBack || loading}
              onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            >
              Previous
            </button>
            <button
              type="button"
              disabled={!canGoForward || loading}
              onClick={() => setOffset(offset + PAGE_SIZE)}
            >
              Next
            </button>
          </div>
        </nav>
      )}
    </div>
  );
}
