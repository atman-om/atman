import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const works = await getJson('/canonical/works'); return <main className="shell"><Nav /><h1>Canonical Library</h1><p>First-source DB: works, editions, passages, locators, evidence.</p><div className="card"><pre>{JSON.stringify(works, null, 2)}</pre></div></main>; }
