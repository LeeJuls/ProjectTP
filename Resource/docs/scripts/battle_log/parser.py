"""라인 프리픽스 분리 + pipe key=value 파싱.

UE 원본 로그 라인 실측 포맷(LogBlueprintUserMessages):
    [2026.08.11-22.32.06:160][596]LogBlueprintUserMessages: [BP_BattleManager_C_0] <내용>

`strip_prefix()`가 `[타임스탬프][프레임카운터]LogCategory: [ActorLabel] ` 부분을 스트립하고
`<내용>`만 반환한다. R-3 음성시험(연출 타이밍만 다른 두 로그 → diff 0)의 대상이 정확히 이 함수다
— 타임스탬프·프레임카운터가 달라도 `<내용>`이 같으면 이 함수의 출력은 같아야 한다.

★`died` 위치 가변 — `effect`/`effectRoll`/`effectApplied` 3필드 유무에 따라 `died`가
6번째(부재 시) ↔ 10번째(존재 시) 필드로 움직인다. 그래서 pipe 라인은 반드시
`parse_pipe_kv()`로 dict화해서 키로 접근한다. 위치(인덱스) 기반 파싱 금지.
"""
from __future__ import annotations

import re

# [2026.08.11-22.32.06:160][596]LogBlueprintUserMessages: [BP_BattleManager_C_0] <rest>
# 프레임카운터 칸이 우측 정렬 공백 패딩되기도 한다: [  9] · [ 56] · [596]
_PREFIX_RE = re.compile(
    r"^\[[0-9.\-:]+\]\[\s*\d+\]Log\w+:\s*(?:\[[^\]]*\]\s*)?(?P<rest>.*)$"
)


def strip_prefix(raw_line: str):
    """엔진 로그 프리픽스를 스트립. 매칭 안 되면(엔진 로그 라인이 아니면) None.

    `extract_battle_log.py` 산출물(`# source:` 등 헤더 3줄 포함)이나 빈 줄도
    매칭 실패로 None을 반환하므로, 소비자는 None을 건너뛰면 된다.
    """
    m = _PREFIX_RE.match(raw_line)
    if not m:
        return None
    return m.group("rest")


def parse_pipe_kv(content: str):
    """`Tag|k=v|k=v|...` 형식을 dict로. pipe가 없으면 None.

    반환 dict의 `_tag` 키에 태그명(첫 토큰, 예: "BattleLog")이 들어간다.
    `=`가 없는 필드는 무시하지 않고 원문을 버리지 않는다는 원칙 하에, 값 없는 키는
    빈 문자열로 채우지 않고 그냥 건너뛴다(현재 15+3종 토큰 중 이런 필드는 관측 0건 —
    있다면 AU-B2-06 필드 append 내성 시험에서 드러난다).
    """
    if "|" not in content:
        return None
    parts = content.split("|")
    tag = parts[0]
    result = {"_tag": tag}
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, _, value = part.partition("=")
        result[key] = value
    return result


def iter_pipe_events(raw_lines, tag: str):
    """원본(프리픽스 포함) 라인들에서 `<tag>|...` 라인만 골라 dict로 yield.

    `tag`는 파이프 앞 토큰 이름(예: 원장 토큰 이름, 상태이상 토큰 이름) — 호출부가
    `battle_log.tokens`의 LogRow.prefixes에서 얻어와야 하며, 이 함수 자체는 특정
    토큰 프리픽스 리터럴을 상수로 갖지 않는다(게이트③: 리터럴 프리픽스는 tokens.py 한 곳뿐).
    """
    marker = f"{tag}|"
    for raw in raw_lines:
        if marker not in raw:
            continue
        content = strip_prefix(raw)
        if content is None:
            continue
        event = parse_pipe_kv(content)
        if event is None or event.get("_tag") != tag:
            continue
        yield event
