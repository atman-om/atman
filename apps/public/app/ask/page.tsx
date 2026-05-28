'use client';

import { useState } from 'react';
import { askAtman, type AskResponse } from '../../lib/api';

export default function AskPage() {
  const [question, setQuestion] = useState('गीता में कर्मयोग का सरल अर्थ क्या है?');
  const [mode, setMode] = useState<'simple' | 'scholar'>('simple');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<AskResponse | null>(null);

  async function submit() {
    setLoading(true); setError(null);
    try { setAnswer(await askAtman(question, mode)); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unknown error'); }
    finally { setLoading(false); }
  }

  return (
    <div className="card">
      <h2>Ask Atman</h2>
      <p>स्रोत-आधारित प्रश्न पूछें। Atman unsupported Sanskrit/citation claims block करेगा।</p>
      <textarea value={question} onChange={(e) => setQuestion(e.target.value)} />
      <div style={{display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap'}}>
        <select value={mode} onChange={(e) => setMode(e.target.value as 'simple' | 'scholar')} style={{maxWidth: 220}}>
          <option value="simple">Simple Hindi</option>
          <option value="scholar">Scholar Mode</option>
        </select>
        <button disabled={loading || question.trim().length < 2} onClick={submit}>{loading ? 'Thinking…' : 'Ask'}</button>
      </div>
      {error && <p style={{color: '#9c1c1c'}}>{error}</p>}
      {answer && <section style={{marginTop: 22}}>
        <h2>Answer</h2>
        <div className="answer">{answer.answer}</div>
        <p>Model: {answer.model_name} · {answer.latency_ms} ms</p>
        <h2>Citations</h2>
        {answer.citations.length === 0 && <p>No verified citations returned.</p>}
        {answer.citations.map((c) => <div className="citation" key={c.chunk_id}>
          <strong>{c.title}</strong><br />
          Locator: {JSON.stringify(c.locator)}<br />
          {c.text_preview}
        </div>)}
        {answer.safety_report.flags.length > 0 && <p>Safety flags: {answer.safety_report.flags.join(', ')}</p>}
      </section>}
    </div>
  );
}
