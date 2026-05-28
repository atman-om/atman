async function loadData() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'}/training/checkpoints`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function Page() {
  const data = await loadData();
  return (
    <section>
      <h1>Qwen Training</h1>
      <p>Atman v1.0 production surface for qwen training.</p>
      <div className="card">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </section>
  );
}
