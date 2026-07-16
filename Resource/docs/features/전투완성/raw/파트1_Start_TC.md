---
type: qa
project: projectTP
feature: 전투완성
stage: 파트1(Start 버튼)
status: 게이트 PASS 2026-07-16 23시경 — TC 46건 verifier 실행 완료(T1 실증 확인, GRAPH 핀 원문 Director 직접검증). P1-R01(F9a 23턴 diff-0)은 오너 결정으로 파트2 이월. P1-G13 문구 정정 반영. 오너 육안 5건(P1-V01~05) 전부 PASS. 상세: [[파트1_Start_진행]] §9
updated: 2026-07-16
---

# 파트1 Start 버튼 — TC

> 대상: 승인 계획서 `humble-purring-glacier.md` §파트1 · [[야간큐_TC]] END-01~08(원장 정정 대상) · [[야간④_End버튼_완료]](박스 3함수 선례) · [[야간F7a_스킬메뉴_완료]](메뉴 배선) · [[야간F9a_풀회귀_완료]] §2(23턴 원장 = 최강 게이트 정답지) · [[언리얼_MCP_실전노하우]] §29 함정(54)·§32
> **qa-critic 적대적 검토 산출물 — 검출·TC설계만.** TC 실행=verifier, 게이트 판정=Director.
> 계획서에 이미 적힌 게이트 항목을 **정식 TC로 승격·정밀화**하고, 실측으로 **계획서 주장 4건을 정정**한 문서. 본 문서의 모든 "실측" 표기는 2026-07-16 라이브 에디터 `find_nodes`+`get_node_infos` 직접 조회 결과다.
#projectTP/전투완성

---

## 0. 범위 & 판정도구

**판정도구 약칭**: **GRAPH**=정적 노드조회(`find_nodes(title="")`+`get_node_infos`) / **자산**=디스크 파일 `grep`·mtime / **PIE**=인스턴스 프로퍼티(`get_properties`, `UEDPIE_0`) / **LOG**=`projectTP.log` grep / **CMP**=컴파일0 / **오너**=육안(불차단).
**★**=게이트(실패 시 단계 정지) / **★★**=최우선 / **★★★**=최강.

> ⚠ `read_graph_dsl`은 이 환경에서 빈 문자열 반환 → 전 GRAPH TC는 `find_nodes(title="")`+`get_node_infos` 조합으로만 판정.

**총 46건** — GRAPH 20 · 자산 4 · PIE 12 · 회귀 10. + 오너 육안 5(별도·불차단).

---

## 1. 착수 전 실측 기준선 (본 문서가 확정 — 인용 시 이 값 기준)

계획서 주장을 라이브 조회로 검증한 결과. **정정 4건 포함.**

| 항목 | 계획서 주장 | 실측 | 판정 |
|---|---|---|---|
| `ShowCancel` 노드 수 | 7 (SetVisibility×3뿐) | **7** | ✅ 일치 |
| `ShowAttack` 노드 수 | 10 | **10** | ✅ 일치 |
| 델타 내용 | "정확히 `SetCollisionEnabled`+`ClickBox` Get"(2노드) | **3노드** — `SetActorHiddenInGame(false)` **+** `SetCollisionEnabled(QueryOnly)` + `ClickBox` Get | ❌ **정정**(N13) |
| `IfThenElse_1` then=폴백/else=Cancel | 같은 Branch 양쪽 핀 | **정확히 일치** — `then`→`SetPendingSkillId(31000000)`→`SetPendingTargetToken("ENEMY1")`→`EnterAwaitTarget` / `else`→`EnterAwaitCommand` | ✅ 일치 |
| `InitBattle` 절단점 | `VariableSet_11.then → CallFunction_5(EnterTurnStart)` | **정확히 일치** (`VariableSet_11`=`SetbWasSkip`) | ✅ 일치 |
| `VariableSet_1` 잠금 리터럴 | `false` | **`false`** (InitBattle 내 `SetbInputLocked` **노드 1개뿐**) | ✅ 일치 |
| `SetBattleState(0)` | InitBattle에 생존 | **`VariableSet_9`** — `EnterTurnStart` 직전(2노드 앞), 동기 체인 | ✅ END-02 위증 **확증** |
| `NotifyUnitClicked` 잠금 가드 | **미실측** | **`FunctionEntry.then → IfThenElse_0(GetbInputLocked)` 직결** — 최상단. `then`(잠금)=**미연결 무음** | ✅ **본 문서가 해소** |
| `MacroInstance_16~19` | `Is Not Valid` exec 미연결 4개 | **4개 전부 미연결 확인** | ✅ 일치 |
| BeginPlay Key 핀 | `CallFunction_2`.Key=`"Battle.Attack"` | **일치** (TableId=`/Game/UI/ST_UI.ST_UI`) | ✅ 일치 |
| `Menu_SkillMenu` 소유 | (Manager 변수처럼 표기) | **`WBP_BattleHUD`의 바인드 위젯** — 접근은 `GetMenu_SkillMenu(self=HUDRef)` | ❌ **정정**(N4) |
| `ClickBox` 기본 콜리전 | (언급 없음) | **`QueryOnly`** (컴포넌트 템플릿 기본값) | ❌ **위험도 역전**(N3) |
| `BattleState` CDO 기본값 | (언급 없음) | **`0`** = 파트1이 만들 "대기" 상태와 동일값 | ❌ **END-02 정정이 재위증**(N7) |
| `bInputLocked` CDO 기본값 | (언급 없음) | **`false`** → InitBattle만 `true`로 뒤집음 = **유일 판별자** | 🔑 N7 해법 |

### 4함수 대칭 전수 실측 (착수 전)

