---
type: gate
project: projectTP
feature: 스킬연출구조
stage: FT1-S3-D2~D6
updated: 2026-08-13
status: PASS
status_note: "D2~D6(심기) 완료 — 변수 1건 신설 + 노드 17건 생성 + 연결 16건(데이터7·exec9) + 핀값 7건. ★D7(무장·스모크)은 절대 미수행 — `ExecutionSequence_0.then_0`·`then_1` 둘 다 빈 채로 유지, 신규 17노드는 BeginPlay로부터 도달 불가능한 고아 섬(N1.execute 입력 핀 connected_pins=[] 직접 확인). 각 단계 끝 compile_blueprint 전부 에러 0(예외 없음). 노드 총수 184(D1 재확인)→186(D3)→201(D4~D6, 불변). N2 생성문자열 확정: `Variables|디폴트|GetAutoStartBattle`. N5·N8 승격 실측 확정: `수학|바이트|Equal(Byte)`(A/B=바이트) · `수학|인티저|integer>integer`(A/B=인티저) — F1(BattleState 타입) 완전 종결, 자동 형변환 노드 0건. save_assets는 D6 끝 1회, 명시 경로 1건(`/Game/Blueprints/BP_BattleManager`). git porcelain: `BP_BattleManager.uasset` 1파일만 M, `.umap` 부재. 편차 3건: ⓐN1 출력 exec 핀 실제 이름은 `Completed`가 아니라 `then`(착수판정 §3-2 표기와 다름, 기능엔 무영향 — connect_pins는 index_id로 연결) ⓑN5·N8의 B핀 연결 후 기본값은 빈 문자열(\"\")이지 \"0\"이 아니었음(TC F9의 '비변별' 가정과 다름 — 명시적 set_pin_value 필요했고 변별적이었다) ⓒget_default_object CDO 프로퍼티 읽기는 컴파일 완료 전엔 실패함(add_variable 직후 즉시 조회 시 에러, 컴파일 후 성공 — AU-FSTP-05→06 순서보다 컴파일이 선행되어야 함)."
---

# FT1-S3 D2~D6 — 심기(수술) 결과 (2026-08-13)

> 선행 지시서: [[FT1-S3_D1_조회결과]](도면 확정) · [[FT1-S3_TC]] §2-D2~D6(`AU-FSTP-05~23`) · [[FT1-S3_착수판정]] §3-2 화이트리스트·§8 정정 5건 · [[언리얼_MCP_실전노하우]] 함정(56)(102)(104)(107)(109)
> 규율: **additive만, 기존 절단 0.** `Sequence.then_0`·`then_1` 접촉 금지(D7·S5 몫). `save_assets`는 D6 끝 1회, 명시 경로만. `.umap`·PIE·git mutating 명령 금지(git status 조회만 허용). 그래프를 바꾸는 호출(`create_node`/`connect_pins`/`set_pin_value`/`add_variable`)은 함정(56)에 따라 **전부 개별 호출**로 수행(ProgrammaticToolset 배치는 조회 전용으로만 사용).
#projectTP/스킬연출구조

---

## 0. 결론

1. **D2~D6 전부 PASS.** 정지선(컴파일 에러·화이트리스트 외 변화·생성문자열 0건·`add_variable` 실패·노드총수 불일치) 어느 것도 발동하지 않았다.
2. ★**D7(무장·스모크)은 수행하지 않았다.** `ExecutionSequence_0.then_0`→N1 연결은 **만들지 않았다** — D6 종료 시점 재조회로 `then_0`·`then_1` 둘 다 `connected_pins: []`(빈 채) 확인. N1의 입력 `execute` 핀도 `connected_pins: []` — 신규 17노드 전체가 BeginPlay 체인에서 도달 불가능한 **고아 섬**이다.
3. **노드 총수 진행**: 184(D1 베이스라인, 이 세션에서 재확인) → 186(D3, N17+N1) → 201(D4, 잔여 15노드) → 201(D5, 데이터연결만) → 201(D6, exec연결만). ★**목표 201과 정확히 일치.**
4. ★**N2 생성 문자열 확정**: `Variables|디폴트|GetAutoStartBattle`(D2에서 변수 신설 직후 `find_node_types`로 1건 매치, D1의 b접두 탈락 예측이 정확히 실현됨).
5. ★★**N5·N8 승격 실측 확정**(F1 최종 종결): `N4(BattleState, 바이트) → N5.A` 연결 직후 N5의 type_id가 `게임플레이태그|Equal(GameplayTagContainer)`(연결 전 임시 표시) → **`수학|바이트|Equal(Byte)`**로, A·B 핀 모두 `와일드카드` → `바이트`로 승격. `N7(Length, 인티저) → N8.A` 연결 직후 N8은 `수학|타임스팬|Timespan>Timespan`(연결 전 임시 표시) → **`수학|인티저|integer>integer`**로, A·B 핀 모두 `와일드카드` → `인티저`로 승격. **자동 형변환 노드 삽입 0건**(연결 전후 노드 총수 201 불변) — D1이 예측한 대로 화이트리스트 17 불변이 실측으로 확정됐다.
6. `save_assets(["/Game/Blueprints/BP_BattleManager"])` D6 끝 **1회만** 호출(명시 경로, 빈 리스트 아님) → `git -c core.quotepath=false status --porcelain` 결과 **`M Blueprints/BP_BattleManager.uasset` 1줄뿐**, `.umap` 부재.

