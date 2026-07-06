"""전투 로그(BattleLog|...) 라인을 UE 엔진 로그에서 추출해 별도 파일로 저장.

BP_BattleManager.EnterExecuting은 매 공격 실행 시 `BattleLog|turn=...` 형식의
구조화된 PrintString 라인을 로그 전용(Print to Screen=false, Log=true)으로 남긴다.
이 스크립트는 그 라인들만 걸러내 개발/밸런스 분석용 파일로 저장한다.

라인 포맷 (BP_BattleManager.EnterExecuting 참고):
    BattleLog|turn=<TurnCounter>|attacker=<ActiveUnit 라벨>|target=<SelectedTarget 라벨>|action=ATTACK1

UE 원본 로그 라인 실측 포맷 (LogBlueprintUserMessages):
    [2026.07.06-18.28.47:963][140]LogBlueprintUserMessages: [BP_BattleManager_C_0] BattleLog|turn=1|...

사용법:
    python extract_battle_log.py            최신(mtime 최대) projectTP*.log 1개만 처리
    python extract_battle_log.py --all       Saved/Logs/의 모든 projectTP*.log를 처리(각 파일당 출력 1개)

동작:
    D:\\unreal\\projectTP\\Saved\\Logs\\ 에서 projectTP*.log(백업 포함) 중 대상을 골라
    'BattleLog|' 를 포함하는 라인만 추출하고, UE 타임스탬프([2026.07.06-18.28.47:963][140] 부분)를
    보존한 채로 D:\\unreal\\projectTP\\Saved\\BattleLogs\\battle_<타임스탬프>.log 에 저장한다
    (BattleLogs 폴더가 없으면 생성). 타임스탬프는 스크립트 실행 시각(YYYYMMDD_HHMMSS) 기준.

    Saved/ 는 .gitignore 대상이라 이 추출 산출물이 레포를 오염시키지 않는다(의도된 설계).

확장 여지:
    데미지/힐 등 필드가 추가되면 BP_BattleManager.EnterExecuting의 FormatText 포맷 문자열에
    |field=값 을 추가하고, 이 스크립트는 라인 전체를 그대로 통과시키므로 별도 수정이 필요 없다
    (파싱이 필요해지면 라인을 '|' 로 split해 key=value 쌍을 dict화하는 헬퍼를 추가할 것).
"""
import glob
import os
import sys
from datetime import datetime

LOGS_DIR = r"D:\unreal\projectTP\Saved\Logs"
OUT_DIR = r"D:\unreal\projectTP\Saved\BattleLogs"
MARKER = "BattleLog|"


def find_log_files(all_files: bool):
    pattern = os.path.join(LOGS_DIR, "projectTP*.log")
    files = glob.glob(pattern)
    if not files:
        return []
    files.sort(key=os.path.getmtime, reverse=True)  # 최신(mtime) 순
    return files if all_files else [files[0]]


def extract_battle_lines(log_path: str):
    lines = []
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if MARKER in line:
                lines.append(line.rstrip("\n"))
    return lines


def write_output(lines, source_path: str, timestamp: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"battle_{timestamp}.log")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# source: {source_path}\n")
        f.write(f"# extracted: {timestamp}\n")
        f.write(f"# lines: {len(lines)}\n")
        for line in lines:
            f.write(line + "\n")
    return out_path


def main():
    all_files = "--all" in sys.argv[1:]
    targets = find_log_files(all_files)
    if not targets:
        print(f"NO LOG FILES FOUND matching projectTP*.log in {LOGS_DIR}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total = 0
    for idx, log_path in enumerate(targets):
        lines = extract_battle_lines(log_path)
        if not lines:
            print(f"SKIP (no BattleLog lines): {log_path}")
            continue
        # --all로 여러 파일을 처리할 때 출력 파일명이 겹치지 않도록 인덱스를 붙인다.
        ts = timestamp if len(targets) == 1 else f"{timestamp}_{idx}"
        out_path = write_output(lines, log_path, ts)
        print(f"SAVED {out_path} ({len(lines)} lines) <- {log_path}")
        total += len(lines)

    if total == 0:
        print("NO BattleLog| LINES FOUND in any processed file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
