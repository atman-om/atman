import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const data = await getJson('/eval/runs'); return <main className="shell"><Nav /><h1>NyayaBench</h1><div className="card"><pre>{JSON.stringify(data, null, 2)}</pre></div></main>; }
