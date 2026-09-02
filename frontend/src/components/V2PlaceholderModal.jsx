function FeatureIcon({ feature }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="modal-feature-logo">
      {feature === 'Learn' && <>
        <path d="m4 8 8-4 8 4-8 4-8-4Z" />
        <path d="M7 10v5c2.7 2.4 7.3 2.4 10 0v-5M20 8v7" />
      </>}
      {feature === 'Contest' && <>
        <path d="M8 4h8v4a4 4 0 0 1-8 0V4Z" />
        <path d="M8 6H5v1a3 3 0 0 0 3 3M16 6h3v1a3 3 0 0 1-3 3M12 12v4M8 20h8M9 16h6" />
      </>}
      {feature === 'Forum' && <>
        <path d="M5 5h14v10H9l-4 4V5Z" />
        <path d="M8 9h8M8 12h5" />
      </>}
      {feature === 'Profile' && <>
        <circle cx="12" cy="8" r="3.5" />
        <path d="M5 20c.7-3.5 3.1-5.5 7-5.5s6.3 2 7 5.5" />
      </>}
    </svg>
  )
}

function WorkProgressIllustration() {
  return (
    <svg viewBox="0 0 180 110" aria-hidden="true" className="work-progress-illustration">
      <defs>
        <clipPath id="roadwork-board">
          <rect x="30" y="35" width="102" height="30" rx="2" />
        </clipPath>
      </defs>
      <path d="M22 88h136" />
      <path d="M30 35h102v30H30z" />
      <g clipPath="url(#roadwork-board)">
        <path d="m24 64 32-34M46 70l32-34M68 70l32-34M90 70l32-34M112 70l32-34" />
      </g>
      <path d="M45 65v23M117 65v23M37 88h16M109 88h16" />
      <path d="m139 88 10-29 10 29M143 77h12M146 68h6" />
    </svg>
  )
}

export function V2PlaceholderModal({ feature, onClose, titleId = 'v2-title', theme = 'default' }) {
  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section className={`modal${theme === 'auth' ? ' modal-auth' : ''}`} role="dialog" aria-modal="true" aria-labelledby={titleId} onClick={(event) => event.stopPropagation()}>
        {['Learn', 'Contest', 'Forum', 'Profile'].includes(feature) && <FeatureIcon feature={feature} />}
        <h2 id={titleId}>{feature}</h2>
        <p className="muted">Arriving in V2</p>
        <WorkProgressIllustration />
        <button type="button" className="primary-button" onClick={onClose}>Close</button>
      </section>
    </div>
  )
}
