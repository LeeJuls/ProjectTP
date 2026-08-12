"""오라클-diff 비교기 CLI — S1 봉인 판정 도구 (F7b ⑦ 게이트의 도구, LOG-A_실행계획.md).

사용법:
    python oracle_diff.py --oracle <오라클.md 또는 .csv> --log <엔진 로그 또는 추출된 battle_*.log>
        [--jobtable <오라클.md>]   # --oracle이 .csv일 때 필수(직업 조인표 출처)
        [--category LEDGER,FLOW]  # 참고용 — 로그 필터링이 이미 됐어도 무관하게 동작 확인(게이트⑦)

동작:
    1. --oracle에서 오라클 정답 20행(§7 CSV)을 읽는다(.md면 문서에서 §7 코드블록을 직접 추출).
    2. --oracle(.md) 또는 --jobtable(.md)에서 §0 "직업 배정" 표를 파싱해 조인표를 유도한다.
       ★조인표는 절대 하드코딩하지 않는다 — battle_log.oracle.parse_job_table() 참고.
    3. --log에서 원장 토큰(LEDGER, 순번11) 라인만 추출·파싱해 오라클 8열 스키마로 매핑한다.
    4. 행 단위(순서·전 열) diff. 첫 불일치에서 즉시 멈추고 그 행 번호를 출력한다(오라클 §8 중단기준).
    5. 불변식 별도 검사(AU-B2-04): 매핑 전 원본 이벤트의 action이 전 행 31000000인지,
       berserk 필드가 있다면 1.0인지.
    6. 무감각 열 고지(AU-B2-05)를 항상 출력한다: attacker·target 열은 판정력이 없다.

종료 코드: 0 = diff 없음(∧ 불변식 위반 없음). 1 = 불일치 또는 불변식 위반 또는 파싱 실패.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from battle_log import io_utils, oracle, parser, tokens  # noqa: E402

_LEDGER_BATTLE_ROW = tokens.row_by_number("11")  # 원장 1차 소스 토큰 — 리터럴은 tokens.py에만 존재
_BATTLE_PREFIX = _LEDGER_BATTLE_ROW.prefixes[0]
_BATTLE_TAG = _BATTLE_PREFIX.rstrip("|")

NOTICE_INSENSITIVE_COLUMNS = (
    '"attacker"·"target" 열은 판정력이 없다 — 오라클 §7-2/§8-1 step4: target은 입력(클릭 스크립트)이지 '
    "출력이 아니다. 실질 판정 열 = dmg·target_hp_after·died·행수."
)


class DiffError(RuntimeError):
    pass


def build_live_rows(log_path: str, job_table: dict):
    """--log 파일에서 원장 이벤트를 추출해 (원본이벤트 리스트, 오라클행 리스트) 반환."""
    raw_lines = io_utils.read_raw_lines(log_path)
    events = list(parser.iter_pipe_events(raw_lines, _BATTLE_TAG))
    if not events:
        raise DiffError(f"로그에서 원장 이벤트를 1건도 못 찾음: {log_path}")
    live_rows = [oracle.map_event_to_oracle_row(e, job_table) for e in events]
    return events, live_rows


def check_invariants(events):
    """AU-B2-04: action 전 행 == 31000000 ∧ berserk 필드 부재 또는 1.0. 위반 목록 반환."""
    violations = []
    for i, e in enumerate(events, start=1):
        action = e.get("action")
        if action != "31000000":
            violations.append(f"행 {i}: action={action!r} (기대값 '31000000')")
        berserk = e.get("berserk")
        if berserk is not None and berserk not in ("1.0", "1"):
            violations.append(f"행 {i}: berserk={berserk!r} (기대값 부재 또는 '1.0')")
    return violations


def rows_equal(a: dict, b: dict) -> bool:
    return all(str(a.get(c, "")) == str(b.get(c, "")) for c in oracle.ORACLE_COLUMNS)


def diff_rows(oracle_rows, live_rows):
    """행 단위(순서·전 열) diff. 첫 불일치에서 중단.

    반환: (match: bool, first_mismatch_row: int | None, detail: str | None)
    `first_mismatch_row`는 1-based 위치(파일상 몇 번째 데이터 행인가).
    """
    n = min(len(oracle_rows), len(live_rows))
    for i in range(n):
        o, l = oracle_rows[i], live_rows[i]
        if not rows_equal(o, l):
            return False, i + 1, f"oracle={o} live={l}"
    if len(oracle_rows) != len(live_rows):
        return False, n + 1, (
            f"행수 불일치: oracle={len(oracle_rows)} live={len(live_rows)}"
        )
    return True, None, None


def run(oracle_path: str, log_path: str, jobtable_path: str | None):
    oracle_rows = oracle.load_oracle_rows(oracle_path)

    jt_source = jobtable_path
    if jt_source is None:
        if not oracle_path.lower().endswith(".md"):
            raise DiffError(
                "--oracle이 .csv일 때는 --jobtable(오라클 .md 경로)이 필수다 "
                "(조인표를 하드코딩하지 않으므로 §0 산문 표 출처가 반드시 필요)"
            )
        jt_source = oracle_path
    with open(jt_source, encoding="utf-8") as f:
        job_table = oracle.parse_job_table(f.read())

    events, live_rows = build_live_rows(log_path, job_table)

    print(f"# oracle: {oracle_path} ({len(oracle_rows)}행)")
    print(f"# log: {log_path} ({len(live_rows)}행 파싱됨)")
    print(f"# jobtable: {jt_source} ({len(job_table)}슬롯: {sorted(job_table)})")
    print(f"# 고지: {NOTICE_INSENSITIVE_COLUMNS}")

    violations = check_invariants(events)
    for v in violations:
        print(f"INVARIANT FAIL: {v}")

    match, first_mismatch, detail = diff_rows(oracle_rows, live_rows)
    if match:
        print("DIFF: 0 (전 행 일치)")
    else:
        print(f"DIFF: 불일치 — 첫 불일치 행 번호 = {first_mismatch}")
        print(f"  detail: {detail}")

    ok = match and not violations
    print("RESULT: PASS" if ok else "RESULT: FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--oracle", required=True, help="오라클 .md(§7 CSV 블록 자동 추출) 또는 사전 추출 .csv")
    ap.add_argument("--log", required=True, help="엔진 로그(.log) 또는 추출된 battle_*.log")
    ap.add_argument("--jobtable", default=None, help="--oracle이 .csv일 때 필수. 오라클 .md 경로")
    args = ap.parse_args()

    try:
        code = run(args.oracle, args.log, args.jobtable)
    except (DiffError, oracle.OracleParseError) as e:
        print(f"ERROR: {e}")
        code = 1
    sys.exit(code)


if __name__ == "__main__":
    main()
