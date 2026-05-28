import { AccountsClient } from '../../components/Console';
import { Nav } from '../../components/Nav';

export default async function Page() {
  return <main className="shell"><Nav /><h1>Accounts &amp; Roles</h1><AccountsClient /></main>;
}
