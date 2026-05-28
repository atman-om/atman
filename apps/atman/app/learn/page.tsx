import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const paths = await getJson('/learning/paths'); const defaults = await getJson('/learning/default-paths'); return <main className="shell"><Nav /><h1>Learn</h1><p>Structured Hindi-first learning paths built on the canonical corpus.</p><div className="grid"><div className="card"><h2>Saved Paths</h2><pre>{JSON.stringify(paths, null, 2)}</pre></div><div className="card"><h2>Default Paths</h2><pre>{JSON.stringify(defaults, null, 2)}</pre></div></div></main>; }
