"""배틀 로그 토큰 레지스트리 — 카테고리·문법 배정의 단일 소스.

출처:
    현행 15종 = docs/로그시스템_점검_2026-08-12.md §1-1 표(그대로 옮김, 순번 1~15 유지)
    신규 3종  = docs/LOG-A_실행계획.md §토큰 계약서(SessionBoundary|·PlayAttack|·SkillSelected|)
    카테고리(LEDGER/FLOW/STAGE/DIAG) = LOG-A_실행계획.md ★★로그 카테고리 체계(오너 결재)

★주의 — FXLAB 행(§1-1 순번 15)만 카테고리가 하나가 아니다:
    plan 카테고리 표가 STAGE 행에 "FXLAB:*"(와일드카드), DIAG 행에 "FXLAB:DIAG 등"을
    동시에 적어 자기모순처럼 보인다. 점검 문서 §1-1의 FXLAB 행 각주("✅, 단 DIAG는
    임시 진단용")로 해소: `FXLAB:DIAG`만 DIAG, 나머지(FXSKIP/TEXMISS/FXNOROW/FXSHOW/FXHIDE)는
    STAGE. 그래서 순번 15를 15/15b 두 엔트리로 쪼갰다 — 표 위 "15종" 카운트는 그대로 유지
    (전투로그.md에도 동일하게 각주로 명시할 것).

이 파일이 바뀌면(신규 토큰 추가 등) `Resource/docs/전투로그.md`의 카테고리 표도 같이 갱신한다.
"""
from __future__ import annotations

from dataclasses import dataclass

LEDGER = "LEDGER"
FLOW = "FLOW"
STAGE = "STAGE"
DIAG = "DIAG"
CATEGORIES = (LEDGER, FLOW, STAGE, DIAG)

# 카테고리 기본 ON/OFF (에디터 bool 4개의 기본값과 대응 — bLogLedger/Flow/Stage=true, bLogDiag=false)
DEFAULT_ON = {
    LEDGER: True,
    FLOW: True,
    STAGE: True,
    DIAG: False,
}

PIPE_KV = "pipe_kv"      # Tag|k=v|k=v|...
COLON_POS = "colon_pos"  # Tag:field1:field2:... 위치 기반(key=value 아님)
PLAIN = "plain"          # Tag:literal 또는 Tag:N (필드 파싱 불요)


@dataclass(frozen=True)
class LogRow:
    row: str          # 점검 문서 §1-1 표 순번("1".."15","15b") 또는 신규("16".."18")
    label: str        # 표에 쓰인 원문 라벨(사람이 읽는 용도)
    prefixes: tuple    # 실제 라인(프리픽스 스트립 후) 매칭 프리픽스들
    category: str
    syntax: str
    note: str = ""


