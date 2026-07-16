---
type: qa
project: projectTP
feature: 전투완성
stage: 파트2(SPD 턴 순서)
status: 핵심 게이트 PASS 2026-07-17 00시경 — 41건(GRAPH 17·PIE 11·회귀 9·데이터 4) 중 **10건 Director 직접 실행·전부 PASS**: GRAPH 5/5(P2-G01·G02·G03·G04·G07, 본 문서 §7이 지목한 "서브에이전트 보고 불인정" 5곳 전부)+보너스 2건(P2-G05·G09) + ★★★최강게이트 P2-P01(런타임 spd 8기)+P2-P02·P2-P11. **계획서 ★게이트가 기능에 무감각함(N1, Critical)을 P2-P01로 대체 확인 완료.** 잔여 31건(첫8턴 LOG·23턴 신규원장 P2-R01 등)은 Start 클릭 필요해 아침 오너 확인으로 이월. 상세: [[파트2_SPD_완료]]
updated: 2026-07-17
---

# 파트2 SPD 턴 순서 — TC

> 대상: 승인 계획서 `humble-purring-glacier.md` §파트2 · [[파트1_Start_TC]](ID·컬럼 규약 계승, 게이트 PASS `7743d85`) · [[언리얼_MCP_실전노하우]] §34 (78)~(83) · [[야간F9a_풀회귀_완료]] §2(원장 = 재수집 대상)
> **qa-critic 적대적 검토 산출물 — 검출·TC설계만.** TC 실행=verifier, 게이트 판정=Director.
> 본 문서의 모든 "실측" 표기는 **2026-07-16 라이브 에디터 직접 조회**(`find_nodes`/`get_node_infos`/`get_properties`/`find_node_types` + uasset 바이너리 grep) 결과다. 계획서 주장 **5건을 정정**한다.
#projectTP/전투완성

---

## 0. 범위 & 판정도구

**판정도구 약칭**(파트1 계승): **GRAPH**=정적 노드조회(`find_nodes(title="")`+`get_node_infos`) / **PIE**=인스턴스 프로퍼티(`get_properties`, `UEDPIE_0`) / **LOG**=`projectTP.log` grep / **파일**=디스크 grep·mtime / **CMP**=컴파일0 / **오너**=육안(불차단).
**★**=게이트 / **★★**=최우선 / **★★★**=최강.

> ⚠ MCP 호출 형식은 §34 (78) 준수: `call_tool(toolset_name="editor_toolset.toolsets.blueprint.BlueprintTools", tool_name="find_nodes", arguments={"graph":{"refPath":"..."}, "title":""})` — **tool_name에 접두어 금지, 객체 인자는 `{refPath}` dict**.
> ⚠ `read_graph_dsl`은 이 환경에서 빈 문자열 반환 → 전 GRAPH TC는 `find_nodes`+`get_node_infos`로만 판정(파트1 계승).
> ⚠ PIE 액터 refPath는 `/Game/Stages/UEDPIE_0_map_battle_octopath.map_battle_octopath:PersistentLevel.BP_BattleSpawnPoint_C_#`.

**총 41건** — GRAPH 17 · PIE 11 · 회귀 9 · 데이터/레벨 4.

---

## 1. 착수 전 실측 기준선 (본 문서가 확정 — 인용 시 이 값 기준)

계획서 주장을 라이브 조회로 검증. **정정 5건 포함.**

| 항목 | 계획서 주장 | 실측 | 판정 |
|---|---|---|---|
| `BreakStruct_0` = `BreakFJobStatsRow`, `Spd` = 출력핀 **idx 7**, `connected_pins==[]` | idx7·미배선 | **정확히 일치** (핀명 `Spd_19_B9186D6E42EBC590B5CC469E61017217`) | ✅ 일치 |
| `SetDef` = `VariableSet_12`, `.then → DynamicCast_2` | 일치 | **일치** (`DynamicCast_2`=`CastToWBP_UnitFrame`) | ✅ 일치 |
| `SortIntegerArray` 실존 | §34(79) 정정대로 실존 | **`유틸리티\|배열\|정렬\|SortIntegerArray` 실존** | ✅ **(79) 재확인** |
| `SelectInt` 실존 | 암묵 전제 | **`수학\|인티저\|SelectInt` 실존** | ✅ 확인 |
| `SetTurnQueue` = 프로젝트 최초 | "프로젝트 최초의 SetTurnQueue" | **uasset grep `SetTurnQueue`==0** | ✅ 일치 |
| DT 폴백값 | 전사 10 · 마법사 12 | **`job_stats.csv`: warrior_g2 Spd=10 / mage_g2 Spd=12** | ✅ 일치 |
| §(A) 레이스 전제(`RegisterUnitReady`가 DT 로드보다 앞) | 앞에 있음 | **일치** — BeginPlay 체인: …→`MacroInstance_5(IsValid ManagerRef)`→**`CallFunction_42(RegisterUnitReady)`**→…→`GetDataTableRow_0`→`SetHp/MaxHp/Atk/Def`→`DynamicCast_2` | ✅ **전제 확증** |
| **DT 폴백 시 순서** | "4-way 동률 ×2 → **매 전투 무작위** → 결정론 소멸" | **오진.** 키에 `(99-Idx)`가 박혀 동률이 원리상 불가 → **완전 결정론** ∧ 결과가 **목표 순서와 바이트 일치** | ❌ **정정(N1, Critical)** |
| **`×10` 오타 실패 모드** | "키 충돌 → 중복·누락 → **길이 8 그대로라 조용히 통과**" | **오진.** 키 저2자리 전부 상이(충돌 0) → 디코드 인덱스 8개 중 **7개가 OOB** → **런타임 에러 7건 + None×7**(시끄럽다) | ❌ **정정(N4, High)** |
| **`TurnQueue` 출처** | (청사진 L21 "큐 = 등록 순서") | **오진.** `Add`/`Set` **프로젝트 전역 0개** → **레벨 인스턴스 손배치 배열**. `RegisterUnitReady`는 **유닛 인자조차 없다**(카운터만 +1) | ❌ **정정(N5, Medium)** |
| `StartBattle` 구조 | (미기술) | **2노드**: `FunctionEntry_0.then → CallFunction_0(EnterTurnStart)`. **`CallFunction_0.then` = 유일한 빈 exec 핀** | ❌ **오삽입 함정(N2, High)** |
| `InitBattle` compact 대상 | "compact" | **`ReverseForEachLoop(TurnQueue)`→`IsValid`→`Is Not Valid`→`RemoveIndex`** = **None만 제거. 사망 유닛은 액터로 유효하므로 제거 0** | ✅ 재전투 무해 확증 |
| `InitBattle` 길이 가드 | (미기술) | `IfThenElse_0` = `Equal(Integer)(Length(TurnQueue), **0**)` → then=PrintString **`"Init ERROR: TurnQueue length is 0 after compact - battle halted"`**→종단 / else=`ForEachLoop`→`ResetForBattle` | 🔑 N4 보조 |
| `DynamicCast_2.execute` 입력 | (단일 경로 전제) | **exec 소스 2개** — `VariableSet_12(SetDef).then`(RowFound) **및** `CallFunction_5(PrintString "JobId lookup failed in DT_JobStats").then`(RowNotFound) | ❌ **머지점(N3, High)** |
| `ResetForBattle` | (미기술) | `SetHp(MaxHp)`·`SetbAlive(true)`·`SetbBlockActive(false)`·`SetBlockValue(0)` + 배열 Clear. **DT 로드 0 · Spd 접촉 0** | ✅ 멱등 전제 충족 |
| `EnterTurnStart` 소비 | (미기술) | `SetActiveUnit(**GetArrayItem(TurnQueue, CurrentIndex)**)` — `Utilities\|Array\|Get(사본)` | 🔑 G01 근거 |
| `Spd`/`SpdOverride` 기존 존재 | 신규 | **둘 다 없음** 확인(`list_properties`) | ✅ 신규 확정 |

