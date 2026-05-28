import { QwenClient } from '../../components/Console';
import { Nav } from '../../components/Nav';

export default async function Page() {
  return <main className="shell"><Nav /><h1>Qwen Serving</h1><QwenClient /></main>;
}
