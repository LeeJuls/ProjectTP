---
type: qa
project: projectTP
feature: 전투완성
stage: F4
status: TC 확정 — 개발 착수 전 BLOCKER 5건 Director 판정 필요
updated: 2026-07-15
---

# F4(TakeHit §8 코어) — TC 설계 + plan 적대적 검토

> 대상: [[plan]] §F4(L251~341) · [[상태이상_확정]] §5~§8·§11·§15 · [[스탯_전투공식_v1]] §5(정답지)·§8(계약) · [[전투로그]](현행 로그 구현) · [[언리얼_MCP_실전노하우]] §7~§11·§13(함정③④⑥⑨⑩⑰).
> 전제 = Director MCP 실측 팩트(재조사 불요). TC 실행 = verifier, 게이트 판정 = Director. **본 문서는 검출·설계만 — BP/데이터 수정 없음.**
> **기능 TC = verifier 게이트(진행 차단) / 비주얼 TC = 오너 육안(진행 불차단)** — 오너 지시 반영.
#projectTP/전투완성

---

## 0. 요약

| 구분 | 개수 |
|---|---|
| 기능 TC (verifier 게이트) | **51** — 승계 7 + 상태이상 통합 F4분 17 + **신규 예외 27** |
| 비주얼 TC (오너 육안, 불차단) | **4** |
| 이월 TC | 3 |
| **BLOCKER**(착수 전 결정 필수) | **5** |
| HIGH | 8 |
| MEDIUM | 7 |

---

## ① 적대적 검토 — BLOCKER (착수 전 Director/엔지니어 결정 필수)

> 아래 5건은 "코딩하면 깨진다"가 아니라 **"결정 없이 코딩하면 반드시 둘 중 틀린 쪽을 고른다"**는 명세 공백·모순이다. 전부 지금 1줄 결정하면 비용 0, F5 이후 발견하면 그래프 수술이다.

### [BLOCKER-1] HP 차감 주체가 이중 — 데미지 2배 / 로그·화면 불일치 (CONFIRMED)

**모순**: [[plan]] §4-2 step8 = `Target.Hp = Max(0, Target.Hp − Dmg)` → **Manager가 HP를 쓴다**. 그런데 Director F4 지시문 = "유닛 쪽에 **HP 차감** + `CachedUnitFrame.SetHp()` 호출 추가" → **유닛도 HP를 쓴다**.

**재현**: A1(전사 Atk40) → B1(전사 Def10/Hp90) 기본공격.
1. Manager.TakeHit step8: `B1.Hp = 90 − 30 = 60` → step9 로그 `dmg=30|hp=60` 방출.
2. 유닛 B1의 `TakeHit`(연출 이벤트)가 `Hp = Hp − PendingDmg`를 또 실행 → `B1.Hp = 30`.
3. `CachedUnitFrame.SetHp(30, 90)` → **화면 HP 바 = 33%**.
→ **로그(hp=60) ≠ 화면(30/90) ≠ 실제 유닛 Hp(30).** TTK가 절반이 되고 F9a 원장이 전부 어긋난다. 로그만 보는 verifier는 PASS 판정한다(로그는 정상값 60).

**요구 결정**: HP를 쓰는 곳은 **정확히 1곳**. 권고 = **Manager.TakeHit step8이 유일한 writer**, 유닛의 연출 이벤트는 **`CachedUnitFrame.SetHp(Hp, MaxHp)` 읽기-갱신만**(차감 금지). → TC-F4-N09/N11.

### [BLOCKER-2] 로그 방출 지점 — 현행 구현은 `EnterExecuting` 진입 직후, §8은 `TakeHit` step9 (CONFIRMED)

**모순**: [[전투로그]] "구현 위치" = **`EnterExecuting` 진입 직후(`SetBattleState(4)` 이전)** 에 PrintString. 즉 **Delay 0.25 이전, 데미지가 존재하기 전**에 로그가 나간다. 반면 [[plan]] §4-2 step9 = "BattleLog 로그 방출 → Return"(TakeHit 말미, HP 적용 후). plan §4-3은 "기존 포맷·기존 TurnCounter 재사용 / 파서 호환 유지"라고만 써서 **"기존 PrintString 노드를 그 자리에서 확장하라"로 읽힌다** — 이 오독이 기본값이다.

**재현**: 기존 노드에 `dmg`/`hp` 인자만 추가하면, 그 시점엔 이번 턴의 dmg가 아직 계산되지 않았다.
- turn1: `dmg=0|hp=90`(피격 전 HP) — 실제로는 30을 맞았는데 로그는 0.
- turn2: `dmg=<turn1의 값>` — **1턴 밀린 stale 값**이 계속 기록된다.
→ TC-F4-07(hp = MaxHp − dmg)이 turn1에서 FAIL하며 잡히긴 하나, **원인 규명에 1사이클을 태운다.**

**요구 결정**: **`EnterExecuting`의 기존 BattleLog PrintString을 제거하고 `TakeHit` step9로 이설**한다고 plan에 명문화. 부수효과 2건도 함께 확정:
- 조기 return 경로(step0 쿨다운 가드 / step1 found=false)는 **BattleLog 라인을 남기지 않는다**(별도 경고 라인만) — 현행은 무조건 1줄이 나갔다.
- `target=`은 `SelectedTargets[0]`이 아니라 **TakeHit의 `Target` 파라미터**를 써야 한다(A2 AoE 대비).

### [BLOCKER-3] TakeHit = Function Graph인데 step9가 latent 보유 커스텀이벤트를 호출 — 함정④/⑨ 충돌 (CONFIRMED 문서 3자 충돌 / PLAUSIBLE 실동작)

**모순**: [[plan]] §4-1 = "§8 판정 자체는 전부 동기 연산이라 **Function Graph**로 가능" + "마지막에 기존 애니 재생용 **Custom Event를 호출**". 그런데
- **함정④**(§8): latent 노드(Delay 계열)는 Function Graph에서 사용 불가.
- **함정⑨**(§11, W2 실측): "**다른 BP의 커스텀 이벤트를 CallFunction으로 호출하는 것은, 그 이벤트가 내부에 latent 노드를 가지고 있다면 호출자 관점에서도 latent 호출이 된다**"(PlayAttack 실측, 1턴 +0.58s).
- 유닛의 `TakeHit` 연출 이벤트는 **`RetriggerableDelay`(0.45s, idle 복귀)를 내부에 보유**한다.

