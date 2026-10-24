import {
  BarChart3,
  BookMarked,
  BookOpen,
  Home,
  Library,
  Plus,
  Search,
  Settings,
  Tag,
  Upload,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

const navigationItems = [
  { label: "Dashboard", path: "/dashboard", icon: Home },
  { label: "Library", path: "/library", icon: Library },
  { label: "Tags", path: "/tags", icon: Tag },
  { label: "Reading", path: "/reading", icon: BookMarked },
  { label: "Import", path: "/import", icon: Upload },
  { label: "Insights", path: "/insights", icon: BarChart3 },
];

export function AppLayout() {
  const navigate = useNavigate();
  const searchRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchRef.current?.focus();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  function handleSearch(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = query.trim();
    navigate(trimmed ? `/library?q=${encodeURIComponent(trimmed)}` : "/library");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <Link to="/dashboard" className="brand">
          <span className="brand-mark" aria-hidden="true">
            <BookOpen size={20} />
          </span>
          <span className="brand-text">
            <span className="brand-name">Kakurega</span>
            <span className="brand-sub">Personal Library</span>
          </span>
        </Link>

        <nav className="nav-list">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
              >
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <Link to="/add-book" className="sidebar-cta">
          <Plus size={18} aria-hidden="true" />
          Add New Book
        </Link>

        <div className="sidebar-footer">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <Settings size={18} aria-hidden="true" />
            <span>Settings</span>
          </NavLink>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <form className="topbar-search" role="search" onSubmit={handleSearch}>
            <Search size={18} aria-hidden="true" />
            <input
              ref={searchRef}
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search title, author, or ISBN..."
              aria-label="Search the library"
            />
            <kbd className="search-hint" aria-hidden="true">
              ⌘K
            </kbd>
          </form>

          <div className="topbar-actions">
            <Link to="/add-book" className="topbar-add">
              <Plus size={16} aria-hidden="true" />
              Add book
            </Link>
            <span className="avatar" aria-hidden="true">
              K
            </span>
          </div>
        </header>

        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
