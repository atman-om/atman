import { DashboardClient } from '../components/Console';
import { Nav } from '../components/Nav';

export default async function Page() {
  return <main className="shell"><Nav /><DashboardClient /></main>;
}
