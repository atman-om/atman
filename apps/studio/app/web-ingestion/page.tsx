async function loadData() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/web-to-corpus/jobs`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function Page() {
  const data = await loadData();
  return (
    <section>
      <h1>Web-to-Corpus Intake</h1>
      <p>Atman v1.0 production surface for web-to-corpus intake.</p>
      <div className="card">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </section>
  );
}
