/**
 * vaultlint core: parsing, link resolution, and checks. Pure functions over
 * in-memory data; no filesystem access in this file.
 *
 * Resolution follows Obsidian's rules closely enough to lint honestly:
 * a wikilink target matches a full vault path, a path suffix, a basename,
 * or a frontmatter alias, all case-insensitive. Links inside code fences,
 * inline code, %% comments %% and frontmatter are not links, so those
 * regions are masked out (offsets preserved) before scanning.
 */

export type Level = "error" | "warning";

export type Finding = {
  level: Level;
  check:
    | "broken-link"
    | "broken-embed"
    | "missing-heading"
    | "missing-block"
    | "missing-frontmatter"
    | "unclosed-frontmatter"
    | "orphan"
    | "duplicate-name"
    | "duplicate-alias";
  file: string;
  line?: number;
  message: string;
};

export type Config = {
  ignore?: string[]; // globs: not scanned or checked, but still link targets
  orphanIgnore?: string[]; // globs: exempt from the orphan check
  frontmatterRules?: { glob: string; require: string[] }[];
};

export type VaultInput = {
  notes: Map<string, string>; // vault-relative posix path -> markdown
  files: Set<string>; // every file in the vault, notes included
};

export type LintResult = {
  findings: Finding[];
  notesScanned: number;
  linksChecked: number;
};

// ---------- globs ----------

export function globToRegex(glob: string): RegExp {
  let re = "";
  for (let i = 0; i < glob.length; i++) {
    const c = glob[i];
    if (c === "*") {
      if (glob[i + 1] === "*") {
        re += glob[i + 2] === "/" ? "(?:.*/)?" : ".*";
        i += glob[i + 2] === "/" ? 2 : 1;
      } else {
        re += "[^/]*";
      }
    } else if (c === "?") {
      re += "[^/]";
    } else {
      re += c.replace(/[.+^${}()|[\]\\]/g, "\\$&");
    }
  }
  return new RegExp("^" + re + "$", "i");
}

const matchAny = (path: string, globs: string[] | undefined) =>
  (globs ?? []).some((g) => globToRegex(g).test(path));

// ---------- note preparation ----------

/** Replace every non-newline char in [from, to) with spaces, keeping offsets. */
function maskRange(chars: string[], from: number, to: number) {
  for (let i = from; i < to && i < chars.length; i++) {
    if (chars[i] !== "\n") chars[i] = " ";
  }
}

export type Meta = Record<string, string | string[]>;

export type PreparedNote = {
  masked: string; // body with non-content regions blanked, offsets intact
  meta: Meta;
  fmUnclosed: boolean;
  headings: Set<string>;
  blocks: Set<string>;
};

