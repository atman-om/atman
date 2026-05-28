import { apiJson } from '../../lib/api';

type Source = { id: string; title: string; rights_status: string; ingestion_status: string; source_type: string; language?: string };

export default async function SourceReviewPage() {
  const sources = await apiJson<Source[]>('/corpus/review/sources?limit=100');
  return (
    <main>
      <h1>Source Review</h1>
      <p>Promote only rights-reviewed, source-addressable material to Z2 production.</p>
      <table>
        <thead><tr><th>Title</th><th>Type</th><th>Language</th><th>Rights</th><th>Status</th><th>ID</th></tr></thead>
        <tbody>
          {sources.map((source) => (
            <tr key={source.id}>
              <td>{source.title}</td>
              <td>{source.source_type}</td>
              <td>{source.language}</td>
              <td>{source.rights_status}</td>
              <td>{source.ingestion_status}</td>
              <td><code>{source.id}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
