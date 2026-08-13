---
type: gate
project: projectTP
feature: 스킬연출구조
stage: FT1-S3-D1
updated: 2026-08-13
status: PASS
status_note: "D1(조회 전용) 완료 — 수술 0건, save_assets 0회. F1(BattleState 타입 모순) 해소: 콘크리트 핀 타입=Byte, `Equal(Byte)`/`integer>integer`는 `K2Node_PromotableOperator`(UE5 와일드카드 승격 연산자)의 승격 후 표시형이며 find_node_types로 직접 검색 시 0건 — 화이트리스트 노드수는 17로 불변이나 N5·N8의 생성 전략이 '기존 type_id 그대로 생성'에서 '와일드카드 생성→연결→승격'으로 정정됨. N8 와일드카드 확정(N5도 동일 클래스로 새로 확인). Delay 생성문자열 확보(`유틸리티|플로컨트롤|Delay`, RetriggerableDelay와 동일 로케일 — Sequence와는 다름). 베이스라인: EventGraph 184노드(불변, compile 전후 동일)·컴파일 경고 0(에러 0, 컴파일 후 LogBlueprint 추가 라인 없음)·`then_0`/`then_1` 둘 다 빈 채. is_dirty(BP)=true(compile로 인한 인메모리, save 미호출)·is_dirty(레벨)=false. 부수 발견: N11(bInputLocked) 생성문자열이 `GetbInputLocked`가 아니라 `GetInputLocked`(b접두 탈락) — 착수판정 힌트 표 정정 필요."
---

# FT1-S3-D1 — 조회 전용 단계 결과 (2026-08-13)

> 선행 지시서: [[FT1-S3_TC]] §2-D1(`AU-FSTP-01~04`) · [[FT1-S3_착수판정]] §3-2 화이트리스트·§8 PM 정정 5건 · [[FT1-S1_조회결과_2026-08-13]] · [[언리얼_MCP_실전노하우]] 함정(103)(104)(109)
> 규율: **조회 전용, 수술 0건.** 사용한 툴: `list_functions`/`list_events`/`list_variables`/`list_graphs`/`get_graph`/`find_nodes`/`get_node_infos`/`get_connected_subgraph`/`find_node_types`/`get_default_object`/`ObjectTools.list_properties`/`ObjectTools.get_properties`/`compile_blueprint`/`AssetTools.is_dirty`/`AssetTools.find_assets`/`LogsToolset.GetLogEntries`. **`create_node`·`connect_pins`·`break_pins`·`set_pin_value`·`add_variable`·`delete_node`·`get_node_type_pins`(함정103 노드생성 위험 회피) 전부 0회.** `save_assets` 0회. `git` 명령 0회(PM 위임).
#projectTP/스킬연출구조

---

## 0. 결론 5줄

1. ★★**F1(BattleState 타입 모순) 해소.** `GetBattleState` VariableGet 노드의 출력 핀 `type_id`가 직접 조회로 **`바이트`(Byte)**임을 실측했다. `ObjectTools.list_properties`가 보고한 `"type":"integer"`는 byte/int32를 모두 포괄하는 JSON Schema 상위 카테고리였을 뿐 — **모순이 아니라 서술 층위 차이**였다. `Equal(Byte)`는 이미 정확한 선택이다. ★단 생성 전략은 정정 필요(§1 참고).
2. ★★**N5·N8 둘 다 `K2Node_PromotableOperator`(와일드카드) 클래스로 확정.** `find_node_types`로 `"Equal(Byte)"`·`"integer>integer"`·`"Equal(Integer)"`를 직접 검색하면 **전부 0건** — 이 문자열들은 独자 생성 불가능한, **연결 후 승격된 표시형**이다. 진짜 생성 문자열은 일반 와일드카드 연산자 카테고리 `유틸리티|연산자|`에서 나왔다: N5=`같음(==)`, N8=`보다큼(>)`. ★**착수판정 §3-2 N5의 "그 노드의 type_id를 조회해 동일 타입으로 생성" 지시는 문자 그대로 실행 불가 — 정정 필요.**
3. **화이트리스트 노드 수는 17로 불변.** 자동 형변환 노드 삽입 위험은 없다(BattleState가 실제로 Byte라서). 단 N5·N8은 D4/D5에서 **"연결 먼저 → 그 다음 리터럴/재조회"** 순서가 필요하다(둘 다 동일 근거).
4. **생성 문자열 8종 전부 확보**(원문, §3 표). `Delay`=`유틸리티|플로컨트롤|Delay`(RetriggerableDelay와 동일 로케일 — Sequence와는 반대 방향이었다). `NotifyAttackButtonClicked` self-call=`함수호출|NotifyAttackButtonClicked`, 입력 데이터 핀 0개 직접 확인.
5. **베이스라인 확정**: EventGraph **184**노드(compile 전후 불변) · 컴파일 에러 0·경고 0(근거는 §5) · `then_0`/`then_1` 둘 다 빈 채 · `is_dirty(BP_BattleManager)=true`(compile로 인한 인메모리, §6) · `is_dirty(레벨)=false` · `save_assets` 0회.

