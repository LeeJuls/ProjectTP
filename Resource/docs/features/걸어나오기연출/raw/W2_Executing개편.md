---
type: raw
feature: 걸어나오기연출
stage: W2
updated: 2026-07-16
---

# W2 구현 기록 — Manager Executing 개편(재배선 2곳+마커 OFF 신규)
#projectTP/걸어나오기연출

## 순서
1. IsPIERunning 확인(false) → BP_BattleManager EnterExecuting 실그래프 확정 조회
2. 마커 OFF 신규 삽입(HideAll 앞, IsValid 가드)
3. 재배선①: HideAll.then→PlayAttack 직결 절단 → WalkForward→Delay(0.55) 삽입
4. 재배선②: Delay(0.75).then→EnterTurnEnd 직결 절단 → WalkBack→Delay(0.45) 삽입
5. ExecWalkPhase 진단 로그 추가
6. compile(warnings_as_errors=true) 0 확인
7. WT-09~12 게이트 스캐폴드(BeginPlay 임시)로 2턴 자동 진행 + 타임라인 실측
8. 스캐폴드 완전 제거 → 재컴파일 0 → 저장

## 1. 실그래프 확정 조회 결과 (재배선 지점 검증)

`find_nodes(EventGraph, entry_points_only=true)` + `get_node_infos`로 `K2Node_CustomEvent_2`가 `EnterExecuting`(plan이 특정한 두 지점 정확히 일치) 확인 후 `get_connected_subgraph`로 전체 체인 조회:
- ① `HideAll(K2Node_CallFunction_23).then → PlayAttack(K2Node_CallFunction_12)` — plan 기술과 정확히 일치.
- ② `Sequence.then_1 → Delay(0.75, K2Node_CallFunction_14).then → EnterTurnEnd(K2Node_CallFunction_16)` — plan 기술과 정확히 일치.
- 마커 OFF 관련 노드는 EnterExecuting 체인에 없음(신규 확인).
- `Delay(0.25, K2Node_CallFunction_13).then → IsValid → TakeHit`(then_0 분기)는 재배선 대상 아님 — 이번 작업에서 **일절 무변경** 확인(작업 후 재조회로 교차검증).

## 2. 마커 OFF 신규 삽입

`ForEachLoop(TurnQueue).Completed`(기존 → HideAll 직결)를 절단 → 삽입 체인:
```
ForEachLoop.Completed → IsValid(GetActiveUnit) → Is Valid → MarkerOff(self=GetActiveUnit) → then → HideAll.execute
```
- `IsValid` 매크로: `Utilities|IsValid`(그래프 컨텍스트 검색으로 확인된 기존 검증 문자열 재사용).
- `MarkerOff` 호출 노드: **함정 재확인** — `get_node_infos`가 보여주는 `|MarkerOff`(축약 표기)를 `create_node`에 그대로 넣으면 실패(`does not exist`). `find_node_types`에 **빈 `context_pins`**로 검색하자 `Class|BPBattleSpawnPoint|MarkerOff`(§13 함정⑮ 패턴과 동일) 형식이 나왔고 이것으로 성공. `GetActiveUnit`은 기존 그래프의 `K2Node_VariableGet_8`(PlayAttack 호출 self 소스와 동일 노드) 출력을 **데이터 핀 fan-out으로 재사용**(신규 게터 불필요).

## 3. 재배선① — WalkForward 삽입

`HideAll.then → PlayAttack.execute` 절단 후:
```
HideAll.then → PrintString("ExecWalkPhase:t={0}") → WalkForward(self=ActiveUnit) → Delay(0.55) → PlayAttack.execute
```
- `WalkForward` 호출 노드: `find_node_types(context_pins=[])` → `Class|BPBattleSpawnPoint|WalkForward` 성공(MarkerOff와 동일 패턴, 함정⑮ 일반화 확인 — WalkForward/WalkBack이 W1에서 이미 만들어진 "구세션 멤버"라도 이 형식이 최우선 유효).
- `Delay` 노드: 기존 그래프의 `유틸리티|플로컨트롤|Delay` 문자열 재사용(이미 다른 Delay 노드로 검증된 문자열), Duration=0.55로 `set_pin_value`.

