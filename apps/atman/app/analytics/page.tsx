import { AnalyticsClient } from '../../components/Console';
import { Nav } from '../../components/Nav';

export default async function Page() {
  return <main className="shell"><Nav /><h1>Analytics</h1><AnalyticsClient /></main>;
}