### 레벨 실측 — `BP_BattleManager_C_0.TurnQueue` (손배치 8기)

| 큐 idx | 액터 | 유닛 | `jobId` | 직업 | `bIsParty` | DT Spd | 배정 `SpdOverride` |
|---|---|---|---|---|---|---|---|
| 0 | `BP_BattleSpawnPoint_C_0` | A1 | 10102000 | 전사 g2 | true | **10** | **93** |
| 1 | `_C_4` | B1 | 10102000 | 전사 g2 | false | **10** | **92** |
| 2 | `_C_9` | A2 | 10102000 | 전사 g2 | true | **10** | **91** |
| 3 | `_C_5` | B2 | 10102000 | 전사 g2 | false | **10** | **90** |
| 4 | `_C_2` | A3 | 10202000 | 마법사 g2 | true | **12** | **97** |
| 5 | `_C_6` | B3 | 10202000 | 마법사 g2 | false | **12** | **96** |
| 6 | `_C_3` | A4 | 10202000 | 마법사 g2 | true | **12** | **95** |
| 7 | `_C_7` | B4 | 10202000 | 마법사 g2 | false | **12** | **94** |

액터↔유닛 매핑은 **계획서와 100% 일치**. 현재 큐 = `[A1,B1,A2,B2,A3,B3,A4,B4]` — 계획서 서술과 일치.

### 정답지 산술 (본 문서가 계산 — 기대값의 근거)

키 = `Spd*100 + (99-Idx)`, `SortIntegerArray(Descending)`, 디코드 = `TurnQueue[99 - (Key%100)]`.

| 시나리오 | 키(큐 순) | 정렬 후 순서 | 판정 |
|---|---|---|---|
| **설계(SpdOverride 적용)** | 9399, 9298, 9197, 9096, 9795, 9694, 9593, 9492 | **`[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]`** | 목표 ✅ |
| **DT 폴백(SpdOverride 전부 미적용)** | 1099, 1098, 1097, 1096, 1295, 1294, 1293, 1292 | **`[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]`** | 🚨 **목표와 바이트 일치 → 전 행동 TC 통과** (N1) |
| **Spd 전부 0**(SetSpd 死경로) | 99, 98, 97, 96, 95, 94, 93, 92 | `[C_0,C_4,C_9,C_5,C_2,C_6,C_3,C_7]` = 레벨 원본 | 순서 TC로 탐지 가능 ✅ |
| **1기만 미적용**(예 A4=`_C_3`) | …, C_3=1293 | `[C_2,C_6,C_7,C_0,C_4,C_9,C_5,**C_3**]` | 순서 TC로 탐지 가능 ✅ |
| **재전투 재정렬**(입력=이미 정렬된 큐) | 9799, 9698, 9597, 9496, 9395, 9294, 9193, 9092 | `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]` **동일** | **멱등 확정** ✅ |
| **`×10` 오타** | 1029, 1018, 1007, 996, 1065, 1054, 1043, 1032 | 디코드 idx = 70,81,92,**3**,34,45,56,67 → **7/8 OOB** → `[None×7, C_5]` | 에러 7건(시끄러움) + 재전투 시 길이 8→1 (N4) |

---