---

## 1. D2 — 변수 `bAutoStartBattle` 신설

### 절차·원문

1. `list_variables(BP_BattleManager)` 사전 조회 → 29종, `bAutoStartBattle` **부재** 확인(원문: `["BattleState","bInputLocked","CurrentIndex","RegisteredCount","TurnQueue","ActiveUnit","ButtonRef","TurnCounter","PartyAttackPoint","EnemyAttackPoint","DefaultCamera","ActionCamDynamic","CamBack","CamLateral","CamHeight","CamLookBias","LookAtZOffset","CamBlendIn","bCamActionEnabled","CamToggleButtonRef","DebugForceEffectChance","SelectedTargets","bBattleOver","WinningTeam","BattleFinished","bWasSkip","HUDRef","PendingSkillId","PendingTargetToken"]`).
2. `add_variable(blueprint, name="bAutoStartBattle", type_name="bool")` → 반환 `null`(예외 없음 = 성공).
3. `set_variable_instance_editable(blueprint, "bAutoStartBattle", true)` → 반환 `null`(성공).
4. `list_variables` 사후 조회 → 30종, `bAutoStartBattle` **실재**(목록 끝에 추가).
5. ⚠**편차**: `get_default_object` 직후 곧바로 `ObjectTools.get_properties(cdo, ["bAutoStartBattle"])`를 시도했더니 에러: `"the following properties could not be read: bAutoStartBattle"`. `get_default_object`의 툴 설명 자체가 *"Blueprint must be compiled for the CDO to reflect the latest state"*라고 명시하는데, TC(`AU-FSTP-05→06`)는 컴파일(`07`)보다 CDO 확인(`06`)을 먼저 배치했다 — **순서를 06→07이 아니라 컴파일 선행으로 조정**했다.
6. `compile_blueprint` → 반환 `null`(에러 0).
7. 재시도: `get_properties(cdo, ["bAutoStartBattle"])` → **`{"bAutoStartBattle": false}`** — CDO 기본값 false 확정.
8. `find_nodes(EventGraph, title="")` 카운트 → **184**(불변, `add_variable`이 그래프 노드를 만들지 않음 확인).

### N2 생성 문자열 재검색·확정

`find_node_types(EventGraph, "GetAutoStartBattle", context_pins=[])` → **`["Variables|디폴트|GetAutoStartBattle"]`**(1건 매치, 무필터 나열 불요). ★D1의 b접두 탈락 예측(`GetInputLocked`·`GetBattleOver`·`GetWasSkip`·`GetCamActionEnabled` 4종 선례)이 5번째 사례로 확증됐다.

### D2 판정

컴파일 에러 0 · 노드총수 184 불변 · 변수 실재(Instance Editable 세터 성공, 단 이 프로젝트 MCP 툴셋엔 getter가 없어 세터 성공 여부로만 확인 — 아래 §7 참고) · CDO=false 확정 · N2 문자열 확정. **PASS.**

---

## 2. D3 — 고위험 노드 2건 (N17 → N1)

### N17 — `NotifyAttackButtonClicked`(self)

