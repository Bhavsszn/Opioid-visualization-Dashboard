export default function PowerBI() {
  const embedUrl = import.meta.env.VITE_POWERBI_EMBED_URL as string | undefined;

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <section className="space-y-2">
        <h2 className="text-2xl font-semibold tracking-wide">Power BI Dashboard</h2>
        <p className="text-white/75">
          Embedded enterprise reporting view from Microsoft Power BI.
        </p>
      </section>

      {!embedUrl ? (
        <section className="rounded-2xl border border-amber-400/30 bg-amber-500/10 p-5 space-y-3">
          <p className="font-semibold">Power BI embed URL is not configured.</p>
          <p className="text-sm text-white/80">
            Set <code>VITE_POWERBI_EMBED_URL</code> in <code>frontend/.env</code> and restart
            the dev server.
          </p>
          <pre className="text-sm bg-black/30 rounded-lg p-3 overflow-auto">
{`VITE_POWERBI_EMBED_URL=https://app.powerbi.com/view?r=YOUR_EMBED_TOKEN`}
          </pre>
        </section>
      ) : (
        <section className="rounded-2xl border border-cyan-500/20 bg-black/10 p-2">
          <iframe
            title="Power BI Dashboard"
            src={embedUrl}
            className="w-full h-[78vh] rounded-xl"
            allowFullScreen
          />
        </section>
      )}
    </div>
  );
}
