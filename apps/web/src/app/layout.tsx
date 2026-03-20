import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  preload: true,
});

export const metadata: Metadata = {
  metadataBase: new URL('https://talentora.ai'),
  title: {
    default: 'Talentora AI — The Bloomberg for the Job Market',
    template: '%s | Talentora AI',
  },
  description:
    'Real-time European job market intelligence. Track 5M+ job offers, benchmark salaries, monitor skill demand and identify hiring trends across 50+ countries.',
  keywords: [
    'job market intelligence',
    'salary benchmarking',
    'skill demand tracking',
    'European job market',
    'HR analytics',
    'recruitment intelligence',
    'labour market data',
    'workforce analytics',
  ],
  authors: [{ name: 'Talentora AI', url: 'https://talentora.ai' }],
  creator: 'Talentora AI',
  publisher: 'Talentora AI',
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
  openGraph: {
    type: 'website',
    locale: 'en_EU',
    url: 'https://talentora.ai',
    siteName: 'Talentora AI',
    title: 'Talentora AI — The Bloomberg for the Job Market',
    description:
      'Real-time European job market intelligence platform. Track 5M+ job offers, benchmark salaries and monitor skill demand across 50+ countries.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Talentora AI — Job Market Intelligence',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Talentora AI — The Bloomberg for the Job Market',
    description:
      'Real-time European job market intelligence. Track 5M+ job offers, benchmark salaries and monitor skill demand.',
    images: ['/og-image.png'],
    creator: '@talentora_ai',
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)',  color: '#0f172a' },
  ],
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
