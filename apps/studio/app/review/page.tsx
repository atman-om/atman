'use client';
import { useEffect, useState } from 'react';
import { Nav } from '../../components/Nav';
import { apiJson } from '../../lib/api';

export default function ReviewPage() {
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState('REVIEW_PENDING');

  async function load() {
    const list = await apiJson<any[]>(`/content/items?review_status=${status}&limit=100`);
    setItems(list);
  }

  async function decide(id: string, decision: string) {
    await apiJson(`/content/items/${id}/review`, { method: 'POST', body: JSON.stringify({ decision, reason: `Studio decision: ${decision}` }) });
    await load();
  }

  useEffect(() => { load(); }, [status]);

  return (
    <main className="shell">
      <Nav />
      <h1>Review Queue</h1>
      <div className="card">
        <select value={status} onChange={e => setStatus(e.target.value)}>
          <option value="REVIEW_PENDING">Review Pending</option>
          <option value="NEEDS_REVISION">Needs Revision</option>
          <option value="AUTO_BLOCKED">Auto Blocked</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </select>
        <button onClick={load}>Refresh</button>
      </div>
      {items.map(item => <section key={item.id} className="card"><h2>{item.title}</h2><p>Score: {item.quality_report?.score} | Flags: {(item.quality_report?.flags ?? []).join(', ')}</p><pre>{item.body.slice(0, 1000)}</pre><button onClick={() => decide(item.id, 'APPROVED')}>Approve</button> <button onClick={() => decide(item.id, 'NEEDS_REVISION')}>Needs Revision</button> <button onClick={() => decide(item.id, 'REJECTED')}>Reject</button></section>)}
    </main>
  );
}
