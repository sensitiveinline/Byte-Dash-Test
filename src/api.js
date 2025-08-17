export async function loadJSON(name) {
  const paths = [
    `./data/${name}`, `../data/${name}`, `/data/${name}`,
    `./public/data/${name}`, `../public/data/${name}`
  ];
  for (const p of paths) {
    try {
      const r = await fetch(p, { cache: "no-store" });
      if (r.ok) return await r.json();
    } catch {}
  }
  return null;
}
export function unwrap(payload) {
  if (!payload) return { items: [], meta: {} };
  if (Array.isArray(payload)) return { items: payload, meta: {} };
  return { items: payload.items || [], meta: payload.meta || {} };
}
export function fmtDelta(n) {
  const v = Number(n ?? 0);
  const cls = v > 0 ? "up" : v < 0 ? "down" : "flat";
  const text = v > 0 ? `+${v.toFixed(1)}` : v < 0 ? v.toFixed(1) : "0.0";
  return `<span class="delta ${cls}">${text}</span>`;
}
