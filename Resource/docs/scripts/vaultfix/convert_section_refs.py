#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
convert_section_refs.py — 문서구조_개선plan v4 4단계: 다른 파일을 가리키는 `§` 텍스트 참조를
`[[파일]] §N` 위키링크로 변환한다.

대상: `<약칭 또는 파일명> §N` 형태에서 앞 토큰이 볼트 안의 실제 파일(접두사 또는 전체 basename)과
      일치하는 경우만. 같은 파일 안을 가리키는 `§N`(앞 토큰이 파일과 무관한 서술어)은 건드리지 않는다.

방법:
  1. 볼트를 스캔해 약칭(파일명 첫 "_" 앞 토큰) → 파일 매핑표를 만든다.
     안전장치: 접두사에 최소 1개 ASCII 숫자가 있어야 후보로 채택한다(순수 한국어/영어 단어는
     오탐 위험이 크므로 제외 — "아래"·"위"·"문서"·"오라클" 등은 자동으로 배제된다).
  2. 전체 basename(예: "전투로그", "알파_개발계획", .md 유무 무관)도 후보로 채택한다(숫자 무관, 이미
     완전한 파일명이라 오탐 위험이 낮다).
  3. 큐레이션된 별칭 2개("실전노하우"·"노하우" → 언리얼_MCP_실전노하우.md, 8+14건 실사용 확인) 추가.
  4. 텍스트에서 `<token> §N`을 찾되(masked — frontmatter·코드펜스·인라인코드·기존 [[..]]/md링크는
     vaultlint와 동일 로직으로 마스킹해 제외), token을 앞뒤 마크다운 기호(★( 등)를 벗겨 정규화한 뒤
     매핑표에서 조회한다.
  5. 후보가 여럿(동명/동접두사 충돌)이면 참조하는 문서와 같은 최상위 feature 폴더의 파일을 우선한다.
     그래도 못 정하면 미해결로 남긴다(추측 금지).
  6. target이 참조하는 문서 자기 자신이면 자기참조로 보고 건드리지 않는다.
  7. 매핑에 아예 없는 토큰(대부분 "아래"·"위"·"문서" 같은 서술어)은 같은 파일 참조로 간주해 그대로 둔다.
  8. 동명 파일(예: plan.md ×10)로 귀결되면 문서화_규칙 §6-4대로 경로+별칭 링크를 쓴다. 이 줄이
     마크다운 표(`|`로 시작하는 행) 안이면 파이프를 `\|`로 이스케이프한다(표 파손 방지).

사용법:
  python convert_section_refs.py                # dry-run (기본)
  python convert_section_refs.py --apply         # 실제 파일 수정
  python convert_section_refs.py --text-report out.txt

멱등성: 이미 `[[...]]  §N`으로 바뀐 참조는 마스킹되어 재매칭되지 않는다(2회 실행해도 diff 0).
"""
import os
import re
import sys
import argparse
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))  # docs/scripts/vaultfix -> docs/

# 큐레이션 별칭 — 실사용 확인된 2건만(§6-a 노하우 문서와 동일 파일)
ALIAS_MAP = {
    "실전노하우": "언리얼_MCP_실전노하우.md",
    "노하우": "언리얼_MCP_실전노하우.md",
}

# 접두사 충돌 수동 판정 — plan 본문이 예시로 명시한 것만("F7 §5-2 → [[F7_스킬아키텍처_확정]] §5-2").
# 다른 충돌(F4/D3/D1 등)은 근거 없는 추측이라 손대지 않고 ambiguous로 보고한다.
MANUAL_PREFIX_OVERRIDE = {
    "F7": "features/전투완성/raw/F7_스킬아키텍처_확정.md",
}

LEADING_STRIP = '*_~"\'(★［<「『«-'  # * _ ~ " ' ( ★ [ < 「 『 « -
TRAILING_STRIP = '*_~"\')】」』»]>,;:.'      # * _ ~ " ' ) 】 」 』 ] > , ; : .


# 토큰과 §N 사이는 정확히 공백 1개만 허용한다(+ 아님). 마스킹된 구간(기존 [[..]]·코드·frontmatter)은
# 최소 2자 이상 공백으로 치환되므로, 이 제약이 "마스킹 틈을 건너뛰어 무관한 토큰과 §N을 잘못 잇는"
# 사고를 원천 차단한다(예: "노하우: [[언리얼_MCP_실전노하우]] §34." — 이미 링크된 참조를 오매칭할 뻔함).
TOKEN_SECTION_RE = re.compile(r'(\S+)[ \t]§([0-9][\w.\-]*)')


# ---------- masking (mirrors docs/scripts/vaultlint/lib.ts) ----------

def mask_text(text):
    chars = list(text)

    def mask_range(a, b):
        for i in range(a, min(b, len(chars))):
            if chars[i] != '\n':
                chars[i] = ' '

    if re.match(r'^---\r?\n', text):
        m = re.search(r'\r?\n(---|\.\.\.)(\r?\n|$)', text[3:])
        if m:
            mask_range(0, 3 + m.end())

    fence = None
    offset = 0
    for line in text.split('\n'):
        openm = re.match(r'^\s*(```+|~~~+)', line)
        if fence is None and openm:
            fence = openm.group(1)[0] * 3
            mask_range(offset, offset + len(line))
        elif fence is not None:
            mask_range(offset, offset + len(line))
            if openm and openm.group(1).startswith(fence):
                fence = None
        offset += len(line) + 1

    masked = ''.join(chars)
    masked = re.sub(r'`[^`\n]*`', lambda m: ' ' * len(m.group(0)), masked)
    masked = re.sub(r'%%[\s\S]*?%%', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), masked)
    # 기존 위키링크(표시 텍스트 포함) — 이미 변환된 참조는 재처리하지 않는다
    masked = re.sub(r'!?\[\[[^\[\]\n]+?\]\]', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), masked)
    # 기존 마크다운 링크
    masked = re.sub(r'!?\[[^\]\n]*\]\([^)\n]+\)', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), masked)
    return masked


# ---------- vault map ----------

def walk_md():
    for root, dirs, files in os.walk(DOCS_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for fn in sorted(files):
            if fn.endswith('.md'):
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, DOCS_ROOT).replace('\\', '/')
                yield path, rel


def compute_prefix(base):
    b = base.lstrip('_')
    if '_' in b:
        return b.split('_', 1)[0]
    return b


def has_ascii_digit(s):
    return any(c.isdigit() and ord(c) < 128 for c in s)


def build_maps():
    all_files = list(walk_md())
    basename_map = defaultdict(list)   # exact-case basename(no .md) -> [relpaths]
    prefix_map = defaultdict(list)     # exact-case prefix -> [relpaths] (digit-safe only)

    for _, rp in all_files:
        base = os.path.basename(rp)[:-3]
        basename_map[base].append(rp)
        prefix = compute_prefix(base)
        if prefix and has_ascii_digit(prefix):
            prefix_map[prefix].append(rp)

    return all_files, basename_map, prefix_map


def feature_root(rp):
    parts = rp.split('/')
    if parts[0] == 'features' and len(parts) > 1:
        return f"features/{parts[1]}"
    return None


def resolve_candidates(candidates, from_rp):
    """dedupe, then disambiguate by same feature-folder as the referencing file."""
    candidates = sorted(set(candidates))
    if len(candidates) == 1:
        return candidates[0], None
    fr = feature_root(from_rp)
    if fr:
        same_folder = [c for c in candidates if c.startswith(fr + '/') or c == f"{fr}.md"]
        if len(same_folder) == 1:
            return same_folder[0], None
    return None, candidates  # ambiguous


def clean_token(tok):
    lead = ''
    while tok and tok[0] in LEADING_STRIP:
        lead += tok[0]
        tok = tok[1:]
    trail = ''
    while tok and tok[-1] in TRAILING_STRIP:
        trail = tok[-1] + trail
        tok = tok[:-1]
    return lead, tok, trail


def wikilink_for(target_rp, basename_map, in_table):
    base = os.path.basename(target_rp)[:-3]
    dupe = len(basename_map.get(base, [])) > 1
    if dupe:
        link_target = target_rp[:-3]  # relpath without .md
        pipe = r'\|' if in_table else '|'
        return f"[[{link_target}{pipe}{base}]]"
    return f"[[{base}]]"


# ---------- conversion ----------

def process_file(path, rp, basename_map, prefix_map, apply_, report):
    with open(path, encoding='utf-8', newline='') as f:
        text = f.read()
    masked = mask_text(text)

    edits = []  # (start, end, replacement)
    for m in TOKEN_SECTION_RE.finditer(masked):
        raw_tok = m.group(1)
        num_preview = m.group(2)
        tok_start = m.start(1)
        lead, core, trail = clean_token(raw_tok)
        if not core:
            continue
        core_no_md = core[:-3] if core.lower().endswith('.md') else core

        candidates = []
        if core in ALIAS_MAP:
            candidates.append(ALIAS_MAP[core])
        if core_no_md in basename_map:
            candidates += basename_map[core_no_md]
        elif core in basename_map:
            candidates += basename_map[core]
        if core in prefix_map:
            candidates += prefix_map[core]

        if not candidates:
            continue  # 매핑 없음 — 같은 파일 참조로 간주, 건드리지 않음

        if core in MANUAL_PREFIX_OVERRIDE and MANUAL_PREFIX_OVERRIDE[core] in candidates:
            target, ambiguous = MANUAL_PREFIX_OVERRIDE[core], None
        else:
            target, ambiguous = resolve_candidates(candidates, rp)
        if target is None:
            report['ambiguous'].append((rp, raw_tok, num_preview, ambiguous))
            continue
        if target == rp:
            report['self'].append((rp, raw_tok, num_preview))
            continue

        line_start = text.rfind('\n', 0, tok_start) + 1
        line_end = text.find('\n', tok_start)
        if line_end == -1:
            line_end = len(text)
        in_table = text[line_start:line_end].lstrip().startswith('|')

        link = wikilink_for(target, basename_map, in_table)
        core_start = tok_start + len(lead)
        core_end = core_start + len(core)
        edits.append((core_start, core_end, link))
        report['applied'].append((rp, raw_tok, num_preview, target))

    if not edits:
        return

    edits.sort()
    out = []
    cursor = 0
    for start, end, repl in edits:
        out.append(text[cursor:start])
        out.append(repl)
        cursor = end
    out.append(text[cursor:])
    new_text = ''.join(out)

    if apply_ and new_text != text:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='실제 파일 수정(기본은 dry-run)')
    ap.add_argument('--text-report', default=None)
    args = ap.parse_args()

    all_files, basename_map, prefix_map = build_maps()

    report = {'applied': [], 'ambiguous': [], 'self': []}
    for path, rp in all_files:
        process_file(path, rp, basename_map, prefix_map, args.apply, report)

    mode = 'APPLY' if args.apply else 'DRY-RUN'
    out = []
    out.append(f"=== convert_section_refs.py [{mode}] ===")
    out.append(f"vault files: {len(all_files)}  prefix keys(safe): {len(prefix_map)}  basename keys: {len(basename_map)}")
    out.append(f"\nconverted: {len(report['applied'])}")
    for rp, raw, num, target in report['applied']:
        out.append(f"  {rp}  ::  {raw!r} §{num}  ->  {target}")
    out.append(f"\nself-reference (skipped, target==source): {len(report['self'])}")
    for rp, raw, num in report['self']:
        out.append(f"  {rp}  ::  {raw!r} §{num}")
    out.append(f"\nambiguous (skipped — multiple candidates, no folder disambiguation): {len(report['ambiguous'])}")
    for rp, raw, num, cands in report['ambiguous']:
        out.append(f"  {rp}  ::  {raw!r} §{num}  candidates={cands}")

    text = '\n'.join(out)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('cp949', errors='replace'))

    if args.text_report:
        with open(args.text_report, 'w', encoding='utf-8') as f:
            f.write(text + '\n')


if __name__ == '__main__':
    main()