ROWS: tuple = (
    LogRow("1", "Align:<라벨>:yaw=", ("Align:",), STAGE, COLON_POS,
           "빌보딩 결함 검증(CT-VF-01~04) — 노이즈 아님, 파서 스코프에서만 제외(범위 밖)"),
    LogRow("2", "State:<이름>:t=", ("State:",), FLOW, COLON_POS,
           "TurnStart/AwaitCommand/AwaitTarget/TurnEnd 등. State|(순번13)와 다른 토큰"),
    LogRow("3", "VFXSetup:<라벨>:...MID=", ("VFXSetup:",), STAGE, COLON_POS,
           "EffectQuad StaticMesh 유실 진단"),
    LogRow("4", "Registered:<N>", ("Registered:",), FLOW, PLAIN,
           "8기 등록 게이트 → InitBattle() 진입 판정"),
    LogRow("5", "WalkFwd:/WalkArrive:/WalkHome:",
           ("WalkFwd:", "WalkArrive:", "WalkHome:"), STAGE, COLON_POS,
           "도착≤공격 순서, WalkBack 직렬화"),
    LogRow("6", "WalkGround:", ("WalkGround:",), STAGE, COLON_POS,
           "접지 보정값(정확한 설계 문서 근거 불명확 — 점검 문서 §1-1 주석)"),
    LogRow("7", "TakeHit:/TakeHitRevert:", ("TakeHitRevert:", "TakeHit:"), STAGE, PLAIN,
           "피격-복귀 레이스 무충돌 증명. ★TakeHitRevert:가 TakeHit:의 접두 상위집합이라 매칭은 "
           "prefix 길이 내림차순으로 수행(match_row 참고)"),
    LogRow("8", "CamCut:.../CamBack:t=", ("CamCut:", "CamBack:"), STAGE, COLON_POS,
           "팀별 캠 매칭, TurnEnd마다 복귀"),
    LogRow("9", "CamToggle:<bool>", ("CamToggle:",), STAGE, PLAIN,
           "ON/OFF/복원/Executing중 BLOCKED"),
    LogRow("10", "ExecWalkPhase:t=", ("ExecWalkPhase:",), FLOW, COLON_POS,
           "걷기 재배선 검증 기준점, 턴길이 실측 핵심 앵커"),
    LogRow("11", "BattleLog|turn=...", ("BattleLog|",), LEDGER, PIPE_KV,
           "전투 원장 1차 소스. ★리포 전체에서 이 리터럴은 여기 한 곳에만 존재해야 한다(게이트③)"),
    LogRow("12", "UnitClicked:<라벨>:valid", ("UnitClicked:",), FLOW, COLON_POS,
           "클릭 유효타겟 판정"),
    LogRow("13", "State|event=...(INIT/BATTLE_END)", ("State|",), FLOW, PIPE_KV,
           "승패·재시작 구분. State:(순번2)와 다른 토큰(우발적 네이밍 충돌 — 소급 통일 안 함)"),
    LogRow("14", "StatusLog|turn=...", ("StatusLog|",), LEDGER, PIPE_KV,
           "상태이상 지속시간·스킵·해제 판정"),
    LogRow("15", "FXLAB:DIAG", ("FXLAB:DIAG",), DIAG, COLON_POS,
           "임시 진단 3줄. 기본 OFF — 켜진 채 남으면 오염(실측: FXLAB:DIAG가 실제로 이렇게 남아있었음)"),
    LogRow("15b", "FXLAB:FXSKIP/TEXMISS/FXNOROW/FXSHOW/FXHIDE", ("FXLAB:",), STAGE, COLON_POS,
           "fail-loud 정식 판정 신호(행 없음/프레임 0/텍스처 캐스트 실패 구분). "
           "★FXLAB:DIAG(순번15)보다 덜 구체적이므로 매칭 우선순위상 뒤에 와야 함 — "
           "match_row가 prefix 길이 내림차순 정렬로 자동 처리"),
    LogRow("16", "SessionBoundary|pieStart=...|sid=...", ("SessionBoundary|",), LEDGER, PIPE_KV,
           "★신규. 원장 파싱의 세션 분리 전제라 LEDGER(FLOW 아님) — LOG-A §카테고리 판정 근거. "
           "sid = 세션 내 불변·세션 간 유일. 이번 단계는 문법 확정만(실제 심기는 FT1-0)"),
    LogRow("17", "PlayAttack|unit=...|phase=enter|exit", ("PlayAttack|",), FLOW, PIPE_KV,
           "★신규. 애니메이션 함수 블로킹 여부 판정(점검 §2-1). 이번 단계는 문법 확정만(FT1-0에서 심음)"),
    LogRow("18", "SkillSelected|unit=...|skillId=...", ("SkillSelected|",), FLOW, PIPE_KV,
           "★신규. 스킬 선택 로그(오너 질문①). 이번 단계는 문법 확정만(FT1-0c에서 심음)"),
)


def all_prefixes() -> tuple:
    """모든 매칭 프리픽스를 (prefix, row) 쌍으로, prefix 길이 내림차순 정렬해 반환.

    길이 내림차순인 이유: `FXLAB:DIAG`(11자)가 `FXLAB:`(6자)보다, `TakeHitRevert:`(14자)가
    `TakeHit:`(8자)보다 먼저 매칭돼야 한다(더 구체적인 쪽 우선).
    """
    pairs = []
    for row in ROWS:
        for prefix in row.prefixes:
            pairs.append((prefix, row))
    pairs.sort(key=lambda pr: len(pr[0]), reverse=True)
    return tuple(pairs)


_SORTED_PREFIXES = all_prefixes()


def match_row(stripped_content: str):
    """프리픽스가 스트립된 라인 내용에서 가장 구체적으로 일치하는 LogRow를 반환. 없으면 None."""
    for prefix, row in _SORTED_PREFIXES:
        if stripped_content.startswith(prefix):
            return row
    return None


def row_by_number(row_id: str):
    for row in ROWS:
        if row.row == row_id:
            return row
    return None
