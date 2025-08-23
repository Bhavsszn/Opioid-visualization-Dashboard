export default function Footer() {
  return (
    <footer className="mt-12 border-t border-cyan-500/20 pt-6 text-sm text-center text-white/70">
      <p>© 2025 Bhavya Sharma — All rights reserved.</p>
      <p className="mt-1">
        Data sources:{" "}
        <a
          href="https://wonder.cdc.gov/mcd.html"
          target="_blank"
          rel="noopener noreferrer"
          className="text-cyan-300 underline"
        >
          CDC WONDER
        </a>{" "}
        &{" "}
        <a
          href="https://www.census.gov/data.html"
          target="_blank"
          rel="noopener noreferrer"
          className="text-cyan-300 underline"
        >
          U.S. Census Bureau
        </a>{" "}
        (public domain)
      </p>
    </footer>
  );
}