| 함수 | 노드 | `SetActorHiddenInGame` | `SetCollisionEnabled` | Label | LabelCancel | LabelEnd |
|---|---|---|---|---|---|---|
| `ShowAttack` | 10 | **false** ✅유일 | **QueryOnly** | true | false | false |
| `ShowCancel` | **7** | ❌없음 | ❌**없음** ← (B) | false | **true** | false |
| `ShowEnd` | 9 | ❌없음 | **QueryOnly** | false | false | **true** |
| `HideAll` | 9 | ❌없음 | **NoCollision** | false | false | false |

**호출처 전수**: `ShowAttack`←`EnterAwaitCommand.CallFunction_4` **1곳뿐**(→작업10 후 진짜 고아 ✅) / `ShowCancel`←`EnterAwaitTarget.CallFunction_4`(ForEachLoop **`Completed`** 핀 하류) / `HideAll`←`EventGraph.CallFunction_23`(EnterExecuting) **이미 호출 중** / `ShowEnd`←`EnterEnd`.

---

## 2. GRAPH 정적 (P1-G##) — 20건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P1-G01** | ★ | **ShowCancel 콜리전 복구**(작업2) — (B) 소프트락 원천 | GRAPH `find_nodes(ShowCancel)`+`get_node_infos` | `type_id=="콜리전\|SetCollisionEnabled"` 노드 **1개** ∧ `NewType=="QueryOnly"` ∧ `self`←`GetClickBox` (착수 전 **0개**) | 계획서 §(B) · 실측 7노드 |
| **P1-G02** | ★ | **4함수 콜리전 대칭 전수** | GRAPH ×4 | `ShowStart`·`ShowCancel`·`ShowEnd`=**QueryOnly** / `HideAll`=**NoCollision**. 각 함수 `SetCollisionEnabled` 정확히 **1개** | 계획서 §위험1 |
| **P1-G03** | ★ | **ShowStart 기능 동치** — ⚠**노드 개수로 판정 금지** | GRAPH `find_nodes(ShowStart)` | 4요소 필수: `SetCollisionEnabled(QueryOnly, self=ClickBox)` ∧ `SetVisibility(Label,true)` ∧ `SetVisibility(LabelCancel,false)` ∧ `SetVisibility(LabelEnd,false)`. `SetActorHiddenInGame` 유무는 **불문**(9/10노드 양쪽 허용) | **N13** — 계획서 "≈10노드 복제" vs 명시 스펙(9노드)이 `SetActorHiddenInGame` 하나로 갈림 |
| **P1-G04** | ★ | **Start 분기 상류성 + 종단**(작업8) | GRAPH exec 트레이스 | 신규 `Branch(Equal(Byte)(GetBattleState, 0))`가 `IfThenElse_0`(bInputLocked)보다 **exec 상류** ∧ `then→StartBattle()` ∧ **`StartBattle().then.connected_pins == []`** | 계획서 §위험2·작업8 |
| **P1-G05** | ★ | **`IfThenElse_1` 보존 + else 무손상** | GRAPH | `IfThenElse_1` **존재** ∧ `Condition`=`Equal(Byte)(BattleState,2)` ∧ **`else→CallFunction_1(EnterAwaitCommand)` 연결 유지** | 실측 — 노드 삭제 시 Cancel 동반 사망 |
| **P1-G06** | ★ | **폴백 절단 + 고아 존치**(작업9) | GRAPH | **`IfThenElse_1.then.connected_pins == []`** ∧ 3노드(`SetPendingSkillId(31000000)`·`SetPendingTargetToken("ENEMY1")`·`EnterAwaitTarget`) **삭제 0** | 작업9 · delete_node 금지 |
| **P1-G07** | **★★** | **작업8 ∧ 작업9 결합 게이트** — 둘 중 하나만 적용 시 **무음 오동작** | GRAPH (G04 ∧ G06 동시) | **G04·G06 동시 PASS**. 하나라도 FAIL이면 단계 정지 | **N1(High)** — 작업9 미적용 + Start `then` 미종단이 겹치면 Start 클릭이 *전투시작+기본공격 커밋*을 동시 수행 → **원장이 조용히 오염** |
| **P1-G08** | ★ | **END-01 순서 보존**(State==6) — ⚠"최상단" 문구 아님 | GRAPH | `IfThenElse_3(Equal(Byte)(BattleState,6))`가 `IfThenElse_0`(lock)보다 **exec 상류** ∧ `then→InitBattle()→종단`. State 0/6은 상호배타라 **둘의 상대 순서는 자유** | **N2(Medium)** — 작업8이 `FunctionEntry.then` 직후에 들어가면 State==6은 더 이상 "최상단"이 아니다 |
| **P1-G09** | | **InitBattle 리셋 세터 생존** | GRAPH | `SetCurrentIndex(0)`(VS_0)·`SetTurnCounter(0)`(VS_2)·`SetBattleState(0)`(VS_9)·`SetbBattleOver(false)`(VS_7)·`SetbWasSkip(false)`(VS_11) 전부 생존 | 계획서 게이트 |
| **P1-G10** | ★ | **InitBattle 잠금 반전**(작업7) | GRAPH | `VariableSet_1`(SetbInputLocked) 리터럴 == **`true`** ∧ InitBattle 내 `SetbInputLocked` 노드 **정확히 1개**(하류에서 false로 되돌리는 세터 0) | 작업7 · 실측(8 VariableSet 중 잠금 세터 1개뿐) |
| **P1-G11** | ★ | **EnterTurnStart 절단**(작업7) | GRAPH | `VariableSet_11.then`→`CallFunction_5` **연결 없음** ∧ `CallFunction_5` 노드 **존재**(고아 존치) ∧ InitBattle 내 `EnterTurnStart` 호출 **0** | 작업7 |
| **P1-G12** | ★ | **InitBattle 새 꼬리**(작업7) — HUDRef 경유 필수 | GRAPH exec 트레이스 | `VariableSet_11.then`→`ShowStart()`→`IsValid(HUDRef)`→`GetMenu_SkillMenu(self=HUDRef)`→`SetVisibility(Collapsed)`. **꼬리가 `SetHUDRef`(VS_10)/CreateWidget 수렴점보다 하류** ∧ IsValid 가드 존재 | **N4(Medium)** — `Menu_SkillMenu`는 HUD 바인드 위젯. `HUDRef`는 InitBattle 내부에서 CreateWidget됨. [[야간④_End버튼_완료]]의 `EnterEnd` 4노드 패턴이 복제원 |
| **P1-G13** | | **EnterAwaitCommand HideAll 교체**(작업10) — ⚠**노드 ID 문자열 그대로 판정 금지**(2026-07-16 Director 정정) | GRAPH | 체인에서 도달 가능한 `Show*`/`HideAll` 호출이 **`HideAll` 하나뿐**(`ShowAttack`은 도달 불가·고아로 존치) ∧ **프로젝트 전역 `ShowAttack` 호출 0** | 작업10 · 실측(호출처 1곳뿐) · **Director 정정 2026-07-16**: 원 문구 `type_id=="\|HideAll"`은 노드 ID 문자열 그대로를 요구해 `delete_node` 금지 정책·노드 함수 retarget 도구 부재와 양립 불가(N13과 같은 부류의 결함 — 노드 **수**뿐 아니라 노드 **ID** 기반 판정도 금지). 실측상 의도는 완전 충족되어 **Director가 PASS 판정**. 상세: [[파트1_Start_진행]] §9-7 |
| **P1-G14** | | **EnterAwaitTarget 메뉴 Collapsed**(작업11) | GRAPH | `ShowCancel()`(=`CallFunction_4`).then→신규 4노드→`SetVisibility(Collapsed)`. ⚠**`MacroInstance_2`는 ForEachLoop** — 신규 체인은 `ShowCancel` 하류(=`Completed` 핀 계열)에만 | 작업11 · **N5(Medium)** 동명 매크로 혼동 |
| **P1-G15** | | **런타임 SetText 0** | GRAPH | BP_AttackButton 전역 `렌더링\|컴포넌트\|텍스트렌더\|SetText` == **2개**, 둘 다 BeginPlay(`Event_0`) 도달 체인 ∧ `Show*`/`HideAll`/`ShowStart` 내 SetText **0** | 계획서 D1 · END-03 · 실측(SetText 2 = Label·LabelEnd. **LabelCancel은 SetText 없음 = 컴포넌트 기본값**) |
| **P1-G16** | | **BeginPlay Key 핀**(작업5) | GRAPH `get_pin_value` | `EventGraph.CallFunction_2`(MakeTextfromStringTable).`Key` == **`"Battle.Start"`** ∧ `TableId` == `/Game/UI/ST_UI.ST_UI` 불변 | 작업5 |
| **P1-G17** | | **NotifyUnitClicked 잠금 가드 순서** — 파트1 무접촉 확인 | GRAPH 1콜 | `FunctionEntry.then→IfThenElse_0(GetbInputLocked)` 직결 ∧ `then`(잠금) **미연결** ∧ `else→IfThenElse_1(Equal(Byte)(BattleState,3))`. **파트1 전후 diff 0** | 계획서 유일 "미실측" 항목 — **본 문서가 착수 전 실측으로 이미 해소**(§1) |
| **P1-G18** | ★ | **작업12 exec 미연결 0 + 목적지 제약**(신규 제약) | GRAPH | `MacroInstance_16/17/18/19`의 `Is Not Valid` **4개 전부 연결** ∧ **목적지 제약: 상태 세터(`SetBattleState`/`SetCurrentIndex`/`SetTurnCounter`) 및 `EnterTurnEnd`/`EnterExecuting` 호출 금지 — 로그+종단만** | 작업12 · **N6(Medium)** — 목적지가 상태 전이면 오늘의 *시끄러운 정지*가 *조용한 턴 스킵*으로 바뀌어 원장을 무음 오염. **정지는 시끄러워서 안전하다** |
| **P1-G19** | ★ | **컴파일 0**(고아 존치 후) | CMP | `BP_AttackButton`·`BP_BattleManager` 컴파일 **에러 0** | delete_node 금지 정책 |
| **P1-G20** | ★ | **파트1 편집 범위 봉인** = diff-0의 구조적 근거 | GRAPH diff | 편집 대상은 **정확히**: BP_AttackButton(`ShowStart` 신설·`ShowCancel`·EventGraph Key핀) + Manager(`InitBattle` 꼬리·`NotifyAttackButtonClicked`·`EnterAwaitCommand` 1노드·`EnterAwaitTarget` 꼬리·EventGraph 4와이어) + ST_UI/csv. **그 외 0** — 특히 `ResolveHit`·`GetOutgoingAtkMult`·`ApplySkillEffects`·`TickStatusesAtTurnEnd`·`EnterTurnStart` **본체 diff 0** | 계획서 "턴 순서도 데미지도 안 바꾼다" |

