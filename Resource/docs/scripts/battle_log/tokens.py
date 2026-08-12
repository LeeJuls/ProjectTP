"""배틀 로그 토큰 레지스트리 — 카테고리·문법 배정의 단일 소스(SSOT).

출처:
    현행 15종 = docs/로그시스템_점검_2026-08-12.md §1-1 표(그대로 옮김, 순번 1~15 유지)
    신규 3종  = docs/LOG-A_실행계획.md §토큰 계약서(SessionBoundary|·PlayAttack|·SkillSelected|)
    카테고리 = LOG-A_실행계획.md ★★로그 카테고리 체계(오너 결재, 4종)
               + qa-critic FT1-0_TC.md §3-B 적대검토 반영 3건(ERROR 신설·SessionBoundary 무소속·FXLAB 재분리)

★SSOT 방향(중요): `Resource/docs/전투로그.md`의 카테고리 표는 **이 파일에서 생성**한다
(손으로 표를 옮겨 적지 않는다). `render_category_markdown()`이 그 생성기다.
근거: qa-critic FT1-0_TC.md [High] *"토큰→카테고리 맵이 두 번째 정본이 된다"* —
카테고리 필터(게이트⑦)를 구현하려면 파서가 표를 코드로 들고 있어야 하는데, 같은 표가
`전투로그.md`에도 손으로 적히면 **정본이 둘**이 된다(job 조인표에서 이미 기각한 실패
모드의 재판). 오라클 §0과 달리 카테고리는 "게임 밸런스 사실"이 아니라 "어떤 로그를 남길
것인가"라는 **엔지니어링 결정**이라 코드가 정본이어도 되며, 코드 쪽이 런타임에 실제로
참조되는 쪽이기도 하다(마크다운 산문을 런타임에 파싱하는 것보다 안전).
잔여 위험(정직 고지): tokens.py를 고치고 `전투로그.md`를 재생성하지 않으면 문서가 stale
해진다 — 이건 "정본이 둘"은 아니지만 "생성물 재생성을 잊는" 신규 위험이다. 완화책은
LOG-A_실행계획.md §"언제 돌리는가" 규약(검증 게이트 통과 시점 자동 실행)에 재생성 커맨드를
포함시키는 것 — `전투로그.md` 하단에 명시.

★주의 — FXLAB 옛 순번15는 카테고리가 3갈래로 갈린다(qa-critic이 STAGE 일괄 배정을 반박):
    `FXLAB:DIAG`(임시 진단)=DIAG / `FXLAB:FXSKIP`·`TEXMISS`·`FXNOROW`(fail-loud 정식 오류
    신호)=ERROR(신설, 끄지 않음) / `FXLAB:FXSHOW`·`FXHIDE`(성공 경로 연출 진단)=STAGE.
    fail-loud 3종을 STAGE(개발 중에만 ON)에 두면 베타에서 끄는 순간 **오류 보고가 침묵**한다
    — qa-critic [Medium-High] 지적. 그래서 별도 표시 신호인 ERROR 카테고리를 신설했다
    (LEDGER처럼 영구지만 "판정 데이터"가 아니라 "오류 진단"이라 별도 축).

★AT4 신규 2종(순번19·20)의 문법이 colon인 이유 — LOG-A "신규는 pipe" 규약의 예외:
    LOG-A 계약서는 *"신규 토큰은 pipe key=value"*로 정했다(순번16~18이 그렇다). 그런데
    순번19·20은 **colon**이다. 근거:
    (a) **계열 일관성이 규약보다 구체적이다.** `FXLAB:` 네임스페이스의 형제 4종(15/15b/15c)이
        전부 colon이고, 파서는 `FXLAB:` 프리픽스로 이들을 한 덩어리로 다룬다. 한 계열 안에
        문법이 둘이면 `match_row()` 이후 분기가 토큰마다 달라진다.
    (b) **pipe의 이점이 여기선 안 산다.** pipe kv는 "나중에 필드가 늘어도 위치가 안 밀린다"가
        핵심 이점인데, 19는 필드 1개이고 20은 5필드 전부 숫자 ID 고정이다. BattleLog의 `died`
        처럼 유무에 따라 자리가 밀리는 가변 필드가 없다(그 사고가 pipe 채택의 실제 동기였다).
    (c) FXLAB은 **실험대 전용 진단 계열**이지 라이브 원장이 아니다. pipe 규약의 적용 대상은
        원장·흐름(LEDGER/FLOW)이며, 실제로 순번16~18은 전부 그쪽이다.
    ★즉 규약은 유지된다 — "라이브 원장·흐름 신규는 pipe / FXLAB 실험대 계열은 계열 문법을
    따른다"로 읽는다. 이 예외를 여기 적어두지 않으면 다음 사람이 19·20을 규약 위반으로 보고
    pipe로 "고쳐" PrintString 리터럴과 어긋나게 만든다(★3주 드리프트가 난 방식 그대로).

이 파일이 바뀌면(신규 토큰 추가 등) `render_category_markdown()`을 재실행해
`Resource/docs/전투로그.md`의 카테고리 표 절을 재생성한다.
"""
from __future__ import annotations

