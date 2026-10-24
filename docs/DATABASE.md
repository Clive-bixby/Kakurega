# DATABASE.md

# Book Catalog --- Database Design

## Design Principles

-   Separate global book metadata from user-specific metadata.
-   Design for future multi-user support.
-   Normalize reusable entities (Author, Genre, Publisher, Series).
-   Support recommendations and analytics without schema changes.

## Implemented Tables

The following tables are implemented and migrated:

- `authors`
- `books`
- `publishers`
- `genres`
- `book_authors`
- `book_genres`
- `tags`
- `book_tags`
- `members`
- `reading_entries`

The following are planned but not yet implemented:

- `series`
- `book_copies`
- import staging tables

### Book

-   id
-   title
-   subtitle
-   isbn10
-   isbn13
-   description
-   notes
-   pages
-   language
-   published_year
-   cover_url
-   google_books_id
-   openlibrary_id
-   publisher_id (FK)
-   created_at

`isbn10` and `isbn13` are unique when present (partial unique indexes), and an
ISBN-10 is stored together with its derived ISBN-13. `title` is indexed, as are
`published_year` and `publisher_id`.

### Author

-   id
-   name
-   bio

### BookAuthor (Many-to-Many)

-   book_id
-   author_id

### Publisher

-   id
-   name
-   country

### Series

-   id
-   name

### Genre

-   id
-   name

### BookGenre (Many-to-Many)

-   book_id
-   genre_id

### BookCopy

Represents a physical copy owned.

-   id
-   book_id
-   location
-   condition
-   purchase_date
-   purchase_price
-   photo_path
-   favorite
-   date_added

### Tag

-   id
-   name (unique case-insensitively)

`GET /tags` derives `book_count` from `book_tags`, so no counter column can
drift. Renaming a tag updates every book at once; deleting a tag removes its
`book_tags` rows and leaves the books intact.

### BookTag

-   book_id (FK, cascades)
-   tag_id (FK, cascades)

### Member

A person in the household. No authentication, email, or login.

-   id
-   name (varchar(100), unique case-insensitively via a `lower(name)` index)
-   created_at

### ReadingEntry

One member's reading state for one book; at most one row per book/member pair.

-   id
-   book_id (FK, cascades with the book)
-   member_id (FK, cascades with the member)
-   status (`want_to_read` | `reading` | `finished` | `abandoned`, check
    constrained)
-   current_page (nullable; validated against `books.pages` when known)
-   started_on (date, nullable)
-   finished_on (date, nullable; cannot precede `started_on`)
-   note (text, nullable)
-   updated_at

Progress is derived from `current_page / pages`; no percentage is stored.
Indexes cover `member_id` and `status` for the reading list and book filters.

## Future Tables

### User

-   id
-   name
-   email

### UserBook

-   user_id
-   book_copy_id
-   reading_status
-   progress
-   rating
-   notes
-   started_reading
-   finished_reading

### ReadingSession

-   id
-   user_id
-   book_copy_id
-   pages_read
-   minutes
-   session_date

### RecommendationCache

-   id
-   book_id
-   source
-   recommendations_json
-   generated_at

## Entity Relationship (Simplified)

``` text
Author
   ▲
   │
BookAuthor
   │
   ▼
 Book ─────────► Publisher
   │
   ├──────────► Series
   │
   ├──────────► BookGenre ◄──── Genre
   │
   ▼
BookCopy
   │
   ├──────────► BookTag ◄──── Tag
   │
   ▼
UserBook (Future)
   ▲
   │
 User (Future)
```

## Notes

-   Book stores universal metadata.
-   BookCopy stores ownership information (not implemented yet).
-   Member + ReadingEntry replace the planned UserBook table for the current
    single-household model; User/ReadingSession remain future work for accounts
    and page-level history.
-   Author, Publisher, and Genre relationships are implemented.
-   ISBN is the book's identity: unique partial indexes plus canonicalisation to
      ISBN-13 prevent duplicate rows.
-   Series and BookCopy remain future work.
-   This schema supports future family accounts without major redesign.
