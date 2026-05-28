import { Nav } from '../components/Nav';

export default function HomePage() {
  return (
    <main className="shell">
      <Nav />
      <h1>Atman Studio v2.0</h1>
      <p>Governed Hindi-first Dharma Knowledge OS with Content Factory, canonical corpus, Qwen serving, analytics, and Model Lab.</p>
      <div className="grid">
        <section className="card"><h2>Sources</h2><p>Upload, review, chunk, and index source material.</p></section>
        <section className="card"><h2>RAG</h2><p>Debug retrieval, citations, and source grounding.</p></section>
        <section className="card"><h2>Content Factory</h2><p>Create source-grounded batches for notes, MCQs, flashcards, lessons, and posts.</p></section>
        <section className="card"><h2>Review Queue</h2><p>Approve, reject, or revise generated content before export.</p></section>
      </div>
    </main>
  );
}
