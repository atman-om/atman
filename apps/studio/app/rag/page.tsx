'use client';
import { useState } from 'react';
import { Nav } from '../../components/Nav';
import { apiJson } from '../../lib/api';

export default function RagPage() {
  const [question, setQuestion] = useState('गीता 2.47 का अर्थ क्या है?');
  const [result, setResult] = useState<unknown>(null);

  async function ask() {
    const data = await apiJson('/rag/query', { method: 'POST', body: JSON.stringify({ question, top_k: 5, require_citations: true }) });
    setResult(data);
  }

  return (
    <main className="shell">
      <Nav />
      <h1>RAG Debugger</h1>
      <div className="card">
        <textarea rows={4} value={question} onChange={e => setQuestion(e.target.value)} />
        <br /><br /><button onClick={ask}>Ask Atman</button>
      </div>
      {result !== null && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </main>
  );
}
