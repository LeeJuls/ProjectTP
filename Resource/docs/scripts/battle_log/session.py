"""세션 경계 유도 + 세션 키 계산 — `SessionBoundary|`(순번16) 소비 전용 모듈.

★sid 산식(계약, 전투로그.md에 원문 인용됨):
    sid = 그 세션의 `SessionBoundary|` 라인의 **엔진 프리픽스 벽시계 원문**(ms 해상도), 그대로.
    BP가 GUID/난수를 만들 필요가 없다 — FT1-0_TC.md §3-A가 조사한 3개 BP측 sid 생성 후보
    (`Now()`·`RandomIntegerInRange`·`NewGuid`)는 전부 "MCP로 실제 생성 가능한지 미실증"
    상태였다(선례: `GetRelativeRotation`은 API는 있지만 MCP `create_node`로 어떤 문자열
    형식으로도 생성 불가로 확정된 바 있음). 그래서 **파서 유도를 1차 계약으로 채택**한다 —
    BP는 `SessionBoundary|event=BeginPlay` 상수 1줄만 찍으면 되고(노드 0개), sid는
    이 모듈이 그 줄의 프리픽스에서 뽑는다.
    FT1-0에서 BP측 sid 생성이 실제로 가능하다고 확인되면 `SessionBoundary|`에 `sid=` 필드를
    추가해 `derive_sid()`가 "필드에 있으면 그 값, 없으면 ts"로 승격할 수 있다(하위호환).

★순서 제약(FT1-0_TC.md §3-A 경고 반영): sid 유도는 프리픽스 스트립과 **분리된 이후 단계가
아니라 동시**에 이뤄져야 한다 — 스트립을 먼저 해버리면(내용만 남기면) sid의 원천인 ts가
사라진다. `battle_log.parser.parse_line_meta()`가 ts·frame·rest를 **한 정규식 매치**로
동시에 반환하므로, 이 모듈은 항상 그 함수를 거쳐 ts를 얻는다(rest만 넘겨받는 경로가 없다
— 구조적으로 순서 위반이 불가능하다).

★세션 키 = (sid, init_ordinal). qa-critic FT1-0_TC.md [Medium] 반영 — `sid` 단위는 PIE
1회인데 원장(BattleLog) 단위는 "전투 1판"이다. 한 PIE 안에서 Start/Attack 버튼 재클릭으로
`InitBattle()`이 여러 번 재호출될 수 있다(`State|event=INIT|mode=RESTART` 실측 확인,
전투BP_현황도 §2-6). `init_ordinal`은 그 sid 구간 안에서 `State|event=INIT` 라인을 만날
때마다 1 증가한다(0 = 그 sid의 첫 INIT 이전 예비 구간, 예: BeginPlay 직후 Registered: 8줄).
오라클 20행 diff는 세션 키 단위로 잘라서 비교해야 한다 — sid만으로 자르면 "1 sid에 원장
2벌"이 섞여 20행 diff가 40행을 보게 된다(qa-critic 재현 시나리오).

★세그먼트 순방향 귀속(FT1-S2_04판정.md §3, `AU-F0a-04` 조건부 PASS 이행, 2026-08-13):
    실측(`projectTP.log`)상 Manager `BeginPlay`(마커 발화점)는 SpawnPoint 8기보다 레벨 액터
    순서상 **늦게** 돈다 — 그래서 세션 N(N≥2)의 선두 초기화 로그가 마커보다 먼저 찍힌다.
    구 계약("첫 SessionBoundary| 이전 = None")대로면 이 선두부가 **직전 세션의 sid로
    오귀속**되고, 유령 세션 키와 "첫 전투 원장이 (sid, 0)에 앉는" 계약 위반이 생긴다.
    그래서 `assign_sessions()`는 엔진 `LogWorld: ... up for play (` 라인(`AU-F0a-01`이 이미
    쓰는 구간 정의)을 **세그먼트 앵커**로 승격해, 마커 이전 선두부를 직전 세션이 아니라
    **그 세그먼트 자신의 sid로 소급 귀속**한다. `BeginPlay` 발화 순서(엔진 비보장)와 무관하게
    세션 키가 불변이 되고, `init_ordinal`의 "0 = 그 sid의 첫 INIT 이전 예비 구간" 의미가
    원설계대로 복원된다. 상세 계약 문구·의사코드는 `assign_sessions()` 함수 docstring과
    `FT1-S2_04판정.md` §3-1 참고. 하위호환: `up for play` 라인이 없는 입력(합성 픽스처 등)은
    이 앵커 분기가 발화하지 않아 개정 전과 출력이 100% 동일하다.
"""
from __future__ import annotations

from . import parser


def _session_boundary_prefix() -> str:
    from . import tokens  # 지연 임포트 — 순환 임포트 회피
    return tokens.row_by_number("16").prefixes[0]


def _state_pipe_prefix() -> str:
    from . import tokens
    return tokens.row_by_number("13").prefixes[0]


def derive_sid(ts: str) -> str:
    """SessionBoundary 라인의 ts(엔진 프리픽스 벽시계 원문)를 그대로 sid로 사용."""
    return ts