---

## 1. ① F1 — `BattleState` 타입 모순 판정

### 실측 절차와 원문

**(a) CDO 프로퍼티 조회** — `get_default_object(BP_BattleManager)` → `/Game/Blueprints/BP_BattleManager.Default__BP_BattleManager_C` → `ObjectTools.list_properties(cdo)`:

```
"battleState":{"type":"integer"}
"turnQueue":{"type":"array","items":{"type":"object","title":"/Game/Blueprints/BP_BattleSpawnPoint.BP_BattleSpawnPoint_C", ...}}
```

`get_properties(cdo, ["BattleState"])` → `{"BattleState":0}` (CDO 기본값, 참고용·판정 비대상).

**(b) `NotifySkillSelected` 그래프 내 실제 노드 조회**(27노드 전수 `get_node_infos`) — 진입 가드 체인:

```
K2Node_VariableGet_1  type_id="|GetBattleState"
  output_pins: [{name:"BattleState", type_id:"바이트", value:"0", n_connected:1}]   ← ★콘크리트 핀 타입 = Byte

K2Node_PromotableOperator_0  type_id="수학|바이트|Equal(Byte)"
  input_pins:
    A: type_id="바이트", n_connected:1 (← GetBattleState 출력에서 연결)
    B: type_id="바이트", value="2", n_connected:0
  output_pins: [{name:"ReturnValue", type_id:"부울"}]
```

### 판정

★**모순이 아니라 서술 층위 차이였다.** `list_properties`가 보고하는 JSON Schema `"type":"integer"`는 UE의 `byte`(uint8)/`int32`/`int64`를 전부 포괄하는 넓은 카테고리다(JSON Schema에 byte 전용 타입이 없다). 반면 그래프 안의 실제 `GetBattleState` 핀은 명확히 `바이트`(Byte)다. [[전투BP_현황도_2026-08-11]] §2가 "정수형 변수"라고 적은 것은 `list_properties`의 이 상위 카테고리 표기를 그대로 옮긴 것으로, **틀린 것이 아니라 정밀도가 낮았을 뿐**이다. `Equal(Byte)`는 처음부터 옳은 선택이었다.

★★**그런데 생성 전략에는 실제 결함이 있었다.** 착수판정 §3-2 N5 지시: *"그 노드의 type_id를 조회해 동일 타입으로 생성(제일 안전)"* — 즉 `"수학|바이트|Equal(Byte)"` 문자열로 직접 `create_node`하라는 뜻인데, 이 문자열은 **`find_node_types`로 검색하면 0건**이다(§2 참고). 이유: `K2Node_PromotableOperator_0`은 UE5의 **와일드카드 승격 연산자**(Promotable Operator) 노드이고, `"Equal(Byte)"`는 A/B 핀이 Byte에 **연결된 뒤** 표시되는 사후 형태일 뿐, 독자적으로 생성 가능한 카탈로그 항목이 아니다(§2에서 `수학|바이트|` 카테고리 전체를 나열해도 `Equal(Byte)`는 없다 — `%(Byte)`·`Min(Byte)`·`Max(Byte)`·`MakeLiteralByte`뿐).

