export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const helpText = message.includes("Backend unavailable")
    ? "Check backend server and VITE_API_BASE."
    : message.includes("Static asset")
      ? "Check VITE_USE_STATIC and generated files under public/api."
      : null;

  return (
    <div className="state-box state-error" role="alert">
      <p>{message}</p>
      {helpText ? <p className="state-description">{helpText}</p> : null}
      {onRetry ? (
        <button className="btn" type="button" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}
