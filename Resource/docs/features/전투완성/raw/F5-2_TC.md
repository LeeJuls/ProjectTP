---
type: raw
project: projectTP
feature: 전투완성
stage: F5-2
status: TC 확정 — 착수 대기(F5-1 게이트 통과가 선행, 완료됨). 커밋은 F5-2 게이트에서 Director 일괄
updated: 2026-07-15
---

# F5-2(죽은 유닛 처리) — 적대적 논리 검토 + 작업별 TC

> 대상: [[F5_착수지시서]](노드레벨 SSOT·BLOCKER B1~B5·HIGH) · [[F5-1_완료]](사망·승패 게이트 통과 = 본 문서 전제) · [[F5_TC]](F5 전체 TC 54건 원본) · [[plan]] §F5(L345~418) · [[상태이상_확정]] §5(TS1~TS6/TE1~TE4) · [[광폭화_재검증]] §2 · [[F4_중단_인수인계]] · [[언리얼_MCP_실전노하우]] §L130/§23/§25
> **qa-critic 적대적 검토 산출물 — 검출·설계만.** TC 실행=verifier, 게이트 판정=Director.
> F5-1은 완료(bBattleOver·EnterEnd·EnterTurnEnd TE4 Branch·ResolveHit survivor-count·TickStatusesAtTurnEnd). **F5-2 = TS1~TS6 · DYING · ClickBox · ResetForBattle · InitBattle 리셋확장** 5개 작업.
#projectTP/전투완성

---

## 0. F5-2 범위 (5개 작업)

1. **EnterTurnStart TS1~TS6** — 사망/STUN 턴스킵 + 쿨다운 스윕 + 막기 해제 (H-1: TS1을 SetTurnCounter 앞 / H-2: 스킵경로 exec 종단)
2. **PlayHurtReaction death 분기** — DYING(Row13→FrameCount5→RetriggerableDelay 0.575→bFreeze=1, idle 복귀 없음)
3. **사망 시 ClickBox NoCollision** — ★위치 Director 확정 = **PlayHurtReaction DYING 분기 최상단**
4. **ResetForBattle() 신규 함수** — Hp/스탯 재로드·bAlive·statuses/cooldowns clear·bFreeze0/Row0·ClickBox 복원·HP바 복원
5. **InitBattle 리셋 확장** — 전 유닛 ResetForBattle() + Manager 상태 리셋

**판정도구 약칭**: **GRAPH**=MCP 정적 그래프조회(`find_nodes`·`get_connected_subgraph`·`get_node_infos`) / **LOG**=`D:\unreal\projectTP\Saved\Logs\projectTP.log` grep(또는 MCP `GetLogEntries`) / **PIE**=PIE 인스턴스 프로퍼티 재조회(`get_properties`, `UEDPIE_0`) / **SCF**=스캐폴드 직접호출 후 LOG/PIE / **CMP**=컴파일 에러 0(`warnings_as_errors=true`). **★**=게이트(진행차단). **[N]**=본 검토 신규 TC.

---

## 1. 태스크 지목 8개 각도 — 판정 결과