from dataclasses import dataclass

LEDGER = "LEDGER"
FLOW = "FLOW"
STAGE = "STAGE"
DIAG = "DIAG"
ERROR = "ERROR"
# UNAFFILIATED = 4(5)종 bool 게이팅 체계 밖. 어느 bLog* 에도 걸리지 않고 항상 찍힌다.
# SessionBoundary 전용 — qa-critic FT1-0_TC.md [High] "SessionBoundary=LEDGER 반박" 반영:
# 세션 분할은 원장(LEDGER)만의 전제가 아니라 FLOW·STAGE·DIAG·ERROR 파싱 전부의 전제이므로
# 특정 카테고리에 속하면 그 카테고리를 끄는 순간 세션 경계가 사라진다. "모든 카테고리의
# 파싱 전제"이므로 카테고리 밖에 둔다(LOG-A_실행계획.md 원문의 LEDGER 배정을 대체).
UNAFFILIATED = "UNAFFILIATED"

# 토글 가능한(bLog* 4개에 대응하는) 카테고리만. UNAFFILIATED는 토글 대상이 아니므로 제외.
CATEGORIES = (LEDGER, FLOW, STAGE, DIAG, ERROR)

# 카테고리 기본 ON/OFF. bLogLedger/Flow/Stage/Error=true(끄지 않음 원칙 — ERROR는 UI상
# 체크박스가 있어도 규범적으로 끄지 말 것을 계약서에 경고), bLogDiag=false.
# UNAFFILIATED(SessionBoundary)는 bool 자체가 없다 — 상수 true로 PrintString에 직결.
DEFAULT_ON = {
    LEDGER: True,
    FLOW: True,
    STAGE: True,
    DIAG: False,
    ERROR: True,
}
# 끄면 안 되는 카테고리(규범 — 체크박스가 있어도 규약상 끄지 않는다).
DO_NOT_DISABLE = (LEDGER, ERROR)

PIPE_KV = "pipe_kv"      # Tag|k=v|k=v|...
COLON_POS = "colon_pos"  # Tag:field1:field2:... 위치 기반(key=value 아님)
PLAIN = "plain"          # Tag:literal 또는 Tag:N (필드 파싱 불요)