export function normalizeHeading(h: string): string {
  return h
    .replace(/\s+#+\s*$/, "")
    .replace(/[*_`~[\]]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function parseFrontmatter(block: string): Meta {
  const meta: Meta = {};
  const lines = block.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^([A-Za-z0-9_][\w.-]*):\s*(.*)$/);
    if (!m) continue;
    const key = m[1];
    let raw = m[2].trim();
    if (raw === "") {
      const items: string[] = [];
      while (i + 1 < lines.length) {
        const it = lines[i + 1].match(/^\s+-\s+(.*)$/);
        if (!it) break;
        items.push(it[1].trim().replace(/^["']|["']$/g, ""));
        i++;
      }
      meta[key] = items.length ? items : "";
    } else if (raw.startsWith("[") && raw.endsWith("]")) {
      const inner = raw.slice(1, -1).trim();
      meta[key] = inner
        ? inner.split(",").map((v) => v.trim().replace(/^["']|["']$/g, ""))
        : [];
    } else {
      meta[key] = raw.replace(/^["']|["']$/g, "");
    }
  }
  return meta;
}

export function prepareNote(text: string): PreparedNote {
  const chars = [...text];
  let meta: Meta = {};
  let fmUnclosed = false;

  // frontmatter
  if (/^---\r?\n/.test(text)) {
    const close = text.slice(3).search(/\r?\n(---|\.\.\.)(\r?\n|$)/);
    if (close >= 0) {
      const end = 3 + close + text.slice(3 + close).match(/\r?\n(---|\.\.\.)(\r?\n|$)/)![0].length;
      meta = parseFrontmatter(text.slice(3, 3 + close));
      maskRange(chars, 0, end);
    } else {
      fmUnclosed = true;
    }
  }

  // fenced code blocks, line by line
  {
    let fence: string | null = null;
    let offset = 0;
    for (const line of text.split("\n")) {
      const open = line.match(/^\s*(```+|~~~+)/);
      if (fence === null && open) {
        fence = open[1][0].repeat(3);
        maskRange(chars, offset, offset + line.length);
      } else if (fence !== null) {
        maskRange(chars, offset, offset + line.length);
        if (open && open[1].startsWith(fence)) fence = null;
      }
      offset += line.length + 1;
    }
  }

  let masked = chars.join("");
  // %% comments %% and inline code, offsets preserved
  masked = masked.replace(/%%[\s\S]*?%%/g, (s) => s.replace(/[^\n]/g, " "));
  masked = masked.replace(/`[^`\n]*`/g, (s) => " ".repeat(s.length));

  const headings = new Set<string>();
  const blocks = new Set<string>();
  for (const line of masked.split("\n")) {
    const h = line.match(/^#{1,6}\s+(.*)$/);
    if (h) headings.add(normalizeHeading(h[1]));
    const b = line.match(/(?:^|\s)\^([A-Za-z0-9-]+)\s*$/);
    if (b) blocks.add(b[1].toLowerCase());
  }

  return { masked, meta, fmUnclosed, headings, blocks };
}

// ---------- link extraction ----------

export type Link = {
  embed: boolean;
  kind: "wiki" | "md";
  target: string; // "" means same-file
  section: string | null; // heading path or ^block, without the #
  line: number;
  raw: string;
};

const lineOf = (text: string, index: number) =>
  text.slice(0, index).split("\n").length;

export function extractLinks(masked: string): Link[] {
  const links: Link[] = [];

  for (const m of masked.matchAll(/(!?)\[\[([^\[\]\n]+?)\]\]/g)) {
    const inner = m[2].split("|")[0].trim().replace(/\\+$/, "").trim();
    const hash = inner.indexOf("#");
    let target = hash >= 0 ? inner.slice(0, hash) : inner;
    const section = hash >= 0 ? inner.slice(hash + 1).trim() : null;
    target = target.trim().replace(/\.md$/i, "");
    links.push({
      embed: m[1] === "!",
      kind: "wiki",
      target,
      section: section || null,
      line: lineOf(masked, m.index!),
      raw: m[0],
    });
  }

  for (const m of masked.matchAll(/(!?)\[(?:[^\]\\\n]|\\.)*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)) {
    let href = m[2];
    if (/^[a-z][a-z0-9+.-]*:/i.test(href)) continue; // http, mailto, obsidian, ...
    if (href.startsWith("#")) continue; // same-page anchor, out of scope
    href = href.split("#")[0];
    try {
      href = decodeURIComponent(href);
    } catch {
      /* keep raw */
    }
    if (!href) continue;
    links.push({
      embed: m[1] === "!",
      kind: "md",
      target: href,
      section: null,
      line: lineOf(masked, m.index!),
      raw: m[0],
    });
  }

  return links;
}

// ---------- resolution ----------

export type Resolver = {
  note: (target: string) => string | null;
  file: (target: string) => string | null;
  mdPath: (target: string, fromNote: string) => string | null;
};

const baseName = (p: string) => p.slice(p.lastIndexOf("/") + 1);
const dirName = (p: string) => (p.includes("/") ? p.slice(0, p.lastIndexOf("/")) : "");

export function buildResolver(
  input: VaultInput,
  metaByNote: Map<string, Meta>,
): { resolver: Resolver; aliasOwners: Map<string, string[]> } {
  const notePaths = [...input.notes.keys()];
  const byPath = new Map<string, string>();
  const byBase = new Map<string, string[]>();
  for (const p of notePaths) {
    const key = p.toLowerCase().replace(/\.md$/, "");
    byPath.set(key, p);
    const b = baseName(key);
    byBase.set(b, [...(byBase.get(b) ?? []), p]);
  }

  const aliasOwners = new Map<string, string[]>();
  for (const [p, meta] of metaByNote) {
    const aliases = meta.aliases;
    for (const a of Array.isArray(aliases) ? aliases : aliases ? [aliases] : []) {
      const key = a.toLowerCase();
      aliasOwners.set(key, [...(aliasOwners.get(key) ?? []), p]);
    }
  }

  const filesByPath = new Map<string, string>();
  const filesByBase = new Map<string, string[]>();
  for (const f of input.files) {
    const key = f.toLowerCase();
    filesByPath.set(key, f);
    const b = baseName(key);
    filesByBase.set(b, [...(filesByBase.get(b) ?? []), f]);
  }

  const note = (target: string): string | null => {
    const t = target.toLowerCase().replace(/\.md$/, "");
    if (!t) return null;
    const exact = byPath.get(t);
    if (exact) return exact;
    if (t.includes("/")) {
      const hit = notePaths.find((p) =>
        p.toLowerCase().replace(/\.md$/, "").endsWith("/" + t),
      );
      if (hit) return hit;
    }
    const base = byBase.get(baseName(t));
    if (base?.length) return base[0];
    const alias = aliasOwners.get(target.toLowerCase().trim());
    if (alias?.length) return alias[0];
    return null;
  };

  const file = (target: string): string | null => {
    const t = target.toLowerCase();
    const exact = filesByPath.get(t);
    if (exact) return exact;
    if (t.includes("/")) {
      const hit = [...input.files].find((f) => f.toLowerCase().endsWith("/" + t));
      if (hit) return hit;
    }
    const base = filesByBase.get(baseName(t));
    if (base?.length) return base[0];
    return null;
  };

  // markdown links resolve relative to the note's folder, then the vault root
  const mdPath = (target: string, fromNote: string): string | null => {
    const clean = target.replace(/^\.\//, "");
    const fromDir = dirName(fromNote);
    const candidates = [
      fromDir ? `${fromDir}/${clean}` : clean,
      clean,
    ].map((c) => normalizeRel(c));
    for (const c of candidates) {
      const hit = filesByPath.get(c.toLowerCase());
      if (hit) return hit;
    }
    return null;
  };

  return { resolver: { note, file, mdPath }, aliasOwners };
}

function normalizeRel(p: string): string {
  const out: string[] = [];
  for (const part of p.split("/")) {
    if (part === "" || part === ".") continue;
    if (part === "..") out.pop();
    else out.push(part);
  }
  return out.join("/");
}

// ---------- the lint ----------

const hasExtension = (target: string) => /\.[A-Za-z0-9]{1,8}$/.test(baseName(target));

export function lintVault(input: VaultInput, config: Config = {}): LintResult {
  const findings: Finding[] = [];
  const prepared = new Map<string, PreparedNote>();
  for (const [p, text] of input.notes) prepared.set(p, prepareNote(text));

  const metaByNote = new Map([...prepared].map(([p, n]) => [p, n.meta] as const));
  const { resolver, aliasOwners } = buildResolver(input, metaByNote);

  const scanned = [...input.notes.keys()].filter((p) => !matchAny(p, config.ignore));
  const inbound = new Map<string, number>();
  let linksChecked = 0;

  const sectionCheck = (notePath: string, targetPath: string, link: Link) => {
    const section = link.section!;
    const target = prepared.get(targetPath)!;
    if (section.startsWith("^")) {
      const id = section.slice(1).toLowerCase();
      if (!target.blocks.has(id)) {
        findings.push({
          level: "error", check: "missing-block", file: notePath, line: link.line,
          message: `${link.raw} -> no block ^${section.slice(1)} in ${targetPath}`,
        });
      }
    } else {
      const last = section.split("#").pop()!;
      if (!target.headings.has(normalizeHeading(last))) {
        findings.push({
          level: "error", check: "missing-heading", file: notePath, line: link.line,
          message: `${link.raw} -> no heading "${last}" in ${targetPath}`,
        });
      }
    }
  };

  for (const notePath of scanned) {
    const note = prepared.get(notePath)!;
    if (note.fmUnclosed) {
      findings.push({
        level: "warning", check: "unclosed-frontmatter", file: notePath, line: 1,
        message: "frontmatter opens with --- but never closes",
      });
    }

    for (const link of extractLinks(note.masked)) {
      linksChecked++;

      if (link.kind === "md") {
        const hit = resolver.mdPath(link.target, notePath);
        if (!hit) {
          findings.push({
            level: "error", check: link.embed ? "broken-embed" : "broken-link",
            file: notePath, line: link.line,
            message: `${link.raw} -> no file at "${link.target}"`,
          });
        } else if (hit.toLowerCase().endsWith(".md") && hit !== notePath) {
          inbound.set(hit, (inbound.get(hit) ?? 0) + 1);
        }
        continue;
      }

      // wikilink or wiki embed
      if (link.target === "") {
        if (link.section) sectionCheck(notePath, notePath, link);
        continue;
      }
      if (hasExtension(link.target) && !/\.md$/i.test(link.target)) {
        if (!resolver.file(link.target)) {
          findings.push({
            level: "error", check: "broken-embed", file: notePath, line: link.line,
            message: `${link.raw} -> no file matches "${link.target}"`,
          });
        }
        continue;
      }
      const hit = resolver.note(link.target);
      if (!hit) {
        findings.push({
          level: "error", check: link.embed ? "broken-embed" : "broken-link",
          file: notePath, line: link.line,
          message: `${link.raw} -> no note matches "${link.target}"`,
        });
        continue;
      }
      if (hit !== notePath) inbound.set(hit, (inbound.get(hit) ?? 0) + 1);
      if (link.section) sectionCheck(notePath, hit, link);
    }
  }

  // orphans
  for (const p of scanned) {
    if (matchAny(p, config.orphanIgnore)) continue;
    if (!inbound.get(p)) {
      findings.push({
        level: "warning", check: "orphan", file: p,
        message: "no other note links here",
      });
    }
  }

  // ambiguity: duplicate basenames and aliases (ignored notes stay resolvable
  // link targets, but never produce findings of their own)
  const byBase = new Map<string, string[]>();
  for (const p of scanned) {
    const b = baseName(p.toLowerCase());
    byBase.set(b, [...(byBase.get(b) ?? []), p]);
  }
  for (const [b, paths] of byBase) {
    if (paths.length > 1) {
      findings.push({
        level: "warning", check: "duplicate-name", file: paths[0],
        message: `${paths.length} notes share the name "${b}": ${paths.join(", ")}`,
      });
    }
  }
  for (const [alias, owners] of aliasOwners) {
    const distinct = [...new Set(owners)].filter((p) => !matchAny(p, config.ignore));
    if (distinct.length > 1) {
      findings.push({
        level: "warning", check: "duplicate-alias", file: distinct[0],
        message: `alias "${alias}" belongs to ${distinct.length} notes: ${distinct.join(", ")}`,
      });
    }
  }

  // frontmatter schema rules
  for (const rule of config.frontmatterRules ?? []) {
    for (const p of scanned) {
      if (!globToRegex(rule.glob).test(p)) continue;
      const meta = prepared.get(p)!.meta;
      const missing = rule.require.filter(
        (k) => meta[k] === undefined || meta[k] === "" ||
          (Array.isArray(meta[k]) && (meta[k] as string[]).length === 0),
      );
      if (missing.length) {
        findings.push({
          level: "error", check: "missing-frontmatter", file: p, line: 1,
          message: `missing required frontmatter: ${missing.join(", ")} (rule: ${rule.glob})`,
        });
      }
    }
  }

  const order: Record<Level, number> = { error: 0, warning: 1 };
  findings.sort(
    (a, b) =>
      order[a.level] - order[b.level] ||
      a.check.localeCompare(b.check) ||
      a.file.localeCompare(b.file) ||
      (a.line ?? 0) - (b.line ?? 0),
  );

  return { findings, notesScanned: scanned.length, linksChecked };
}
