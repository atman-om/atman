import { runtimeStatus } from '../lib/api';

export default async function HomePage() {
  let status: any = null;
  try { status = await runtimeStatus(); } catch { status = null; }
  return (
    <div className="hero">
      <section className="card">
        <div className="badge">Hindi-first · Source-governed · Qwen-ready</div>
        <h1>Atman</h1>
        <p>
          Atman is a Dharma AI platform that answers in simple Hindi from verified sources,
          shows citations, and refuses unsupported shloka or doctrinal claims.
        </p>
        <p><a href="/ask"><button>Ask Atman</button></a></p>
      </section>
      <aside className="card">
        <h2>Runtime</h2>
        <p>Family: {status?.model_family || 'Qwen'}</p>
        <p>Mode: {status?.mode || 'deterministic'}</p>
        <p>Model: {status?.runtime_model || 'Atman-Lab-Qwen-14B-v0.6'}</p>
        <p>Weights bundled: {status?.weights_bundled ? 'Yes' : 'No'}</p>
      </aside>
      <section className="grid" style={{gridColumn: '1 / -1'}}>
        <div className="card"><h2>Ask</h2><p>Question answering with citations and safety checks.</p></div>
        <div className="card"><h2>Sources</h2><p>Only rights-reviewed, citation-addressable corpus should reach production.</p></div>
        <div className="card"><h2>Shloka</h2><p>No fake Sanskrit. Verified source locator required.</p></div>
      </section>
    </div>
  );
}
