import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/uat/', '/redirect/'],
      },
    ],
    sitemap: 'https://jobmatch.zip/sitemap.xml',
  }
}