## 2. GRAPH 정적 (P2-G##) — 17건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P2-G01** | **★★** | **정렬이 `EnterTurnStart`의 exec 상류** — ⚠**"StartBattle에 있다"로 판정 금지** | GRAPH exec 트레이스 `StartBattle` | `FunctionEntry_0.then` → **`SortTurnQueueBySpd()`** → `CallFunction_0(EnterTurnStart)`. 즉 정렬이 `CallFunction_0`보다 **exec 상류** ∧ `CallFunction_0.then.connected_pins == []`(종단 유지) | **N2(High)** — 실측상 `CallFunction_0.then`이 **StartBattle의 유일한 빈 exec 핀** = "배선하라"는 지시에 가장 자연스러운 부착점. 거기 붙이면 `EnterTurnStart`가 **미정렬** `TurnQueue[0]`=`C_0`를 ActiveUnit에 캐시 → 1턴 A1 → A1 중복·A3 누락. **계획서 게이트 "정렬이 StartBattle에"는 이 오배선을 통과시킨다** → ✅**PASS**(2026-07-17 00시경, Director 직접 핀조회로 exec 상류성 확인. 상세: [[파트2_SPD_완료]] §2) |
| **P2-G02** | ★ | **키 인코딩 곱수 == 100** — **★Director 직접 핀 원문 조회** | GRAPH `get_node_infos` 곱셈 노드 | `SortKeys.Add`의 입력 체인에 `수학\|인티저\|곱하기`(또는 `PromotableOperator`로 승격된 `*`) ∧ 상수 피연산자 == **`100`**(≠10, ≠1000) | 계획서 ★게이트. ⚠**실패 모드 정정**: 계획서의 "키 충돌→무음 중복"은 **오진**(N4) — 실제는 OOB 에러 7건. TC 자체는 유효하므로 존치 → ✅**PASS**(2026-07-17 00시경, Director 직접 핀조회 — `B value="100"` 확인. [[파트2_SPD_완료]] §2) |
| **P2-G03** | ★ | **`SetTurnQueue`가 디코드 ForEach의 `Completed` 핀** — **★Director 직접** | GRAPH exec 트레이스 | 디코드 `ForEachLoop`의 **`Completed`** → `SetTurnQueue` ∧ **`LoopBody` 하류에 `SetTurnQueue` 없음** | 계획서 ★게이트 — LoopBody에 있으면 원본을 읽는 중 파괴 → ✅**PASS**(2026-07-17 00시경, Director 직접 핀조회 — `Completed`(idx3)→`VariableSet_0` 확인. [[파트2_SPD_완료]] §2) |
| **P2-G04** | ★ | **정렬이 `StartBattle`에, `InitBattle`엔 없다** — **★Director 직접** | GRAPH ×2 | `StartBattle`에 `SortTurnQueueBySpd` 호출 **1개** ∧ `InitBattle`에 **0개** ∧ 프로젝트 전역 호출처 **정확히 1곳** | 계획서 §(A) — `InitBattle`에 있으면 8번째 유닛 Spd=0 레이스 부활 → ✅**PASS**(2026-07-17 00시경, Director 직접 — `find_nodes(InitBattle,"Sort")`=0건 확인. [[파트2_SPD_완료]] §2) |
| **P2-G05** | ★ | **`Random*` 노드 0개**(死코드 금지) | GRAPH `find_nodes(SortTurnQueueBySpd, title="Random")` | `SortTurnQueueBySpd` 그래프에 `Random*` **0개** ∧ `Shuffle` **0개** | 오너 결정 4. ⚠**근거 정정**: 死코드인 이유는 "8기 SPD 상이"가 **아니라** 키에 `(99-Idx)`가 박혀 **동률이 원리상 SortIntegerArray에 도달 불가**하기 때문(N7) — SPD를 나중에 같게 만들어도 여전히 死코드 → ✅**PASS**(2026-07-17 00시경, `find_nodes(SortTurnQueueBySpd,"Random")`=0건 확인. [[파트2_SPD_완료]] §2·§8) |
| **P2-G06** | ★ | **`SetSpd` 삽입 위치**(작업2) | GRAPH exec 트레이스 | `VariableSet_11(SetAtk).then` → `VariableSet_12(SetDef)` → **`SetSpd`** → `DynamicCast_2.execute`. ∧ `CallFunction_5(RowNotFound PrintString).then → DynamicCast_2` **연결 유지**(무손상) | 작업2 · **N3(High)** — `DynamicCast_2.execute`는 **exec 소스 2개**(RowFound/RowNotFound)를 받는 머지점. SetSpd는 `BreakStruct_0`를 읽으므로 **RowFound 경로에만** 놓일 수밖에 없다(설계는 옳음). RowNotFound 경로는 P2-P04가 커버 |
| **P2-G07** | **★★** | **`SelectInt` 배선 극성** — 무음 실패 3종의 원천 | GRAPH `get_node_infos` | `SelectInt`: **`A` ← `GetSpdOverride`** ∧ **`B` ← `BreakStruct_0` 출력핀 `index_id==7`**(`Spd_19_…`) ∧ **`bPickA` ← `보다큼(>)`(A=`GetSpdOverride`, B=리터럴 `0`)**. ⚠ A/B 뒤바뀜·조건 반전(`<`,`<=`,`>=`) 전부 FAIL | **N6(Medium)** — (a)A/B 뒤바뀜 (b)조건 반전 (c)인스턴스값 미전파 **셋 다 "항상 DT 폴백"으로 귀결** → **순서가 목표와 완전 일치**해 모든 행동 TC 통과(N1). **GRAPH+P2-P01만이 탐지 수단** → ✅**PASS**(2026-07-17 00시경, Director 직접 핀조회 — A←SpdOverride, B←BreakStruct_0 idx7, bPickA←`>`(A=SpdOverride,B=0) 3항 전부 정극성 확인. [[파트2_SPD_완료]] §2) |
| **P2-G08** | ★ | **인코드/디코드 대칭** — `(99-Idx)` ↔ `99-(Key%100)` | GRAPH | 인코드 tiebreak == `빼기(A=99, B=ArrayIndex)` ∧ 디코드 == `빼기(A=99, B=Modulo(Key, **100**))`. **두 `99`와 두 `100`이 각각 동일 리터럴** | 계획서 정렬 의사코드 · 비대칭 시 전부 OOB |
| **P2-G09** | ★ | **`SortIntegerArray` 파라미터** | GRAPH | `유틸리티\|배열\|정렬\|SortIntegerArray` **1개** ∧ `TargetArray` ← `GetSortKeys` ∧ **`bStableSort==true`** ∧ **`SortOrder=="Descending"`** | 계획서 작업4. ⚠ §34 (80): 프로모터블 승격은 **배선 후 `get_node_infos`로만** 확인 → ✅**PASS**(부분 — 2026-07-17 00시경 `bStableSort="true"`·`SortOrder="Descending"` 확인. `TargetArray`←`GetSortKeys` 소스 자체는 미기재. [[파트2_SPD_완료]] §2) |
| **P2-G10** | | **`Clear` 2개**(재진입 안전) | GRAPH | 함수 선두에 `Clear(SortKeys)` ∧ `Clear(SortedQueue)` 각 1개, **`SortIntegerArray`·`Add`보다 exec 상류** | 계획서 작업4 — 멤버 변수일 경우 필수, 로컬이면 무해. 재전투 누적 방지 |
| **P2-G11** | ★ | **`SetSpd` 프로젝트 전역 정확히 1개** — 멱등 전제 | GRAPH 전역 | `BP_BattleSpawnPoint` 전 그래프에서 `SetSpd` 노드 **정확히 1개**(BeginPlay 체인) ∧ `ResetForBattle`에 **0개** | **N8(Medium)** — 멱등성 전제(a). 2곳 이상이면 재전투마다 Spd가 바뀔 수 있어 정렬 결정론 붕괴. 실측: `ResetForBattle`은 DT 로드가 없어 현재 구조상 안전 |
| **P2-G12** | ★ | **디코드가 원본 `TurnQueue`를 읽음** | GRAPH | 디코드 `GetArrayItem`의 `Array` ← **`GetTurnQueue`**(≠`GetSortedQueue`, ≠`GetSortKeys`) | 계획서 작업4 — `SortedQueue`를 읽으면 자기참조로 빈 배열/None |
| **P2-G13** | | **정렬이 `ActiveUnit`·`CurrentIndex` 무접촉** | GRAPH | `SortTurnQueueBySpd`에 `ActiveUnit`·`CurrentIndex`·`TurnCounter`·`BattleState` **Get/Set 0개** | Director 질의(stale ActiveUnit 상호작용) — 정렬은 큐 **내용**만 바꾼다. P2-G01이 성립하면 stale은 `EnterTurnStart`가 즉시 덮음 |
| **P2-G14** | ★ | **컴파일 0** | CMP | `BP_BattleSpawnPoint`·`BP_BattleManager` 컴파일 **에러 0 · 경고 0**(신규분) | 표준 |
| **P2-G15** | ★ | **파트2 편집 범위 봉인** | GRAPH diff | 편집 대상은 **정확히**: `BP_BattleSpawnPoint`(변수 `Spd`·`SpdOverride` 신설, EventGraph `SetSpd` 1노드+SelectInt 서브그래프) + `BP_BattleManager`(`SortTurnQueueBySpd` 신설, `StartBattle` 배선 1개) + 레벨 8기 `SpdOverride`. **그 외 0** — 특히 `ResolveHit`·`GetOutgoingAtkMult`·`ApplySkillEffects`·`TickStatusesAtTurnEnd`·`EnterTurnStart` **본체 diff 0** | 파트1 P1-G20 계승 · P2-R01 원장 재수집의 구조적 근거 |
| **P2-G16** | | **`SpdOverride` 소비처 1곳** | GRAPH 전역 | `GetSpdOverride` 참조가 **`SelectInt.A` + `보다큼(>).A` 2개뿐** ∧ `SetSpdOverride` 노드 **0개**(= 레벨 인스턴스 지정값) | N6 보조 — 세터가 생기면 인스턴스 값이 런타임에 덮여 무의미 |
| **P2-G17** | | **`SortKeys`/`SortedQueue` 타입·스코프** | GRAPH | 둘 다 **인티저 배열 / BP Battle Spawn Point 오브젝트 레퍼런스 배열** ∧ 계획서대로 **로컬(graph 파라미터)** 우선. 멤버일 경우 P2-G10 필수 | 계획서 작업4 주석 |