→ Function Graph가 "호출자 관점에서 latent가 되는 호출"을 품는 게 성립하는지 **이 프로젝트에서 실측된 바 없다.** 성립하지 않으면 컴파일 실패, 성립하면 step9의 **쿨다운 세팅·BattleLog 방출이 0.45초 뒤로 밀린다**(F5에서 `bBattleOver` 세팅이 이 뒤에 붙으면 EnterTurnEnd 게이트와의 마진이 그만큼 깎인다).

**요구 결정**: F4 착수 **첫 액션**으로 1회 실측(TC-F4-N20/N21). 실패 시 **대안 확정**: 연출 호출을 TakeHit 밖으로 빼서 `EnterExecuting` then_0에 두기 —
```
then_0: Delay(0.25) → [배열 ForEach] → Manager.TakeHit(Attacker, T, SkillId)  ← 순수 동기 Function(계산·HP·로그·플래그)
                                     → T.PlayHurtReaction()                    ← 연출(EventGraph, latent OK)
```
이 배치가 **F5 레이스 대책과도 정합**(플래그가 게이트보다 확실히 먼저 확정)이라 권고안이다.

### [BLOCKER-4] `PendingHitTarget`/`PendingHitDied` 소유자 미확정 (CONFIRMED 모순)

[[plan]] §4-1 본문 = "TakeHit 로직 마지막에 **멤버 변수**(예: `PendingHitTarget`, `PendingHitDied`)를 세팅" → 이름상 **Manager 소유**로 읽힌다. 같은 §4-1 말미 + [[상태이상_확정]] §11⑤·§15-4 = "HURT 리액션 이벤트(`PendingHitTarget`+`RetriggerableDelay`)는 **대상 유닛(BP_BattleSpawnPoint) 소유**로 배치할 것 — **F4 착수 시 최우선 확인**".

**두 서술이 양립 불가**: 이벤트가 유닛 소유라면 유닛 자신이 곧 Target이므로 `PendingHitTarget`(어느 유닛을 때릴지)이라는 멤버는 **유닛 위에서 의미가 없다**. 그대로 Manager에 두면 §15-4가 경고한 함정(Manager 단일 인스턴스의 RetriggerableDelay가 A2 AoE에서 리셋 → 마지막 대상만 idle 복귀)을 **F4에서 그대로 짓는다**(선례 = `WalkForward`의 `WalkTargetLoc`은 **유닛 멤버**다).

**요구 결정**: 플래그는 **대상 유닛 소유 bool**(`bPendingDied` 등) — Manager가 `Target.bPendingDied = ...`를 세팅한 뒤 `Target.<연출이벤트>()`를 호출. RetriggerableDelay 체인은 **유닛 그래프에만** 존재. → TC-F4-N05/N20.

### [BLOCKER-5] Manager 함수 `TakeHit` ↔ 유닛 커스텀이벤트 `TakeHit` 동명 — 오배선 시 무한 재귀(에디터 크래시) (CONFIRMED 위험 / PLAUSIBLE 발생)

클래스가 달라 컴파일 충돌은 없다. **문제는 노드 생성 단계다**: Manager 그래프에서 `find_node_types("TakeHit")`는 **self 함수 `TakeHit`과 대상 유닛의 이벤트 `TakeHit` 둘 다**를 후보로 낸다. 함정⑨/⑩상 "다른 BP의 커스텀 이벤트 CallFunction 노드는 검색 문자열 그대로 `create_node`하면 실패 → **기존 노드 역산이 유일 해법**"이라 엔지니어는 기존 `SelectedTarget.TakeHit()` 노드를 복제하게 되는데, 이때 **Target 핀을 self로 잘못 물리면 `Manager.TakeHit` → `Manager.TakeHit` 무한 재귀 → 스택 오버플로 → 에디터 크래시**다.

**요구 결정**: 둘 중 하나를 개명. 권고 = **유닛 이벤트를 `PlayHurtReaction`으로 개명**(plan §4-1이 이미 옵션으로 제시) 또는 Manager 함수를 `ResolveHit`/`ApplyHit`로. 개명은 지금 비용 0. → TC-F4-N05.

---

## ② 적대적 검토 — HIGH

### [H-1] `FormatText`의 Integer 그룹핑 → `action=31,000,000` (CONFIRMED)
현행 로그는 `FormatText`의 와일드카드 인자에 Integer를 직접 연결한다([[전투로그]] §구현: `{0}`=turn, Integer 자동승격). BP가 Integer→Text 승격 시 삽입하는 `ToText (Integer)` 노드는 **`UseGrouping` 기본값이 true**다. `turn=1`처럼 3자리 이하는 증상이 없어 지금까지 안 걸렸지만, **`action=<SkillId>`는 8자리(`31000000`)** — 그대로 꽂으면 로그가 `action=31,000,000`으로 나간다.
**영향**: TC-F4-06(스키마) FAIL + `action=SkillId`↔`skills.csv` 조인(TC-QA08) 붕괴 + F9a 원장 파서 오염.
**대책**: SkillId를 **`ToString(int)`로 String화한 뒤** FormatText 인자에 연결(또는 `UseGrouping=false` 명시). → TC-F4-N22.

### [H-2] 실수 정밀도 — 베기가 42가 아니라 **41**로 나올 수 있다 (PLAUSIBLE, 미실측)
`Base = floor(Atk × OutgoingAtkMult × PowerRate)`, 단일 floor. **`40 × 1.3`이 유일한 칼날 경계**다:
- `PowerRate`가 **single(float32)**: `1.3f = 1.2999999523…` → `40 × 1.3f = 51.999998…` → **floor = 51 → dmg = 41**(정답지 42 아님).
- `PowerRate`가 **double(UE5 BP Real 기본)**: `1.3d = 1.30000000000000004…` → `40 × 1.3 = 52.0000000000000018` → floor = 52 → **dmg = 42** ✔
다른 셀은 전부 안전(`42×1.7 = 71.4`, `42×0.8 = 33.6`, `42×0.75×1.7×1.5 = 80.32…` — single/double 모두 동일 floor).
**영향**: TC-F4-03이 41로 FAIL했을 때 **로직 버그로 오진하고 그래프를 뜯게 된다**(실제 원인은 `F_SkillsRow.powerRate`의 정밀도 또는 중간 float32 로컬 변수).
**대책**: 착수 전 `F_SkillsRow.powerRate` 정밀도 확인 + 데미지 체인 로컬 변수에 float32 금지. **41 = single-precision의 지문**임을 미리 못박는다. → TC-F4-N14.

