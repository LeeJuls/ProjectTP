"""라인 프리픽스 분리 + pipe key=value 파싱.

UE 원본 로그 라인 실측 포맷(LogBlueprintUserMessages):
    [2026.08.11-22.32.06:160][596]LogBlueprintUserMessages: [BP_BattleManager_C_0] <내용>

`parse_line_meta()`가 `[타임스탬프][프레임카운터]LogCategory: [ActorLabel] ` 부분과
`<내용>`을 **한 정규식 매치에서 동시에** 뽑는다. `strip_prefix()`는 그 `<내용>`만 반환하는
얇은 래퍼다. R-3 음성시험(연출 타이밍만 다른 두 로그 → diff 0)의 대상이 정확히 이 스트립
동작이다 — 타임스탬프·프레임카운터가 달라도 `<내용>`이 같으면 결과가 같아야 한다.

★sid 유도 순서 계약(FT1-0_TC.md §3-A): `SessionBoundary|` 라인의 sid는 이 프리픽스의
타임스탬프(`ts`)에서 유도된다(`battle_log.session.derive_sid`). **스트립을 먼저 해서
`<내용>`만 넘기면 sid의 원천이 사라진다** — 그래서 `parse_line_meta()`가 ts와 rest를
분리된 두 단계가 아니라 하나의 매치로 동시에 반환하도록 설계했다. `strip_prefix()`만 쓰는
기존 소비자는 ts를 버리지만, sid가 필요한 소비자(`battle_log.session`)는 반드시
`parse_line_meta()`를 직접 호출해 ts를 함께 받는다 — "내용만 있는 상태에서 사후적으로
sid를 만들려는" 경로 자체가 코드에 없다.

★`died` 위치 가변 — `effect`/`effectRoll`/`effectApplied` 3필드 유무에 따라 `died`가
6번째(부재 시) ↔ 10번째(존재 시) 필드로 움직인다. 그래서 pipe 라인은 반드시
`parse_pipe_kv()`로 dict화해서 키로 접근한다. 위치(인덱스) 기반 파싱 금지.
"""
from __future__ import annotations

import re

# [2026.08.11-22.32.06:160][596]LogBlueprintUserMessages: [BP_BattleManager_C_0] <rest>
# 프레임카운터 칸이 우측 정렬 공백 패딩되기도 한다: [  9] · [ 56] · [596]
_META_RE = re.compile(
    r"^\[(?P<ts>[0-9.\-:]+)\]\[\s*(?P<frame>\d+)\]Log\w+:\s*(?:\[[^\]]*\]\s*)?(?P<rest>.*)$"
)


def parse_line_meta(raw_line: str):
    """엔진 로그 프리픽스에서 (ts, frame, rest)를 한 번에 추출. 매칭 안 되면 None.

    `extract_battle_log.py` 산출물의 `# source:` 등 헤더 3줄이나 빈 줄도 매칭 실패로
    None을 반환한다 — 소비자는 None을 건너뛰면 된다.
    """
    m = _META_RE.match(raw_line)
    if not m:
        return None
    return m.group("ts"), m.group("frame"), m.group("rest")


def strip_prefix(raw_line: str):
    """엔진 로그 프리픽스를 스트립하고 `<내용>`만 반환. 매칭 안 되면 None.

    `parse_line_meta()`의 얇은 래퍼 — ts가 필요 없는 기존 소비자(카테고리 필터 등) 전용.
    """
    meta = parse_line_meta(raw_line)
    return None if meta is None else meta[2]


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


def normalize_number(value: str) -> str:
    """UE가 붙인 천 단위 쉼표를 제거해 숫자 리터럴로 되돌린다. 숫자가 아니면 원문 그대로.

    ★2026-08-12 실측으로 발견한 함정 — 이 함수가 없으면 값이 조용히 틀린다:
        State:AwaitTarget:t=6,915.2      ← 실측. 6915.2초 지점
        `[\\d.]+` 로 잡으면 "6"에서 멈춘다 → 델타가 전부 0이 되고,
        "타임스탬프가 멈췄다"는 **가짜 결함**으로 오독된다(실제로 그렇게 오독했다).

    ★발현 조건이 고약하다 — **값이 1000을 넘어야만** 나타난다. 짧은 세션에서는 영원히
    안 보이다가, 긴 세션(1시간 55분 지점에서 실측됨)에서만 조용히 깨진다. 그래서
    "지금까지 안 났으니 괜찮다"가 근거가 되지 못한다.

    ★적용 대상은 **float 필드**다. UE의 int→string은 쉼표를 안 붙이고(실측:
    `FXLAB:FXNOROW:63009999`), float/Text 변환만 로케일 포맷을 탄다. 따라서 위험한 것은
    `t=` 계열과 소수를 가질 수 있는 수치 필드이며, ★`PlayAttack|...|t=`(tokens 순번17)가
    정확히 여기 해당한다 — **아직 심지 않았으므로 지금이 막을 수 있는 마지막 시점이다.**

    RAW 계약(`dmg`는 무변환)과 충돌하지 않는다: `parse_pipe_kv()`는 값을 원문 그대로 두고,
    **숫자로 해석하려는 소비자만** 이 함수를 거친다. 즉 "원문 보존"과 "숫자 정규화"의
    책임이 분리돼 있다.
    """
    if not value:
        return value
    candidate = value.replace(",", "")
    try:
        float(candidate)
    except ValueError:
        return value  # 숫자가 아니면 쉼표가 의미를 가질 수 있다 — 건드리지 않는다
    return candidate


def iter_pipe_events(raw_lines, tag: str, with_meta: bool = False):
    """원본(프리픽스 포함) 라인들에서 `<tag>|...` 라인만 골라 dict로 yield.

    `tag`는 파이프 앞 토큰 이름(예: 원장 토큰 이름, 상태이상 토큰 이름) — 호출부가
    `battle_log.tokens`의 LogRow.prefixes에서 얻어와야 하며, 이 함수 자체는 특정
    토큰 프리픽스 리터럴을 상수로 갖지 않는다(게이트③: 리터럴 프리픽스는 tokens.py 한 곳뿐).

    `with_meta=True`면 반환 dict에 `_ts`/`_frame`(엔진 프리픽스 메타)도 채워 넣는다.
    기본 False — R-3처럼 "타이밍은 달라도 내용이 같으면 동일 결과"를 diff로 확인하려는
    소비자는 굳이 켤 필요 없다(오히려 ts가 섞이면 그 diff 자체가 오염된다).
    """
    marker = f"{tag}|"
    for raw in raw_lines:
        if marker not in raw:
            continue
        meta = parse_line_meta(raw)
        if meta is None:
            continue
        ts, frame, content = meta
        event = parse_pipe_kv(content)
        if event is None or event.get("_tag") != tag:
            continue
        if with_meta:
            event["_ts"] = ts
            event["_frame"] = frame
        yield event
