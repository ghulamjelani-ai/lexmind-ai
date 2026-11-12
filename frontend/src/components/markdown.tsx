import type { ReactNode } from "react";

/**
 * Minimal, safe Markdown renderer for AI output.
 *
 * Everything is built as React elements — there is no `dangerouslySetInnerHTML`
 * — so untrusted model text can never inject markup. Handles the structures the
 * assistant actually emits: headings, bold/italic, inline code, and bullet or
 * numbered lists. Partial markdown during streaming degrades gracefully.
 */
export function Markdown({ content }: { content: string }) {
  const blocks = parseBlocks(content);
  return <div className="space-y-2.5">{blocks.map((b, i) => renderBlock(b, i))}</div>;
}

type Block =
  | { type: "h"; level: number; text: string }
  | { type: "ul"; items: string[] }
  | { type: "ol"; items: string[] }
  | { type: "p"; text: string };

function parseBlocks(src: string): Block[] {
  const lines = src.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === "") {
      i++;
      continue;
    }
    const heading = /^(#{1,6})\s+(.*)$/.exec(line);
    if (heading) {
      blocks.push({ type: "h", level: heading[1].length, text: heading[2].trim() });
      i++;
      continue;
    }
    if (/^\s*[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, "").trim());
        i++;
      }
      blocks.push({ type: "ul", items });
      continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, "").trim());
        i++;
      }
      blocks.push({ type: "ol", items });
      continue;
    }
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^#{1,6}\s+/.test(lines[i]) &&
      !/^\s*[-*]\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i])
    ) {
      para.push(lines[i].trim());
      i++;
    }
    blocks.push({ type: "p", text: para.join(" ") });
  }
  return blocks;
}

function renderBlock(b: Block, key: number): ReactNode {
  switch (b.type) {
    case "h": {
      const size =
        b.level <= 1
          ? "text-base"
          : b.level === 2
            ? "text-[0.95rem]"
            : "text-sm";
      return (
        <p key={key} className={`font-serif font-semibold text-[var(--text)] ${size} ${key > 0 ? "mt-1" : ""}`}>
          {inline(b.text)}
        </p>
      );
    }
    case "ul":
      return (
        <ul key={key} className="list-disc space-y-1 pl-5">
          {b.items.map((t, j) => (
            <li key={j}>{inline(t)}</li>
          ))}
        </ul>
      );
    case "ol":
      return (
        <ol key={key} className="list-decimal space-y-1 pl-5">
          {b.items.map((t, j) => (
            <li key={j}>{inline(t)}</li>
          ))}
        </ol>
      );
    case "p":
      return (
        <p key={key} className="leading-relaxed">
          {inline(b.text)}
        </p>
      );
  }
}

// Inline formatting: **bold**, *italic*, `code`, _italic_.
function inline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  // Bold (**) is matched before single-* italic so it wins; code and _italic_ too.
  const re = /(\*\*([^*]+)\*\*|\*([^*\n]+)\*|`([^`]+)`|_([^_]+)_)/g;
  let last = 0;
  let k = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    if (m[2] !== undefined) {
      nodes.push(<strong key={k++}>{m[2]}</strong>);
    } else if (m[3] !== undefined) {
      nodes.push(<em key={k++}>{m[3]}</em>);
    } else if (m[4] !== undefined) {
      nodes.push(
        <code key={k++} className="rounded bg-[var(--surface-2)] px-1 text-[0.85em]">
          {m[4]}
        </code>,
      );
    } else if (m[5] !== undefined) {
      nodes.push(<em key={k++}>{m[5]}</em>);
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}
