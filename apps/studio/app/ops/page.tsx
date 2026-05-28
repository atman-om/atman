async function loadData() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/ops/readiness`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function Page() {
  const data = await loadData();
  return (
    <section>
      <h1>Production Ops</h1>
      <p>Atman v1.0 production surface for production ops.</p>
      <div className="card">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </section>
  );
}
