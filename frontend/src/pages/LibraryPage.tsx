import { Link } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";
import { useBooks } from "../hooks/useBooks";

export function LibraryPage() {
  const { books, loading, error } = useBooks();

  return (
    <div>
      <PageHeader title="Library" />
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <ul>
        {books.map((book) => (
          <li key={book.id}>
            <Link to={`/library/${book.id}`}>{book.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