@dataclass(frozen=True)
class LogRow:
    row: str          # 점검 문서 §1-1 표 순번("1".."15","15b","15c") 또는 신규("16".."18")
    label: str        # 표에 쓰인 원문 라벨(사람이 읽는 용도)
    prefixes: tuple    # 실제 라인(프리픽스 스트립 후) 매칭 프리픽스들
    category: str      # LEDGER/FLOW/STAGE/DIAG/ERROR/UNAFFILIATED
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
           "승패·재시작 구분. State:(순번2)와 다른 토큰(우발적 네이밍 충돌 — 소급 통일 안 함). "
           "★event=INIT은 세션 키의 2번째 축(sid, INIT 순번)에도 쓰인다 — battle_log.session 참고"),
    LogRow("14", "StatusLog|turn=...", ("StatusLog|",), LEDGER, PIPE_KV,
           "상태이상 지속시간·스킵·해제 판정"),
    LogRow("15", "FXLAB:DIAG", ("FXLAB:DIAG",), DIAG, COLON_POS,
           "임시 진단 3줄. 기본 OFF — 켜진 채 남으면 오염(실측: FXLAB:DIAG가 실제로 이렇게 남아있었음)"),
    LogRow("15b", "FXLAB:FXSKIP/TEXMISS/FXNOROW", ("FXLAB:FXSKIP", "FXLAB:TEXMISS", "FXLAB:FXNOROW"),
           ERROR, COLON_POS,
           "★qa-critic 반박 반영(FT1-0_TC.md [Medium-High]) — fail-loud 정식 오류 신호"
           "(행 없음/프레임 0/텍스처 캐스트 실패 구분)를 STAGE(개발중에만 ON)에 두면 베타에서 "
           "끄는 순간 오류 보고가 침묵한다. 그래서 ERROR로 분리하고 끄지 않는다(DO_NOT_DISABLE)"),
    LogRow("15c", "FXLAB:FXSHOW/FXHIDE", ("FXLAB:FXSHOW", "FXLAB:FXHIDE"), STAGE, COLON_POS,
           "정상 표시/숨김 성공 경로(연출 진단). 점검 §1-1 각주 — 실측 0회 관측이나 "
           "E-S2_FxLabQuad_결과.md에 설계 근거가 있어 카테고리 표에서 누락시키지 않음"),
    LogRow("16", "SessionBoundary|sid=...|event=BeginPlay|...", ("SessionBoundary|",),
           UNAFFILIATED, PIPE_KV,
           "★신규. ★qa-critic 반박 반영(FT1-0_TC.md [High]) — 세션 분할은 LEDGER 하나의 "
           "전제가 아니라 FLOW·STAGE·DIAG·ERROR 파싱 전부의 전제라 카테고리 무소속(무조건 ON, "
           "bLog* 어디에도 안 걸림). sid 산식·세션 키는 battle_log.session/oracle 문서 참고. "
           "이번 단계는 문법 확정만(실제 심기는 FT1-0a)"),
    LogRow("17", "PlayAttack|unit=SpawnPoint_...|phase=enter|exit|t=...", ("PlayAttack|",),
           FLOW, PIPE_KV,
           "★신규. 애니메이션 함수 블로킹 여부 판정(점검 §2-1). unit= 값은 BattleLog와 동일 원문"
           "(SpawnPoint_<Team>_<Slot>) — 조인 규칙 통일. 이번 단계는 문법 확정만(FT1-0b에서 심음)"),
    LogRow("18", "SkillSelected|unit=SpawnPoint_...|skillId=...|state=...", ("SkillSelected|",),
           FLOW, PIPE_KV,
           "★신규. 스킬 선택 로그(오너 질문①). 이번 단계는 문법 확정만(FT1-0c에서 심음 — "
           "FT1-0c는 qa-critic이 '설계 미확정'으로 표시한 단계라 필드 상세는 FT1-0c 착수 시 확정)"),
    LogRow("19", "FXLAB:STGNOROW:<stagingId>", ("FXLAB:STGNOROW",), ERROR, COLON_POS,
           "★AT4 신규. GetDataTableRow(DT_Stagings) RowNotFound exec 직후 fail-loud. "
           "15b(FXNOROW)와 동형이라 같은 ERROR — STAGE에 두면 베타에서 끄는 순간 침묵한다. "
           "★문법이 pipe가 아니라 colon인 이유는 아래 주석 참고"),
    LogRow("20", "FXLAB:RESOLVE:<skillId>:<stagingId>:<fxCast>:<fxProj>:<fxImpact>",
           ("FXLAB:RESOLVE",), STAGE, COLON_POS,
           "★AT4 신규. stagings/skills 해석 결과를 그대로 뱉는 검증 신호 — AU-A5-05(DT_Skills "
           "신규 6필드가 FxLab Director까지 흘러왔는가, 상류 1홉 관통)의 판정 근거다. "
           "★DIAG 금지: DIAG는 기본 OFF라 AU-A5-05가 실행 불가가 된다(qa-critic 지적). "
           "5필드 전부 숫자 ID 고정이라 위치 기반이 안전하다 — BattleLog의 died처럼 "
           "유무에 따라 자리가 밀리는 가변 필드가 없다"),
)