---

## 3. 자산 (P1-A##) — 4건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P1-A01** | ★ | **ST_UI `Battle.Start` 존재** | 자산 `grep -cF` | **`grep -cF "Battle.Start" ST_UI.uasset` ≥ 1**. ⚠**`-F` 필수** — `.`이 정규식 와일드카드라 `grep -c "Battle.Start"`는 `BattleXStart`도 매치 | 작업1 · **방법 검증 완료**: 인코딩 **UTF-8**, 기존 키 3종 전부 `grep -cF`==**2**, `Battle.Start` 착수 전 **0** |
| **P1-A02** | ★ | **ST_UI mtime 갱신** — `save_assets` 반환값 신뢰 금지 | 자산 `stat` | mtime > **2026-07-16 19:58:04**(실측 기준선, size 3615). ⚠`set_entry`가 dirty를 안 세워 `save_assets`가 **true 반환하며 no-op** | 계획서 작업1 · [[야간④_End버튼_완료]] §1(동일 우회 선례) |
| **P1-A03** | | **csv 미러 동기** | 자산 grep | `Resource/data/st_ui.csv`에 `Battle.Start,Start` **1행 추가** ∧ 기존 `Battle.*` **5행**(Attack·Cancel·CamOn·CamOff·End) **바이트 불변** | 작업1 |
| **P1-A04** | | **SourceString 정합** | 자산 대조 | ST_UI의 `Battle.Start` 값 == csv `SourceString` == **`"Start"`** | [[야간F7a_스킬메뉴_완료]] §5가 남긴 `strings.csv`↔`ST_UI` 싱크 갭 전례 |

