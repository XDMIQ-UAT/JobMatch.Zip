export const metadata = {
  title: 'Privacy Policy | JobMatch',
  description: 'Our commitment to privacy, data handling, and user control.'
}

export default function PrivacyPage() {
  return (
    <main className="container" style={{ padding: '2rem', maxWidth: 900, margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Privacy Policy</h1>
      <p style={{ color: '#555', marginBottom: '1.5rem' }}>
        Last updated: November 22, 2025
      </p>

      <section style={{ display: 'grid', gap: '1rem' }}>
        <p>
          We respect your privacy. This page outlines how JobMatch collects, uses, and protects
          information across our Universal Canvas, assessments, marketplace, and related services.
        </p>

        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>What we collect</h2>
        <ul style={{ paddingLeft: '1.25rem' }}>
          <li>Account info (email/phone/social IDs when you choose to authenticate)</li>
          <li>Usage data (events, diagnostics, crash logs)</li>
          <li>Content you submit (messages, drawings, assessments)</li>
        </ul>

        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>How we use data</h2>
        <ul style={{ paddingLeft: '1.25rem' }}>
          <li>Provide and improve the service (matching, assessments, collaboration)</li>
          <li>Security and fraud prevention</li>
          <li>Analytics and product improvements</li>
        </ul>

        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Your controls</h2>
        <ul style={{ paddingLeft: '1.25rem' }}>
          <li>Access, export, or delete your data via Settings or by contacting support</li>
          <li>Control cookies and local storage in your browser</li>
          <li>Opt in/out of emails and analytics where applicable</li>
        </ul>

        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Contact</h2>
        <p>
          Questions? Contact info@jobmatch.zip
        </p>
      </section>
    </main>
  )
}
