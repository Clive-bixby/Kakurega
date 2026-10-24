import { useEffect, useRef, useState } from "react";

import {
  createTaxonomy,
  searchTaxonomy,
  TaxonomyKind,
} from "../services/api";

export type SelectedOption = {
  id: number | null;
  name: string;
};

type Props = {
  label: string;
  kind: TaxonomyKind;
  selected: SelectedOption[];
  onChange: (next: SelectedOption[]) => void;
  multiple?: boolean;
};

export function TaxonomyPicker({
  label,
  kind,
  selected,
  onChange,
  multiple = true,
}: Props) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState<{ id: number; name: string }[]>([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const requestId = useRef(0);

  useEffect(() => {
    const handle = setTimeout(() => {
      const id = ++requestId.current;
      searchTaxonomy(kind, query, 20)
        .then((items) => {
          if (id === requestId.current) setOptions(items);
        })
        .catch((e) => {
          if (id === requestId.current) {
            setError(e instanceof Error ? e.message : "Failed to load options");
          }
        });
    }, 250);
    return () => clearTimeout(handle);
  }, [kind, query]);

  const available = options.filter(
    (option) =>
      !selected.some(
        (chosen) =>
          chosen.id === option.id ||
          (chosen.id === null &&
            chosen.name.toLowerCase() === option.name.toLowerCase()),
      ),
  );
  const trimmed = query.trim();
  const exact =
    trimmed.length > 0 &&
    [...options, ...selected].some(
      (option) => option.name.toLowerCase() === trimmed.toLowerCase(),
    );

  function add(option: SelectedOption) {
    if (multiple) {
      onChange([...selected, option]);
    } else {
      onChange([option]);
    }
    setQuery("");
    setOpen(false);
    setError(null);
  }

  function remove(index: number) {
    onChange(selected.filter((_, position) => position !== index));
  }

  async function create() {
    if (!trimmed) return;
    setBusy(true);
    try {
      const created = await createTaxonomy(kind, trimmed);
      add({ id: created.id, name: created.name });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create option");
    } finally {
      setBusy(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      if (available.length > 0) {
        add({ id: available[0].id, name: available[0].name });
      } else if (trimmed && !exact) {
        void create();
      }
    } else if (e.key === "Escape") {
      setOpen(false);
    } else if (e.key === "Backspace" && !query && selected.length > 0 && multiple) {
      remove(selected.length - 1);
    }
  }

  return (
    <div className="taxonomy-picker">
      <span className="field-label">{label}</span>
      {selected.length > 0 && (
        <ul className="chips" aria-label={`${label} selected`}>
          {selected.map((option, index) => (
            <li key={`${option.id ?? "new"}-${option.name}`} className="chip">
              {option.name}
              <button
                type="button"
                onClick={() => remove(index)}
                aria-label={`Remove ${option.name}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={handleKeyDown}
        placeholder={multiple ? "Search or add..." : "Search or add one..."}
        aria-label={label}
        aria-expanded={open}
        autoComplete="off"
      />
      {open && (available.length > 0 || (trimmed && !exact)) && (
        <div className="picker-menu" onMouseDown={(e) => e.preventDefault()}>
          {available.slice(0, 8).map((option) => (
            <button
              key={option.id}
              type="button"
              className="picker-option"
              onClick={() => add({ id: option.id, name: option.name })}
            >
              {option.name}
            </button>
          ))}
          {trimmed && !exact && (
            <button
              type="button"
              className="picker-option picker-create"
              onClick={create}
              disabled={busy}
            >
              {busy ? "Adding..." : `Add “${trimmed}”`}
            </button>
          )}
        </div>
      )}
      {error && <p role="alert">{error}</p>}
    </div>
  );
}
