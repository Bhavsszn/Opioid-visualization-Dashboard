export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="state-box">
      <p className="state-title">{title}</p>
      {description ? <p className="state-description">{description}</p> : null}
    </div>
  );
}