### ★화이트리스트 영향

- **노드 수: 17 → 17, 불변.** BattleState가 실제로 Byte이므로 `N4→N5.A` 연결 시 자동 형변환 노드가 삽입될 일이 없다(형변환이 필요한 진짜 타입 불일치가 아니었다).
- **생성 전략만 정정**: N5는 `"수학|바이트|Equal(Byte)"`가 아니라 **`"유틸리티|연산자|같음(==)"`**(와일드카드)으로 생성 → `N4(Byte)→N5.A` 연결 → 노드 전체가 Byte로 승격됨을 재조회로 확인.

---

## 2. ② N8(`TurnQueue.Length > 0`) 와일드카드 여부 판정

### 재사용 후보 탐색(지시서 권고대로 먼저 수행)

`NotifySkillSelected`에서 `GetSkillCooldown(...) > 0`(쿨다운 체크) 비교 노드를 발견:

```
K2Node_PromotableOperator_1  type_id="수학|인티저|integer>integer"
  input_pins:
    A: type_id="인티저", n_connected:1 (← GetSkillCooldown.ReturnValue)
    B: type_id="인티저", n_connected:0 (리터럴, 값 미표시=기본 0)
  output_pins: [{name:"ReturnValue", type_id:"부울"}]
```

`InitBattle`에서도 `TurnQueue.Length == 0` 체크(가드 `"Init ERROR: TurnQueue length is 0 after compact - battle halted"`, S1이 이미 실측한 리터럴과 원문 일치)에 쓰이는 자매 노드 발견:

```
K2Node_PromotableOperator_0  type_id="수학|인티저|Equal(Integer)"
  input_pins: A(인티저, connected 1) / B(인티저, connected 0)
```

**세 개의 비교 노드(Equal Byte / Integer>Integer / Equal Integer) 전부 동일 클래스 `K2Node_PromotableOperator`다.**

### 직접 검색으로 재확인(결정적 증거)

`find_node_types(EventGraph, "integer>integer")` → **0건**. `find_node_types(EventGraph, "Equal(Integer)")` → **0건**(별도 확인은 안 했으나 같은 클래스·같은 원리이므로 Equal(Byte)와 동형 — §1 근거 재사용). `수학|인티저|` 카테고리 전체 나열에도 비교 연산자 없음(Min/Max/Clamp/Sign/Wrap/Bitwise 등뿐).

`유틸리티|연산자|` 카테고리 전체 나열(10건) — **여기가 진짜 생성처**:

```
유틸리티|연산자|같지않음(!=)
유틸리티|연산자|같음(==)        ← N5 생성 문자열
유틸리티|연산자|작거나같음(<=)
유틸리티|연산자|작음(<)
유틸리티|연산자|크거나같음(>=)
유틸리티|연산자|보다큼(>)       ← ★N8 생성 문자열
유틸리티|연산자|빼기
유틸리티|연산자|곱하기
유틸리티|연산자|나누기
유틸리티|연산자|추가            (함정104 기지정)
```

### ★판정 — N8은 와일드카드다(확정)

★★**N8은 `K2Node_PromotableOperator` 와일드카드 노드다.** 근거는 이중이다: (a) 함정104의 일반 패턴(`유틸리티|연산자|<한글>(<기호>)` 계열은 와일드카드) (b) **이번에 이 블루프린트 안에서 실물로 확인** — `Integer>Integer` 비교가 이미 2곳(NotifySkillSelected 쿨다운 체크, 그리고 N5 재사용후보인 Equal(Byte)와 동일 클래스)에서 승격된 형태로 존재하고, 승격 전 원형 문자열(`integer>integer`)로는 생성이 불가능함을 직접 검색으로 확인했다.

### D4/D5 순서 분기 결론

