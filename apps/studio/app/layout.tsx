import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'Atman Studio',
  description: 'Source-governed Dharma AI admin dashboard'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="hi">
      <body>{children}</body>
    </html>
  );
}
