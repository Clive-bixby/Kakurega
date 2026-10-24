import { ArrowRight, BookOpen, Palette, ShieldCheck, Tag } from "lucide-react";
import { Link } from "react-router-dom";

import { PageHeader } from "../shared/PageHeader";

export function SettingsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Preferences"
        title="Settings"
        description="Kakurega is a local-first personal library. Appearance is fixed to the Literary Noir theme; everything else lives with your data."
      />

      <div className="settings-grid">
        <nav className="settings-nav" aria-label="Settings sections">
          <a href="#appearance" className="active">
            Appearance
          </a>
          <a href="#library">Library</a>
          <a href="#data">Data &amp; privacy</a>
          <a href="#about">About</a>
        </nav>

        <div>
          <section className="settings-section" id="appearance">
            <h2>Appearance</h2>
            <p>
              The interface uses the Literary Noir palette: deep charcoal
              surfaces, a lavender accent, and Inter for both headings and body
              text.
            </p>
            <div className="settings-card">
              <div className="settings-item">
                <span className="add-card-icon" aria-hidden="true">
                  <Palette size={20} />
                </span>
                <div>
                  <strong>Dark theme</strong>
                  <p>Always on, tuned for low-glare reading.</p>
                </div>
              </div>
              <div className="settings-item">
                <span className="add-card-icon" aria-hidden="true">
                  <BookOpen size={20} />
                </span>
                <div>
                  <strong>Cover-first library</strong>
                  <p>
                    Books without cover art get a generated typographic cover
                    instead of an empty box.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="settings-section" id="library">
            <h2>Library</h2>
            <p>
              Keep the collection tidy. Tags, household members, and imports
              each have their own workspace.
            </p>
            <div className="settings-links">
              <Link to="/tags" className="settings-link">
                <Tag size={18} aria-hidden="true" />
                <span>
                  <strong>Tags</strong>
                  <small>Create, rename, and delete tags</small>
                </span>
                <ArrowRight size={16} aria-hidden="true" />
              </Link>
              <Link to="/reading" className="settings-link">
                <BookOpen size={18} aria-hidden="true" />
                <span>
                  <strong>Household members</strong>
                  <small>Manage readers and their activity</small>
                </span>
                <ArrowRight size={16} aria-hidden="true" />
              </Link>
              <Link to="/import" className="settings-link">
                <ShieldCheck size={18} aria-hidden="true" />
                <span>
                  <strong>Import a shelf</strong>
                  <small>Bring in a CSV without leaving your data</small>
                </span>
                <ArrowRight size={16} aria-hidden="true" />
              </Link>
            </div>
          </section>

          <section className="settings-section" id="data">
            <h2>Data &amp; privacy</h2>
            <p>
              Books, covers, and reading history stay on this Kakurega instance.
              Metadata lookups only run when you add a book by ISBN, and CSV
              imports never contact an external service.
            </p>
            <p>
              Uploaded covers are stored alongside the app and referenced by
              relative path, so backups should include the storage directory.
            </p>
          </section>

          <section className="settings-section" id="about">
            <h2>About</h2>
            <p>
              Kakurega is a personal library manager for cataloguing books,
              organising them with genres and tags, and tracking who in the
              household is reading what.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