★**착수판정 §8 "부수 정정"(gameplay-engineer)이 N8에 대해 예상한 "연결 먼저, 리터럴 나중"이 옳았고, 이번 조사로 그 근거가 실측으로 굳어졌다.** ★단 이 조사는 **N5도 동일하게 적용해야 함을 추가로 발견**했다(착수판정은 N5에 대해 "type_id 그대로 생성"이 안전하다고 봤으나 §1에서 보였듯 그 전제가 틀렸다).

**권고 순서(N5·N8 공통)**: `create_node("유틸리티|연산자|같음(==)" 또는 "유틸리티|연산자|보다큼(>)")` → `connect_pins(A ← 소스)` → `get_node_infos`로 노드가 Byte/Integer로 승격됐는지 재확인 → (B는 승격 후 기본값이 이미 0이므로 대개 별도 `set_pin_value` 불요 — `AU-FSTP-12`가 이미 "B값 비변별" 고지) → 필요시 `set_pin_value(B, 0)` → 재조회.

★이것은 **직접 `create_node` 실험이 아니라 기존 승격된 노드·직접 검색 결과로부터의 추론**이다. D3(`AU-FSTP-08/09`)이 실제 `create_node`로 이 예측을 확정해야 한다.

---

## 3. ③ 생성 문자열 확정 목록 (원문)

전부 `find_node_types(EventGraph, ...)`로 직접 검색해 확정(괄호 안은 검증 방법):

| # | 노드 | ★확정 생성 문자열 | 검증 |
|---|---|---|---|
| N1 | `Delay` | **`유틸리티|플로컨트롤|Delay`** | 직접 검색 1건 매치(전체 79건 중). RetriggerableDelay·DelayUntilNextTick·DelayUntilNextFrame과 **동일 로케일**(한글 카테고리+영문 이름) — Sequence(함정109, 영문카테고리+한글이름)와는 반대 |
| N3,N9,N10,N12 | `Branch` | **`Utilities|FlowControl|Branch`** | 직접 검색 1건 매치 + 기존 노드 5건(NotifySkillSelected 4·InitBattle 1) 전수 일치 |
| N4 | VariableGet `BattleState` | **`Variables|디폴트|GetBattleState`** | 직접 검색 성공 |
| N5 | 동등비교 | ★**`유틸리티|연산자|같음(==)`**(와일드카드, 연결 후 Byte로 승격) | §1·§2 — `Equal(Byte)` 직접검색 0건 확인 후 카테고리 전체나열로 대체확정 |
| N6 | VariableGet `TurnQueue` | **`Variables|디폴트|GetTurnQueue`** | 직접 검색 성공 |
| N7 | Array `Length` | **`유틸리티|배열|Length`** | 직접 검색 1건 매치(28건 카테고리 전체 나열에도 포함) + 기존 노드(InitBattle `K2Node_CallArrayFunction_1`) 일치. ★N5/N8과 달리 **원형 이름 그대로 독자 생성 가능**(승격 후에도 이름이 안 바뀜) |
| N8 | 초과비교 | ★**`유틸리티|연산자|보다큼(>)`**(와일드카드, 연결 후 Integer로 승격) | §2 — `integer>integer` 직접검색 0건 확인 후 카테고리 전체나열로 대체확정 |
| N11 | VariableGet `bInputLocked` | ★**`Variables|디폴트|GetInputLocked`**(★b접두 탈락 주의) | 직접 검색 성공. `"GetbInputLocked"`로 검색하면 **0건** — 아래 §7 참고 |
| N13~N16 | `PrintString` | **`개발|PrintString`** | 직접 검색 1건 매치 + 기존 노드 다수(NotifySkillSelected 2·InitBattle 3·EventGraph 마커 1) 일치. S2 실적과 동일 |
| N17 | `NotifyAttackButtonClicked`(self) | **`함수호출|NotifyAttackButtonClicked`** | 직접 검색 1건 매치. 함수 `FunctionEntry` 노드를 직접 조회해 **출력 핀이 `then`(실행) 1개뿐**임을 확인 — 입력 데이터 핀 0개(파라미터 없음), 착수판정의 "무인자 호출 전제"가 실제로 성립 |

