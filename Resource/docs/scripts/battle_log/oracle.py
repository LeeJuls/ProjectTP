"""오라클 문서(SPD원장_오라클_v1.md) 파싱 — job 조인표의 유일 정본.

★설계 결정(LOG-A_실행계획.md §설계 결정 1): job 조인표(A1..B4 → WAR/MAG)를
코드에 상수로 하드코딩하지 않는다. `AU-B2-03`이 금지한 것이 정확히 그것이다
("조인표가 하드코딩이면 오라클 §0 재유도 시 무음 스테일"). 대신 §0의 "직업 배정" 산문 표
행을 정규식으로 파싱해 매 실행마다 유도한다 — 오라클 §0이 바뀌면(전면 재유도) 조인표도
같이 갱신되고, 안 바뀌면 그대로다. 사이드카 CSV(정본을 둘로 만듦)도, 인자 주입(호출 시점
실수 위험)도 쓰지 않는다.

★취약점(공개 고지): 이 파서는 "| **직업 배정** | <슬롯>=<직업명> <급수>성 / ... |" 형식의
마크다운 표 행 문법에 결합돼 있다. 오라클 §0의 표 서식 자체가 바뀌면(예: 열 순서 변경,
다른 구두점 채택) 파싱이 실패한다 — 단, 그 경우 **침묵하지 않고 예외를 던진다**
(OracleParseError, fail-loud 요구사항). 빈 조인표로 조용히 진행하는 경우는 없다.

또한 이 모듈은 §7 "파싱용 CSV" 코드블록을 오라클 문서에서 직접 추출하는 기능도 제공한다
(AU-B2-01 자가시험이 "오라클 §7 20행 그대로 입력"을 사람이 손으로 옮겨적지 않고 문서에서
그대로 읽게 하기 위함 — 전사 오류 위험 제거).
"""
from __future__ import annotations

import csv
import io
import re

# 언어명 → CSV 코드. ★이것은 "어느 슬롯이 어느 직업인가"(진짜 조인 데이터, 하드코딩 금지 대상)가
# 아니라 "직업 이름을 뭐라고 부르는가"(어휘 번역표)다. 현재 2직업(전사/마법사)만 존재 —
# 신규 직업 추가 시 여기 추가해야 하며, 미등록 직업명은 아래에서 fail-loud로 걸린다.
_JOB_KO_TO_CODE = {
    "전사": "WAR",
    "마법사": "MAG",
}

_JOB_ROW_RE = re.compile(r"\|\s*\*\*직업 배정\*\*\s*\|(?P<value>[^|]+)\|")
_SLOT_GROUP_RE = re.compile(r"^([A-B][0-9](?:·[A-B][0-9])*)\s*=\s*([^0-9/]+?)\s*[0-9]*성?\s*$")
_SLOT_LABEL_RE = re.compile(r"^SpawnPoint_(?:Party|Enemy)_(?P<slot>[AB][0-9]+)$")
_CSV_BLOCK_RE = re.compile(r"##\s*7\..*?```csv\r?\n(?P<csv>.*?)```", re.S)

ORACLE_COLUMNS = (
    "T", "attacker", "attacker_job", "target", "target_job", "dmg", "target_hp_after", "died",
)


class OracleParseError(RuntimeError):
    """오라클 문서 파싱 실패 — fail-loud. 빈 조인표/빈 CSV로 진행하지 않는다."""


def parse_job_table(oracle_md_text: str) -> dict:
    """§0 "직업 배정" 표 행을 파싱해 {슬롯라벨: 직업코드} 딕셔너리를 반환.

    예: "A3·A4·B3·B4 = 마법사 2성 / A1·A2·B1·B2 = 전사 2성"
        → {"A3":"MAG","A4":"MAG","B3":"MAG","B4":"MAG","A1":"WAR","A2":"WAR","B1":"WAR","B2":"WAR"}
    """
    matches = _JOB_ROW_RE.findall(oracle_md_text)
    if len(matches) != 1:
        raise OracleParseError(
            f"'직업 배정' 표 행이 {len(matches)}개 발견됨(정확히 1개여야 함). "
            "오라클 §0 산문 표 서식이 바뀌었을 수 있다 — _JOB_ROW_RE 갱신 필요."
        )
    value = matches[0]
    groups = [g.strip() for g in value.split("/") if g.strip()]
    if len(groups) < 2:
        raise OracleParseError(f"'직업 배정' 값에 '/' 구분 그룹이 부족함(최소 2 필요): {value!r}")

    table: dict = {}
    for group in groups:
        m = _SLOT_GROUP_RE.match(group)
        if not m:
            raise OracleParseError(f"직업 배정 그룹 파싱 실패: {group!r}")
        slots = m.group(1).split("·")
        job_ko = m.group(2).strip()
        if job_ko not in _JOB_KO_TO_CODE:
            raise OracleParseError(
                f"미등록 직업명 {job_ko!r} — _JOB_KO_TO_CODE에 신규 직업 번역 추가 필요"
                "(슬롯 매핑이 아니라 '언어명→코드' 어휘표만 확장하면 됨)"
            )
        code = _JOB_KO_TO_CODE[job_ko]
        for slot in slots:
            if slot in table and table[slot] != code:
                raise OracleParseError(f"슬롯 {slot} 중복/충돌 배정: {table[slot]} vs {code}")
            table[slot] = code

    if not table:
        raise OracleParseError("직업 배정 파싱 결과가 빈 조인표 — fail-loud")
    return table