---

## 3. PIE 런타임 (P2-P##) — 11건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P2-P01** | **★★★** | **런타임 `Spd` 8기 실값** — 🚨**파트2의 유일한 진짜 게이트** | PIE 프로퍼티 `get_properties(UEDPIE_0 액터, ["spd","spdOverride"])` ×8 | PIE 진입 후(**State 0 대기 중에 읽어도 됨** — Spd는 BeginPlay 확정) `spd` == **`_C_0`:93 / `_C_4`:92 / `_C_9`:91 / `_C_5`:90 / `_C_2`:97 / `_C_6`:96 / `_C_3`:95 / `_C_7`:94`**. ⚠**`spd`가 10/12면 즉시 FAIL**(= DT 폴백 = 기능 미작동) | **N1(Critical)** — 계획서의 ★게이트("SpdOverride 전부 ≠0∧상이", "첫 8턴 == […]")는 **작업1~3을 전혀 안 해도 전부 PASS**한다. DT 폴백(전사10·마법사12)이 목표 순서와 **바이트 일치**하기 때문(§1 정답지 산술). **런타임 `spd` 직접 조회만이 탐지 수단.** 파트1이 만든 State 0 무한 대기창 덕에 저비용 → ✅**PASS**(2026-07-17 00시경, Director 직접 PIE 조회 — `_C_0`:93/`_C_4`:92/`_C_9`:91/`_C_5`:90/`_C_2`:97/`_C_6`:96/`_C_3`:95/`_C_7`:94, 8기 전부 목표값과 일치·전부 상이·DT 폴백값(10/12) 아님 확인. **파트2 최강 게이트 통과.** 상세: [[파트2_SPD_완료]] §3) |
| **P2-P02** | ★ | **`SpdOverride` 8기 ≠0 ∧ 전부 상이** | PIE 프로퍼티 ×8 | `spdOverride` == {93,92,91,90,97,96,95,94} ∧ 8개 전부 **≠0** ∧ 전부 **상이** | 계획서 ★게이트. ⚠**이 PASS는 기능 작동을 증명하지 않는다**(입력값일 뿐) — **P2-P01이 유일 증명**. 둘 다 필요 → ✅**PASS**(2026-07-17 00시경, P2-P01과 동일 조회로 `spdOverride` {93,92,91,90,97,96,95,94} 확인. [[파트2_SPD_완료]] §3) |
| **P2-P03** | **★★** | **`StartBattle` 직후 `TurnQueue` 실배열** | PIE 프로퍼티 `get_properties(Manager, ["TurnQueue"])` | Start 클릭 직후 `TurnQueue` == **`[_C_2, _C_6, _C_3, _C_7, _C_0, _C_4, _C_9, _C_5]`**(순서 포함 완전 일치) ∧ `None` 원소 **0개** | 계획서 게이트 정밀화 — 8턴 관측(P2-P04)보다 **싸고 강하다**(1콜, 사망 스킵 간섭 없음). ⚠ 단 N1 때문에 **이것만으로 SpdOverride 적용을 증명 못 함** |
| **P2-P04** | ★ | **첫 8턴 ActiveUnit 순서 + 전부 상이** | LOG `BattleLog\|` grep + PIE | 첫 8유닛턴의 ActiveUnit == `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]` ∧ **8개 전부 상이**(중복 0·누락 0) | 계획서 ★게이트. ⚠**FAIL 시 원인 분리**: 계획서는 이 FAIL을 "키 인코딩 오배선"으로 규정하나 **P2-G01 오배선(정렬이 EnterTurnStart 뒤)도 동일 증상**(A1 중복·A3 누락) → **G01·G02를 먼저 본다** |
| **P2-P05** | ★ | **`JobId lookup failed` 0건** — SetSpd 우회 경로 | LOG grep | `"JobId lookup failed in DT_JobStats"` **0건** | **N3(High)** — RowNotFound 시 `SetSpd`가 통째로 우회되어 그 유닛 `Spd=0`(SpdOverride조차 무시) → 큐 최후미로 밀림. 기존 PrintString이 있어 **무음은 아님** → grep 0건으로 봉인 |
| **P2-P06** | ★ | **PIE 재시작 ×3 순서 동일** — §(A) 레이스 검출 | PIE ×3 | PIE 재시작 3회, 각 회차 Start 후 `TurnQueue` == `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]` **3회 전부 동일** ∧ `spd` 8기 값도 3회 동일 | 계획서 §(A). **보강**: 실측상 큐 자체가 레벨 손배치라 **등록 순서에 의존하지 않는다**(N5) → 레이스는 `Spd` 값에만 영향. 그래서 **순서뿐 아니라 `spd`도 3회 비교**해야 검출력이 생긴다 |
| **P2-P07** | ★ | **에러·경고 0** — OOB/None/Modulo | LOG grep | `"out of bounds"` **0건** ∧ `"Modulo by zero"` **0건** ∧ 한국어 로케일 **`"None에 액세스"` 0건** ∧ `Attempted to (get\|access)` 0건 | **N4(High)** — `×10`(또는 인코드/디코드 비대칭) 시 디코드 인덱스 8개 중 **7개 OOB** → 각각 BP 런타임 에러 + None. 계획서가 "무음"이라 본 것과 정반대로 **가장 시끄러운 신호** |
| **P2-P08** | ★ | **큐 길이 불변 8** (H2) | PIE 프로퍼티 ×4 시점 | `Length(TurnQueue) == 8` — ① Start 전(State 0) ② Start 직후 ③ 전투 중(임의 턴) ④ State 6(End) | 계획서 H2 |
| **P2-P09** | ★ | **첫 전투 == 재전투**(멱등) | PIE | End→Start 재전투 후 `TurnQueue` == 첫 전투와 **동일 배열** ∧ 첫 8턴 순서 동일 | Director 질의(멱등성). **산술 확정**: 재정렬 입력=이미 정렬된 큐 → 키 9799…9092 → 디코드 0..7 → **불변**(§1). **멱등의 의존처 3가지**: (a) `Spd` 불변(P2-G11·P2-R06) (b) 디코드가 원본 읽고 `SetTurnQueue`가 Completed에(P2-G03·G12) (c) 키 저2자리↔인덱스 1:1(P2-G08) |
| **P2-P10** | | **stale `ActiveUnit` 무해** | PIE | State 0(대기)에서 `ActiveUnit` = 직전 전투 잔재여도, Start 후 첫 턴 `ActiveUnit == _C_2`(A3) | Director 질의. 파트1 TC §1 "소비처 0 + EnterTurnStart 즉시 재세팅" 계승. **P2-G01 성립이 전제** |
| **P2-P11** | | **State 0에서 정렬 미실행** | PIE | PIE 진입 후 Start **누르기 전** `TurnQueue` == 레벨 원본 `[_C_0,_C_4,_C_9,_C_5,_C_2,_C_6,_C_3,_C_7]` | **N5** 보강 — 정렬이 `InitBattle`에 잘못 들어갔으면 대기 중 이미 정렬돼 있다 → **P2-G04의 런타임 교차검증** → ✅**PASS**(2026-07-17 00시경, Start 클릭 전 `TurnQueue==[C_0,C_4,C_9,C_5,C_2,C_6,C_3,C_7]`(레벨 원본, 미정렬) 확인 — 파트1 대기상태 재확인과 동시 획득. [[파트2_SPD_완료]] §4) |

