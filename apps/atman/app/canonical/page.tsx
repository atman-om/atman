import { CanonicalClient } from '../../components/Console';
import { Nav } from '../../components/Nav';

export default async function Page() {
  return <main className="shell"><Nav /><h1>Canonical Library</h1><p>First-source DB: works, passages, locators, and evidence health.</p><CanonicalClient /></main>;
}
