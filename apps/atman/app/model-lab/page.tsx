import { Nav } from '../../components/Nav';
import { getJson } from '../../lib/api';
export default async function Page() {
  const readiness = await getJson('/model-lab/readiness');
  const comparison = await getJson('/model-lab/comparison');
  const experiments = await getJson('/model-lab/experiments');
  return <main className="shell"><Nav /><h1>Atman Model Lab</h1><p>Fine-tuning runs in parallel. Remote Qwen remains production until an Atman-Qwen adapter passes gates.</p><div className="grid"><div className="card"><h2>Readiness</h2><pre>{JSON.stringify(readiness, null, 2)}</pre></div><div className="card"><h2>Comparison</h2><pre>{JSON.stringify(comparison, null, 2)}</pre></div><div className="card"><h2>Experiments</h2><pre>{JSON.stringify(experiments, null, 2)}</pre></div></div></main>;
}
