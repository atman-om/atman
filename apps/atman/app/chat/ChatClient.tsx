'use client';

import { useState } from 'react';
import { API_BASE } from '../../lib/api';

type Msg = { role: string; content: string; citations?: unknown[]; usage?: unknown };

function consoleHeaders(): HeadersInit {
  try {
    const auth = JSON.parse(window.localStorage.getItem('atman.console.auth') || '{}') as { token?: string; role?: string };
    return {
      'Content-Type': 'application/json',
      'X-Atman-Role': auth.role === 'operator' ? 'operator' : 'admin',
      ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
    };
  } catch {
    return { 'Content-Type': 'application/json', 'X-Atman-Role': 'admin' };
  }
}

export default function ChatClient() {
  const [sessionId, setSessionId] = useState<string>('');
  const [question, setQuestion] = useState('Karma yoga kya hai?');
  const [messages, setMessages] = useState<Msg[]>([]);
  const [citationMode, setCitationMode] = useState<'hidden' | 'source' | 'scholar'>('hidden');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function ensureSession(): Promise<string> {
    if (sessionId) return sessionId;
    const res = await fetch(`${API_BASE}/chat/sessions`, {
      method: 'POST',
      headers: consoleHeaders(),
      body: JSON.stringify({ title: 'Atman Chat', mode: 'simple', language: 'hi', citation_mode: citationMode }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    setSessionId(data.id);
    return data.id;
  }

  async function send() {
    setBusy(true);
    setError('');
    try {
      const sid = await ensureSession();
      setMessages((prev) => [...prev, { role: 'user', content: question }]);
      const res = await fetch(`${API_BASE}/chat/sessions/${sid}/messages`, {
        method: 'POST',
        headers: consoleHeaders(),
        body: JSON.stringify({ message: question, citation_mode: citationMode, top_k: 5 }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: data.assistant_message?.content ?? JSON.stringify(data),
        citations: data.assistant_message?.visible_citations,
        usage: data.assistant_message?.usage,
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat request failed');
    } finally {
      setBusy(false);
    }
  }

  return <div className="grid chat-grid">
    <div className="card"><h2>Chat</h2>
      <div className="chat-form">
        <select value={citationMode} onChange={(event) => setCitationMode(event.target.value as any)}>
          <option value="hidden">Hidden citations</option>
          <option value="source">Source mode</option>
          <option value="scholar">Scholar mode</option>
        </select>
        <textarea rows={5} value={question} onChange={(event) => setQuestion(event.target.value)} />
        <p className="chat-actions"><button disabled={busy} onClick={send}>{busy ? 'Generating...' : 'Ask Atman'}</button><span>Session: <code>{sessionId || 'new'}</code></span></p>
        {error ? <div className="error-box">{error}</div> : null}
      </div>
    </div>
    <div className="card conversation"><h2>Conversation</h2>{messages.length === 0 ? <p className="empty-state">No messages yet.</p> : messages.map((message, index) => <div className="bubble" key={index}><b>{message.role}</b><p>{message.content}</p>{message.citations?.length ? <pre>{JSON.stringify(message.citations, null, 2)}</pre> : null}{message.usage ? <small>{JSON.stringify(message.usage)}</small> : null}</div>)}</div>
  </div>;
}