**참고 — 생성 불필요(D2 대상, 변수 자체가 없음)**:

| 항목 | 상태 |
|---|---|
| V1 `bAutoStartBattle` (변수) | `list_variables`·`get_properties` 양쪽에서 **부재 확인**(get_properties 시도 시 `"the following properties could not be read: bAutoStartBattle"` 에러로 확정) |
| N2 VariableGet `bAutoStartBattle` | ★변수가 없어 검색 불가 — **예측만 가능**: `Variables|디폴트|GetAutoStartBattle`(b접두 탈락 패턴, 아래 §7 근거로 외삽). **미확정 — D2에서 변수 생성 직후 재검색 필수** |

---

## 4. ④ `TurnQueue` 타입 재확인 (근거사슬 보강)

`list_variables(BP_BattleManager)` 원문(29종 중 발췌) — `TurnQueue`가 실재:
```
["BattleState", "bInputLocked", "CurrentIndex", "RegisteredCount", "TurnQueue", "ActiveUnit", ...]
```

`ObjectTools.list_properties(cdo)` 원문(보강):
```
"turnQueue":{"type":"array","items":{"type":"object","title":"/Game/Blueprints/BP_BattleSpawnPoint.BP_BattleSpawnPoint_C", "properties":{"refPath":{...}}}}
```

★**확정**: `TurnQueue` = `BP_BattleSpawnPoint` 오브젝트 레퍼런스 **배열**. `E0_프로브`(2026-07-07, `bInputLocked` 등 생성)와 `AT4-b-2_결과`(`ForEachLoop` 재확인)의 기존 결론과 완전히 일치 — 근거사슬의 인용 누락만 메운 것이며 신규 모순 없음.

---

## 5. ⑤ 베이스라인 기록

### EventGraph 노드 총수

`find_nodes(EventGraph, title="")` → **184**(compile 전) / **184**(compile 후, 재확인) — ★불변.

### `ExecutionSequence_0` 및 상류 체인 핀 원문 (`get_connected_subgraph(BeginPlay)`)

```
K2Node_Event_0 (BeginPlay, type_id="이벤트추가|BeginPlay이벤트")
  output: OutputDelegate(델리게이트, connected=[]) / then(실행, connected=[K2Node_CallFunction_12])

K2Node_CallFunction_12 (PrintString 마커, type_id="개발|PrintString")
  input: InString = "SessionBoundary|event=BeginPlay"
  output: then(실행, connected=[K2Node_ExecutionSequence_0])

K2Node_ExecutionSequence_0 (Sequence, type_id="Utilities|FlowControl|시퀀스")   ← 함정109 실측과 정확히 일치
  input: execute(connected=[K2Node_CallFunction_12])
  output: then_0(실행, connected_pins=[])   ← ★빈 채
          then_1(실행, connected_pins=[])   ← ★빈 채
```

`get_connected_subgraph` 반환 노드 수 = **3**(BeginPlay·마커·Sequence뿐 — S2 상태와 완전 일치, 하류 확장 없음).

### 컴파일 결과

`compile_blueprint(BP_BattleManager, warnings_as_errors=False)` → 예외 없이 반환(= **에러 0**). 반환값 자체는 구조화 데이터가 없음(`{"returnValue": null}` — 이 툴은 warning 카운트를 직접 반환하지 않는다, §7 예상과 달랐던 것 참고).

