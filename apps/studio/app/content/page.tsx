'use client';
import { useState } from 'react';
import { Nav } from '../../components/Nav';
import { apiJson } from '../../lib/api';

export default function ContentPage() {
  const [topic, setTopic] = useState('कर्मयोग');
  const [contentType, setContentType] = useState('notes');
  const [quantity, setQuantity] = useState(5);
  const [batch, setBatch] = useState<any>(null);
  const [items, setItems] = useState<any[]>([]);

  async function createAndRunBatch() {
    const created = await apiJson<any>('/content/batches', {
      method: 'POST',
      body: JSON.stringify({ name: `${topic} ${contentType}`, topic, content_type: contentType, quantity, source_required: true })
    });
    const run = await apiJson<any>(`/content/batches/${created.id}/run`, { method: 'POST' });
    setBatch(run);
    const list = await apiJson<any[]>(`/content/items?batch_id=${run.id}`);
    setItems(list);
  }

  return (
    <main className="shell">
      <Nav />
      <h1>Content Factory</h1>
      <div className="card">
        <label>Topic</label><br />
        <input value={topic} onChange={e => setTopic(e.target.value)} />
        <br /><br />
        <label>Content Type</label><br />
        <select value={contentType} onChange={e => setContentType(e.target.value)}>
          <option value="notes">Notes</option><option value="qa">Q&A</option><option value="mcq">MCQ</option><option value="flashcards">Flashcards</option><option value="explainer">Explainer</option><option value="lesson_plan">Lesson Plan</option><option value="article">Article</option><option value="daily_wisdom">Daily Wisdom</option><option value="worksheet">Worksheet</option><option value="shorts_script">Shorts Script</option><option value="social_post">Social Post</option>
        </select>
        <br /><br />
        <label>Quantity</label><br />
        <input type="number" value={quantity} min={1} max={100} onChange={e => setQuantity(Number(e.target.value))} />
        <br /><br /><button onClick={createAndRunBatch}>Create + Run Batch</button>
      </div>
      {batch && <div className="card"><h2>Batch</h2><pre>{JSON.stringify(batch, null, 2)}</pre></div>}
      {items.map(item => <section key={item.id} className="card"><h2>{item.title}</h2><p>Status: {item.review_status}</p><pre>{item.body.slice(0, 1200)}</pre></section>)}
    </main>
  );
}
