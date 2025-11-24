import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://jobmatch.zip'
  
  // Core pages
  const routes = [
    '',
    '/assessment',
    '/matching',
    '/articulation',
    '/forums',
    '/xdmiq',
    '/auth',
    '/marketplace',
    '/canvas',
    '/recover',
  ]

  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: route === '' ? 'daily' : 'weekly',
    priority: route === '' ? 1.0 : 0.8,
  }))
}

