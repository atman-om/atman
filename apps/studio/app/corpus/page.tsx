'use client';

import { FormEvent, useEffect, useState } from 'react';
import { apiForm, apiJson } from '../../lib/api';

type Dashboard = {
  sources_total: number;
  files_total: number;
  chunks_total: number;
  pending_source_reviews: number;
  pending_chunk_reviews: number;
  approved_z2_sources: number;
  indexed_sources: number;
  rights_distribution: Record<string, number>;
  ingestion_distribution: Record<string, number>;
};

export default function CorpusPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [status, setStatus] = useState<string>('');

  async function load() {
    const data = await apiJson<Dashboard>('/corpus/dashboard');
    setDashboard(data);
  }

  useEffect(() => { load().catch((err) => setStatus(String(err))); }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus('Uploading and extracting...');
    const form = new FormData(event.currentTarget);
    const result = await apiForm<any>('/corpus/upload', form);
    setStatus(`Uploaded ${result.source.title}; chunks=${result.ingestion_report.chunks_created}`);
    await load();
  }

  return (
    <main>
      <h1>Corpus Ingestion</h1>
      <section className="card">
        <h2>Upload Source</h2>
        <form onSubmit={submit} className="grid">
          <input name="title" placeholder="Title" />
          <input name="language" defaultValue="hi" />
          <select name="rights_status" defaultValue="UNKNOWN">
            <option value="UNKNOWN">UNKNOWN</option>
            <option value="PUBLIC_DOMAIN_VERIFIED">PUBLIC_DOMAIN_VERIFIED</option>
            <option value="OPEN_LICENSE_VERIFIED">OPEN_LICENSE_VERIFIED</option>
            <option value="LICENSED_VERIFIED">LICENSED_VERIFIED</option>
            <option value="USER_OWNED">USER_OWNED</option>
            <option value="REFERENCE_ONLY">REFERENCE_ONLY</option>
            <option value="NO_TRAINING_ALLOWED">NO_TRAINING_ALLOWED</option>
          </select>
          <input name="locator" placeholder="Optional canonical locator e.g. BG.2.47" />
          <input name="tradition_scope" placeholder="Comma-separated scopes" />
          <input name="file" type="file" required />
          <button type="submit">Upload → Extract → Chunk → Index</button>
        </form>
        {status && <p>{status}</p>}
      </section>
      <section className="card">
        <h2>Corpus Dashboard</h2>
        {dashboard ? <pre>{JSON.stringify(dashboard, null, 2)}</pre> : <p>Loading...</p>}
      </section>
    </main>
  );
}
