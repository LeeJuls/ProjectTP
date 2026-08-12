"""BT2 TC 게이트(AU-B2-01~06) + balance R-3 음성시험 자가실행 스크립트.

LOG-A_실행계획.md ★TC 게이트: 전부 `M`(machine) 주체 — MCP 불요, 이 스크립트만으로 재현 가능.

사용법:
    python battle_log_selftest.py

이 스크립트는:
    - 픽스처를 오라클 §7 CSV(§0 job_table 포함)에서 **파생 생성**한다(손으로 옮겨 적지 않음 —
      전사 오류 위험 제거, "정본을 직접 파싱"의 취지를 자가시험에도 적용).
    - R-3만 예외로 실제 관측 로그(battle_20260716_123951.log)를 원본 그대로 읽고,
      스크래치 디렉터리에 프리픽스만 치환한 사본을 만든다(원본 로그 파일 무수정).
    - 산출물은 전부 스크래치 디렉터리에 쓴다(레포·Saved/ 오염 없음).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(r"D:\unreal\Resource\docs\scripts")
sys.path.insert(0, str(SCRIPTS_DIR))

from battle_log import io_utils, oracle, parser, session, tokens  # noqa: E402
import extract_battle_log  # noqa: E402

io_utils.ensure_utf8_stdout()

ORACLE_MD = r"D:\unreal\Resource\docs\features\전투완성\raw\SPD원장_오라클_v1.md"
REAL_EXTRACTED_LOG = r"D:\unreal\projectTP\Saved\BattleLogs\battle_20260716_123951.log"
ORACLE_DIFF_PY = str(SCRIPTS_DIR / "oracle_diff.py")

SCRATCH = Path(os.environ.get(
    "BATTLE_LOG_SCRATCH",
    r"C:\Users\user\AppData\Local\Temp\claude\D--unreal-Resource\7246227d-0e35-430a-a874-e287b4339af8\scratchpad\battle_log_fixtures",
))
SCRATCH.mkdir(parents=True, exist_ok=True)

_BATTLE_ROW = tokens.row_by_number("11")
_BATTLE_PREFIX = _BATTLE_ROW.prefixes[0]

RESULTS: list[tuple[str, bool, str]] = []


def record(tc_id: str, ok: bool, detail: str):
    RESULTS.append((tc_id, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {tc_id}: {detail}")


def fake_prefix(seq: int) -> str:
    """실측 포맷과 동일한 형태의 프리픽스를 합성(타임스탬프는 시험용 더미)."""
    return f"[2026.01.01-00.00.{seq % 60:02d}:000][{seq % 999:3d}]LogBlueprintUserMessages: [BP_BattleManager_C_0] "


def synth_log_line(seq: int, row: dict, extra_fields: str = "") -> str:
    """오라클 행(dict) 1개를 합성 원장 라인(프리픽스 포함)으로 역변환."""
    attacker = oracle.slot_to_raw_label(row["attacker"])
    target = oracle.slot_to_raw_label(row["target"])
    parts = [
        f"turn={row['T']}",
        f"attacker={attacker}",
        f"target={target}",
        "action=31000000",
        f"dmg={row['dmg']}",
        f"hp={row['target_hp_after']}",
    ]
    if extra_fields:
        parts.append(extra_fields)
    if row.get("died"):
        parts.append("died=true")
    content = _BATTLE_PREFIX + "|".join(parts)
    return fake_prefix(seq) + content


def write_lines(path: Path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def run_oracle_diff(oracle_path: str, log_path: str, jobtable: str | None = None):
    cmd = [sys.executable, ORACLE_DIFF_PY, "--oracle", oracle_path, "--log", log_path]
    if jobtable:
        cmd += ["--jobtable", jobtable]
    # ★자식 프로세스도 UTF-8로 출력하게 강제한다.
    #   이걸 안 하면 한국어 Windows(콘솔 cp949)에서 자식이 cp949로 쓰고 부모는 utf-8로
    #   읽어 UnicodeDecodeError → proc.stdout=None → "argument of type 'NoneType'"로 크래시한다.
    #   실제 발생(2026-08-12): 구현 에이전트 환경에선 30/30 PASS인데 PM 환경에선 전량 크래시.
    #   재현되지 않는 테스트는 게이트가 아니므로 환경 의존을 제거한다.
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    proc = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# 준비: 오라클 §0 job_table + §7 20행 로드 (정본을 직접 파싱 — 하드코딩 0)
# ---------------------------------------------------------------------------
oracle_text = Path(ORACLE_MD).read_text(encoding="utf-8")
JOB_TABLE = oracle.parse_job_table(oracle_text)
ORACLE_ROWS = oracle.load_oracle_rows(ORACLE_MD)
print(f"job_table ({len(JOB_TABLE)}슬롯): {JOB_TABLE}")
print(f"oracle rows: {len(ORACLE_ROWS)}")

GOLDEN_LINES = [synth_log_line(i, row) for i, row in enumerate(ORACLE_ROWS, start=1)]


# ---------------------------------------------------------------------------
# AU-B2-01 — 오라클 §7 20행 그대로 입력 → diff 0 ∧ 종료 코드 0
# ---------------------------------------------------------------------------
golden_path = write_lines(SCRATCH / "au_b2_01_golden.log", GOLDEN_LINES)
code, out, err = run_oracle_diff(ORACLE_MD, golden_path)
ok = (code == 0) and ("DIFF: 0" in out) and ("RESULT: PASS" in out)
record("AU-B2-01", ok, f"exit={code}, 'DIFF: 0' in stdout={'DIFF: 0' in out}\n{out}\n{err}")


# ---------------------------------------------------------------------------
# AU-B2-02 — 변조 3종: (a)행 삭제/추가 (b)값 변조 (c)순서 뒤바꿈
# ---------------------------------------------------------------------------
def mismatch_row_from_output(out: str):
    m = re.search(r"첫 불일치 행 번호 = (\d+)", out)
    return int(m.group(1)) if m else None


# (a-delete) T=19 행 삭제 → 첫 불일치는 19행(그 위치부터 밀림)
lines_a_del = [l for i, l in enumerate(GOLDEN_LINES, start=1) if i != 19]
path = write_lines(SCRATCH / "au_b2_02a_del19.log", lines_a_del)
code, out, err = run_oracle_diff(ORACLE_MD, path)
row = mismatch_row_from_output(out)
ok = (code == 1) and (row == 19)
record("AU-B2-02(a-삭제 19행)", ok, f"exit={code}, first_mismatch_row={row} (기대 19)\n{out}")

# (a-add) 21번째 스푸리어스 행 추가 → 20행까지는 일치, 21행에서 길이불일치 검출
extra_row = dict(ORACLE_ROWS[-1])
extra_row["T"] = "21"
lines_a_add = GOLDEN_LINES + [synth_log_line(21, extra_row)]
path = write_lines(SCRATCH / "au_b2_02a_add21.log", lines_a_add)
code, out, err = run_oracle_diff(ORACLE_MD, path)
row = mismatch_row_from_output(out)
ok = (code == 1) and (row == 21)
record("AU-B2-02(a-추가 21행)", ok, f"exit={code}, first_mismatch_row={row} (기대 21)\n{out}")

# (b) T13 dmg 36→35
row13 = dict(ORACLE_ROWS[12])
assert row13["T"] == "13", row13
mutated13 = dict(row13)
mutated13["dmg"] = str(int(row13["dmg"]) - 1)
lines_b = list(GOLDEN_LINES)
lines_b[12] = synth_log_line(13, mutated13)
path = write_lines(SCRATCH / "au_b2_02b_dmg.log", lines_b)
code, out, err = run_oracle_diff(ORACLE_MD, path)
row = mismatch_row_from_output(out)
ok = (code == 1) and (row == 13)
record("AU-B2-02(b-값 변조 T13 dmg)", ok, f"exit={code}, first_mismatch_row={row} (기대 13)\n{out}")

# (c) T8 ↔ T9 순서 뒤바꿈
lines_c = list(GOLDEN_LINES)
lines_c[7], lines_c[8] = lines_c[8], lines_c[7]
path = write_lines(SCRATCH / "au_b2_02c_swap.log", lines_c)
code, out, err = run_oracle_diff(ORACLE_MD, path)
row = mismatch_row_from_output(out)
ok = (code == 1) and (row == 8)
record("AU-B2-02(c-순서 뒤바꿈 T8↔T9)", ok, f"exit={code}, first_mismatch_row={row} (기대 8)\n{out}")


# ---------------------------------------------------------------------------
# AU-B2-03 — 로그→오라클 스키마 매핑 단위시험 (5건)
# ---------------------------------------------------------------------------
ok1 = oracle.strip_slot("SpawnPoint_Party_A1") == "A1"
record("AU-B2-03①(Party_A1→A1)", ok1, f"strip_slot 결과={oracle.strip_slot('SpawnPoint_Party_A1')!r}")

ok2 = oracle.strip_slot("SpawnPoint_Enemy_B1") == "B1"
record("AU-B2-03②(Enemy_B1→B1)", ok2, f"strip_slot 결과={oracle.strip_slot('SpawnPoint_Enemy_B1')!r}")

ev_died = {"turn": "3", "attacker": "SpawnPoint_Party_A4", "target": "SpawnPoint_Enemy_B2",
           "action": "32001000", "dmg": "61", "hp": "0", "died": "true"}
ev_alive = {"turn": "1", "attacker": "SpawnPoint_Party_A3", "target": "SpawnPoint_Enemy_B2",
            "action": "31000000", "dmg": "32", "hp": "58"}
mapped_died = oracle.map_event_to_oracle_row(ev_died, JOB_TABLE)
mapped_alive = oracle.map_event_to_oracle_row(ev_alive, JOB_TABLE)
ok3 = (mapped_died["died"] == "B2") and (mapped_alive["died"] == "")
record("AU-B2-03③(died=true→target 값 / 부재→\"\")", ok3,
       f"died 있음→{mapped_died['died']!r}, died 없음→{mapped_alive['died']!r}")

ok4 = mapped_alive["target_hp_after"] == "58"
record("AU-B2-03④(hp→target_hp_after)", ok4, f"target_hp_after={mapped_alive['target_hp_after']!r}")

ok5 = (mapped_died["attacker_job"] == "MAG" and mapped_died["target_job"] == "WAR"
       and mapped_alive["attacker_job"] == "MAG" and mapped_alive["target_job"] == "WAR")
record("AU-B2-03⑤(attacker_job/target_job — §0 파싱 조인, 하드코딩 아님)", ok5,
       f"died행: attacker_job={mapped_died['attacker_job']!r} target_job={mapped_died['target_job']!r}")


# ---------------------------------------------------------------------------
# AU-B2-04 — action 전 행 불변식 ∧ berserk 필드 부재/1.0
# ---------------------------------------------------------------------------
sys.path.insert(0, str(SCRIPTS_DIR))
import oracle_diff  # noqa: E402

events_ok = [ev_alive, {**ev_alive, "turn": "2"}]  # 둘 다 action=31000000(even-trade 정상 케이스)
viol_ok = oracle_diff.check_invariants(events_ok)
ok = len(viol_ok) == 0
record("AU-B2-04(정상 — action=31000000, berserk 부재)", ok, f"violations={viol_ok}")

ev_bad_action = {**ev_alive, "action": "32001000"}
viol_bad = oracle_diff.check_invariants([ev_bad_action])
ok = len(viol_bad) == 1 and "action" in viol_bad[0]
record("AU-B2-04(action 위반 검출)", ok, f"violations={viol_bad}")

ev_berserk_ok = {**ev_alive, "berserk": "1.0"}
viol_berserk_ok = oracle_diff.check_invariants([ev_berserk_ok])
ok = len(viol_berserk_ok) == 0
record("AU-B2-04(berserk=1.0 정상)", ok, f"violations={viol_berserk_ok}")

ev_berserk_bad = {**ev_alive, "berserk": "1.5"}
viol_berserk_bad = oracle_diff.check_invariants([ev_berserk_bad])
ok = len(viol_berserk_bad) == 1 and "berserk" in viol_berserk_bad[0]
record("AU-B2-04(berserk≠1.0 위반 검출)", ok, f"violations={viol_berserk_bad}")


# ---------------------------------------------------------------------------
# AU-B2-05 — 무감각 열 고지가 산출물에 명시되는가
# ---------------------------------------------------------------------------
code, out, err = run_oracle_diff(ORACLE_MD, golden_path)
ok = "판정력이 없다" in out
record("AU-B2-05(attacker·target 무감각 열 고지)", ok, f"고지 문자열 포함 여부={ok}")


# ---------------------------------------------------------------------------
# AU-B2-06 — 미지 필드(effect/effectRoll/effectApplied) 섞여도 예외 0 ∧ 무시, berserk는 검사
# ---------------------------------------------------------------------------
row5 = dict(ORACLE_ROWS[4])
lines_unknown = list(GOLDEN_LINES)
lines_unknown[4] = synth_log_line(5, row5, extra_fields="effect=ATK_DOWN|effectRoll=-1|effectApplied=false")
path = write_lines(SCRATCH / "au_b2_06_unknown_fields.log", lines_unknown)
try:
    code, out, err = run_oracle_diff(ORACLE_MD, path)
    exc = None
except Exception as e:  # noqa: BLE001
    code, out, err, exc = None, "", "", e
ok = (exc is None) and (code == 0) and ("DIFF: 0" in out)
record("AU-B2-06(미지 필드 무시 ∧ 예외 0 ∧ diff 0 유지)", ok, f"exc={exc}, exit={code}\n{out}")


# ---------------------------------------------------------------------------
# R-3 음성시험 — 연출 타이밍(프리픽스)만 다른 두 로그 → diff 0
# ---------------------------------------------------------------------------
real_raw_lines = io_utils.read_raw_lines(REAL_EXTRACTED_LOG)
# 프리픽스(타임스탬프·프레임카운터)만 치환한 사본 생성. 원본 파일은 무수정(읽기 전용 접근).
_PREFIX_SUB_RE = re.compile(r"^\[[0-9.\-:]+\]\[\s*\d+\]")


def swap_prefix(line: str) -> str:
    return _PREFIX_SUB_RE.sub("[2099.12.31-23.59.59:999][  1]", line)


variant_a_lines = [l for l in real_raw_lines if not l.startswith("#")]
variant_b_lines = [swap_prefix(l) for l in variant_a_lines]

variant_a_path = write_lines(SCRATCH / "r3_variant_a.log", variant_a_lines)
variant_b_path = write_lines(SCRATCH / "r3_variant_b.log", variant_b_lines)

events_a = list(parser.iter_pipe_events(io_utils.read_raw_lines(variant_a_path), _BATTLE_PREFIX.rstrip("|")))
events_b = list(parser.iter_pipe_events(io_utils.read_raw_lines(variant_b_path), _BATTLE_PREFIX.rstrip("|")))
ok = (len(events_a) > 0) and (events_a == events_b)
record("R-3(프리픽스만 다른 두 로그 → 파싱 결과 diff 0)", ok,
       f"events_a={len(events_a)}건, events_b={len(events_b)}건, 완전일치={events_a == events_b}")

# 부가: 실제 프리픽스가 정말 다른지도 확인(변조가 no-op이 아니었는지 자기검증)
prefix_actually_changed = any(a != b for a, b in zip(variant_a_lines, variant_b_lines) if a.strip())
record("R-3(부가 — 변조가 실제로 프리픽스를 바꿨는지 자기검증)", prefix_actually_changed,
       f"prefix_changed={prefix_actually_changed}")


# ---------------------------------------------------------------------------
# 카테고리 SSOT 확장 시험 — ERROR 신설·SessionBoundary 무소속·sid 유도 순서 (PM 지시 4건)
# ---------------------------------------------------------------------------

# (1) ERROR 카테고리: fail-loud 3종만 포함, FXSHOW/FXHIDE(STAGE)는 제외
error_markers = extract_battle_log.resolve_markers("ERROR", None)
ok = (set(error_markers) >= {"FXLAB:FXSKIP", "FXLAB:TEXMISS", "FXLAB:FXNOROW"}
      and "FXLAB:FXSHOW" not in error_markers and "FXLAB:FXHIDE" not in error_markers)
record("PM지시①(--category ERROR = fail-loud 3종만)", ok, f"markers={error_markers}")

# (2) STAGE: FXSHOW/FXHIDE는 포함하되 fail-loud 3종은 제외(ERROR로 이관됐으므로)
stage_markers = extract_battle_log.resolve_markers("STAGE", None)
ok = ({"FXLAB:FXSHOW", "FXLAB:FXHIDE"} <= set(stage_markers)
      and not ({"FXLAB:FXSKIP", "FXLAB:TEXMISS", "FXLAB:FXNOROW"} & set(stage_markers)))
record("PM지시①(--category STAGE = FXSHOW/FXHIDE만, fail-loud 제외)", ok, f"markers={stage_markers}")

# (3) SessionBoundary 무소속 — 단일 카테고리만 요청해도 항상 포함
sb_prefix = tokens.row_by_number("16").prefixes[0]
for cat in ("LEDGER", "FLOW", "STAGE", "DIAG", "ERROR"):
    markers = extract_battle_log.resolve_markers(cat, None)
    ok = sb_prefix in markers
    record(f"PM지시②(SessionBoundary 무소속 — --category {cat}에도 포함)", ok, f"markers 일부={markers[:3]}...")

# (4) sid 유도 순서 — parse_line_meta는 ts와 rest를 동시에 반환(strip_prefix는 ts를 버림)
sample_raw = "[2026.08.11-22.32.06:160][596]LogBlueprintUserMessages: [BP_BattleManager_C_0] " + \
             sb_prefix + "event=BeginPlay"
meta = parser.parse_line_meta(sample_raw)
ok = (meta is not None) and (meta[0] == "2026.08.11-22.32.06:160") and (meta[2].startswith(sb_prefix))
record("PM지시③(parse_line_meta — ts·rest 동시 추출)", ok, f"meta={meta}")

stripped_only = parser.strip_prefix(sample_raw)
ok = stripped_only == meta[2]  # strip_prefix는 parse_line_meta의 rest만 반환하는 래퍼
record("PM지시③(strip_prefix는 parse_line_meta의 래퍼 — ts는 버림, rest는 동일)", ok,
       f"strip_prefix 결과={stripped_only!r}")


# (5) 세션 분할 + 세션 키(sid, init_ordinal) — 2 sid × 각 2 INIT(FRESH/RESTART)
def _raw(ts: str, frame: int, content: str) -> str:
    return f"[{ts}][{frame:3d}]LogBlueprintUserMessages: [BP_BattleManager_C_0] {content}"


battle_prefix = tokens.row_by_number("11").prefixes[0]
state_prefix = tokens.row_by_number("13").prefixes[0]
registered_prefix = tokens.row_by_number("4").prefixes[0]

synthetic_session_lines = [
    _raw("2026.08.11-12.00.00:000", 1, registered_prefix + "1"),  # 마커 이전 — sid None 기대
    _raw("2026.08.11-12.00.01:000", 2, sb_prefix + "event=BeginPlay"),  # sid=A 시작
    _raw("2026.08.11-12.00.01:100", 3, registered_prefix + "1"),  # sid=A, ordinal 0(예비)
    _raw("2026.08.11-12.00.02:000", 4, state_prefix + "event=INIT|mode=FRESH"),  # ordinal→1
    _raw("2026.08.11-12.00.02:500", 5, battle_prefix + "turn=1|attacker=x|target=y|action=31000000|dmg=1|hp=1"),
    _raw("2026.08.11-12.00.03:000", 6, state_prefix + "event=INIT|mode=RESTART"),  # ordinal→2
    _raw("2026.08.11-12.00.03:500", 7, battle_prefix + "turn=1|attacker=x|target=y|action=31000000|dmg=1|hp=1"),
    _raw("2026.08.11-13.30.00:000", 8, sb_prefix + "event=BeginPlay"),  # sid=B 시작(다른 벽시계)
    _raw("2026.08.11-13.30.01:000", 9, state_prefix + "event=INIT|mode=FRESH"),  # sid=B ordinal→1
    _raw("2026.08.11-13.30.01:500", 10, battle_prefix + "turn=1|attacker=x|target=y|action=31000000|dmg=1|hp=1"),
]

# 인덱스 지도(0-based, 10줄): 0=마커 이전 / 1=SB(ts1) / 2=Registered / 3=INIT FRESH /
# 4=BattleLog / 5=INIT RESTART / 6=BattleLog / 7=SB(ts2) / 8=INIT FRESH / 9=BattleLog
sessions = session.assign_sessions(synthetic_session_lines)
sids = [s for s, _ in sessions]
ok = (sids[0] is None) and (len(set(sids[1:7])) == 1) and (sids[7] != sids[1]) and (sids[7] == sids[8] == sids[9])
record("PM지시④(assign_sessions — 마커 이전 None ∧ 세션별 sid 분리 ∧ 2세션 sid 서로 다름)",
       ok, f"sids={sids}")

keyed = session.assign_session_keys(synthetic_session_lines)
# sid=A 구간(인덱스 1~6, SB 라인 자신 포함): SB=0, Registered=0, INIT FRESH=1, BattleLog=1, INIT RESTART=2, BattleLog=2
ordinals_sid_a = [k[1] for k, raw in keyed if k[0] == sids[1]]
ok = ordinals_sid_a == [0, 0, 1, 1, 2, 2]
record("PM지시④(assign_session_keys — sid=A 내 init_ordinal 0,0,1,1,2,2, SB 자신은 예비=0)",
       ok, f"ordinals={ordinals_sid_a}")

# sid=B 구간(인덱스 7~9, SB 라인 자신 포함): SB=0, INIT FRESH=1, BattleLog=1
ordinals_sid_b = [k[1] for k, raw in keyed if k[0] == sids[7]]
ok = ordinals_sid_b == [0, 1, 1]
record("PM지시④(assign_session_keys — sid=B 내 init_ordinal 0,1,1, 새 sid에서 리셋)", ok,
       f"ordinals={ordinals_sid_b}")


# ---------------------------------------------------------------------------
# ★천 단위 쉼표 내성 (2026-08-12 실측 함정 — 전투로그.md §1-6)
# UE float->string이 1000 초과에서 로케일 쉼표를 붙인다(실측 t=6,915.2).
# int->string은 안 붙인다(실측 FXLAB:FXNOROW:63009999) — 그래서 한 로그에 둘이 공존한다.
# 회귀 방지: 이 케이스가 없으면 normalize_number가 조용히 되돌려져도 아무도 모른다.
# ---------------------------------------------------------------------------
comma_cases = [
    ("6,915.2", "6915.2"),      # ★실측 원문
    ("1,234", "1234"),
    ("1,234,567", "1234567"),
    ("36", "36"),               # 쉼표 없는 정수 — 무변
    ("-33", "-33"),             # 치유 음수(dmg RAW 계약) — 무변
    ("63009999", "63009999"),   # 8자리 ID — 무변
    ("A3", "A3"),               # ★슬롯 라벨 — 숫자가 아니므로 원문 보존
    ("false", "false"),
    ("", ""),
]
bad = [(src, parser.normalize_number(src), want)
       for src, want in comma_cases if parser.normalize_number(src) != want]
record("천단위쉼표(normalize_number — 숫자만 정규화, 비숫자 원문 보존)",
       not bad, f"불일치={bad}" if bad else f"{len(comma_cases)}건 전부 기대값")

# ★rows_equal이 실제로 그 정규화를 거치는가 — 헬퍼만 고치고 소비처를 안 고치는 실수 방지
_row_a = {c: "" for c in oracle.ORACLE_COLUMNS}
_row_b = dict(_row_a)
_num_col = "dmg" if "dmg" in oracle.ORACLE_COLUMNS else oracle.ORACLE_COLUMNS[-1]
_row_a[_num_col] = "1,234"   # 라이브(UE가 쉼표를 붙인 값)
_row_b[_num_col] = "1234"    # 오라클(사람이 쓴 값)
record("천단위쉼표(oracle_diff.rows_equal — 라이브 1,234 == 오라클 1234)",
       oracle_diff.rows_equal(_row_a, _row_b),
       f"열={_num_col}")


# ---------------------------------------------------------------------------
# 요약
# ---------------------------------------------------------------------------
print("\n=== 요약 ===")
n_pass = sum(1 for _, ok, _ in RESULTS if ok)
n_total = len(RESULTS)
for tc_id, ok, _ in RESULTS:
    print(f"  {'PASS' if ok else 'FAIL'}  {tc_id}")
print(f"{n_pass}/{n_total} PASS")
sys.exit(0 if n_pass == n_total else 1)