---

## 4. PIE 런타임 (P1-P##) — 12건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P1-P01** | **★★** | **자동 시작 0 + 대기 성립** — END-02 정정의 핵심 | PIE 프로퍼티 + LOG | PIE 진입 **5초 대기** 후 `BattleState==0` **AND `bInputLocked==true`** AND `TurnCounter==0` AND `CurrentIndex==0`. 보강: LOG `State\|event=INIT\|mode=FRESH` **1줄** | **N7(High)** — ⚠⚠**`BattleState==0` 단독 판정 금지**. CDO 기본값도 **0**이라 "InitBattle 완료 후 대기"와 "InitBattle 미실행"이 **구분 불가** = END-02 위증의 재발. **`bInputLocked==true`가 유일 판별자**(CDO=`false`, InitBattle `VariableSet_1`만 true로 뒤집음) |
| **P1-P02** | ★ | **대기 중 박스 = Start·클릭가능** | PIE 프로퍼티 | `Label.bVisible==true` ∧ `LabelCancel.bVisible==false` ∧ `LabelEnd.bVisible==false` ∧ `ClickBox.collisionEnabled=="QueryOnly"` | 매트릭스 State 0. ⚠**이 PASS는 ShowStart의 콜리전 노드 존재를 증명하지 않는다**(N3) — **P1-G02/G03이 유일 증명** |
| **P1-P03** | ★ | **대기 중 메뉴 Collapsed** | PIE | `HUDRef.Menu_SkillMenu.Visibility == Collapsed` | 작업7 |
| **P1-P04** | | **대기 중 유닛 클릭 거절** — ⚠판정법 주의 | PIE **음성 증거** | 유닛 클릭 → `BattleState` 불변(0) ∧ `SelectedTargets` 불변 ∧ **신규 `BattleLog\|` 라인 0** | **N8(Medium)** — ⚠**거절 로그 grep 금지**. `NotifyUnitClicked`의 잠금 분기는 **미연결=완전 무음**(`NotifyAttackButtonClicked`는 `BLOCKED (bInputLocked=true)`를 찍는 것과 **비대칭**). 로그로 판정하면 **거짓 FAIL** |
| **P1-P05** | ★ | **Start 클릭 → 전투 시작** | PIE + LOG | 클릭 1회 → `BattleState==2` ∧ `bInputLocked==false` ∧ ActiveUnit==**A1**(`BP_BattleSpawnPoint_C_0`) ∧ `TurnCounter==1` ∧ 메뉴 **Visible** ∧ 3라벨 전부 invisible ∧ `ClickBox` **NoCollision** | 계획서 PIE ③ + 매트릭스 State 2 |
| **P1-P06** | **★★** | **스킬 선택 → Cancel 且 실제 클릭 가능** — **(B) 회귀 최우선** | PIE 프로퍼티 **+ 실클릭 왕복** | 스킬 선택 → `BattleState==3` ∧ `LabelCancel.bVisible==true` ∧ **`ClickBox.collisionEnabled=="QueryOnly"`**. **且 박스 실클릭 → `BattleState==2` 복귀** | 계획서 §(B). ⚠**콜리전 프로퍼티만 보고 PASS 금지** — 클릭 왕복까지가 TC |
| **P1-P07** | | **AwaitTarget 메뉴 Collapsed**(작업11) | PIE | State 3에서 `Menu_SkillMenu.Visibility==Collapsed` ∧ 취소 복귀 후 State 2에서 **Visible 자동 복원** | 작업11 — 복원은 `EnterAwaitCommand`가 이미 Visible 세팅 |
| **P1-P08** | | **종료 → End** | PIE | 전멸 → `BattleState==6` ∧ `LabelEnd.bVisible==true` ∧ `ClickBox` **QueryOnly** ∧ 메뉴 Collapsed | 매트릭스 State 6 |
| **P1-P09** | ★ | **End 클릭 → Start 대기(자동 재시작 안 함)** — 재전투 경로(Path B) | PIE + LOG | End 클릭 → `BattleState==0` ∧ **`bInputLocked==true`** ∧ **8기 `Hp==MaxHp`·`bAlive`** ∧ 메뉴 Collapsed ∧ Label visible. **5초 후 재확인 — 자동 진행 0**. LOG `State\|event=INIT\|mode=RESTART` | 계획서 PIE ⑦ + **N9(Medium)** — Path A(첫 PIE)는 InitBattle이 8번째 유닛 BeginPlay 한복판에서 돌고 **BeginPlay 꼬리가 뒤이어 SetHp 자가치유**. Path B는 **BeginPlay 꼬리가 없어 `ResetForBattle`만이 복원원**. 파트1의 무한 대기창이 이 차이를 **사상 처음 PIE로 관측 가능하게** 만든다 |
| **P1-P10** | | **End 더블클릭**(END-08 무수정 통과 확인) | PIE | 연타 → **크래시 0·소프트락 0**. 2번째 클릭은 State 0 → Start 분기 → 전투 시작(= "Start 화면 1회 못 봄" = 계획서가 **수용한 기지 증상**). 최종 `BattleState==2` | 계획서 §이번에 안 하기로 한 것(디바운스 미도입) |
| **P1-P11** | | **ButtonRef/ManagerRef 재컴파일 생존**(신규) | PIE | 작업3~4(`ShowStart` 신설 + `compile_blueprint(BP_AttackButton)`) 후 `Manager.ButtonRef != None` ∧ `AttackButton.ManagerRef != None` | **N10(Medium)** — 두 레퍼런스는 **세터 노드 0개 = 레벨 인스턴스 지정값**. 함정(54)("기배치 인스턴스에 값 소급 전파 안 됨")이 **2회 재현**된 전례([[야간④_End버튼_완료]] §3-②). 무효화되면 `Show*` 전부 **무음 no-op** → Start 안 뜸 |
| **P1-P12** | | **런타임 에러 0** | LOG | 전 구간 에러 0 — 한국어 로케일 패턴 **"None에 액세스"** 스캔 | [[언리얼_MCP_실전노하우]] §28 함정㊾ |

