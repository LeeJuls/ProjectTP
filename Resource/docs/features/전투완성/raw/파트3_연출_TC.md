---
type: qa
project: projectTP
feature: 전투완성
stage: 파트3(막기·치유 연출)
status: 핵심 게이트 PASS 2026-07-17 01시경 — 38건(GRAPH 18·PIE 11·회귀 9) 중 **6건 Director 직접 실행·전부 PASS**: GRAPH 6/6(P3-G01·G02·G03·G04·G05·G06, 본 문서가 지목한 ★★★/★★ 최우선 6곳 전부). **★착수 전 Director 결정 3건(N1·N2·N3) 채택 후 구현 — 결정 없이 구현했다면 5건 중 3건이 "그래프 게이트는 PASS·증상은 그대로"로 끝났을 것.** 잔여 32건(GRAPH 12·PIE 11·회귀 9)은 Start+스킬선택 클릭이 필요해 아침 오너 확인으로 이월. 실행=verifier(오늘 밤은 Director 직접)·게이트 판정=Director. **[2026-07-17 갱신]** 이월 32건 전부 §8에서 ID별 처분(코어게이트흡수10·S1오라클런흡수5·F9b흡수13·A2회귀스위트2·폐기2) 완료 — blanket 통과 없음. ★P3-P02·P3-P03은 파트4([[파트4_라벨힐_완료]])가 치유 연출을 **오너 지시로 재설계**(아군이동→제자리)해 원문 전제가 소멸 — **Director 판정(2026-07-17)으로 폐기 확정**(P02 대체 동작은 파트4 오너 육안 PASS로 검증 완료 / P03 전제 소멸은 Director 핀 검증으로 확정, 잔여 런타임 확인은 P4A-11이 F9b에서 수행). 상세: [[파트3_연출_완료]]
updated: 2026-07-17
---

# 파트3 막기·치유 연출 — TC

> 대상: 승인 계획서 `humble-purring-glacier.md` §파트3 · [[파트2_SPD_TC]](ID·컬럼 규약 계승) · [[언리얼_MCP_실전노하우]] §34 (78)~(83)
> **qa-critic 적대적 검토 산출물 — 검출·TC설계만.** TC 실행=verifier, 게이트 판정=Director.
> 본 문서의 모든 "실측"은 **2026-07-17 라이브 에디터 직접 조회**(`find_nodes`/`get_node_infos`/`list_variables`/`ObjectTools.get_properties`/`DataTableTools.get_rows` + uasset 바이너리 grep) 결과다. **Director 실측 3건은 전부 확증**했고, **계획서 수정 5건 중 3건이 명세대로 구현하면 동작하지 않음을 확정**한다.
#projectTP/전투완성

---

## 0. 범위 & 판정도구

**판정도구 약칭**(파트1·2 계승): **GRAPH**=정적 노드조회(`find_nodes(title="")`+`get_node_infos`) / **PIE**=인스턴스 프로퍼티(`ObjectTools.get_properties`, `UEDPIE_0`) / **LOG**=`projectTP.log` grep / **DT**=`DataTableTools.get_rows` / **파일**=디스크 grep·mtime / **CMP**=컴파일0 / **오너**=육안(불차단).
**★**=게이트 / **★★**=최우선 / **★★★**=최강.

> ⚠ MCP 호출 형식 §34 (78): `call_tool(toolset_name="editor_toolset.toolsets.blueprint.BlueprintTools", tool_name="find_nodes", arguments={"graph":{"refPath":"..."},"title":""})`.
> ⚠ `ObjectTools.get_properties`의 인자명은 **`instance`/`properties`**다(`object`/`property_names` 아님 — 실측 확정).
> ⚠ PIE 액터 refPath: `/Game/Stages/UEDPIE_0_map_battle_octopath.map_battle_octopath:PersistentLevel.BP_BattleSpawnPoint_C_#`.
> ⚠ **PIE를 켠 채로 저장 금지**(§34 (81) — PIE 중엔 저장 경로가 막힌다).

**총 38건** — GRAPH 18 · PIE 11 · 회귀 9.

---

## 1. 착수 전 실측 기준선 (본 문서가 확정 — 인용 시 이 값 기준)

### 1-1. Director 실측 3건 — **전부 확증**

| Director 주장 | 실측 | 판정 |
|---|---|---|
| `ExecutionSequence`가 3개, Smear는 **`_0`**(position -1150,100): `execute←CallFunction_15`, `then_0→CallFunction_17`, `then_1→CallFunction_117` | **완전 일치**. `CallFunction_117`=`트랜스포메이션\|SetWorldLocation`(self←`VariableGet_28` 씬컴포넌트) | ✅ 확증 |
| `BreakStruct_1`(`Utilities\|Struct\|BreakFMotionsRow`, position **-1200,300**) = 같은 그래프 인접, 입력 ← `GetDataTableRow_1` | **완전 일치** | ✅ 확증 |
| `FrameCount`(idx4)→`CallFunction_202` 연결 / **`IsAttackFamily`(idx6) 미배선** / `EndBehavior`(idx7) 미배선 / 나머지 전부 `[]` | **완전 일치**. `IsAttackFamily`는 **부울** = Branch 직결 가능(형변환 불요) | ✅ 확증 |
| **⇒ #4는 브리징 불필요, 같은 그래프 직결** | **위상학적으로 옳다.** 추가 확증: `CallFunction_13 → GetDataTableRow_1 → VariableSet_18/19 → IfThenElse_8 → CallFunction_14 → CallFunction_15 → ExecutionSequence_0`은 **단일 선형 exec 체인** → `BreakStruct_1`은 smear 시점에 **이번 호출의 값**을 갖는다(stale 아님) | ✅ **확증 — 이전 검토자의 "크로스 액터 브리징" 지적은 오진, Director 정정이 옳다** |

### 1-2. 계획서 주장 검증

| 계획서 주장 | 실측 | 판정 |
|---|---|---|
| `BreakFSkillsRow`(`BreakStruct_0`)가 소비하는 필드는 `MotionRow` 단 하나 | **정확.** idx5 `MotionRow`→`VariableSet_11(SetPendingMotionRow)` **만** 연결. **`Kind`(idx4)·`Target`(idx6) 포함 나머지 22핀 전부 `connected_pins:[]`** | ✅ 일치 |
| `CallFunction_165`(WalkForward) 분기 없이 무조건 호출 | **정확.** `execute←CallFunction_169(PrintString).then`, 분기 0 | ✅ 일치 |
| `GetAttackPointForTeam(bIsParty)`는 타겟 인자가 없다 | **정확.** 나아가 **`WalkForward`(CustomEvent_8) 자체가 입력 파라미터 0개** | ✅ 일치 |
| **죽은 변수 `AttackPointOverride`** — 참조 1개(WalkForward의 IsValid), **Set이 전체에 0개** | **정확.** `VariableGet_31` 1노드(→`MacroInstance_13.InputObject` + `CallFunction_122(GetActorLocation)` 2핀). **바이너리 grep `SetAttackPointOverride`: Manager 0 · SpawnPoint 0** | ✅ 일치 |
| `AttackPointOverride`는 이 문제를 위해 설계됐다가 배선만 안 된 훅 | **정확.** `WalkForward → IsValid(AttackPointOverride) ? SetWalkTargetLoc(override 위치) : GetAttackPointForTeam 폴백` — 훅이 **이미 완성돼 있고 Set만 없다** | ✅ 일치 |
| `IfThenElse_6` 조건 = 타겟-시전자 거리 < 1.0 | **정확.** `PromotableOperator_13`=`수학\|플로트\|float<float`(A←`VectorLength(targetLoc − casterLoc)`, B=리터럴 `1.0`) | ✅ 일치 |
| `CallFunction_2`(PlayHurtReaction) 무조건 호출 | **정확.** `execute←CallFunction_1(ResolveHit).then`, self←`GetArrayItem_0`(=**타겟**), **`then`=`[]` 종단** | ✅ 일치 |
| **#5를 `dmg 부호`로 게이팅 가능** | ❌ **오진.** `CallFunction_1`(`\|ResolveHit`)의 **출력 핀은 `then`(실행) 하나뿐 — 데미지 반환값이 없다.** dmg 부호는 이 지점에 **데이터 소스로 존재하지 않는다** | ❌ **정정(N4)** |
| **#3을 `Target` 종류 기반으로** | ❌ **불충분.** 가장 자연스러운 `Target=="SELF"`는 **5스킬 전부에 대해 현행과 바이트 동일한 no-op** | ❌ **정정(N2, High)** |
| **#4를 `IsAttackFamily`로 게이팅** | ❌ **불충분.** 치유의 모션(row11 casting2)은 **`isAttackFamily=true`** → 치유 잔상은 안 없어진다 | ❌ **정정(N3, High)** |
| **#1·#3이 `BreakStruct_0.Target`을 읽을 수 있다** | ❌ **불가.** `BreakStruct_0`의 소스 `GetDataTableRow_0`이 **WalkForward·IfThenElse_6보다 exec 하류** | ❌ **정정(N1, High·최우선)** |
| 막기 자세 유지: `bFreeze`가 SpawnPoint 26개 변수에 없음 | 변수는 **28개**(파트2가 `Spd`·`SpdOverride` 추가) — **`bFreeze` 없음 확인**. ⚠ 바이너리 grep은 `bFreeze`×3을 잡지만 §34(82) 한계(정황≠증명)대로 **변수 목록이 진실** | ✅ **범위 밖 판단 유지**(TC 없음) |

### 1-3. `EnterExecuting` exec 순서 (본 문서가 확정 — 모든 TC의 근거)