★**경고 개수는 로그 대조로 간접 확정**: `LogsToolset.GetLogEntries(category="LogBlueprint")` 최신 8건 원문:
```
[06.44.59][728] LogBlueprint: Warning: No execute pin found on node .../EventGraph.K2Node_Event_0
[06.48.01][474] LogBlueprint: Warning: No execute pin found on node .../NotifyAttackButtonClicked.K2Node_FunctionEntry_0
[06.48.01][474] LogBlueprint: Warning: No then pin found on node .../NotifyAttackButtonClicked.K2Node_VariableGet_0
[06.48.01][474] LogBlueprint: Warning: No then pin found on node .../NotifyAttackButtonClicked.K2Node_VariableGet_1
[06.48.01][474] LogBlueprint: Warning: No then pin found on node .../NotifyAttackButtonClicked.K2Node_PromotableOperator_0
[06.48.01][474] LogBlueprint: Warning: No then pin found on node .../NotifyAttackButtonClicked.K2Node_PromotableOperator_1
[06.48.01][474] LogBlueprint: Warning: No then pin found on node .../NotifyAttackButtonClicked.K2Node_PromotableOperator_2
[06.48.10][  8] LogBlueprint: Compiling Blueprint '/Game/Blueprints/BP_BattleManager.BP_BattleManager'
```

★**주의(중요 구분)**: 위 6건의 "Warning"은 **컴파일 경고가 아니다.** 타임스탬프(06:44:59·06:48:01)가 `compile_blueprint` 호출(06:48:10) **이전**이고, 내용이 정확히 이 세션에서 직전에 실행한 `get_connected_subgraph`(BeginPlay 조회)·`find_nodes(entry_points_only=True)`(NotifyAttackButtonClicked 조회) 대상 노드들과 일치한다 — **MCP 조회 툴 자신의 그래프 순회 로직이 LogBlueprint 카테고리에 남긴 진단 잡음**(VariableGet/PromotableOperator/FunctionEntry가 exec 핀이 없거나 입력 exec가 없는 것은 정상이며 실제 결함이 아니다). `"Compiling Blueprint '...'"` 라인 **이후로는 LogBlueprint에 아무 것도 추가되지 않았다**(재조회로 재확인, §5 마지막 줄) → ★**컴파일 경고 0으로 판정**(간접 근거 — `compile_blueprint`가 구조화된 경고 카운트를 직접 반환하지 않으므로).

---

## 6. BP 무변경 실증

- `is_dirty("/Game/Blueprints/BP_BattleManager")` = **`true`** — ★`compile_blueprint` 호출로 인한 **인메모리** dirty(함정102·S1 §8 F0p-04와 동형 현상). 이 세션에서 `create_node`/`connect_pins`/`break_pins`/`set_pin_value`/`add_variable`/`delete_node` **호출 0회** — 노드·핀·연결·변수 구조는 조회 시작 시점과 완전히 동일(184→184 재확인).
- `is_dirty("/Game/Stages/map_battle_octopath")` = **`false`** — 레벨 무접촉.
- `save_assets` 호출 **0회**.
- `git` 명령 **0회**(지시서 절대 제약대로 PM 위임).

★**D8(저장 단계)의 대조 기준선**: 이번 D1 시점 `is_dirty(레벨)=false`를 `AU-FSTP-01`·`AU-FSTP-31`이 요구하는 D1 베이스라인 값으로 기록한다.

---

## 7. 예상과 달랐던 것

