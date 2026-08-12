#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
generate_index.py — 문서구조_개선plan v4 5단계: 루트 `docs/INDEX.md`를 frontmatter에서 자동생성한다.

목적: LLM이 볼트를 탐색할 때 인덱스를 먼저 읽고 필요한 문서만 골라 읽게 한다(Karpathy LLM Wiki 패턴).
      손으로 쓰면 파일이 하나 늘 때마다 드리프트하므로 반드시 스크립트로 생성한다.

무엇을 하는가:
  1. `docs/` 아래 모든 `.md`를 스캔해 frontmatter(`type`·`status`·`status_note`)를 읽는다.
     (INDEX.md 자기 자신도 재실행 시 포함된다 — type: index 그룹에 자연히 속한다.)
  2. 한 줄 요약의 출처는 이 우선순위:
       ① frontmatter `status_note` (있으면 그대로)
       ② 문서 첫 `#` 헤딩 다음에 오는 첫 비어있지 않은 줄(마크다운 인용/목록 기호는 벗겨서)
       ③ 없으면 빈칸으로 두고 카운트만 한다(억지로 만들지 않는다)
  3. `type`(정규화 9종 + 미분류)별로 묶어 표로 낸다. 표 안 위키링크는 전부 `[[경로\|표시]]` 형태로
     통일한다 — 동명 파일이 많아 경로 필수이고, 표 셀 안이라 파이프를 이스케이프해야 렌더가 안 깨진다.
  4. summary 텍스트에 우연히 `|`가 있으면 그것도 이스케이프한다.

사용법:
  python generate_index.py                # dry-run: 콘솔에 통계만 출력, 파일 쓰기 없음
  python generate_index.py --apply         # docs/INDEX.md 실제 생성/갱신

멱등성: 같은 날 두 번 실행하면 바이트 단위로 동일한 파일이 나온다(정렬 고정, `updated`는 오늘 날짜
        고정이라 같은 날 재실행에서는 diff 0).
