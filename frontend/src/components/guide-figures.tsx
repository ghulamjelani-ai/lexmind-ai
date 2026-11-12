/**
 * Illustrated figures for the Help & Guide. Inline SVG (themeable via CSS vars,
 * crisp at any size, no image files) rather than screenshots — so the guide
 * never goes stale when the UI changes and renders in light and dark alike.
 * Labelled to mirror the real LexMind screen so it reads like the actual app.
 */

const NAV = [
  { label: "Dashboard", group: "WORKSPACE" },
  { label: "Intake" },
  { label: "Cases", active: true },
  { label: "Clients" },
  { label: "Documents" },
  { label: "AI Assistant", group: "INTELLIGENCE" },
  { label: "Legal Library" },
  { label: "Tax" },
  { label: "Reports" },
];

const ROWS = [
  ["Bail application — State vs Khan", "Bail", "Open"],
  ["Property dispute — Ali vs Ahmed", "Civil", "In hearing"],
  ["Recovery suit — Khan & Co", "Banking", "Pending"],
];

/** A labelled map of the LexMind screen: sidebar, create area, list, top bar. */
export function InterfaceMap() {
  const ink = "var(--brand-ink)";
  const gold = "var(--brand-gold)";
  const surface = "var(--surface)";
  const surface2 = "var(--surface-2)";
  const border = "var(--border)";
  const text = "var(--text)";
  const muted = "var(--muted)";

  let y = 86;
  const nav: { label: string; active?: boolean; group?: string; y: number }[] = [];
  for (const item of NAV) {
    if (item.group) y += 16;
    nav.push({ ...item, y });
    y += 30;
  }

  return (
    <svg viewBox="0 0 640 410" className="w-full" role="img" aria-label="LexMind interface map" style={{ fontFamily: "var(--font-inter), system-ui, sans-serif" }}>
      {/* Window */}
      <rect x="6" y="6" width="628" height="398" rx="14" fill={surface} stroke={border} />

      {/* Top bar */}
      <line x1="178" y1="46" x2="634" y2="46" stroke={border} />
      <text x="196" y="30" fontSize="10" fill={muted}>Signed in as QA Tester</text>
      <rect x="548" y="20" width="26" height="14" rx="7" fill={surface2} stroke={border} />
      <rect x="582" y="20" width="44" height="14" rx="7" fill={surface2} stroke={border} />
      <text x="604" y="30" fontSize="8" fill={muted} textAnchor="middle">Sign out</text>

      {/* Sidebar */}
      <path d="M6 20a14 14 0 0 1 14-14h158v398H20A14 14 0 0 1 6 390z" fill={ink} />
      <rect x="22" y="22" width="16" height="16" rx="4" fill={gold} />
      <text x="46" y="34" fontSize="12" fontWeight="700" fill="#ffffff">LexMind</text>

      {nav.map((item) => (
        <g key={item.label}>
          {item.group && (
            <text x="24" y={item.y - 8} fontSize="7.5" letterSpacing="1" fill="#ffffff" opacity="0.4">
              {item.group}
            </text>
          )}
          <rect
            x="18"
            y={item.y}
            width="146"
            height="22"
            rx="7"
            fill={item.active ? gold : "#ffffff"}
            opacity={item.active ? 1 : 0.07}
          />
          <circle cx="32" cy={item.y + 11} r="3.5" fill={item.active ? "#3a2a06" : "#ffffff"} opacity={item.active ? 1 : 0.6} />
          <text x="44" y={item.y + 15} fontSize="10" fontWeight={item.active ? 700 : 500} fill={item.active ? "#3a2a06" : "#ffffff"} opacity={item.active ? 1 : 0.85}>
            {item.label}
          </text>
        </g>
      ))}

      {/* Main — create card */}
      <rect x="198" y="68" width="420" height="92" rx="10" fill={surface2} stroke={border} />
      <text x="214" y="88" fontSize="8.5" letterSpacing="1" fill={muted}>CREATE A CASE</text>
      <rect x="214" y="98" width="286" height="26" rx="6" fill={surface} stroke={border} />
      <text x="224" y="115" fontSize="9" fill={muted} opacity="0.8">e.g. Bail application — State vs Khan</text>
      <rect x="512" y="98" width="92" height="26" rx="6" fill={ink} />
      <text x="558" y="115" fontSize="9" fontWeight="600" fill="#ffffff" textAnchor="middle">Create case</text>
      <rect x="214" y="132" width="120" height="16" rx="5" fill={surface} stroke={border} />
      <text x="224" y="143" fontSize="8" fill={muted}>Category ▾</text>

      {/* Main — list card */}
      <rect x="198" y="176" width="420" height="214" rx="10" fill={surface} stroke={border} />
      <rect x="198" y="176" width="420" height="30" rx="10" fill={surface2} />
      <text x="214" y="195" fontSize="8" letterSpacing="0.5" fill={muted}>TITLE</text>
      <text x="420" y="195" fontSize="8" letterSpacing="0.5" fill={muted}>CATEGORY</text>
      <text x="520" y="195" fontSize="8" letterSpacing="0.5" fill={muted}>STATUS</text>
      {ROWS.map((r, i) => {
        const ry = 226 + i * 40;
        return (
          <g key={i}>
            <text x="214" y={ry} fontSize="9.5" fill={text}>{r[0]}</text>
            <text x="420" y={ry} fontSize="9" fill={muted}>{r[1]}</text>
            <rect x="512" y={ry - 11} width="64" height="16" rx="8" fill={surface2} stroke={border} />
            <text x="544" y={ry} fontSize="8" fill={muted} textAnchor="middle">{r[2]}</text>
            {i < ROWS.length - 1 && <line x1="214" y1={ry + 16} x2="602" y2={ry + 16} stroke={border} />}
          </g>
        );
      })}

      {/* Callouts */}
      <Callout x={170} y={160} n={1} gold={gold} />
      <Callout x={300} y={62} n={2} gold={gold} />
      <Callout x={300} y={200} n={3} gold={gold} />
      <Callout x={604} y={16} n={4} gold={gold} />
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