```
CallFunction_164 → CallFunction_23(HideAll) → CallFunction_169(PrintString)
  → CallFunction_165 (WalkForward)      ★#1 대상 ─┐
  → CallFunction_166 (Delay 0.55s)                │ 이 구간엔
  → IfThenElse_14 (Condition ← bCamActionEnabled) │ BreakStruct_0가
      ├ then → MacroInstance_16/17/18/19 (IsValid×4)   아직 유효하지 않다
      │          → IfThenElse_6 (dist < 1.0)  ★#3 대상 ─┘
      │              ├ then → GetDataTableRow_0        ★★ BreakStruct_0 소스 최초 실행
      │              └ else → CallFunction_229(SetActorLocation ActionCamDynamic) → CallFunction_231 → …
      └ else → GetDataTableRow_0                       ★★ (동)
  → GetDataTableRow_0 (DT_Skills, RowName←StringToName(PendingSkillId))  ※ exec 소스 3개(머지)
      ├ then         → VariableSet_11 (SetPendingMotionRow ← BreakStruct_0.MotionRow, self=ActiveUnit)
      └ RowNotFound  → VariableSet_12
  → CallFunction_0 (PlayAttack, self=ActiveUnit)  ※ exec 소스 2개(머지) → SpawnPoint의 smear 체인 기동
  → ExecutionSequence_1 → … → MacroInstance_2 → CallFunction_1(ResolveHit) → CallFunction_2(PlayHurtReaction) ★#5 대상 → [종단]
```
- `bCamActionEnabled` **CDO 기본값 = `true`**(실측) → `IfThenElse_14.then` 경유 = **`IfThenElse_6`은 도달 가능**. #3 대상은 살아 있다.
- `CallFunction_167`(WalkBack) exec 소스 **2개**: `MacroInstance_20.IsNotValid`(에러 폴백) + `MacroInstance_25.Completed`(정상). self=ActiveUnit.
- 타겟 = `GetArrayItem_0` = `SelectedTargets[**리터럴 0**]`. `MacroInstance_18`이 IsValid 가드 → None 역참조는 봉인돼 있음.
- 카메라 `Normalize`(`CallFunction_220`) **Tolerance=0.0001** → 0벡터 입력 시 **ZeroVector 반환(NaN 아님)**.

### 1-4. 데이터 실측 (**DT 직접 조회** — CSV 미러 아님)

**DT_Skills** — 5스킬 전량

| Row | kind | motionRow | **target** | category | primaryTargetGroup | powerRate |
|---|---|---|---|---|---|---|
| 31000000 기본공격 | `PHYS` | 5 | `ENEMY1` | ATTACK | SINGLE_ENEMY | 1.0 |
| 31001000 베기 | `PHYS` | 5 | `ENEMY1` | SKILL | SINGLE_ENEMY | 1.3 |
| 32001000 파이어볼 | `MAG` | 10 | `ENEMY1` | MAGIC | SINGLE_ENEMY | 1.7 |
| **33001000 막기** | `DEF` | **15** | **`SELF`** | DEFEND | SELF | **0.0** |
| **34001000 치유** | `HEAL` | **11** | **`ALLY1`** | MAGIC | SINGLE_ALLY | 0.8 |

**DT_Motions** — 관련 행

| Row | rowIndex | **isAttackFamily** | endBehavior | 용도 |
|---|---|---|---|---|
| 60020000 run1 | 2 | `false` | LOOP | WalkForward/Back |
| 60050000 atk1 | 5 | **`true`** | REVERT_IDLE | 기본공격·베기 |
| 60100000 casting1 | 10 | **`true`** | REVERT_IDLE | 파이어볼 |
| **60110000 casting2** | **11** | **`true`** ⚠ | REVERT_IDLE | **치유** |
| 60120000 hurt | 12 | `false` | REVERT_IDLE | 피격 |
| **60150000 block** | **15** | **`false`** ✅ | FREEZE_LAST | **막기** |

> 🚨 **`Target`·`Kind`는 enum이 아니라 `스트링`이다**(BreakStruct_0 idx6·idx4 실측). 게이팅은 **문자열 비교**가 되며, UE의 문자열 `==`는 **`Equal Exactly (String)`(대소문자 구분)** 과 **`Equal, Case Insensitive (String)`** 두 오버로드가 존재한다 → **리터럴 오타·대소문자 불일치 = 무음 false**(P3-G07).

### 1-5. 게이팅 소스 적합성 (Director 질의 §"게이팅 조건의 소스"에 대한 답 — 표)

| # | 판별해야 하는 것 | **옳은 소스** | 현행 5스킬 결과 | 부적합 소스와 이유 |
|---|---|---|---|---|
| **#1** WalkForward 생략 | 시전자가 이동하는가 | **`Target`**: `SELF`→생략 | 막기만 생략 | `Kind==DEF`는 **우연히** 일치(SELF↔DEF 상관) |
| **#2** 걸음 목적지 | 어디로 걷는가 | **`Target`**: `ALLY1`→override | 치유만 override | — |
| **#3** 카메라 생략 | 타겟이 적진 쪽인가 | **`Target != "ENEMY1"`** | 막기·치유 생략 | **`Target=="SELF"`는 no-op**(N2) |
| **#4** 잔상 | 참격 비주얼인가 | **`IsAttackFamily` 단독 불가**(N3) | — | `IsAttackFamily`: 치유(row11)=true → 실패 |
| **#5** 피격 플린치 | 타겟이 피해를 입었나 | **`Target == "ENEMY1"`** | 공격 3종만 플린치 | **`dmg 부호` 불가**(N4, ResolveHit 반환값 없음) / `PowerRate>0`은 **치유 0.8>0 → 실패** |

**⇒ Director 질의 "5건이 서로 다른 소스를 쓰면 일관성이 깨진다"에 대한 답**: **#1·#2·#3·#5 네 건 모두 `Target` 단일 축으로 통일 가능하다.** `Kind`가 꼭 필요한 건 #4뿐이고, #4는 어차피 별도 결정이 필요하다(N3). → **"Target = 공간 축(어디로/무엇을 향해), Kind = 의미 축(해로운가)"** 로 축을 나누되, **현행 5스킬에선 두 축이 완전 상관**(SELF↔DEF, ALLY1↔HEAL, ENEMY1↔PHYS/MAG)이라 **어느 쪽을 써도 오늘은 통과한다** — 그래서 잘못 고른 소스는 **오늘 검출 불가·나중에 폭발**한다.

**Director 질의 "SELF인데 Kind가 DEF가 아닌 스킬이 생기면?" 에 대한 답**: 실재하는 위험이다. 예 `Kind=BUFF, Target=SELF`인 자기강화가 추가되면 —
- #1이 `Target`이면 → 이동 생략 ✅
- #5가 `Kind`의 **부정목록**(`DEF`·`HEAL`이면 플린치 안 함)이면 → **BUFF는 목록에 없음 → 자기가 피격 플린치** ❌
**⇒ 규칙: 게이팅 술어는 반드시 "해로운 것의 허용목록"으로 쓴다(`Kind ∈ {PHYS,MAG}` 또는 `Target == ENEMY1`), "무해한 것의 부정목록"(`Kind ∉ {DEF,HEAL}`)으로 쓰지 않는다.** 전자는 새 Kind 추가 시 **안전측으로 실패**(연출 누락), 후자는 **위험측으로 실패**(오연출). → **P3-G03**이 이 규칙을 강제한다.

---

## 2. ★★ 착수 전 Director 결정 3건 (결정 없이 구현 착수 금지)

> 아래 3건은 **TC로 판정할 사항이 아니라 판정 기준 자체를 정하는 결정**이다. 미결 상태로 구현하면 gameplay-engineer는 계획서 문구대로 배선하고, **GRAPH 게이트는 PASS하며, 증상은 그대로 남는다.**

**결정①(N1) — `Target`을 WalkForward 시점에 읽을 방법**: `GetDataTableRow_0`이 하류라 `BreakStruct_0.Target`은 이번 턴 값이 아니다. 택1 —
- **(a) `GetDataTableRow_0`을 `CallFunction_23`(HideAll) 직후로 이설** — 구조적 정답. 단 exec 소스 3개(`MacroInstance_23.Completed`/`IfThenElse_14.else`/`IfThenElse_6.then`) 재배선 필요.
- **(b) 게이팅 전용 `GetDataTableRow`(DT_Skills) 1개를 WalkForward 상류에 신설** — RowName 순수체인(`StringToName(CallFunction_52(PendingSkillId))`)이 이미 있어 **재사용만 하면 됨. 기존 머지 3개 무접촉 = 최저위험.** ← **권고**
- **(c) 순수 함수 `GetSkillTarget(PendingSkillId)` 신설** — 가장 깨끗, 어디서나 호출 가능.
- ❌ **(d) `PendingSkillId` 리터럴 비교**(`==33001000`) — 스캐폴드 규약(리터럴 금지, [[파트2_SPD_TC]] P2-R07) 위반. 채택 금지.

**결정②(N3) — 치유 잔상이 범위인가**: 계획서 #4 증상란은 *"**막기·치유**에 참격 잔상"* 이라 **둘 다 범위**로 읽히나, **아침 오너 육안 게이트의 치유 항목엔 "참격 잔상 없음"이 없다**(막기 항목에만 있음). `IsAttackFamily`로는 **막기만** 고쳐진다. 택1 —
- **(a) 범위 밖 선언** — `IsAttackFamily` 단독 배선으로 종료. 오너 게이트는 통과. **치유 잔상은 존치**(P3-P07이 문서화).
- **(b) 데이터 수정** — `motions.csv` `60110000`의 `IsAttackFamily` TRUE→FALSE + DT 리임포트. **`IsAttackFamily`는 소비처가 프로젝트 전역 0개**(실측)라 **오늘 회귀 위험 0**. 파이어볼(row10)은 `true` 유지 → 무변경. ← **최소비용 권고**
- **(c) `Kind` 브리징** — `VariableSet_11`(`SetPendingMotionRow`) 옆에 `ActiveUnit.SetPendingIsHarmful(Kind ∈ {PHYS,MAG})` 1노드 추가. **이미 쓰는 패턴과 동일**이라 Director가 기각한 "크로스 액터 브리징"과는 다른 물건.

**결정③(N2) — #3의 조건식**: `Target=="SELF"`는 no-op. **`(Target != "ENEMY1") OR (dist < 1.0)`** 권고 — 기존 퇴화 가드를 **논리합으로 보존**하면 신규 경로(N7)가 아예 생기지 않고 치유는 고쳐진다. 비용 = `OR` 노드 1개.

---

