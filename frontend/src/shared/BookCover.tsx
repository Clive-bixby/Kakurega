type Props = {
  title: string;
  coverUrl?: string | null;
  className?: string;
  decorative?: boolean;
};

const GRADIENTS = [
  "linear-gradient(150deg, #2b2a5e 0%, #191a24 55%, #111317 100%)",
  "linear-gradient(150deg, #3a2338 0%, #1d1921 55%, #111317 100%)",
  "linear-gradient(150deg, #1f3348 0%, #161d26 55%, #111317 100%)",
  "linear-gradient(150deg, #2f3323 0%, #191c17 55%, #111317 100%)",
  "linear-gradient(150deg, #2a2f47 0%, #171922 55%, #111317 100%)",
];

function gradientFor(title: string): string {
  let hash = 0;
  for (let index = 0; index < title.length; index += 1) {
    hash = (hash * 31 + title.charCodeAt(index)) % 997;
  }
  return GRADIENTS[hash % GRADIENTS.length];
}

export function BookCover({
  title,
  coverUrl,
  className = "",
  decorative = false,
}: Props) {
  if (coverUrl) {
    return (
      <img
        className={`book-cover ${className}`.trim()}
        src={coverUrl}
        alt={decorative ? "" : `Cover of ${title}`}
        loading="lazy"
      />
    );
  }

  return (
    <div
      className={`book-cover book-cover-fallback ${className}`.trim()}
      style={{ background: gradientFor(title) }}
      aria-hidden="true"
    >
      <span className="cover-mark">Kakurega</span>
      <span className="cover-title">{title}</span>
      <span className="cover-rule" />
    </div>
  );
}
