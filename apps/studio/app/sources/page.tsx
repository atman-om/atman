'use client';
import { useState } from 'react';
import { Nav } from '../../components/Nav';
import { apiJson } from '../../lib/api';

type Source = { id: string; title: string; ingestion_status: string; rights_status: string };

export default function SourcesPage() {
  const [title, setTitle] = useState('Atman Demo Source');
  const [text, setText] = useState('भगवद्गीता 2.47 कर्मयोग का आधार है।');
  const [sources, setSources] = useState<Source[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function createSource() {
    setError(null);
    try {
      await apiJson('/sources', {
        method: 'POST',
        body: JSON.stringify({ source_type: 'text', title, language: 'hi', rights_status: 'USER_OWNED', source_metadata: { locator: 'BG.2.47' }, text })
      });
      const rows = await apiJson<Source[]>('/sources');
      setSources(rows);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <main className="shell">
      <Nav />
      <h1>Source Upload</h1>
      <div className="card">
        <label>Title<input value={title} onChange={e => setTitle(e.target.value)} /></label><br /><br />
        <label>Text<textarea rows={8} value={text} onChange={e => setText(e.target.value)} /></label><br /><br />
        <button onClick={createSource}>Create + Ingest</button>
        {error && <pre>{error}</pre>}
      </div>
      <h2>Recent Sources</h2>
      <section className="grid">{sources.map(s => <div className="card" key={s.id}><div className="label">{s.rights_status}</div><h3>{s.title}</h3><p>{s.ingestion_status}</p><small>{s.id}</small></div>)}</section>
    </main>
  );
}
