import { PageHeader } from "../../components/ui/PageHeader";

export default function PowerBIPage() {
  const defaultShareUrl =
    "https://app.powerbi.com/links/R61jbPUqrQ?ctid=7e90c06e-a2ea-4a08-9e34-238080872b7e&pbi_source=linkShare";
  const configured = (import.meta.env.VITE_POWERBI_EMBED_URL as string | undefined)?.trim();
  const embedUrl = configured || defaultShareUrl;

  return (
    <div className="page-stack">
      <PageHeader
        title="Power BI"
        subtitle="Embedded business intelligence report published from the analytics pipeline"
      />

      <section className="card-block">
        <iframe title="Power BI Dashboard" src={embedUrl} className="powerbi-frame" allowFullScreen />
        <div className="panel-actions">
          <span>If embedding is blocked by tenant policy, open it directly.</span>
          <a href={embedUrl} target="_blank" rel="noreferrer" className="btn">
            Open in Power BI
          </a>
        </div>
      </section>
    </div>
  );
}
