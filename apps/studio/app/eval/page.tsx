async function runPreview() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/eval/run/hardened`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ benchmark_name: 'nyayabench_hardened', model_version: 'Atman-Lab-Qwen-14B-v0.7' }),
    cache: 'no-store',
  });
  if (!res.ok) return null;
  return res.json();
}

export default async function EvalPage() {
  const data = await runPreview();
  return (
    <section>
      <h1>NyayaBench Hardened</h1>
      <p>Deterministic release-gate checks for citation alignment, fake shloka risk, ritual safety, and runtime policy.</p>
      {!data ? <p>Eval API unavailable.</p> : (
        <div className="card">
          <h2>Latest ad-hoc run</h2>
          <pre>{JSON.stringify(data.release_readiness, null, 2)}</pre>
          <h3>Category scores</h3>
          <pre>{JSON.stringify(data.category_scores, null, 2)}</pre>
          <h3>Failures</h3>
          <pre>{JSON.stringify(data.run.hard_failures, null, 2)}</pre>
        </div>
      )}
    </section>
  );
}
