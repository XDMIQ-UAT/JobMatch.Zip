import { FEATURES, LEGEND, Feature } from '@/lib/features';

function Group({ title, items }: { title: string; items: Feature[] }) {
  return (
    <div>
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <ul className="space-y-2 list-disc list-inside text-gray-700">
        {items.map((f) => (
          <li key={f.label}>{f.label}</li>
        ))}
      </ul>
    </div>
  );
}

export default function RoadmapPage() {
  const groups = {
    live: FEATURES.filter((f) => f.status === 'live'),
    beta: FEATURES.filter((f) => f.status === 'beta'),
    coming: FEATURES.filter((f) => f.status === 'coming'),
    planned: FEATURES.filter((f) => f.status === 'planned'),
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold mb-6">Roadmap</h1>
      <p className="text-gray-600 mb-6">
        Status legend: {LEGEND.map((l, i) => (
          <span key={l.status} className={l.color}>
            {l.icon} {l.label}{i < LEGEND.length - 1 ? ' · ' : ''}
          </span>
        ))}
      </p>
      <div className="grid md:grid-cols-2 gap-8">
        <Group title="Live" items={groups.live} />
        <Group title="Beta" items={groups.beta} />
        <Group title="Coming" items={groups.coming} />
        <Group title="Planned" items={groups.planned} />
      </div>
      <div className="mt-8 text-sm text-indigo-600">
        <a href="https://github.com/XDM-ZSBW/JobMatch.Zip" target="_blank" rel="noreferrer" className="hover:underline">Contribute on GitHub</a>
      </div>
    </div>
  );
}