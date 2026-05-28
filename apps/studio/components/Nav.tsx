export function Nav() {
  return (
    <nav className="nav">
      <a href="/">Dashboard</a>
      <a href="/sources">Sources</a>
      <a href="/corpus">Corpus</a>
      <a href="/source-review">Source Review</a>
      <a href="/chunk-review">Chunk Review</a>
      <a href="/source-explorer">Source Explorer</a>
      <a href="/canonical">Canonical DB</a>
      <a href="/qwen-serving">Qwen Serving</a>
      <a href="http://localhost:3002">Atman App</a>
      <a href="/web-ingestion">Web Intake</a>
      <a href="/ocr">OCR</a>
      <a href="/rag">RAG Debugger</a>
      <a href="/content">Content Factory</a>
      <a href="/review">Review Queue</a>
      <a href="/exports">Exports</a>
      <a href="/eval">NyayaBench</a>
      <a href="/training">Training</a>
      <a href="/models">Models</a>
      <a href="/ops">Ops</a>
    </nav>
  );
}