- `find_node_types(EventGraph, "함수호출|NotifyAttackButtonClicked", [])` → 1건 매치.
- `create_node(EventGraph, "함수호출|NotifyAttackButtonClicked", pos=(2400,-300))` → `refPath = EventGraph.K2Node_CallFunction_15`.
- `get_node_infos` 원문: `input_pins=[{"name":"execute","type_id":"실행"}, {"name":"self","type_id":"Self 오브젝트 레퍼런스"}]` / `output_pins=[{"name":"then","type_id":"실행"}]`. **데이터 입력 핀 0개** — 무인자 호출 전제 확인(착수판정 §2-가 전제와 일치).

### N1 — `Delay`

- `find_node_types(EventGraph, "유틸리티|플로컨트롤|Delay", [])` → `["유틸리티|플로컨트롤|DelayUntilNextTick","유틸리티|플로컨트롤|DelayUntilNextFrame","유틸리티|플로컨트롤|Delay"]`(정확 문자열 포함 확인).
- `create_node(EventGraph, "유틸리티|플로컨트롤|Delay", pos=(900,-200))` → `refPath = EventGraph.K2Node_CallFunction_28`.
- `get_node_infos` 원문: `input_pins=[{"name":"execute","type_id":"실행"}, {"name":"Duration","type_id":"플로트(단정밀도)","value":"0.2"}]` / `output_pins=[{"name":"then","type_id":"실행"}]`.
- ⚠★**편차(명세 대비)**: 출력 exec 핀 실제 이름은 **`then`** — 착수판정 §3-2가 명시한 `Completed`가 **아니다**. `connect_pins`는 이름이 아니라 `(direction, index_id, node)`로 연결하므로 D6 연결에는 지장이 없었으나, 문서 표기와 실물이 다르다는 사실은 기록한다.

### D3 검증

- `find_nodes` 카운트 → **186**(184+2).
- `get_node_infos(ExecutionSequence_0)` 재조회 → `then_0`·`then_1` `connected_pins:[]` 그대로, `execute` 입력은 여전히 마커 PrintString(`K2Node_CallFunction_12`)에서만 연결 — **무변화 확인**(함정107 규칙3).
- `compile_blueprint` → 에러 0.

**D3 PASS.**

---

## 3. D4 — 잔여 15노드 + 핀값 5건(N5·N8의 B는 D5로 이월)

### 생성 문자열 재확인(읽기 전용 배치 — 함정56 예외 허용 범위)

| 대상 | 문자열 | 매치 |
|---|---|---|
| N3,N9,N10,N12 | `Utilities\|FlowControl\|Branch` | 1건 |
| N4 | `Variables\|디폴트\|GetBattleState` | 1건 |
| N5 | `유틸리티\|연산자\|같음(==)` | 1건(와일드카드) |
| N6 | `Variables\|디폴트\|GetTurnQueue` | 1건 |
| N7 | `유틸리티\|배열\|Length` | 1건 |
| N8 | `유틸리티\|연산자\|보다큼(>)` | 1건(와일드카드) |
| N11 | `Variables\|디폴트\|GetInputLocked` | 1건 |
| N13~16 | `개발\|PrintString` | 1건 |

### 생성된 노드 15건 (개별 `create_node` 호출, refPath는 반환값 그대로 사용 — 함정103)

| # | refPath (`EventGraph.` 이하) | type_id(생성 직후) |
|---|---|---|
| N2 | `K2Node_VariableGet_2` | `\|GetbAutoStartBattle`(표시는 b유지, 출력 `bAutoStartBattle`=false) |
| N3 | `K2Node_IfThenElse_7` | `Utilities\|FlowControl\|Branch` |
| N4 | `K2Node_VariableGet_9` | `\|GetBattleState`(출력 `BattleState`=바이트,"0") |
| N5 | `K2Node_PromotableOperator_2` | `게임플레이태그\|Equal(GameplayTagContainer)`(연결 전 임시, A/B=와일드카드) |
| N6 | `K2Node_VariableGet_14` | `\|GetTurnQueue`(출력 `TurnQueue`=BP Battle Spawn Point 오브젝트 레퍼런스 배열) |
| N7 | `K2Node_CallArrayFunction_1` | `유틸리티\|배열\|Length`(출력 `ReturnValue`=인티저,"0") |
| N8 | `K2Node_PromotableOperator_3` | `수학\|타임스팬\|Timespan>Timespan`(연결 전 임시, A/B=와일드카드) |
| N9 | `K2Node_IfThenElse_8` | `Utilities\|FlowControl\|Branch` |
| N10 | `K2Node_IfThenElse_9` | `Utilities\|FlowControl\|Branch` |
| N11 | `K2Node_VariableGet_15` | `\|GetbInputLocked`(출력 `bInputLocked`=false) |
| N12 | `K2Node_IfThenElse_10` | `Utilities\|FlowControl\|Branch` |
| N13 | `K2Node_CallFunction_29` | `개발\|PrintString`(InString 기본 "Hello") |
| N14 | `K2Node_CallFunction_30` | 〃 |
| N15 | `K2Node_CallFunction_31` | 〃 |
| N16 | `K2Node_CallFunction_32` | 〃 |

