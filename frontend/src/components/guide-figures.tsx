/**
 * Illustrated figures for the Help & Guide. Inline SVG (themeable via CSS vars,
 * crisp at any size, no image files) rather than screenshots — so the guide
 * never goes stale when the UI changes and renders in light and dark alike.
 */

/** Annotated map of the LexMind layout: sidebar, create area, list, top bar. */
export function InterfaceMap() {
  const ink = "var(--brand-ink)";
  const gold = "var(--brand-gold)";
  const surface = "var(--surface)";
  const surface2 = "var(--surface-2)";
  const border = "var(--border)";
  const muted = "var(--muted)";

  const navItems = [8, 32, 56, 80, 104, 128, 160, 184, 208, 232];
  return (
    <svg viewBox="0 0 640 380" className="w-full" role="img" aria-label="LexMind interface map">
      {/* Window */}
      <rect x="6" y="6" width="628" height="368" rx="14" fill={surface} stroke={border} />
      {/* Top bar */}
      <line x1="162" y1="44" x2="634" y2="44" stroke={border} />
      <rect x="176" y="22" width="14" height="14" rx="4" fill={ink} />
      <rect x="196" y="25" width="54" height="8" rx="4" fill={muted} opacity="0.5" />
      <rect x="548" y="23" width="28" height="12" rx="6" fill={surface2} stroke={border} />
      <rect x="584" y="23" width="40" height="12" rx="6" fill={surface2} stroke={border} />

      {/* Sidebar */}
      <path d="M6 20a14 14 0 0 1 14-14h142v368H20A14 14 0 0 1 6 360z" fill={ink} />
      <rect x="22" y="20" width="16" height="16" rx="4" fill={gold} />
      <rect x="46" y="24" width="56" height="8" rx="4" fill="#ffffff" opacity="0.85" />
      {navItems.map((y, i) => {
        const active = i === 3;
        return (
          <g key={y}>
            <rect
              x="18"
              y={54 + y}
              width="128"
              height="18"
              rx="6"
              fill={active ? gold : "#ffffff"}
              opacity={active ? 1 : 0.14}
            />
            <rect x="26" y={60 + y} width="10" height="6" rx="3" fill={active ? "#3a2a06" : "#ffffff"} opacity={active ? 1 : 0.5} />
            <rect x="42" y={60 + y} width={60 - (i % 3) * 8} height="6" rx="3" fill={active ? "#3a2a06" : "#ffffff"} opacity={active ? 1 : 0.5} />
          </g>
        );
      })}

      {/* Main — create card */}
      <rect x="182" y="66" width="434" height="92" rx="10" fill={surface2} stroke={border} />
      <rect x="198" y="80" width="80" height="8" rx="4" fill={muted} opacity="0.6" />
      <rect x="198" y="98" width="300" height="24" rx="6" fill={surface} stroke={border} />
      <rect x="198" y="132" width="120" height="16" rx="5" fill={surface} stroke={border} />
      <rect x="512" y="98" width="88" height="24" rx="6" fill={ink} />

      {/* Main — list card */}
      <rect x="182" y="174" width="434" height="186" rx="10" fill={surface} stroke={border} />
      <rect x="182" y="174" width="434" height="30" rx="10" fill={surface2} />
      {[0, 1, 2, 3].map((r) => (
        <g key={r}>
          <rect x="200" y={220 + r * 34} width="120" height="8" rx="4" fill={muted} opacity="0.55" />
          <rect x="360" y={220 + r * 34} width="70" height="8" rx="4" fill={muted} opacity="0.35" />
          <rect x="470" y={218 + r * 34} width="44" height="12" rx="6" fill={surface2} stroke={border} />
          {r < 3 && <line x1="196" y1={240 + r * 34} x2="602" y2={240 + r * 34} stroke={border} />}
        </g>
      ))}

      {/* Callouts */}
      <Callout x="150" y="150" n={1} gold={gold} />
      <Callout x="300" y="60" n={2} gold={gold} />
      <Callout x="300" y="196" n={3} gold={gold} />
      <Callout x="604" y="18" n={4} gold={gold} />
    </svg>
  );
}

function Callout({ x, y, n, gold }: { x: number; y: number; n: number; gold: string }) {
  return (
    <g>
      <circle cx={x} cy={y} r="11" fill={gold} stroke="#ffffff" strokeWidth="2" />
      <text x={x} y={y + 4} textAnchor="middle" fontSize="12" fontWeight="700" fill="#3a2a06">
        {n}
      </text>
    </g>
  );
}