### [H-3] `int × float` 절삭 — 기본공격만 정답이 나오는 위양성 (CONFIRMED 위험)
`Atk`(int) × `PowerRate`(float)를 BP에서 **정수 Multiply**로 배선하면 PowerRate가 int로 절삭된다: `1.0→1`(정답), `1.3→1`, `1.7→1`.
- 기본공격(PR=1.0): `40×1 = 40 − 10 = 30` → **TC-F4-01/02 PASS**
- 베기(PR=1.3): `40×1 = 40 − 10 = 30` → 정답 42인데 **30**
- 파이어볼(PR=1.7): `42×1 = 42 − 10 = 32` → 정답 61인데 **32**
→ **F4의 게이트 TC 2개(01/02)가 전부 통과하는데 스킬만 조용히 망가진다.** TC-F4-03(베기 42)이 유일한 검출기 = **게이트 필수, 이월 금지**. → TC-F4-N13/N15.

### [H-4] `GetOutgoingAtkMult` 누산기 초기값 0.0 → 전 공격 dmg=1 (CONFIRMED)
`Π(1 − Value_i)`를 ForEach로 짤 때 BP **float 로컬 변수 기본값 = 0.0**. 엔트리가 없으면(=F4 상시) 곱 누산기가 0.0 그대로 반환된다 → `Base = floor(40 × 0.0 × 1.0) = 0` → `dmg = 0 − 10 = −10` → **step7 min1이 이걸 1로 덮어써서 크래시도 에러도 없이 "모든 공격이 1 데미지"**가 된다.
**대책**: 누산기 초기값 **명시적으로 1.0**, 무엔트리 조기 return 1.0. → TC-F4-N12.

### [H-5] min1(step7)이 상위 버그를 은폐 — `dmg=1`은 자동 FAIL 신호 (CONFIRMED)
[[스탯_전투공식_v1]] §2 안전규칙상 **라이브 로스터에서 min1은 도달 불가**(`min Atk×1.0 = 32 > max Def 13`). 따라서 라이브 로스터 로그에 `dmg=1`이 1줄이라도 있으면 **그건 min1이 아니라 상위(step4 곱) 버그의 결과**다(H-3/H-4가 전부 여기로 수렴). 이 불변식을 TC로 못박아야 은폐가 깨진다. → TC-F4-N17.

### [H-6] min1 ↔ HEAL 음수 로그의 상호작용 — exec 병합 시 `dmg=-33`이 `1`이 된다 (CONFIRMED, Director 질의 답)
**두 스텝은 서로 독립이 아니다 — 단, "goto 9"를 exec 배선으로 지킬 때만 독립이다.** step2(HEAL)/step3(DMG_REDUCE)는 `LogDmg`에 각각 `-HealAmt`/`0`을 넣고 **step9로 직행**한다. 노드를 아끼려고 세 분기를 공용 꼬리(step7 `Max(1, floor(dmg))` → step8 → step9)로 합류시키면:
- HEAL: `Max(1, -33) = 1` → 로그 `dmg=1` + **HP가 33 회복이 아니라 1 감소**
- 막기: `Max(1, 0) = 1` → 로그 `dmg=1` + **자기 자신이 1 피해**
→ 부호 규약(회복 음수/막기 0)이 통째로 붕괴한다. F4 시점엔 도달 불가(스킬 F7)라 **런타임으로 못 잡는다 → 정적 그래프 TC가 유일 방어선**. → TC-F4-N16.

### [H-7] `SelectedTargets` 미클리어 + `Add` 누적 → 이전 턴 타겟을 함께 때린다 (CONFIRMED)
현행 `EnterAwaitCommand`는 `SelectedTarget = None`으로 초기화한다. 배열화하며 이 초기화를 **`Clear`로 옮기지 않고**, `NotifyUnitClicked`가 **`Set`이 아니라 `Add`**로 짜이면:
- turn1: 클릭 B1 → `[B1]` → ForEach 1회
- turn2: 클릭 B2 → `[B1, B2]` → **ForEach 2회 → B1이 자기 턴도 아닌데 또 맞는다**(BattleLog 2줄/턴)
→ 턴당 BattleLog 라인 수 = 1 불변식으로 검출. → TC-F4-N01/N02/N03.

### [H-8] DT 재임포트(S0 GUID 교체)의 잔여 위험 (PLAUSIBLE)
S0에서 `DT_Skills`를 delete 후 재임포트해 **애셋 GUID가 바뀌었다**. 현재 BattleManager가 DT_Skills를 참조조차 안 하므로 **끊길 하드참조가 없다**(= 지금은 무해). 남은 위험은 둘:
1. F4가 새로 꽂는 `GetDataTableRow(DT_Skills)`의 DataTable 리터럴 핀이 **리다이렉터/구 경로**를 물면 `found=false` → step1 조기 return → **전 공격 무피해**(그런데 크래시도 로그도 조용). 첫 배선 직후 `found=true`+`powerRate=1.0` 실증 필수.
2. **같은 절차(delete→import)를 `DT_JobStats`에 적용하면 즉시 파국**: `BP_BattleSpawnPoint.BeginPlay`가 이 DT를 하드참조 중 → 끊기면 `Hp/MaxHp/Atk/Def = 0` → `MaxHp=0`으로 SetHp 0나눗셈([[U단계_TC]] TC-U09) + `Def=0`으로 전 데미지 오염 + 8기 즉사. **F4는 DT_JobStats/DT_Motions를 건드리지 않는다**를 규칙으로 못박고 TC로 감시. → TC-F4-N08.

---

## ③ 적대적 검토 — MEDIUM