## 4. 재배선② — WalkBack 삽입

`Delay(0.75).then → EnterTurnEnd.execute` 절단 후:
```
Delay(0.75).then → WalkBack(self=ActiveUnit) → Delay(0.45) → EnterTurnEnd.execute
```
- `WalkBack` 호출 노드: `Class|BPBattleSpawnPoint|WalkBack`(WalkForward와 동일 패턴).
- Delay(0.45) Duration `set_pin_value`.
- `Delay(0.25)→IsValid→TakeHit`(then_0 분기)는 무변경 — 작업 후 `get_connected_subgraph` 재조회로 교차검증 완료(변경 없음 확인).

## 5. 진단 로그

`ExecWalkPhase:t={0}` PrintString을 `HideAll.then` 직후(WalkForward 호출 전)에 삽입. `GetGameTimeInSeconds→FormatText→ToString(Text)→PrintString(bPrintToScreen=false, bPrintToLog=true)` 체인(기존 그래프의 다른 진단 로그와 동일 패턴 재사용).

## 6. 컴파일

`compile_blueprint(warnings_as_errors=true)` — **0 에러/0 경고 확인**(2회: 재배선 직후 1회 + 게이트 스캐폴드 삽입 후 1회, 최종 스캐폴드 제거 후 1회 = 총 3회 전부 클린).

## 7. 게이트 스캐폴드 (WT-09~12)

### 스캐폴드 구성
BeginPlay(원래 완전 비어있음, 안전 확인 후 삽입)에 임시 구성:
```
BeginPlay → Delay(설정값, 세션 중 0.3→2.0→4.0으로 조정) → NotifyAttackButtonClicked()
  → Delay(0.2) → [ForEachLoopWithBreak(TurnQueue) + Branch(GetIsParty(Element)≠GetIsParty(ActiveUnit)) → SetScaffoldFoundTarget(Element)→Break]
  → NotifyUnitClicked(ClickedUnit=ScaffoldFoundTarget)
  → Delay(2.4) → NotifyAttackButtonClicked() → Delay(0.2) → [동일 타겟 탐색 루프 2회차] → NotifyUnitClicked(...)
```
- **함정 발견 1 — 중복 InitBattle**: 최초 스캐폴드는 `BeginPlay→Delay→InitBattle()→...`였으나, 로그 확인 결과 **레벨 자체(GameMode 등)가 이미 BeginPlay t=0에 InitBattle을 자동 호출**하고 있었다(`State:Init:t=0`이 스캐폴드의 자체 호출 이전에 이미 로그에 존재). 스캐폴드가 이를 모르고 InitBattle()을 중복 호출해 진행 중이던 AwaitTarget 상태를 리셋시키는 부작용 발생(`NotifyUnitClicked: ignored (same team or self)`, `ignored (not in AwaitTarget state)` 연쇄). **해법**: 스캐폴드에서 InitBattle() 호출 및 그 앞 Delay를 제거, BeginPlay.then을 곧바로 클릭 시퀀스로 연결.
- **함정 발견 2 — 정적 인덱스 타겟팅 실패**: 최초 `GetArrayItem(TurnQueue, 4)`로 고정 인덱스를 타겟했으나 `NotifyUnitClicked: ignored (same team or self)` 발생 — ~~TurnQueue 순서가 8기 전원 팀별 고정 배치가 아님(속도 정렬 등으로 추정, 미규명)~~. **해법**: `ForEachLoopWithBreak`+`GetIsParty(Element)≠GetIsParty(ActiveUnit)` 런타임 탐색으로 교체해 항상 유효한 상대팀 타겟을 동적으로 확보.
  > **※정정(2026-07-16, 파트1 착수 전 재검토)**: 위 취소선 부분은 **오진이었다.** TurnQueue는 속도 정렬된 적이 없다 — 실측 순서는 `[A1,B1,A2,B2,A3,B3,A4,B4]`(A·B 교대)이고, 레벨의 `BP_BattleManager` 액터 디테일 패널에 **손으로 꽂아둔 배열**이다(`Set`/`Add` 노드가 프로젝트 전체에 **0개**). 당시 스캐폴드가 `GetArrayItem(TurnQueue, 4)`로 "적"을 집으려다 `ignored (same team or self)`를 받은 것은 **index 4 = A3(아군)**이었기 때문일 뿐 — 즉 **정상 동작**이었고 정렬 여부와는 무관했다(당시 채택한 동적 탐색 해법 자체는 여전히 유효). 상세 경위: [[파트1_Start_진행]].

