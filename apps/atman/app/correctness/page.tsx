import { Nav } from '../../components/Nav';
export default function Page() { return <main className="shell"><Nav /><h1>Correctness Engine</h1><div className="card"><p>Use <code>POST /correctness/claims/check</code> to grade claims against candidate evidence.</p><pre>{`{
  "claim": "गीता 2.47 में कर्म पर अधिकार बताया गया है",
  "candidate_evidence": [{"text":"कर्मण्येवाधिकारस्ते...", "authority_level":"A", "locator":"BG.2.47"}],
  "strictness":"normal",
  "public_answer":true
}`}</pre></div></main>; }