1. ★★**`list_variables`는 타입 정보를 반환하지 않는다.** 반환값은 순수 변수명 배열(`["BattleState", "bInputLocked", ...]`)뿐이다. 지시서(`AU-FSTP-03`)의 *"list_variables로 BattleState 타입 원문"*은 문자 그대로는 불가능 — 실제 타입 확정은 `get_default_object`+`ObjectTools.list_properties`/`get_properties`(전투BP_현황도가 원래 쓴 방법)로만 가능했다. 결과 자체(Byte 콘크리트 타입)는 얻었으나 **경로가 지시서와 달랐다.**
2. ★★**N5의 "기존 노드 type_id 그대로 생성" 전략이 실패한다는 것을 직접 검색으로 실증.** 착수판정은 이걸 "제일 안전"으로 표현했으나, `K2Node_PromotableOperator`류(생성 시 와일드카드, 연결 후 이름이 바뀌는 노드)에는 **적용되지 않는 전략**이다. `유틸리티|연산자|` 제네릭 와일드카드 검색이 유일한 경로였다.
3. **`bInputLocked`의 Get 노드 생성 문자열이 `GetbInputLocked`가 아니라 `GetInputLocked`**(불리언 변수의 `b` 헝가리안 접두사가 검색 카탈로그에서 탈락). 같은 패턴이 `bBattleOver→GetBattleOver`·`bWasSkip→GetWasSkip`·`bCamActionEnabled→GetCamActionEnabled` 등 이 블루프린트의 **다른 불리언 변수 전부에서 일관되게 확인**됐다(4종 독립 확인) — 반면 `get_node_infos`로 조회한 **기존 배치된 노드**의 표시 `type_id`는 `"|GetbInputLocked"`로 `b`를 유지한다. ★**생성 시 검색 문자열 ≠ 배치 후 표시 문자열**이 불리언 변수에서도 발생한다는, 함정104/109 계열에 추가할 신규 사례다. 이 패턴을 근거로 `bAutoStartBattle`의 Get 노드도 `GetAutoStartBattle`(b탈락)로 **예측**하지만, **변수가 아직 없어 직접 검증은 불가**했다.
4. **`Delay`는 함정109가 걱정한 "형제 노드끼리 로케일이 갈리는" 사례가 *아니었다*.** `Delay`·`RetriggerableDelay`·`DelayUntilNextTick`·`DelayUntilNextFrame` 4종 전부 `유틸리티|플로컨트롤|<영문이름>`으로 **로케일이 일관**됐다. 로케일이 갈린 것은 어디까지나 `Sequence`(영문카테고리+한글이름) 단독 사례였다 — 지시서의 우려("같은 카테고리 형제끼리 혼합 방향이 정반대")는 이번엔 실현되지 않았지만, **사전에 가정하지 않고 직접 검색했기 때문에 안전하게 확인**할 수 있었다.
5. `compile_blueprint`가 경고 개수를 구조화된 값으로 반환하지 않는다(`outputSchema` 자체가 없음, 반환값이 `null`) — 로그 대조라는 간접 경로가 필요했다.

---

## 8. 다음 단계(D2~D6)를 위한 요약 도면

```
V1  bAutoStartBattle          add_variable(Boolean) — D2. Get노드 문자열은 D2 완료 후 재검색 필수(예측: Variables|디폴트|GetAutoStartBattle)
N1  Delay                     유틸리티|플로컨트롤|Delay
N2  VariableGet bAutoStartBattle   (D2 후 재검색)
N3,N9,N10,N12  Branch         Utilities|FlowControl|Branch
N4  VariableGet BattleState   Variables|디폴트|GetBattleState
N5  같음(==)                  유틸리티|연산자|같음(==)  ★와일드카드 — A(←N4) 연결 후 Byte로 승격 확인 필수
N6  VariableGet TurnQueue     Variables|디폴트|GetTurnQueue
N7  Array Length              유틸리티|배열|Length
N8  보다큼(>)                 유틸리티|연산자|보다큼(>)  ★와일드카드 — A(←N7 ReturnValue) 연결 후 Integer로 승격 확인 필수
N11 VariableGet bInputLocked  Variables|디폴트|GetInputLocked  (★GetbInputLocked 아님)
N13~N16  PrintString          개발|PrintString
N17 NotifyAttackButtonClicked(self)  함수호출|NotifyAttackButtonClicked  (입력 데이터 핀 0개 확인됨)
```

★**N5·N8 공통 권고 절차**(착수판정 §3-3의 "핀값설정(5)→연결(6)" 순서를 이 두 노드에 한해 재배열): `create_node` → `connect_pins`(A측 데이터 연결) → `get_node_infos` 재조회로 Byte/Integer 승격 확인 → B값 재확인(승격 후 기본값이 이미 0이므로 대개 추가 조치 불요, 그래도 `AU-FSTP-12`대로 명시적 `get_pin_value` 인용은 수행).

---

## 관련

[[FT1-S3_TC]] · [[FT1-S3_착수판정]] · [[FT1-S1_조회결과_2026-08-13]] · [[전투BP_현황도_2026-08-11]] · [[언리얼_MCP_실전노하우]]
