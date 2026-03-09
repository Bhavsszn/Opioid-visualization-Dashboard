import React from "react";

export const LoadingSpinner = React.memo(function LoadingSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="loading-wrap" role="status" aria-live="polite">
      <span className="loading-spinner" />
      <span>{label}</span>
    </div>
  );
});
