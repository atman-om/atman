export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export type Citation = {
  chunk_id: string;
  source_id: string;
  title: string;
  locator: Record<string, unknown>;
  score: number;
  text_preview: string;
};

export type AskResponse = {
  answer: string;
  citations: Citation[];
  safety_report: { allowed: boolean; flags: string[]; reason?: string | null };
  model_name: string;
  latency_ms: number;
  ui_hints: Record<string, unknown>;
};

export async function askAtman(question: string, mode: 'simple' | 'scholar' = 'simple'): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/public/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, language: 'hi', top_k: 5, mode }),
    cache: 'no-store',
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Atman API failed: ${res.status} ${detail}`);
  }
  return res.json();
}

export async function runtimeStatus() {
  const res = await fetch(`${API_BASE}/runtime/status`, { cache: 'no-store' });
  if (!res.ok) throw new Error('runtime status failed');
  return res.json();
}
