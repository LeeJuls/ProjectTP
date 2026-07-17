---
type: qa
project: projectTP
feature: 전투완성
stage: 파트4(유닛 라벨 + 치유 제자리 + 힐 표시)
status: 게이트 PASS(Director, 2026-07-17) — 오너 육안 4항목 PASS + Director 핀검증(작업1 라벨 GRAPH 8건) PASS + P4C-15(런타임조인 8기) PASS + 컴파일0·디스크저장 실증. 59건 재분류: **23건 PASS**(오너9+Director핀8+P4C-15+컴파일2+디스크정황2+본세션검증1) · **6건 F9b(오너 풀플레이) 이월** · **30건 코어 게이트 흡수·A2 회귀 스위트 이월**(qa-critic 재분류 규칙: PIE-시각형→F9b 종착점, GRAPH/데이터변형형→A2). ★게이트 19건 중 작업1(라벨) 6건 전체 PASS, 나머지 13건(작업2·3·회귀 GRAPH) A2 이월. 신규발견 7(High 2·Medium 2·Low 3)은 §7 참고 — NF1·NF2는 정황상 해소, 핀레벨 확정은 A2 이월. 상세: [[파트4_라벨힐_완료]]
updated: 2026-07-17
---

# 파트4 — 유닛 라벨 · 치유 제자리 · 힐 표시 TC