---

## 4. 회귀 (P2-R##) — 9건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P2-R01** | **★★★** | **신규 원장 재수집 = 새 기준선** — 파트1 이월분 흡수 | LOG 원장 수집 | **PIE 1회 관측**(계산 아님)으로 완주 → `Saved/BattleLogs/battle_<시각>.log` 확보 → 이후 기준선으로 봉인. ⚠**절차**: ①**에디터 재시작으로 `projectTP.log` 롤오버**(또는 **마지막 `turn=1`부터 끝까지만** 취급 — 스크립트가 최신 로그를 **통째로** 긁는데 전투 구분자가 없고 현재 로그엔 오너 테스트분이 이미 섞여 있다) ② PIE 완주 ③ `cd D:\unreal\Resource\docs\scripts && python extract_battle_log.py` | 계획서 §회귀 파급. ⚠ `extract_battle_log.py`는 **런타임 기록기가 아니라 수동 사후 추출 도구**(BP에 파일쓰기 노드 없음 → "엔진 로그에 구조화 라인 + 사후 추출" 2단 설계). **[[파트1_Start_TC]] P1-R01(23턴 diff-0)이 파트2로 이월**됐으므로 본 TC가 그 종착점 |
| **P2-R02** | ★ | **F8 게이트 표 기대값 갱신** | LOG 원장 판독 | **신규 원장에서 `turn40`의 실제 행위자를 읽어** 기대 데미지 갱신(전사 50 / 마법사 53). ⚠**단순 modulo 역산 금지** — 사망 스킵 시 `TurnCounter`는 안 오르고 `CurrentIndex`는 오르므로 `turn % 8`로 유닛을 특정할 수 없다 | 계획서 §회귀 파급. 미갱신 시 이 FAIL이 *광폭화 공식 붕괴*처럼 보인다 |
| **P2-R03** | ★ | **큐 길이 영구 붕괴 없음** — N4 2차 피해 | PIE 재전투 ×2 | 재전투 2회 후 `Length(TurnQueue) == 8` ∧ `None` 원소 0개 | **N4(High) 2차** — 정렬이 큐에 None을 남기면 **다음 `InitBattle`의 compact가 None을 실제로 제거** → 길이 영구 축소(레벨 값 재로드 = PIE 재시작뿐). 게다가 기존 가드는 `Length==**0**`만 잡아 **길이 1은 통과**한다 → "Init ERROR: TurnQueue length is 0" grep만으론 불충분 |
| **P2-R04** | ★ | 🚨 **`QA-H4`/`TC-16` 보존**(갱신 대상 아님) | 문서 + GRAPH | `QA-H4`/`TC-16`의 *"순서 고정"* = **노드 실행 순서**(마커 OFF → 인덱스 증가)이지 턴 순서가 아니다. 정렬은 큐 **내용**만 바꾼다 → **원문 무수정 존치** ∧ `EnterTurnEnd`의 마커OFF↔인덱스증가 순서 **diff 0** | 계획서 §회귀 파급(v1이 "파트2가 위반"으로 잘못 지시했다가 정정). **살아있는 안전 불변식** — 삭제 금지 |
| **P2-R05** | ★ | **파트1 무접촉** | GRAPH + PIE | `ShowStart`/`ShowCancel`/`ShowEnd`/`HideAll` 4함수 **diff 0** ∧ `NotifyAttackButtonClicked` Start 분기 **diff 0** ∧ `InitBattle` 꼬리 **diff 0** ∧ P1-P01~P11 재통과 | 파트1 게이트 PASS(`7743d85`) 보호 |
| **P2-R06** | ★ | **`ResetForBattle`이 `Spd` 미접촉** — 멱등 전제(a) | GRAPH | `ResetForBattle`에 `SetSpd` **0개** ∧ `GetDataTableRow` **0개** ∧ 기존 4세터(`SetHp(MaxHp)`·`SetbAlive(true)`·`SetbBlockActive(false)`·`SetBlockValue(0)`) **diff 0** | **N8** — 실측상 현재 안전. 파트2가 여기 DT 재로드를 넣으면 **재전투마다 Spd가 DT로 되돌아가 멱등 붕괴**(그리고 N1 때문에 **순서로는 안 보인다**) |
| **P2-R07** | | **스캐폴드 규약 추가** | 문서 | `전투완성/plan.md` L258 · `F4_TC` 스캐폴드 규약에 **"TurnQueue 인덱스 리터럴 금지"** 1행 추가(같은 커밋) | 계획서 §회귀 파급 — 정렬 후 큐 인덱스는 유닛을 식별하지 않는다 |
| **P2-R08** | | **H-1 회귀**(사망 스킵) | LOG | 신규 원장에서 `SKIP_TURN_DEATH` 방출 시 **`TurnCounter` 불변** | 계획서 §게이트 LOG |
| **P2-R09** | | **문서 정정 3건** | 문서 | ① `청사진.md` L21 **"큐 = 등록 순서"** → **"큐 = 레벨 인스턴스 손배치 배열(`BP_BattleManager_C_0.TurnQueue`), 실제 행동 순서는 StartBattle 정렬 후"**(N5 — 계획서는 "정렬 후"만 고치라 했으나 **애초에 등록 순서가 아니었다**) ② `TC.md` TC-11 분해(11a=레벨 배열 원본 / 11b=StartBattle 후 정렬 순서) ③ §34에 N1·N2·N4 등재 | 계획서 §부채 정리 3 + **N5(Medium)** |

---

