/**
 * Structured Data Component for SEO
 * Adds JSON-LD structured data to pages for better search engine understanding
 */

interface StructuredDataProps {
  type: 'WebSite' | 'JobPosting' | 'Organization' | 'BreadcrumbList'
  data: Record<string, any>
}

export default function StructuredData({ type, data }: StructuredDataProps) {
  const baseSchema = {
    '@context': 'https://schema.org',
    '@type': type,
    ...data,
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(baseSchema) }}
    />
  )
}