> 대상: 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md`(SSOT — B1·B2·H1·H2·H3·M1~M5 반영 최종본) · [[파트3_연출_TC]](ID·컬럼·판정도구 규약 계승) · [[언리얼_MCP_실전노하우]] §34 (78)~(85).
> **qa-critic 적대적 검토 산출물 — 검출·TC설계만.** TC 실행=verifier, 게이트 판정=Director.
> 본 문서의 모든 "실측"은 **2026-07-17 라이브 에디터 직접 조회**(`find_nodes`/`get_node_infos` + `.uasset` ASCII grep, PIE OFF) 결과다. 계획서가 지목한 급소 노드·핀을 전수 확증했고, **계획서 내부 모순 1건(3-2↔D2 Amount 소스)** 을 신규 검출했다.
#projectTP/전투완성

---

## 0. 범위 & 판정도구

**판정도구 약칭**(파트1~3 계승): **GRAPH**=정적 노드조회(`find_nodes(title="")`+`get_node_infos`) / **PIE**=인스턴스 프로퍼티(`get_properties`, `UEDPIE_0`) / **LOG**=`projectTP.log`·원장 grep / **파일**=디스크 grep·mtime / **CMP**=컴파일0 / **오너**=육안(불차단).
**★**=게이트 / **★★**=최우선 / **★★★**=최강(컴파일0+"핀 연결됨"을 통과하며 기능은 미작동하는 부류 = Director 직접 핀조회 권고).

> ⚠ MCP 형식 §34 (78): `call_tool(toolset_name="editor_toolset.toolsets.blueprint.BlueprintTools", tool_name="find_nodes", arguments={"graph":{"refPath":"..."},"title":""})`. 객체 인자는 `{"refPath":"..."}` dict.
> ⚠ `get_properties`의 인자명은 **`instance`/`properties`**. PIE 액터 refPath(§34 (85)): `/Game/Stages/UEDPIE_0_map_battle_octopath.map_battle_octopath:PersistentLevel.<액터>`.
> ⚠ **PIE 켠 채 저장 금지**(§34 (81)) — ST_UI 저장·레벨 CharName 세팅이 무음 실패. **착수 전 PIE OFF.**
> ⚠ **저장 판정은 API 반환값 아니라 디스크 mtime**(§34 (81)(82) — `save_assets` true도 `is_dirty()` true도 신뢰 금지).
> ⚠ **`ProgrammaticToolset`은 단일 트랜잭션**(§34 (84)) — 꼬리 오류 하나가 앞선 성공을 통째 롤백. **쓰기와 검증 호출 분리.**

**총 59건** — P4A(작업2 치유 제자리) 12 · P4B(작업3 힐 표시) 20 · P4C(작업1 유닛 라벨) 16 · P4R(회귀) 11.

**리소스 refPath 실측 확정**:
- BP_BattleManager: `/Game/Blueprints/BP_BattleManager.BP_BattleManager` — 그래프 `:EventGraph`(작업2) · `:ResolveHit`(작업3 힐 콜사이트·델타) · `:SpawnDamageNumber`(작업3 부호·색)
- WBP_SkillMenu: `/Game/UI/Components/WBP_SkillMenu.WBP_SkillMenu:SetActiveUnit`(작업1)
- WBP_DamageNumber: `/Game/UI/Components/WBP_DamageNumber.WBP_DamageNumber` (SpawnDamageNumber가 매 호출 신규 생성)
- ST_UI: `/Game/UI/ST_UI.ST_UI` (디스크 `D:\unreal\projectTP\Content\UI\ST_UI.uasset`)
- 레벨: `/Game/Stages/map_battle_octopath` (디스크 `...\Content\Stages\map_battle_octopath.umap`)

---

## 1. 착수 전 실측 기준선 (본 문서가 확정 — 인용 시 이 값 기준)

### 1-1. 작업2 (치유 제자리) — `BP_BattleManager:EventGraph`

| 계획서 주장 | 실측 | 판정 |
|---|---|---|
| `IfThenElse_3`(Target=="ALLY1").then → `VariableSet_6`(override Set) | **정확.** `IfThenElse_3.then.connected_pins == [VariableSet_6]`, Condition ← `CallFunction_24`(문자열 Equal). else → `IfThenElse_4` | ✅ |
| `IfThenElse_3.else → IfThenElse_4`(SELF·ENEMY1 공용) | **정확.** `IfThenElse_4.execute ← [VariableSet_6.then, IfThenElse_3.else]`(2소스). `IfThenElse_4.then→CallFunction_166`(Delay)·`else→CallFunction_165`(WalkForward) | ✅ |
| `CallFunction_166`(Delay 0.55)이 **2-way 병합** → 직결 시 3-way | **정확.** `CallFunction_166.execute ← [CallFunction_165.then, IfThenElse_4.then]`(2소스), Duration=**0.55**. IfThenElse_3.then 직결 시 3소스 | ✅ |
| **`GetArrayItem_0`은 고아 아님 — 6 팬아웃 중 5 라이브** | **정확·핵심.** `GetArrayItem_0.Output`(SpawnPoint ref) → **6곳**: ①`MacroInstance_18`(IsValid) ②`CallFunction_213` ③`MacroInstance_2` ④**`CallFunction_1`(=EventGraph ResolveHit 호출, Target 인자 idx3)** ⑤**`CallFunction_2`(PlayHurtReaction self)** ⑥`VariableSet_6`(override 값). **①~⑤ 5곳이 라이브** — VariableSet_6만 고아화 | ✅ **"정리"가 라이브 5곳을 끊는 사고 확증** |
| `VariableSet_5`(Clear)는 死코드 아님 | **정확.** `VariableSet_5`(SetAttackPointOverride, 값핀 **미연결=None**).execute ← `GetDataTableRow_1.then` AND `.RowNotFound`(2소스=무조건), then→`IfThenElse_3` | ✅ 존치(무해) |
| 소비처는 `WalkForward` 단 하나 | (파트3 실측 계승) VariableSet_6 고아화 시 override 영구 null → WalkForward 폴백만 남음 | ✅ |

### 1-2. 작업3 (힐 표시) — `ResolveHit` HEAL 꼬리 + `SpawnDamageNumber`

| 계획서 주장 | 실측 | 판정 |
|---|---|---|
| HEAL 경로: `IfThenElse_5`(kind=="HEAL").then → SetHp → 위젯SetHp → SetDmg → SetSkillCooldown | **정확.** `IfThenElse_5.then → VariableSet_6`(SetHp,self=Target) → `CallFunction_46`(위젯 SetHp) → `VariableSet_7`(SetDmg) → `CallFunction_24`(SetSkillCooldown). else→`IfThenElse_6` | ✅ |
| `VariableSet_6`(SetHp).Hp ← `Comm_2`(Min 결과) | **정확.** `VariableSet_6.Hp ← CommutativeAssociativeBinaryOperator_2` (= 계획서 "Comm_2"). 위젯 SetHp도 동일 소스 | ✅ pure 재평가 함정원 |
| `CallFunction_24`(SetSkillCooldown) **6-way 병합** | **정확.** execute ← [`VariableSet_7`, `VariableSet_10`, `IfThenElse_9`(else), `VariableSet_18`, `VariableSet_22`, `VariableSet_23`] = **6소스** | ✅ 삽입 후 6 유지 |
| `VariableSet_7`(SetDmg).then → `CallFunction_24` 직결 = 신규노드 삽입 자리 | **정확.** `VariableSet_7.then.connected_pins == [CallFunction_24]` | ✅ |
| `CallFunction_1`(피해 SpawnDamageNumber)에 힐 물리면 승패 서브트리 감염 | **정확.** `CallFunction_1.then → IfThenElse_9`(승패). execute ← [IfThenElse_8, VariableSet_3, IfThenElse_13] = **피해 경로 3소스**(HEAL 아님). Amount ← `VariableGet_31`(GetDmg), WorldLoc ← `CallFunction_0`(GetWorldLocation on Target) | ✅ 별도 노드 필수 |
| `SpawnDamageNumber`: Append 핀 A="-" 미연결 / ToString(Integer).InInt ← Amount raw | **정확.** `CommutativeAssociativeBinaryOperator_0`(Append) A="-"(미연결), B ← `CallFunction_4`(ToString Integer). CallFunction_4.InInt ← FunctionEntry.**Amount(raw, Abs 없음)** | ✅ |
| SetText 경로 + Txt_Amount 자동Get 재사용 | **정확.** Append → `CallFunction_5`(ToText String) → `CallFunction_11`(SetText, self ← `VariableGet_1`=GetTxt_Amount). **기존 SetColorandOpacity 노드 0개**(신규 진짜 신규) | ✅ |
| 위젯 1회용 | **정확·핵심.** `CreateWidget_0`(Class=`WBP_DamageNumber_C`)가 **매 호출 신규 생성**. 위젯 ref는 내부(GetTxt_Amount·AddChild·SetTargetWorldLoc)만 소비 | ✅ probe#3 해소(아래 §4) |
| 엔트리 시그니처 (Amount:int, WorldLoc:vector) | **정확.** FunctionEntry: `Amount`(인티저), `WorldLoc`(벡터). bHeal 없음 | ✅ 불변 |

### 1-3. 작업1 (유닛 라벨) — `WBP_SkillMenu:SetActiveUnit`

| 계획서 주장 | 실측 | 판정 |
|---|---|---|
| 직업명 소스 = `BreakStruct_0.jobId`(구조체 필드) | **정확.** `BreakStruct_0`=`BreakFJobStatsRow`(입력 ← `GetDataTableRow_1`=DT_JobStats). 출력 **`JobId_8...`(인티저) = 유휴 핀**(connected_pins **[]**). 소비되는 건 `SkillIds` 하나뿐 | ✅ jobId=직업ID(90100100), **BP 변수 JobId(로우키)와 무관** |
| `GetDataTableRow_1.RowNotFound` 경로 존재 | **정확.** DataTable=`/Game/Data/DT_JobStats`, RowNotFound → `CallFunction_13`(라이브). RowName ← `CallFunction_4`(기본 "10101000") | ✅ 이름 잔류 방어 필요 |
| `Txt_TurnOwner` SetText(`CallFunction_459/460`)가 BreakStruct_0보다 상류 | **정확(qa H2).** 459/460.self ← `VariableGet_170`=**`GetTxt_TurnOwner`**, execute ← `IfThenElse_75`(Condition ← `VariableGet_169`=`GetbIsParty`).then/.else = **아군/적군 토글**, FunctionEntry 직후 = BreakStruct_0보다 상류 | ✅ 그 자리 불가 |
| `Txt_UnitName`은 아무도 값 안 넣음(placeholder "전사 I") | **정확.** 459/460은 **Txt_TurnOwner**를 세팅(UnitName 아님). SetActiveUnit에 Txt_UnitName setter 부재 | ✅ 신규 라벨 대상 |
| Unit 파라미터에서 CharName 조달 | **정확.** FunctionEntry.`Unit`(BP Battle Spawn Point ref) 팬아웃 다수 → CharName Get 부착 가능 | ✅ |
| **FormatText 메커니즘**(H3): Format 리터럴을 파싱해 `{N}` 인자 핀 생성 | **★실증(신규발견 NF4).** `ResolveHit.FormatText_0`(`Utilities|Text|포맷텍스트`)가 **리터럴** Format(`NSLOCTEXT(...,"BattleLog\|turn={0}\|...\|effectApplied={8}")`)로 인자 핀 `"0"`..`"8"` 보유. 추가로 `"9"`..`"17"`(과거 긴 포맷의 **잔류 orphan 핀**)까지 = **리터럴→핀 생성 확정 + 핀은 포맷 변경 후에도 잔류** | ✅ H3 우회로(리터럴 먼저) 성립 |

### 1-4. 디스크 베이스라인 (ASCII grep, PIE OFF, 2026-07-17)

| 애셋 | mtime | 실측 |
|---|---|---|
| `ST_UI.uasset` | 2026-07-16 23:06 | `Job.Warrior`·`Job.Mage`·`Battle.UnitLabel`·`Battle.TurnLabel` **전부 0건** → 4키 신규 추가 확정 |
| `BP_BattleSpawnPoint.uasset` | 2026-07-17 01:01 | `CharName` **0건**(신규 변수) · `SpdOverride` **1건**(파트2, grep 동작 증명) |

> ⚠ §34 (82): grep **0건 = 부재 증명(신뢰)**, **존재 = 최신 저장 증명 아님**. 저장 판정은 **mtime 갱신**으로.

---

## 2. ★게이트 목록 (Director 직접 핀조회 권고 — 자체 보고를 게이트로 인정 말 것)

> **★★★/★★는 "컴파일0 + 핀 연결됨"을 통과하며 기능은 미작동하는 부류**다(파트2 N1·파트3 N1과 동층). 핀 원문만이 탐지 수단.

- **작업2**: `P4A-01`(then 직결) · `P4A-02`(→VariableSet_6 절단) · `P4A-04`(GetArrayItem_0 라이브 5곳) · `P4A-08`(크로스그래프 봉인)
- **작업3**: `P4B-01`(Amount>0 극성) · `P4B-03`(MakeSlateColor 브릿지) · `P4B-08`(별개 노드) · `P4B-10`(HpBefore가 SetHp 앞) · `P4B-11`(Comm_2 재사용 금지) · `P4B-12`(부호 반전) · `P4B-13`(델타≠VariableGet_31)
- **작업1**: `P4C-01`(Format 인자 핀 실존) · `P4C-02`(Append 우회 금지) · `P4C-03`(jobId 구조체 필드) · `P4C-07`(Txt_UnitName 배선·위치) · `P4C-10`(ST_UI 4키 디스크) · `P4C-15`(런타임 조인 8기)
- **회귀**: `P4R-04`(ResolveHit 데미지 diff0) · `P4R-05`(크로스그래프 VariableSet_6 봉인)

---

## 3. TC — 작업별

### §작업2 — 치유 제자리 casting (P4A) · 12건

> 편집 대상: `BP_BattleManager:EventGraph`. **와이어 1개 전환 + 고아 1개.** 오너 불만 핵심 → 최우선.

| ID | ★ | 검증 내용 | 판정 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P4A-01** | ★★★ | **IfThenElse_3.then 직결 전환** | GRAPH | `EventGraph.IfThenElse_3.then.connected_pins == [CallFunction_166]`(단일, VariableSet_6 아님) | 작업2 핵심 와이어. 실측 현재 then→VariableSet_6 |
| **P4A-02** | ★★★ | **기존 →VariableSet_6 링크 절단** | GRAPH | `EventGraph.VariableSet_6.execute.connected_pins`에 **IfThenElse_3.then 없음**(고아). 자동 절단 실패 시 `break_pins` 선행 확인 | exec 출력 1링크 제약상 자동 절단 예상하나 **미보장** — 이 확인 자체가 TC |
| **P4A-03** | ★★ | **IfThenElse_3.else 무손상** | GRAPH | `IfThenElse_3.else.connected_pins == [IfThenElse_4]` | SELF·ENEMY1 공용 진입점. 실측 확인 |
| **P4A-04** | ★★★ | **★GetArrayItem_0 라이브 5곳 무손상** | GRAPH | `EventGraph.GetArrayItem_0.Output`이 **[MacroInstance_18, CallFunction_213, MacroInstance_2, CallFunction_1, CallFunction_2] 5곳 유지**(6번째 VariableSet_6만 무효/제거 허용) | ★내 검출 — "고아 정리"가 라이브 소비처를 끊는 사고 방지. **CallFunction_1=ResolveHit Target 인자, CallFunction_2=PlayHurtReaction self** — 끊기면 데미지/피격 붕괴(무음) |
| **P4A-05** | ★★ | **CallFunction_166 3-way 병합·미연결 종단 0** | GRAPH | Delay.execute ← [CallFunction_165.then, IfThenElse_4.then, **IfThenElse_3.then**] 3소스 ∧ 신규 미연결 exec 종단 0 | 실측 현재 2소스 → 3소스. 소프트락 봉인(파트3 P3-G02 계열) |
| **P4A-06** | ★ | **Delay Duration 무변경** | GRAPH | `CallFunction_166.Duration == 0.55` 리터럴 유지 | 타이밍 보존 |
| **P4A-07** | ★ | **VariableSet_5(Clear) 무변경** | GRAPH | execute ← GetDataTableRow_1.then+RowNotFound(무조건), AttackPointOverride 핀 미연결(None), then→IfThenElse_3 | override 영구 null → WalkForward 폴백 정상(ENEMY1 무영향의 근거) |
| **P4A-08** | ★★ | **★크로스그래프 오손상 봉인** | GRAPH diff | 작업2는 **`EventGraph`의 VariableSet_6·IfThenElse_3·IfThenElse_4만** 편집. **`ResolveHit`의 동명 VariableSet_6(SetHp)·IfThenElse_3·IfThenElse_4 diff 0** | 그래프 간 동명 함정 — `ResolveHit.VariableSet_6`=SetHp(라이브 힐)를 고아로 만들면 **힐 통째 사망**. 지시서는 fully-qualified 경로 |
| **P4A-09** | ★★ | **ENEMY1 여전히 걷는가** | PIE/오너 | 공격·베기·파이어볼 시전 시 시전자 `WalkTargetLoc` ≈ 적진 공격지점(제자리 아님) | override=None이어도 WalkForward 폴백 정상. 작업2가 ENEMY1 무영향(else 경로) |
| **P4A-10** | ★★ | **ALLY1 제자리 치유** | PIE/오너 | 치유 시전 시 시전자 `GetActorLocation` ≈ `HomeLocation`(걸음 없음) ∧ Casting2(row11) 재생 | 작업2 목적. ALLY1 exec = SELF(막기, 오너 PASS)와 동일 |
| **P4A-11** | ★ | **AttackPointOverride 항상 None** | PIE | 전 유닛·전 시점 override == None(VariableSet_6 고아 → Set 소스 소멸) | 파트3 N6 오염 **원천 소멸**(Set 자체가 죽음). ⚠ 원장 무기록 — PIE만이 탐지 |
| **P4A-12** | ★ | **에러 0** | PIE/LOG | 치유·공격 시 `"Accessed None"`·`"None에 액세스"`·`"out of bounds"` 각 0건 | 표준 |

### §작업3 — 힐 표시 `+N` 초록 (P4B) · 20건

> 편집: `SpawnDamageNumber`(부호·색, 시그니처 불변) + `ResolveHit` HEAL 꼬리(콜사이트·델타 ~5노드). **3-1·3-2 동일 세션 완결 필수.**

**3-1. `SpawnDamageNumber` 내부 부호·색 분기 (시그니처 불변)**

| ID | ★ | 검증 내용 | 판정 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P4B-01** | ★★★ | **판별자 Amount>0 극성** | GRAPH | Append(`CommutativeAssociativeBinaryOperator_0`) 핀 A ← `SelectString(bPickA=(Amount>0), A="-", B="+")`. ⚠ `Amount<0` 형태면 **FAIL** | qa M3 — 힐 0(만피)이 빨간 `-0`으로 뜨는 것 방지. Amount=0 → `>0` false → "+" 초록 |
| **P4B-02** | ★★ | **Abs 삽입** | GRAPH | `CallFunction_4`(ToString Integer).InInt ← `Abs(Amount)`(직접 Amount 아님) | 부호는 SelectString, 자릿수는 Abs. 실측 현재 InInt ← Amount raw |
| **P4B-03** | ★★★ | **MakeSlateColor 브릿지 존재** | GRAPH/CMP | `SetColorandOpacity`(입력 **FSlateColor**) ← `MakeSlateColor` ← `SelectColor`(LinearColor). ⚠ SelectColor 직결이면 **컴파일 FAIL** | umg 실측 타입 불일치. 브릿지 노드 1개 필수 |
| **P4B-04** | ★★ | **SelectColor 극성·색값** | GRAPH | `SelectColor(bPickA=(Amount>0), A=빨강(1.0,0.4196,0.3843), B=초록(0.5608,0.8784,0.4157))` | Amount>0(피해)=빨강, ≤0(힐)=초록. 형제 일관성(sRGB 직접, 143/224/106) |
| **P4B-05** | ★★★ | **SetColorandOpacity 단일경로 실행** | GRAPH | 신규 `SetColorandOpacity`.self ← `VariableGet_1`(GetTxt_Amount 재사용), exec가 `CreateWidget_0` 하류(SetText~AddChild 구간). SpawnDamageNumber 내부는 **단일 exec 경로** → 피해(CallFunction_1)·힐(신규) 콜사이트 **모두 통과** | ★probe#3 해소 — 위젯이 매 호출 신규 CreateWidget(1회용) → 초기색=디자인 기본값 → **명시 Set이 매번 필요·안전**. 분기는 SelectColor(pure)라 별도 "피해 경로" 없음 → 스킵 위험 0 |
| **P4B-06** | ★ | **시그니처 불변** | GRAPH | FunctionEntry (Amount:int, WorldLoc:vector). **bHeal 파라미터 미신설** | 진실원 2개(부호규약↔bHeal) 불일치 방지 |
| **P4B-07** | ★ | **애니 충돌 없음** | 파일/오너 | `WBP_DamageNumber` 애니(`Anim_Float`)에 `MovieSceneColorTrack` 부재(Opacity=RenderOpacity 별개 채널) → SetColorandOpacity 무간섭 | umg 실측. **PLAUSIBLE** — verifier 육안(색이 페이드 중 유지되는가) |

**3-2. 힐 콜사이트 신설 + D2 적용 델타 (`ResolveHit`)**

| ID | ★ | 검증 내용 | 판정 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P4B-08** | ★★★ | **신규 SpawnDamageNumber = CallFunction_1과 별개 노드** | GRAPH | 힐용 SpawnDamageNumber는 **신규 노드**, `ResolveHit.CallFunction_1`(피해용)에 exec 4번째로 안 물림. 신규노드.execute ← `VariableSet_7.then` 단독 | `CallFunction_1.then→IfThenElse_9`(승패 서브트리) — 힐이 승패·사망 로직 타는 계약 위반 방지. 실측 확인 |
| **P4B-09** | ★★ | **CallFunction_24 병합 6 유지** | GRAPH | 삽입 후 SetSkillCooldown.execute = **6소스**[신규노드, VariableSet_10, IfThenElse_9, VariableSet_18, VariableSet_22, VariableSet_23](VariableSet_7 자리를 신규가 대체) | `VariableSet_7.then→CallFunction_24` 와이어에 삽입. 실측 현재 6소스 |
| **P4B-10** | ★★★ | **★HpBefore 로컬 캡처가 SetHp 앞** | GRAPH | 신규 `SetHpBefore`(로컬)가 `ResolveHit.VariableSet_6`(SetHp)보다 exec **상류**(`IfThenElse_5.then → SetHpBefore → VariableSet_6`) | D2. ⚠ SetHp **뒤**면 HpBefore=NewHp → Delta=0 상시 → **모든 힐 "+0"**(비만피도 거짓 0) |
| **P4B-11** | ★★★ | **★Comm_2 재사용 금지** | GRAPH | Delta의 "SetHp 후 Hp"는 `GetHp(Target)` **재조회**, `CommutativeAssociativeBinaryOperator_2`(Min 결과) 아님 | pure 재평가 함정 — Comm_2는 SetHp 후 `Min(NewHp+Heal,Max)`로 재계산돼 **오값**. GetHp는 저장된 NewHp 반환(안전). 실측 SetHp.Hp ← Comm_2 |
| **P4B-12** | ★★★ | **★부호 반전** | GRAPH | 신규 SpawnDamageNumber.Amount = `0 − Delta`(Delta=NewHp−HpBefore>0 → **Amount<0**). ⚠ Delta 그대로(양수) 전달 → 힐이 빨간 피해. ⚠ 이중 반전(Delta=HpBefore−NewHp 후 다시 0−Delta) 금지 | 판별자 Amount>0=피해 → 힐은 음수여야 초록. 만피: Delta=0 → Amount=0 → 초록 "+0". *(대수적 등가 `Subtract(HpBefore, NewHp)` 단일노드 허용 — 최종 Amount≤0만 충족하면 됨)* |
| **P4B-13** | ★★★ | **★힐 Amount 소스 = 델타이지 VariableGet_31 아님** | GRAPH | 신규 SpawnDamageNumber.Amount ← 델타 서브그래프, `ResolveHit.VariableGet_31`(GetDmg) **아님** | ★신규발견 NF1 — 계획서 3-2("Amount ← VariableGet_31 재사용")를 **D2("Amount=0−Delta")가 폐기**. VariableGet_31=Dmg=−HealAmt(원시). 비만피엔 −HealAmt≈−Delta라 동일(통과) → **만피에서만 "+33"(HP 0이동)** = D2가 막으려던 그 버그 |
| **P4B-14** | ★★ | **WorldLoc 재사용** | GRAPH | 신규 SpawnDamageNumber.WorldLoc ← `ResolveHit.CallFunction_0`(GetWorldLocation on Target) 재사용(pure) | 3-2·D2 공통 생존분(Amount만 대체). pure 팬아웃 안전 |
| **P4B-15** | ★★ | **BattleLog dmg 무변경** | GRAPH/LOG | `ResolveHit.VariableSet_7`(SetDmg).Dmg ← `PromotableOperator_7`(−HealAmt) **diff 0**, 델타 서브그래프가 SetDmg/로그에 미개입 | F9a 원장이 원시 −HealAmt 기대. **로그=원시(−33) / 화면=적용 델타(만피 +0)** 분리 |
| **P4B-16** | ★★ | **만피 힐 = 초록 +0** | PIE/오너 | 8기 만피 시작에서 힐 → "**+0**" 초록, HP바 무이동 | D2 핵심 케이스 — 거짓 "+33" 방지 |
| **P4B-17** | ★★ | **비만피 힐 = 초록 +N** | PIE/오너 | HP 감소 아군 힐 → "**+실제회복량**" 초록 ∧ **숫자 == HP바 이동량** | 적용 델타 = HP바 일치 |
| **P4B-18** | ★★ | **피해 = 빨강 −N 무변경** | PIE/오너 | 공격 시 "**−33**" 빨강(=DF-01 분홍 룩 유지) | 회귀 — SelectString/SelectColor가 피해(Amount>0)도 정확 통과 |
| **P4B-19** | ★ | **3-1·3-2 동일 세션 완결** | 세션/커밋 | 3-1(부호·색)+3-2(콜사이트) **같은 커밋**. 3-2만 랜딩 = 힐 빨간 "−33" 중간상태 금지 | gameplay — 중간 상태 위험 |
| **P4B-20** | ★ | **컴파일 0** | CMP | `BP_BattleManager` 에러 0 · 신규 경고 0 | 표준(MakeSlateColor 브릿지 누락 시 여기서 터짐) |

### §작업1 — 유닛 라벨 `전사 | 이름5` (P4C) · 16건

> 편집: `WBP_SkillMenu:SetActiveUnit` 배선 + ST_UI 4키 + 레벨 8기 CharName + BP_BattleSpawnPoint.CharName 변수. **Format Text 체크포인트 통과가 선행.**

| ID | ★ | 검증 내용 | 판정 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P4C-01** | ★★★ | **★Format Text 인자 핀 생성 체크포인트** | GRAPH | 신규 `K2Node_FormatText`가 Format 리터럴 `"{0} \| {1}"`에서 인자 핀 **`"0"`·`"1"` 생성**. ⚠ **`get_node_infos`(배선 후)로 확인** — `get_node_type_pins` 프리뷰 신뢰 금지(§34(80), NF3). ⚠ Format을 StringTable에 **연결만** 하고 리터럴 미거치면 인자 핀 미생성 → 화면에 `"{0} \| {1}"` 그대로 | qa H3 + ★실증 NF4 — `ResolveHit.FormatText_0`가 리터럴 Format으로 인자 핀 `"0".."8"` 보유·잔류 확인 = 메커니즘 증명. 순서: 리터럴 설정 → 핀 확인 → 나머지 배선 |
| **P4C-02** | ★★★ | **★Append 우회 금지** | GRAPH | 라벨 결합이 `K2Node_FormatText`(포맷텍스트)이지 **`Append` 3연쇄/구분자 하드코딩 아님**. 구분자 `" \| "`는 `Battle.UnitLabel` 스트링테이블 값 | §G 위반(선례 UI_DRAFT_PICK_COUNT/UI_BATTLE_COOLDOWN_FORMAT). **2회 실패 시 Director 보고**(구현 규약) |
| **P4C-03** | ★★★ | **★직업명 소스 = BreakStruct_0.JobId(구조체 필드)** | GRAPH | SelectString 조건의 정수 입력 = `SetActiveUnit.BreakStruct_0` **`JobId_8...` 출력 핀**(구조체 필드, 90100100). ⚠ `Unit.JobId`(BP 변수, 로우키 10102000)면 **FAIL** | 이름 혼동 함정. 실측: BreakStruct_0=BreakFJobStatsRow, JobId_8 유휴 핀 |
| **P4C-04** | ★★ | **SelectString 극성·리터럴** | GRAPH | `SelectString(bPickA=(JobId==90100100), A="Job.Warrior", B="Job.Mage")`. 리터럴 `90100100` 바이트 일치 | DT 6행 실측(전사 90100100/마법사 90100200). N9 계열(정수라 대소문자 무관하나 값 정확도) |
| **P4C-05** | ★★ | **{0} = MakeTextfromStringTable** | GRAPH | `{0}` ← `MakeTextfromStringTable`(Advanced, TableId=`/Game/UI/ST_UI.ST_UI`, Key=SelectString 결과) | 구동 경로(ST_UI). GetLocalizedString/DT_Strings 死데이터라 그 경로 아님 |
| **P4C-06** | ★★ | **{1} = Unit.CharName → ToText** | GRAPH | `{1}` ← `ToText`(string) ← `Unit.CharName`. Unit = FunctionEntry.Unit | ★probe#4 — FormatText 인자 핀에 string 직결 자동변환 불확실 → **명시 ToText가 안전**(계획서 채택). CharName은 SetActiveUnit의 Unit 파라미터에서 |
| **P4C-07** | ★★★ | **★Txt_UnitName SetText 배선 + 삽입 위치** | GRAPH | FormatText 결과 → `Txt_UnitName.SetText`, exec가 `BreakStruct_0`/`GetDataTableRow_1` **하류**. ⚠ Txt_TurnOwner(CallFunction_459/460)는 3스텝 상류라 그 자리 불가 | qa H2 — 실측(459/460=Txt_TurnOwner, IfThenElse_75/bIsParty 상류). Txt_UnitName 현재 setter 0(placeholder "전사 I") |
| **P4C-08** | ★★ | **Txt_TurnLabel "턴" 바인딩·제거 금지** | GRAPH | `Txt_TurnLabel` 위젯 **존치** + `Battle.TurnLabel` 바인딩(Construct/PreConstruct 1회). ⚠ 제거 시 FAIL | qa M1 — spec §3-1a 오너 디자인(Jost 9px 금색). 현재도 올바른 "턴" 표시 중, 결함은 하드코딩뿐 |
| **P4C-09** | ★★ | **RowNotFound 이름 잔류 방지** | GRAPH | `GetDataTableRow_1.RowNotFound`(→CallFunction_13) 경로에서 Txt_UnitName이 갱신 도달 or 폴백(빈/직전값 아님)임이 문서화 | 실측 RowNotFound 라이브. 현행 8기 전부 유효 로우라 도달 불가(오늘)이나 방어. **PLAUSIBLE** |
| **P4C-10** | ★★★ | **★ST_UI 4키 디스크 grep** | 파일 | `ST_UI.uasset` ASCII grep: `Job.Warrior`·`Job.Mage`·`Battle.UnitLabel`·`Battle.TurnLabel` 각 ≥1 ∧ **mtime > 2026-07-16 23:06** | §34(81) — set_entry 무음 → update_metadata_tags 강제 dirty → save → mtime+grep. 베이스라인 현재 4키 0(실측). PIE OFF |
| **P4C-11** | ★★ | **data/st_ui.csv 미러** | 파일 | csv에 4키 반영 | 미러 규약 |
| **P4C-12** | ★★★ | **★레벨 8기 CharName 세팅** | 파일 | 레벨 저장 후 map uasset grep `이름1`~`이름8` ∧ `BP_BattleSpawnPoint.uasset` CharName 변수 존재(mtime > 2026-07-17 01:01). 매핑: 이름1(A3/C_2) 이름2(B3/C_6) 이름3(A4/C_3) 이름4(B4/C_7) 이름5(A1/C_0) 이름6(B1/C_4) 이름7(A2/C_9) 이름8(B2/C_5) | ⚠ `save_assets(["/Game/Stages/map_battle_octopath"])` — save_actor 아님(OFPA 아님). ⚠ 트랜잭션 롤백(§34(84)) — 쓰기/검증 분리. 베이스라인 CharName 0(실측) |
| **P4C-13** | ★ | **레이아웃 무손상** | 오너/umg | 가용 폭 230px, `"마법사 \| 이름1"` ≈100~130px 여유 | umg 실측 |
| **P4C-14** | ★ | **컴파일 0** | CMP | `WBP_SkillMenu` 에러 0 · 신규 경고 0 | 표준 |
| **P4C-15** | ★★★ | **★런타임 조인 8기 전수** | PIE | PIE에서 `TurnQueue[i].CharName == "이름{i+1}"` **8기 전수**(i=0..7, 순서대로 이름1~이름8). ⚠ "전부 상이"는 무감각 게이트(파트2 N1 폐기 부류) — **정확한 매핑 대조** | qa H1 — SSOT 이중유지(SpdOverride↔CharName)의 **유일 감지 수단**. §34(85) PIE refPath + `get_properties(instance,[CharName])`. 파트2 "런타임 spd 8기 실측"과 동층 |
| **P4C-16** | ★★ | **메뉴 라벨 턴마다 변화** | PIE/오너 | 스킬 메뉴 헤더가 `"마법사 \| 이름1"`처럼 뜨고 턴 진행 시 갱신(placeholder "전사 I" 소멸) | 오너 육안 게이트 |

---

## 4. 회귀 (P4R) · 11건

| ID | ★ | 검증 내용 | 판정 | 기대값 | 근거 |
|---|---|---|---|---|---|
| **P4R-01** | ★★★ | **파트3 막기 제자리 무손상** | PIE/오너 | SELF 막기 제자리 유지(작업2가 `IfThenElse_3.else→IfThenElse_4` 무접촉) | 파트3 게이트(f59d1fe) 보호 |
| **P4R-02** | ★★★ | **파트3 SELF 게이팅 무손상** | PIE/오너 | 막기: 자기 피격플린치 없음 ∧ 참격잔상 없음 유지 | 파트3 SELF 항목 |
| **P4R-03** | ★★ | **공격·베기·파이어볼 무변경** | PIE/오너 | ENEMY1 3종 이동·카메라·잔상·플린치 전부 현행(P4A-09가 이동 봉인) | Director "완전 무변경" |
| **P4R-04** | ★★★ | **★ResolveHit 편집 범위 재-스코프** | GRAPH diff | **데미지 서브그래프 diff 0** + **HEAL 꼬리만 신규 ~5노드**(SetHpBefore 로컬 + GetHp/Subtract×2 + SpawnDamageNumber). `VariableSet_6`(SetHp)·`CallFunction_46`·`VariableSet_7`·`CallFunction_24`·`CallFunction_1`·`VariableGet_31` **본체 무변경** | qa M2 — P3-G16 계승. "본체 diff0 + 꼬리만 증분"으로 회귀원 봉인 |
| **P4R-05** | ★★★ | **★크로스그래프 VariableSet_6 봉인** | GRAPH | 작업2=`EventGraph.VariableSet_6`(SetAttackPointOverride 고아화) · 작업3=`ResolveHit.VariableSet_6`(SetHp 무변경). **두 그래프 혼동 0** | 동명 노드가 두 작업에 걸쳐 서로 다른 의도로 등장 — `ResolveHit.VariableSet_6` 오손상 시 힐 사망 |
| **P4R-06** | ★★ | **파트1 무접촉** | GRAPH | Start/Cancel/End·`NotifyAttackButtonClicked`·`StartBattle` diff 0 | 파트1 게이트(7743d85) |
| **P4R-07** | ★★ | **파트2 무접촉** | GRAPH/PIE | `SortTurnQueueBySpd` diff 0 ∧ 8기 spd {97..90} ∧ 첫 8턴 `[C_2,C_6,C_3,C_7,C_0,C_4,C_9,C_5]`. ⚠ CharName 세팅이 SpdOverride를 안 건드림(둘 다 Instance Editable, 같은 액터) | 파트2 게이트 + SSOT 이중유지 |
| **P4R-08** | ★★ | **원장 diff 0(수치)** | LOG | 데미지·턴·순서 무변경. **단 힐 로그 dmg=−33 유지**(P4B-15) | ⚠ 원장은 라벨·색·위치·이름 미기록 → **P4B/P4C 기능은 원장으로 검출 불가**(파트3 R02 한계 계승). diff0=수치 무변경만 |
| **P4R-09** | ★★ | **피해 SpawnDamageNumber 회귀** | PIE | 피해 시 `CallFunction_1` 정상 "−33" 빨강 — 공유 SpawnDamageNumber 내부 수정(SelectString/Abs/SelectColor)이 피해(Amount>0)도 정확 통과 | 공유 함수 수정의 피해측 회귀 |
| **P4R-10** | ★ | **재전투 멱등** | PIE | End→Start 재전투 후 CharName 유지 ∧ 라벨 정상 ∧ 힐 표시 정상 | CharName은 레벨 데이터(재초기화 무관) |
| **P4R-11** | ★ | **WBP_DamageNumber 시그니처 무변경** | GRAPH | `SetTargetWorldLoc`·`EventGraph` diff 0(호출측만 수정) | 위젯 내부 무변경 |

---

## 5. 신규 발견 (계획서·§34에 없던 것) — 7건: High 2 · Medium 2 · Low 3

> **CONFIRMED**=라이브 조회/산술 확정 / **PLAUSIBLE**=논리상 의심, 실측 필요.

### Critical
- **없음.** 소프트락 계열(미연결 exec 종단)은 계획의 와이어 재합류 설계로 원천 차단 — `P4A-05`(Delay 3-way 미연결 종단 0)·`P4B-08`(신규 힐노드 then→CallFunction_24)가 봉인. 파트3 N0가 잡은 부류가 파트4엔 신규로 생기지 않음(실측: 모든 신규 exec가 기존 병합점에 합류).

### High
- **NF1 — 계획서 3-2와 D2가 힐 Amount 소스를 놓고 충돌한다** `CONFIRMED`
  §3-2는 *"신규 SpawnDamageNumber ← Amount ← **기존 `VariableGet_31`(GetDmg) 재사용**"* 이라 명시하고, §D2는 *"Amount = **0 − Delta**"* 로 재규정한다. **D2가 3-2를 폐기**하지만 3-2 문구가 그대로 남아 있어, 구현자가 "1노드" 저비용안(VariableGet_31)을 물릴 위험이 크다.
  실측: `ResolveHit.VariableSet_7`(SetDmg)이 HEAL 경로에서 `Dmg = −HealAmt`(원시 음수)를 쓴다 → `VariableGet_31`(GetDmg)는 **−HealAmt**를 반환. 비만피 힐에선 `−HealAmt ≈ −Delta`(적용량 = 원시량)라 **두 소스가 동일 결과 → 모든 비만피 TC를 통과**. **만피에서만** VariableGet_31=−33 → "**+33**"(HP바 0이동)으로 폭발 = D2가 막으려던 정확히 그 버그. 살아남는 재사용은 **WorldLoc(CallFunction_0)뿐**.
  → **P4B-13(★★★)** 봉인. **계획서에 "3-2의 Amount 소스는 D2로 대체, WorldLoc 재사용만 생존" 정정 권고**(다음 사람이 3-2만 읽고 배선하지 않게).

- **NF2 — 크로스그래프 `VariableSet_6` 동명 함정이 파트4에서 두 작업에 동시 걸린다** `CONFIRMED`
  실측: `BP_BattleManager:EventGraph.VariableSet_6`=`SetAttackPointOverride`(작업2가 **고아화** 대상) · `BP_BattleManager:ResolveHit.VariableSet_6`=`SetHp`(작업3 HEAL **적용 노드, 무변경** 대상). 같은 BP·같은 이름·정반대 취급이 **같은 커밋**에 공존한다. 그래프 미한정 지시서·스크립트가 엉뚱한 VariableSet_6을 건드리면 — `ResolveHit.VariableSet_6`을 고아로 만들 경우 **힐 적용이 통째로 죽는다**(HP 회복 자체가 안 됨, 화면 숫자 이전 문제). `IfThenElse_3`·`IfThenElse_4`도 양 그래프에 별개 존재.
  → **P4A-08 · P4R-05(둘 다 ★★★/★★)**. **모든 지시·작업은 fully-qualified 경로**(`:EventGraph.` / `:ResolveHit.`)로.

### Medium
- **NF3 — Format 인자 핀 검증은 `get_node_type_pins` 프리뷰가 아니라 `get_node_infos`여야 한다** `CONFIRMED`
  계획서 H3 체크포인트는 *"즉시 `get_node_type_pins`로 인자 핀 생성 확인"* 이라 적었으나, **§34(80)이 프리뷰 신뢰 금지를 명문화**한다(첫 매치 오버로드/미승격 표시). 인자 핀 *존재* 여부는 프리뷰로도 보일 여지가 있으나, **최종 판정은 배선 후 `get_node_infos`**. → **P4C-01**에 반영(get_node_infos 명시).

- **NF4 — `K2Node_FormatText` 인자 핀은 Format 리터럴이 짧아져도 잔류한다(orphan 핀)** `CONFIRMED`
  실측: `ResolveHit.FormatText_0`가 리터럴 Format(`{0}`..`{8}`, 9개)인데 인자 핀은 `"0"`..`"17"`(**18개**) — `"9"`..`"17"`은 과거 더 긴 포맷의 **잔류 핀**(현재 포맷이 참조 안 함, 연결만 남음). **유익한 함의**: (a) 리터럴→핀 생성 확정, (b) 핀은 포맷 변경 후에도 잔류 → **H3 우회로(리터럴 "{0} \| {1}" 먼저 설정→핀 생성→그 다음 Format을 StringTable로 연결)가 실제로 성립**(연결된 Format이라도 잔류 핀이 런타임에 `{0}/{1}`을 공급). 단 무해한 잔류 핀이 쌓이지 않게 **신규 노드는 정확히 `"0"·"1"`만** 갖게 검증. → **P4C-01** 근거.

### Low
- **NF5 — 0/저 HP 아군 힐의 델타 표시는 정상(+N)이나 사실상 부활이 된다** `CONFIRMED`(논리)
  `SetHp = Min(Target.Hp + HealAmt, MaxHp)`라 저 HP(예 Hp=1)도 델타 정상(Min 클램프). Hp=0(사망, `bAlive=false`이나 IsValid 유지 — 파트3 실측)인 아군을 힐하면 `Min(0+Heal,Max)=Heal>0` → 화면 "**+Heal**" 초록·HP바 정상. **표시는 버그 아님**(적용 델타 정확). 다만 이는 **사실상 부활**(Hp 0→N)이라 밸런스(사망 아군 힐 허용) 문제 소지 — **범위 밖**(기록만). 델타 계산 자체는 사망 직전에도 정상.

- **NF6 — `HpBefore` 로컬 stale 무위험(연속 힐 2회 포함)** `CONFIRMED`
  `ResolveHit`는 함수라 로컬은 **호출마다 초기화**. 게다가 HEAL 경로 불변식(Set은 SetHp **앞**, Read는 SpawnDamageNumber 지점=SetHp 뒤)상 **매 호출 Write가 Read보다 선행** → 설령 구현자가 실수로 **멤버 변수**로 만들어도 stale 불가(직전 호출값이 이번 Write로 덮임). 같은 전투 내 연속 힐 2회도 각 ResolveHit 호출이 독립. **전제 조건**: `SetHpBefore`가 `IfThenElse_5.then`(HEAL) 서브트리에 있고 Read 전 무조건 실행 — 이 불변식을 **P4B-10**이 봉인. (즉 위험은 "로컬이 stale"이 아니라 "Set을 SetHp 뒤에 두는 배선 실수"다 → P4B-10이 진짜 급소.)

- **NF7 — `SpawnDamageNumber` 내부 off-screen 게이트** `CONFIRMED`
  실측: `IfThenElse_0`(Condition ← `ProjectWorldLocationToWidgetPosition.ReturnValue`, "화면 내인가")의 **`else`가 빈 종단**. WorldLoc가 화면 밖으로 투영되면 위젯 미생성 = 숫자 미표시. 힐 대상이 화면 내면 무관(현행 8기 배치). 힐·피해 공통 경로라 신규 위험 아님(기록만).

### 검토했으나 문제 없음 (빈손 통과 아님 — 근거 명시)
- **SetColorandOpacity가 피해 경로에서 스킵될 위험** → **없음.** `SpawnDamageNumber` 내부는 **단일 exec 경로**(피해/힐 구분은 `SelectColor`(Amount>0) pure 데이터일 뿐 exec 분기 아님). 위젯은 매 호출 `CreateWidget_0` 신규 생성(1회용) → 색은 **매번 명시 Set**(디자인 기본색 무관). 피해(CallFunction_1)·힐(신규) 두 콜사이트 모두 같은 Set 통과 → "피해 경로만 Set 누락" 시나리오 자체가 성립 안 함. → **P4B-05**가 이 단일경로성을 봉인.
- **CharName ↔ SpdOverride SSOT 충돌** → **없음.** 둘 다 `BP_BattleSpawnPoint`의 Instance Editable 변수로 **같은 액터에 병존**, 세팅 스크립트가 서로 다른 필드 → 상호 무간섭(P4R-07). 위험은 "SPD 바꾸면 이름 손으로 맞춰야"인 운영 부담뿐(오너가 단순함을 택함) — **P4C-15**가 런타임 정합을 감시.
- **부호 반전 이중적용** → **P4B-12가 봉인**(Delta 양수 확인 + Amount=0−Delta 폴러티).
- **CallFunction_24 병합 수 변동** → **없음.** VariableSet_7 자리를 신규노드가 1:1 대체 → 6 유지(P4B-09, 실측 6소스).

---

## 6. 커버리지 근거

**검토 축**:
- **순서/시간(★최대 수확)**: `HpBefore` Set↔SetHp exec 순서(P4B-10, D2 급소) · pure 재평가 함정 `Comm_2`(P4B-11)·GetHp 재조회 = 파트3 N1 계열 · Format 리터럴→인자 핀 생성 순서(P4C-01) · 3-1↔3-2 랜딩 순서(P4B-19).
- **경계값**: 만피 힐 델타=0(P4B-16) · 저/0 HP 타겟 델타(NF5) · Amount=0 판별자 극성(P4B-01, `>0` vs `<0`) · SelectString/SelectColor 극성(P4B-04, P4C-04).
- **상태누수**: `AttackPointOverride` 고아화로 오염 원천 소멸(P4A-11) · `HpBefore` 로컬 stale(NF6) · CharName 재전투 멱등(P4R-10).
- **null/off-screen**: SpawnDamageNumber off-screen 게이트(NF7) · GetDataTableRow_1.RowNotFound 이름 잔류(P4C-09) · 에러 grep(P4A-12).
- **타입 정합**: FSlateColor↔LinearColor 브릿지(P4B-03) · string↔FText ToText(P4C-06).
- **명세-구현 갭(★신규 수확)**: 계획서 내부 3-2↔D2 Amount 소스 모순(NF1) · get_node_type_pins vs get_node_infos(NF3).
- **동명/오손상(★신규 수확)**: 크로스그래프 VariableSet_6·IfThenElse_3/4 동명(NF2, P4A-08/P4R-05) · GetArrayItem_0 라이브 5곳(P4A-04) · ResolveHit 데미지 본체 diff0(P4R-04).
- **무감각 게이트 방지**: 런타임 조인 정확 매핑(P4C-15, "전부 상이" 폐기) · 원장 diff0의 한계 명시(P4R-08, 라벨·색·위치 미기록).
- **§G 규약**: Append 우회 금지(P4C-02) · ST_UI 구동 경로(P4C-05).

**판정 불가로 남긴 것(verifier 실측 이월)**:
- `WBP_DamageNumber` 애니의 색 채널 부재 → **P4B-07 PLAUSIBLE**(정적 조회로 MovieSceneColorTrack 유무 미확정, 육안 확인).
- `GetDataTableRow_1.RowNotFound`의 하류 상세(CallFunction_13→?) → **P4C-09 PLAUSIBLE**(현행 8기 유효 로우라 도달 불가, 방어 확인만).
- FormatText 인자 핀에 string 직결 시 자동 ToText 삽입 여부 → **미확정**이라 계획서대로 **명시 ToText**(P4C-06)로 회피(자동변환에 의존 안 함).

**Director 직접 검증 권고**(자체 보고 게이트 불인정): 위 §2 ★게이트 18건. 특히 **P4B-10/11/13(델타·부호·소스)·P4A-04(라이브 5곳)·P4A-08/P4R-05(동명 봉인)·P4C-01(인자 핀)** 은 컴파일0·"핀 연결됨"을 통과하며 기능이 틀리는 부류다.

---

## 7. 게이트 결과 및 재분류 (2026-07-17, Director — 실행=verifier 없이 Director 직접 확인분 포함)

> 전체 서사·근거는 [[파트4_라벨힐_완료]] 참고. 이 절은 위 §0~§6의 59건 각각의 **최종 상태만** 체크한다(CLAUDE.md 문서갱신 룰 — frontmatter와 본문을 함께 갱신).

**PASS 23건**:
- 오너 육안 4항목 매핑(9): `P4C-16` · `P4A-10`·`P4B-17` · `P4B-16` · `P4R-01`·`P4A-09`·`P4R-03`·`P4B-18`·`P4R-09`
- Director 핀검증, 작업1 라벨 GRAPH(8): `P4C-01`·`P4C-02`·`P4C-03`·`P4C-04`·`P4C-05`·`P4C-06`·`P4C-07`·`P4C-09`(★단 RowNotFound 폴백이 `SetText("")+Collapsed` 방식이라 원 TC 문구의 "비-공백" 기대와 다름 — 결과는 안전, 문구만 불일치. [[파트4_라벨힐_완료]] §3 각주 참고)
- 런타임 조인(1): `P4C-15`
- 컴파일 0에러(2): `P4B-20`·`P4C-14`
- 디스크 mtime 정황(2): `P4C-10`·`P4C-12`
- 본 문서화 세션 직접 재확인(1): `P4C-11`(`data/st_ui.csv` 4키 기존 반영 확인)

**F9b(오너 풀플레이) 이월 6건**(PIE-시각형, 이번 세션 미실행): `P4A-11`·`P4A-12`·`P4B-07`·`P4C-13`·`P4R-02`·`P4R-10`

**A2 회귀 스위트 이월 30건**(GRAPH/데이터 변형형 — "코어 게이트 흡수" 후 이월):
- P4A: `01`·`02`·`03`·`04`·`05`·`06`·`07`·`08`
- P4B: `01`·`02`·`03`·`04`·`05`·`06`·`08`·`09`·`10`·`11`·`12`·`13`·`14`·`15`·`19`
- P4C: `08`
- P4R: `04`·`05`·`06`·`07`·`08`·`11`

**★게이트 19건 결산**(§2 목록): 작업1(라벨) 6건(`P4C-01·02·03·07·10·15`) **전체 PASS**. 작업2 4건·작업3 7건·회귀 2건(13건)은 GRAPH형이라 A2 이월.

**재분류 규칙**(qa-critic 판정): PIE-시각형 TC → F9b(오너 풀플레이)가 종착점 / GRAPH·데이터 변형형 TC → 핵심 기능은 오너육안·핀검증·컴파일·mtime으로 이미 실증됐으므로 "코어 게이트 흡수" 처리 후 A2(캐릭터 코어) 회귀 스위트로 이월(배선 세부 재확인은 A2 확장 시 회귀 방지망 역할).

---

## 관련
- 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md`(원문은 파트4 작업 중 덮어쓰기로 소실 — [[파트4_라벨힐_완료]] §9 SSOT 승격 참고)
- [[파트4_라벨힐_완료]](게이트 결과·재분류 서사 전문) · [[파트3_연출_TC]](ID·컬럼·판정도구 원본) · [[파트2_SPD_TC]] · [[파트1_Start_TC]]
- [[언리얼_MCP_실전노하우]] §34 (78)~(86) — (86)은 이번 파트4 세션 실측(BlueprintTools refPath 규약)으로 신규 등재
- [[plan]] · [[청사진]] · [[에이전트팀_설계]]
