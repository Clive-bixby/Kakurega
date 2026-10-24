import {
  BarChart3,
  BookMarked,
  BookOpen,
  Home,
  Library,
  PlusCircle,
  Search,
  Settings,
  Tag,
  Upload,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

const navigationItems = [
  { label: "Dashboard", path: "/dashboard", icon: Home },
  { label: "Library", path: "/library", icon: Library },
  { label: "Tags", path: "/tags", icon: Tag },
  { label: "Reading", path: "/reading", icon: BookMarked },
  { label: "Add Book", path: "/add-book", icon: PlusCircle },
  { label: "Import", path: "/import", icon: Upload },
  { label: "Search", path: "/search", icon: Search },
  { label: "Insights", path: "/insights", icon: BarChart3 },
  { label: "Settings", path: "/settings", icon: Settings },
];

export function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand">
          <BookOpen aria-hidden="true" size={24} />
          <span>Kakurega</span>
        </div>

        <nav className="nav-list">
          {navigationItems.map((item) => (
            <NavLink key={item.path} to={item.path} className="nav-link">
              <item.icon aria-hidden="true" size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
