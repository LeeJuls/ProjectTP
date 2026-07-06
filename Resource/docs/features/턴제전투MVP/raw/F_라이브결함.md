---
type: raw
feature: 턴제전투MVP
updated: 2026-07-07
---

# F단계 라이브 결함 핫픽스 실행 기록 (gameplay-engineer)

> 상위: [[../plan|턴제전투MVP plan]] · [[../청사진|청사진]] · 선행: [[E3_게이트]]
> 오너가 F단계 라이브 핫시트 테스트 중 발견한 결함 5건(치명 2·시인성 2·정리 1) + 보너스 로그 1건. 원인은 Director가 라이브 로그·프로퍼티 조회로 사전 확정한 상태로 지시서 수령 → 재조사 없이 즉시 수정 진행.
#projectTP/턴제전투MVP

## ① [치명] Sprite 쿼드가 클릭 차단 — 유닛 콜리전 정리

**원인**: `BP_BattleSpawnPoint`의 `Sprite`(SM_SpriteQuad, 648cm) 콜리전이 `BlockAllDynamic`이라 PC 클릭 트레이스(Visibility 채널)를 전부 흡수 → 뒤 유닛들의 `ClickBox`에 클릭이 도달 못함.

**수정**: BeginPlay 체인 끝(`SetCollisionResponseToChannel(ClickBox)`의 `then`, 원래 미연결)에 신규 노드 2개 추가:
- `SetCollisionEnabled(Sprite, NoCollision)` (K2Node_CallFunction_78, self=`GetSprite`의 output 재사용)
- `SetCollisionEnabled(TurnMarker, NoCollision)` (K2Node_CallFunction_79, self=`GetTurnMarker`의 output 재사용)

그래프 노드 방식으로 처리(CLAUDE.md 원칙 — 콜리전은 BeginPlay 그래프 노드로, 인스턴스 프로퍼티 직접 세팅 금지). `NewType` enum 핀은 노드 생성 시 기본값이 이미 `NoCollision`이라 별도 set_pin_value 불필요했음(재조회로 확인).

**검증**: `get_node_infos` 재조회로 체인 `SetCollisionResponseToChannel → SetCollisionEnabled(Sprite) → SetCollisionEnabled(TurnMarker)` 정확히 배선됨 확인. 에디터 동작(End키 스냅 등)은 BeginPlay 미실행이라 이 변경으로 무영향 유지.

이 함정은 실전노하우 §10 함정⑧로 신규 등재(투명 스프라이트 쿼드가 클릭 방패가 되는 함정).

## ② [치명] BP_AttackButton의 LabelCancel 미설정

**원인 실측**: 레벨 인스턴스(`BP_AttackButton_C_0.LabelCancel`)의 트랜스폼이 `relativeLocation(0,0,0)`·`relativeRotation(0,0,0)`·`worldSize 26`·`text "Text"`로, 기존 `Label`의 확정값(`relativeLocation(40,0,72)`·`relativeRotation(pitch90,yaw0,roll180)`·`worldSize 50`·`text "Attack"`, `textRenderColor (1, 0.949, 0.6, 1)`)과 완전히 어긋나 있었음 — 옆면이라 안 보이고 내용도 틀림.

CDO(`BP_AttackButton_C:LabelCancel_GEN_VARIABLE`)를 먼저 조회한 결과 CDO 자체는 이미 `relativeLocation(0,0,2)`·`relativeRotation(0,0,0)`·`worldSize 48`·`text "Cancel"`(해석값)로, Label의 CDO 값(동일 트랜스폼)과는 일치했으나 지시서가 요구한 목표값(Label **인스턴스** 확정값)과는 다른 상태였음.

**수정**: 레벨 인스턴스와 CDO 양쪽에 동일하게 적용.
- `worldSize`: 50
- `text`: `LOCTABLE("/Game/UI/ST_UI", "Battle.Cancel")` — 스트링테이블 `ST_UI`에 `Battle.Cancel="Cancel"` 키가 이미 존재함을 `list_keys`로 확인 후 임포트 문자열로 설정(신규 키 생성 불필요, 기존 E2 산출물).
- `relativeLocation`: (40, 0, 72)
- `relativeRotation`: (pitch 90, yaw 0, roll 180)
- `textRenderColor`: (1.0, 0.949..., 0.6, 1.0) — Label과 동일 가독 흰빛 계열