---

## 5. 회귀 (P1-R##) — 10건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P1-R01** | **★★★** | **F9a 23턴 원장 diff 0** — 파트1 최강 게이트 → **[파트2 이월 — 오너 결정 2026-07-16]** | LOG 원장 대조 | **메뉴 경유**로 23유닛턴 완주 → [[야간F9a_풀회귀_완료]] §2 원장과 **attacker/target/dmg/hp 바이트 일치**(비사망 16줄) ∧ 사망 **7줄**(T5·6·11·12·17·18·23) `died=true` ∧ `State\|turn=23\|event=BATTLE_END\|winner=A` 1줄 ∧ 최종 생존 A4 `hp=8` | 계획서 ★최강 게이트. ⚠**비교 조건**: 원 원장은 **박스 폴백**(31000000) 경유 수집 → 파트1 후엔 **메뉴에서 "공격" 선택**으로만 재현. 베기/파볼 선택 시 dmg 42/61이 나오는 건 **파트1 결함 아님**. **[이월 결정]** 오너 판단("T1만 실증, 23턴은 파트2에서") — 사유: (a) 무접촉은 GRAPH로 이미 증명(P1-G20) (b) 지금 뽑아도 파트2 SPD 정렬이 곧 무효화 (c) 폴백 제거 후 메뉴 클릭 46회 자동화 비용. 파트1 게이트는 대신 T1 실증으로 판정(PASS). 상세: [[파트1_Start_진행]] §9-5·§9-6 |
| **P1-R02** | ★ | **END-04 재정의** — ⚠**계획서 누락** | GRAPH+PIE | **舊 END-04**("재전투 후 `EnterAwaitCommand` 경유 → 'Attack' 라벨 복원, Label **ON**", **PASS 기록됨**)는 작업10+작업5 후 **거짓**이 된다(State 2에서 Label **OFF**). **新**: "재전투 후 **InitBattle 꼬리** 경유 → Label('Start') ON·LabelEnd OFF" **+** "`EnterAwaitCommand` 경유 시 **3라벨 전부 OFF**" | **N11(High)** — 계획서 §부채정리는 END-02(위증)·END-08(무수정)만 다루고 **END-04를 빠뜨렸다**. 미정정 시 다음 풀회귀에서 **원인 불명 FAIL**로 출현 |
| **P1-R03** | | **END-06 재정의** — 계획서 누락 | GRAPH | **舊 END-06**의 예시 "AwaitCommand→공격커밋"은 작업9(폴백 은퇴)+작업10(State 2 NoCollision)으로 **이중 도달 불가**가 됨. **新**: "State 6 분기가 정상경로 오염 0(State 0/3 분기 의미 유지)" | N11 자매 |
| **P1-R04** | | **END-02 정정 반영** | 문서 | 舊 END-02의 `BattleState==0` 어서션은 **위증** → **P1-P01이 대체**. ⚠단 P01의 **판별자(`bInputLocked==true`) 없이는 재위증** | 계획서 §부수 발견 + **N7** |
| **P1-R05** | | **F5-2 무접촉** | GRAPH + LOG | `ResetForBattle`·`bWasSkip`·턴스킵 경로 노드 **diff 0**. R01 완주 중 `SKIP_TURN_DEATH` 방출 시 **`TurnCounter` 불변**(H-1) | Director 질의(회귀 범위) |
| **P1-R06** | | **F7a 무접촉**(메뉴 본체) | GRAPH + PIE | `NotifySkillSelected` 3중 가드·쿨다운·Row 배선 **diff 0**(파트1이 건드리는 건 Manager의 **표시 제어**뿐). 5스킬 정상(베기42·파볼61·막기 반감·치유 -33) | Director 질의 |
| **P1-R07** | | **F8 무접촉** | GRAPH + LOG | 광폭화 공식 노드 **diff 0**. turn≤23 구간 `BerserkMult=1.00` → **R01 성립이 곧 F8 무접촉 증명** | Director 질의 |
| **P1-R08** | | **데미지폰트 무접촉** | PIE + LOG | R01 중 매 타격 `DamageText` 스폰 ∧ 표시값 == `BattleLog` `dmg`(DF-01 재확인) | Director 질의 |
| **P1-R09** | | **RegisteredCount 재전투 무해 재확인** | PIE | 재전투 후 `RegisteredCount==8` 불변 ∧ InitBattle 정상 완주 ∧ `RegisterUnitReady` 재진입 **0**(BeginPlay 1회성이라 구조적) | Director 질의 — **"무해" 판정 재확인 완료**. 단 **N12** 참조(파트1이 실패 모드를 악화시킴) |
| **P1-R10** | | **고아 노드 존치** | GRAPH + CMP | `ShowAttack`(함수 10노드) · `InitBattle.CallFunction_5`(EnterTurnStart) · 폴백 3노드 · **`EventGraph.CallFunction_1`(SetInputModeGameAndUI, 기존 고아)** 전부 **삭제 0** ∧ 컴파일 0 | delete_node 금지 · **N14** — ⚠"고아 0" 류 어서션 쓰면 **거짓 FAIL**(착수 전부터 고아 1건 존재) |