| # | 항목 | 내용 | 확신도 |
|---|---|---|---|
| M-1 | **쿨다운 저장소가 명세에 없다** | §8 step0/step9가 `GetSkillCooldown`/`SetSkillCooldown`을 호출하는데 [[상태이상_확정]] §15-2 신규멤버·§15-3 함수표 **어디에도 없다**(멤버 타입·소유·키 전부 미정). 또 §15-3 `InitBattle` 리셋 목록에 **쿨다운이 빠져 있다** → 재시작 시 쿨다운 잔류. 권고: 유닛 소유 `SkillCooldowns : Map<Integer,Integer>` + InitBattle Clear | CONFIRMED |
| M-2 | **쿨다운이 유닛별인지 전역인지 미정** | Manager 전역 Map(키=SkillId)으로 짜면 A1이 베기를 쓰면 **A2의 베기까지 잠긴다**(전사 2명 = A1·A2). §7-6 "유닛별 (SkillId→남은 쿨턴) 상태로 저장"이 근거지만 §15에는 반영 안 됨 | CONFIRMED |
| M-3 | **`DebugForceEffectChance` sentinel** | §12-2가 "비활성값이면 실제 EffectChance 사용"이라 했으나 **비활성값을 0.0으로 잡으면 TC-SE01(Chance=0 강제)과 구분 불가**. 0/1이 전부 유효 강제값이므로 **sentinel = −1.0**이어야 함 | CONFIRMED |
| M-4 | **F4 상태이상은 영원히 만료되지 않는다** | F4는 step8.5(부여)를 짓지만 `TickStatusesAtTurnEnd`(TE2)·`IsStunSkipActive`(TS4)는 **F5 소관**. 즉 F4에서 ON_HIT 스캐폴드를 굴리면 STUN/ATK_DOWN이 **그 PIE 세션 내내 잔류**. STUN은 소비처(TS4)가 없어 무해하나, **ATK_DOWN이 붙은 유닛으로 이후 데미지 TC를 돌리면 정답지가 어긋난다**(`40×0.75×1.0 = 30 − 10 = 20 ≠ 30`) → **TC 실행 순서 규칙 필수** | CONFIRMED |
| M-5 | **RowName 조회 강제** | [[plan]] L213: DataTable struct의 `.id` 필드는 **항상 0**, 진짜 키는 RowName. `GetDataTableRow(DT_Skills, SkillId)`는 **int → String → Name 변환**을 거쳐야 하고, `.id`로 찾으려 하면 전 행 매칭 실패 | CONFIRMED |
| M-6 | **StatusLog는 기존 파서에 안 잡힌다** | `extract_battle_log.py`의 `MARKER = "BattleLog|"` → **`StatusLog|` 라인은 추출물에 0줄**. 스크립트 수정이 아니라 **별도 grep 커맨드 추가**가 정답([[상태이상_확정]] §8-2가 "verifier 확인 1건"으로 예고) | CONFIRMED |
| M-7 | **`BattleState`(Byte 매직넘버) 미접촉** | F4의 TakeHit은 상태를 **절대 전이시키지 않는다**(F5 레이스 대책의 전제). 정적으로 `SetBattleState`/`EnterEnd`/`EnterTurnEnd`/`EnterTurnStart` 노드 0개를 확인해야 F5의 게이트 단일화가 유효 | CONFIRMED |

### F5 레이스 대책이 F4 때문에 무력화되는 경로 (Director 질의 답)

병렬 Sequence(then_0 = Delay0.25→TakeHit / then_1 = Delay0.75→WalkBack→Delay0.45→EnterTurnEnd)에서 **F5의 방어선은 단 하나 — "TakeHit은 플래그만 세우고, 상태 전이는 EnterTurnEnd 게이트에서만"**이다. F4가 이걸 깨는 방법은 정확히 3가지:

1. **TakeHit이 상태를 직접 전이**(`SetBattleState`/`EnterEnd` 호출) → then_1의 EnterTurnEnd가 그걸 되돌린다. → M-7 정적 TC로 차단.
2. **TakeHit이 비동기가 된다**(내부 latent, 또는 BLOCKER-3의 latent 흡수) → 플래그 확정이 then_1의 게이트 평가보다 **늦어질 수 있다** → 게이트가 False를 읽고 다음 턴이 열린다. 현재 타이밍 마진은 **`t≈0.25`(플래그) vs `t≈2.0+`(게이트) = 약 1.7초**로 넉넉하나, **연출 호출을 플래그 세팅보다 앞에 두면(§8 step9 서술 순서 그대로) 0.45초가 잠식**된다. → **step9 내 순서를 "쿨다운 → HP/플래그 → 로그 → (마지막에) 연출 호출"로 고정**할 것. TC-F4-N21이 로그 타임스탬프 델타로 실측.
3. **then_0에 조기 return이 생겨 플래그가 아예 안 써진다**(step0 쿨다운 가드·step1 found=false) → F5에서 "죽었는데 bBattleOver 미세팅"이 아니라 "타격 자체가 없었음"이라 무해. **단 로그가 0줄이므로 verifier가 "턴이 사라졌다"고 오판하지 않도록 경고 라인 1줄은 반드시 남길 것**.

### §8 스텝을 BP 노드로 옮길 때의 함정 (Director 질의 답)

| 축 | 함정 | 대응 TC |
|---|---|---|
| 중간 floor | step4는 **단일 floor**. `floor(Atk×Mult)` 후 다시 `×PR`하면 `floor(40×1.0)=40 → ×1.3 = 52`(우연히 일치)지만 ATK_DOWN 시 `floor(40×0.75)=30 → ×1.3 = 39 → 29` ≠ 정답 `floor(40×0.75×1.3)=39 → 29`. 알파 값에선 우연히 겹치나 **F8 BerserkMult 결선 시 어긋난다** | N13 |
| 정수 절삭 | `int × float`가 int Multiply로 배선되면 PR이 절삭(H-3). step6 `dmg × (1 − 0.5)`도 동일 — `0.5 → int 0` → **막기가 피해를 반감이 아니라 0으로** 만들고 min1이 1로 덮는다 | N13/N15 |
| 정수 나눗셈 | 데미지 경로엔 나눗셈 없음. **단 `SetHp`의 `Hp/MaxHp`가 첫 실구동**([[U단계_TC]] TC-U09는 주입 테스트였다) → `60/90`이 int÷int면 **0.0** | N10 |
| 0 나눗셈 | `MaxHp = 0`(DT 끊김, H-8-2) 시 `Hp/MaxHp` → NaN | N08/N10 |
| Byte 오버플로 | Byte는 `BattleState`(0~5)뿐 — **F4 데미지 경로에 Byte 없음**. `Hp/Atk/Def`는 int32라 오버플로 무관(최대 132). **검토 결과 해당 없음** | — |
| floor vs truncate | BP의 암묵 `Conv_DoubleToInt`는 **truncate**(0방향)다. step4/step7 값은 항상 양수라 floor와 결과 동일 → **무해**. 단 명시적 `Floor` 노드 사용을 권고(F8 음수 진입 시 대비) | N13 |

---

## ④ TC 표 — A. 승계(plan §F4 TC-F4-01~08) · 판정방법 구체화

> **판정도구 약칭**: **LOG**=엔진 로그 파싱(`D:\unreal\projectTP\Saved\Logs\projectTP.log` grep, 또는 MCP `GetLogEntries(category="LogBlueprintUserMessages", pattern="BattleLog\\|")`) / **SCF**=스캐폴드 직접호출 후 LOG / **MOCK**=mock 값 주입 후 LOG / **GRAPH**=MCP 정적 그래프 조회(`find_nodes`·`get_connected_subgraph`·`get_node_infos` — `read_graph_dsl`은 빈 문자열 반환 사례 있어 백업용) / **PIE**=PIE 인스턴스 프로퍼티 재조회(`ObjectTools.get_properties`, `UEDPIE_0` 월드) / **DT**=`DataTableTools.get_rows` / **CSV**=`data/*.csv` 직접 대조 / **CMP**=컴파일 에러 0(`warnings_as_errors=true`) / **오너**=오너 육안(PIE).
> **스캐폴드 규약**(함정⑥): 유닛은 반드시 `GetTurnQueue()`→`Array Get(사본)`으로 획득(리터럴 오브젝트 레퍼런스 금지 — PIE 그림자 액터).
> **배정표**(F0③): A1·A2·B1·B2 = 전사2성(Hp90/Atk40/Def10) · A3·A4·B3·B4 = 마법사2성(Hp80/Atk42/Def6).

