type Item = {
  label: string;
  value: number;
};

type Props = {
  items: Item[];
  label: string;
  emptyText?: string;
};

export function BarList({ items, label, emptyText = "No data yet." }: Props) {
  if (items.length === 0) {
    return <p className="muted">{emptyText}</p>;
  }

  const max = Math.max(...items.map((item) => item.value), 1);

  return (
    <ul className="bar-list" aria-label={label}>
      {items.map((item) => (
        <li key={item.label} className="bar-list-item">
          <div className="bar-list-heading">
            <span className="bar-list-label">{item.label}</span>
            <span className="muted tabular">{item.value}</span>
          </div>
          <div className="bar-track" aria-hidden="true">
            <div
              className="bar-fill"
              style={{ width: `${Math.max((item.value / max) * 100, 2)}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}
