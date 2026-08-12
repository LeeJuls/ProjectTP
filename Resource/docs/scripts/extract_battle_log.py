"""전투 로그 라인을 UE 엔진 로그에서 추출해 별도 파일로 저장 (battle_log 모듈의 thin wrapper).

BP_BattleManager.EnterExecuting은 매 공격 실행 시 원장 토큰(파이프 key=value) 형식의
구조화된 PrintString 라인을 로그 전용(Print to Screen=false, Log=true)으로 남긴다.
이 스크립트는 그 라인들만 걸러내 개발/밸런스 분석용 파일로 저장한다.

라인 포맷·토큰 카탈로그는 `battle_log.tokens`가 단일 소스다(이 파일은 리터럴을 갖지 않는다).

사용법:
    python extract_battle_log.py                최신(mtime 최대) projectTP*.log 1개, 기본 토큰만 추출
    python extract_battle_log.py --all           Saved/Logs/의 모든 projectTP*.log를 각각 처리
    python extract_battle_log.py --category LEDGER,FLOW
                                                  기본 토큰 대신 지정 카테고리에 속하는 모든 토큰 추출
                                                  (게이트⑦: STAGE를 끈 로그도 LEDGER/FLOW만으로 파싱 가능)
    python extract_battle_log.py --logs-dir D:\\path --out-dir D:\\path2
                                                  기본 경로 대신 임의 경로 사용(비교기가 두 파일을 자유롭게 받게 하기 위함)

기본 동작(인자 없음)은 개조 전 스크립트와 **바이트 동일**하다(회귀 0 — LOG-A_실행계획.md 게이트⑤):
    D:\\unreal\\projectTP\\Saved\\Logs\\ 에서 projectTP*.log(백업 포함) 중 최신 1개를 골라
    원장 토큰(순번11) 라인만 추출하고, UE 타임스탬프를 보존한 채로
    D:\\unreal\\projectTP\\Saved\\BattleLogs\\battle_<타임스탬프>.log 에 저장한다.
    Saved/ 는 .gitignore 대상이라 이 추출 산출물이 레포를 오염시키지 않는다(의도된 설계).

확장 여지:
    필드가 추가되면 BP_BattleManager.EnterExecuting의 FormatText 포맷 문자열에 필드를 추가하면
    되고, 이 스크립트는 라인 전체를 그대로 통과시키므로 별도 수정이 필요 없다(파싱은
    battle_log.parser.parse_pipe_kv()가 담당 — died 위치 가변 등은 dict 파싱이라 자동 대응).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from battle_log import io_utils, tokens  # noqa: E402

DEFAULT_LOGS_DIR = r"D:\unreal\projectTP\Saved\Logs"
DEFAULT_OUT_DIR = r"D:\unreal\projectTP\Saved\BattleLogs"

# 기본 추출 대상 = 원장(LEDGER) 1차 소스 토큰(순번11) 하나만 — 개조 전 스크립트와 동일 범위.
_DEFAULT_ROW = tokens.row_by_number("11")


def resolve_markers(category_arg: str | None, tokens_arg: str | None):
    """추출 대상 마커 목록을 결정. 인자가 전부 없으면 기본(순번11) 1종만(회귀 0 보장)."""
    if tokens_arg:
        return [t for t in tokens_arg.split(",") if t]
    if category_arg:
        requested = {c.strip().upper() for c in category_arg.split(",") if c.strip()}
        unknown = requested - set(tokens.CATEGORIES)
        if unknown:
            raise ValueError(f"알 수 없는 카테고리: {sorted(unknown)} (유효: {tokens.CATEGORIES})")
        markers = []
        for row in tokens.ROWS:
            if row.category in requested:
                markers.extend(row.prefixes)
        if not markers:
            raise ValueError(f"카테고리 {sorted(requested)}에 해당하는 토큰이 없음")
        return markers
    return list(_DEFAULT_ROW.prefixes)


def extract_battle_lines(log_path: str, markers):
    lines = []
    for raw in io_utils.read_raw_lines(log_path):
        if any(m in raw for m in markers):
            lines.append(raw)
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="Saved/Logs/의 모든 projectTP*.log를 처리")
    ap.add_argument("--logs-dir", default=DEFAULT_LOGS_DIR)
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--category", default=None, help="예: LEDGER,FLOW (게이트⑦ — STAGE 꺼진 로그도 파싱)")
    ap.add_argument("--tokens", default=None, help="쉼표구분 프리픽스 명시(예: 'StatusLog|,SessionBoundary|')")
    args = ap.parse_args()

    try:
        markers = resolve_markers(args.category, args.tokens)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    targets = io_utils.find_log_files(args.logs_dir, args.all)
    if not targets:
        print(f"NO LOG FILES FOUND matching projectTP*.log in {args.logs_dir}")
        sys.exit(1)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total = 0
    for idx, log_path in enumerate(targets):
        lines = extract_battle_lines(log_path, markers)
        if not lines:
            print(f"SKIP (no matching lines): {log_path}")
            continue
        ts = timestamp if len(targets) == 1 else f"{timestamp}_{idx}"
        out_path = io_utils.write_extracted(lines, log_path, args.out_dir, ts)
        print(f"SAVED {out_path} ({len(lines)} lines) <- {log_path}")
        total += len(lines)

    if total == 0:
        print("NO MATCHING LINES FOUND in any processed file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