| ID | 구분 | 조건 → 기대결과 (재현 시나리오) | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-01** | 기능 | **전사 basic**: SCF `TakeHit(A1, B1, 31000000)` → `dmg=30`,`hp=60`. SCF `TakeHit(A1, B3, 31000000)` → `dmg=34`,`hp=46` | SCF — `grep -oE "BattleLog\|.*attacker=SpawnPoint_Party_A1\|target=SpawnPoint_Enemy_B1\|action=31000000\|dmg=30\|hp=60"` 1줄 이상 | 대기 |
| **TC-F4-02** | 기능 | **마법사 basic**: SCF `TakeHit(A3, B1, 31000000)` → `dmg=32`,`hp=58`. SCF `TakeHit(A3, B3, 31000000)` → `dmg=36`,`hp=44` | SCF — 상동 grep(attacker=…A3) | 대기 |
| **TC-F4-03**★ | 기능 | **베기**(게이트 필수·이월 금지): SCF `TakeHit(A1, B1, 31001000)` → `dmg=42`,`hp=48` / `TakeHit(A1, B3, …)` → `dmg=46`,`hp=34`. **`dmg=30`이면 H-3(int절삭), `dmg=41`이면 H-2(single precision)** — 값으로 원인을 가른다 | SCF — `grep -oE "action=31001000\|dmg=[0-9]+"` 후 42/46 대조. **effect/effectRoll 필드는 이 TC의 판정 대상 아님**(25% 롤이라 비결정) | 대기 |
| **TC-F4-04** | 기능 | 파볼61/65·치유+33·막기0 셀 — F4 스켈레톤 도달불가(스킬 UI는 F7) | — | **이월(F7)** |
| **TC-F4-05** | 기능 | **min1 보정**: MOCK으로 B1.Def=50 주입(Base 40 < Def) → `dmg=1`,`hp=89`. **검증 후 Def=10 복원 실증**(상태 누수 금지) | MOCK(PIE `set_properties(Def=50)`) + LOG + 복원 후 PIE 재조회 `Def==10` | 대기 |
| **TC-F4-06** | 기능 | **로그 스키마**: 라인이 정확히 `BattleLog\|turn=N\|attacker=S\|target=S\|action=<정수>\|dmg=<정수>\|hp=<정수>` 6필드. `ATTACK1` 리터럴 **0건**. `action`은 숫자 SkillId | LOG — `grep -c "action=ATTACK1"` = **0** / `grep -oE "BattleLog\|[^ ]+"` 1줄을 `\|` split해 key 6개·순서 대조 | 대기 |
| **TC-F4-07** | 기능 | **HP 적용**: 만피 대상 첫 타격 라인에서 `hp == MaxHp − dmg` 정확, `dmg` 양수. 오버킬 시 `hp=0`(음수 미표시) | LOG — 라인의 dmg/hp를 파싱해 산술 대조 | 대기 |
| **TC-F4-08** | 기능 | **쿨다운 가드**: SCF `TakeHit(A1,B1,31001000)` 2연속 호출 → BattleLog `action=31001000` 라인 **정확히 1줄**, B1.Hp = 90−42 = **48**(2회 차감 아님). 2번째는 step0 조기 return | SCF + LOG(라인수) + PIE(`B1.Hp==48`) | 대기 |

---

## ⑤ TC 표 — B. 상태이상+AoE 통합 TC의 **F4 실행분** ([[plan]] §"F4/F5/F7 확장" 33개 중)

