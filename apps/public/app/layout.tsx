import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Atman — Hindi-first source-governed Dharma AI',
  description: 'Ask source-backed Dharma questions in simple Hindi.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="hi">
      <body>
        <main className="shell">
          <nav className="nav">
            <a className="brand" href="/">Atman</a>
            <div className="navlinks">
              <a href="/ask">Ask</a>
              <a href="/sources">Sources</a>
              <a href="/source-explorer">Source Explorer</a>
              <a href="/shloka">Shloka</a>
            </div>
          </nav>
          {children}
          <div className="footer">Atman v2.0 · Dharma Knowledge OS · Model Lab enabled</div>
        </main>
      </body>
    </html>
  );
}