★N5·N8의 연결 전 임시 type_id(`Equal(GameplayTagContainer)`/`Timespan>Timespan`)는 **와일드카드 노드의 기본 오버로드 표시**일 뿐 — A·B 핀 자체는 `와일드카드`로 아직 미확정. D1이 예측한 성질이 실측 재현됐다(구체적으로 어느 오버로드가 기본 표시되는지는 D1도 예측하지 못한 세부사항).

### 핀값 5건 (order-independent, N5.B·N8.B는 D5로 이월)

| 핀 | 설정 전 | 설정 후(재조회) |
|---|---|---|
| N1.Duration | `0.2` | `0.1` |
| N13.InString | `Hello` | `MA:AUTOSTART:GUARDFAIL:state` |
| N14.InString | `Hello` | `MA:AUTOSTART:GUARDFAIL:queue` |
| N15.InString | `Hello` | `MA:AUTOSTART:GUARDFAIL:lock` |
| N16.InString | `Hello` | `MA:AUTOSTART:FIRE` |

리터럴 4종은 착수판정 §3-2 원문과 **바이트 단위 일치**(콜론 개수·대소문자·공백 전부 대조 완료).

### D4 검증

- `find_nodes` 카운트 → **201**(184+17, N1·N17 포함 전체).
- `get_node_infos(ExecutionSequence_0)` → `then_0`·`then_1` 여전히 빈 채, 무변화.
- 신규 17노드 전수의 입력 exec 핀 `connected_pins`가 이 시점까지 전부 `[]`(연결을 아직 하나도 안 했으므로 자명) — 진입점 0 자명 성립.
- `compile_blueprint` → 에러 0.

**D4 PASS.**

---

## 4. D5 — 데이터 연결 7건 (+ N5·N8 승격 확인 및 B값 확정)

### 연결 7건 (개별 `connect_pins`, 전부 데이터 핀)

| # | 출력 | 입력 |
|---|---|---|
| 1 | `N2(VariableGet_2).bAutoStartBattle`(out,0) | `N3(IfThenElse_7).Condition`(in,1) |
| 2 | `N4(VariableGet_9).BattleState`(out,0) | `N5(PromotableOperator_2).A`(in,0) |
| 3 | `N5.ReturnValue`(out,0) | `N9(IfThenElse_8).Condition`(in,1) |
| 4 | `N6(VariableGet_14).TurnQueue`(out,0) | `N7(CallArrayFunction_1).TargetArray`(in,0) |
| 5 | `N7.ReturnValue`(out,0) | `N8(PromotableOperator_3).A`(in,0) |
| 6 | `N8.ReturnValue`(out,0) | `N10(IfThenElse_9).Condition`(in,1) |
| 7 | `N11(VariableGet_15).bInputLocked`(out,0) | `N12(IfThenElse_10).Condition`(in,1) |

`get_node_infos` 재조회(함정107 규칙3) → **7건 전부 양방향** `connected_pins`에 반영 확인(원문 전량 조회 완료, 편도 누락 0건).

### ★★N5·N8 승격 확정 (원문)

**N5** (`K2Node_PromotableOperator_2`) 연결 후:
```
type_id: "수학|바이트|Equal(Byte)"
A: type_id="바이트", connected_pins=[N4.BattleState]
B: type_id="바이트", connected_pins=[]
```

**N8** (`K2Node_PromotableOperator_3`) 연결 후:
```
type_id: "수학|인티저|integer>integer"
A: type_id="인티저", connected_pins=[N7.ReturnValue]
B: type_id="인티저", connected_pins=[]
```