| ID | 구분 | 조건 → 기대결과 (F4 실행판으로 구체화) | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-V1** | 기능 | `EffectType∈{STUN,ATK_DOWN}` ⇒ `PowerRate>0` — 베기 1.3·파볼 1.7 | CSV(`data/skills.csv`) + **DT 교차**(라이브 `DT_Skills`도 동일값인지 — CSV만 보면 S0 재임포트 누락을 못 잡는다) | 대기 |
| **TC-V2** | 기능 | `Kind=HEAL` ⇒ `EffectType∈{NONE,HEAL}` — 치유행 HEAL | CSV + DT | 대기 |
| **TC-V3** | 기능 | `ATK_DOWN` ⇒ `EffectDurationTurns ≥ 1` — 파볼 dur=2 | CSV + DT | 대기 |
| **TC-V4** | 기능 | `ON_HIT` ⇒ `EffectChance ∈ (0,1]` — 베기 0.25·파볼 0.35 | CSV + DT | 대기 |
| **TC-V5** | 기능 | `Target` 토큰 ∈ 발급목록(ENEMY1/ALLY1/SELF 3종만 사용, ENEMY_ALL·ALLY_ALL 데이터 0건) | CSV + DT | 대기 |
| **TC-V6** | 기능 | `EffectValue` 의미=**감소율** — STUN=0 / ATK_DOWN=**0.25**(0.75 아님) / DMG_REDUCE=0.5 | CSV + DT | 대기 |
| **TC-SE01** | 기능 | **Chance=0 회귀**: `DebugForceEffectChance=0` 강제 → v1 §5-1 전 셀 무변경(TC-F4-01~03 재실행 시 동일값) + StatusLog APPLY **0줄** | SCF + LOG(BattleLog 값 + StatusLog 부재) | 대기 |
| **TC-SE05** | 기능 | **킬링블로우 롤 생략**: MOCK B1.Hp=30 → SCF `TakeHit(A1,B1,31001000)`(dmg42 > 30) → `hp=0` + `effectRoll=-1` + `effectApplied=false` + **B1.ActiveStatuses 길이=0**(시체 상태 Clear) | SCF+MOCK + LOG(effect 필드) + PIE(ActiveStatuses length) | 대기 |
| **TC-QA01** | 기능 | **SelectedTargets 배열화 무회귀**: 길이1 경로로 TC-F4-01~08 전부 PASS + 라이브 1턴 정상 완주 | LOG(승계 TC 재사용) | 대기 |
| **TC-QA02** | 기능 | **ResolveTargetPool 단일 소스**: ENEMY1 풀이 **하이라이트·클릭유효·커밋** 3소비처에서 동일(F4엔 bEnabled 슬롯이 없어 4번째는 F7 이월) + 반환 순서 = TurnQueue 오름차순 | GRAPH(3소비처가 전부 ResolveTargetPool 호출 노드를 경유) + PIE(반환 배열 순서) | 대기 |
| **TC-QA03** | 기능 | **예약 토큰 폴백**: MOCK으로 `ResolveTargetPool("ENEMY_ALL", A1)` 직접 호출 → 빈 배열 + 경고 로그 1줄 + **크래시/Accessed None 0** | MOCK(SCF) + LOG | 대기 |
| **TC-QA04** | 기능 | **死코드 0**: Manager 그래프에 ALL 분기 실행부·AwaitTarget ALL 모드 플래그 **부재** | GRAPH | 대기 |
| **TC-QA05** | 기능 | **step4 곱 순서·단일 floor**: 노드 체인이 `Atk → ×OutgoingAtkMult → ×PowerRate`(BerserkMult 자리는 F8 공백) + **Floor 노드 정확히 1개**, 중간 Floor/Truncate **0개** | GRAPH(step4 서브그래프 노드 열거) | 대기 |
| **TC-QA09** | 기능 | **킬링블로우 표기 구분**: TC-SE05 라인이 `hp=0 ∧ effectRoll=-1 ∧ applied=false` → "사망에 의한 미적용". 반면 생존 대상 굴림 실패 라인은 `effectRoll∈[0,1) ∧ applied=false` | LOG(두 라인 대조) | 대기 |
| **TC-QA10** | 기능 | **F_ActiveStatus 실증**: 유닛 신규 멤버 `ActiveStatuses`가 `F_ActiveStatus[]`이고 필드 = `statusToken:String`/`value:Float`/`remainingTurns:Integer` | MCP `list_properties`(BP_BattleSpawnPoint) | 대기 |
| **TC-QA11** | 기능 | **CSV 게이트 일괄**: 라이브 `skills.csv` 5행이 V1~V6 전 룰 통과(TC-V1~V6 합산 PASS) | CSV + DT | 대기 |
| **TC-QA15** | 기능 | **InitBattle 리셋**: 상태·쿨다운 보유 중 `InitBattle` 재호출 → 전 유닛 `ActiveStatuses` 길이 0 + `SelectedTargets` 길이 0 + **쿨다운 전량 0**(M-1 반영) | SCF + PIE(8기 + Manager 재조회) | 대기 |

---

## ⑥ TC 표 — C. **신규 예외상황 TC**(qa-critic 신규 27 + 비주얼 4 = 31)

### C-1. 회귀·배선 (SelectedTarget → SelectedTargets)

| ID | 구분 | 조건 → 기대결과 (재현 시나리오) | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-N01** | 기능 | **잔존 노드 0**: 전 그래프에서 구 `SelectedTarget`(단수) Get/Set 노드 **0개**. Director 실측상 최소 3곳(`NotifyUnitClicked` 세팅 / `EnterExecuting` then_0 `IsValid`+`TakeHit` / `EnterAwaitCommand` None 초기화) + **`EnterExecuting` 진입 로그의 `GetSelectedTarget→GetDisplayName`**(4번째, [[전투로그]] §구현) 전부 재배선. 컴파일 0 | GRAPH(변수명 검색) + CMP | 대기 |
| **TC-F4-N02** | 기능 | **누적 금지(H-7)**: 라이브 3턴 연속 진행 → 매 턴 `SelectedTargets.Length == 1` + **턴당 BattleLog 정확히 1줄**(2줄이면 전 턴 타겟 중복 타격) | PIE(턴마다 Manager 재조회) + LOG(턴별 라인수 카운트) | 대기 |
| **TC-F4-N03** | 기능 | **초기화 이설**: `EnterAwaitCommand`의 구 `SelectedTarget=None`이 **`SelectedTargets` Clear(길이 0)** 로 대체됨. AwaitCommand 진입 시점 PIE 조회 길이 0 | GRAPH + PIE | 대기 |
| **TC-F4-N04** | 기능 | **빈 풀/None 가드**: MOCK으로 `SelectedTargets`를 빈 배열로 만든 뒤 `EnterExecuting` 진입 → **`Accessed None` 경고 0건**, `Array Get(0) out of bounds` 0건, 경고 로그 1줄 후 정상 턴 종료 | MOCK(SCF) + LOG(`grep -c "Accessed None"` = 0) | 대기 |

### C-2. 함수·이름·그래프 종류

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-N05**★ | 기능 | **이름 충돌·재귀(BLOCKER-5)**: Manager의 연출 호출 노드의 **Target 핀 = 유닛 오브젝트 레퍼런스(≠ self)**. PIE 1턴 진행 시 스택 오버플로/무한루프/행(hang) 0. (개명 채택 시: Manager 그래프에 동명 노드가 애초에 없음을 확인) | GRAPH(호출 노드 Target 핀 소스) + PIE(1턴 완주) | 대기 |
| **TC-F4-N06** | 기능 | **DT 조회 실패**: MOCK `TakeHit(A1, B1, 99999999)` → `found=false` 경로 → **경고 로그 1줄 + return**, B1.Hp 무변화(90), BattleLog 라인 0줄, 크래시 0 | MOCK(SCF) + LOG + PIE(Hp==90) | 대기 |
| **TC-F4-N07** | 기능 | **RowName 조회(M-5)**: `GetDataTableRow(DT_Skills, …)`의 RowName 입력이 **SkillId(int)→String→Name 변환 체인**을 경유(`.id` 필드 미사용 — 항상 0). `31000000` 조회 시 `found=true` ∧ `powerRate=1.0` | GRAPH(변환 노드 체인) + SCF+LOG(정상 dmg=30) | 대기 |
| **TC-F4-N20**★ | 기능 | **F5 레이스 보호(M-7)**: `Manager.TakeHit` 서브그래프에 `SetBattleState`·`EnterEnd`·`EnterTurnEnd`·`EnterTurnStart` 노드 **0개** + **latent 노드(Delay/RetriggerableDelay/Timeline) 0개**. RetriggerableDelay 체인은 **BP_BattleSpawnPoint 그래프에만** 존재(BLOCKER-4) | GRAPH(2 BP 서브그래프 열거) | 대기 |
| **TC-F4-N21**★ | 기능 | **TakeHit 동기성(BLOCKER-3)**: 1턴 로그 타임스탬프에서 `BattleLog`(then_0, 예상 t≈0.25s) 와 다음 턴 `BattleLog`/TurnEnd 사이 델타 확인 → **BattleLog가 EnterTurnEnd보다 확실히 먼저**(마진 ≥1.0s). 연출 호출을 step9 **맨 마지막**에 두었는지 정적 확인 | LOG(UE 타임스탬프 델타) + GRAPH(step9 노드 순서) | 대기 |