| # | 각도 | 판정 | 논거 |
|---|---|---|---|
| 1 | 자기 턴에 반격/상태로 죽음 | **N/A(구조적 불가)** | 알파는 1타격=1대상, 반사·DoT·자해 없음, 자기 턴 중 피격 없음. 사망은 오직 상대 턴 `ResolveHit`. F7+ DoT 착지 시 재검(이월) |
| 2 | 스킵 연쇄 중 한 팀 전멸 타이밍 | **안전(CONFIRMED)** | 전멸(bBattleOver=true)은 **kill로만** 발생 → **killing unit 자신의 EnterTurnEnd TE4가 즉시 EnterEnd로 종단**. EnterEnd는 terminal → 후속 시체가 TS1 스킵에 도달할 일 없음. F5-1 실증(turn24 후 turn25 없음) |
| 3 | STUN스킵(TS5)+사망스킵(TS1) 겹침 | **이중처리 불가(CONFIRMED)** | (a) 사망 시 F4 step8이 ActiveStatuses **Clear** → 시체는 STUN 없음 (b) **TS1<TS4 + 종단** → 사망이 항상 먼저 잡고 종료. **단 H-2(exec 종단) 위반 시에만** 겹침 → N02가 유일 방어선 |
| 4 | CurrentIndex wrap(%8)+스킵 겹침 | **안전(CONFIRMED)** | 스킵도 **full EnterTurnEnd 경유** → TE3 `(i+1)%8` 정상, wrap 7→0 정상. 연쇄 스킵도 각 반복이 `Delay(0.35)` 통과 → 스택 누적 0 |
| 5 | ResetForBattle을 안 죽은 유닛에 호출 | **대체로 무해 — 4개 신규결함** | G-B/G-C/G-F/G-G |
| 6 | 재전투 후 bFreeze/상태 잔존 | **BLOCKER-3+ResetForBattle 처리 — 단 latent race** | **G-A(신규)**·G-B(신규) |
| 7 | TS3 쿨다운 하한/Map순회 중 수정 | **N06 정적체크 커버** | zero-entry 미prune 무해(guard `>0`), 음수 미방지도 guard상 무해하나 스펙위반 → N06 `Max(0,V-1)` 정적확인이 방어 |
| 8 | 시체 stale 참조(SelectedTargets) | **안전(조건부)** | SelectedTargets 매 턴 AwaitCommand Clear + Executing이 kill 후 재읽기 안 함. 단 H-7(ResolveHit bAlive 가드 부재 가능) → N15 커버 |

