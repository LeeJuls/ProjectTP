---
type: design
project: projectTP
feature: 전투완성
stage: BT3
updated: 2026-08-12
status: 설계 완료(구현 0건) — 게이트 AU-B3-01~03 + 신설 3항 반영 / PM 확인 요청 4건 / 미확인 8건
---

# BT3 — MA(Method A) 상세 설계서

> ★**오프라인 전용 작성** — MCP 툴 호출 0회, uasset 무접촉, 커밋 0건. 다른 gameplay-engineer 세션(AT4-b)이 에디터를 점유 중이라 조회조차 하지 않았다.
> 대상 게이트: [[../../../자율진행_plan_v2|자율진행_plan_v2]] §3 BT트랙 표(BT3 행) + [[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] §3-3(`AU-B3-01~03`).
> **경계**: 본 문서는 설계서다. 구현은 FT1(1a/1b/1c) 착수 시 별도 세션에서 한다. 여기서 확정하지 못한 것은 "미확인"으로 남기고 실측을 요구한다.
#projectTP/전투완성

---

## 0. PM 3줄

1. **게이트 3건(`AU-B3-01`~`03`) + plan v2 신설 3항 전부 이 문서에서 충족**한다 — §7 대응표 참조. **v2와의 모순은 0건**(§8에서 4제약 대조표로 실증).
2. **F7b v2 원문 MA-1 게이트("재생 원장 ↔ 오너 수동 원장 diff 0")는 plan v2가 이미 상위 문서에서 2축(`MA-1a`/`MA-1b`)으로 대체했다** — 이건 모순이 아니라 **문서 갱신 시차**다. `F7b_재개계획_초안.md`의 MA-1 한 줄이 아직 구판이므로 **PM이 그 파일도 동기화할 것을 권고**한다(§9-1).
3. **"타겟 명시 주입"(신설 3항 중 3번째)의 근거 문구는 자율진행_TC/plan v2 어디에도 없고 [[턴예산_balance판정_2026-08-12]] R-4 조건(ii)에서 나왔다** — balance가 판 근거를 그대로 계승해 설계했다(§6). qa의 "MA-1c 무감각 고지"·"오라클 §9 R5"와 범위가 다르므로 혼동 방지 표를 넣었다(§6-3).

---

## 1. MA란 무엇인가 — 정의 확정

**MA = Method A = 자동 시나리오 훅.** 클릭 기반 전투를 오너 대신 자동 재생하는 **검증 전용 스캐폴드**다. 근거 3개가 일치한다:

- [[F7b_재개계획_초안]] `[MA] Method A 자동 시나리오` 청크 — "정식 청크로 편입(자체 게이트·세이브포인트)"
- [[../../../자율진행_plan_v2|자율진행_plan_v2]] §2-(가) — "**FT1 = MA 훅(1a) + 자동 시작 토글(1b) + SCF 호출기(1c)**. 셋 다 `BP_BattleManager` 계열 additive 스캐폴드"
- [[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] §7-2 — MA는 "원장을 만들지 않는다 — **입력을 만든다**. 원장은 라이브 BP의 출력이다"

★**MA ≠ FT1 전체다.** FT1(plan v2가 부르는 "검증 하네스")은 MA를 포함해 **3개 구성요소**로 이뤄진다. 본 문서는 게이트 명칭과의 혼동을 피하려고 아래 표기를 쓴다(§7-2에서 상세):

| 표기 | 정체 | 근거 |
|---|---|---|
| **FT1-1a** | MA 훅 — `EnterAwaitCommand`/`EnterAwaitTarget` 말단 → `NotifySkillSelected`/`NotifyUnitClicked` 자동 호출 | F7b v2 [MA] |
| **FT1-1b** | 자동 시작 토글 — `BeginPlay`에서 `StartBattle` 자동 발화(함정99 우회) | plan v2 §2-(가) |
| **FT1-1c** | SCF 호출기 — `ApplyEffectEntry`/`EvaluateCondition` 등 임의 인자 관통 디버그 훅 | plan v2 §2-(가) · qa AU-B3-03 |

★**주의 — 이 "FT1-1a/1b/1c" 표기는 본 문서의 편의 표기이지 원문에 확정된 ID가 아니다.** [[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]](로그 스캐폴드 3종, LOG-A 계열)가 같은 접두어로 "FT1-1a~1c의 착수 조건 = FT1-0 PASS"라고 이미 쓰고 있어(§로그 스캐폴드는 이 셋과 다른 대상 — `SessionBoundary|`/`PlayAttack|`/`SkillSelected|`) **우연히 정합**하지만, plan v2 원문은 이 셋에 정식 ID를 아직 부여하지 않았다(그냥 "1a"/"1b"/"1c"로만 부른다). §9-2에서 PM 확인을 요청한다.

---

## 2. 현재 상태(오프라인 조사로 확정 가능한 범위)

| 항목 | 실측 근거 | 확정 여부 |
|---|---|---|
| `EnterAwaitCommand`/`EnterAwaitTarget`은 Function Graph다 | F7b v2 [MA] "gameplay 실측" 인용(원 실측 세션 문서는 본 조사 범위 밖) | ★**F7b v2 문서를 근거로 승계** — 본 세션 재실측 안 함(MCP 금지) |
| `NotifySkillSelected`/`NotifyAttackButtonClicked`는 무인자 커스텀 함수 | [[전진로직_실체_확정]] §7 핀 원문(`execute`+`self` 2핀뿐) | ✅ 확정(2026-08-12 조회) |
| `NotifySkillSelected`의 SELF 스킵 분기 | [[전투BP_현황도_2026-08-11]] §상태표 4행 — "SELF면 `SelectedTargets=[Caster]` 즉시 세팅 후 AwaitTarget 스킵 → Executing 직행" | ✅ 확정 |
| `NotifyUnitClicked`의 유효성 가드 | 〃 §상태표 6행 — "`BattleState==3` 가드 + `ResolveTargetPool` 결과 포함 여부(`ContainsItem`) 확인" | ✅ 확정 |
| `PlayAttack`은 턴 흐름을 블로킹하지 않는다(H18 부정) | [[턴길이_실측확정_2026-08-12]] — 60fps 4회 전부 `1.750`=`0.55+0.75+0.45` | ✅ 확정(간접 — 턴길이 산술로 증명, `PlayAttack` 자체의 enter/exit 로그는 아직 없음) |
| `PlayAttack`이 Function Graph인가 EventGraph 커스텀 이벤트인가, 내부 latent 유무 | [[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] `AU-F0p-03` | ❌ **미확인 — 상태 `대기`.** MA 설계에는 영향 없음(§3-3에서 이유 설명) |
| `EnterAwaitCommand`/`EnterAwaitTarget`의 실제 핀 원문(정확한 노드 refPath) | — | ❌ **미확인.** 이번 조사 범위(전진로직_실체_확정)는 `EnterExecuting` 계열만 조회했다. FT1-1a 구현 착수 전 MCP 조회 1회 필요(§9-3) |

---

## 3. 신설 1 — MA `Delay` 노드 0 명문화

### 3-1. 규약

> **MA 그래프(FT1-1a 훅과 그것이 호출하는 EventGraph 커스텀 이벤트) 내부에 `Delay`/`RetriggerableDelay`/`Timeline` 등 latent 스케줄링 노드를 두지 않는다.**

### 3-2. 근거 — 이중 근거(엔진 제약 + 설계 제약)

| 근거 | 내용 | 강도 |
|---|---|---|
| **엔진 제약** | `EnterAwaitCommand`/`EnterAwaitTarget`은 **Function Graph**라 애초에 latent 노드를 넣을 수 없다(컴파일 거부) — F7b v2 constraint ① | 하드(우회 불가) |
| **설계 제약** | plan v2 반박#2 판정: qa Critical 2(*"(b)는 MA-1을 깬다"*)는 원 근거(원장 8열에 시간 열 없음)가 성립하지 않아 **부분수용**됐지만, balance가 단 조건 — *"MA가 Delay 스케줄링을 쓰면 그때는 (b′)가 MA-1을 깬다"* — 은 **잔존 진실**로 인정됐다. 그래서 plan v2가 직접 "BT3에 'MA 그래프 내 Delay 노드 0개' 명문화"를 지시했다 | 설계 결정(BT3 본 절이 그 명문화) |

즉 EventGraph로 우회하면 기술적으로는 Delay를 넣을 수 있게 되지만(F7b v2가 "타이밍 필요 시 EventGraph 신규 커스텀 이벤트 경유"라고 우회로를 열어뒀다), **그 우회로에도 Delay를 넣지 않는다**는 것이 이 규약의 핵심이다.

### 3-3. 왜 Delay가 MA-1을 깨는가 (설계 추론 — plan v2가 결론만 주고 이유는 안 적었다)

MA 훅은 "폴링/대기"가 아니라 **"콜백"**이어야 한다. `EnterAwaitCommand`/`EnterAwaitTarget`이 실행되는 **바로 그 시점**에 훅이 함께 발화하도록 말단에 심으므로(§4), MA는 애초에 "기다릴 이유가 없다" — 상태가 준비된 순간 즉시 다음 클릭을 흉내낸다. 여기 Delay를 넣으면:

1. **MA-1b(경로 동치)가 깨진다** — 상태 전이 토큰 시퀀스(`State:AwaitCommand→AwaitTarget→…`)의 **타이밍**이 오너 수동 클릭과 달라진다. 오너는 반응 시간만큼 대기하지만 그 대기가 상태 사이에 다른 이벤트를 끼워넣지는 않는다. MA가 Delay로 대기하면 그 사이 다른 유닛의 턴 진행·타임아웃 로직과 **레이스**가 생길 수 있다(현재 그런 로직이 있는지는 미확인 — §9-4).
2. **PlayAttack의 `RetriggerableDelay`와 상호작용 위험** — [[BP정리_통합명세_2026-08-11]] L267이 `PlayAttack` 내부에 `RetriggerableDelay`가 있다고 기록했다(단 그 값이 턴을 블로킹한다는 해석은 이미 부정됨, §2). `RetriggerableDelay`는 **재진입 시 타이머를 리셋**한다([[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] §3-B High 2). MA가 자체 Delay로 다음 액션을 서두르거나 늦추면, 이미 존재하는 latent 타이머와 **의도치 않게 겹쳐 재트리거**될 위험이 있다.
3. **오라클(1)은 시간 열이 없다(§7-2)** — 그래서 원장 결과 자체(dmg/hp/died)는 Delay 유무와 무관하게 안 깨진다는 것이 balance의 원래 반박이었다. 다만 **MA-1b가 신설되면서** "시간 열 없음"이라는 방어가 더 이상 충분하지 않다 — 경로 동치는 **토큰 순서와 무관하게 값만 보는 게 아니라 시퀀스 자체를 비교**하기 때문이다.

### 3-4. 적용 범위 경계 — FT1-1b(자동 시작 토글)는 예외다

★**이 규약은 FT1-1b에는 적용되지 않는다.** 노하우 §6(1049행 인근, "MCP엔 PIE 콘솔 명령 주입 수단 없음 → 임시 스캐폴드(`BeginPlay`+`Delay`→이벤트 호출) 심고 검증 후 제거가 정석")가 권고하는 표준 패턴은 정확히 `BeginPlay`+`Delay`다. FT1-1b는:

- **MA 그래프가 아니다** — 턴별 의사결정 루프 밖에 있는 **1회성 부트스트랩**(전투 시작 전 단 1회 발화)이다.
- 전투가 실제로 시작된 뒤(=턴 루프 진입 후)에는 다시 발화하지 않으므로 SlotBudgetSec·턴 길이 측정에 영향이 없다.

→ **경계선 한 문장**: *"MA 훅(FT1-1a)과 그 EventGraph 콜백에는 Delay 0개. 전투 시작 전 1회성 부트스트랩(FT1-1b)에는 Delay 허용."* 이 구분을 명문화하지 않으면 다음 사람이 (a) 1b도 금지 대상으로 오인해 함정99 우회 수단을 잃거나, (b) 반대로 1a에도 몰래 Delay를 넣어 MA-1b를 무음으로 깬다.

---

## 4. 신설 2 — FT1 스캐폴드 명세 (무엇을 세우고 무엇을 검증하는가)

### 4-1. FT1-1a — MA 훅

**목적**: 클릭 기반 20 유닛턴 even-trade 런을 오너 대신 자동 재생해 오라클과 대조하는 도구를 만든다.

**배선(설계, 미실측 — 착수 전 MCP 조회 1회 필요, §9-3)**:

```
EnterAwaitCommand (Function Graph, 기존 로직 종단 이후)
  └ 말단에 추가: IsValid(bAutoScenarioActive)? → true → CustomEvent_MA_OnAwaitCommand 호출(즉시, latent 아님)

EnterAwaitTarget (Function Graph, 기존 로직 종단 이후)
  └ 말단에 추가: IsValid(bAutoScenarioActive)? → true → CustomEvent_MA_OnAwaitTarget 호출(즉시, latent 아님)
```

- 두 커스텀 이벤트(`CustomEvent_MA_OnAwaitCommand`/`CustomEvent_MA_OnAwaitTarget`)는 **EventGraph에 신설**한다(F7b v2 constraint ①의 우회로).
- ★**"커스텀 이벤트 호출" 자체는 latent가 아니다** — 이벤트 디스패치는 즉시 실행되는 일반 exec 호출이라 Function Graph에서도 허용된다. latent가 금지되는 것은 그 **이벤트 본문 안에서 Delay 등을 쓰는 것**이다(§3).
- `CustomEvent_MA_OnAwaitCommand` 내부: `bAutoScenarioActive` 재확인(이중 게이트) → 시나리오 리졸버로 다음 `SkillId` 결정 → `NotifySkillSelected(SkillId)` 즉시 호출.
- `CustomEvent_MA_OnAwaitTarget` 내부: 시나리오 리졸버로 다음 `TargetSlotId` 결정 → 런타임 리졸버(`ResolveSlotToActor`류, §6)로 액터 해석 → `NotifyUnitClicked(Actor)` 즉시 호출.

**SELF 스킵 처리(F7b v2 constraint ④, "선행 트레이스")**: `NotifySkillSelected` 내부에서 `Target=="SELF"`면 `SelectedTargets=[Caster]`를 즉시 세팅하고 **`EnterAwaitTarget`을 아예 호출하지 않는다**([[전투BP_현황도_2026-08-11]] §상태표 4행). 즉 SELF 스킬 턴에서는 `CustomEvent_MA_OnAwaitTarget`이 **발화하지 않는 것이 정상**이다. 시나리오 리졸버가 SELF 스킬의 `TargetSlotId`를 준비해도 소비되지 않으므로, MA-1b(경로 동치) 토큰 시퀀스에도 `AwaitTarget` 상태가 **등장하지 않아야** 정상이다. 이 케이스를 놓치면 "MA가 타겟 훅을 안 태웠다"를 결함으로 오판할 위험이 있다.

**게이트(§7-2 2축 분해, AU-B3-02 반영 — §5 참조)**:
- **MA-1a 결과 동치**: MA 재생 20행 ↔ [[SPD원장_오라클_v1]] §7 diff 0 (오너 비용 0)
- **MA-1b 경로 동치**: MA 1 유닛턴 상태 전이 토큰 시퀀스 ↔ 오너 수동 1 유닛턴 시퀀스, 토큰 단위 동일 (오너 비용 1턴)
- **MA-1c 무감각 고지**: `attacker`/`target` 열은 판정력 없음을 산출물에 명기
- **MA-2 무접촉 증명**: `EnterExecuting`·`ResolveHit` 노드 수 **완전 무변**(MA는 이 두 함수를 절대 건드리지 않는다). ⚠**"EventGraph 노드수 무변"의 자기모순 발견 — §4-4 참조**
- **MA-3 회귀 무변**: `bAutoScenarioActive=false`에서 수동 클릭 경로 무회귀 — 5스킬 회귀(기본 30·베기 42+STUN·파볼 61+ATK_DOWN·막기 15·치유 −33) PASS

### 4-2. FT1-1b — 자동 시작 토글

**목적**: 함정(99) 우회 — 에이전트 PIE는 "Start" 버튼 클릭 1회를 만들 수 없어 전투가 0턴 진행된다(노하우 §41). `BeginPlay`에서 배틀을 자동 시작시켜 이후 상태머신이 스스로 진행되게 한다("막힌 지점은 정확히 1개"라는 실측이 이 훅의 투자 근거).

**배선(설계)**:

```
ReceiveBeginPlay (BP_BattleManager, 기존 로직 종단 이후 — carve-out, splice 아님)
  └ 말단에 추가: IsValid(bAutoStartBattle)? → true → Delay(0.1) → StartBattle() 호출
```

- `bAutoStartBattle` 기본값 **false**, Instance Editable(FT1-1a의 `bAutoScenarioActive`와 동일한 스캐폴드 관례).
- `Delay(0.1)`는 초기화 레이스 방지용 여유(다른 액터의 `BeginPlay`가 끝나기를 기다림 — [[전투BP_현황도_2026-08-11]]는 `BP_BattleSpawnPoint`도 `BeginPlay`에서 `DT_JobStats` 조회를 한다고 기록했다. 순서 보장이 없으므로 소액의 지연이 안전하다).
- ★**`StartBattle()`을 직접 호출하는 것을 권고**한다 — `NotifyAttackButtonClicked`도 대안이 될 수 있으나([[전진로직_실체_확정]] §7이 확인한 대로 `BattleState==0`이면 그 함수가 `StartBattle`을 호출한다) 그 함수는 **Start/Cancel/End 겸 4역할**을 `BattleState`/`bInputLocked` 값으로 구분하는 다의적 함수라, 자동시작 훅이 실수로 다른 역할을 트리거할 여지가 있다(예: 재진입 시 `BattleState==6`이면 `InitBattle` 재초기화). `StartBattle()` 직접 호출이 모호성을 없앤다.
- **게이트**: 토글 off에서 수동 흐름 무회귀 / on일 때 `BeginPlay` 이후 정확히 1회 `StartBattle` 발화.
- ⚠ **미확인**: `StartBattle()`이 이미 진행 중인 배틀에서 재호출됐을 때 스스로 재진입 가드를 갖는지 — 미확인이면 자동시작 토글이 PIE 1회에 전투를 2번 시작시킬 수 있다([[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] §3-B Medium 항목 "sid 단위=PIE 세션인데 원장 단위는 전투"와 같은 계열 위험). §9-4에서 PM 확인 요청.

### 4-3. FT1-1c — SCF 호출기

**목적**: `AU-B3-03`이 지목한 문제 — `ApplyEffectEntry`/`EvaluateCondition`을 **비기본값**(`coeff≠1.0` 등)으로 관통시켜 검증할 실행 수단이 없다. MA(`NotifySkillSelected`/`NotifyUnitClicked`)는 UI 클릭을 흉내낼 뿐 **임의 함수 호출기가 아니다**. 노하우 §6: "MCP엔 PIE 콘솔 명령 주입 수단 없음 → 임시 스캐폴드가 정석."

**배선(설계)**: BP는 문자열로 함수를 동적 디스패치하는 범용 리플렉션 호출기를 그래프로 만들기 어렵다. 따라서 **검증 대상 함수마다 전용 디버그 커스텀 이벤트를 1개씩** 둔다(제네릭 디스패처 1개가 아니라 함수별 스텁 N개).

```
예) Debug_SCF_ApplyEffectEntry(Attacker, Target, EffectRow, CoeffOverride)
      └ 내부에서 ApplyEffectEntry(Attacker, Target, EffectRow, CoeffOverride) 직접 호출

예) Debug_SCF_EvaluateCondition(Caster, Target, ConditionRow)
      └ 내부에서 EvaluateCondition(...) 직접 호출, ReturnValue를 PrintString/BattleLog로 방출
```

- 트리거는 FT1-1b와 같은 패턴(`bDebugSCFEnabled` 기본 false + `BeginPlay`+`Delay`→해당 이벤트 1회 호출) — **이 Delay도 §3-4 예외 범위**(전투 판정 루프 밖 1회성 디버그 트리거)이므로 "MA Delay 0" 규약 위반이 아니다.
- **인자 주입 방식**: 자동 파라미터 스윕이 아니라 **리터럴 1회 값 주입**이다. 케이스마다(예: `coeff=0.75`) 리터럴을 MCP `set_pin_value`로 바꾸고 재컴파일·재실행한다. 이는 additive 범위 안(핀 값 변경, exec 절단 0).
- **게이트**: `FT2` `AU-F2-02`(SCF 회귀 — 베기 STUN·파볼 ATK_DOWN×0.75 불변), `FT4` `AU-F4-03`(FAKEGREEN — `coeff≠1.0` 주입 시 `dmg`가 `floor(Atk×coeff)−Def`로 실제로 변하는지, 1.0 폴백 은폐 방지).
- **처분**: 노하우 §6 원칙대로 "검증 후 제거"가 기본이나, FT1 4제약(§7 자율 경계, `Instance Editable bool 기본 false`)이 이미 라이브 경로 무영향을 보장하므로 **⑩b(스캐폴드 처분)에서 최종 판정**한다(F7b v2 §⑩b — "Method A·MOCK은 A2 회귀 스위트가 재사용" 계승).

### 4-4. ★발견한 내부 모순(1건) — "MA-2 EventGraph 노드수 무변"의 문언

F7b v2 원문: *"MA-2 `EnterExecuting`·`ResolveHit`·`EventGraph` 노드수 무변(무접촉 증명)"*.

문자 그대로 읽으면 **`EventGraph` 전체 노드수가 0 diff**여야 한다. 그런데 같은 문서의 constraint ①이 *"타이밍 필요 시 EventGraph 신규 커스텀 이벤트 경유"*라고 **신설을 명시적으로 허용**한다 — FT1-1a 자체가 EventGraph에 커스텀 이벤트 2개(+호출 노드)를 반드시 추가해야 하므로, "EventGraph 노드수 완전 무변"은 **자기모순**이다.

**본 설계서의 해석(권고, PM/qa 확인 요청 — §9-1)**: MA-2를 다음으로 재정의한다 —
- `EnterExecuting`/`ResolveHit` 함수: **완전 무변**(0 diff) — 원문 그대로 유지, MA는 이 둘을 절대 안 건드린다.
- `EnterAwaitCommand`/`EnterAwaitTarget` 함수: 말단에 **정확히 1개 노드**(이벤트 호출) 추가, 기존 노드 0개 변형.
- EventGraph: **MA 신설분(`CustomEvent_MA_OnAwaitCommand`/`OnAwaitTarget` 및 그 내부 노드)을 제외한 기존 노드는 diff 0**.

이 해석이 맞는지는 **qa-critic 또는 PM 확인이 필요**하다 — 원문을 임의로 고쳐 쓰지 않고 해석만 제안한다.

---

## 5. 신설 3-대응 — MA-1 게이트 2축 분해 반영 (`AU-B3-02`)

`AU-B3-02` 요구: *"설계서에 §7-2의 2축 분해(MA-1a 결과동치 / MA-1b 경로동치)와 무감각 열이 반영됨. 미반영이면 FT1이 동어반복 게이트로 착수된다."*

★**반영 완료 — §4-1 "게이트" 절**. 추가로 [[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] §7-2의 핵심 논증을 그대로 승계한다:

| 산출물 | 생산 주체 | MA와의 독립성 | 본 설계서에서의 역할 |
|---|---|---|---|
| (1) [[SPD원장_오라클_v1]] §7 20행 | 손계산(balance, BP 미접근·blind 선언) | ★**완전 독립** | **MA-1a의 대조군** |
| (2) 오너 수동 런 파싱 CSV | 사람 클릭 → 라이브 BP 출력 | 독립 | **MA-1b의 대조군**(F7b v2 원문 MA-1이 원래 요구하던 것) |
| (3) MA 재생 파싱 CSV | MA 주입 → 라이브 BP 출력 | — | 이 문서가 설계하는 도구의 출력 |

★**BT5 (b)안 기각과의 연동 — 동어반복 방지선**: [[BT5_S1봉인수단_판별]]에서 이미 (b)안(*"MA 선구축으로 S1 봉인 대체"*)이 기각되고 (c)안(오너 직접 20턴 런)이 확정됐다. 이건 §7-2 판정3의 우려(*"(b)를 택하면 (3) vs (3) = 항등이 되어 어떤 버그도 검출 못 한다"*)를 원천 차단한 것과 같다 — **(1) 오라클은 여전히 MA와 완전 독립인 대조군으로 남는다.** 본 설계서는 이 전제(BT5 (b) 기각 확정) 위에 서 있다.

**MA-1b가 잡는 것 — (3) vs (1)이 못 잡는 실패 모드**: MA가 상태 진입 자체를 우회해 같은 결과를 만드는 경우(`EnterAwaitCommand`/`EnterAwaitTarget`을 실제로 거치지 않고 `NotifySkillSelected`/`NotifyUnitClicked`를 직접 호출하는 게 MA 설계 자체이므로, 원리적으로 "우회"가 내재해 있다 — 그래서 §4-1의 훅 위치가 함수 **말단**이어야 한다: 기존 로직이 전부 실행된 **후**에 훅이 발화해야 "상태 진입을 스킵"하는 게 아니라 "상태 진입 직후 입력을 흉내"내는 것이 된다).

---

## 6. 신설 3 — 타겟 명시 주입

### 6-1. 출처 확정

★★**이 문구의 정확한 출처를 확정한다** — plan v2·자율진행_TC 어디에도 "타겟 명시 주입"이라는 문자열이 없다(전수 grep 확인). 유일한 출처는 [[턴예산_balance판정_2026-08-12]] **R-4**(Medium):

> *"MA-1 순환성은 qa 대기 없이 지금 닫힌다. 오라클이 §0.5에서 '게임 BP 미접근·손계산'을 선언 → 도구 독립. MA는 **입력만 주입**하고 출력은 게임이 생산 → 순환 아님. **단 조건 2개**: (i) S1 런을 MA로 생산 금지 → B5 (b)안 기각 권고 (ii) **타겟은 오라클 대상 열 명시 주입**(게임 자동 타겟팅 위임 시 '게임이 게임을 채점')"*

즉 이 신설 3항은 **balance-designer의 순환성 방어 조건 (ii)**를 BT3 설계 규약으로 승격한 것이다. plan v2 발주자(PM)가 이걸 알고 신설 3항에 넣었을 개연성이 높으나, 원문 인용 없이 축약됐다 — 이 계보를 밝혀두지 않으면 다음 사람이 "왜 이 규칙이 있는가"를 못 찾는다.

### 6-2. 규약

> **`CustomEvent_MA_OnAwaitTarget`은 `ResolveTargetPool`이 계산한 유효 타겟 풀 중 아무거나 고르지 않는다. 시나리오 데이터가 지정한 `TargetSlotId`를 런타임 리졸버(`ResolveSlotToActor`류)로 액터화해 `NotifyUnitClicked`에 그 정확한 액터를 넘긴다.**

**왜 필요한가**: 만약 MA가 타겟 선택을 게임의 자동 타겟팅(`ResolveTargetPool`이 반환한 풀의 첫 번째/무작위 등)에 위임하면, "그 타겟팅이 맞는가"라는 질문에 **게임 스스로가 답을 채점하는 순환**이 생긴다. 오라클(1)은 `target` 열도 이미 갖고 있으므로(§0에서 blind 선언 시점에 라이브 실측을 고정입력으로 채택 — [[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] §7-2 "추가 발견"), MA는 그 값을 **그대로 주입**해야 대조군(1)과의 독립성이 유지된다.

### 6-3. 이 규약이 닫지 "않는" 것 — 오라클 §9 R5와의 경계선 (혼동 방지)

★**"타겟 명시 주입"은 R5(자동 타겟팅 정확성 검증)를 닫지 않는다.** 둘은 다른 축이다:

| 축 | 질문 | MA-1a/1b가 답하는가 |
|---|---|---|
| **타겟 명시 주입(본 절)** | MA가 **원하는 타겟을 정확히 재현**하는가 | ✅ 예 — 이게 이 규약의 목적 |
| **오라클 §9 R5** | `ResolveTargetPool`의 **자동 선택 규칙**(최저 슬롯 등)이 옳은가 | ❌ **아니오** — MA-1a/1b는 타겟을 입력으로 주므로 자동 선택 로직 자체를 통과하지 않는다 |

[[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] `AU-F1-04`가 이미 이 갭을 인지하고 **별도 이월**했다(*"타겟 자동 지정 모드로 1판 → target 열이 오라클과 일치하는지 확인. 자동 지정 모드가 없으면 미검증 축으로 명시 이월"*). plan v2 미해결 8건 #6도 동일 — *"오라클 R5는 S1로도 MA-1로도 구조적으로 안 닫힌다 — 명시 이월"*. ★**본 설계서는 이 이월 상태를 유지한다** — R5를 닫는 설계(가칭 "자동 지정 모드")는 **BT3 범위 밖**이다(범위 확대 금지 지시 준수). 필요해지면 별도 스캐폴드(`bAutoTargetingProbe` 등, MA-1a/1b와 독립된 토글)로 분리해야 한다 — R-4 조건 (i)/(ii)를 지키는 MA 본체와 섞으면 순환성 방어가 다시 깨진다.

### 6-4. fail-silent 위험 — 설계서에 명시

`NotifyUnitClicked`의 가드(§2)는 `ResolveTargetPool` 결과에 클릭 유닛이 **포함되지 않으면 클릭을 조용히 무시**한다(`ContainsItem` 확인, 실패 시 `SelectedTargets` 갱신 없음 — [[전투BP_현황도_2026-08-11]] §상태표 6행). 시나리오 데이터의 `TargetSlotId`가 실제 유효 풀과 어긋나면(예: 이미 죽은 유닛을 지정) MA의 클릭이 **씹히고 아무 에러도 안 난다**.

**권고**: `CustomEvent_MA_OnAwaitTarget`에 `NotifyUnitClicked` 호출 직후 **사후 검증**을 추가한다 — `SelectedTargets`가 기대한 슬롯을 가리키는지 확인하고, 어긋나면 `PrintString`(fail-loud 카테고리, [[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] §3-B "ERROR 카테고리 신설" 권고와 결이 같다)으로 즉시 경고한다. 이 검증 자체는 데이터 핀 비교이지 latent가 아니므로 §3 규약과 충돌하지 않는다.

---

## 7. 게이트 대응표 — 어디서 충족되는가

| 게이트 | 요구 | 충족 위치 | 판정 |
|---|---|---|---|
| **`AU-B3-01`** | F7b v2 [MA] 절과 대조, 모순 0 ∧ 4제약 반영 | §1(정의)·§4-1(배선)·§8(4제약 대조표) | ✅ 반영, 모순 0 |
| **`AU-B3-02`** | MA-1 2축 분해(`MA-1a`/`MA-1b`) + 무감각 열(`MA-1c`) 반영 | §4-1 "게이트" 절·§5 | ✅ 반영 |
| **`AU-B3-03`** | SCF 실행 수단 명시(`ApplyEffectEntry`·`EvaluateCondition` 임의 인자 관통) | §4-3(FT1-1c) | ✅ 반영 |
| **신설① MA Delay 노드 0 명문화** | 규약 + 근거 | §3 | ✅ |
| **신설② FT1 스캐폴드 명세** | 무엇을 세우고 무엇을 검증하는가 | §4 전체 | ✅ |
| **신설③ 타겟 명시 주입** | 암묵 참조 금지, 명시 주입 | §6 | ✅ |

---

## 8. v2 4제약 대조표 (`AU-B3-01` 실증)

| # | F7b v2 원문(요약) | 본 설계서 반영 위치 | 모순 |
|---|---|---|---|
| ① | `EnterAwaitCommand`/`EnterAwaitTarget`은 Function Graph, latent 불가 → EventGraph 신규 커스텀 이벤트 경유 | §4-1 배선도, §3(Delay 0 규약이 이 우회로에도 적용됨을 명문화) | 0 |
| ② | `bAutoScenarioActive` 기본 false + Instance Editable | §4-1 (`bAutoScenarioActive`), §4-2(`bAutoStartBattle`도 동일 패턴 계승), §4-3(`bDebugSCFEnabled`도 동일) | 0 |
| ③ | 시나리오 데이터 = 슬롯ID/CharName + 런타임 리졸버(하드코딩 금지) | §4-1, §6-2(`ResolveSlotToActor`) | 0 |
| ④ | `NotifySkillSelected`의 SELF 스킵 조건 선행 트레이스 | §4-1 "SELF 스킵 처리" 절 — [[전투BP_현황도_2026-08-11]] 실측으로 트레이스 완료 | 0 |

★**모순 0건 확인.** 단 §4-4에서 별도 문서(F7b v2) **내부**의 자기모순 1건(MA-2 문언)을 발견해 별항으로 분리했다 — 이건 "v2 대비 본 설계서의 모순"이 아니라 "v2 원문 자체의 표현 문제"이므로 §7 대응표의 PASS 판정에 영향 없음.

---

## 9-0. ★PM 판정 (2026-08-12) — 아래 §9 요청 4건 처분

| # | 요청 | 판정 |
|---|---|---|
| 1 | MA-2 문언 재정의(§4-4) | ★**승인 + 조건 1개**(아래) |
| 2 | `FT1-1a/1b/1c` 표기 정식 채택 | ★**채택** — 충돌 아니다 |
| 3 | FT1-1a 착수 전 조회 세션 발주 | **별도 발주 불요** — AT트랙 세션에 편승 |
| 4 | `F7b_재개계획_초안.md` 동기화 | ★**즉시 실행함**(같은 한 줄에 MA-1·MA-2가 둘 다 있었다) |

### ★1 — MA-2 재정의 승인, 단 화이트리스트를 사전 고정한다

원문이 **자기모순**인 것이 맞다: *"`EventGraph` 노드수 무변"*을 문자 그대로 지키면 **MA 훅 자체가 불가능**한데 같은 문서가 EventGraph 경유를 허용한다. 문언이 자기모순이면 **취지로 돌아가는 것이 표준**이고, 취지는 *"기존 로직 무접촉"*이다. §4-4의 3층 해석이 그 취지를 보존하면서 실행 가능하게 만든다 — 오히려 **원문보다 엄격하다**(*"말단에 정확히 1노드, 기존 노드 0개 변형"*).

★**조건**: *"MA 신설분 제외"*만으로는 **"신설분"의 범위를 사후에 넓힐 수 있어** 게이트가 무력해진다.
→ **FT1-1a 착수 전에 신설 노드의 이름과 개수를 문서에 못 박고**, 게이트는 **그 화이트리스트 외 diff 0**으로 판정한다. AT6-b의 Holy 임포트 화이트리스트(t0 커밋 → 결과 집합 완전일치)와 같은 패턴이다.

**director를 부르지 않은 이유**: 대안 해석이 없다(문자 그대로면 MA가 성립 불가). 막힌 문제가 아니라 문언 결함이라 PM 판정 범위로 본다. ★단 **FT1 착수 시 qa 검토 항목에 포함**한다 — 게이트 판정력을 건드리는 재정의이므로 적대 검토를 한 번은 받아야 한다.

### 2 — 표기 채택 (충돌 아님)

`FT1-0*`(로그 스캐폴드) / `FT1-1*`(MA)은 **뒤 숫자가 다르다.** *"우연히 정합"*이 아니라 체계적이다. 과거 AT/BT/FT 트랙 개명은 **같은 기호가 3개 축에서 충돌**했던 경우이고, 이건 해당하지 않는다.

### 3 — 조회 세션은 편승

`EnterAwaitCommand`/`EnterAwaitTarget` 핀 원문 조회는 **조회 전용**이라 라이브 무접촉이다. AT5 또는 AT6-a **세션 말미에 편승**시킨다(FT1-0 프로브 `AU-F0p-*`와 같은 방식). MCP 세션을 하나 더 여는 것은 낭비다.

---

## 9. PM 확인 요청

### 9-1. MA-2 "EventGraph 노드수 무변" 문언 재정의 승인

§4-4에서 제안한 해석(MA 신설분 제외 diff 0)이 맞는지 PM 또는 qa-critic 확인 필요. 틀리면 FT1-1a 착수 시 게이트 판정 기준이 흔들린다.

### 9-2. "FT1-1a/1b/1c" 표기 채택 여부

본 문서가 편의상 도입한 표기다. `FT1-0_TC.md`가 이미 "FT1-1a~1c"를 다른 맥락(LOG-A 로그 스캐폴드의 하류 참조)에서 쓰고 있어 **우연히 정합**하지만, plan v2 원문은 정식 ID를 아직 안 줬다. PM이 이 표기를 정식 채택할지, 다른 ID 체계(예: `AU-F1-1a` 등 qa 네이밍 규칙)로 통일할지 결정 필요.

### 9-3. FT1-1a 착수 전 MCP 조회 1회 필요

`EnterAwaitCommand`/`EnterAwaitTarget`의 실제 핀 원문(정확한 노드 refPath, exec 종단 형태)이 이번 조사 범위 밖이다([[전진로직_실체_확정]]은 `EnterExecuting` 계열만 조회). 배선 설계(§4-1)는 F7b v2의 서술을 승계했을 뿐 핀 단위로 재확인하지 않았다. **FT1-1a 실제 구현 착수 전 조회 세션 1회**(AT트랙과 배타 세션 공유 가능) 필요 — [[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] §9-5 후속 조사 발주안과 같은 방식(조회 전용, 수정 0건)으로 발주 권고.

### 9-4. `StartBattle()` 재진입 가드 여부

§4-2에서 미확인으로 남긴 항목. `StartBattle()`이 이미 진행 중인 배틀에서 재호출됐을 때 자체 가드가 있는지 확인 필요 — 없으면 FT1-1b 설계에 재진입 방지 조건(`BattleState==0` 사전 체크 등)을 명시적으로 추가해야 한다.

---

## 10. 미확인 목록(전수)

| # | 무엇 | 왜 미확인인가 | 닫는 방법 |
|---|---|---|---|
| 1 | `EnterAwaitCommand`/`EnterAwaitTarget` 핀 원문 | 본 조사 범위 밖(오프라인 제약) | §9-3 조회 세션 |
| 2 | `PlayAttack`이 Function Graph인가 EventGraph인가, 내부 latent 유무 | [[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] `AU-F0p-03` 상태 `대기` | FT1-0 트랙에서 별도로 닫힘 예정(MA 설계에는 영향 없음, §2) |
| 3 | `StartBattle()` 재진입 가드 | 미조회 | §9-4 |
| 4 | MA-2 "EventGraph 노드수 무변" 문언의 정확한 원 의도 | 원문 작성자(director) 의도 미확인, 본 문서는 해석만 제안 | §9-1 PM/qa 확인 |
| 5 | `bLogStage`/`bLogFlow` 등 [[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] 로그 카테고리 4bool이 MA-1b의 상태 전이 토큰(`State:AwaitCommand→…`)을 이미 커버하는지 | FT1-0(LOG-A) 트랙과 FT1-1(MA) 트랙의 교차점이 이번 조사 범위 밖 | FT1-1a 착수 전 FT1-0 진행 상태 확인 필요 |
| 6 | 시나리오 데이터(슬롯ID/CharName 시퀀스)를 어느 자산에 담을지(DataTable? 배열 변수? CSV?) | plan v2/F7b v2 모두 "런타임 리졸버"만 요구하고 저장 형식은 미지정 | FT1-1a 구현 착수 시 결정(설계 범위 밖으로 판단 — 세부 구현 선택) |
| 7 | `ResolveSlotToActor` 류 리졸버 함수가 이미 존재하는가, 신규 작성해야 하는가 | 전역 `find_nodes` 조회 필요(MCP 금지로 미실시) | §9-3과 같은 조회 세션에서 함께 확인 권고 |
| 8 | `D1 §9-3`(R-9 `EstimatedTurnSec`) 0.55 어긋남의 실질 영향 범위 | AT6/D6(FX 예산 린트 L27) 소관이라 MA 설계 자체엔 직접 영향 없다고 판단했으나, FT1-1c(SCF)로 FX 타이밍 관련 함수를 검증할 때 이 어긋남이 재발할 수 있다 — 미검토 | AT6/D6 착수 전 별도 정정 필요(plan v2가 이미 지시함, §11 참조) |

---

## 11. ★반드시 반영할 실측 3건 — 반영 확인

| # | 실측 | 본 문서 반영 위치 |
|---|---|---|
| 1 | 유닛턴 2.100s / FX 가용 창 1.200s / `Delay(0.55)` 3경로 합류 | §2 표 · §4-2(초기화 레이스 서술의 배경) — MA 자체는 이 예산 소비 구간(`EnterExecuting` 이후) 밖에서 동작하므로 **직접 영향 없음**을 확인(§4-1 게이트가 `EnterExecuting`/`ResolveHit` 무접촉을 요구하는 이유와 정합) |
| 2 | `PlayAttack`은 블로킹하지 않는다(H18 부정, 60fps 실측) | §2 표 · [[BP정리_통합명세_2026-08-11]] L267의 구판 서술("~0.58s 블록")이 **스테일**임을 §2에서 명시. MA 설계는 이 구판 가설 위에 서지 않았음(FT1-1a/1b/1c 어디도 `PlayAttack` 타이밍에 의존하지 않는다) |
| 3 | `D1 §9-3`(R-9) 가산식이 실측과 0.55 어긋남(임팩트 FX 병렬인데 식은 순차 가산) | §10 미확인 8번 — **모순을 명시만 하고 판정하지 않았다.** MA 설계 범위 밖(AT6/D6 소관)이나, FT1-1c SCF로 FX 관련 함수를 찌를 때 이 어긋남을 실측 기준으로 재확인할 것을 권고 |

---

## 관련

[[../../../자율진행_plan_v2|자율진행_plan_v2]] · [[../../스킬연출구조/raw/자율진행_TC|자율진행_TC]] · [[F7b_재개계획_초안]] · [[전진로직_실체_확정]] · [[턴길이_실측확정_2026-08-12]] · [[턴예산_balance판정_2026-08-12]] · [[BP정리_통합명세_2026-08-11]] · [[../../스킬연출구조/raw/D1_4슬롯구조_확정|D1_4슬롯구조_확정]] · [[../../스킬연출구조/raw/FT1-0_TC|FT1-0_TC]] · [[BT5_S1봉인수단_판별]] · [[전투BP_현황도_2026-08-11]] · [[../../../언리얼_MCP_실전노하우|언리얼_MCP_실전노하우]]