### C-3. 데이터·애셋(S0 GUID 교체 여파)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-N08**★ | 기능 | **DT 참조 무결(H-8)**: (a) `BP_BattleManager`·`BP_BattleSpawnPoint` **컴파일 에러 0**(끊긴 하드참조·null DT 핀 없음) (b) `DT_Skills` 라이브 5행 + `31001000` = STUN/dur1/chance0.25 (c) **`DT_JobStats`는 F4에서 재임포트 금지** — PIE 8기 스탯이 여전히 90/40/10·80/42/6 (d) `/Game/Data/`에 ObjectRedirector 0개 | CMP + DT + PIE(8기 스탯) + MCP 애셋 조회 | 대기 |

### C-4. 산술·정밀도(§8 코어)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-N12**★ | 기능 | **누산기 1.0(H-4)**: `GetOutgoingAtkMult`가 **빈 `ActiveStatuses`에서 1.0 반환**(0.0 아님). 정적으로 곱 누산기 로컬의 **기본값=1.0** 확인 + 런타임 `dmg=30`(1이 아님) | GRAPH(로컬 변수 default) + PIE(함수 반환값) + LOG | 대기 |
| **TC-F4-N13**★ | 기능 | **곱 순서·타입·단일 floor(H-3/TC-QA05 자매)**: step4 곱 노드가 전부 **실수 Multiply**(정수 Multiply 0개), Floor 1개, 중간 Floor/Truncate 0개. step6 `dmg × (1−BlockValue)`도 **실수 Multiply**(정수면 0.5→0 → 막기가 피해를 0으로) | GRAPH(노드 타입 열거) | 대기 |
| **TC-F4-N14**★ | 기능 | **실수 정밀도(H-2)**: `F_SkillsRow.powerRate`가 double(Real)인지 확인 + 데미지 체인 로컬에 float32 없음. **베기 dmg가 42면 PASS, 41이면 single-precision 확정**(로직 버그 아님 — 오진 방지) | MCP `list_properties`(정밀도) + GRAPH(로컬 타입) + LOG(TC-F4-03 값) | 대기 |
| **TC-F4-N15** | 기능 | **암묵 절삭 없음**: `Atk`(int)가 실수로 승격되는 지점에 `Conv_IntToFloat/Double` 존재 + PowerRate/Mult가 **int 핀에 물리지 않음**(물리면 1.3→1) | GRAPH(핀 타입 대조) | 대기 |
| **TC-F4-N16**★ | 기능 | **HEAL/막기 goto9 exec 분리(H-6)**: step2(HEAL)·step3(DMG_REDUCE) 분기의 exec가 **step7 `Max(1,·)` 노드를 경유하지 않고 step9로 직행**. 경유하면 `dmg=-33 → 1`, `dmg=0 → 1`로 부호규약 붕괴. **F4엔 도달 불가라 정적 검증이 유일 방어선** | GRAPH(exec 경로 추적) | 대기 |
| **TC-F4-N17**★ | 기능 | **min1 은폐 불변식(H-5)**: 라이브 로스터 전 BattleLog 라인에서 **`dmg=1` 0건**(정답지상 도달 불가 — mock TC-F4-05 라인 제외). 1건이라도 있으면 상위 step4 버그 | LOG — `grep -c "\|dmg=1\|"` = 0 | 대기 |
| **TC-F4-N22**★ | 기능 | **FormatText 그룹핑(H-1)**: 로그에 **콤마 0개** — `grep -c "action=31,000,000"` = 0, `grep -cE "action=[0-9]{8}(\||$)"` ≥ 1 | LOG | 대기 |

### C-5. HP 적용·표시

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-N09**★ | 기능 | **HP 이중 차감 금지(BLOCKER-1)**: 1타 후 **세 값이 정확히 일치** — 로그 `hp=60` == PIE `B1.Hp`==60 == `MaxHp − dmg`==60. 30이면 이중 차감 | LOG + PIE(유닛 Hp) 교차 | 대기 |
| **TC-F4-N10**★ | 기능 | **HP 바 갱신·정수 나눗셈**: 1타 후 B1의 `WBP_UnitFrame` PIE 인스턴스에서 `Bar_Hp.Percent ≈ 0.667`(±0.01) + `Txt_HpValue == "60/90"`. **Percent가 0.0이면 int÷int 회귀**([[U단계_TC]] TC-U09의 첫 실구동 재검) | PIE(위젯 인스턴스 프로퍼티) | 대기 |
| **TC-F4-N11** | 기능 | **SetHp 호출 존재·가드**: 유닛 그래프의 피격 경로에 `CachedUnitFrame.SetHp(Hp, MaxHp)` 노드 존재 + **`IsValid(CachedUnitFrame)` 가드**. 미호출이면 계산은 맞는데 화면만 안 바뀐다 | GRAPH | 대기 |
| **TC-F4-N23** | 기능 | **사망 후 F4 거동(오버킬)**: Hp=0 유닛을 재타격(SCF) → **크래시 0**, `hp=0`(음수 아님), `dmg`는 정상값 기록. F4엔 사망 스킵·타겟 제외·승패가 없으므로 **"좀비 전투"가 예상 동작**임을 확인(F5에서 해소) | SCF + LOG + PIE | 대기 |