**§7 함정③(인라인 구조체 set_properties 비결정성) 실측 재현**: `relativeLocation`/`relativeRotation` 첫 호출에서 각각 1개 필드만 반영됨(location은 x만, z=0으로 남음 / rotation은 pitch만, roll=0으로 남음). 재조회로 불일치 확인 후 **동일 페이로드를 키 순서 바꿔 재호출** → 전 필드 정확히 반영 확인. `textRenderColor`(4필드)는 첫 호출에 전부 반영(비결정성 재현 안 됨 — 노하우 문서의 "비결정적" 서술과 일치). CDO 세팅은 이번엔 전 프로퍼티 1회 호출로 전부 반영됨(재현 안 됨).

**검증**: 레벨 인스턴스·CDO 양쪽 `get_properties` 재조회로 Label 확정값과 완전 일치 확인(6개 필드 전부).
```
relativeLocation: {x:40, y:0, z:72}
relativeRotation: {pitch:90, yaw:0, roll:180}
relativeScale3D:  {x:1, y:1, z:1}
worldSize: 50
text: "Cancel"  (해석값)
textRenderColor: {r:1, g:0.9490196704864502, b:0.60000002384185791, a:1}
```
런타임 `SetText` 재배선은 시도하지 않음(§6 노하우의 함정 — 무반영 확인된 경로를 재사용할 이유 없음, 에디터 프로퍼티 직접 설정으로 충분).

## ③ [시인성] 턴 마커가 너무 작음

**수정**: `BP_BattleSpawnPoint` BeginPlay의 `TurnMarker SetWorldScale3D` 핀 값(MakeVector 노드 `K2Node_CallFunction_57`) X: 0.5→**1.2**, Y: 0.35→**0.8** (Z=1.0 불변). `set_pin_value`로 핀 값만 변경, 그래프 구조 불변. 재조회로 확인.

## ④ [시인성] 타겟 하이라이트가 안 보임

**수정**: `HighlightOn` 이벤트의 `SetScalarParameterValue(EmissiveBoost)` 노드(`K2Node_CallFunction_39`) Value 핀 2.0→**6.0**. `set_pin_value`로 핀 값만 변경. 재조회로 확인.

## ⑤ [정리] State 디버그 텍스트가 화면에 노출

**대상 전수 조사**: `BP_BattleManager`의 전 그래프(EventGraph·NotifyUnitClicked·RegisterUnitReady·InitBattle·EnterTurnStart·EnterAwaitCommand·EnterAwaitTarget·NotifyAttackButtonClicked)를 `find_nodes`+`get_connected_subgraph`로 전수 조회해 PrintString/PrintText 노드 11개를 확인.

**Screen=true→false로 변경한 10개**:
| 그래프 | 노드 | 메시지 |
|---|---|---|
| EventGraph | K2Node_CallFunction_18 | "State:TurnEnd:t={0}" |
| EventGraph | K2Node_CallFunction_10 | "State:Executing:t={0}" |
| NotifyUnitClicked | K2Node_CallFunction_4 | "ignored (same team or self)" |
| NotifyUnitClicked | K2Node_CallFunction_3 | "ignored (not in AwaitTarget state)" |
| InitBattle | K2Node_CallFunction_1 | "State:Init:t={0}" |
| InitBattle | K2Node_CallFunction_2 | "Init ERROR: TurnQueue length is 0..." |
| EnterTurnStart | K2Node_CallFunction_1 | "State:TurnStart:t={0}" |
| EnterAwaitCommand | K2Node_CallFunction_1 | "State:AwaitCommand:t={0}" |
| EnterAwaitTarget | K2Node_CallFunction_1 | "State:AwaitTarget:t={0}" |
| NotifyAttackButtonClicked | K2Node_CallFunction_2 | "BLOCKED (bInputLocked=true)" |

