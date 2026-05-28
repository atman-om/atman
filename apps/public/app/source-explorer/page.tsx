async function searchSources(q = '') {
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  params.set('limit', '25');
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/public/source-explorer/search?${params}`, { cache: 'no-store' });
  if (!res.ok) return { query: q, total: 0, sources: [], chunks: [], filters: {} };
  return res.json();
}

export default async function SourceExplorerPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const resolvedSearchParams = await searchParams;
  const q = resolvedSearchParams?.q || '';
  const data = await searchSources(q);
  return (
    <section className="card">
      <h1>Source Explorer</h1>
      <p>Only rights-cleared, production-approved sources are visible here.</p>
      <form action="/source-explorer" className="row">
        <input name="q" defaultValue={q} placeholder="कर्म, ज्ञान, BG.2.47..." />
        <button type="submit">Search</button>
      </form>
      <div className="grid">
        <div>
          <h2>Sources ({data.total})</h2>
          {data.sources.map((src: any) => (
            <a className="mini-card" key={src.id} href={`/source-explorer/${src.id}`}>
              <strong>{src.title}</strong>
              <span>{src.language || 'unknown'} · {src.rights_status} · chunks {src.chunk_count}</span>
            </a>
          ))}
        </div>
        <div>
          <h2>Matched chunks</h2>
          {data.chunks.map((chunk: any) => (
            <div className="mini-card" key={chunk.id}>
              <strong>{chunk.citation_locator?.locator || `Chunk ${chunk.chunk_order}`}</strong>
              <p>{chunk.highlight || chunk.chunk_text.slice(0, 220)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