def all_prefixes() -> tuple:
    """모든 매칭 프리픽스를 (prefix, row) 쌍으로, prefix 길이 내림차순 정렬해 반환.

    길이 내림차순인 이유: `FXLAB:FXSKIP`(13자)가 `FXLAB:`류 일반형보다, `TakeHitRevert:`(14자)가
    `TakeHit:`(8자)보다 먼저 매칭돼야 한다(더 구체적인 쪽 우선 — qa-critic이 지적한 "구현 순서
    의존 버그"를 이 정렬 규칙으로 원천 차단).
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


def rows_by_category(category: str) -> tuple:
    return tuple(r for r in ROWS if r.category == category)


# ---------------------------------------------------------------------------
# ★SSOT 생성기 — 전투로그.md의 카테고리 표는 이 함수 출력을 그대로 붙여넣은 것이다.
# 재생성: `python -c "from battle_log import tokens; print(tokens.render_category_markdown())"`
# ---------------------------------------------------------------------------
_CATEGORY_ORDER = (LEDGER, FLOW, STAGE, ERROR, DIAG, UNAFFILIATED)
_CATEGORY_DESC = {
    LEDGER: ("영구", "ON(끄지 않음)", "전투 원장 1차 데이터 — 밸런스 회귀·오라클 대조의 근거"),
    FLOW: ("알파~베타", "ON", "상태머신·연출 타이밍 등 개발기 판정"),
    STAGE: ("개발 중", "ON", "연출·시각 검증 — 개발 완료 후 끌 수 있음"),
    ERROR: ("영구", "ON(끄지 않음)", "fail-loud 정식 오류 신호 — 베타에도 침묵시키지 않는다"),
    DIAG: ("일회성", "OFF", "임시 진단 — 켜진 채 방치되면 로그 오염(실측 사례 있음)"),
    UNAFFILIATED: ("영구", "ON(bool 없음, 상수)", "세션 경계 — 모든 카테고리 파싱의 전제라 무소속"),
}


def render_category_markdown() -> str:
    """전투로그.md에 붙여넣을 카테고리 표를 ROWS에서 생성. tokens.py가 정본, 이 출력은 생성물."""
    lines = []
    lines.append("| 카테고리 | 수명 | 기본값 | 성격 |")
    lines.append("|---|---|---|---|")
    for cat in _CATEGORY_ORDER:
        life, default, desc = _CATEGORY_DESC[cat]
        lines.append(f"| **{cat}** | {life} | {default} | {desc} |")
    lines.append("")
    lines.append("| 순번 | 토큰(프리픽스) | 카테고리 | 문법 | 비고 |")
    lines.append("|---|---|---|---|---|")
    for row in ROWS:
        prefixes_str = " / ".join(f"`{p}`" for p in row.prefixes)
        lines.append(f"| {row.row} | {prefixes_str} | {row.category} | {row.syntax} | {row.note} |")
    return "\n".join(lines)
