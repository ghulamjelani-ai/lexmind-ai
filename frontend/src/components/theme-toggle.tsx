"use client";

import { useEffect, useState } from "react";

type Theme = "system" | "light" | "dark";

/**
 * Cycles the colour theme: System → Light → Dark → System. The choice is saved
 * in localStorage and applied to <html data-theme> (a pre-paint script in the
 * root layout applies it on first load so there is no flash).
 */
export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("lexmind-theme");
      if (saved === "light" || saved === "dark") setTheme(saved);
    } catch {
      /* storage blocked — stay on system */
    }
  }, []);

  function apply(next: Theme) {
    setTheme(next);
    try {
      if (next === "system") {
        localStorage.removeItem("lexmind-theme");
        document.documentElement.removeAttribute("data-theme");
      } else {
        localStorage.setItem("lexmind-theme", next);
        document.documentElement.setAttribute("data-theme", next);
      }
    } catch {
      /* ignore */
    }
  }

  function cycle() {
    apply(theme === "system" ? "light" : theme === "light" ? "dark" : "system");
  }

  const label =
    theme === "system" ? "System theme" : theme === "light" ? "Light theme" : "Dark theme";

  return (
    <button
      onClick={cycle}
      title={`${label} — click to change`}
      aria-label={`${label}. Click to change theme.`}
      className="flex h-9 w-9 items-center justify-center rounded-[10px] border border-[var(--border)] text-[var(--muted)] transition hover:bg-[var(--surface-2)] hover:text-[var(--text)]"
    >
      {theme === "dark" ? <Moon /> : theme === "light" ? <Sun /> : <Monitor />}
    </button>
  );
}

const common = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.7,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function Sun() {
  return (
    <svg {...common}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

function Moon() {
  return (
    <svg {...common}>
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  );
}

function Monitor() {
  return (
    <svg {...common}>
      <rect x="3" y="4" width="18" height="12" rx="2" />
      <path d="M8 20h8M12 16v4" />
    </svg>
  );
}