### C-6. 쿨다운·상태·검증훅

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-N18** | 기능 | **쿨다운은 유닛별(M-2)**: SCF `TakeHit(A1,B1,31001000)` 성공 → 이어서 SCF `TakeHit(A2,B1,31001000)`(**다른 전사**) → **A2의 베기는 성공**(dmg=42 라인 1줄 추가). 전역 Map이면 A2가 조기 return되어 라인이 안 나온다 | SCF + LOG(라인 2줄) | 대기 |
| **TC-F4-N19** | 기능 | **쿨다운 저장소 실재(M-1)**: `GetSkillCooldown`/`SetSkillCooldown`의 백킹 멤버가 실재(유닛 소유, `Map<Integer,Integer>` 등) + `InitBattle`에서 Clear됨 | GRAPH + MCP `list_properties` | 대기 |
| **TC-F4-N24** | 기능 | **DebugForceEffectChance sentinel(M-3)**: 비활성 sentinel이 **0.0이 아님**(−1 등) — `=0` 강제와 "비활성"이 구분 가능. `=0` 강제 시 APPLY 0줄, `=1` 강제 시 APPLY 1줄 | GRAPH(기본값) + SCF+LOG(0/1 강제 각 1회) | 대기 |
| **TC-F4-N25** | 기능 | **상태 오염·실행순서(M-4)**: F4엔 TE2(만료 차감)가 없어 ON_HIT 부여 상태가 **PIE 세션 내내 잔류**. → **verifier 실행 규칙**: ① L0/데미지 TC(01·02·03·05~08) 먼저 ② ON_HIT 스캐폴드(SE05·QA09) 마지막 ③ 그 후 데미지 TC 재실행 시 **PIE 재시작 필수**. 규칙 위반 시 `40×0.75=30−10=20`(≠30) 위양성 | LOG(순서 준수 기록) + PIE(ActiveStatuses 잔류 확인) | 대기 |
| **TC-F4-N26** | 기능 | **StatusLog 별도 수집(M-6)**: `extract_battle_log.py`(MARKER=`BattleLog\|`) 산출물에 StatusLog **0줄**임을 확인하고, **별도 커맨드**로 수집 — `grep -o "StatusLog\|.*" projectTP.log`. 스크립트 수정 금지 | LOG(2종 커맨드) | 대기 |
| **TC-F4-N27** | 기능 | **무회귀 기반선**: F4 전후 8기 Location/FaceLeft/Sprite **diff=0**([[F3_사전스냅샷]] 대조) + 2 BP 컴파일 에러 0 + 걸음/카메라 로그(`WalkArrive`·`CamCut`) 기존과 동일 | PIE(트랜스폼 diff) + CMP + LOG(회귀) | 대기 |

### C-7. 비주얼 TC (오너 육안 — **게이트 불차단**)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F4-V1**★ | 비주얼 | **공격하면 HP가 실제로 깎인다** — 첫 진짜 전투감(plan `[F4][오너]` 승계) | 오너 라이브(PIE) | 대기 |
| **TC-F4-V2** | 비주얼 | 피격 유닛이 HURT(Row12) 재생 후 **0.45초 뒤 idle 복귀**(굳거나 계속 움찔하지 않음) | 오너 라이브(PIE) | 대기 |
| **TC-F4-V3** | 비주얼 | 히트 VFX가 **매 타격마다** 발생(HP 갱신이 VFX를 삼키지 않음) | 오너 라이브(PIE) | 대기 |
| **TC-F4-V4** | 비주얼 | **[사전 고지 — 버그 아님]** HP가 0이 된 유닛이 **쓰러지지 않고 계속 서서 행동**하고, 적 전멸 후에도 전투가 끝나지 않는다(F4엔 사망 연출·턴 스킵·승패가 없음 — **F5 소관**). 오너는 이걸 결함으로 보고하지 말 것 | 오너 라이브(PIE, 고지 확인) | 대기 |

> **오너 라이브 안내 초안(Director용)**: "Attack 버튼 → 적 1기 클릭 → **머리 위 HP 바가 줄어드는지** 보세요. 전사 상대 30, 마법사 상대 34가 정상입니다. **HP 0이 돼도 안 쓰러지고 계속 싸우는 건 F4 예정 동작**입니다(F5에서 사망·승패 붙임). 적 4기를 다 죽이면 진행이 막힐 수 있으니 **1~2기만 때려보고 멈춰주세요.**"

---

## ⑦ 이월 TC

| TC | 사유 | 검증 예정 |
|---|---|---|
| TC-F4-04 (파볼·치유·막기 셀) | 스킬 UI가 F7 | F7 |
| TC-QA02의 **bEnabled 소비처** | F4엔 스킬 슬롯이 없음(Attack 1버튼) | F7 |
| TC-SE02/03/06/07 · TC-QA06/07/08/12/13/14 | TS4(스킵)·TE2(만료 차감)가 F5 소관 | F5/F7 |

---

## ⑧ 커버리지 근거 (검토한 축 — 빈손 OK 금지)

- **경계값**: Def≥Base(min1, N17/F4-05) · Hp=0 재타격(N23) · 만피 클램프(F7 이월) · PowerRate 1.0/1.3/1.7의 부동소수 경계(N14) · `EffectChance=0`(기본공격, SE01) · 빈 배열(N04)
- **정수/실수**: int×float 절삭(N13/N15) · 정수 나눗셈 `Hp/MaxHp`(N10) · 0 나눗셈 `MaxHp=0`(N08) · 단일 floor vs 중간 floor(N13) · float32 vs double(N14) · **Byte 오버플로 = 해당 없음**(BattleState만 Byte, 데미지 경로 미접촉 — 검토 후 통과)
- **동시성/순서**: then_0(TakeHit) ‖ then_1(EnterTurnEnd) 병렬(N20/N21) · latent 흡수(함정⑨, BLOCKER-3) · 연출 호출 위치가 플래그 확정을 지연시키는 경로(N21) · TC 실행 순서 의존(N25)
- **null/참조**: 빈 타겟 풀 → Accessed None(N04) · DT found=false(N06) · DT GUID 교체 후 dangling(N08) · `CachedUnitFrame` null(N11)
- **상태 누수**: mock Def 복원(F4-05) · ActiveStatuses 영구 잔류(N25) · 쿨다운 InitBattle 미리셋(N19/QA15) · SelectedTargets 누적(N02)
- **이중 소스/이중 쓰기**: HP writer 2곳(BLOCKER-1/N09) · 로그 방출 지점 2곳(BLOCKER-2/N01) · 이름 충돌(BLOCKER-5/N05)
- **명세-구현 불일치**: plan §8 step8(Manager가 HP 쓰기) vs Director 지시(유닛이 HP 쓰기) · [[전투로그]](EnterExecuting 로그) vs plan §8 step9(TakeHit 로그) · plan §4-1(Manager 멤버) vs §15-4(유닛 소유) · §8 step0/9(쿨다운 함수) vs §15(멤버·함수 목록에 부재)
- **무증상 실패(silent)**: min1이 step4 버그를 1로 은폐(N17) · PR 절삭 시 **기본공격만 정답**(N13, TC-F4-01/02가 PASS하는 위양성) · 로그는 맞는데 화면/실HP가 틀림(N09/N10) · `found=false` 조용한 무피해(N06)

---

## 관련 문서
[[plan]] · [[상태이상_확정]] · [[스탯_전투공식_v1]] · [[광폭화_재검증]] · [[전투로그]] · [[U단계_TC]] · [[U단계_HP게이지_UMG_실장]] · [[언리얼_MCP_실전노하우]] · [[개발_워크플로우]]
