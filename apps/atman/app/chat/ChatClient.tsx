'use client';
import { useState } from 'react';
import { API_BASE } from '../../lib/api';

type Msg = { role: string; content: string; citations?: unknown[]; usage?: unknown };

export default function ChatClient() {
  const [sessionId, setSessionId] = useState<string>('');
  const [question, setQuestion] = useState('कर्म योग क्या है?');
  const [messages, setMessages] = useState<Msg[]>([]);
  const [citationMode, setCitationMode] = useState<'hidden'|'source'|'scholar'>('hidden');
  const [busy, setBusy] = useState(false);

  async function ensureSession(): Promise<string> {
    if (sessionId) return sessionId;
    const res = await fetch(`${API_BASE}/chat/sessions`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: 'Atman Chat', mode: 'simple', language: 'hi', citation_mode: citationMode }) });
    const data = await res.json();
    setSessionId(data.id);
    return data.id;
  }

  async function send() {
    setBusy(true);
    try {
      const sid = await ensureSession();
      setMessages(prev => [...prev, { role: 'user', content: question }]);
      const res = await fetch(`${API_BASE}/chat/sessions/${sid}/messages`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: question, citation_mode: citationMode, top_k: 5 }) });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.assistant_message?.content ?? JSON.stringify(data), citations: data.assistant_message?.visible_citations, usage: data.assistant_message?.usage }]);
    } finally { setBusy(false); }
  }

  return <div className="grid">
    <div className="card"><h2>Chat</h2>
      <select value={citationMode} onChange={(e) => setCitationMode(e.target.value as any)}><option value="hidden">Hidden citations</option><option value="source">Source mode</option><option value="scholar">Scholar mode</option></select>
      <textarea rows={5} value={question} onChange={(e) => setQuestion(e.target.value)} />
      <p><button disabled={busy} onClick={send}>{busy ? 'Generating…' : 'Ask Atman'}</button></p>
      <p>Session: <code>{sessionId || 'new'}</code></p>
    </div>
    <div className="card"><h2>Conversation</h2>{messages.map((m, i) => <div className="bubble" key={i}><b>{m.role}</b><p>{m.content}</p>{m.citations?.length ? <pre>{JSON.stringify(m.citations, null, 2)}</pre> : null}{m.usage ? <small>{JSON.stringify(m.usage)}</small> : null}</div>)}</div>
  </div>;
}
