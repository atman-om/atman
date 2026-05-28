import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() { const me = await getJson('/accounts/me'); const users = await getJson('/accounts/users'); return <main className="shell"><Nav /><h1>Accounts & Roles</h1><div className="grid"><div className="card"><h2>Current Demo User</h2><pre>{JSON.stringify(me, null, 2)}</pre></div><div className="card"><h2>Users</h2><pre>{JSON.stringify(users, null, 2)}</pre></div></div></main>; }
