async function getSource(sourceId: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'}/public/source-explorer/sources/${sourceId}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function SourceDetailPage({ params }: { params: Promise<{ sourceId: string }> }) {
  const { sourceId } = await params;
  const data = await getSource(sourceId);
  if (!data) return <section className="card"><h1>Source not found</h1><p>This source is not public or does not exist.</p></section>;
  return (
    <section className="card">
      <a href="/source-explorer">← Back</a>
      <h1>{data.source.title}</h1>
      <p>{data.source.source_type} · {data.source.language || 'unknown'} · {data.source.rights_status}</p>
      <div className="mini-card">
        <strong>Allowed uses</strong>
        <pre>{JSON.stringify(data.rights_explanation.allowed_uses, null, 2)}</pre>
      </div>
      <h2>Chunks</h2>
      {data.chunks.map((chunk: any) => (
        <article className="mini-card" key={chunk.id}>
          <strong>{chunk.citation_locator?.locator || `Chunk ${chunk.chunk_order}`}</strong>
          <p>{chunk.chunk_text}</p>
        </article>
      ))}
    </section>
  );
}
