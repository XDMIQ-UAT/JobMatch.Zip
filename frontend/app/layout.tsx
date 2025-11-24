import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://jobmatch.zip'),
  title: {
    default: 'JobMatch.zip - AI Job Matching Platform | Longest First',
    template: '%s | JobMatch.zip'
  },
  description: 'Find the longest-lasting job matches first. AI-powered job matching platform for LLC owners and independent contractors with AI capabilities. Capability-first matching, anonymous identity, zero-knowledge credentialing.',
  keywords: [
    'job matching',
    'longest first',
    'AI job matching',
    'LLC job matching',
    'capability matching',
    'anonymous job search',
    'AI capabilities',
    'longest job matches',
    'job search platform',
    'independent contractor jobs',
    'XDMIQ assessment',
    'capability-first matching'
  ],
  authors: [{ name: 'JobMatch.zip' }],
  creator: 'JobMatch.zip',
  publisher: 'JobMatch.zip',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://jobmatch.zip',
    siteName: 'JobMatch.zip',
    title: 'JobMatch.zip - AI Job Matching Platform | Longest First',
    description: 'Find the longest-lasting job matches first. AI-powered job matching for LLC owners with AI capabilities.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'JobMatch.zip - AI Job Matching Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'JobMatch.zip - AI Job Matching Platform | Longest First',
    description: 'Find the longest-lasting job matches first. AI-powered job matching for LLC owners.',
    images: ['/og-image.png'],
    creator: '@jobmatchzip',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    // Add your verification codes here after setting up Google Search Console
    // google: 'your-google-verification-code',
    // yandex: 'your-yandex-verification-code',
  },
  alternates: {
    canonical: 'https://jobmatch.zip',
  },
  category: 'job matching',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'JobMatch.zip',
    url: 'https://jobmatch.zip',
    description: 'AI-powered job matching platform for LLC owners and independent contractors with AI capabilities. Find the longest-lasting job matches first.',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://jobmatch.zip/matching?q={search_term_string}',
      },
      'query-input': 'required name=search_term_string',
    },
    publisher: {
      '@type': 'Organization',
      name: 'JobMatch.zip',
      url: 'https://jobmatch.zip',
    },
  }

  const jobPostingSchema = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    title: 'AI Job Matching Platform',
    description: 'Find the longest-lasting job matches first. Capability-first matching for LLC owners.',
    employmentType: 'CONTRACTOR',
    jobLocation: {
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressCountry: 'US',
      },
    },
  }

  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="canonical" href="https://jobmatch.zip" />
        <meta name="theme-color" content="#2196f3" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jobPostingSchema) }}
        />
      </head>
      <body>
        {children}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Prevent scroll restoration on page load
              if ('scrollRestoration' in history) {
                history.scrollRestoration = 'manual';
              }
              
              // Prevent auto-scroll to hash on load
              if (window.location.hash) {
                window.addEventListener('load', () => {
                  // Small delay to prevent scroll jump
                  setTimeout(() => {
                    const hash = window.location.hash.substring(1);
                    const element = document.getElementById(hash);
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                  }, 100);
                });
              }
            `,
          }}
        />
      </body>
    </html>
  )
}


