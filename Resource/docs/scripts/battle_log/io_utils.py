"""로그 파일 탐색·읽기·추출 산출물 저장.

`extract_battle_log.py`(개조 전) 40~46행(find_log_files)·58~67행(write_output)·
51행(errors="replace")을 그대로 이관한 것 — 동작 변경 없음(게이트⑤ 바이트 동일의 기반).
"""
from __future__ import annotations

import glob
import os
from datetime import datetime


def find_log_files(logs_dir: str, all_files: bool):
    """`<logs_dir>/projectTP*.log`를 mtime 내림차순으로. all_files=False면 최신 1개만."""
    pattern = os.path.join(logs_dir, "projectTP*.log")
    files = glob.glob(pattern)
    if not files:
        return []
    files.sort(key=os.path.getmtime, reverse=True)
    return files if all_files else [files[0]]


def read_raw_lines(log_path: str):
    """`errors="replace"` 관용 읽기로 원본 라인(개행 제거)을 그대로 반환."""
    with open(log_path, encoding="utf-8", errors="replace") as f:
        return [line.rstrip("\n") for line in f]


def write_extracted(lines, source_path: str, out_dir: str, timestamp: str | None = None):
    """`# source:`/`# extracted:`/`# lines:` 헤더 3줄 + 라인들을 `<out_dir>/battle_<ts>.log`에 저장.

    `timestamp`를 생략하면 실행 시각(YYYYMMDD_HHMMSS)을 쓴다. 인자로 받는 이유는
    게이트⑤(바이트 동일) 자가시험에서 시각을 고정해 재현 가능한 비교를 하기 위함.
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"battle_{timestamp}.log")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# source: {source_path}\n")
        f.write(f"# extracted: {timestamp}\n")
        f.write(f"# lines: {len(lines)}\n")
        for line in lines:
            f.write(line + "\n")
    return out_path