## 5. 데이터·레벨 (P2-D##) — 4건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P2-D01** | ★ | **8기 `SpdOverride` 디스크 저장**(OFPA) | 파일 grep + mtime | `save_actor` 후 8개 OFPA `.uasset`(`__ExternalActors__/`) **mtime 갱신** ∧ 바이너리 grep `SpdOverride` ≥1. ⚠**API 반환값 신뢰 금지** — 디스크로만 판정 | 계획서 작업3 · §34 (81)(82) — "저장 성공은 mtime·바이너리 grep으로만" |
| **P2-D02** | ★ | **재컴파일 후 8기 값 재확인** — 함정(54) | PIE 프로퍼티 ×8 | `compile_blueprint(BP_BattleSpawnPoint)` **후** 8기 `spdOverride`가 여전히 {93,92,91,90,97,96,95,94}. ⚠ 2회 재컴파일 발생 시 **매번 재확인** | 계획서 작업3 ⚠ · **함정(54) 이 프로젝트에서 2회 재현**([[야간④_End버튼_완료]] §3-②) — 무효화 시 8기 전부 0 → **DT 폴백 → 순서는 정상 → 무음**(N1). **P2-P01이 최종 안전망** |
| **P2-D03** | ★ | **변수 스펙** | GRAPH/프로퍼티 | `Spd`: 인티저, **Instance Editable 불요**, 기본 0 / `SpdOverride`: 인티저, **Instance Editable = true**, 기본 **0**. 둘 다 `BP_BattleSpawnPoint` 멤버 | 계획서 작업1. **Director 질의 답(N8)**: `Spd`는 **멤버가 맞다** — `SortTurnQueueBySpd`가 Manager에서 돌며 `TurnQueue` 원소(SpawnPoint)의 Spd를 **크로스-액터로 읽어야** 하므로 로컬 변수로는 원리상 불가 |
| **P2-D04** | | **레벨 `TurnQueue` 배열 불변** | 프로퍼티(에디터, 非PIE) | 작업 전후 `BP_BattleManager_C_0.TurnQueue` == `[_C_0,_C_4,_C_9,_C_5,_C_2,_C_6,_C_3,_C_7]` **불변** | **N5** — 파트2는 큐 **내용**을 런타임에만 바꾼다. 레벨 원본을 건드리면 P2-P11·P2-P06의 기준이 무너진다 |

---

## 6. 신규 발견 — 계획서에 없던 것 (8건)

> 심각도순. **CONFIRMED**=라이브 조회/산술로 확정 / **PLAUSIBLE**=논리상 의심, 실측 필요.

### Critical

- **N1 — DT 폴백이 목표 순서와 100% 동일 → 계획서 ★게이트가 기능에 무감각** `CONFIRMED`
  계획서: *"`SpdOverride` 미적용 → 조용히 DT 폴백 → **4-way 동률 ×2** → 매 전투 순서 무작위 → 결정론 소멸"*. **틀렸다.**
  키가 `Spd*100 + (99-Idx)`이므로 **동률은 원리상 `SortIntegerArray`에 도달하지 못한다** — 정렬 입력은 **언제나 8개 상이 정수**다. 따라서 DT 폴백은 무작위가 아니라 **완전 결정론**이며, 산술상 결과가 목표와 **바이트 일치**한다:
  - 폴백 키: 전사(idx0~3)=`10*100+(99-i)` = 1099,1098,1097,1096 / 마법사(idx4~7)=`12*100+(99-i)` = 1295,1294,1293,1292
  - 내림차순 → 디코드 `99-(k%100)` → `4,5,6,7,0,1,2,3` → **`[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]`** = 설계 목표와 동일
  **원인**: 오너의 SPD 배정 규칙(*"마법사 12 > 전사 10 성향 일관 → 그 안에서는 현재 큐 순서대로 97부터 내림차순"*)이 **DT 폴백 + 인덱스 tiebreak가 계산하는 것과 정의상 같은 함수**다. 계획서 §SPD배정이 스스로 밝힌 그 기준이 곧 폴백 공식이다.
  **귀결**: 작업1(Spd 변수)·작업2(SetSpd 삽입)·작업3(8기 SpdOverride)을 **전부 생략해도** 계획서의 ★PIE 게이트 — "첫 8턴 == `[C_2,…]`", "8턴 전부 상이", "재시작 ×3 동일", "첫 전투 == 재전투" — 가 **전부 PASS**한다. 즉 **행동 TC 전량이 파트2 작업량의 3/4에 대해 무감각**하다.
  → **P2-P01(런타임 `spd` 8기 직접 조회)을 ★★★로 신설.** 계획서의 "SpdOverride 전부 ≠0∧상이"(P2-P02)는 **입력 확인일 뿐 효과를 증명하지 않는다** — 사이에 SelectInt 배선·`>0` 조건·RowFound 경로·함정(54) 전파가 끼어 있다.
  ※ 대칭 확인: `Spd`가 8기 전부 **0**이면(SetSpd가 死경로) 순서 = 레벨 원본 → 순서 TC로 **탐지된다**. **"전부 0"은 잡히고 "전부 DT"는 안 잡힌다** — 하필 더 그럴듯한 쪽이 안 잡힌다.
  → **[해소 — 2026-07-17 00시경]** P2-P01 실행 완료: 런타임 `spd` 8기가 목표값(93/92/91/90/97/96/95/94)과 정확히 일치하고 DT 폴백값(10/12)이 아님을 직접 확인 — **SpdOverride가 실제로 적용됐다는 최초의 긍정 증거**. 이 결과 하나로는 파트2 작업량의 3/4(변수·SetSpd·8기값)가 전부 옳게 동작함까지는 증명하지 못하지만(N6의 3종 무음오배선은 P2-G07로 별도 봉인 완료), 적어도 "DT 폴백으로 조용히 대체됐다"는 이 항목의 핵심 우려는 배제됐다. 상세: [[파트2_SPD_완료]] §3

### High

- **N2 — `StartBattle`의 유일한 빈 exec 핀이 정렬의 오삽입 자리** `CONFIRMED`
  실측 `StartBattle` 전문: `K2Node_FunctionEntry_0.then → K2Node_CallFunction_0(|EnterTurnStart)`, 그리고 **`CallFunction_0.then.connected_pins == []`**. 이 그래프에서 **비어 있는 exec 핀은 그것 하나뿐**이다. *"`SortTurnQueueBySpd()` 신설 → `StartBattle()`에 배선"* 지시를 받은 구현자에게 **가장 자연스러운 부착점이 바로 그 빈 핀**(= append) — 그러면 정렬이 `EnterTurnStart` **뒤**에 실행된다.
  `EnterTurnStart`는 실측상 `SetActiveUnit(GetArrayItem(TurnQueue, CurrentIndex))` — **미정렬** 큐의 `[0]`=`C_0`(A1)을 캐시한다. 이후 정렬된 큐를 인덱스 1..7로 소비 → 첫 8턴 = `[A1, B3, A4, B4, A1, B1, A2, B2]` → **A1 중복·A3 누락**.
  **계획서 게이트 "★정렬이 `StartBattle`에(`InitBattle` 아님)"는 그래프 소속만 보므로 이 오배선을 통과시킨다.** 그리고 P2-P04 FAIL을 계획서는 *"키 인코딩 오배선"*의 신호로 규정해 놔서 **오진을 유도**한다.
  → **P2-G01(★★)**: "StartBattle에 있다"가 아니라 **"`EnterTurnStart`보다 exec 상류"**로 어서션.

