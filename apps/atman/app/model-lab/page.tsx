import { ModelLabClient } from '../../components/Console';
import { Nav } from '../../components/Nav';

export default async function Page() {
  return <main className="shell"><Nav /><h1>Atman Model Lab</h1><p>Fine-tuning runs in parallel. Remote Qwen remains production until an Atman-Qwen adapter passes gates.</p><ModelLabClient /></main>;
}