---

## 6. 오너 육안 (불차단 — 진행 안 막음)

| ID | 항목 | 결과 |
|---|---|---|
| **P1-V01** | Start 라벨 룩·위치·크기 | **PASS**(2026-07-16 23시경 — 박스 "Start" 표시 확인, [[파트1_Start_진행]] §9-4 #1) |
| **P1-V02** | Start→메뉴 전환 체감(박스가 사라지고 메뉴가 뜨는 흐름) | **PASS**(§9-4 #2 — Start→턴 시작+메뉴) |
| **P1-V03** | Cancel 라벨 가독성 | **PASS**(§9-4 #3 — 박스 "Cancel" 且 실제 클릭됨, 최대 회귀 지점 콜리전 복구 실증) |
| **P1-V04** | 대기 화면 8기 풀피 HP바(현상 명시 — 신규 지정 아님) | **PASS**(전투 진행 구간 육안 확인, 이상 보고 없음) |
| **P1-V05** | 재전투 페이싱(End→Start 대기 전환) | **PASS**(§9-4 #5 — 전투 끝→"End"→Start 대기) |

오너 코멘트(2026-07-16 23시경, 5항목 전체): *"전부 완료(문제 없음, 일단 기본 공격만 사용)"* — [[파트1_Start_진행]] §9-4.

---

## 7. 신규 발견 — 계획서에 없던 것 (14건)

> 심각도순. **CONFIRMED**=라이브 조회로 확정 / **PLAUSIBLE**=논리상 의심, 실측 필요.

### High

- **N1 — 작업8·작업9 결합 무음 오동작** `CONFIRMED`
  계획서 #5의 위험 근거("미종단이면 … **아래 분기로 흘러듦**")는 **작업9 적용 후엔 stale**이다. 실측상 작업9가 `IfThenElse_1.then`을 끊으면 미종단 Start는 절단 스텁으로 흘러 **무해**해진다. **진짜 위험은 작업9가 아직/영영 미적용인 상태**: 그때 Start 클릭 = `StartBattle()` → State 2·lock=false로 복귀 → `IfThenElse_3`(≠6) → `IfThenElse_0`(unlock) → `IfThenElse_1`(**==2 참**) → **폴백 발화** = 전투시작과 동시에 기본공격 커밋. **길이·에러 없이 원장만 조용히 오염.** → **P1-G07 결합 게이트**(둘을 하나로 묶어 판정).

- **N7 — `BattleState==0`은 파트1 이후에도 위증 가능** `CONFIRMED`
  실측 **CDO `BattleState=0`**. 계획서 §부수 발견은 "파트1이 State 0을 실체화하면서 END-02 어서션이 **처음으로 참이 된다**"고 하나, **참이 되는 이유가 옳다는 보장이 없다** — 0은 "InitBattle 완료 후 대기"이자 "**InitBattle 미실행**"이다. 같은 값을 같은 방법으로 읽으면 **QA-H6 위반이 그대로 재발**한다. 판별자 필수: **`bInputLocked==true`**(CDO=`false`, InitBattle의 `VariableSet_1`만 뒤집음 — 실측상 InitBattle 내 잠금 세터는 **1개뿐**) 또는 `State|event=INIT` 로그. → **P1-P01**.

- **N11 — TC 원장 2건 파손(END-04·END-06), 계획서 부채정리 누락** `CONFIRMED`
  [[야간큐_TC]] **END-04**는 *"재전투 후 `EnterAwaitCommand` 경유 → 버튼 'Attack' 라벨 복원(LabelEnd OFF, **Label ON**)"*으로 **PASS 기록**돼 있다. 작업10이 `EnterAwaitCommand`를 `HideAll`로 바꾸면 State 2에서 Label은 **OFF** → 어서션 **거짓**. 작업5(Label→"Start")까지 겹쳐 "Attack 라벨"이라는 표현 자체가 소멸. **END-06**의 *"AwaitCommand→공격커밋"* 예시도 작업9+작업10으로 **이중 도달 불가**. 계획서는 END-02·END-08만 손대고 이 둘을 빠뜨렸다 → **P1-R02·R03**.

### Medium

- **N3 — ShowStart 콜리전 누락은 "게임 시작 불가"가 아니라 *무증상*** `CONFIRMED` — **위험도 역전**
  실측: `ClickBox` 컴포넌트 기본 `collisionEnabled` = **`QueryOnly`**. 두 진입 경로 모두 ShowStart 직전 콜리전이 이미 QueryOnly다 — Path A(첫 PIE)=컴포넌트 기본값(그 전에 `HideAll` 실행 없음), Path B(재전투)=`ShowEnd`가 켜둔 값. → **`SetCollisionEnabled`를 빠뜨려도 Start는 정상 클릭된다.** 계획서 위험1("ShowStart/ShowCancel 콜리전 누락 → **게임 시작 불가**")은 ShowStart 쪽이 **틀렸고**, 실제로는 **PIE 전 항목을 통과하면서 잠복**하는 쪽이라 더 나쁘다. **GRAPH가 유일 탐지수단**(P1-G02/G03), P1-P02의 PASS를 증명으로 쓰면 안 된다.
  ↔ 반면 **ShowCancel 누락은 진짜 Critical** — 작업10 후 `HideAll`(NoCollision)이 **직전**에 실행되므로 인접 의존. **계획서 §(B)는 100% 정확**.

- **N4 — `Menu_SkillMenu`는 Manager 변수가 아니라 HUD 바인드 위젯** `CONFIRMED`
  실측: `GetMenu_SkillMenu`의 `self` 핀 ← **`WBP Battle HUD 오브젝트 레퍼런스`**. 계획서 작업7의 표기 `Menu_SkillMenu.SetVisibility(Collapsed)`는 Manager 변수처럼 읽힌다. 실제 필요 형태는 `GetHUDRef → IsValid → GetMenu_SkillMenu(self=HUDRef) → SetVisibility(Collapsed)`(**4노드** — 계획서 작업11의 "4노드" 추정치와 일치). 추가로 **`HUDRef`는 InitBattle 내부에서 `CreateWidget`**되므로(IsValid 가드 하에 1회), 새 꼬리는 반드시 `SetHUDRef` 수렴점 **하류**여야 한다. `EnterEnd`가 정확히 이 패턴이라 복제원으로 적합. → **P1-G12**.

- **N5 — 동명 매크로 혼동 함정** `CONFIRMED`
  `EnterAwaitCommand.MacroInstance_2` = **`IsValid`(HUDRef)** / `EnterAwaitTarget.MacroInstance_2` = **`ForEachLoop`**. **같은 노드명, 다른 매크로.** 작업11은 후자의 `Completed` 핀 하류(`ShowCancel()` 뒤)에 붙어야 한다. 노드명 기준으로 작업하면 오배선. → **P1-G14**.

- **N6 — 작업12 목적지 미정 = 무음 오염 위험 + 커밋 오염** `CONFIRMED`
  계획서가 목적지를 *"기존 에러 처리 패턴을 찾아 확정"*으로 열어뒀다. 목적지가 `EnterTurnEnd` 같은 **상태 전이**면 오늘의 **시끄러운 정지**(턴 영구 멈춤 = 즉시 발각)가 **조용한 턴 스킵**(원장 무음 오염)으로 **악화**된다. **정지는 시끄러워서 안전하다** → 목적지는 **로그+종단**으로 제약해야(P1-G18). 또 4핀 전부 **도달 불가 경로**라 PIE 검증이 원리상 불가 = GRAPH 전용 → **diff-0 게이트가 걸린 커밋에 도달불가 4와이어를 섞으면 실패 시 원인 분리가 어려워진다. 별도 커밋 권고**(Director 판단).

- **N8 — `NotifyUnitClicked` 잠금 거절은 완전 무음** `CONFIRMED`
  실측: `IfThenElse_0.then`(잠금) **미연결** — 로그 **없음**. `NotifyAttackButtonClicked`는 `"NotifyAttackButtonClicked: BLOCKED (bInputLocked=true)"`를 찍는데 **비대칭**. 계획서 PIE 게이트 ②("대기 중 유닛 클릭 거절")를 **로그 grep으로 판정하면 거짓 FAIL**. 음성 증거(State 불변·BattleLog 라인 0)로만 판정 → **P1-P04**.

- **N9 — 진입 경로 비대칭(Path A/B)** `CONFIRMED`
  Path A(첫 PIE): InitBattle이 **8번째 유닛 BeginPlay 한복판**에서 동기 실행 → 반환 후 **그 유닛의 BeginPlay 꼬리가 이어서 실행**(`SetHp` 자가치유 — 계획서 §(A)가 지적한 그 구조). Path B(재전투): End 클릭 → InitBattle → **BeginPlay 꼬리 없음** → `ResetForBattle`만이 유일 복원원. 파트1이 State 0을 **무한 관측창**으로 만들면서 이 차이가 **사상 처음 PIE 프로퍼티로 직접 관측 가능**해진다 — 이는 END-02가 원래 원했으나 구조상 가질 수 없던 것이다. → **P1-P09**가 그 창을 활용.

- **N10 — `ButtonRef`/`ManagerRef` 세터 0개 = 레벨 인스턴스 지정값** `CONFIRMED`(구조) / `PLAUSIBLE`(재컴파일 영향)
  실측: 두 변수 모두 **`Set*` 노드가 프로젝트 전역 0개**(`ButtonRef`는 EventGraph에서 `HideAll` 호출용 Get 1개 + 함수들의 Get뿐). → 레벨 인스턴스에 손으로 꽂은 참조. 작업4가 **`compile_blueprint(BP_AttackButton)`을 명시적으로 요구**하는데, 함정(54)("기배치 인스턴스에 값 소급 전파 안 됨")은 이 프로젝트에서 **2회 재현**된 이력이 있다([[야간④_End버튼_완료]] §3-②). 무효화되면 `ShowStart`/`ShowCancel`/`ShowEnd`가 **전부 무음 no-op** → Start 안 뜸. → **P1-P11**.

### Low

- **N12 — 파트1이 `RegisteredCount<8` 실패 모드를 악화시킴** `PLAUSIBLE`
  실측: `RegisterUnitReady`는 `Equal(Integer)(RegisteredCount, 8)` **정확 비교** → `then→InitBattle()`, `else` 미연결. 8에 도달 못 하면 InitBattle 미실행. **파트1 전**: 전투가 안 시작됨 = 즉시 발각. **파트1 후**: `ShowStart`가 InitBattle 꼬리에만 있으므로 박스는 **기본 상태**로 남는데 — Label은 BeginPlay SetText로 이미 **"Start"**, ClickBox는 컴포넌트 기본값 **QueryOnly** → **정상처럼 보이고 클릭도 된다.** 그리고 `BattleState`도 CDO **0**이라 Start 분기가 **참** → **빈/불완전 `TurnQueue`로 `StartBattle()` 진입**. 도달성은 레벨 오구성 전제라 낮음(8기 BeginPlay는 동일 프레임 처리라 사람이 그 틈에 클릭 불가). 저비용 완화: `StartBattle` 진입부 `TurnQueue.Length==8` 가드 — 단 **死코드 규약과 충돌 소지**가 있어 Director 판단 필요.
  ※ Director 질의 **"RegisteredCount 재리셋 없음이 재전투에 무해한가"** → **무해 확인**(BeginPlay 1회성 → `RegisterUnitReady` 재진입 0, 재전투는 InitBattle 직접 호출로 우회). 적대적 검증의 "무해" 판정 **유지**. 위 N12는 재전투가 아니라 **최초 진입 실패 모드**에 관한 별건.

- **N13 — `SetActorHiddenInGame` 4함수 비대칭** `CONFIRMED`
  `ShowAttack`만 `SetActorHiddenInGame(bNewHidden=false)` 보유, 나머지 3함수 없음, `HideAll`에 대응 setter(true) **없음**, CDO `bHidden=false` → **현재 완전 무동작(no-op)**. 실해 없음. 다만 계획서 §(B)의 *"델타가 **정확히** `SetCollisionEnabled`+`ClickBox` Get"*은 **부정확**(실제 델타 **3노드**). 이 오차가 작업3의 *"`ShowAttack` 복제(≈**10**노드)"* vs 명시 스펙(SetVisibility×3+SetCollisionEnabled = **9**노드) 불일치를 낳는다 → **노드수 기반 TC는 어느 값을 써도 거짓 판정**. **P1-G03을 기능 동치로 설계한 이유.**

- **N14 — 기존 고아 1건** `CONFIRMED`
  `BP_AttackButton:EventGraph.CallFunction_1`(`SetInputModeGameAndUI`)의 `execute` **미연결**. F7a ③이 `SetInputMode`를 `InitBattle`로 옮기며 남은 잔재([[야간F7a_스킬메뉴_완료]] §2-③). 무해·존치. 단 **"고아 0" 류 어서션을 쓰면 착수 전부터 거짓 FAIL** → **P1-R10을 "삭제 0"으로 표기**.

### 상태 전이 중 "라벨은 A인데 동작은 B" 탐색 결과 (Director 질의)

**전이 경계 전수 검토 → 실질 어긋남 0건.** 근거:
- State 0/3/6만 클릭 가능하고, 셋 다 **라벨과 동작이 일치**(Start→StartBattle / Cancel→EnterAwaitCommand / End→InitBattle).
- State 0·6 분기는 잠금 체크 **상류**, State 3은 `IfThenElse_1.else`로 도달 — 셋 다 정합.
- **모든 상태 함수가 Function Graph(latent 불가)**라 라벨 세팅과 콜리전 세팅 사이에 **프레임이 끼어들 수 없다** — `Show*` 4함수는 각각 단일 동기 체인. State 5만 Custom Event+Delay(0.35s)지만 **박스 무접촉**(State 4의 `HideAll` 상속).
- ⚠ 단 **1건 준-어긋남**: `IfThenElse_1.else`(Cancel)는 `State==3` 검사가 **아니라** `State!=2`다. 지금은 0/1/4/5가 잠금에, 6이 상류 분기에 걸려 **소거법으로만** State 3에 국한된다. **파트1은 이 구조를 안 건드리므로 회귀 아님**이나, 향후 "잠금 없는 새 상태"를 추가하면 Cancel이 오발화한다. 기록만(F7b 이후 재검).

---

## 8. 커버리지 근거 (빈손 통과 아님)

**검토 축**: 경계값(State 0/2/3/4/5/6 전수·CDO 기본값 일치 함정) · 동시성(BeginPlay 순서·Path A/B·8번째 유닛 레이스·더블클릭) · null(ButtonRef·ManagerRef·HUDRef·Menu_SkillMenu 4종 참조 + IsValid 가드 4곳) · 순서(작업8↔9 결합·잠금 상류성·SetHUDRef 하류성·ForEachLoop Completed) · 상태전이(4함수 대칭·콜리전 상속 사슬·라벨-동작 정합) · 명세-구현(END-01/02/04/06/08 원장 대조·spec.md §5 메뉴 가시성) · 무음실패(콜리전 무증상 누락·로그 없는 거절·grep 정규식·save_assets no-op).

**PLAUSIBLE(verifier 실측 확정 요망)**: N10(재컴파일이 레벨 인스턴스 참조를 무효화하는지 — 구조는 CONFIRMED, 영향은 실측 필요) · N12(도달성 낮음, 완화는 Director 판단).

**판정 불가로 남긴 것**: 작업12의 4개 `Is Not Valid` 경로는 **원리상 PIE 도달 불가** → GRAPH 전용, 런타임 실증 **영구 이월**(N6).

---

## 관련
- 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md` §파트1
- [[야간큐_TC]] END-01~08 (**END-02·04·06 정정 대상** — R02/R03/R04)
- [[야간F9a_풀회귀_완료]] §2 (23턴 원장 = R01 정답지)
- [[야간④_End버튼_완료]] (박스 3함수·함정(54) 선례) · [[야간F7a_스킬메뉴_완료]] (메뉴 배선·고아 잔재)
- [[언리얼_MCP_실전노하우]] §28 함정㊾ · §29 (54)(57)(58) · §32 (66)~(71)
- [[plan]] · [[청사진]]