둘 다 `와일드카드` → 콘크리트 타입으로 승격 확인. **화이트리스트 노드수 불변**(재조회 `find_nodes` 카운트 = 201, D4와 동일 — 자동 형변환 노드 삽입 0건, F1 완전 종결).

### ⚠B값 편차 — 명시 확인 필요했음(TC F9 가정과 다름)

`get_pin_value(N5.B)` → `""`(빈 문자열, `"0"`이 아님). `get_pin_value(N8.B)` → `""`(동일). ★**TC(`AU-FSTP-12`/F9)의 "승격 후 기본값이 이미 0"이라는 가정이 실측과 달랐다** — 승격 직후 값은 미설정 상태(빈 문자열)였다. `set_pin_value(N5.B, "0")` / `set_pin_value(N8.B, "0")` 실행 후 재조회 → 둘 다 **`"0"`** 확정.

### D5 검증

- `find_nodes` 카운트 → **201**(불변, D4와 동일).
- `get_node_infos(ExecutionSequence_0)` → 무변화.
- `compile_blueprint` → 에러 0.

**D5 PASS.** (핀값 7건 전체 이제 완결: N1.Duration=0.1 · N5.B=0 · N8.B=0 · N13~16.InString ×4)

---

## 5. D6 — exec 연결 9건 (★부착 제외)

### 연결 9건 (개별 `connect_pins`, 전부 exec 핀 — `Sequence.then_0→N1`은 제외)

| # | 출력 | 입력 | 의미 |
|---|---|---|---|
| 1 | `N1(CallFunction_28).then`(out,0) | `N3(IfThenElse_7).execute`(in,0) | Delay 완료 → 토글 게이트 |
| 2 | `N3.then`(out,0, True) | `N9(IfThenElse_8).execute`(in,0) | 토글 on → state 게이트 |
| 3 | `N9.then`(out,0, True) | `N10(IfThenElse_9).execute`(in,0) | state==0 → queue 게이트 |
| 4 | `N9.else`(out,1, False) | `N13(CallFunction_29).execute`(in,0) | state≠0 → GUARDFAIL:state |
| 5 | `N10.then`(out,0, True) | `N12(IfThenElse_10).execute`(in,0) | qlen>0 → lock 게이트 |
| 6 | `N10.else`(out,1, False) | `N14(CallFunction_30).execute`(in,0) | qlen==0 → GUARDFAIL:queue |
| 7 | `N12.then`(out,0, True) | `N15(CallFunction_31).execute`(in,0) | locked==true → GUARDFAIL:lock |
| 8 | `N12.else`(out,1, False) | `N16(CallFunction_32).execute`(in,0) | locked==false → FIRE |
| 9 | `N16.then`(out,0) | `N17(CallFunction_15).execute`(in,0) | FIRE 로그 → 실제 호출 |

`N3.else`(False, 인덱스1)는 **의도적으로 미연결**(토글 off = 무음 종단, 착수판정 §2-나 설계 그대로).

### 재조회 검증 (함정107 규칙3, 원문)

- `N1.then.connected_pins = [N3.execute]` ✓ / `N3.execute.connected_pins=[N1.then]` ✓
- `N3.then.connected_pins=[N9.execute]` ✓, `N3.else.connected_pins=[]`(의도된 무연결) ✓
- `N9.then.connected_pins=[N10.execute]` ✓, `N9.else.connected_pins=[N13.execute]` ✓
- `N10.then.connected_pins=[N12.execute]` ✓, `N10.else.connected_pins=[N14.execute]` ✓
- `N12.then.connected_pins=[N15.execute]` ✓, `N12.else.connected_pins=[N16.execute]` ✓
- `N16.then.connected_pins=[N17.execute]` ✓
- `N17.then.connected_pins=[]`(체인 종단, 하류 없음 — 화이트리스트 외 연결 0 확인)

### ★★부착 미실행 확정 (핀 원문)

```
K2Node_ExecutionSequence_0
  output then_0: connected_pins = []   ← ★빈 채(부착 안 함)
  output then_1: connected_pins = []   ← ★빈 채(S5 예약, 무손상)
  input  execute: connected_pins = [K2Node_CallFunction_12]   ← 마커 PrintString, 기존 그대로

K2Node_CallFunction_28 (N1, Delay)
  input execute: connected_pins = []   ← ★신규 17노드 체인 전체가 여기서 끊김 = 고아 섬
```