**결론**: 8개 각도 중 6개 구조적 안전(논거 확보), 2개(#5·#6 = ResetForBattle/재전투)에서 신규 결함 6건 검출. 기존 [[F5_TC]]의 BLOCKER5·HIGH8은 F5-2 범위에 유효하며 본 문서는 그 위에 얹는 증분(NEW).

**결정적 확인**: 기존 `InitBattle`에 이미 `SetCurrentIndex(0)`·`SetTurnCounter(0)` 실재([[전투로그]] L33) → **재시작 인덱스/턴 리셋은 갭 아님**(회귀만 방지하면 됨 = N32).

---

## 2. 신규 발견 G-A ~ G-I (심각도순)

### [HIGH] G-B — ResetForBattle의 SpriteMID SetScalar가 `declaring_class` 누락 시 무음 실패 → 전원 "얼어붙은 채 부활" (CONFIRMED)
`ResetForBattle` step6은 SpriteMID에 **4개 SetScalar**(bFreeze=0·RowIndex=0·FrameCount=6·TimeOffset=0)를 **F5-2에서 처음 신규 생성**. 노하우 §L130: `SetScalarParameterValue`가 `declaring_class=/Script/Engine.MaterialInstanceDynamic` 미명시 시 **MPC 오버로드로 무음 실패**. 4개 다 누락되면 스프라이트 리셋 안 됨 → **BLOCKER-3와 동일한 "누운 시체 부활" 증상이 다른 근본원인으로 재현**. BLOCKER-5(N16④)는 이 함정을 DYING 분기에만 걸었으므로 **ResetForBattle 4개 노드에도 동일 적용 필수**. → N28. (N18 런타임 `bFreeze==0`이 결과는 잡으나, 정적 declaring_class 체크가 컴파일 시점 조기 검출)

### [MED] G-A — DYING의 RetriggerableDelay(0.575) latent가 사망보다 오래 살아 후속 ResetForBattle을 덮어씀 → 살아난 유닛 재동결 (CONFIRMED 메커니즘 / PLAUSIBLE 도달성)
`PlayHurtReaction` death: `…RowIndex=13 → RetriggerableDelay(0.575) → bFreeze=1`. 이 latent가 사망+0.575s까지 생존. 그 창 안에 `InitBattle→ResetForBattle`(bAlive=true·bFreeze=0·RowIndex=0)이 실행되면 **뒤늦게 완료된 latent가 bFreeze=1 재세팅** → 부활한 유닛이 IDLE 마지막 프레임에 동결("서 있는 시체").
- **F5-2 자체 검증 흐름 미도달**: M-8상 InitBattle은 End 도달(kill +1.20s) 후에만 → 마지막 사망 latent는 +0.825s에 완료. 안전.
- **그러나 A6 "무전환 재시작 버튼"(설계 목표)이 아무 때나 눌리면 사망 후 0.575s 내 재시작 시 재현.** F5가 리셋 인프라를 짓는 지금이 가드 시점.
- **권고(값싼 가드)**: `bFreeze=1` 노드를 **`Branch(bAlive==false)`로 게이팅**. → N26.

### [MED] G-C — ResetForBattle의 Hp 소스: DT_JobStats 재조회는 조회 실패 시 Hp=0 (권고: MaxHp 캐시)
착수지시서 step1이 "DT_JobStats(JobId) 재조회" 또는 "Hp=MaxHp" 선택지. **재조회는 JobId 룩업 실패 시 Out Row 기본값 Hp=0** → "Hp=0 부활" 재발. **전투 중 Atk/Def는 절대 변이 안 됨**(ATK_DOWN은 데미지 계산 시점 배율일 뿐 스탯 미변경) → **`Hp=MaxHp`(BeginPlay 캐시)만으로 완전 충분+안전**. → N29. (F7+ 영구 스탯버프 생기면 재검, 이월)

### [MED/LOW] G-D — TE1의 카메라 복귀가 스킵 턴마다 실행(카메라 미부착인데) → 무회귀 기반선(N25) 오염 가능 (PLAUSIBLE)
plan L372: EnterTurnEnd TE1 = `MarkerOff + SetViewTargetWithBlend(DefaultCamera,0.3s)` **무조건 실행**. **사망/기절 스킵도 full EnterTurnEnd 경유**하므로 TE1 카메라 복귀가 **매 스킵 턴 발동**(그 턴엔 카메라 미부착). idempotent면 무해, 불필요 CamCut 로그가 찍히면 N25("CamCut 로그 기존과 동일") 회귀 대조 어긋남. → 스킵 턴 로그에서 카메라 아티팩트 유무 확인, 발생 시 TE1 카메라 노드를 "정상 진행 턴에만" 게이팅 권고.

### [LOW / 조건부] G-E ~ G-I
- **G-E [N/A — Director 확정]**: **M-5 오너 확정 = "죽은 유닛 HP바 유지"** → ResetForBattle에 SetVisibility 복원 **불요**. N31 = **N/A**.
- **G-F(LOW)**: ResetForBattle `FrameCount=6` 하드코딩 = 전 잡 IDLE 6프레임 공유 가정. motions.csv Row0 확인.
- **G-G(LOW)**: ResetForBattle `CachedUnitFrame.SetHp`·SpriteMID 4종 SetScalar에 **IsValid 가드 없으면 위젯/MID null 시 Accessed None**. E2 선례대로 가드. → N30.
- **G-H(LOW·회귀)**: InitBattle 확장이 **기존 `SetCurrentIndex(0)`·`SetTurnCounter(0)`([[전투로그]] L33) 훼손 안 하는지** 확인. → N32.
- **G-I [Director 확정]**: `ClickBox→NoCollision`은 **PlayHurtReaction DYING 분기 최상단**(RetriggerableDelay보다 앞 = 즉시). → N27.

---

## 3. 작업별 TC 표

### 작업1 — EnterTurnStart TS1~TS6 (사망/STUN 스킵 + 쿨다운스윕 + 막기해제)

| ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|
| **N01**★ | **TS1<TS2(정적)**: exec 체인에서 `bAlive` Branch가 `SetTurnCounter`보다 앞. `bAlive` Get 대상이 **새 Set된 ActiveUnit**(직전 유닛 아님) | GRAPH(exec순서+데이터핀 소스) | 대기 |
| **N04**★ | **사망스킵 TurnCounter 미증가(H-1 런타임)**: B1(1기) 사망 후 **A1 연속 두 턴 사이 turn 증분==7**(살아있는 유닛 수). 8이면 TS1이 TS2 뒤 | LOG(`attacker=A1` 라인 turn값 차) | 대기 |
| **N02**★ | **스킵 exec 종단(H-2)**: TS1 True·TS5 True의 `EnterTurnEnd` 호출노드 **then 미연결**. MarkerOn/AwaitCommand 경로 부재 | GRAPH(exec 추적) | 대기 |
| **N03**★ | **큐 무결성(런타임)**: B1 킬 후 2사이클 → ①매 EnterTurnEnd당 CurrentIndex **정확히 +1**(2칸 0회) ②생존7기 사이클당 1회씩 attacker ③시체B1 **AwaitCommand 미진입**(BattleState==2 폴링 0회) | LOG(attacker 시퀀스)+PIE(CurrentIndex 폴링) | 대기 |
| **N06** | **TS3 실재+TS3<TS4(정적)**: 쿨다운 스윕루프(`Keys` ForEach→`Max(0,V−1)` Set)+`SetbBlockActive(false)`가 **둘 다 STUN판정(TS4) 앞**. Keys 먼저 뽑아 순회(Map 변경 중 순회 아님) | GRAPH | 대기 |
| **N07** | **영구막기 차단(TS3 위반 검출)**: SCF `B1.bBlockActive=true`+`ApplyStatus(B1,STUN,0,1)` → 기절턴 종료 후 `bBlockActive==false`. true 잔존 시 영구 막기 | SCF+PIE | 대기 |
| **SE06** | **기절턴 쿨다운·막기 진행(TS3<TS4)**: SCF `SetSkillCooldown(B1,31001000,1)`+`bBlockActive=true`+`STUN` → 종료 후 `쿨다운==0` ∧ `bBlockActive==false`. 하나라도 1/true면 이중 페널티 | SCF+PIE(Map·bool) | 대기 |
| **SE07** | **기절스킵은 TurnCounter +1**(사망스킵과 구분): 기절턴에도 TurnCounter 증가 → turn 시퀀스에 갭(…5,**7**…) | LOG(turn 시퀀스)+PIE | 대기 |
| **SE09** | **재부여=갱신**: SCF `STUN` 2연속 → ActiveStatuses 길이 **1** ∧ remaining==1(연장없음) ∧ REFRESH 로그 1줄 | SCF+PIE+LOG | 대기 |
| **SE10** | **기절자는 생존**: 기절 B1이 타겟풀 포함·클릭가능(QueryOnly)·`bAlive==true` (사망자와 명확 구분) | SCF+PIE | 대기 |
| **N05** | **전원기절 스트레스(E5)**: SkillId핀=`31001000`+`DebugForceEffectChance=1.0` → hang/크래시 0·턴 계속전진(CurrentIndex 순환)·각 유닛 **1턴만 스킵**·유한턴 내 End. **종료 후 핀 `31000000` 원복** | LOG(전 시퀀스)+PIE | 대기 |

### 작업2 — PlayHurtReaction death 분기 (DYING)

| ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|
| **N16**★ | **DYING 배선(B5)**: ①`bAlive` Branch가 IsValid(SpriteMID) 가드 안쪽 ②DYING이 `RowIndex=0` 복귀노드에 **미연결** ③`bFreeze=1`이 **RetriggerableDelay(≈0.575) 뒤** ④SetScalar **`declaring_class=MID` 명시** ⑤대상=SpriteMID | GRAPH+CMP | 대기 |
| **N17**★ | **DYING 스칼라 3종(M-10)**: `RowIndex=13` **+ FrameCount=5**(HURT의 4 잔존 금지) **+ TimeOffset=GetGameTimeInSeconds** 전부 세팅 | GRAPH(SetScalar 3개·핀값) | 대기 |
| **N19** | **DYING이 VFX 삼키지 않음**: 킬링블로우에도 히트VFX 발생(분기가 공용VFX **뒤** 또는 양분기 배치) | GRAPH+LOG/PIE(VFX 액터) | 대기 |
| **N13**★ | **PlayHurtReaction 플래그 set-only(H-5)**: 서브그래프에 `SetbBattleOver`/`SetWinningTeam` **0개**(마진 0.95s 잠식 차단) | GRAPH | 대기 |
| **N26**[N] | **bFreeze latent 재동결 가드(G-A)**: `bFreeze=1` 노드가 **`Branch(bAlive==false)`로 게이팅**(RetriggerableDelay 완료 시 유닛이 리셋되어 살아있으면 미실행). 미가드면 restart race 시 "서있는 시체" | GRAPH(exec) + (선택)SCF 재현: 사망 직후 InitBattle 강제→0.6s후 bFreeze 폴링 | 대기 |
| **F5-06** | **시체 정지(기능판)**: 사망 0.6s후~30s후 두 시점 `RowIndex==13 ∧ FrameCount==5 ∧ bFreeze==1` 동일 | PIE(MID scalar) 또는 GRAPH(복귀경로 부재) | 대기 |

### 작업3 — 사망 시 ClickBox NoCollision (★위치 Director 확정 = DYING 분기 최상단)

| ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|
| **N15**★ | **시체 재타격 방어(H-7)**: SCF로 사망B1 강제 타겟커밋 → ①`NotifyUnitClicked` 거부(SelectedTargets 길이 0) ②(강행 시) ResolveHit 진입부 `bAlive` 가드 경고+return, BattleLog 0줄, DYING 재재생 안 함, Hp==0 불변 | SCF+LOG+PIE | 대기 |
| **F5-07**★ | **사망자 타겟불가**: ①`ResolveTargetPool(ENEMY1,A1)`에 B1 **부재** ②B1 `ClickBox.collisionEnabled=="NoCollision"` ③SCF 시체클릭 → 거부(SelectedTargets 0 유지) | SCF+PIE+LOG | 대기 |
| **N27**[N] | **ClickBox-off 배치(G-I, Director 확정)**: `SetCollisionEnabled(NoCollision)` 노드가 **PlayHurtReaction DYING 분기 최상단**(RetriggerableDelay 앞 = 즉시). 정적 확인 | GRAPH | 대기 |
| **F5-12** | **하이라이트 잔존 없음**: 하이라이트된 적이 그 타격에 사망 → 직후·End 후 8기 하이라이트 OFF | PIE(8기 하이라이트 프로퍼티) | 대기 |

### 작업4 — ResetForBattle() 신규 함수

| ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|
| **N28**[N]★ | **ResetForBattle SetScalar declaring_class(G-B)**: step6의 4개 SetScalar(bFreeze/RowIndex/FrameCount/TimeOffset) 전부 **`declaring_class=MID` 명시** + IsValid(SpriteMID) 가드. 미명시 시 무음실패로 얼어붙은 부활 | GRAPH(노드 속성)+CMP | 대기 |
| **N29**[N] | **Hp 소스=MaxHp(G-C)**: step1이 `Hp=MaxHp`(캐시) 사용, DT_JobStats 재조회 아님(또는 재조회면 JobId 유효+row-not-found 방어). SetHp가 **Hp 복원 뒤**(마지막) 실행 | GRAPH(핀 소스·exec 순서) | 대기 |
| **N30**[N] | **CachedUnitFrame·SpriteMID 가드(G-G)**: `CachedUnitFrame.SetHp` 앞 IsValid, SpriteMID SetScalar 앞 IsValid. null 시 Accessed None 0 | GRAPH+LOG(Accessed None grep) | 대기 |
| ~~N31~~ | **[N/A — Director 확정]** HP바 가시성 복원(G-E): **M-5 = "죽은 유닛 HP바 유지"** 확정 → SetVisibility 복원 불요 | — | **N/A** |

### 작업5 — InitBattle 리셋 확장

| ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|
| **N18**★ | **완전 리셋(B3)**: End 후 InitBattle() 재호출 → 8기 전수 `Hp==MaxHp ∧ bAlive ∧ ActiveStatuses.Length==0 ∧ SkillCooldowns 0/빈 ∧ bBlockActive==false ∧ bFreeze==0 ∧ RowIndex==0 ∧ ClickBox=="QueryOnly" ∧ HP바 MaxHp/MaxHp` + Manager `SelectedTargets.Length==0 ∧ bBattleOver==false ∧ CurrentIndex==0 ∧ TurnCounter==0 ∧ BattleState==0` → **재시작 후 1턴 정상 완주**. **End 도달 후에만**(M-8) | SCF+PIE(8기+Manager 전수)+CMP+LOG | 대기 |
| **N32**[N] | **InitBattle 회귀(G-H)**: 확장 편집 후에도 `SetCurrentIndex(0)`·`SetTurnCounter(0)` 노드 실재+exec 연결 유지. 전 유닛 `ResetForBattle()`이 `ForEachLoop(TurnQueue)`로 **8회 호출** | GRAPH | 대기 |
| **F5-03**★ | **큐 길이 불변**: 사망 전후 `GetTurnQueue().Length==8`. TurnQueue Remove/Insert/Clear 노드 0개(초기 Register 제외)+`Modulo by zero` 경고 0건 | PIE(Length)+GRAPH(배열 변경 노드)+LOG | 대기 |

---

## 4. 게이트 TC 구체적 판정법 (착수지시서 게이트)

| 게이트 | 구체적 PASS/FAIL 판정법 |
|---|---|
| **turn 증분==7** | `grep "attacker=A1" projectTP.log` → turn값 시퀀스 추출. **정확히 1기(B1)만 사망** 고정 상태에서 연속 A1 두 라인의 turn차 **==7 PASS / ==8 FAIL**. (사망 N기면 기대치=8−N, verifier가 사망수 고정 후 계산) → N04 |
| **AwaitCommand 미진입 + CurrentIndex 1칸** | 정적(견고): N02 = TS1 EnterTurnEnd호출 노드 then 미연결 → exec가 TS6로 안 흐름. 런타임: 시체 B1 턴 구간 BattleState 폴링 → **==2(AwaitCommand) 0회** + B1 attacker BattleLog **0줄** + CurrentIndex 폴링이 매 EnterTurnEnd당 **+1**(2칸 점프 0회) → N02+N03 |
| **시체 클릭불가** | ①정적: ClickBox `SetCollisionEnabled(NoCollision)` 노드 실재(DYING 분기 최상단) ②런타임: B1 `ClickBox.collisionEnabled=="NoCollision"` PIE ③SCF: `NotifyUnitClicked(B1)` → SelectedTargets 길이 **0 유지**(거부) → N15+N27+F5-07 |
| **재플레이 정상** | End 도달 후 InitBattle() 재호출(SCF) → **N18 전수 체크**(특히 `bFreeze==0 ∧ RowIndex==0`이 G-B 무음실패의 결정적 검출기) → 이어 공격 1회 dmg 정상(=30) 실증. **반드시 End 후 실행**(M-8) → N18 |
| **큐길이 8불변** | 정적: TurnQueue 변경노드 0개(Register 제외). 런타임: 사망전/후/End 모두 `Length==8` + `grep -c "Modulo by zero"`==0 → F5-03 |

---

## 5. 계획 추가/수정 권고 (Director 판정용)

1. **[HIGH] ResetForBattle 4개 SetScalar에 `declaring_class=MID` 명시를 착수지시서에 명문화**(G-B). B5(N16④)가 DYING 분기에만 걸어둔 함정이 ResetForBattle에서 재발 → N28 정적 게이트.
2. **[MED] `bFreeze=1` 노드를 `Branch(bAlive==false)`로 게이팅**(G-A). A6 재시작버튼의 latent-race 봉쇄. 값싼 가드 → N26.
3. **[MED] ResetForBattle Hp 소스를 `Hp=MaxHp`로 확정**(G-C). DT 재조회 경로 폐기(조회실패=Hp0 재발 방지) → N29.
4. **[LOW] IsValid 가드**(SpriteMID·CachedUnitFrame) ResetForBattle에 명시(G-G, N30) + InitBattle 회귀체크(N32).
5. **[LOW] 스킵 턴 카메라 아티팩트 확인**(G-D) — verifier가 스킵 턴 로그에서 불필요 카메라 복귀 유무 관찰, N25 회귀 기반선 반영.

**신규 TC 6건 확정**(N26·N27·N28·N29·N30·N32). N31은 **N/A**(M-5 = HP바 유지). 나머지 F5-2 범위는 기존 [[F5_TC]](N01~N19, SE06/07/09/10, F5-03/06/07/12)가 커버.

**커버리지 근거(빈손 통과 아님)**: 경계값(turn증분·bFreeze 고정프레임·%8 wrap)·동시성(스킵의 full-EnterTurnEnd 경유·마진 0.95s)·순서(TS1<TS2<TS3<TS4, TE2<TE3)·null(SpriteMID/CachedUnitFrame IsValid)·상태누수(bFreeze/ClickBox/쿨다운 잔존·latent race)·무음실패(declaring_class ×2) 전 축 점검.

**PLAUSIBLE 플래그(통과 아님, verifier 실측 확정 요망)**: G-D(TE1 카메라 스킵턴 아티팩트)·G-A 도달성 — 실제 노드/런타임 확인 전까지 PLAUSIBLE. 놓친 버그가 통과된 버그보다 나쁘므로 둘 다 TC 등재.

---

## 관련
- [[F5_착수지시서]] · [[F5-1_완료]] · [[F5_TC]] · [[plan]] §F5
- [[상태이상_확정]] §5 · [[광폭화_재검증]] §2 · [[F4_중단_인수인계]] · [[전투로그]]
- [[언리얼_MCP_실전노하우]] §L130(declaring_class)·§23·§25
