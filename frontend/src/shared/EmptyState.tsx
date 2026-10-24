import { ReactNode } from "react";

type Props = {
  title: string;
  children?: ReactNode;
};

export function EmptyState({ title, children }: Props) {
  return (
    <div className="empty-state">
      <p className="empty-title">{title}</p>
      {children && <p className="empty-body">{children}</p>}
    </div>
  );
}
