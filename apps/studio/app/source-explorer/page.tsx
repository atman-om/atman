async function search() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/source-explorer/search?limit=50`, { cache: 'no-store' });
  if (!res.ok) return { sources: [], chunks: [], total: 0 };
  return res.json();
}

export default async function StudioSourceExplorerPage() {
  const data = await search();
  return (
    <section>
      <h1>Source Explorer</h1>
      <p>Admin explorer can inspect all corpus sources, including review-pending sources.</p>
      <div className="card">
        <h2>Sources ({data.total})</h2>
        {data.sources.map((src: any) => (
          <div className="row" key={src.id}>
            <strong>{src.title}</strong>
            <span>{src.rights_status} · {src.ingestion_status} · chunks {src.chunk_count}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
