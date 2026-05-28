import { Nav } from '../../components/Nav';
export default function Page() { return <main className="shell"><Nav /><h1>Ask Atman</h1><div className="card"><p>Use API: <code>POST /canonical/answers/generate</code></p><pre>{`{\n  "question": "कर्म योग क्या है?",\n  "citation_mode": "hidden"\n}`}</pre></div></main>; }