**이미 조건 충족(변경 불필요)**: `RegisterUnitReady.K2Node_CallFunction_0`("Registered:{0}", PrintText, 이미 Screen=false/Log=true) / `BP_BattleSpawnPoint.TakeHit`의 PrintText 2개(K2Node_CallFunction_34·35, "TakeHit:{0}"/"TakeHitRevert:{0}", 이미 Screen=false/Log=true — E2에서 이미 처리된 것으로 확인). `bPrintToLog`는 전 11개 노드 모두 재확인 결과 `true` 유지(판정 체계 보존).

**검증**: 10개 노드 전부 `get_pin_value` 재조회로 `false` 확인.

## 보너스: NotifyUnitClicked 유효 클릭 경로 로그 추가

`NotifyUnitClicked`의 유효 클릭 판정 경로(`bInputLocked==false` → `BattleState==AwaitTarget` → `bIsParty(ClickedUnit)!=bIsParty(ActiveUnit)`, 전부 통과 시 `SetSelectedTarget`)와 `EnterExecuting()` 호출 사이에 신규 로그 삽입.

**구성 노드**(모두 신규 생성): `GetDisplayName(Object=ClickedUnit)`(String) → `FormatText(Format="UnitClicked:{0}:valid", 인자0=위 String)`(Text) → `ToString(Text)`(String) → `PrintString(bPrintToScreen=false, bPrintToLog=true)`.

**exec 재배선**: 기존 `SetSelectedTarget.then → EnterExecuting.execute` 직결을 `break_pins`로 끊고, `SetSelectedTarget.then → PrintString.execute → PrintString.then → EnterExecuting.execute`로 재배선. `get_node_infos` 재조회로 체인 정확성 확인.

## 검증 절차 실행 기록

1. **compile_blueprint(warnings_as_errors=true) 3 BP 전부 에러 0** — BP_BattleSpawnPoint/BP_AttackButton/BP_BattleManager 개별 확인.
2. **StartPIE(warmup 2s) → GetLogEntries**: 1차 시도에서 로그가 수 시간 전 타임스탬프에 멈춰 최신 반영이 확인 안 되는 현상 발생(원인 불명, 재현조건 미확정 — 실전노하우 §10에 별도 기록). StopPIE 후 `get_current_level` 정상 반환으로 로그 시스템 자체 이상은 배제. **재시도(StartPIE warmup 3s)에서 정상 반영 확인**: `Registered:1~8 → State:Init:t=0 → State:TurnStart:t=0 → State:AwaitCommand:t=0` 순서대로 정확히 로그 발생. 화면 출력(Screen=false) 자체의 시각 확인은 지시서에 따라 스캐폴드하지 않고 오너 실플레이로 이월.
3. **LabelCancel 재조회**: 위 ②절 표 참고 — 레벨 인스턴스·CDO 양쪽 6개 필드 전부 Label 기준값과 일치 확인.
4. **StopPIE → save_assets**(`BP_BattleSpawnPoint`·`BP_AttackButton`·`BP_BattleManager`·`map_battle_octopath`·`ST_UI`) → `is_dirty` 재조회 5개 전부 `false`. `map_battle_village`(village 회귀 확인용)도 `is_dirty=false` 확인(변경 없음).

## 최종 상태

- 3개 핵심 BP `compile_blueprint(warnings_as_errors=true)` 전부 에러 0.
- 5개 관련 에셋 + village 레벨 전부 `is_dirty=false`.
- `IsPIERunning=false`(PIE 완전 종료), 현재 로드 레벨 `/Game/Stages/map_battle_octopath`.

## 이월 항목 (Director 보고)

1. **StartPIE 직후 GetLogEntries가 한 번 최신 로그를 반영하지 않은 현상** — 재시도로 해결됐으나 근본 원인 미규명. 실전노하우 §10에 조건부 관찰로 기록, 후속 세션에서 재현 시도 권장.
2. **화면 출력(Screen=false 적용분) 시각 확인**은 지시서 지침에 따라 스캐폴드하지 않음 — 오너가 다음 실플레이에서 화면에 State 텍스트가 안 뜨는지 직접 확인 필요.
3. **클릭 경로(①의 실제 클릭 성공 여부) 시각 확인**도 동일하게 오너 실플레이 확인 필요(지시서 명시 사항, 스캐폴드로 대체하지 않음 — 함정⑥ 그림자 액터 회피 원칙 준수).