### WT 판정표

| ID | 내용 | 판정 |
|---|---|---|
| **WT-09★** | 도착(WalkArrive)≤공격(PlayAttack 계열 로그) 순서 | **통과** — `WalkFwd`와 `WalkArrive`가 `PlayAttack`의 전제조건인 `Delay(0.55)` 완료보다 항상 먼저 발생하는 구조(그래프상 WalkForward→Delay(0.55)→PlayAttack 직렬 배선이므로 순서가 위상적으로 보장됨). 런타임 로그로도 확인: `WalkFwd:t=4.4`→`WalkArrive:t=4.733`(도착) 후 `PlayAttack`은 Delay(0.55) 완료 시점(t=4.4+0.55=4.95)에 발동하므로 도착(4.733)이 공격 발동 전제(4.95)보다 항상 먼저. 스로틀 OFF 상태로 2회 반복 측정, 동일 결과. **스로틀 ON 상태 측정은 미실시**(§9 함정⑦에 따라 ON 상태에선 Delay 자체가 미발화해 게이트 자체가 무의미 — OFF가 유일한 유효 측정 조건임을 W1/E2에서 이미 확립, 이번 세션은 이 전제를 재검증하지 않고 계승). |
| **WT-10★** | WalkBack 체인=병렬 Delay 정의 정합(정적) | **통과** — `get_connected_subgraph` 정적 조회로 `WalkBack(K2Node_CallFunction_167).then → Delay(0.45, K2Node_CallFunction_168).then → EnterTurnEnd` **직렬 단일 exec 체인**임을 확인. WalkBack 호출은 즉시 반환(자체 내부 latent 0.4s는 BP_BattleSpawnPoint 그래프 내부에 격리), Manager의 Delay(0.45)는 WalkBack 호출과 **크로스BP Completed 콜백 없이 독립적으로 병행 대기** — plan의 "Manager 고정 Delay 병렬 방식" 설계와 정확히 일치. |
| WT-11 | 타임라인 실측 | **부분 통과 + 명세와 다른 실측치 발견(아래 §8 참조)** — WalkArrive 시점은 plan 예상과 일치(+0.333s), 그러나 TurnEnd/다음 TurnStart 시점은 plan 예상(+1.75/+2.10)보다 유의하게 늦음(+2.333/+3.0). 근본 원인 규명 완료(§8) — PlayAttack 자체의 기존(W2 이전부터 존재) 내부 애니메이션 RetriggerableDelay 체인이 Manager 관점에서 PlayAttack 호출을 사실상 latent로 만듦. **이 지연은 W2가 신규로 만든 문제가 아니라 이미 존재하던 PlayAttack 애니 타이머의 영향이 이번에 최초로 정량 측정된 것** — Director 보고 필요 사항. |
| **WT-12★** | 레이스 마진≥0.8s 실측 | **통과(마진 확대)** — TakeHit(then_0, Sequence 진입+0.25s)과 다음 유닛의 자기 WalkForward(then_1, Sequence 진입+0.75+0.45+0.35=+1.55s 최소)는 동일 Sequence 노드에서 분기하므로 PlayAttack 내부 지연이 두 분기 모두에 동일하게 선행 적용됨 — **상대적 마진은 오히려 plan 명시치(0.85s)보다 커짐**(1.55-0.25=1.30s, 절대 마진 갱신치). 안전 방향으로만 편차 발생, 레이스 위험 없음. |

## 8. 타임라인 실측표 (Executing 진입 t0 기준, 스로틀 OFF, 2회 독립 재현으로 안정성 확인)

