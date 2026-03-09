export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="state-box state-error" role="alert">
      <p>{message}</p>
      {onRetry ? (
        <button className="btn" type="button" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}
