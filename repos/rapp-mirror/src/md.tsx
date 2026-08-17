import type { ReactNode } from "react";

/**
 * Tiny, safe markdown-to-React renderer for transcript text: bold, italics,
 * inline code, links, and numbered/bulleted lists. React's escaping keeps it
 * XSS-safe; links open in the system browser (window.ts denies popups and
 * hands the URL to shell.openExternal).
 */

function inline(text: string, keyBase: string): ReactNode[] {
  const out: ReactNode[] = [];
  // links first, then bold, italics, code
  const re = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`|(https?:\/\/[^\s<>()]+[^\s<>().,;:!?'"])/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const key = `${keyBase}-${k++}`;
    if (m[1] !== undefined) {
      out.push(
        <a key={key} href={m[2]} target="_blank" rel="noreferrer">
          {m[1]}
        </a>,
      );
    } else if (m[3] !== undefined) out.push(<b key={key}>{inline(m[3], key)}</b>);
    else if (m[4] !== undefined) out.push(<i key={key}>{m[4]}</i>);
    else if (m[5] !== undefined) out.push(<code key={key}>{m[5]}</code>);
    else if (m[6] !== undefined) {
      out.push(
        <a key={key} href={m[6]} target="_blank" rel="noreferrer">
          {m[6].replace(/^https?:\/\//, "").slice(0, 60)}
        </a>,
      );
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

export function renderMd(text: string): ReactNode[] {
  // Re-break flattened numbered/bulleted runs ("… 1. … 2. …") onto lines.
  const prepared = text
    .replace(/\s(\d{1,2}\.\s\*\*)/g, "\n$1")
    .replace(/\s([-•]\s)/g, "\n$1")
    .replace(/\s*---\s*$/g, "");
  const lines = prepared.split(/\n+/).map((l) => l.trim()).filter(Boolean);
  const out: ReactNode[] = [];
  let list: { ordered: boolean; items: ReactNode[][] } | null = null;
  const flush = (key: string) => {
    if (!list) return;
    out.push(
      list.ordered ? (
        <ol key={key}>{list.items.map((it, i) => <li key={i}>{it}</li>)}</ol>
      ) : (
        <ul key={key}>{list.items.map((it, i) => <li key={i}>{it}</li>)}</ul>
      ),
    );
    list = null;
  };
  lines.forEach((line, i) => {
    const num = /^\d{1,2}\.\s+(.*)$/.exec(line);
    const bullet = /^[-•]\s+(.*)$/.exec(line);
    if (num || bullet) {
      const ordered = Boolean(num);
      if (!list || list.ordered !== ordered) flush(`l${i}`);
      list = list ?? { ordered, items: [] };
      list.items.push(inline((num ?? bullet)![1], `i${i}`));
      return;
    }
    flush(`l${i}`);
    out.push(<p key={`p${i}`}>{inline(line, `p${i}`)}</p>);
  });
  flush("tail");
  return out;
}
