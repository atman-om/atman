import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const channels = await getJson('/publishing/channels'); const items = await getJson('/publishing/items'); return <main className="shell"><Nav /><h1>Publishing</h1><p>Manage approved content into manual/web/social/PWA publishing queues.</p><div className="grid"><div className="card"><h2>Channels</h2><pre>{JSON.stringify(channels, null, 2)}</pre></div><div className="card"><h2>Items</h2><pre>{JSON.stringify(items, null, 2)}</pre></div></div></main>; }
