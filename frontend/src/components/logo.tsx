/**
 * LexMind brand mark — a minimal scales-of-justice monogram (navy + gold) with
 * a serif wordmark. Used in the sidebar, login and landing. No third-party logo.
 */
export function Logo({
  size = 28,
  withWordmark = true,
  className = "",
}: {
  size?: number;
  withWordmark?: boolean;
  className?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className="shrink-0"
      >
        <rect width="32" height="32" rx="8" className="fill-[var(--brand-ink)]" />
        <path d="M16 6.5V23" stroke="var(--brand-gold)" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="16" cy="6.5" r="1.9" fill="var(--brand-gold)" />
        <path d="M8.5 10.5H23.5" stroke="var(--brand-gold)" strokeWidth="1.8" strokeLinecap="round" />
        <path
          d="M8.5 10.5L6 15.5C6 17 7.2 18 8.5 18C9.8 18 11 17 11 15.5L8.5 10.5Z"
          fill="var(--brand-gold)"
          fillOpacity="0.22"
          stroke="var(--brand-gold)"
          strokeWidth="1.4"
          strokeLinejoin="round"
        />
        <path
          d="M23.5 10.5L21 15.5C21 17 22.2 18 23.5 18C24.8 18 26 17 26 15.5L23.5 10.5Z"
          fill="var(--brand-gold)"
          fillOpacity="0.22"
          stroke="var(--brand-gold)"
          strokeWidth="1.4"
          strokeLinejoin="round"
        />
        <path d="M11.5 24.5H20.5" stroke="var(--brand-gold)" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
      {withWordmark && (
        <span className="font-serif text-lg font-semibold tracking-tight text-[var(--brand-ink)] dark:text-white">
          Lex<span className="text-[var(--brand-gold-ink)]">Mind</span>
        </span>
      )}
    </span>
  );
}
