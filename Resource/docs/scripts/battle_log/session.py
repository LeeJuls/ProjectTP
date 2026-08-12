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


def assign_sessions(raw_lines):
    """raw_lines(프리픽스 포함)를 세션 경계로 분할해 [(sid_or_None, raw_line), ...]를 반환.

    `sid_or_None`: 첫 `SessionBoundary|` 라인 이전 구간은 **None**으로 명시 라벨링한다
    (직전 세션에 조용히 병합하지 않는다 — FT1-0 AU-F0a-05 롤오버 내성 계약).
    """
    boundary_prefix = _session_boundary_prefix()
    out = []
    current_sid = None
    for raw in raw_lines:
        meta = parser.parse_line_meta(raw)
        if meta is not None:
            ts, _frame, content = meta
            if content.startswith(boundary_prefix):
                current_sid = derive_sid(ts)
        out.append((current_sid, raw))
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
