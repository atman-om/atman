import { API_BASE } from '../../lib/api';

export default async function SourcesPage() {
  let sources: any[] = [];
  try {
    const res = await fetch(`${API_BASE}/public/sources`, { cache: 'no-store' });
    if (res.ok) sources = await res.json();
  } catch {}
  return (
    <div className="card">
      <h2>Verified Sources</h2>
      <p>Public view only shows rights-reviewed source records eligible for user-facing retrieval.</p>
      {sources.length === 0 && <p>No public sources yet. Seed/review corpus in Atman Studio first.</p>}
      {sources.map((s) => <div className="citation" key={s.id}>
        <strong>{s.title}</strong><br />
        Rights: {s.rights_status} · Status: {s.ingestion_status} · Language: {s.language || 'unknown'}
      </div>)}
    </div>
  );
}
