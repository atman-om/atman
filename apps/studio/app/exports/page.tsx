'use client';
import { useEffect, useState } from 'react';
import { Nav } from '../../components/Nav';
import { apiJson, API_BASE } from '../../lib/api';

export default function ExportsPage() {
  const [format, setFormat] = useState('jsonl');
  const [exportsList, setExportsList] = useState<any[]>([]);

  async function load() { setExportsList(await apiJson<any[]>('/content/exports')); }
  async function createExport() {
    await apiJson('/content/exports', { method: 'POST', body: JSON.stringify({ export_format: format, review_status: 'APPROVED' }) });
    await load();
  }
  useEffect(() => { load(); }, []);

  return (
    <main className="shell">
      <Nav />
      <h1>Exports</h1>
      <div className="card"><select value={format} onChange={e => setFormat(e.target.value)}><option value="jsonl">JSONL</option><option value="markdown">Markdown</option><option value="csv">CSV</option></select> <button onClick={createExport}>Export Approved Content</button></div>
      {exportsList.map(ex => <section key={ex.id} className="card"><h2>{ex.export_format} export</h2><p>Items: {ex.item_count}</p><p>{ex.file_path}</p><a href={`${API_BASE}/content/exports/${ex.id}/download`}>Download</a></section>)}
    </main>
  );
}