## 3. GRAPH 정적 (P3-G##) — 18건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P3-G01** | **★★★** | **#1·#3의 `Target` 소스가 exec 상류에서 확정** — ⚠**"`Target` 핀에 연결됐다"로 판정 금지** | GRAPH exec 트레이스 | #1의 Branch 조건이 읽는 DT 조회 노드가 **`CallFunction_165`(WalkForward)보다 exec 상류** ∧ #3의 `IfThenElse_6` 조건이 읽는 DT 조회 노드가 **`IfThenElse_6`보다 exec 상류**. 결정①(b) 채택 시: 신설 `GetDataTableRow`의 `execute`가 `CallFunction_23.then`~`CallFunction_165.execute` 구간에 존재 | **N1(High·최우선)** — 실측상 `GetDataTableRow_0`은 WalkForward·IfThenElse_6의 **하류**. 기존 `BreakStruct_0`을 그대로 물리면 **직전 턴 값(또는 첫 턴 빈 문자열)** 을 읽는다. **계획서 문구("`BreakStruct_0`의 `Target` 핀으로 게이팅")를 그대로 따르면 반드시 이 버그가 난다** → ✅**PASS**(2026-07-17 01시경, Director 직접 핀조회 — `CallFunction_169(PrintString) → GetDataTableRow_1`이 `WalkForward`(`CallFunction_165`)·`IfThenElse_6`보다 exec 상류 확정. [[파트3_연출_완료]] §4) |
| **P3-G02** | **★★★** | **#1 Branch의 미채택 경로가 종단이 아니다** — 소프트락 봉인 | GRAPH | #1 Branch의 **`then`·`else` 양쪽 모두** `connected_pins != []` ∧ 두 경로가 **`IfThenElse_14`(또는 `CallFunction_166`)로 합류** ∧ `EnterExecuting`에서 **exec 미연결 종단이 신규로 0개** | **Critical 위험** — WalkForward를 건너뛰는 경로를 **미연결로 두면 PlayAttack·ResolveHit·EnterTurnEnd가 전부 실행되지 않아 턴 영구 정지**(=전투 진행 불가). 계획서 §파트1 12번이 잡은 "F4부터 잠복하던 미연결 then"과 **동일 계열** — 이 프로젝트에서 이미 1회 터졌다 → ✅**PASS**(2026-07-17 01시경, Director 직접 핀조회 — `IfThenElse_4`(`Target=="SELF"`) `then→CallFunction_166`(Delay)·`else→CallFunction_165`(WalkForward)`→166` 양쪽 다 하류 재합류 확인, 미연결 종단 0. [[파트3_연출_완료]] §4) |
| **P3-G03** | **★★** | **#5 술어가 허용목록** | GRAPH `get_node_infos` | `CallFunction_2`(PlayHurtReaction) 상류 Branch 조건 == **`Target == "ENEMY1"`**(권고) 또는 **`Kind ∈ {"PHYS","MAG"}` 허용목록**. ⚠ **`Kind != "DEF" && Kind != "HEAL"` 형태(부정목록)면 FAIL** | **N5(Medium)** · §1-5 — 부정목록은 새 Kind 추가 시 **위험측 실패**(오연출). Director 질의 "SELF인데 Kind가 DEF가 아닌 스킬" 시나리오의 직접 대응 → ✅**PASS**(2026-07-17 01시경, Director 직접 핀조회 — `IfThenElse_5.Condition ← CallFunction_26`(`EqualExactly`, `Target=="ENEMY1"`) 허용목록 형태 확인(부정목록 아님), `then→CallFunction_2`(PlayHurtReaction). [[파트3_연출_완료]] §4) |
| **P3-G04** | **★★** | **#3 조건이 `Target=="SELF"`가 아니다** | GRAPH | `IfThenElse_6.Condition` 상류에 **`"SELF"` 단독 비교가 아님**. 결정③ 채택 시 `(Target != "ENEMY1") OR (dist<1.0)` ∧ `PromotableOperator_13`(`float<float`, B=`1.0`) **생존** | **N2(High)** — `SELF ⟺ dist<1.0`이 현행 5스킬에서 **논리적으로 동치**라 `Target=="SELF"`는 **바이트 동일 no-op**. "조건을 Target 기반으로 바꿨다"는 GRAPH 확인은 이 no-op를 **통과시킨다** → ✅**PASS**(2026-07-17 01시경, Director 직접 핀조회 — `IfThenElse_6.Condition ← CommutativeAssociativeBinaryOperator_1`(OR), `then`/`else` 기존 보존 확인(no-op 아님, P3-G12 겸 확인). [[파트3_연출_완료]] §4) |
| **P3-G05** | **★★** | **`AttackPointOverride` Set/Clear가 모든 경로를 지배** | GRAPH exec 트레이스 | `SetAttackPointOverride`(신설)가 **#1 Branch보다 exec 상류**에 위치 ∧ 그 지점을 지나는 **모든 스킬**(SELF/ALLY1/ENEMY1)이 Set 또는 Clear를 **반드시 1회 통과**. ⚠ Set이 Branch의 한쪽 arm에만 있으면 FAIL | **N6(High)** — Director 질의(생명주기). Set만 있고 Clear가 없으면 **다음 턴 다른 스킬이 stale 값을 물려받아 엉뚱한 곳으로 무음 이동**. `IsValid(AttackPointOverride)`가 분기 조건이므로 **None 복귀 지점이 필수** → ✅**PASS**(2026-07-17 01시경, Director 직접 핀조회 — `VariableSet_5`(Clear)의 execute ← `GetDataTableRow_1.then` AND `.RowNotFound`(2소스 병합=무조건 실행) 확인. [[파트3_연출_완료]] §4) |
| **P3-G06** | **★★** | **#2 Set이 `ALLY1`에만** — 회귀 봉인 | GRAPH | `SetAttackPointOverride`의 값이 **`Target=="ALLY1"`일 때만** `SelectedTargets[0]`, **그 외 전부 `None`**. ⚠ **무조건 `SelectedTargets[0]` 대입이면 FAIL** | **N8(High)** — 무조건 대입하면 **ENEMY1 공격도 override 경로**를 타 `GetAttackPointForTeam` 대신 **적 유닛 실제 위치로 걸어간다** → 기본공격·베기·파이어볼 연출 변경 = **"완전 무변경" 위반**. 무음(로그 없음) → ✅**PASS**(2026-07-17 01시경, Director 직접 핀조회 — `VariableSet_6`(Set)의 execute ← `IfThenElse_3`(`ALLY1`)`.then` 단독 확인(무조건 대입 아님). [[파트3_연출_완료]] §4) |
| **P3-G07** | ★ | **문자열 비교 노드·리터럴 정확도** | GRAPH `get_node_infos` | 비교 노드 `type_id`가 **대소문자 정책이 확정된 오버로드** ∧ 리터럴이 DT 값과 **바이트 일치**(`SELF`/`ALLY1`/`ENEMY1`/`PHYS`/`MAG` — **전부 대문자**) ∧ 앞뒤 공백 0 | **N9(Medium)** — `Target`/`Kind`는 **enum이 아니라 스트링**(실측). UE엔 `Equal Exactly (String)`(구분)·`Equal, Case Insensitive (String)`(무시)가 **둘 다 존재** → `"Self"`로 적으면 **무음 false → 게이팅 전체 무력화**. §34(79)(로캘로 노드명이 다름)·(80)(승격은 배선 후 확인) 계열 |
| **P3-G08** | ★ | **#4 `IsAttackFamily` 직결** | GRAPH | `BreakStruct_1` 출력 **idx6**(`IsAttackFamily_18_…`, 부울)이 신설 Branch의 `Condition`에 **직결**(형변환 노드 0) ∧ 그 Branch가 `ExecutionSequence_0.then_1`과 `CallFunction_117` **사이** | Director 실측 확증분 · **브리징 불요 확정** |
| **P3-G09** | ★ | **#4 Branch의 미채택 경로 처리** | GRAPH | 신설 Branch의 잔상 미실행 경로가 **`CallFunction_93`(SetMaterial)으로 합류** ∨ **종단이어도 무해함이 확인**됨. ⚠ `CallFunction_117.then → CallFunction_93 → CallFunction_95` 체인이 **끊기면 안 됨** | **N10(Medium)** — `CallFunction_117`(smear)의 `then`은 **`CallFunction_93`(SetMaterial)로 이어진다**. Branch로 117을 건너뛰면서 93까지 같이 건너뛰면 **머티리얼 복원이 안 돼 잔상 머티리얼이 눌러붙을 수 있다**. `then_1` 서브체인 전체를 스킵할지 117만 스킵할지 **명시 필요** |
| **P3-G10** | ★ | **`GetDataTableRow_1.RowNotFound` 경로의 #4 거동** | GRAPH | `GetDataTableRow_1.RowNotFound → VariableSet_19 → IfThenElse_8 → … → ExecutionSequence_0` 경로에서 신설 Branch가 읽는 `IsAttackFamily`는 **기본값 false** → 잔상 생략. 이 거동이 **의도된 것으로 문서화**됨 | **N11(Low)** — RowNotFound에서도 smear 체인에 **합류한다**(실측: `IfThenElse_8.execute` ← `VariableSet_18.then` ∧ `VariableSet_19.then`). 그때 `BreakStruct_1`은 **기본 구조체** → `IsAttackFamily=false`. ⚠ **`DT_Motions`의 RowNotFound는 PrintString이 없어 무음**(DT_JobStats와 달리 grep 불가) |
| **P3-G11** | ★ | **`CallFunction_2.then` 종단 유지** | GRAPH | `CallFunction_2`(PlayHurtReaction)의 `then` == `[]` **유지**(현행과 동일) | 실측 — PlayHurtReaction은 **리프 노드**라 게이팅이 **하류 고아를 만들지 않는다** = #5는 5건 중 **구조적으로 가장 안전**. 기록으로 남겨 오배선 시 대조 |
| **P3-G12** | ★ | **`IfThenElse_6` 양 갈래 무손상** | GRAPH | `IfThenElse_6.then → GetDataTableRow_0` **유지** ∧ `else → CallFunction_229`(SetActorLocation ActionCamDynamic) **유지** | **F7a 소프트락 회귀 봉인** — `then`은 F4부터 미연결로 잠복하다 SELF 스킬이 처음 밟아 터진 이력. **조건만 바꾸고 배선은 건드리지 말 것** |
| **P3-G13** | ★ | **WalkBack 게이팅 여부 명시** | GRAPH | `CallFunction_167`(WalkBack)의 exec 소스 **2개**(`MacroInstance_20.IsNotValid`·`MacroInstance_25.Completed`) **무변경**. 게이팅했다면 **양쪽 소스 모두**에 동일 술어 적용 ∧ 미채택 경로 종단 아님 | **N7·Director 질의(WalkBack)** — 계획서 #1은 WalkForward만 언급. WalkBack을 한쪽 소스만 게이팅하면 **에러 폴백 경로에서만 복귀 안 함** = 유닛이 적진에 영구 잔류 |
| **P3-G14** | ★ | **`Delay(0.55)` 처리 명시** | GRAPH | `CallFunction_166`(Delay, Duration=**0.55**) 리터럴 **무변경** ∧ #1 미채택 경로가 Delay를 **통과하는지/건너뛰는지**가 결정되어 그래프에 반영 | **N12(Low)** — WalkForward는 **CustomEvent(비동기 디스패치)** 라 Manager는 `Delay(0.55)`로 걸음을 기다린다. 걸음을 생략해도 Delay를 통과시키면 **막기 전에 0.55초 정지**가 남는다(무해하나 오너 육안 대상). 건너뛰면 타이밍이 0.55초 당겨져 **원장 무관·연출만 변경** |
| **P3-G15** | ★ | **컴파일 0** | CMP | `BP_BattleManager`·`BP_BattleSpawnPoint` **에러 0 · 신규 경고 0** | 표준 |
| **P3-G16** | ★ | **파트3 편집 범위 봉인** | GRAPH diff | 편집 대상은 **정확히**: `BP_BattleManager:EventGraph`(#1 Branch·#2 Set·#3 조건·#5 Branch + 결정①의 DT 조회) + `BP_BattleSpawnPoint:EventGraph`(#4 Branch) + `BP_BattleSpawnPoint` 변수(`SetAttackPointOverride` 노출) + (결정②(b) 시) `DT_Motions` 1행. **그 외 0** — 특히 **`ResolveHit`·`GetOutgoingAtkMult`·`ApplySkillEffects`·`TickStatusesAtTurnEnd`·`EnterTurnStart`·`SortTurnQueueBySpd` 본체 diff 0** | 파트1 P1-G20·파트2 P2-G15 계승 · P3-R02(원장 diff 0)의 구조적 근거 |
| **P3-G17** | | **`bCamActionEnabled` 전제 유지** | GRAPH/PIE | `bCamActionEnabled` CDO == **`true`** ∧ `IfThenElse_14.Condition ← GetbCamActionEnabled` **무변경** | 실측 — **false면 `IfThenElse_6`이 통째로 도달 불가 = #3이 no-op**. #3 작업의 **대전제**라 명시 |
| **P3-G18** | | **카메라 수학 무변경** | GRAPH | `CallFunction_220`(`수학\|벡터\|Normalize`) **Tolerance == `0.0001`** ∧ `PromotableOperator_12`(target−caster) ∧ `PromotableOperator_22`(cam loc) **diff 0** | N7 보조 — #3은 **조건만** 바꾼다. 수학을 건드리면 ENEMY1 카메라가 회귀 |

---

## 4. PIE 런타임 (P3-P##) — 11건

> 공통: 파트2 확정 매핑 — A1=`_C_0` B1=`_C_4` A2=`_C_9` B2=`_C_5` A3=`_C_2` B3=`_C_6` A4=`_C_3` B4=`_C_7`. 턴 순서 `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]`(마법사 4기 먼저).
> **막기=전사 계열 / 치유=마법사 계열**로 오너·verifier가 스킬 메뉴에서 선택해 유도한다.

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P3-P01** | **★★★** | **막기: 시전자가 제자리** | PIE 프로퍼티 | 막기 시전 턴 전 구간에서 시전자 `GetActorLocation` ≈ `HomeLocation`(오차 <1.0) ∧ **`WalkTargetLoc`가 적진 좌표로 갱신되지 않음** | 계획서 #1 · 오너 육안 게이트("제자리에서 방어"). **`WalkTargetLoc`(SpawnPoint 변수)가 핵심 판정면** — WalkForward 진입 시 **동기적으로 1회 확정**되므로 애니메이션 타이밍에 의존하는 위치 샘플링보다 **결정론적** |
| **P3-P02** | **★★★** | **치유: 아군 쪽으로 이동** | PIE 프로퍼티 | 치유 시전 턴에 시전자 `WalkTargetLoc`의 (X,Y) ≈ **힐 대상 아군의 `GetActorLocation`**(X,Y) ∧ **적진 좌표가 아님** ∧ `AttackPointOverride` == 그 아군 액터 | 계획서 #2 · 오너 육안("아군 쪽으로 이동"). `WalkForward`는 `BreakVector(GetActorLocation(AttackPointOverride))`의 **X,Y만** 쓴다(실측: `CallFunction_123.Z`=`[]` 미연결) → **Z는 비교 대상 아님** |
| **P3-P03** | **★★★** | **`AttackPointOverride` stale 0** — 무음 오염 봉인 | PIE 프로퍼티 ×전 유닛 ×3시점 | ① 전투 시작 직후 8기 전부 `None` ② **치유 턴 종료 후 시전자 `None`으로 복귀** ③ **그 시전자의 다음 턴(ENEMY1 스킬) 시작 시 `None`** ∧ 그 턴 `WalkTargetLoc` == 적진 공격지점(치유 대상 좌표 아님) | **N6(High)** — Director 질의. 미클리어 시 **마법사가 다음 파이어볼 때 자기 후방 아군에게 걸어가 허공을 때린다**. ⚠ **원장(데미지·턴)엔 안 찍히므로 P3-R02 diff-0로는 검출 불가** — 이 TC가 **유일한 탐지 수단** |
| **P3-P04** | **★★** | **막기: 자기가 피격 플린치 안 함** | PIE + 오너 | 막기 턴에 시전자 `PendingMotionRow` **≠ 12**(hurt) ∧ 육안으로 피격 모션 없음 ∧ 막기 모션(row **15**) 재생 | 계획서 #5 · 오너 육안 게이트 **명문**. 현행 증상의 직접 반증 |
| **P3-P05** | **★★** | **치유: 아군이 피격 플린치 안 함** | PIE + 오너 | 치유 턴에 **힐 대상 아군**의 `PendingMotionRow` ≠ 12 ∧ 육안으로 피격 모션 없음 ∧ **HP는 정상 회복** | 계획서 #5 · 오너 육안 게이트 **명문** |
| **P3-P06** | **★★** | **막기: 참격 잔상 없음** | 오너 육안 + GRAPH | 막기(motionRow 15 → `isAttackFamily=false`) 시 `CallFunction_117`(SetWorldLocation smear) **미실행** ∧ 육안 잔상 0 | 계획서 #4 · 오너 육안 게이트 **명문**. **DT 실측상 row15=false라 `IsAttackFamily` 게이팅으로 확실히 해결됨** |
| **P3-P07** | **★★** | 🚨 **치유: 참격 잔상 — Director 결정② 확인** | 오너 육안 | **결정②(a)** 채택 시: 치유 잔상 **존치**를 기대값으로 기록(FAIL 아님, **이월**). **결정②(b)/(c)** 채택 시: 잔상 **0** | **N3(High)** — `IsAttackFamily` 단독 배선으론 **치유(row11=true) 잔상이 남는다**. **이 TC는 "무엇이 옳은가"가 아니라 "결정이 내려졌는가"를 강제한다** — 미결이면 구현자는 계획서대로 배선하고 GREEN 보고 후 증상 존치 |
| **P3-P08** | ★ | **치유: 카메라 역방향 컷 없음** | PIE + 오너 | 치유 턴에 `ActionCamDynamic`의 `GetActorLocation`이 **직전 프레임 대비 급변(180° 반대편 점프) 없음** ∧ 육안 역방향 컷 0 | 계획서 #3 · 오너 육안 게이트 **명문** |
| **P3-P09** | ★ | **에러·경고 0** | LOG grep | `"Accessed None"` ∧ 한국어 로케일 **`"None에 액세스"`** ∧ `"out of bounds"` ∧ `Attempted to (get\|access)` **각 0건** ∧ 신규 `Blueprint Runtime Error` 0건 | 표준 · 파트2 P2-P07 계승. #2가 `SelectedTargets[0]`을 override에 넣으므로 **빈 배열 시 None 대입** 가능성 |
| **P3-P10** | ★ | **WalkBack 제자리 복귀 무해** | 오너 육안 + PIE | 막기 턴 후반 `CallFunction_167`(WalkBack) 실행 시 **제자리 달리기(run1, row2) 모션이 보이지 않음** ∧ 최종 위치 == `HomeLocation` | **N7(PLAUSIBLE)** · Director 질의(WalkBack). 걸음을 생략해도 WalkBack은 **무조건 호출**된다(#1은 WalkForward만 게이팅). WalkForward/WalkBack은 이동 기계(`MacroInstance_16`→`CallFunction_140`)를 **공유**하므로, 거리 0에서 run 모션이 최소 1프레임 재생될 수 있다 → **육안 확인 필요** |
| **P3-P11** | | **첫 턴 게이팅 정상** | PIE | **PIE 진입 후 최초 스킬 시전**(A3=`_C_2`)에서 게이팅이 정상 — 특히 그 스킬이 ENEMY1이면 **정상 이동** | **N1 보조** — 결정①을 잘못 처리하면 **첫 턴은 `Target`이 빈 문자열**이라 거동이 다르다. 첫 턴은 **stale이 아니라 default**를 읽는 유일한 턴 = **N1의 가장 순수한 관측창** |

---

## 5. 회귀 (P3-R##) — 9건

| ID | 우선 | 검증 내용 | 판정방법 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P3-R01** | **★★★** | **ENEMY1 3종 완전 무변경** | 오너 육안 + PIE | 기본공격·베기·파이어볼에서 ① 적진으로 **걸어나감**(`WalkTargetLoc` == 적진 공격지점, **치유 대상 아님**) ② **카메라 컷 정상** ③ **참격 잔상 재생** ④ 타겟 **피격 플린치 재생** ⑤ WalkBack 복귀 — **5항 전부 현행과 동일** | Director 명시 요구("완전 무변경"). **N8(#2 무조건 Set)·N1(stale Target)·N2(#3 조건)이 전부 여기서 터진다** |
| **P3-R02** | **★★★** | **23턴 원장 diff 0** | LOG 원장 수집 | 파트2가 재수집한 신규 원장 대비 **diff 0**. 파트3은 **연출만** 바꾸므로 데미지·턴·순서가 **한 줄도** 달라지면 안 됨. 절차는 [[파트2_SPD_TC]] P2-R01과 동일(에디터 재시작 → PIE 완주 → `extract_battle_log.py`) | 파트1 diff-0 게이트 계승. ⚠ **한계 명시**: 원장은 **위치·카메라·잔상·플린치를 기록하지 않는다** → **P3의 증상 5건 중 어느 것도 원장으로는 검출 불가**. diff 0은 *"수치를 안 건드렸다"*만 증명 — **P3-P01~P08이 기능 증명** |
| **P3-R03** | **★★** | **막기 수치 효과 무변경** | LOG/PIE | 막기 다음 턴 피격 시 `bBlockActive`·`BlockValue`(0.5) 적용 → **데미지 반감 그대로**(30→15) | 계획서 §문제정의가 *"정작 다음 턴 30→15 반감될 때 **표시 0**"* 이라 적었으나 **수정 5건 어디에도 표시 항목이 없다** → **표시는 범위 밖**(N13). 최소한 **수치 반감이 안 깨졌는지**는 봉인 |
| **P3-R04** | ★ | **파트1 무접촉** | GRAPH | `ShowStart`/`ShowCancel`/`ShowEnd`/`HideAll` 4함수 **diff 0** ∧ `NotifyAttackButtonClicked` Start 분기 **diff 0** ∧ `StartBattle` diff 0. ⚠ `CallFunction_23`(`\|HideAll`)이 **#1 상류에 인접**하므로 결정①(b) 삽입 시 **오손상 주의** | 파트1 게이트 PASS(`7743d85`) 보호 |
| **P3-R05** | ★ | **파트2 무접촉** | GRAPH + PIE | `SortTurnQueueBySpd` **diff 0** ∧ `SetSpd`/`SelectInt` 서브그래프 diff 0 ∧ 8기 `spd` == {93,92,91,90,97,96,95,94} ∧ 첫 8턴 == `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]` | 파트2 게이트 보호 · P2-P01/P03 재통과 |
| **P3-R06** | ★ | **F7a 소프트락 회귀** | PIE | **SELF 스킬(막기)을 실제로 시전해 완주** — 턴이 정상 종료되고 다음 턴 진입. `IfThenElse_6.then` 경로가 **여전히 살아 있음** | **F4→F7a 이력 직접 회귀** — `then`이 미연결이던 시절 SELF 스킬이 처음 밟아 소프트락. #3이 조건을 바꾸면 **이 경로의 진입 조건이 바뀐다** → 재검증 필수 |
| **P3-R07** | ★ | **`DT_Motions` 변경 회귀**(결정②(b) 채택 시만) | DT + 파일 + 오너 | `60110000.isAttackFamily` == `false` ∧ **`60100000`(파이어볼)은 `true` 유지** ∧ 나머지 15행 **diff 0** ∧ `data/motions.csv` 미러 갱신 ∧ **디스크 mtime 갱신 + 바이너리 grep** | §34(81)(82) — DT 저장은 **API 반환값 신뢰 금지, 디스크로만 판정**. `IsAttackFamily` 소비처가 **전역 0개**(실측)라 다른 회귀 경로는 없음 |
| **P3-R08** | | **재전투 멱등** | PIE | End→Start 재전투 후 8기 `AttackPointOverride` 전부 `None` ∧ 막기·치유 연출이 첫 전투와 동일 | **N6 2차** — `ResetForBattle`은 `SetHp`·`SetbAlive`·`SetbBlockActive`·`SetBlockValue`뿐(파트2 실측) → **`AttackPointOverride`를 초기화하지 않는다**. 전투 종료 시 stale이 남으면 **다음 전투 첫 턴까지 오염**이 넘어간다 |
| **P3-R09** | | **문서 정정** | 문서 | ① 계획서 §파트3 표의 **#3·#4·#5 수정란**을 실측 기반으로 정정(N1·N2·N3·N4) ② §34에 **N1**(pure 노드의 impure 소스 exec 순서 함정) 등재 ③ `전투완성/plan.md` TC 상태 반영 | 계획서 5건 중 **3건이 명세대로면 미작동** — 다음 사람이 같은 함정을 밟는다 |

---

## 6. 신규 발견 — 계획서·§34에 없던 것 (14건: Critical 1 · High 6 · Medium 4 · Low 3)

> 심각도순. **CONFIRMED**=라이브 조회/산술로 확정 / **PLAUSIBLE**=논리상 의심, 실측 필요.
> 심각도 기준(프로젝트 규약): Critical(전투 진행 불가/크래시) > High(밸런스 붕괴/명세위반) > Medium > Low.

### Critical

- **N0 — #1·#5 Branch의 미채택 경로를 미연결로 두면 턴 영구 정지** `CONFIRMED`(구조) / `PLAUSIBLE`(발생)
  계획서는 #1·#5를 *"Branch로 게이팅"* 이라고만 적고 **미채택 경로의 목적지를 지정하지 않았다.**
  - **#1**: `CallFunction_165`(WalkForward)의 `then`은 `CallFunction_166`(Delay 0.55)→`IfThenElse_14`→…→`GetDataTableRow_0`→`PlayAttack`→`ResolveHit`→`EnterTurnEnd`로 **턴 전체를 끌고 간다**. Branch의 미채택 경로를 미연결로 두면 **막기를 고르는 순간 전투가 영구 정지**한다(=전투 진행 불가).
  - **#5**: 반대로 `CallFunction_2`(PlayHurtReaction)의 `then`은 **이미 `[]` 종단**(실측)이라 게이팅해도 **하류 고아가 생기지 않는다** → #5는 5건 중 **구조적으로 가장 안전**.
  이 프로젝트는 **동일 계열 사고 전력이 있다**(계획서 §파트1 12번: `MacroInstance_16~19`의 `Is Not Valid → exec 미연결`; F7a가 SELF 스킬로 처음 밟아 소프트락).
  → **P3-G02(★★★)** 로 봉인. **Director 직접 핀 원문 확인 권고.**

### High

- **N1 — `BreakStruct_0.Target`은 #1·#3 시점에 아직 유효하지 않다(exec 순서 역전)** `CONFIRMED` ← **최우선**
  계획서 #1: *"`BreakStruct_0`의 **`Target` 핀**으로 게이팅"*, #3: *"**`Target` 종류 기반**으로"*. **둘 다 물리적으로 불가능하다.**
  실측 exec 순서(§1-3): `CallFunction_165`(WalkForward) → `Delay(0.55)` → `IfThenElse_14` → [`IfThenElse_6`] → **`GetDataTableRow_0`** → `BreakStruct_0`.
  `BreakStruct_0`은 **순수(pure) 노드**이고 그 입력은 **impure 노드 `GetDataTableRow_0.ReturnValue`** 다. 순수 노드는 사용 지점에서 인라인 평가되지만 **읽는 값은 impure 노드가 마지막으로 써 둔 것**이다. `GetDataTableRow_0`이 아직 실행되지 않은 시점에 `Target`을 읽으면 —
  - **첫 턴**: 기본값 **빈 문자열 `""`**
  - **이후 턴**: **직전 턴 스킬의 `Target`**(ubergraph 프레임 잔류)
  어느 쪽이든 **이번 턴 값이 아니다.**
  **관측될 증상**(치명적으로 그럴듯하다):
  - 직전이 ENEMY1 · 이번이 막기 → stale `"ENEMY1"` → **막기가 그대로 걸어나간다 = 고치려던 버그가 안 고쳐짐**
  - 직전이 막기 · 이번이 기본공격 → stale `"SELF"` → **공격이 제자리에서 나간다 = ENEMY1 3종 회귀**(P3-R01 위반)
  → 즉 **"막기는 여전히 걸어나가고, 공격이 가끔 제자리에서 때린다"** — 턴 순서 의존이라 **간헐적**. `IsAttackFamily`(#4)는 SpawnPoint 안에서 `GetDataTableRow_1`이 **상류**라 무사한 것과 **정확히 대비**된다.
  → **P3-G01(★★★)** + **결정①**. **`compile 0`·"Target 핀이 연결됨" GRAPH 확인은 이 버그를 100% 통과시킨다.**

- **N2 — #3을 `Target=="SELF"`로 구현하면 현행 5스킬 전부에 대해 바이트 동일 no-op** `CONFIRMED`(산술)
  `IfThenElse_6`의 현행 조건은 `VectorLength(targetLoc − casterLoc) < 1.0`. 5스킬에 대해:
  | 스킬 | Target | dist<1.0 | Target=="SELF" | 두 조건 |
  |---|---|---|---|---|
  | 기본공격·베기·파이어볼 | ENEMY1 | false | false | **동일** |
  | 막기 | SELF | **true**(타겟==시전자) | **true** | **동일** |
  | 치유 | ALLY1 | false(아군은 다른 위치) | false | **동일** |
  → `SELF ⟺ dist<1.0`이 **논리적으로 동치**라 조건 교체가 **아무것도 바꾸지 않는다**. 특히 **치유는 여전히 `else` → `SetActorLocation(ActionCamDynamic)` → 180° 역방향 컷 존치** = 고치려던 증상 그대로.
  **옳은 조건은 `Target != "ENEMY1"`**(SELF ∧ ALLY1 → 카메라 생략). 권고형 **`(Target != "ENEMY1") OR (dist < 1.0)`** 은 퇴화 가드를 논리합으로 보존해 N7을 원천 차단.
  → **P3-G04(★★)** + **결정③**.

- **N3 — 치유의 모션이 `isAttackFamily=true`라 #4로는 치유 잔상이 안 없어진다** `CONFIRMED`(DT 직접 조회)
  계획서 #4 증상란: *"**막기·치유**에 참격 잔상"*. 실측:
  | 스킬 | motionRow | 모션 | **isAttackFamily** | `IsAttackFamily` 게이팅 결과 |
  |---|---|---|---|---|
  | 막기 | **15** | motion_block | **`false`** | 잔상 제거 ✅ |
  | **치유** | **11** | motion_casting2 | **`true`** ⚠ | **잔상 존치** ❌ |
  | 파이어볼 | 10 | motion_casting1 | `true` | 잔상 유지 ✅(무변경 요구와 일치) |
  `DT_Motions` 60110000의 memo가 스스로 *"**공격계열(마법)**/cast loop 70-72/F7 **치유**"* 라고 적고 있다 — **데이터가 치유 모션을 공격계열로 분류**한다. 즉 `IsAttackFamily`는 *"참격 잔상을 그릴 것인가"* 의 술어가 **아니라** *"모션 시트상 공격 계열인가"* 의 술어다. **두 개념이 계획서에서 동일시됐다.**
  ⚠ **오너 육안 게이트의 치유 항목엔 "참격 잔상 없음"이 없다**(막기에만 있음) → **범위 판단은 Director 몫**. → **결정②** + **P3-P07**(FAIL이 아니라 *"결정이 내려졌는가"* 를 강제).

- **N4 — #5의 제시 소스 `dmg 부호`는 존재하지 않는다** `CONFIRMED`
  계획서 #5: *"`Kind`/**dmg 부호**로 게이팅"*. 실측: `CallFunction_1`(`|ResolveHit`)의 **출력 핀은 `then`(실행) 하나뿐**이다 — `ReturnValue`도, out 파라미터도 없다. 데미지 값은 `ResolveHit` 내부에서 소비되고 **밖으로 나오지 않는다.**
  → dmg 부호로 게이팅하려면 **`ResolveHit`의 시그니처를 바꿔야 하고**, 그 함수는 기본공격·베기·파이어볼의 데미지 경로 **본체**다(P3-G16이 diff 0을 요구하는 대상) → **범위 밖 + 최대 회귀원**. **`Kind`/`Target`만이 실현 가능한 소스.**
  ※ 대안으로 검토했다 기각: **`PowerRate > 0`** → 막기 0.0 / **치유 0.8** → 치유가 통과해 아군이 플린치. **실패.**

- **N6 — `AttackPointOverride`는 초기화 주체가 없다: `ResetForBattle`도 안 지운다** `CONFIRMED`
  Director 질의(생명주기)에 대한 답. 실측:
  - `SetAttackPointOverride` **프로젝트 전역 0개**(바이너리 grep: Manager 0 · SpawnPoint 0) → 파트3이 **최초의 라이터**가 된다.
  - `ResetForBattle`(파트2 실측)은 `SetHp(MaxHp)`·`SetbAlive(true)`·`SetbBlockActive(false)`·`SetBlockValue(0)` + 배열 Clear뿐 → **`AttackPointOverride` 미접촉**.
  - `AttackPointOverride`는 **per-SpawnPoint(유닛별)** 이고 `WalkForward`가 `IsValid()`로 분기 → **None 복귀 지점이 없으면 그 유닛은 영구히 override 경로**를 탄다.
  **오염 시나리오**(구체): 마법사 A3가 5턴에 치유(override=아군 B) → 미클리어 → 13턴에 파이어볼(ENEMY1) → `IsValid(override)`=true → **아군 B에게 걸어가 허공에 파이어볼**. HP·데미지는 정상이라 **원장 diff 0을 통과**하고, 로그도 안 남는다 → **P3-P03만이 탐지 수단**.
  **필요 불변식**: Set/Clear가 **모든 스킬 경로를 지배**(#1 Branch보다 상류에서 무조건 Set-or-Clear) + **재전투 시 초기화**(P3-R08).
  → **P3-G05 · P3-P03 · P3-R08**.

- **N8 — #2를 "무조건 `SelectedTargets[0]` 대입"으로 구현하면 ENEMY1 3종이 회귀한다** `CONFIRMED`(구조)
  Director 질의("#1과 #2의 상호작용")의 핵심 답. `WalkForward`는 **`IsValid(AttackPointOverride)`만 보고 분기**한다 — `Target`을 보지 않는다. 따라서 override가 **어떤 이유로든 valid면 `GetAttackPointForTeam` 폴백은 통째로 우회**된다.
  → #2를 *"타겟 위치를 Set"* 이라고만 읽고 **모든 스킬에 대해 Set**하면, ENEMY1 공격도 override 경로를 타 **적의 팀 공격지점이 아니라 적 유닛의 실제 위치로 걸어간다**. 두 좌표가 다르면(공격지점은 중앙선, 유닛은 자기 홈) **기본공격 연출이 바뀐다** = *"완전 무변경"* 위반. **무음**(로그·원장 무기록).
  **#1과 #2는 충돌하지 않는다** — 단 **순서 제약**이 있다: `WalkForward`는 **CustomEvent(비동기)** 라 override를 **자기 진입 시점에 읽는다** → Set은 **`CallFunction_165`보다 exec 상류**여야 한다. 그리고 **Clear는 #1 Branch보다도 상류**여야 SELF 경로가 stale을 남기지 않는다(N6).
  **정리된 안전 형태**: `[Clear or Set: Target=="ALLY1" ? SelectedTargets[0] : None]` → `Branch(Target=="SELF")` → false → `WalkForward`.
  → **P3-G06 · P3-G05 · P3-R01**.

### Medium

- **N5 — 게이팅 술어를 "무해한 것의 부정목록"으로 쓰면 새 스킬에서 위험측으로 실패한다** `CONFIRMED`(논리)
  §1-5 참조. Director 질의("SELF인데 Kind가 DEF가 아닌 스킬이 생기면?")의 답. `Kind != "DEF" && Kind != "HEAL"` 형태는 새 Kind(`BUFF`·`DEBUFF`)가 추가되는 순간 **자동으로 "플린치함"에 편입**된다 → 오연출. `Kind ∈ {"PHYS","MAG"}` 또는 `Target == "ENEMY1"`(허용목록)은 **연출 누락 = 안전측 실패**.
  현행 데이터는 `Target`↔`Kind`가 **완전 상관**(SELF↔DEF, ALLY1↔HEAL, ENEMY1↔PHYS/MAG)이라 **오늘은 어느 쪽도 통과** → **GRAPH 술어 형태 검사(P3-G03)만이 탐지 수단**. → **권고: #1·#2·#3·#5를 `Target` 단일 축으로 통일**(§1-5).

- **N9 — `Target`/`Kind`는 enum이 아니라 스트링 → 대소문자·오타가 무음 false** `CONFIRMED`
  `BreakStruct_0` 실측: `Kind`(idx4)·`Target`(idx6) 모두 **`스트링`**. UE엔 **`Equal Exactly (String)`(대소문자 **구분**)** 와 **`Equal, Case Insensitive (String)`** 두 오버로드가 공존하고, 문자열 핀에서 `==`를 끌면 어느 쪽이 잡힐지 **로캘·컨텍스트 의존**이다(§34(79) 로캘 함정 · (80) 프리뷰 신뢰 금지 계열).
  `"Self"`·`"self"`·`"ENEMY1 "`(후행 공백) 중 하나라도 들어가면 **비교가 조용히 false** → 게이팅 전체 무력화 → **증상 그대로 + GRAPH는 "연결됨" PASS**. → **P3-G07**. DT 실측 정답: **`SELF`·`ALLY1`·`ENEMY1`·`PHYS`·`MAG`·`DEF`·`HEAL` 전부 대문자.**

- **N10 — #4 Branch가 `then_1` 서브체인 전체를 스킵하면 머티리얼 복원이 누락된다** `CONFIRMED`(구조)
  실측: `ExecutionSequence_0.then_1 → CallFunction_117`(SetWorldLocation = smear) **→ `CallFunction_93`(SetMaterial, self←`VariableGet_21` 프리미티브, Material←`VariableGet_22`) → `CallFunction_95`**.
  즉 `then_1` 가지는 **잔상 이동 + 머티리얼 세팅**의 2단이다. Branch를 `then_1` **직후**에 넣고 미채택 경로를 종단으로 두면 **`CallFunction_93`/`_95`까지 같이 스킵**된다 → 잔상 머티리얼 상태가 갱신되지 않아 **이전 잔상이 눌러붙거나 다음 공격의 잔상이 어긋날 수 있다**.
  → **P3-G09**: `CallFunction_117`**만** 스킵하고 `CallFunction_93`으로 합류시킬지, `then_1` 전체를 스킵할지 **명시**하고, 후자면 `_93`/`_95`의 역할을 확인할 것.

- **N13 — 계획서 §문제정의의 증상 6개 중 1개가 수정 5건 어디에도 없다** `CONFIRMED`(문서)
  §문제정의 막기 항목: *"…Idle → 복귀. **정작 다음 턴 30→15 반감될 때 표시 0**."* — 이 *"표시 0"*(반감이 화면에 안 보임)은 **수정 5건 표에 대응 항목이 없고**, 오너 육안 게이트에도 없다. → **범위 밖으로 보이나 증상 목록엔 남아 있어** 다음 사람이 *"파트3이 고쳤어야 하는 것"* 으로 오독할 수 있다. **최소한 수치 반감이 살아 있는지는 P3-R03이 봉인**하고, 표시 자체는 **명시적으로 이월**할 것.

### Low

- **N7 — #3 조건 교체 시 신규 경로 `ENEMY1 ∧ dist<1.0`이 생긴다(퇴화 가드 상실)** `CONFIRMED`(구조) / 현재 도달 불가
  Director 질의("퇴화 분기가 다시 도달 불가가 되나, 새 경로가 생기나")의 답: **새 경로가 생긴다.**
  현행 `dist<1.0`은 **모든 스킬**에 대한 **0벡터 방향 가드**다. `Target` 기반으로 **교체**하면 `ENEMY1 ∧ dist<1.0`(타겟이 시전자 위치에 겹침)이 처음으로 `else`(카메라 수학)에 도달할 수 있다.
  - **도달성**: 현재 8기 고정 배치(아군/적군 반대편)라 **도달 불가**. 단 **F4→F7a 선례가 정확히 이 패턴**(도달 불가라 방치 → 조건이 바뀌는 날 폭발).
  - **피해**: `CallFunction_220`(`Normalize`) **Tolerance=0.0001** → 0벡터 입력 시 **ZeroVector 반환(NaN·크래시 아님)** → 카메라가 타겟 위치에 겹쳐 **프레이밍만 깨짐**. **비치명.**
  - **반대 방향**: `then`(카메라 생략)은 SELF ∧ ALLY1 둘로 **여전히 도달 가능** → 死코드화 없음.
  → **권고 `(Target != "ENEMY1") OR (dist < 1.0)`** 은 퇴화 가드를 **논리합으로 보존**해 신규 경로를 원천 차단(비용 = OR 노드 1개). → **P3-G04 · P3-G18**.

- **N11 — `DT_Motions`의 RowNotFound는 무음이다** `CONFIRMED`
  실측: `GetDataTableRow_1.RowNotFound → VariableSet_19(PendingFrameCount = 리터럴 6.0) → IfThenElse_8`(RowFound 경로와 **머지**) → … → `ExecutionSequence_0`. 즉 **RowNotFound도 smear 체인에 도달**하고, 그 경로에서 `BreakStruct_1`은 **기본 구조체**(`IsAttackFamily=false`) → #4 게이팅 시 **잔상 생략**.
  기존 코드는 이 위험을 이미 알고 있다 — RowNotFound에서 `BreakStruct_1.FrameCount`(=0)를 **안 읽고 리터럴 6.0을 쓴다**. 그런데 **`DT_JobStats`와 달리 PrintString이 없어 완전 무음**(파트2 N3의 `"JobId lookup failed"` grep 같은 탐지 수단이 없다).
  → **P3-G10**으로 거동을 문서화. 현행 5스킬의 motionRow(5·10·11·15)는 **DT_Motions에 전부 실존**(실측) → **오늘 도달 불가**.

- **N12 — WalkForward는 비동기라 `Delay(0.55)`가 걸음을 대신 기다린다** `CONFIRMED`
  `WalkForward`는 **함수가 아니라 CustomEvent**(`CustomEvent_8`, `list_graphs`에 함수 그래프 4개뿐 — `UserConstructionScript`/`AlignSpriteToCamYaw`/`ResetForBattle`/`EventGraph`)라 `CallFunction_165`는 **즉시 리턴**한다. Manager는 `CallFunction_166`(**Delay 0.55s**)로 걸음 시간을 **하드코딩해 기다린다**.
  → **#1이 걸음만 생략하고 Delay를 남기면 막기 전에 0.55초 정지**가 생긴다(무해하나 오너 육안 대상). Delay까지 건너뛰면 막기 타이밍이 0.55초 당겨진다(원장 무영향 — 원장은 시간을 안 적는다).
  → **P3-G14**로 **결정을 강제**(둘 중 무엇이든 명시할 것). 미결이면 구현자 재량으로 갈리고 오너가 아침에 "왜 멈칫하지?"를 묻게 된다.

### 검토했으나 문제 없음 (빈손 통과 아님 — 근거 명시)

- **#4의 `BreakStruct_1` stale 위험** → **없음. CONFIRMED 안전.** 처음엔 "pure 노드가 다른 exec 체인의 impure 소스를 읽는다"를 의심했으나(N1과 동일 계열), 실측상 `CallFunction_13 → GetDataTableRow_1 → VariableSet_18/19 → IfThenElse_8 → CallFunction_14 → CallFunction_15 → ExecutionSequence_0`은 **단일 선형 체인**이고 `GetDataTableRow_1`이 **strictly 상류**다 → smear 시점의 `IsAttackFamily`는 **이번 호출의 값**. y좌표가 100(smear)/300(DT조회)으로 갈려 있어 **다른 체인처럼 보이지만 아니다.** **Director의 "직결 가능" 결론이 옳다.**
- **타겟 None 역참조** → **봉인됨.** `GetArrayItem_0`(`SelectedTargets[0]`, `Utilities|Array|Get(사본)`)은 빈 배열에서 None을 반환하지만, `MacroInstance_18`(IsValid 타겟)이 `IfThenElse_6` **상류**에 있고 `MacroInstance_16/17/19`도 각각 PC/ActiveUnit/ActionCam을 가드한다. 단 이 4개의 `Is Not Valid` 미연결 문제는 **파트1 12번이 이미 처리**(계획서).
- **카메라 0벡터 NaN** → **불가.** `Normalize` Tolerance=0.0001 → `|V|²<Tolerance`면 **ZeroVector 반환**. UE의 `Normalize`/`GetSafeNormal`은 NaN-safe. → N7의 피해가 "크래시"가 아니라 "프레이밍 깨짐"인 근거.
- **죽은 아군에게 치유** → **#5 게이팅이 오히려 개선한다.** 현행은 힐 대상에게 무조건 `PlayHurtReaction` → 사망 모션(row13, FREEZE_LAST) 위에 피격 모션이 덮인다. #5 적용 후엔 플린치 자체가 없어져 **사망 모션이 유지**된다. 부작용 없음(기록만).
- **override가 죽은 아군을 가리킴** → **무해.** 유닛은 `bAlive=false`만 되고 **파괴되지 않는다**(파트2 실측: `InitBattle`의 compact가 사망 유닛을 안 지우는 근거와 동일) → `IsValid` true 유지 → 시체 위치로 걸어감. 연출상 이상하지만 **크래시·소프트락 없음**. 밸런스(죽은 아군 힐 허용 여부)는 **범위 밖**.
- **동시 사망 / 턴 중 사망 × 연출** → **접점 없음.** 파트3은 `ResolveHit` 본체·`bAlive`·턴 진행에 **일절 손대지 않는다**(P3-G16). 연출 게이팅은 `ResolveHit` **호출 전(WalkForward·카메라)** 과 **호출 후(PlayHurtReaction)** 에만 개입하고, 둘 다 사망 판정과 독립.
- **`PlayAttack` 2-소스 머지(RowFound/RowNotFound)** → **#4에 무해.** `CallFunction_0`(PlayAttack)의 exec 소스는 `VariableSet_11.then`·`VariableSet_12.then` 2개지만, **양쪽 다 SpawnPoint의 동일 체인**을 기동하고 `GetDataTableRow_1`은 그 안에서 상류다 → `IsAttackFamily` 유효성은 어느 소스로 들어와도 동일.
- **오버플로·0 나눗셈** → **해당 없음.** 파트3은 산술을 신설하지 않는다(문자열 비교 + Branch만). 기존 `IfThenElse_8`이 FrameCount 0 가드를 이미 수행(리터럴 6.0 폴백).

**PLAUSIBLE(verifier 실측 확정 요망)**
- **N7-PLAUSIBLE**: 막기 시 `WalkBack`(제자리, 거리 0)이 **run1(row2) 모션을 최소 1프레임 재생**하는가. WalkForward/WalkBack은 이동 기계(`MacroInstance_16`→`CallFunction_140`)를 **공유**한다 → 거리 0에서 조기 종료되는지 아니면 고정 시간을 도는지는 `CallFunction_140` 내부에 달렸고, **미추적**. → **P3-P10**(오너 육안).
- **N1-PLAUSIBLE(세부)**: stale 값이 *"직전 턴 값"* 인지 *"매번 기본값"* 인지는 UE가 해당 로컬을 **UberGraphFrame으로 승격했는지**에 달렸다(`Delay`가 latent 경계를 만들므로 승격 가능성이 높다). **어느 쪽이든 "이번 턴 값이 아니다"는 불변**이라 N1의 결론·TC는 영향받지 않는다. 구분이 필요하면 **P3-P11**(첫 턴 = default를 읽는 유일한 창)로 관측.

---

## 7. 커버리지 근거

**검토 축**: 경계값(dist<1.0 임계·`Normalize` Tolerance 0.0001·`SelectedTargets[0]` 리터럴 인덱스·FrameCount 0 가드·PowerRate 0.0) · **순서/시간(★최대 수확)**(pure↔impure exec 순서 = N1 · Set↔비동기 CustomEvent 진입 = N8 · Branch↔Delay 배치 = N12 · `GetDataTableRow_1` 상류성 = 안전 확증) · 상태누수(`AttackPointOverride` 생명주기 = N6 · `ResetForBattle` 미접촉 · 재전투 이월 = P3-R08) · null(타겟 None 가드 4중 · override의 죽은 액터 · RowNotFound 머지 ×2) · 동시성(동시 사망 × 연출 = 접점 0으로 판정) · 상태전이(F7a 소프트락 경로 재검증 · 미연결 exec = N0) · 명세-구현(**계획서 5건 중 3건이 명세대로면 미작동** = N1·N2·N3, +N4 소스 부재, +N13 증상-수정 갭) · **무음실패**(stale override = 원장 무기록 · 문자열 대소문자 = N9 · 무조건 Set 회귀 = N8 · DT_Motions RowNotFound 무음 = N11).

**판정 불가로 남긴 것**:
- `CallFunction_140`(이동 기계 내부) 미추적 → **P3-P10을 오너 육안으로 이월**. 정적 추적으로는 "거리 0일 때 run 모션이 도는가"를 확정할 수 없다.
- `MacroInstance_23`/`MacroInstance_25`가 순회하는 `VariableGet_85` 배열의 정체 미확정 → `GetDataTableRow_0`의 **3번째 exec 소스**(`MacroInstance_23.Completed`)가 언제 발화하는지 미확정. **결정①(a)를 채택하면 이 소스의 재배선이 필요**하므로 그때 추적 필수 → **결정①(b)(신설) 권고의 실질적 근거**.
- 막기 자세 유지(`EndBehavior=FREEZE_LAST`·`bFreeze`) → **Director 지시로 범위 밖, TC 없음.** 단 §1-2 기록: 변수 목록(28개)에 `bFreeze` **부재 확인** → 범위 밖 판단의 근거는 **유효**(바이너리 grep `bFreeze`×3은 §34(82) 한계상 **정황이지 증명이 아니다**).

**Director 직접 검증 권고(자체 보고를 게이트로 인정하지 말 것)**:
**P3-G01**(`Target` 소스의 exec 상류성 — N1) · **P3-G02**(미연결 종단 0 — 소프트락) · **P3-G04**(#3 조건이 no-op 아님 — N2) · **P3-G05/G06**(override Set/Clear 지배 + ALLY1 한정 — N6/N8).
**이 다섯 곳은 전부 "컴파일 0 + 핀이 연결됨"을 통과하면서 기능은 작동하지 않는 부류**다 — 파트2의 N1(DT 폴백 등가성)과 같은 계열이며, **행동 TC가 아니라 핀 원문만이 탐지 수단**이다.

---

## 8. 이월 TC 처분 (2026-07-17, Director — ID별, blanket 통과 금지)

> 38건 중 미실행 32건(GRAPH 12·PIE 11·회귀 9)을 ID별로 처분한다. 처분 기준은 [[파트2_SPD_TC]] §8과 동일(코어 게이트 흡수/S1 오라클 런 흡수/F9b 흡수/A2 회귀 스위트 이월/근거 미확인 — 이월 유지).
>
> **★특기 — 파트4 재설계와의 충돌 발견(수정하지 않고 보고)**: [[파트4_라벨힐_완료]] 작업2가 치유(`ALLY1`)의 `IfThenElse_3.then`을 `VariableSet_6`(override Set)이 아니라 `CallFunction_166`(Delay) 직결로 재배선해, **치유 시전자가 "아군 쪽으로 이동"하지 않고 파트3 착수 이전 설계와 달리 "제자리 캐스팅"으로 바뀌었다**(파트4 §7 오너 육안 ②항목 "치유 제자리"로 확정). 이는 P3-P02("치유: 아군 쪽으로 이동")의 원문 기대와 정면으로 배치된다. 원인이 된 `VariableSet_6`(Set)는 파트4에서 고아화됐다(P4A-11 "AttackPointOverride 항상 None"). **P3-P02·P3-P03은 아래에서 "근거 미확인 — 이월 유지"로 정직하게 남기고, 원문·완료문서는 수정하지 않는다** — 처분 확정은 Director/오너 판단 필요.

### GRAPH (12건)

| ID | 처분 | 근거 |
|---|---|---|
| P3-G07 | 코어 게이트 흡수 | 이미 PASS한 P3-G01·G03·G04·G06이 핀 원문에서 실사용 문자열 리터럴(`"ENEMY1"` 등)·`EqualExactly`(대소문자 구분) 비교 연산자를 이미 확인했다 — G07이 우려하는 지점 대부분을 실질적으로 커버. |
| P3-G08 | 코어 게이트 흡수 | [[파트3_연출_완료]] §4 보너스 항목("#4 서브체인이 단일 진입점으로 통째 게이팅됨")이 `IsAttackFamily`(idx6) 직결·형변환 0을 핀 원문으로 확인했다. |
| P3-G09 | 코어 게이트 흡수 | 위와 동일 보너스 항목 — 미채택 경로가 종단이 아니라 `then_0`로 안전 분리됨을 확인. |
| P3-G10 | A2 회귀 스위트 이월 | `GetDataTableRow_1.RowNotFound` 경로는 현재 데이터로는 도달 불가(§1-4 실측 — 5스킬 motionRow 전부 DT_Motions에 실존)라 S1·F9b 어느 런도 이 경로를 밟지 않는다. |
| P3-G11 | 코어 게이트 흡수 | P3-G03(이미 PASS)이 `CallFunction_2`(PlayHurtReaction) 진입 배선을 확인했고, 이 노드는 리프 노드라 파트3 작업범위(#5는 진입 조건만 변경)에서 출력 측을 건드릴 이유가 없었다. |
| P3-G12 | 코어 게이트 흡수 | [[파트3_연출_완료]] §4가 P3-G04 확인 시 **"P3-G12 겸 확인"**이라고 명시적으로 기록 — `IfThenElse_6`의 `then`/`else` 양 갈래 보존이 이미 핀 원문으로 확인됐다. |
| P3-G13 | 코어 게이트 흡수 | [[파트3_연출_완료]] §6이 "WalkBack은 Director 확정 5건에 없어 무접촉(P3-G13이 요구하는 '무변경'과 일치)"이라고 명시적으로 확인했다. |
| P3-G14 | 코어 게이트 흡수 | [[파트3_연출_완료]] §6이 결정("SELF 스킵 경로가 `CallFunction_166`(Delay)로 합류해 막기에도 0.55초 대기가 남는다")을 명시적으로 기록 — G14가 요구하는 "결정이 그래프에 반영됐는지"가 P3-G02 확인(§4)으로 실질 커버. |
| P3-G15 | 코어 게이트 흡수 | [[파트3_연출_완료]] §5가 "컴파일 에러 0건(엔진 로그 직접 grep, Director 실행)"을 명시적으로 기록. |
| P3-G16 | S1 오라클 런 흡수 | S1 런의 데미지 값이 [[SPD원장_오라클_v1]]과 일치해야 하므로 `ResolveHit` 데미지 서브그래프 무결이 행동적으로 뒷받침된다(부분 — §5 자산표의 `DT_Skills.uasset` mtime 불변도 보조 근거이나, "그 외 0" 전체 범위의 구조적 diff는 아님). |
| P3-G17 | F9b 흡수 | F9b §7 오너 육안 게이트의 "회귀: 카메라 컷 정상" 항목이 성립하려면 `bCamActionEnabled` CDO가 true여야 한다(false면 카메라 로직 전체가 도달 불가해져 회귀 항목 자체가 실패로 드러난다). |
| P3-G18 | F9b 흡수 | F9b §7 오너 육안 게이트의 "치유: 카메라 역방향 컷 없음"·"회귀: 카메라 컷 정상"이 카메라 수학(`Normalize` 등)의 실질적 무결성을 행동으로 검증한다. |

### PIE (11건)

| ID | 처분 | 근거 |
|---|---|---|
| P3-P01 | F9b 흡수 | §7 오너 육안 게이트 "막기: 제자리에서 방어" 항목에 명시. |
| P3-P02 | **폐기 — 설계 변경으로 전제 무효 (Director 판정 2026-07-17)** | [[파트4_라벨힐_완료]] 작업2가 **오너 명시 지시**("제자리에서 casting")로 치유 경로를 "아군 쪽 이동"→"제자리 캐스팅"으로 재설계 — 본 TC의 기대 동작(아군 쪽 이동) 자체가 폐기된 설계다. 대체 동작(제자리 casting + HP 회복)은 **파트4 오너 육안 4항목 PASS(2026-07-17)로 이미 검증 완료**. |
| P3-P03 | **폐기 — 전제 소멸 (Director 판정 2026-07-17)** | 오염 시나리오의 전제(override에 valid 값이 들어감)가 파트4 작업2로 원천 소멸 — `IfThenElse_3(ALLY1).then → CallFunction_166` 직결·`VariableSet_6`(SetAttackPointOverride) 고아화는 **Director가 핀 원문으로 직접 확정**(파트4 게이트, 2026-07-17). override에 값을 쓰는 노드가 그래프에 없으므로 오염 경로 자체가 없다. 잔여 런타임 재확인은 P4A-11(F9b 이월)이 수행. |
| P3-P04 | F9b 흡수 | §7 "자기가 피격 리액션 안 함" 항목에 명시. |
| P3-P05 | F9b 흡수 | §7 "아군이 피격 리액션 안 함" 항목에 명시. |
| P3-P06 | F9b 흡수 | §7 "참격 잔상 없음"(막기) 항목에 명시. |
| P3-P07 | F9b 흡수 | §7 "참격 잔상 없음"(치유) 항목에 명시 — 결정②(b) 채택(`motions.csv` 60110000 수정, §5 mtime 갱신 확인)이 이미 반영됨. |
| P3-P08 | F9b 흡수 | §7 "카메라 역방향 컷 없음" 항목에 명시. 파트4의 치유 재배선(#2)은 카메라 게이팅(#3, 별도 `IfThenElse_6`) 자체를 건드리지 않아 영향 없음. |
| P3-P09 | F9b 흡수 | 에러 0 확인은 풀플레이 전 구간에서 자연 수집된다(S1도 부분 커버하나 ALLY1 경로는 F9b에서만 노출). |
| P3-P10 | F9b 흡수 | §7 "(관찰, FAIL 아님) 막기 시 제자리 run 모션 스침" 항목에 명시. |
| P3-P11 | S1 오라클 런 흡수 | even-trade 런의 첫 턴(A3)이 결정론적으로 기본공격(ENEMY1 타겟)이므로 "첫 턴 게이팅 정상"을 확정적으로 검증한다 — 스킬 선택이 오너 재량인 F9b보다 오히려 더 결정론적인 관측창. |

### 회귀 (9건)

| ID | 처분 | 근거 |
|---|---|---|
| P3-R01 | F9b 흡수 | §7 "회귀: 공격·베기·파이어볼(ENEMY1) 3종 동일" 항목에 명시 — S1은 기본공격만이라 부분 커버, 베기·파이어볼은 F9b에서만 노출. |
| P3-R02 | S1 오라클 런 흡수 | **[정정 2026-07-17]** 검증 내용의 ~~"23턴 원장"~~은 **20유닛턴 — [[SPD원장_오라클_v1]]이 정의**로 정정한다. 절차는 [[파트2_SPD_TC]] P2-R01(§4에서 오라클-diff로 정정됨)과 동일하게 대체 — 데미지·턴·순서 무변경 diff는 S1 런에서 자연 산출된다. |
| P3-R03 | F9b 흡수 | 막기 수치 반감(30→15) 검증은 막기 스킬 실사용이 필요, even-trade는 기본공격만이라 커버 못함. |
| P3-R04 | S1 오라클 런 흡수 | S1 런은 Start 버튼 클릭으로 시작하므로 파트1 UI 흐름 무접촉을 실행 전제로 재확인한다. |
| P3-R05 | S1 오라클 런 흡수 | S1 런이 spd 값·턴순서(20턴, 첫 8턴 포함)를 재관측한다. |
| P3-R06 | F9b 흡수 | F7a 소프트락 회귀 확인은 SELF(막기) 스킬을 실제로 시전해 완주해야 하는데, even-trade는 기본공격만이다. |
| P3-R07 | 코어 게이트 흡수 | [[파트3_연출_완료]] §5가 `DT_Motions.uasset` mtime 갱신(8,391→8,350B)과 `motions.csv` L13(60110000) 수정을 명시적으로 기록 — 디스크 실증 존재(단 "나머지 15행 diff 0" 전수 grep 재확인은 별도로 없음, 부분 커버). |
| P3-R08 | A2 회귀 스위트 이월 | 재전투(End→Start) 멱등 검증은 S1·F9b 어느 쪽도 단일 전투라 커버하지 못한다. |
| P3-R09 | 코어 게이트 흡수 | 3개 하위항목 모두 이미 해소된 상태다 — ① 계획서 원문이 파트4 작업 중 소실돼 정정 대상 자체가 소멸([[파트4_라벨힐_완료]] §9) ② §34 N1 등재는 Director가 명시적으로 미채택 결정(본 문서 "관련" 절에 이미 자기-정정 기록) ③ `plan.md` TC 상태 반영은 완료(plan.md frontmatter의 파트3 서술). |

**집계**: 코어 게이트 흡수 10 · S1 오라클 런 흡수 5 · F9b 흡수 13 · A2 회귀 스위트 이월 2 · **폐기 2**(P3-P02·P3-P03 — 파트4 오너 재설계로 전제 무효, Director 판정 2026-07-17).

---

## 관련
- 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md` §파트3 (표의 #3·#4·#5는 **P3-R09로 정정 대상**)
- [[파트2_SPD_TC]] (ID·컬럼 규약 원본 · P2-R01 신규 원장 → P3-R02의 기준선) · [[파트1_Start_TC]]
- [[언리얼_MCP_실전노하우]] §34 (78)~(85) — ⚠**정정**: 이 줄이 원래 제안했던 "N1을 (84)로 등재"는 Director가 채택하지 않았다. N1은 별도 신규 번호 없이 [[파트3_연출_완료]] §2 서사로 기록됐다(같은 계열: [[야간F6_모션데이터구동_완료]]의 "세터가 소비자보다 늦은" 가짜 GREEN). 대신 (84)(85)는 이번 세션(파트2·3) 실측 2건 — `ProgrammaticToolset` 트랜잭션 롤백·PIE 액터 refPath 형식 — 으로 등재됐다.
- `data/skills.csv` · `data/motions.csv` (결정②(b) 채택 시 `motions.csv` 60110000 수정 대상)
- [[plan]] · [[청사진]]