- **N3 — `SetSpd` 삽입 지점이 2-소스 머지 노드 바로 앞** `CONFIRMED`
  실측: `DynamicCast_2.execute`의 `connected_pins`에 **2개** — `VariableSet_12(SetDef).then`(RowFound) **및** `CallFunction_5.then`(RowNotFound → `PrintString("JobId lookup failed in DT_JobStats")`). 즉 `GetDataTableRow_0`의 두 갈래가 여기서 합류한다.
  계획서의 *"`SetDef` → `DynamicCast_2` 사이에 `SetSpd` 삽입"*은 RowFound 경로만 덮는다. **설계 자체는 옳다** — `SelectInt.B`가 `BreakStruct_0`(RowFound에서만 유효)를 읽으므로 구조상 그 경로에만 놓일 수 있다. 다만 귀결을 명시해야 한다: **RowNotFound 시 `SpdOverride`까지 무시되고 그 유닛 `Spd=0`** → 큐 최후미.
  다행히 **무음이 아니다**(기존 PrintString). → **P2-P05**: `"JobId lookup failed in DT_JobStats"` **0건** 어서션으로 봉인.
  ※ 부수: `DynamicCast_2.CastFailed`는 **미연결**(기존) — SetSpd를 RowFound 경로에 두면 무관. 기록만.

- **N4 — `×10` 오타의 실제 실패 모드는 "무음 중복"이 아니라 "OOB 에러 폭풍 + 다음 전투 큐 영구 붕괴"** `CONFIRMED`
  계획서: *"`×10` 오타 시 **키 충돌** → 큐에 유닛 **중복·누락**이 생기는데 **길이는 8 그대로라 조용히 통과**"*. 산술상 **틀렸다.**
  `Spd*10 + (99-idx)` → 키 = 1029,1018,1007,996,1065,1054,1043,1032. 저2자리 = 29,18,07,96,65,54,43,32 — **전부 상이. 충돌 0.** 디코드 `99-(k%100)` = **70,81,92,3,34,45,56,67** → **8개 중 7개가 배열 범위(0~7) 밖**.
  `Utilities|Array|Get(사본)`은 OOB에서 **블루프린트 런타임 에러를 찍고 None을 반환**한다 → `SortedQueue` = `[None×7, C_5]` → `SetTurnQueue` → `ActiveUnit=None` → `"None에 액세스"` 연쇄. **가장 시끄러운 실패다.**
  **진짜 위험은 그 다음**: 재전투 시 `InitBattle`의 compact(`ReverseForEachLoop`+`IsValid`+`RemoveIndex`)가 **None 7개를 실제로 제거** → **`TurnQueue` 길이 8→1로 영구 축소**. `TurnQueue`엔 코드 라이터가 없으므로(N5) **레벨 값 재로드 = PIE 재시작 외에 복구 경로가 없다.** 게다가 기존 가드는 `Length == **0**`만 잡으므로(실측: `"Init ERROR: TurnQueue length is 0 after compact - battle halted"`) **길이 1은 조용히 통과**한다.
  → 곱수 TC(P2-G02)는 **유지**(옳다). 단 실패 모드 서술을 정정하고 **P2-P07**(OOB/None grep)·**P2-R03**(길이 붕괴)을 추가.

### Medium

- **N5 — `TurnQueue`는 등록 순서가 아니라 레벨 인스턴스 손배치 배열이다** `CONFIRMED`
  실측: `SetTurnQueue`·`Add`·`AddUnique` **프로젝트 전역 0개**(uasset 바이너리 grep `SetTurnQueue`==0, `TurnQueue` 참조는 **Get 3개 + RemoveIndex의 by-ref**뿐). `RegisterUnitReady`는 **유닛 인자조차 없고** `SetRegisteredCount(+1)` → `Branch(==8)` → `InitBattle()`만 한다.
  `BP_BattleManager_C_0.TurnQueue` = 레벨에 **손으로 꽂은 8개 레퍼런스** = `[C_0,C_4,C_9,C_5,C_2,C_6,C_3,C_7]`.
  → 청사진 L21 *"큐 = 등록 순서"*는 **오진**. 계획서 §부채정리 3은 이걸 *"큐 = 등록 순서, 실제 행동 순서는 StartBattle 정렬 후"*로 고치라 했으나 **이유가 틀렸다** — 애초에 등록 순서가 아니었다.
  **함의 3가지**: ① 큐 순서는 **PIE 재시작에 안정적**(§(A) 레이스는 `Spd` 값에만 영향, 큐 **순서**엔 무관) → P2-P06은 순서뿐 아니라 **`spd`도 3회 비교**해야 검출력이 생긴다. ② 파트2의 `SetTurnQueue`는 **프로젝트 최초의 TurnQueue 라이터**이며 레벨 값을 **런타임 세션 동안 영구 대체**한다. ③ N4의 길이 붕괴가 **왜 영구인지**를 설명한다.

- **N6 — 정렬을 통과하는 무음 오배선 3종** `CONFIRMED`(산술)
  아래 셋은 **턴 순서가 목표와 완전히 일치**해 P2-P03·P04·P06·P09를 **전부 통과**한다:
  (a) `SelectInt`의 **A/B 뒤바뀜**(A=`BreakStruct_0.Spd`, B=`SpdOverride`) → 항상 DT
  (b) **`bPickA` 조건 반전**(`SpdOverride <= 0` / `< 0` / `>= 0`) → 항상 DT
  (c) **`SpdOverride` 인스턴스 값 미전파**(함정(54), 이 프로젝트에서 **2회 재현**) → 8기 전부 0 → 항상 DT
  전부 **N1의 등가류**. 탐지는 **P2-G07(GRAPH 극성) + P2-P01(런타임 `spd`)** 둘뿐.

- **N7 — 死코드 판정의 근거가 계획서보다 강하다** `CONFIRMED`
  오너 결정 4: *"전원 상이면 (동률 랜덤은) 도달 불가 = 死코드"*. **결론은 맞으나 근거가 약하다.**
  실제: 키 `Spd*100 + (99-Idx)`에서 `Idx`가 유일하므로 **SPD가 8기 전부 같아도 키는 상이**하다 → 동률은 `SortIntegerArray`에 **원리상 도달 불가**. 즉 死코드인 이유는 *"8기 SPD가 상이해서"*가 아니라 *"키 설계상 동률이 불가능해서"*다.
  → **실무 함의**: 나중에 SPD를 같게 조정해도 동률 랜덤은 여전히 死코드다(규약 위반 유지). `Random*` 0개 TC(P2-G05)의 근거를 이걸로 교체하면 더 견고. 동시에 이것이 **N1의 근본 원인**이기도 하다 — tiebreak가 결정론을 보장하는 만큼, SPD 값 자체가 순서에 기여하는 정보량이 줄었다.