def extract_csv_block(oracle_md_text: str) -> str:
    """§7 "파싱용 CSV" 코드블록 원문을 추출."""
    m = _CSV_BLOCK_RE.search(oracle_md_text)
    if not m:
        raise OracleParseError('§7 "파싱용 CSV" 코드블록을 찾지 못함(```csv 펜스 확인)')
    return m.group("csv")


def load_oracle_rows(path: str) -> list:
    """오라클 CSV 행을 dict 리스트로 로드.

    `path`가 `.md`면 문서에서 §7 CSV 블록을 추출해서 파싱(AU-B2-01 self-test 경로).
    `.csv`면 파일 내용을 그대로 CSV로 파싱(사전 추출된 오라클 CSV 사용 경로).
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    csv_text = extract_csv_block(text) if path.lower().endswith(".md") else text
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = [dict(row) for row in reader]
    if not rows:
        raise OracleParseError(f"오라클 CSV 파싱 결과 0행: {path}")
    missing = [c for c in ORACLE_COLUMNS if c not in rows[0]]
    if missing:
        raise OracleParseError(f"오라클 CSV에 필수 열 누락: {missing} (파일: {path})")
    return rows


def strip_slot(raw_label: str) -> str:
    """`SpawnPoint_Party_A1` → `A1`, `SpawnPoint_Enemy_B1` → `B1` (오라클 매핑①②)."""
    m = _SLOT_LABEL_RE.match(raw_label)
    if not m:
        raise OracleParseError(f"알 수 없는 슬롯 라벨(GetDisplayName 포맷 변경 의심): {raw_label!r}")
    return m.group("slot")


def slot_to_raw_label(slot: str) -> str:
    """`strip_slot`의 역함수(self-test용 fixture 합성에 사용) — `A1`→`SpawnPoint_Party_A1`."""
    team = "Party" if slot.startswith("A") else "Enemy"
    return f"SpawnPoint_{team}_{slot}"


def map_event_to_oracle_row(event: dict, job_table: dict) -> dict:
    """BattleLog 이벤트 dict(파이프 파싱 결과)를 오라클 8열 스키마로 매핑(AU-B2-03 매핑 5건).

    ① SpawnPoint_Party_A1 → A1 (attacker)
    ② SpawnPoint_Enemy_B1 → B1 (target)
    ③ died=true → died 열 = 스트립된 target 값 / 필드 부재 → ""
    ④ hp → target_hp_after (리네임)
    ⑤ attacker_job/target_job → 이 함수의 job_table 인자(§0 파싱 결과)로 조인
    부수: turn → T. dmg는 RAW 무변환(치유 음수 그대로, 오버킬 원시값 그대로).
    """
    attacker_slot = strip_slot(event["attacker"])
    target_slot = strip_slot(event["target"])
    if attacker_slot not in job_table:
        raise OracleParseError(f"job_table에 슬롯 {attacker_slot!r} 없음(조인표 누락)")
    if target_slot not in job_table:
        raise OracleParseError(f"job_table에 슬롯 {target_slot!r} 없음(조인표 누락)")

    died_raw = event.get("died")
    return {
        "T": event["turn"],
        "attacker": attacker_slot,
        "attacker_job": job_table[attacker_slot],
        "target": target_slot,
        "target_job": job_table[target_slot],
        "dmg": event["dmg"],
        "target_hp_after": event["hp"],
        "died": target_slot if died_raw == "true" else "",
    }
