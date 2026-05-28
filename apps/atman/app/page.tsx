import { Nav } from '../components/Nav';
import { getJson } from '../lib/api';

export default async function Page() {
  const os = await getJson<Record<string, unknown>>('/os/status');
  const modelLab = await getJson<Record<string, unknown>>('/model-lab/readiness');
  const analytics = await getJson<Record<string, unknown>>('/analytics/overview');
  const readiness = await getJson<Record<string, unknown>>('/analytics/readiness');
  return <main className="shell"><Nav />
    <section className="hero">
      <span className="badge">Atman v2.0</span>
      <h1>Dharma Knowledge OS with parallel Model Lab</h1>
      <p>Remote-Qwen live chatbot, ShrutiKosh canonical library, learning paths, content studio, correctness engine, analytics, and Qwen fine-tuning R&amp;D lane running in parallel.</p>
    </section>
    <section className="grid">
      <div className="card"><h2>Knowledge OS</h2><pre>{JSON.stringify(os, null, 2)}</pre></div>
      <div className="card"><h2>Model Lab Readiness</h2><pre>{JSON.stringify(modelLab, null, 2)}</pre></div>
      <div className="card"><h2>Product Readiness</h2><pre>{JSON.stringify(readiness, null, 2)}</pre></div>
      <div className="card"><h2>Analytics</h2><pre>{JSON.stringify(analytics, null, 2)}</pre></div>
    </section>
  </main>;
}