### D6 검증

- `find_nodes` 카운트 → **201**(불변, D4·D5와 동일). 화이트리스트 정확히 17노드분만 반영.
- `compile_blueprint` → 에러 0.

**D6 PASS.**

---

## 6. 저장 및 diff 확인 (D6 종료 직후, 1회)

- `save_assets(["/Game/Blueprints/BP_BattleManager"])` → 반환 `true`. **명시 경로 1건, 빈 리스트 아님**(함정102 회피).
- `git -C "D:/unreal/projectTP/Content" -c core.quotepath=false status --porcelain` 원문:
  ```
   M Blueprints/BP_BattleManager.uasset
  ```
  **정확히 1파일만 M, `.umap` 부재.**

---

## 7. 예상과 달랐던 것 (편차 3건 + 참고 2건)

1. ★**N1 출력 exec 핀 실제 이름 = `then`**(착수판정 §3-2의 `Completed` 표기와 다름). `connect_pins`는 `(direction,index_id,node)`로 연결하므로 실제 배선에는 영향 없었으나, 문서·실물 표기 불일치는 후속 문서(착수판정 재정정)에 반영 필요.
2. ★★**N5·N8의 B핀은 승격 직후 기본값이 `"0"`이 아니라 빈 문자열**이었다 — TC F9("B값이 이미 0이라 재조회로 성공/실패 구분 불가")의 전제가 틀렸다. 실제로는 `set_pin_value`가 **변별적**이었다(빈 문자열 → "0"으로 변화 관측). 값 자체는 최종적으로 설계 의도(`B=0`)와 일치하므로 실해는 없으나, 적대검토 문서의 가정 정정이 필요하다.
3. ★**`get_default_object`+`ObjectTools.get_properties`는 컴파일 완료 전에는 신규 변수를 읽지 못한다**(에러: `the following properties could not be read`). 툴 자체 문서가 이미 "컴파일 후에만 CDO가 최신 상태를 반영한다"고 명시하므로 예상 가능했으나, TC(`AU-FSTP-05→06→07`)의 순서 그대로는 실행 불가 — 컴파일(07 해당 동작)을 06보다 먼저 수행했다.
4. (참고) N5·N8의 **연결 전 임시 type_id**가 `게임플레이태그|Equal(GameplayTagContainer)` / `수학|타임스팬|Timespan>Timespan`처럼 의미상 전혀 무관한 오버로드로 표시됐다 — D1은 "임시 표시가 있을 것"까지는 예측했으나 구체적으로 어떤 오버로드가 기본인지는 예측 범위 밖이었다. 기능에는 영향 없음(승격 후 정확한 Byte/Integer로 교정 확인).
5. (참고) `Branch`(`IfThenElse`)의 출력 exec 핀 이름은 `then`/`else`(Sequence의 `then_0`/`then_1`과 다른 명명 체계) — 연결에는 index_id 0/1로 대응했으므로 지장 없음.

★**이 세션에서 그래프를 바꾸는 호출은 전부 개별 `mcp__unreal-mcp__call_tool` 호출로 수행**했다(함정56 회피 — `ProgrammaticToolset` 배치는 `find_nodes` 카운트 집계 등 순수 조회에만 사용). `add_variable`/`create_node`×17/`connect_pins`×16/`set_pin_value`×7 전부 개별 호출, 매 단계 직후 `get_node_infos` 재조회로 확인.

---

## 8. 다음 단계(D7)를 위한 참고 — ★이번 세션에서 만들지 않음

D7이 만들 유일한 잔여 연결(부착):
```
ExecutionSequence_0.then_0(out,0) → K2Node_CallFunction_28(N1, Delay).execute(in,0)
```
D7 착수 시 `get_node_infos(ExecutionSequence_0)`로 `then_0`이 **여전히 미배선**임을 먼저 재확인(함정107 규칙1)한 뒤 연결할 것 — 이 문서가 그 사전 확인의 기준선이다.

---

## 관련

[[FT1-S3_D1_조회결과]] · [[FT1-S3_TC]] · [[FT1-S3_착수판정]] · [[언리얼_MCP_실전노하우]]
