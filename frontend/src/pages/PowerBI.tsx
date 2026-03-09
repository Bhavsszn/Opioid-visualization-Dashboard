export default function PowerBI() {
  const defaultShareUrl =
    "https://app.powerbi.com/links/R61jbPUqrQ?ctid=7e90c06e-a2ea-4a08-9e34-238080872b7e&pbi_source=linkShare";
  const configuredUrl = (import.meta.env.VITE_POWERBI_EMBED_URL as string | undefined)?.trim();
  const embedUrl = configuredUrl || defaultShareUrl;

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <section className="space-y-2">
        <h2 className="text-2xl font-semibold tracking-wide">Power BI Dashboard</h2>
        <p className="text-white/75">
          Embedded enterprise reporting view from Microsoft Power BI.
        </p>
      </section>

      <section className="rounded-2xl border border-cyan-500/20 bg-black/10 p-2 space-y-3">
        <iframe
          title="Power BI Dashboard"
          src={embedUrl}
          className="w-full h-[78vh] rounded-xl"
          allowFullScreen
        />
        <div className="flex items-center justify-between gap-3 px-2 pb-2">
          <p className="text-sm text-white/70">
            If your tenant blocks iframe embedding, open the report directly in Power BI.
          </p>
          <a
            href={embedUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 rounded-md text-sm btn-neon"
          >
            Open in Power BI
          </a>
        </div>
      </section>
    </div>
  );
}
