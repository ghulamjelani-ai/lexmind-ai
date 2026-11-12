/** Minimal inline icon set (stroke, currentColor) — no icon library dependency. */
export function Icon({ name, className = "h-[18px] w-[18px]" }: { name: string; className?: string }) {
  const common = {
    className,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (name) {
    case "home":
      return <svg {...common}><path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" /></svg>;
    case "folder":
      return <svg {...common}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /></svg>;
    case "users":
      return <svg {...common}><circle cx="9" cy="8" r="3" /><path d="M3 20c0-3 3-5 6-5s6 2 6 5" /><path d="M16 5.5a3 3 0 0 1 0 5.5M21 20c0-2-1.5-3.6-3.5-4.3" /></svg>;
    case "doc":
      return <svg {...common}><path d="M6 2h8l4 4v16H6z" /><path d="M14 2v4h4" /><path d="M9 13h6M9 17h6" /></svg>;
    case "spark":
      return <svg {...common}><path d="M12 3v4M12 17v4M3 12h4M17 12h4" /><path d="M12 8l1.4 2.6L16 12l-2.6 1.4L12 16l-1.4-2.6L8 12l2.6-1.4z" /></svg>;
    case "scale":
      return <svg {...common}><path d="M12 4v16M7 20h10" /><path d="M5 7h14M12 4a1.5 1.5 0 1 0 0 .01" /><path d="M5 7l-2.5 5a2.5 2.5 0 0 0 5 0zM19 7l-2.5 5a2.5 2.5 0 0 0 5 0z" /></svg>;
    case "chart":
      return <svg {...common}><path d="M4 20V4M20 20H4" /><path d="M8 16v-4M12 16V8M16 16v-6" /></svg>;
    case "shield":
      return <svg {...common}><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z" /><path d="M9.5 12l1.8 1.8L15 10" /></svg>;
    case "gear":
      return <svg {...common}><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1" /></svg>;
    case "scales-filled":
      return <svg {...common}><path d="M12 3v18M7 21h10" /></svg>;
    case "download":
      return <svg {...common}><path d="M12 3v12M8 11l4 4 4-4" /><path d="M4 21h16" /></svg>;
    case "check":
      return <svg {...common}><path d="M5 12l4 4 10-10" /></svg>;
    case "alert":
      return <svg {...common}><path d="M12 8v5M12 16v.01" /><path d="M10.3 3.6 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0z" /></svg>;
    case "clock":
      return <svg {...common}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>;
    case "bolt":
      return <svg {...common}><path d="M13 2 4 14h7l-1 8 9-12h-7z" /></svg>;
    case "receipt":
      return <svg {...common}><path d="M6 2h12v20l-3-2-3 2-3-2-3 2z" /><path d="M9 7h6M9 11h6M9 15h4" /></svg>;
    case "link":
      return <svg {...common}><path d="M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1" /><path d="M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1" /></svg>;
    case "intake":
      return <svg {...common}><circle cx="9" cy="8" r="3" /><path d="M4 20c0-3 2.5-5 5-5 1.2 0 2.3.3 3.2.9" /><path d="M16 15h5M18.5 12.5v5" /></svg>;
    case "shield-alert":
      return <svg {...common}><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z" /><path d="M12 8v3M12 14v.01" /></svg>;
    case "wallet":
      return <svg {...common}><path d="M3 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2H5a2 2 0 0 1-2-2z" /><path d="M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6H16a2 2 0 0 0 0 4h5" /></svg>;
    case "vault":
      return <svg {...common}><rect x="3" y="4" width="18" height="16" rx="2" /><circle cx="12" cy="12" r="3.5" /><path d="M12 8.5V12M4 20l1-1M20 20l-1-1" /></svg>;
    case "help":
      return <svg {...common}><circle cx="12" cy="12" r="9" /><path d="M9.5 9a2.5 2.5 0 1 1 3.4 2.3c-.9.4-1.4 1-1.4 1.9" /><path d="M12 17h.01" /></svg>;
    default:
      return <svg {...common}><circle cx="12" cy="12" r="9" /></svg>;
  }
}
