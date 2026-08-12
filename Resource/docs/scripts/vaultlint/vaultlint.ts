/**
 * vaultlint: a structure linter for Obsidian vaults.
 *
 *   node vaultlint.ts [path-to-vault] [--json] [--strict] [--config file]
 *
 * Checks: broken wikilinks and embeds, missing heading and block targets,
 * broken local markdown links, orphan notes, duplicate note names and
 * aliases, unclosed frontmatter, and required-frontmatter rules from an
 * optional .vaultlint.json in the vault root.
 *
 * Exit codes: 0 clean, 1 errors found (or warnings with --strict), 2 usage.
 * Needs Node 23.6+ (native TypeScript). No dependencies.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { type Config, type Finding, type VaultInput, lintVault } from "./lib.ts";

const SKIP_DIRS = new Set(["node_modules"]);

export function loadVault(root: string): VaultInput {
  const notes = new Map<string, string>();
  const files = new Set<string>();

  const walk = (dir: string, rel: string) => {
    for (const name of readdirSync(dir)) {
      if (name.startsWith(".") || SKIP_DIRS.has(name)) continue;
      const abs = join(dir, name);
      const relPath = rel ? `${rel}/${name}` : name;
      if (statSync(abs).isDirectory()) {
        walk(abs, relPath);
      } else {
        files.add(relPath);
        if (name.toLowerCase().endsWith(".md")) {
          notes.set(relPath, readFileSync(abs, "utf-8"));
        }
      }
    }
  };

  walk(root, "");
  return { notes, files };
}

function loadConfig(root: string, explicit?: string): Config {
  const path = explicit ?? join(root, ".vaultlint.json");
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch (e) {
    if (explicit) {
      console.error(`Could not read config ${path}: ${(e as Error).message}`);
      process.exit(2);
    }
    return {};
  }
}

const TITLES: Record<Finding["check"], string> = {
  "broken-link": "BROKEN LINKS",
  "broken-embed": "BROKEN EMBEDS",
  "missing-heading": "MISSING HEADINGS",
  "missing-block": "MISSING BLOCK REFS",
  "missing-frontmatter": "MISSING FRONTMATTER",
  "unclosed-frontmatter": "UNCLOSED FRONTMATTER",
  orphan: "ORPHANS",
  "duplicate-name": "DUPLICATE NAMES",
  "duplicate-alias": "DUPLICATE ALIASES",
};

function main() {
  const args = process.argv.slice(2);
  const json = args.includes("--json");
  const strict = args.includes("--strict");
  const cfgIdx = args.indexOf("--config");
  const explicitCfg = cfgIdx >= 0 ? args[cfgIdx + 1] : undefined;
  const positional = args.filter(
    (a, i) => !a.startsWith("--") && (cfgIdx < 0 || i !== cfgIdx + 1),
  );
  if (positional.length > 1) {
    console.error("Usage: node vaultlint.ts [vault] [--json] [--strict] [--config file]");
    process.exit(2);
  }
  const root = positional[0] ?? ".";

  let input: VaultInput;
  try {
    input = loadVault(root);
  } catch (e) {
    console.error(`Could not read vault at "${root}": ${(e as Error).message}`);
    process.exit(2);
  }
  const config = loadConfig(root, explicitCfg);
  const { findings, notesScanned, linksChecked } = lintVault(input, config);

  const errors = findings.filter((f) => f.level === "error").length;
  const warnings = findings.length - errors;

  if (json) {
    console.log(JSON.stringify(
      { summary: { notesScanned, linksChecked, errors, warnings }, findings },
      null, 2,
    ));
  } else {
    console.log(`vaultlint: ${notesScanned} notes scanned, ${linksChecked} links checked\n`);
    let lastCheck = "";
    for (const f of findings) {
      if (f.check !== lastCheck) {
        const n = findings.filter((x) => x.check === f.check).length;
        console.log(`${TITLES[f.check]} (${n})`);
        lastCheck = f.check;
      }
      const loc = f.line ? `${f.file}:${f.line}` : f.file;
      console.log(`  ${loc}  ${f.message}`);
    }
    if (findings.length) console.log("");
    console.log(`${errors} error${errors === 1 ? "" : "s"}, ` +
      `${warnings} warning${warnings === 1 ? "" : "s"}`);
  }

  process.exit(errors > 0 || (strict && warnings > 0) ? 1 : 0);
}

const isDirectRun = process.argv[1] &&
  import.meta.url.endsWith(process.argv[1].replace(/\\/g, "/").split("/").pop()!);
if (isDirectRun) main();
