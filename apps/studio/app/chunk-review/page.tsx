import { apiJson } from '../../lib/api';

type Chunk = { id: string; source_id: string; chunk_order: number; chunk_text: string; quality_score: number; review_status: string; citation_locator: Record<string, unknown> };

export default async function ChunkReviewPage() {
  const chunks = await apiJson<Chunk[]>('/corpus/review/chunks?review_status=REVIEW_PENDING&limit=100');
  return (
    <main>
      <h1>Chunk Review</h1>
      <p>Review chunks before promotion to production-grade RAG/content generation.</p>
      <div className="grid">
        {chunks.map((chunk) => (
          <section className="card" key={chunk.id}>
            <h3>Chunk {chunk.chunk_order}</h3>
            <p><strong>Status:</strong> {chunk.review_status} · <strong>Quality:</strong> {chunk.quality_score}</p>
            <p><strong>Locator:</strong> <code>{JSON.stringify(chunk.citation_locator)}</code></p>
            <pre>{chunk.chunk_text.slice(0, 900)}</pre>
            <p><code>{chunk.id}</code></p>
          </section>
        ))}
      </div>
    </main>
  );
}