- **N8 — `Spd`는 멤버가 맞다. 단 Set은 정확히 1곳이어야** `CONFIRMED`
  Director 질의 *"`Spd` 멤버가 정렬 외에 소비처가 없는데 굳이 멤버로 두는 게 맞나"* → **맞다.** `SortTurnQueueBySpd`는 `BP_BattleManager`에서 돌며 `TurnQueue` 각 원소(`BP_BattleSpawnPoint`)의 Spd를 **크로스-액터로 읽어야** 한다 → 멤버 변수(또는 getter)가 **유일한 경로**. 로컬 변수로는 원리상 불가.
  **검증거리는 있다**: `SetSpd`가 **정확히 1곳**(BeginPlay 체인)이어야 멱등성 전제(a)가 선다 → **P2-G11**. 실측상 `ResetForBattle`은 `SetHp(MaxHp)`·`SetbAlive`·`SetbBlockActive`·`SetBlockValue`뿐이고 **DT 로드가 없어** 현재 구조는 안전 → **P2-R06**으로 봉인(여기 DT 재로드가 들어오면 재전투마다 Spd가 DT로 되돌아가고, **N1 때문에 순서로는 안 보인다**).

### 검토했으나 문제 없음 (빈손 통과 아님 — 근거 명시)

- **재전투 멱등성** → **CONFIRMED 멱등.** `InitBattle`은 큐를 재구축하지 않고 compact만 하며, compact는 `IsValid`(객체 유효성) 기준이라 **사망 유닛을 제거하지 않는다**(유닛은 `bAlive=false`만 되고 파괴되지 않음) → 2회차 입력 = 1회차 정렬 결과. 재정렬 산술: 키 9799,9698,9597,9496,9395,9294,9193,9092 → 디코드 0..7 → **불변**. **멱등의 의존처는 SPD 상이가 아니라** (a)`Spd` 불변 (b)디코드가 원본 읽고 `SetTurnQueue`가 Completed에 (c)키 저2자리↔인덱스 1:1 — 셋 다 TC로 봉인(P2-G11/R06, G03/G12, G08).
- **사망 유닛 + `InitBattle` 재호출 × `ResetForBattle` × 정렬 상호작용** → **무해.** compact가 사망 유닛을 안 지우므로 큐 길이 8 유지 → `IfThenElse_0.else` → `ForEachLoop(TurnQueue)` → `ResetForBattle` 8회(전원 부활) → 그 **후** Start 클릭 시 `StartBattle`에서 정렬. 시간축이 완전히 분리돼 상호작용 없음.
- **stale `ActiveUnit`**(Start 클릭 → 정렬 → EnterTurnStart 사이) → **무해**, 단 **P2-G01 성립이 전제**. 정렬은 `ActiveUnit`을 읽지도 쓰지도 않고(P2-G13), `EnterTurnStart`의 첫 동작이 `SetActiveUnit`이라 즉시 덮인다. G01이 깨지면(정렬이 뒤) stale이 아니라 **미정렬 큐의 [0]**이 1턴을 먹는다 — 별개의 버그(N2).
- **`Modulo by zero`** → 리터럴 100을 0으로 잘못 넣은 경우에만. `%0` → 경고 + 반환 0 → 디코드 99 → OOB. 계획서 TC 유효, P2-P07에 통합.
- **오버플로** → 최대 키 = `97*100+99` = 9799 ≪ int32 max. 불가.

**PLAUSIBLE(verifier 실측 확정 요망)**
- `SortIntegerArray`의 `TargetArray`(by-ref)에 **로컬 변수 Get**을 물렸을 때 제자리 정렬이 실제로 반영되는가 — 멤버 변수 선례는 있으나(`RemoveIndex(TurnQueue)`) **로컬 배열 by-ref 선례가 이 프로젝트에 없다**. 미반영 시 `SortKeys`가 원순서 그대로 → 디코드 → `[C_0,C_4,C_9,C_5,C_2,C_6,C_3,C_7]`(레벨 원본) → **P2-P03이 탐지**. 멤버로 만들면 회피 가능(그 경우 P2-G10 필수).
- §34 (80) 프로모터블 승격: `곱하기`·`빼기`·`보다큼(>)`·`Modulo`가 **인티저 오버로드로 승격**되는지는 **배선 후 `get_node_infos`로만** 확정. 실수(float) 오버로드로 승격되면 `%`가 부동소수 오차를 낳을 수 있다 → P2-G02/G08에서 `type_id` 확인 필수.

---

## 7. 커버리지 근거

**검토 축**: 경계값(키 최대 9799·최소 92·OOB 인덱스 0~7 밖·`Length==0` 가드) · 동시성(§(A) 8번째 유닛 BeginPlay 레이스·`RegisterUnitReady`↔DT로드 순서·PIE 재시작 ×3) · null(RowNotFound 머지·`CastFailed` 미연결·`Get(사본)` OOB→None·큐 None 잔류) · 순서(정렬↔`EnterTurnStart` exec 상류성·`SetTurnQueue`↔ForEach Completed·`Clear`↔`Add`·인코드↔디코드 대칭) · 상태전이(State 0 대기 중 큐 원본·재전투 멱등·사망 유닛 compact) · 명세-구현(계획서 5건 정정·청사진 L21·QA-H4 보존) · **무음실패(DT 폴백 등가성 ← 최대 발견·SelectInt 극성 3종·함정(54) 전파·`save_actor` 반환값)**.

**판정 불가로 남긴 것**: `DynamicCast_2.CastFailed` 경로는 원리상 PIE 도달 불가(`WBP_UnitFrame`이 아닌 위젯이 생길 경로 없음) → GRAPH 전용, 런타임 실증 영구 이월.

**Director 직접 검증 권고(계획서 §담당 반영)**: **P2-G02(×100) · P2-G03(Completed 핀) · P2-G04(StartBattle 소속)** — 계획서가 지목한 3곳. **여기에 P2-G01(exec 상류성)·P2-G07(SelectInt 극성)을 추가 권고** — 전자는 계획서 게이트가 구조적으로 통과시키는 오배선(N2), 후자는 행동 TC 전량이 무감각한 오배선(N1/N6). **다섯 곳 전부 서브에이전트 보고를 게이트로 인정하지 말 것.**

---

## 관련
- 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md` §파트2
- **[[파트2_SPD_완료]]**(2026-07-17 00시경 — 본 TC 10건의 PASS 근거 raw 기록, Director 직접 핀조회·PIE 실측 원문)
- [[파트1_Start_TC]] (ID·컬럼 규약 원본 · P1-R01 이월분 → P2-R01) · [[파트1_Start_진행]]
- [[야간F9a_풀회귀_완료]] §2 (구 원장 — P2-R01이 대체)
- [[언리얼_MCP_실전노하우]] §34 (78)(79)(80)(81)(82) · §29 함정(54)
- [[plan]] · [[청사진]] (L21 정정 대상 — P2-R09)