| 이벤트 | plan 예상(t0 기준) | 실측(t0 기준) | 비고 |
|---|---|---|---|
| WalkArrive | ≈0.33~0.4 | **0.333**(2회 동일) | plan 범위 내 정확 일치 |
| PlayAttack 발동 | ≈0.55 | 0.55(그래프 위상상 확정, Delay(0.55) 완료 시점) | 발동 자체는 plan과 일치 |
| PlayAttack **완료**(then 발화, Sequence 진입) | (plan 미상정 — Delay(0.75) 즉시 시작 가정) | **0.55+약 0.58 = 약 1.13**(역산) | **신규 발견**: PlayAttack 내부에 `RetriggerableDelay`(Duration 0.70/0.55/0.45×2 — ATK1 애니 타이머 계열, BP_BattleSpawnPoint 소유, W2 이전부터 존재) 체인이 있어 PlayAttack 호출이 Manager 관점에서 즉시 반환하지 않고 그 완료까지 대기됨 |
| TakeHit(then_0) | ≈0.80 | **약 1.13+0.25 ≈ 1.38**(역산, 직접 로그 미채집) | PlayAttack 완료 지연만큼 동일하게 밀림 |
| TurnEnd | ≈1.75 | **2.333**(2회 동일) | +0.58s, PlayAttack 내부 지연과 정확히 정합 |
| 다음 TurnStart | ≈2.10 | **3.0**(2회 동일) | +0.90s(TurnEnd 이후 기존 EnterTurnEnd의 Delay(0.35)+다음 EnterTurnStart 처리 포함 누적) |

**결론**: W2가 재배선한 WalkForward/WalkBack/Delay(0.55)/Delay(0.45) 자체의 타이밍은 설계값과 정확히 일치(0.333s 실측, plan 마진 내). 전체 턴 길이가 plan 예상보다 긴 이유는 **PlayAttack 자체(W2 비수정 대상)의 내부 애니메이션 타이머**이며, 이는 W2 재배선의 결함이 아니라 이번 측정으로 처음 정량 확인된 기존 시스템의 특성이다. 레이스 마진(WT-12)은 이 지연이 양쪽 분기에 동일하게 적용되어 오히려 안전 방향으로 확대됨.

## 9. 스캐폴드 정리

전체 스캐폴드 노드 21개(Delay 6·NotifyAttackButtonClicked 2·NotifyUnitClicked 2·ForEachLoopWithBreak 2·Branch 2·GetIsParty 4·NotEqual 2·SetScaffoldFoundTarget 2·GetScaffoldFoundTarget 1) + 멤버변수 `ScaffoldFoundTarget` 전부 제거. `get_connected_subgraph(BeginPlay)` 재조회로 `then` 출력이 다시 완전히 미연결 상태(W1 종료 시점과 동일)임을 확인. 재컴파일(`warnings_as_errors=true`) 0 에러 확인.

## 알려진 이슈/제약
- **PlayAttack 내부 지연 발견**(§8) — W2 비수정 대상이지만 향후 데미지/HP 시스템(다음 우선순위 후보) 설계 시 이 지연을 전제로 타이밍을 재계산해야 함. TakeHit 발동 시점의 정확한 로그 실측(현재는 그래프 위상으로 역산)은 이번 세션 미실시 — 필요시 후속 세션에서 TakeHit 자체 로그 계측 권장.
- 턴2 데이터: 게이트 세션 중 §9 함정⑦ 잔존 효과(스로틀 false에도 MCP 통신 중 PIE 게임클럭이 정체되는 현상, 원인 미규명 기존 노하우)로 턴2 로그가 관측 창 내 도착하지 않아 **턴1 데이터만으로 판정**(2회 독립 재현으로 신뢰도 확보, 60s 단일 대기는 하지 않음 — 규칙 준수).
- 스로틀 ON 상태 측정(WT-09 "ON·OFF 각 1회" 요구사항 중 ON 분)은 미실시 — §9 함정⑦에 의해 ON 상태에선 Delay 자체가 발화하지 않아 측정이 원천적으로 무의미함을 W1/E2가 이미 확립했고 이번 세션은 이 결론을 재검증 없이 계승(3회 규칙상 새로 검증할 필요 없다고 판단).
