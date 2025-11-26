export type FeatureStatus = 'live' | 'beta' | 'coming' | 'planned';
export type Feature = { label: string; status: FeatureStatus };

export const FEATURES: Feature[] = [
  { label: 'AI-powered job matching with verified employers', status: 'live' },
  { label: 'Direct messaging with hiring managers', status: 'beta' },
  { label: 'Real-time application tracking', status: 'coming' },
  { label: 'Interview preparation & coaching', status: 'planned' },
  { label: 'Career insights & salary analytics', status: 'planned' },
];

export const LEGEND = [
  { status: 'live' as FeatureStatus, label: 'Live', icon: '✅', color: 'text-green-600' },
  { status: 'beta' as FeatureStatus, label: 'Beta', icon: '🧪', color: 'text-amber-500' },
  { status: 'coming' as FeatureStatus, label: 'Coming', icon: '🕒', color: 'text-gray-500' },
  { status: 'planned' as FeatureStatus, label: 'Planned', icon: '◌', color: 'text-gray-500' },
];