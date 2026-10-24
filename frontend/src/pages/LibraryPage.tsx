import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { READING_STATUS_OPTIONS } from "../components/StatusBadge";
import { useBooks } from "../hooks/useBooks";
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

const PAGE_SIZE = 25;
const NEXT_YEAR = new Date().getFullYear() + 1;

function parseYear(value: string): number | undefined {
  const number = Number(value);
  return Number.isInteger(number) && number >= 1000 ? number : undefined;
}

export function LibraryPage() {
  const [offset, setOffset] = useState(0);
  const [members, setMembers] = useState<Member[]>([]);
  const [genres, setGenres] = useState<TaxonomyItem[]>([]);
  const [tags, setTags] = useState<TagSummary[]>([]);

  const [searchInput, setSearchInput] = useState("");
  const [query, setQuery] = useState("");
  const [genreId, setGenreId] = useState("");
  const [tagName, setTagName] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [memberId, setMemberId] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState<"title" | "added" | "year">("title");

  useEffect(() => {
    const handle = window.setTimeout(() => setQuery(searchInput.trim()), 300);
    return () => window.clearTimeout(handle);
  }, [searchInput]);

  useEffect(() => {
    setOffset(0);
  }, [query, genreId, tagName, yearFrom, yearTo, memberId, status, sort]);

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
    q: query || undefined,
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
    query !== "" ||
    genreId !== "" ||
    tagName !== "" ||
    yearFrom !== "" ||
    yearTo !== "" ||
    memberId !== "" ||
    status !== "" ||
    sort !== "title";

  function clearFilters() {
    setSearchInput("");
    setQuery("");
    setGenreId("");
    setTagName("");
    setYearFrom("");
    setYearTo("");
    setMemberId("");
    setStatus("");
    setSort("title");
  }

  return (
    <div>
      <PageHeader title="Library" />

      <section className="panel filter-panel" aria-label="Library filters">
        <div className="filter-grid">
          <label className="filter-search">
            Search
            <input
              type="search"
              value={searchInput}
              placeholder="Title, author, ISBN..."
              onChange={(event) => setSearchInput(event.target.value)}
            />
          </label>
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
          <label>
            Sort by
            <select
              value={sort}
              onChange={(event) =>
                setSort(event.target.value as "title" | "added" | "year")
              }
            >
              <option value="title">Title</option>
              <option value="added">Recently added</option>
              <option value="year">Publication year</option>
            </select>
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
              disabled={!filtered}
            >
              Clear filters
            </button>
          </div>
        </div>
      </section>

      {loading && <p>Loading...</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && !error && books.length === 0 && (
        <EmptyState
          title={filtered ? "No books match these filters" : "Your library is empty"}
        >
          {filtered ? (
            "Try a different combination or clear the filters."
          ) : (
            <>
              Add a book by ISBN or <Link to="/import">import a shelf</Link>.
            </>
          )}
        </EmptyState>
      )}

      <ul className="book-list">
        {books.map((book) => (
          <li key={book.id} className="book-list-item">
            {book.cover_url ? (
              <img
                className="book-list-cover"
                src={book.cover_url}
                alt=""
                loading="lazy"
              />
            ) : (
              <div className="book-list-cover book-list-cover-empty" aria-hidden="true" />
            )}
            <div className="book-list-body">
              <Link to={`/library/${book.id}`} className="book-list-title">
                {book.title}
              </Link>
              <p className="book-list-meta">
                {[
                  book.published_year,
                  book.language,
                  book.pages ? `${book.pages} pages` : null,
                ]
                  .filter(Boolean)
                  .join(" · ") || "No details yet"}
              </p>
              {book.tag_ids.length > 0 && (
                <ul className="chips book-list-tags">
                  {book.tag_ids.map((tagId) => {
                    const name = tagNames.get(tagId);
                    return name ? (
                      <li key={tagId} className="chip">
                        {name}
                      </li>
                    ) : null;
                  })}
                </ul>
              )}
            </div>
          </li>
        ))}
      </ul>

      <div className="pager">
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
    </div>
  );
}
