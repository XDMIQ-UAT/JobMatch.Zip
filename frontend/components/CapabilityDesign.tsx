/**
 * Capability-First UI Design System
 * Highlights what users CAN do, not credentials
 * Accessible by default (WCAG AAA)
 * Low-bandwidth friendly
 * Mobile-first, responsive, VR-ready
 */

export const designTokens = {
  colors: {
    primary: '#0066cc',
    secondary: '#004499',
    background: '#ffffff',
    text: '#333333',
    border: '#e0e0e0',
  },
  spacing: {
    // Use CSS custom properties for fluid spacing
    xs: 'var(--spacing-xs)',
    sm: 'var(--spacing-sm)',
    md: 'var(--spacing-md)',
    lg: 'var(--spacing-lg)',
    xl: 'var(--spacing-xl)',
    '2xl': 'var(--spacing-2xl)',
  },
  typography: {
    fontFamily: 'system-ui, -apple-system, sans-serif',
    fontSize: {
      xs: 'var(--font-xs)',
      sm: 'var(--font-sm)',
      base: 'var(--font-base)',
      lg: 'var(--font-lg)',
      xl: 'var(--font-xl)',
      '2xl': 'var(--font-2xl)',
      '3xl': 'var(--font-3xl)',
      '4xl': 'var(--font-4xl)',
    },
  },
  containers: {
    sm: 'var(--container-sm)',
    md: 'var(--container-md)',
    lg: 'var(--container-lg)',
    xl: 'var(--container-xl)',
    '2xl': 'var(--container-2xl)',
  },
  vr: {
    safeAreaTop: 'var(--vr-safe-area-inset-top)',
    safeAreaRight: 'var(--vr-safe-area-inset-right)',
    safeAreaBottom: 'var(--vr-safe-area-inset-bottom)',
    safeAreaLeft: 'var(--vr-safe-area-inset-left)',
  },
}

export const capabilityStyles = {
  container: {
    width: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    paddingLeft: designTokens.spacing.md,
    paddingRight: designTokens.spacing.md,
    maxWidth: designTokens.containers.lg,
  },
  containerResponsive: {
    width: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    paddingLeft: designTokens.spacing.md,
    paddingRight: designTokens.spacing.md,
    maxWidth: designTokens.containers['2xl'],
  },
  card: {
    border: `1px solid ${designTokens.colors.border}`,
    borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
    padding: designTokens.spacing.lg,
    marginBottom: designTokens.spacing.md,
    // Responsive card - adapts to container
    containerType: 'inline-size' as const,
  },
  button: {
    backgroundColor: designTokens.colors.primary,
    color: 'white',
    border: 'none',
    padding: `${designTokens.spacing.sm} ${designTokens.spacing.lg}`,
    borderRadius: 'clamp(4px, 0.5vw + 4px, 8px)',
    cursor: 'pointer',
    fontSize: designTokens.typography.fontSize.base,
    // Responsive button text
    whiteSpace: 'nowrap' as const,
    minWidth: 'clamp(80px, 10vw, 120px)',
  },
  grid: {
    display: 'grid',
    gap: designTokens.spacing.md,
    gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 300px), 1fr))',
  },
  flexResponsive: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: designTokens.spacing.md,
  },
}


