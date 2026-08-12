#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalize_status_type.py — BT-DOC2 SSOT(§3~§8) 실행: frontmatter status/type enum 정규화.

원본 규칙 문서: docs/features/전투완성/raw/BT-DOC2_status매핑규칙.md (SSOT — 여기서 규칙을 새로 만들지 않는다)

사용법:
  python normalize_status_type.py --dry-run       # 기본값과 동일. 아무 파일도 쓰지 않는다.
  python normalize_status_type.py --apply         # 실제 파일 수정.
  python normalize_status_type.py --apply --verbose

멱등성: status 값이 이미 enum 7종 중 하나이면 그 파일은 완전히 건드리지 않는다(스킵).
        type 매핑은 32→9 고정 테이블이라 이미 9종 중 하나면 자기 자신으로 매핑되어 무해하다.
"""
import os
import re
import sys
import json
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))  # docs/scripts/vaultfix -> docs/

ENUMS = ["PASS", "WIP", "DRAFT", "BLOCKED", "AWAIT_OWNER", "SUPERSEDED", "ARCHIVED"]

FROZEN_FOLDERS = {"옥토패스대치", "기본전투무대", "턴제전투MVP", "카메라액션", "걸어나오기연출", "방향성1_백업"}

# ── PM 판정 #1: "?" 표시 보류 — 완전 무접촉 (§9 VFX_임시통합_방침 + §5 공격버튼데모 2건) ──
HELD_FILES = {
    "features/턴제전투MVP/raw/VFX_임시통합_방침.md",
    "features/공격버튼데모/plan.md",
    "features/공격버튼데모/raw/D2_구현.md",
}

# ── §4 type 32종 → 9종 ──
TYPE_GROUPS = {
    "plan":      ["plan", "blueprint", "roadmap", "ops_plan"],
    "design":    ["design", "spec", "decision"],
    "gate":      ["gate"],
    "test":      ["test", "tc", "test-cases", "verification"],
    "review":    ["qa", "review", "codex_review_mirror"],
    "record":    ["raw", "log", "report", "retro", "snapshot", "backup", "investigation", "portfolio", "codex_mcp_connection_mirror"],
    "index":     ["index", "moc", "hub"],
    "reference": ["reference", "guide", "owner_guide"],
    "process":   ["process", "convention"],
}
TYPE_MAP = {src: tgt for tgt, srcs in TYPE_GROUPS.items() for src in srcs}

# ── §6 수동 50건 director 사전판정 (VFX_임시통합_방침 held 제외 = 49건) ──
# path -> (enum, superseded_by 또는 None, 추가 note 또는 None)
MANUAL_MAP = {
    "기획_방향성.md": ("PASS", None, None),
    "데이터규약_예시.md": ("SUPERSEDED", "[[데이터_서버_규약]]", None),
    "로드맵_버전계획.md": ("PASS", None, None),
    "알파_개발계획.md": ("WIP", None, "A1 진행 중인 살아있는 계획"),
    "오너_대기목록.md": ("WIP", None, "상시 롤링 문서"),
    "자율작업배치_2026-07-17.md": ("PASS", None, "전 트랙 완료"),
    "자율진행_plan_v2.md": ("WIP", None, "AT/FT 트랙 진행 중"),

    "features/HD2D배경/raw/룩_지침_2D타일셋.md": ("ARCHIVED", None, None),
    "features/HD2D배경/raw/오너_2D배경_튜닝가이드.md": ("ARCHIVED", None, None),

    "features/걸어나오기연출/TC.md": ("ARCHIVED", None, "동결. W3 이월분은 아래 원문 참고"),
    "features/걸어나오기연출/청사진.md": ("ARCHIVED", None, "WF 잔여는 아래 원문 + 오너_대기목록 이관 확인"),

    "features/옥토패스대치/plan.md": ("ARCHIVED", None, "기능 동결 — 아래 원문의 '진행중'은 스테일"),
    "features/옥토패스대치/배치가이드.md": ("ARCHIVED", None, None),
    "features/옥토패스대치/청사진.md": ("ARCHIVED", None, "기능 동결 — 아래 원문의 '진행중'은 스테일"),

    "features/턴제전투MVP/plan.md": ("ARCHIVED", None, None),
    "features/턴제전투MVP/청사진.md": ("ARCHIVED", None, None),
    "features/턴제전투MVP/TC.md": ("ARCHIVED", None, "E3 실증 미완인 채 동결"),

    "features/스킬연출구조/E_스파이크_plan.md": ("WIP", None, "S2 진행 중 · S3~S6 재검토 대기"),
    "features/스킬연출구조/raw/D5_값배정.md": ("PASS", None,
        "FxCastId=0 반전 정정 반영 + 내장트레일 파급 재검토 중 — [[BT-DOC1_정본경계설계]] §5-5"),

    "features/전투완성/plan.md": ("WIP", None, None),  # 3,727자 — 본문 이관 별도 처리(LONG_VALUE_FILES)
    "features/전투완성/청사진.md": ("PASS", None, "문서 확정 — 진행은 plan·status층 소관"),

    "features/전투완성/raw/AU-A1-09_T1전후_실측대조.md": ("PASS", None, None),
    "features/전투완성/raw/BP정리_통합명세_2026-08-11.md": ("PASS", None, None),
    "features/전투완성/raw/BT3_MA_상세설계서.md": ("PASS", None, "PM 확인 요청 4건 — 아래 원문 참고"),
    "features/전투완성/raw/F5-1_완료.md": ("PASS", None, None),
    "features/전투완성/raw/FT1_착수조회_2026-08-12.md": ("PASS", None, None),
    "features/전투완성/raw/qa_스탯공식검토.md": ("PASS", None, None),
    "features/전투완성/raw/스탯_전투공식_v1.md": ("PASS", None, None),
    "features/전투완성/raw/야간작업_총결산_2026-07-16.md": ("PASS", None, "정정으로 오너결정 대기 2건 해소 명시"),
    "features/전투완성/raw/파트2_SPD_완료.md": ("PASS", None, None),
    "features/전투완성/raw/파트3_연출_완료.md": ("PASS", None, None),
    "features/전투완성/raw/파트4_라벨힐_완료.md": ("PASS", None, None),
    "features/전투완성/raw/F7_스킬아키텍처_확정.md": ("PASS", None, None),
    "features/전투완성/raw/상태이상_설계_qa검증.md": ("PASS", None, "BLOCKER 2건은 [[상태이상_확정]]에서 해소"),

    "features/전투완성/raw/F4_TC.md": ("PASS", None, "'BLOCKER 5건 판정 필요'는 스테일 — 판정 완료·F4 통과"),
    "features/전투완성/raw/F5_TC.md": ("PASS", None, "동(BLOCKER 판정 완료)"),
    "features/전투완성/raw/F5-2_TC.md": ("PASS", None, None),
    "features/전투완성/raw/F7_TC.md": ("PASS", None, None),
    "features/전투완성/raw/U단계_TC.md": ("PASS", None, "'확정 대기'는 스테일"),
    "features/전투완성/raw/파트1_Start_TC.md": ("PASS", None, None),
    "features/전투완성/raw/파트2_SPD_TC.md": ("PASS", None, None),
    "features/전투완성/raw/파트3_연출_TC.md": ("PASS", None, None),
    "features/전투완성/raw/파트4_라벨힐_TC.md": ("PASS", None, None),

    "features/전투완성/raw/F4_중단_인수인계.md": ("ARCHIVED", None, "정정 각주로 역할 종료"),
    "features/전투완성/raw/F5_착수지시서.md": ("ARCHIVED", None, "'착수 대기'는 스테일 — F5 완료"),
    "features/전투완성/raw/F7b_데이터초안_노트.md": ("DRAFT", None, "라이브 미반영 초안, 유효"),
    "features/전투완성/raw/F7b_재개계획_초안.md": ("BLOCKED", None,
        "BLOCKED 근거(director 지정): 선행=S1 원장 봉인 — 오너 20턴 런은 [[BT5_S1봉인수단_판별]]의 AWAIT_OWNER가 추적. 대기 사유 1건은 문서 1개만 담당"),

    "방향성1_백업/방향성1_로드맵_버전계획.md": ("SUPERSEDED", "[[로드맵_버전계획]]", "원문 '대체됨' 명시(방향성2로 대체) — superseded_by는 파일명 대응으로 추론(PM 보고 대상)"),
    "방향성1_백업/방향성1_알파_개발계획.md": ("SUPERSEDED", "[[알파_개발계획]]", "원문 '대체됨' 명시(방향성2로 대체) — superseded_by는 파일명 대응으로 추론(PM 보고 대상)"),
}

# ── §5 정오표 — 자동 결과를 덮는 확증 스테일 override (4건 확정, 5번째 행은 HELD) ──
OVERRIDE_MAP = {
    "features/전투완성/raw/상태이상_타겟범위_설계안.md": ("SUPERSEDED", "[[상태이상_확정]]", "병합 완료 2026-07-14"),
    "features/전투완성/raw/상태이상_카탈로그_밸런스.md": ("SUPERSEDED", "[[상태이상_확정]]", "병합 완료 2026-07-14(동)"),
    "features/스킬연출구조/청사진.md": ("SUPERSEDED", "[[features/스킬연출구조/plan|plan]]", "3슬롯 스테일 — 허브 표1이 명시"),
    "features/걸어나오기연출/plan.md": ("ARCHIVED", None, "기능 동결(plan v4 §대상). WF 잔여는 아래 status_note 원문 참고"),
}

# ── 1,000자 초과 값 — 본문으로 이관(잘라내기 금지) ──
LONG_VALUE_THRESHOLD = 1000
LONG_VALUE_FILES = {
    "features/전투완성/plan.md": {
        "summary": "F0~F9a 게이트 전부 통과, 잔여 F9b(오너 육안 풀플레이)·S1 SPD 오라클런 검증. 원문(3,727자)은 본문 §부록 참고(2026-08-13 frontmatter enum화로 이관).",
    },
}

# ── 원문이 이미 정확히 이 토큰이면(트리비얼 매핑) status_note 생략 ──
TRIVIAL_EXACT = {
    "완료": "PASS", "초안": "DRAFT", "진행중": "WIP", "진행 중": "WIP",
    "active": "WIP", "Active": "WIP",
}

SEP_CHARS = ['—', '·', ',', '/', '(']


def get_leading(value):
    idx = len(value)
    for ch in SEP_CHARS:
        i = value.find(ch)
        if i != -1 and i < idx:
            idx = i
    return value[:idx].strip()


# ── A규칙 (순서 고정, 첫 일치 승리) ──
def a1(value, leading):
    if re.search(r'대체됨|superseded|백업/구버전', value, re.IGNORECASE):
        return "SUPERSEDED"
    return None


def a2(value, leading):
    if re.match(r'^(종결|종료|기각)', leading):
        return "ARCHIVED"
    if re.search(r'오너 기각|트랙 종료 —', value):
        return "ARCHIVED"
    return None


def a3(value, leading):
    if re.search(r'(verifier|실증|검증)\s*대기', value):
        return "WIP"
    return None


def a4(value, leading):
    if re.search(r'오너[^.·—/~]{0,25}?(대기|필요)', value):
        return "AWAIT_OWNER"
    return None


def a6(value, leading):
    pat = (r'(PASS|통과|완료|확정|산출|승인|채택|해소|봉인|판정|개정|기록|스냅샷)'
           r'[\s\d\-:.년월일시경야간()~]*$|^(판정|결재)\b|^(complete|configured)')
    if re.search(pat, leading):
        if re.search(r'진행\s?중|착수 예정', value):
            return "WIP"  # A6b guard
        return "PASS"
    return None


def a7(value, leading):
    if re.match(r'^(진행 ?중|active|활성|골격 완료|부분 통과|부분 판정|신설)', leading, re.IGNORECASE):
        return "WIP"
    return None


def a8(value, leading):
    if re.match(r'^(초안|초판|DRAFT|잠정|provisional)', leading, re.IGNORECASE):
        return "DRAFT"
    return None


ORDERED_A_RULES = [("A1", a1), ("A2", a2), ("A3", a3), ("A4", a4), ("A6", a6), ("A7", a7), ("A8", a8)]


def compute_auto(value):
    leading = get_leading(value)
    for rule_id, fn in ORDERED_A_RULES:
        result = fn(value, leading)
        if result:
            return result, rule_id
    return None, None


def m_checks(rp, value):
    auto_result, auto_rule = compute_auto(value)
    m1 = len(value) > 300
    m2 = ('~~' in value) or ('❌' in value)
    m3 = re.search('정정', value) is not None
    folder = None
    parts = rp.split('/')
    if parts[0] == 'features' and len(parts) > 1:
        folder = parts[1]
    elif parts[0] in FROZEN_FOLDERS:
        folder = parts[0]
    m4 = (folder in FROZEN_FOLDERS) and (auto_result in ("WIP", "BLOCKED", "AWAIT_OWNER"))
    m5 = re.search(r'BLOCKER|차단|막힘|착수 대기|진입 조건|선행 조건|선행 필요', value) is not None
    m9 = auto_result is None
    manual_trigger = m1 or m2 or m3 or m4 or m5 or m9
    return {
        "auto_result": auto_result, "auto_rule": auto_rule,
        "m1": m1, "m2": m2, "m3": m3, "m4": m4, "m5": m5, "m9": m9,
        "manual_trigger": manual_trigger,
    }


# ── YAML 안전 처리 ──
def needs_quoting(text):
    if not text:
        return False
    if text[0] in '-?:,[]{}#&*!|>\'"%@`':
        return True
    if re.search(r':\s', text):
        return True
    if text.rstrip().endswith(':'):
        return True
    if '\n' in text:
        return True
    return False


def yaml_scalar(text):
    if needs_quoting(text):
        escaped = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return text


# ── frontmatter 파싱 ──
FM_FULL_RE = re.compile(r'(^---\r?\n)(.*?)(\r?\n---\r?\n)', re.DOTALL)


def load_file(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def find_field_line(lines, field):
    pat = re.compile(rf'^{re.escape(field)}:\s*(.*)$')
    for i, line in enumerate(lines):
        m = pat.match(line)
        if m:
            return i, m.group(1)
    return None, None


def resolve_status(rp, raw_value):
    """returns dict describing what to do, or None if no change needed."""
    value = raw_value.strip()

    if value in ENUMS:
        return {"action": "SKIP_ALREADY_ENUM"}

    trace = m_checks(rp, value)

    if rp in MANUAL_MAP:
        enum_val, supersede, extra = MANUAL_MAP[rp]
        source = "MANUAL_50"
    elif rp in OVERRIDE_MAP:
        enum_val, supersede, extra = OVERRIDE_MAP[rp]
        source = "OVERRIDE_5"
    else:
        if trace["manual_trigger"]:
            return {"action": "UNHANDLED_MANUAL", "trace": trace, "value": value}
        enum_val = trace["auto_result"]
        supersede, extra = None, None
        source = f"AUTO_{trace['auto_rule']}"
        # 안전장치(BT-DOC2 §7-2 요구사항에서 도출): SUPERSEDED는 superseded_by가 필수인데
        # AUTO 경로는 대체 대상 문서를 알 수 없다. A1("대체됨" 등)이 본문 서술(과거사 묘사)에서
        # 오탐할 수 있으므로, MANUAL_MAP/OVERRIDE_MAP에 없는 AUTO-SUPERSEDED는 임의 적용하지 않는다.
        if enum_val == "SUPERSEDED":
            return {"action": "UNHANDLED_MANUAL", "trace": trace, "value": value,
                    "reason": "AUTO_A1이 SUPERSEDED로 판정했으나 superseded_by 대상을 알 수 없음(본문 서술 오탐 의심) — 임의 배정 금지"}

    if enum_val not in ENUMS:
        return {"action": "ERROR_BAD_ENUM", "enum": enum_val, "trace": trace}

    # note 필요 여부
    is_trivial = (value in TRIVIAL_EXACT) and (TRIVIAL_EXACT[value] == enum_val) and not extra and not supersede
    note = None
    if not is_trivial:
        note = value
        if extra:
            note = f"{value} — [director 판정] {extra}" if not extra.startswith("BLOCKED 근거") else f"{extra} | 원문: {value}"

    long_special = rp in LONG_VALUE_FILES
    if long_special:
        note = LONG_VALUE_FILES[rp]["summary"]

    return {
        "action": "APPLY",
        "enum": enum_val,
        "note": note,
        "supersede_by": supersede,
        "source": source,
        "trace": trace,
        "long_special": long_special,
        "orig_value": value,
    }


def process_file(path, rp, apply, report, verbose):
    text = load_file(path)
    m = FM_FULL_RE.match(text)
    if not m:
        report["no_frontmatter"].append(rp)
        return

    prefix, fm_content, suffix = m.group(1), m.group(2), m.group(3)
    rest = text[m.end():]
    eol = '\r\n' if '\r\n' in prefix else '\n'
    lines = fm_content.split(eol)

    changed = False
    body_append = None

    # ---- TYPE pass ----
    if rp not in HELD_FILES:
        t_idx, t_val = find_field_line(lines, 'type')
        if t_val is not None:
            t_val_stripped = t_val.strip()
            mapped = TYPE_MAP.get(t_val_stripped)
            if mapped is None:
                report["type_unmapped"].append((rp, t_val_stripped))
            elif mapped != t_val_stripped:
                report["type_changed"].append((rp, t_val_stripped, mapped))
                if apply:
                    lines[t_idx] = f'type: {mapped}'
                    changed = True
        else:
            report["type_missing"].append(rp)

    # ---- STATUS pass ----
    if rp in HELD_FILES:
        report["held"].append(rp)
    else:
        s_idx, s_val = find_field_line(lines, 'status')
        if s_val is None:
            report["status_missing"].append(rp)
        else:
            result = resolve_status(rp, s_val)
            action = result["action"]
            if action == "SKIP_ALREADY_ENUM":
                report["already_enum"].append(rp)
            elif action == "UNHANDLED_MANUAL":
                report["unhandled_manual"].append((rp, result["value"], result["trace"], result.get("reason")))
            elif action == "ERROR_BAD_ENUM":
                report["errors"].append((rp, "bad enum", result))
            elif action == "APPLY":
                report["applied"].append((rp, result["orig_value"], result["enum"], result["source"], result["note"], result["supersede_by"], result["long_special"]))
                if apply:
                    lines[s_idx] = f'status: {result["enum"]}'
                    insert_at = s_idx + 1
                    new_lines = []
                    if result["note"]:
                        new_lines.append(f'status_note: {yaml_scalar(result["note"])}')
                    if result["supersede_by"]:
                        new_lines.append(f'superseded_by: {yaml_scalar(result["supersede_by"])}')
                    for offset, nl in enumerate(new_lines):
                        lines.insert(insert_at + offset, nl)
                    changed = True
                    if result["long_special"]:
                        heading = "## 부록 — 구 frontmatter `status` 원문 (2026-08-13, 3단계 status enum화로 이관)"
                        note_line = (f"> 원본 frontmatter `status` 필드가 {len(result['orig_value'])}자로 M1(300자 초과) 규칙 임계를 "
                                     f"크게 넘어 본문으로 이관했다({LONG_VALUE_THRESHOLD}자 초과 규칙 적용). "
                                     f"frontmatter `status_note`는 요약만 담는다. 전문은 아래(무수정).")
                        body_append = f"\n\n{heading}\n\n{note_line}\n\n{result['orig_value']}\n"

    if apply and changed:
        new_fm = eol.join(lines)
        new_text = prefix + new_fm + suffix + rest
        if body_append:
            new_text = new_text.rstrip('\n').rstrip('\r') + (eol * 2) + body_append.lstrip('\n').replace('\n', eol)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_text)


def walk_docs():
    for root, dirs, files in os.walk(DOCS_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for fn in sorted(files):
            if fn.endswith('.md'):
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, DOCS_ROOT).replace('\\', '/')
                yield path, rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='실제 파일 수정 (기본은 dry-run)')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--json-report', default=None, help='결과를 JSON으로 저장할 경로')
    ap.add_argument('--text-report', default=None, help='결과를 UTF-8 텍스트로 저장할 경로(콘솔 인코딩 우회용)')
    args = ap.parse_args()
    apply = args.apply

    report = {
        "held": [], "already_enum": [], "status_missing": [],
        "unhandled_manual": [], "errors": [], "applied": [],
        "type_changed": [], "type_missing": [], "type_unmapped": [],
        "no_frontmatter": [],
    }

    for path, rp in walk_docs():
        process_file(path, rp, apply, report, args.verbose)

    mode = "APPLY" if apply else "DRY-RUN"
    out = []
    out.append(f"=== normalize_status_type.py [{mode}] ===")
    out.append(f"held (무접촉, ? 보류): {len(report['held'])}")
    for f in report['held']:
        out.append(f"  - {f}")
    out.append(f"already enum (스킵): {len(report['already_enum'])}")
    for f in report['already_enum']:
        out.append(f"  - {f}")
    out.append(f"status 없음 (범위 밖, 미부여): {len(report['status_missing'])}")
    out.append(f"applied (status 변경): {len(report['applied'])}")
    out.append(f"unhandled_manual (규칙 미적용 케이스!): {len(report['unhandled_manual'])}")
    for rp, val, trace, reason in report['unhandled_manual']:
        r = f" reason={reason}" if reason else ""
        out.append(f"  ! {rp} :: {val[:120]!r}{r} trace={trace}")
    out.append(f"errors: {len(report['errors'])}")
    for e in report['errors']:
        out.append(f"  ! {e}")
    out.append(f"type changed: {len(report['type_changed'])}")
    out.append(f"type missing (범위 밖): {len(report['type_missing'])}")
    for f in report['type_missing']:
        out.append(f"  - {f}")
    out.append(f"type unmapped (미확인 값!): {len(report['type_unmapped'])}")
    for f, v in report['type_unmapped']:
        out.append(f"  ! {f} :: {v}")

    from collections import Counter
    dist = Counter(a[2] for a in report['applied'])
    out.append("\n--- applied enum distribution ---")
    for k in ENUMS:
        out.append(f"  {k}: {dist.get(k, 0)}")

    out.append(f"no_frontmatter (frontmatter 자체 없음 — 범위 밖): {len(report['no_frontmatter'])}")
    for f in report['no_frontmatter']:
        out.append(f"  - {f}")

    total_accounted = (len(report['held']) + len(report['already_enum']) + len(report['status_missing'])
                        + len(report['applied']) + len(report['unhandled_manual']) + len(report['errors'])
                        + len(report['no_frontmatter']))
    out.append(f"\ntotal md accounted (status side): {total_accounted}")

    text = "\n".join(out)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('cp949', errors='replace'))

    if args.text_report:
        with open(args.text_report, 'w', encoding='utf-8') as f:
            f.write(text + "\n")

    if args.json_report:
        def ser(o):
            return o
        with open(args.json_report, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=ser)
        print(f"\nJSON report -> {args.json_report}")


if __name__ == '__main__':
    main()
