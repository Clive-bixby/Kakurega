# DATABASE.md

# Book Catalog --- Database Design

## Design Principles

-   Separate global book metadata from user-specific metadata.
-   Design for future multi-user support.
-   Normalize reusable entities (Author, Genre, Publisher, Series).
-   Support recommendations and analytics without schema changes.

## Core Entities

### Book

-   id
-   title
-   subtitle
-   isbn10
-   isbn13
-   description
-   pages
-   language
-   published_year
-   cover_url
-   google_books_id
-   openlibrary_id
-   publisher_id (FK)
-   series_id (FK)

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
-   name

### BookTag

-   book_copy_id
-   tag_id

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
-   BookCopy stores ownership information.
-   UserBook stores personal reading information.
-   This schema supports future family accounts without major redesign.
