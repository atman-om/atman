import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const jobs = await getJson('/acquisition/jobs'); return <main className="shell"><Nav /><h1>Wide Corpus Acquisition</h1><p>Scrape/discover broadly, quarantine first, verify before canonical use.</p><div className="card"><pre>{JSON.stringify(jobs, null, 2)}</pre></div></main>; }
