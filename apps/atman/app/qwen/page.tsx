import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const profiles = await getJson('/qwen/serving/profiles'); const status = await getJson('/qwen/serving/status'); return <main className="shell"><Nav /><h1>Qwen Serving</h1><div className="grid"><div className="card"><h2>Status</h2><pre>{JSON.stringify(status, null, 2)}</pre></div><div className="card"><h2>Profiles</h2><pre>{JSON.stringify(profiles, null, 2)}</pre></div></div></main>; }
