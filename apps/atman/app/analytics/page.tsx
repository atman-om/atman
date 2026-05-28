import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const data = await getJson('/analytics/overview'); const readiness = await getJson('/analytics/readiness'); return <main className="shell"><Nav /><h1>Analytics</h1><div className="grid"><div className="card"><h2>Overview</h2><pre>{JSON.stringify(data, null, 2)}</pre></div><div className="card"><h2>Readiness</h2><pre>{JSON.stringify(readiness, null, 2)}</pre></div></div></main>; }
