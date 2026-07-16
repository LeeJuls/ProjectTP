---
type: raw
project: projectTP
feature: 전투완성
stage: 파트2(SPD 턴 순서)
status: 핵심 게이트 PASS 2026-07-17 00시경 — Director 직접검증 GRAPH 5/5(P2-G01·G02·G03·G04·G07) + 보너스 2건(P2-G05·G09) PASS. ★★★최강게이트 P2-P01(런타임 spd 8기 실값) PASS + P2-P02·P2-P11 PASS. 전체 41건 중 10건 실행·전부 PASS, 잔여 31건(첫8턴 LOG·23턴 신규원장 P2-R01 등)은 Start 클릭이 필요해 아침 오너 확인으로 이월(Director 판단, §7).
updated: 2026-07-17
---

# 파트2(SPD 턴 순서) — 야간 게이트 결과 (핵심 게이트 PASS, 잔여 이월)

> 대상: 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md`(v3) §파트2 · [[파트2_SPD_TC]](qa-critic TC 41건 — 이 문서가 그중 10건의 PASS 근거) · [[파트1_Start_진행]](선행 게이트 — State 0 무한 대기창을 만들어 이번 검증의 전제가 됨) · [[야간F9a_풀회귀_완료]](구 원장, 파트2가 대체할 기준선) · [[언리얼_MCP_실전노하우]] §34
> 오너 확정 결정 5([[파트1_Start_진행]] §2)대로 **SPD 검증은 Director가 직접 챙긴다** — 구현은 sonnet(gameplay-engineer), 게이트 판정은 Director가 `get_node_infos`/`get_properties` 원문을 직접 조회해 확정한다. 이 문서에 적힌 "실측"은 전부 그 직접조회 원문이며, 서브에이전트 보고를 그대로 게이트로 인정하지 않는다.
#projectTP/전투완성

**요약**: 41건 TC 중 **10건을 오늘 밤 직접 실행해 전부 PASS**시켰다 — GRAPH 핀 원문 검증 7건([[파트2_SPD_TC]]가 "서브에이전트 보고를 게이트로 인정하지 말 것"이라 지목한 5곳 전부 + 보너스 2곳) + PIE 런타임 3건(그중 P2-P01은 이 TC 문서 자신이 발견한 **"파트2의 유일한 진짜 게이트"**). 나머지 31건(첫 8턴 순서·23턴 신규 원장·회귀 9건·데이터 4건 등)은 오너가 Start를 눌러야만 진행되는 항목이라 **아침으로 이월**했다 — 이유는 §7에.

---

## 1. 무엇을 만들었나

SPD 높은 순으로 턴이 오게 한다. **밸런스는 범위 밖**(오너 명시 — 순서 기능만). 배정 기준은 하나: **DT 성향 일관**(마법사 12 > 전사 10) + 큐 순서대로 97~90.

- `BP_BattleSpawnPoint`: `Spd`(int) + `SpdOverride`(int, Instance Editable) 신설. `SetDef.then → DynamicCast_2` 사이에 `SetSpd` 삽입, 값 = `SelectInt(A=SpdOverride, B=BreakStruct_0.Spd핀[idx7], bPickA=SpdOverride>0)`.
- `BP_BattleManager`: `SortTurnQueueBySpd()` 신설(18노드, 로컬 `SortKeys`/`SortedQueue`) → **`StartBattle()`에 배선**.
- 레벨 8기 `SpdOverride`: A3=97 · B3=96 · A4=95 · B4=94 · A1=93 · B1=92 · A2=91 · B2=90.

---

## 2. Director 직접 검증 — GRAPH 5/5 PASS (핀 원문)

[[파트2_SPD_TC]] §7 "커버리지 근거"가 스스로 지목한 **"다섯 곳 전부 서브에이전트 보고를 게이트로 인정하지 말 것"**(P2-G02·G03·G04·G01·G07) 전부를 Director가 직접 `get_node_infos`로 조회했다. 5/5 PASS. 보너스로 2곳을 더 확인했다.

| # | 검증 내용 | 핀 원문(Director 직접 조회) | 대응 TC |
|---|---|---|---|
| 1 | 키 인코딩 곱수 == 100 | `SortTurnQueueBySpd.K2Node_PromotableOperator_0` = `수학\|인티저\|int*int`, `A ← VariableGet_3(GetSpd)`, **`B value="100"`** — `×10` 오타였다면 인덱스 OOB로 큐가 8→1로 영구 붕괴할 자리 | **P2-G02** |
| 2 | `SetTurnQueue`가 디코드 `Completed` 핀 | 디코드 `MacroInstance_1`(ForEachLoop)의 **`Completed`(idx3) → `VariableSet_0`(SetTurnQueue)**, `LoopBody`(idx0)는 `CallArrayFunction_3`(Add→SortedQueue)로 분리 — 읽는 중 원본 파괴 없음 | **P2-G03** |
| 3 | 정렬 그래프 소속 = `StartBattle`만 | `find_nodes(InitBattle,"Sort")` = **0건** | **P2-G04** |
| 4 | ★정렬이 `EnterTurnStart` exec 상류 | `FunctionEntry_0.then → CallFunction_1(\|SortTurnQueueBySpd) → CallFunction_0(\|EnterTurnStart)`, 후자 `then=[]`. [[파트2_SPD_TC]] N2가 경고한 "`StartBattle`의 유일한 빈 exec 핀(`EnterTurnStart.then`)에 오삽입"을 회피했음을 확인 | **P2-G01**(★★) |
| 5 | ★`SelectInt` 극성 | `A ← VariableGet_0(SpdOverride)`, **`B ← BreakStruct_0` 출력 idx7**(Spd 핀), `bPickA ← PromotableOperator_0` = `수학\|인티저\|integer>integer`(`A←SpdOverride`, `B="0"`) → **`SpdOverride > 0`**(N6이 경고한 A/B뒤바뀜·조건반전·값미전파 3종 무음오배선 전부 회피) | **P2-G07**(★★) |
| 보너스 | `SortIntegerArray` 파라미터 | `유틸리티\|배열\|정렬\|SortIntegerArray`, **`bStableSort="true"`**, **`SortOrder="Descending"`**, 인코드 루프 `Completed` 후 실행 → 디코드 루프로 진입. **오늘 오전 "이 노드는 존재하지 않는다"고 오진했던 바로 그 노드**([[언리얼_MCP_실전노하우]] §34 (79)) | **P2-G09**(부분 — `TargetArray` 소스 자체는 미기재) |
| 보너스 | 死코드 0건 | `find_nodes(SortTurnQueueBySpd,"Random")` = **0건**(오너 결정 4 준수) | **P2-G05** |

---

## 3. ★★★ 최강 게이트 — P2-P01 PASS (런타임 `spd` 8기, PIE 실측)

| 유닛 | Spd | SpdOverride | bIsParty |
|---|---|---|---|
| C_2(A3) | 97 | 97 | true |
| C_6(B3) | 96 | 96 | false |
| C_3(A4) | 95 | 95 | true |
| C_7(B4) | 94 | 94 | false |
| C_0(A1) | 93 | 93 | true |
| C_4(B1) | 92 | 92 | false |
| C_9(A2) | 91 | 91 | true |
| C_5(B2) | 90 | 90 | false |

**8기 전부 ≠0 ∧ 전부 상이** — 설계 배정표와 100% 일치. **DT 폴백(전사10·마법사12)이 아니라 오버라이드가 실제로 먹었다.** 같은 조회로 `SpdOverride` 컬럼도 확보되므로 **P2-P02도 동시에 PASS**한다.

**왜 이게 파트2의 유일한 진짜 게이트인가**: [[파트2_SPD_TC]] N1이 발견한 대로, **DT 폴백으로 계산해도 목표 순서와 바이트 일치**한다(키 `1099,1098,1097,1096,1295,1294,1293,1292` → 같은 디코드 `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]`). 즉 **작업1~3(Spd 변수·SetSpd 삽입·8기 SpdOverride)을 통째로 생략해도 PIE 순서 게이트(첫 8턴·재시작 동일 등)는 전부 PASS**해버린다. **순서만 보는 검증으로는 이 기능이 실제로 동작하는지 증명이 불가능**하고, **런타임 `spd`/`spdOverride` 직접 조회만이 유일한 증거**다 — 이번 조회로 그 증거가 확보됐다.

---

## 4. 부수 실증 — 파트1까지 재확인

PIE 시작 직후(Start 클릭 전) `BP_BattleManager_C_0` 조회:

- `BattleState=0`, `bInputLocked=true`
- **`TurnQueue=[C_0,C_4,C_9,C_5,C_2,C_6,C_3,C_7]`(레벨 원본, 미정렬)**

→ **Start를 안 눌렀으니 `StartBattle`이 안 돌았다** = 파트1의 대기 상태 성립을 재확인 + **정렬이 `StartBattle`에 있다는 런타임 교차증거**(P2-P11, §2의 GRAPH 조회와 별개 경로로 P2-G04를 재확인).

---

## 5. PIE 액터 경로 형식 — 신규 발견 (§34 후보)

verifier가 이 형식을 몰라 파트1 검증을 진행하지 못했던 지점이라, 다음 세션을 위해 기록한다.

- ❌ `/Temp/UEDPIE_0_map_battle_octopath...`
- ❌ `/Game/Blueprints/BP_BattleManager:UEDPIE_0_...`
- ✅ **`/Game/Stages/UEDPIE_0_map_battle_octopath.map_battle_octopath:PersistentLevel.BP_BattleSpawnPoint_C_2`** — 원래 애셋 폴더 경로 + `UEDPIE_0_` 접두어를 레벨명 앞에 붙이는 형식.
- `ObjectTools.get_properties(instance={refPath}, properties=[...])` — 파라미터명이 `object`/`property_names`가 아니라 **`instance`/`properties`**.

---

## 6. 명세 이탈 1건 (Director 수용)

**`save_actor`(OFPA 개별 저장) → `AssetTools.save_assets`(레벨 패키지 통째 저장)로 변경.** 계획서·[[파트2_SPD_TC]] 둘 다 OFPA(External Actors)를 전제했으나, **`map_battle_octopath`는 OFPA가 아니다** — 8기가 단일 `.umap`에 내장된 구조. 에러 원문:

> `'SpawnPoint_Party_A3' is not an external actor asset and cannot be saved individually. Save the level instead.`

(`__ExternalActors__/` 폴더 자체는 존재하나 무관한 `/Game/test` 소유 — 이 레벨과 무관.) 결과는 동일(8기 값 저장됨).

부수 발견(§34 후보): **`ProgrammaticToolset`은 트랜잭션 단위로 실행된다** — 스크립트 중간에 실패하면 그 안에서 이미 성공한 `set_properties` 호출도 함께 롤백된다.

---

## 7. 미실행 — 아침 오너 확인으로 이월

**첫 8턴 순서 + 23턴 신규 원장**(P2-P04·P2-R01)은 Start 클릭이 필요한데, 자동화하려면 다음을 전부 통과해야 한다:

- 창 전환(당시 전면 창이 'Claude'였음)
- 클릭 좌표 판독 — **함정 (51)**: 클릭 좌표는 화면 픽셀 판독만 신뢰해야 하고, 원경 유닛은 오차가 크다.
- **미해결 함정**: `CaptureViewport`가 PIE가 아닌 에디터 원본을 찍는 정황([[언리얼_MCP_실전노하우]] §7 이월).
- 메뉴 경유 46클릭 — 1회라도 오타격이면 원장이 통째로 틀어진다.

**Director 판단**: ★★★ 게이트(런타임 spd)와 GRAPH 5/5가 이미 통과했고, **아침에 오너가 Start를 한 번만 누르면 순서가 즉시 드러난다.** 야간 시간은 파트3에 쓰는 게 가치가 높다고 판단해 **자동화를 접었다**(오너 승인은 "허용"이지 "필수"가 아님 — 이 시점의 오너 승인 없이 Director 단독 판단으로 이월 결정).

→ **아침 오너 확인 항목**: Start 클릭 → 턴이 **마법사 4기부터**(A3→B3→A4→B4→A1→B1→A2→B2) 오는지 확인.
→ 23턴 원장 재수집·F8 turn40 기대값 갱신([[파트2_SPD_TC]] P2-R02)은 그다음.

---

## 8. 자산 (디스크 실증)

| 파일 | 착수 전 | 착수 후 | mtime |
|---|---|---|---|
| `BP_BattleSpawnPoint.uasset` | 1,090,891 | **1,103,709** | 2026-07-17 00:05:54 |
| `BP_BattleManager.uasset` | 2,438,048 | **2,486,212** | 2026-07-17 00:05:54 |
| `map_battle_octopath.umap` | 3,847,443 | **3,847,823** | 2026-07-16 23:57:22 |

바이너리 grep 신규 등장: `SortKeys`·`SortedQueue`·`SpdOverride`·`SelectInt`. `find_nodes(SortTurnQueueBySpd,"Random")` = **0건**(死코드 없음, 오너 결정 4 준수 — §2 보너스 항목과 동일 근거).

---

## 9. TC 41건 실행 현황 — 10건 실행·전부 PASS / 31건 이월

| 분류 | 총계 | 오늘 밤 실행·PASS | 미실행(아침 이월) |
|---|---|---|---|
| GRAPH (P2-G##) | 17 | **7** — G01·G02·G03·G04·G05·G07·G09 | 10 |
| PIE (P2-P##) | 11 | **3** — P01·P02·P11 | 8 |
| 회귀 (P2-R##) | 9 | 0 | 9(R01 신규원장 재수집이 나머지 대부분의 선행조건) |
| 데이터 (P2-D##) | 4 | 0(§8 자산표가 정황 증거는 제공하나 D01·D02가 요구하는 8기 개별값 확인은 미실행) | 4 |
| **합계** | **41** | **10** | **31** |

실행 안 된 31건 중 실질적으로 새로운 결함을 잡아낼 가능성이 있는 항목은 §7이 이월한 P2-P04·P2-R01(첫 8턴·23턴 원장) 정도이고, 나머지 회귀 TC는 대부분 P2-R01 완주 이후에나 판정 가능한 파생 항목이다.

---

## 10. 다음 단계

1. **아침 오너**: Start 클릭 → 턴 순서가 §7 기대값(마법사 4기부터)과 일치하는지 육안 확인.
2. 통과 시 verifier가 23유닛턴 신규 원장 수집([[파트2_SPD_TC]] P2-R01 절차대로) → [[야간F9a_풀회귀_완료]] 원장을 대체하는 새 기준선으로 봉인.
3. 신규 원장 기준으로 F8 turn40 기대값 갱신(P2-R02) + 잔여 GRAPH/PIE/회귀/데이터 TC(31건) 마저 실행.
4. 전부 통과 시 파트2 게이트를 [[파트2_SPD_TC]] frontmatter에서 "전체 PASS"로 재승격.

---

## 관련
- [[파트2_SPD_TC]] · [[파트1_Start_진행]] · [[plan]] · [[청사진]]
- [[야간F9a_풀회귀_완료]](구 원장 — P2-R01이 대체 예정) · [[야간F8_광폭화_완료]](turn40 기대값 갱신이 참조할 F8 계산 기준)
- [[스탯_전투공식_v1]](DT_JobStats Spd 기본값 — 전사10·마법사12 — 의 출처, DT 폴백 산술의 근거)
- [[언리얼_MCP_실전노하우]] §34 (78)~(83) · §7(CaptureViewport 미해결 이월)
