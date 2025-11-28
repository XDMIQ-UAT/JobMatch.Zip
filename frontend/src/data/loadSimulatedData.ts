/**
 * Load simulated opportunities and profiles data
 */

export interface Opportunity {
  id: string
  title: string
  company: string
  location: string
  isRemote: boolean
  description: string
  skills: string[]
  requirements: string[]
  salaryMin: number
  salaryMax: number
  employmentType: string
  postedDate: string
  createdAt: string
  isActive: boolean
  field: string
}

export interface CandidateProfile {
  id: string
  anonymousId: string
  skills: string[]
  location: string
  summary: string
  experience: Array<{
    title: string
    company: string
    duration: string
    description: string
  }>
  education: Array<{
    degree: string
    field: string
    year: string
  }>
  yearsExperience: number
  field: string
  preferences: {
    workType: string
    salaryMin: number
    employmentType: string
  }
  createdAt: string
}

let opportunitiesCache: Opportunity[] | null = null
let profilesCache: CandidateProfile[] | null = null

export async function loadOpportunities(): Promise<Opportunity[]> {
  if (opportunitiesCache) {
    return opportunitiesCache
  }

  try {
    const response = await fetch('/data/simulated_opportunities.json')
    if (!response.ok) {
      throw new Error('Failed to load opportunities')
    }
    const data = await response.json()
    opportunitiesCache = data
    return data
  } catch (error) {
    console.error('Error loading opportunities:', error)
    // Return empty array if file doesn't exist
    return []
  }
}

export async function loadProfiles(): Promise<CandidateProfile[]> {
  if (profilesCache) {
    return profilesCache
  }

  try {
    const response = await fetch('/data/simulated_profiles.json')
    if (!response.ok) {
      throw new Error('Failed to load profiles')
    }
    const data = await response.json()
    profilesCache = data
    return data
  } catch (error) {
    console.error('Error loading profiles:', error)
    // Return empty array if file doesn't exist
    return []
  }
}

/**
 * Calculate match score between a profile and opportunity
 */
export function calculateMatchScore(
  profile: CandidateProfile,
  opportunity: Opportunity
): number {
  // Skill overlap (0-60 points)
  const profileSkills = new Set(profile.skills.map(s => s.toLowerCase()))
  const oppSkills = new Set(opportunity.skills.map(s => s.toLowerCase()))
  const commonSkills = [...profileSkills].filter(s => oppSkills.has(s))
  const skillScore = Math.min(60, (commonSkills.length / Math.max(oppSkills.size, 1)) * 60)

  // Field match (0-20 points)
  const fieldScore = profile.field === opportunity.field ? 20 : 10

  // Location preference (0-10 points)
  let locationScore = 5 // Default
  if (opportunity.isRemote && profile.preferences.workType === 'remote') {
    locationScore = 10
  } else if (!opportunity.isRemote && profile.preferences.workType === 'onsite') {
    locationScore = 8
  } else if (opportunity.location.includes('Remote') && profile.preferences.workType === 'remote') {
    locationScore = 10
  }

  // Salary expectation (0-10 points)
  let salaryScore = 5
  if (profile.preferences.salaryMin <= opportunity.salaryMax) {
    const overlap = Math.max(0, opportunity.salaryMax - profile.preferences.salaryMin)
    const range = opportunity.salaryMax - opportunity.salaryMin
    salaryScore = Math.min(10, 5 + (overlap / range) * 5)
  }

  const totalScore = Math.round(skillScore + fieldScore + locationScore + salaryScore)
  return Math.min(100, Math.max(0, totalScore))
}