"""
import os
import re
import sys
import argparse
from datetime import date
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))  # docs/scripts/vaultfix -> docs/
INDEX_PATH = os.path.join(DOCS_ROOT, 'INDEX.md')

TYPE_ORDER = ["plan", "design", "gate", "test", "review", "record", "index", "reference", "process"]
TYPE_LABEL = {
    "plan": "계획 (plan)",
    "design": "설계 (design)",
    "gate": "게이트 판정 (gate)",
    "test": "테스트/TC (test)",
    "review": "리뷰/QA (review)",
    "record": "기록·로그 (record)",
    "index": "인덱스/허브 (index)",
    "reference": "참고자료 (reference)",
    "process": "규약/프로세스 (process)",
}
UNCLASSIFIED = "(미분류)"


def walk_md():
    for root, dirs, files in os.walk(DOCS_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for fn in sorted(files):
            if fn.endswith('.md'):
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, DOCS_ROOT).replace('\\', '/')
                yield path, rel


FM_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n', re.DOTALL)


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    fm_text = m.group(1)
    meta = {}
    for line in fm_text.split('\n'):
        line = line.rstrip('\r')
        km = re.match(r'^([A-Za-z0-9_][\w.-]*):\s*(.*)$', line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        elif val.startswith("'") and val.endswith("'") and len(val) >= 2:
            val = val[1:-1]
        meta[key] = val
    return meta, body


HEADING_RE = re.compile(r'^#\s+(.*)$', re.MULTILINE)

# "한 줄 요약" 상한 — status_note 원문 중엔 정정 이력이 누적돼 500자를 넘는 것도 있다(예:
# 자율진행_plan_v2). frontmatter 원문은 절대 건드리지 않지만(읽기만), INDEX 표 칸에 그대로
# 박으면 "한 줄"이 아니게 되므로 표시용으로만 첫 문장 selector + 길이 상한을 적용한다.
SUMMARY_MAXLEN = 200
SENTENCE_CUT_RE = re.compile(r'(다\.|음\.|임\.|요\.|\.)(\s|$)')


def first_sentence(line, maxlen=SUMMARY_MAXLEN):
    cut = SENTENCE_CUT_RE.search(line)
    sentence = line[:cut.end(1)] if cut else line
    if len(sentence) > maxlen:
        sentence = sentence[:maxlen - 1] + '…'
    return sentence


def first_heading_next_sentence(body):
    m = HEADING_RE.search(body)
    if not m:
        return None
    rest = body[m.end():]
    for line in rest.split('\n'):
        line = line.strip()
        if not line:
            continue
        # 인용/목록/헤딩 기호 벗기기
        line = re.sub(r'^[>\-*#\s]+', '', line).strip()
        if not line:
            continue
        return first_sentence(line)
    return None


def esc(text):
    if text is None:
        return ''
    return text.replace('|', r'\|')


def build_rows(all_files):
    groups = defaultdict(list)
    blank_summary = 0
    for path, rp in all_files:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        meta, body = parse_frontmatter(text)
        typ = meta.get('type', '').strip()
        status = meta.get('status', '').strip()
        status_note = meta.get('status_note', '').strip()

        summary = first_sentence(status_note) if status_note else first_heading_next_sentence(body)
        if not summary:
            summary = ''
            blank_summary += 1

        group_key = typ if typ in TYPE_ORDER else UNCLASSIFIED
        base = os.path.basename(rp)[:-3]
        link_target = rp[:-3]
        groups[group_key].append({
            'rp': rp, 'type': typ, 'status': status,
            'summary': summary, 'base': base, 'link_target': link_target,
        })

    for g in groups.values():
        g.sort(key=lambda r: r['rp'].lower())

    return groups, blank_summary


def render_index(groups, total, blank_summary):
    today = date.today().isoformat()
    lines = []
    lines.append('---')
    lines.append('type: index')
    lines.append('status: PASS')
    lines.append('project: projectTP')
    lines.append(f'updated: {today}')
    lines.append('status_note: docs/scripts/vaultfix/generate_index.py로 frontmatter에서 자동생성 — 손으로 편집하지 않는다')
    lines.append('---')
    lines.append('')
    lines.append('# INDEX — projectTP 옵시디언 볼트 전체 목록')
    lines.append('')
    lines.append('> ★자동생성 문서. 손으로 편집하지 마라 — 다음 `generate_index.py --apply` 실행에서 덮어써진다.')
    lines.append(f'> 총 {total}개 문서, `type`별로 묶었다. 표의 "요약"은 frontmatter `status_note`가 있으면 그 첫 문장,')
    lines.append(f'> 없으면 문서 첫 헤딩 다음 문장을 썼다(둘 다 {SUMMARY_MAXLEN}자 상한 — 표시용 절삭이며 frontmatter 원문은 무수정).')
    lines.append('> 둘 다 없으면 빈칸이다(추측해서 채우지 않는다). 전문은 각 문서의 frontmatter/본문에서 확인.')
    lines.append('')
    lines.append(f'| 항목 | 값 |')
    lines.append(f'|---|---|')
    lines.append(f'| 총 문서 수 | {total} |')
    lines.append(f'| 요약 빈칸 | {blank_summary} |')
    lines.append(f'| type 그룹 수 | {len(groups)} |')
    lines.append('')

    ordered_keys = [k for k in TYPE_ORDER if k in groups] + ([UNCLASSIFIED] if UNCLASSIFIED in groups else [])
    for key in ordered_keys:
        rows = groups[key]
        label = TYPE_LABEL.get(key, key) if key != UNCLASSIFIED else UNCLASSIFIED
        lines.append(f'## {label} ({len(rows)})')
        lines.append('')
        lines.append('| 문서 | status | 요약 |')
        lines.append('|---|---|---|')
        for r in rows:
            link = f"[[{r['link_target']}\\|{r['base']}]]"
            lines.append(f"| {link} | {esc(r['status'])} | {esc(r['summary'])} |")
        lines.append('')

    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='실제로 docs/INDEX.md를 쓴다(기본은 dry-run)')
    args = ap.parse_args()

    all_files = list(walk_md())
    groups, blank_summary = build_rows(all_files)
    total = sum(len(v) for v in groups.values())

    out = render_index(groups, total, blank_summary)

    print(f"=== generate_index.py [{'APPLY' if args.apply else 'DRY-RUN'}] ===")
    print(f"total files scanned: {len(all_files)}  total rows: {total}")
    print(f"blank summary: {blank_summary}")
    for key in TYPE_ORDER + [UNCLASSIFIED]:
        if key in groups:
            print(f"  {key}: {len(groups[key])}")

    if args.apply:
        with open(INDEX_PATH, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        print(f"\nwrote {INDEX_PATH}")
    else:
        print("\n(dry-run — no file written; pass --apply to write docs/INDEX.md)")


if __name__ == '__main__':
    main()