# ★세그먼트 앵커(AU-F0a-04 세그먼트 순방향 귀속, FT1-S2_04판정.md §3-1). 이 리터럴은 BP
# PrintString 토큰이 아니라 엔진(`LogWorld`) 발화 라인이므로 tokens.py(게이트③: BP 토큰
# 프리픽스의 SSOT) 밖에 모듈 상수로 둔다. 실측 원문(`projectTP.log` L17289):
#   [2026.08.13-03.11.56:600][326]LogWorld: Bringing World
#   /Game/Stages/UEDPIE_0_map_battle_octopath.map_battle_octopath up for play
#   (max tick rate 3) at 2026.08.13-12.11.56
_WORLD_UP_FOR_PLAY = (" up for play (", "]LogWorld: Bringing World ")


def assign_sessions(raw_lines):
    """raw_lines(프리픽스 포함)를 세션 경계로 분할해 [(sid_or_None, raw_line), ...]를 반환.

    ★세그먼트 순방향 귀속(AU-F0a-04 조건부 PASS 이행 — FT1-S2_04판정.md §3):
    세그먼트 = 엔진 `up for play` 라인에서 다음 `up for play` 라인까지(`AU-F0a-01`이 이미
    쓰는 구간 정의를 파서에 승격한 것). 세그먼트의 sid = 그 세그먼트 안 첫
    `SessionBoundary|` 마커의 프리픽스 ts이며, ★마커 이전 선두부(BeginPlay 경합 구간 —
    SpawnPoint 8기가 Manager보다 레벨 액터 순서상 먼저 도는 구조 때문에 생긴다. 엔진이
    액터 간 BeginPlay 순서를 보장하지 않으므로 파서 좌표계에서 흡수한다)도 **소급하여 그
    세그먼트 자신의 sid로 귀속**한다 — 직전 세그먼트로 새지 않는다.

    마커가 없는 세그먼트(EOF까지 또는 다음 `up for play`까지 마커 미발화)는 전체 `None`으로
    라벨링한다(직전 세션에 조용히 병합하지 않는다 — `AU-F0a-05` 롤오버 내성 계약 계승,
    fail-loud 유지). 파일 선두에 `up for play` 라인 자체가 없으면(첫 세그먼트 이전 잡음 등)
    첫 `SessionBoundary|` 이전 구간도 동일하게 **None**이다.

    `init_ordinal`(→ `assign_session_keys`)의 의미는 불변("그 sid 구간 안 INIT 카운트")이나,
    ★마커 라인 자신은 발화 순서에 따라 ordinal 0 또는 1에 앉을 수 있다 — 마커의 역할은 sid
    공급뿐, ordinal 판정에는 쓰지 않는다.

    ★하위호환: 입력에 `up for play` 라인이 없으면(합성 픽스처 등 엔진 라인이 없는 입력)
    첫 분기가 한 번도 발화하지 않아 개정 전 로직과 출력이 100% 동일하다.
    """
    boundary_prefix = _session_boundary_prefix()
    out = []
    current_sid = None
    pending = None  # None = 버퍼링 비활성 / list = `up for play` 이후 마커 대기 중(세그먼트 선두부)
    for raw in raw_lines:
        if all(marker in raw for marker in _WORLD_UP_FOR_PLAY):
            if pending is not None:            # 직전 세그먼트가 마커 없이 끝남 — fail-safe
                out.extend((None, r) for r in pending)
            pending = [raw]                    # 새 세그먼트 개시(이 줄 자신도 선두부에 포함)
            current_sid = None                 # ★직전 sid 전파 차단 지점
            continue
        meta = parser.parse_line_meta(raw)
        if meta is not None:
            ts, _frame, content = meta
            if content.startswith(boundary_prefix):
                current_sid = derive_sid(ts)
                if pending is not None:        # ★세그먼트 선두부(BeginPlay 경합 구간) 소급 귀속
                    out.extend((current_sid, r) for r in pending)
                    pending = None
                out.append((current_sid, raw))
                continue
        if pending is not None:
            pending.append(raw)
        else:
            out.append((current_sid, raw))
    if pending is not None:                    # EOF까지 마커 없음 — fail-safe(전체 None)
        out.extend((None, r) for r in pending)
    return out


def assign_session_keys(raw_lines):
    """[((sid_or_None, init_ordinal), raw_line), ...] 반환.

    같은 sid 구간 안에서 `State|event=INIT` 라인을 만날 때마다 init_ordinal이 1 증가한다.
    """
    state_prefix = _state_pipe_prefix()
    sessioned = assign_sessions(raw_lines)

    out = []
    _UNSET = object()
    last_sid = _UNSET
    ordinal = 0
    for sid, raw in sessioned:
        if sid != last_sid:
            ordinal = 0
            last_sid = sid
        meta = parser.parse_line_meta(raw)
        if meta is not None:
            _, _, content = meta
            if content.startswith(state_prefix):
                event = parser.parse_pipe_kv(content)
                if event is not None and event.get("event") == "INIT":
                    ordinal += 1
        out.append(((sid, ordinal), raw))
    return out
