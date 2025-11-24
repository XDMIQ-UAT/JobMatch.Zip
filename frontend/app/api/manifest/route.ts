import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

// Embedded manifest content - always available
const manifest = {
  name: "JobMatch.zip - AI Job Matching Platform",
  short_name: "JobMatch",
  description: "AI-powered job matching platform for LLC owners and independent contractors with AI capabilities. Find the longest-lasting job matches first.",
  start_url: "/",
  display: "standalone",
  background_color: "#ffffff",
  theme_color: "#2196f3",
  icons: [
    {
      src: "/icon.svg",
      sizes: "any",
      type: "image/svg+xml",
      purpose: "any maskable"
    },
    {
      src: "/icon-192.png",
      sizes: "192x192",
      type: "image/png"
    },
    {
      src: "/icon-512.png",
      sizes: "512x512",
      type: "image/png"
    }
  ],
  orientation: "any",
  categories: ["business", "productivity"],
  shortcuts: [
    {
      name: "Start Chat",
      short_name: "Chat",
      description: "Chat with JobMatch assistant",
      url: "/",
      icons: [{ src: "/icon.svg", sizes: "any" }]
    },
    {
      name: "Universal Canvas",
      short_name: "Canvas",
      description: "Create a new canvas",
      url: "/canvas?new=true",
      icons: [{ src: "/icon.svg", sizes: "any" }]
    }
  ]
}

export async function GET() {
  return NextResponse.json(manifest, {
    headers: {
      'Content-Type': 'application/manifest+json',
      'Cache-Control': 'public, max-age=3600, must-revalidate',
    },
  })
}

