---
type: qa
project: projectTP
feature: 전투완성
stage: F5
status: TC 확정 — 개발 착수 전 BLOCKER 5건 Director 판정 필요
updated: 2026-07-15
---

# F5(사망·승패 / End 상태) — TC 설계 + 적대적 검토

> 대상: [[plan]] §F5(L345~418) · [[상태이상_확정]] §5(TS1~TS6 / TE1~TE4)·§8-2·§13 · [[F4_중단_인수인계]](F4 실적 = 본 문서의 전제) · [[F4_TC]](승계 규약) · [[E2_상태머신]](현행 EnterTurnStart/TurnEnd) · [[전투로그]](TurnCounter 삽입 위치) · [[W2_Executing개편]](Sequence 병렬 실측) · [[광폭화_재검증]] §2 · [[언리얼_MCP_실전노하우]] L130·함정⑥⑧⑨⑮⑯⑰
> **BP 조회 금지 상태에서 작성**(에디터 손상) — 전부 문서 기반. "실측 필요" 표기 항목은 착수 첫 액션으로 GRAPH 확인할 것.
> **기능 TC = verifier 게이트(진행 차단) / 비주얼 TC = 오너 육안(진행 불차단)**.
> TC 실행 = verifier, 게이트 판정 = Director. **본 문서는 검출·설계만 — BP/데이터 수정 없음.**
#projectTP/전투완성

---

## 0. 요약

| 구분 | 개수 |
|---|---|
| 기능 TC (verifier 게이트) | **48** — 승계 12 + 상태이상 통합 F5분 11(TC-QA15는 N18로 통합 실행) + **신규 예외 26** |
| 비주얼 TC (오너 육안, 불차단) | **6** |
| 이월 TC | 4 |
| **BLOCKER**(착수 전 결정 필수) | **5** |
| HIGH | 8 |
| MEDIUM | 10 |

**BLOCKER 한 줄 요약**
1. `bBattleOver` 생존수 카운트 대상이 **반대로** 명세됨 → 문면대로 짓면 **전투가 영원히 안 끝난다**
2. `BattleFinished` payload(전멸팀) ↔ `WinningTeam`(승자)가 **정반대 값** → 직결하면 승패가 뒤집힘
3. `InitBattle` 리셋 목록에 **Hp·bFreeze·RowIndex·ClickBox가 없다** → 재시작 시 전원 "Hp=0 누운 시체"로 부활 → TC-F5-11이 약속한 "재시작 가능"이 성립 안 함
4. **TS3(쿨다운 스윕·막기 해제)는 "기존"이 아니라 미구현** — 3문서가 3개 단계에 배정. TS3 없이는 F5 설계의 핵심 근거("TS3가 TS4보다 앞")가 검증 불가
5. `bFreeze=1` **세팅 시점** 미정 — DYING과 동시에 세팅하면 **사망 모션이 통째로 스킵**(마지막 프레임으로 즉시 팝)

---

## ① 적대적 검토 — BLOCKER (착수 전 Director 결정 필수)

> 5건 전부 "코딩 실수"가 아니라 **명세 자체의 모순·공백**이다. 지금 1줄 결정하면 비용 0, F5 구현 후 발견하면 그래프 수술이다.

### [BLOCKER-1] `bBattleOver` 카운트 대상이 반대 — 전투가 영원히 끝나지 않는다 (CONFIRMED)

**모순**: [[plan]] L382 원문 —
> `Target.bAlive=false` 직후 → **상대팀(Target과 반대 bIsParty) 생존수 카운트** → 0이면 `SetbBattleOver(true)` + `SetWinningTeam(Attacker.bIsParty)`

전투 종료 조건은 **죽은 Target 자신의 팀**에 생존자가 0인 것이다. 그런데 명세가 지시하는 집합은 `bIsParty != Target.bIsParty` = **공격자 팀**이다. 공격자는 방금 자기 턴에 행동했으므로 **반드시 살아 있다** → 카운트는 항상 ≥1 → **`bBattleOver`는 절대 true가 되지 않는다.**

**재현 시나리오**:
1. B1~B3 사망 상태에서 A1이 B4(마지막 적)를 킬 → `Target=B4(bIsParty=false)`
2. 명세대로 `bIsParty != false` = 파티팀(A1~A4) 생존수 카운트 = **4** ≠ 0
3. `bBattleOver=false` → `EnterTurnEnd` TE4 Branch(False) → Delay(0.35) → 다음 턴 개시
4. 적 4기 전원 시체인데 전투 계속 → 다음 파티 유닛 턴에서 `ResolveTargetPool("ENEMY1")` = **빈 배열** → `EnterAwaitTarget`에 하이라이트·클릭 가능 대상 0 → **입력 대기 무한 = 소프트락**(F5엔 슬롯 bEnabled 게이팅이 없다 — 그건 F7)

**확신도**: CONFIRMED(문면 그대로 구현 시 100% 재현). `WinningTeam = Attacker.bIsParty`(승자)와도 자기모순 — 승자를 기록하면서 승리 조건은 승자 팀의 전멸을 본다.

**요구 결정(권고)**: 카운트 집합을 **`u.bIsParty == Target.bIsParty ∧ u.bAlive`** 로 정정. 0이면 `bBattleOver=true`, `WinningTeam = Attacker.bIsParty`(= `NOT Target.bIsParty`). → TC-F5-N11.

---

### [BLOCKER-2] `BattleFinished` payload와 `WinningTeam`이 정반대 — 그대로 배선하면 승패가 뒤집힌다 (CONFIRMED 모순)

**모순**: 같은 plan 안의 두 문장이 정반대 bool을 요구한다.
- §5-2(L382): `SetWinningTeam(Attacker.bIsParty)` → **승자**의 bIsParty
- §5-4(L391): "`BattleFinished` 이벤트 디스패처 방출, payload = **전멸한 파티의 `bIsParty`**" → **패자**의 bIsParty

두 값은 항상 서로의 `NOT`이다. 엔지니어가 `BattleFinished(WinningTeam)`으로 직결하는 것이 가장 자연스러운 배선인데, 그러면 §5-4 계약(payload=전멸팀)을 위반한다. **A1엔 이 디스패처의 소비자가 없어 런타임 증상이 0** → A6(Result 화면)에서 "패배를 승리로 표시"하는 형태로 터진다.

**요구 결정(권고)**: payload 의미를 **승자(`WinningTeam`)** 로 통일하고 §5-4 문구를 정정. (디스패처 이름이 `BattleFinished`이고 A6가 알고 싶은 것은 "누가 이겼나"다.) 패자 유지 시엔 `Not(WinningTeam)`을 **명시 노드로** 배선하고 그 사실을 plan에 못박을 것. → TC-F5-N20.

---

### [BLOCKER-3] `InitBattle` 리셋 목록이 불완전 — 재시작하면 전원 "Hp=0 누운 시체"로 부활한다 (CONFIRMED)

**공백**: Director F5 지시 항목7 + [[상태이상_확정]] §15-3의 리셋 목록 =
`ActiveStatuses` Clear · `SkillCooldowns` Clear · `SelectedTargets` Clear · `bAlive=true` · `bBattleOver=false` — **5개뿐**.

**빠진 것(F5가 새로 만드는 상태들)**:

| 빠진 리셋 | 안 하면 | 근거 |
|---|---|---|
| `Hp = MaxHp` | **Hp는 `BeginPlay`에서만 DT_JobStats로 로드된다**(F3) — `InitBattle`은 Hp를 건드리지 않는다 → 부활한 유닛 전원 `Hp=0` | [[plan]] §F3-2 |
| `bFreeze = 0` | 시체가 DYING 마지막 프레임에 **얼어붙은 채 부활** — 살아서 행동하는데 누워 있다 | F5-3, S1 |
| `RowIndex=0 / FrameCount=6 / TimeOffset=0` | 상동(스프라이트가 IDLE로 안 돌아옴) | motions.csv Row0 |
| `ClickBox` 콜리전 = QueryOnly | 사망 시 NoCollision으로 바꿨으므로 **부활해도 영원히 클릭 불가**(타겟 지정 불능) | F5 지시 항목6 |
| `bBlockActive=false / BlockValue=0` | 막기 잔류(F7에서 발현) | F4 신규 변수 |
| `CachedUnitFrame.SetHp(MaxHp, MaxHp)` | HP 바가 `0/90`에 고정 | [[U단계_HP게이지_UMG_실장]] |
| `WinningTeam` 초기화 | 이전 판 승자가 잔류(bBattleOver=false라 무해하나 감사 혼선) | — |

**재현 시나리오**: 한 판 완주(적 4기 Hp=0·DYING 고정) → `InitBattle()` 재호출 → `bAlive=true`로 "부활"하지만 Hp는 0 그대로, 스프라이트는 누워 있고, 클릭도 안 되며, 첫 피격에 즉사한다. → **TC-F5-11("비파괴 종료 → InitBattle 재호출로 재시작 가능")이 문면상 PASS(크래시 없음)인데 실제로는 플레이 불가.**

**확신도**: CONFIRMED.

**요구 결정**: F5의 "재시작 가능" 계약을 택일.
- **(a) 완전 재시작**(권고): 위 7항목 전부 리셋 추가(≈15노드). TC-F5-11/N18을 "재시작 후 한 턴 정상 진행 + 8기 Hp=MaxHp + 전원 IDLE·클릭 가능"으로 강화.
- **(b) 최소 보장**: "InitBattle 재호출이 크래시·에러 없이 완주"만 보장, 완전 재시작은 A6 이월. **이 경우 TC-F5-11의 문구를 반드시 격하**해야 한다(현 문구는 (a)를 약속한다) + 오너 비주얼 TC에 "재시작해도 시체가 안 일어나는 것은 예정 동작" 사전 고지 필요.

---

### [BLOCKER-4] TS3(쿨다운 스윕·막기 해제)는 "기존"이 아니라 **미구현** — 3문서 3주장 (CONFIRMED 3자 충돌)

| 문서 | TS3 소속 |
|---|---|
| [[상태이상_확정]] §5-1 TS3 | "**(기존 불변** — ★기절 여부와 무관하게 실행)" → **이미 있다고 서술** |
| [[plan]] §F7-4 | "쿨다운 진행: `EnterTurnStart`(자기 턴 시작)에서 …−1(하한0)" → **F7 소관** |
| Director F5 지시서 | "TS3 쿨다운−1 + 막기해제" → **F5에서 만든다** |
| **F4 실적**([[F4_중단_인수인계]] §3) | `GetSkillCooldown`/`SetSkillCooldown`(접근자) · step0 가드 · step9 세팅뿐 — **매 턴 스윕 없음** |

**귀결**: 엔지니어가 "기존 불변"을 믿고 TS3를 건너뛰면 —
1. 쿨다운이 영원히 안 줄어든다 → 베기(cd1)는 **판당 1회**만 사용 가능(F7에서 발현, F5에선 무증상)
2. `bBlockActive`가 한번 켜지면 **영구 막기**(F7에서 발현)
3. **F5 설계의 핵심 근거인 "TS3가 TS4보다 앞(이중 페널티 방지)"이 공허해진다** — 없는 노드의 순서는 검증할 수 없다
4. 본 문서 TC-SE06 · TC-F5-N06/N07(이중 페널티·영구 막기 검출)이 **실행 불가**

**확신도**: CONFIRMED(3문서 대조).

**요구 결정(권고)**: **F5가 TS3를 신설**한다고 확정. 구현 주의 2건:
- `SkillCooldowns`는 **`Map<String,Int>`**(F4 실적 — 키가 Integer가 아니라 **String**이다) → 스윕은 `Keys` 배열을 **먼저 뽑아 두고** ForEach(순회 중 컨테이너 변경 금지) → `Max(0, V−1)`로 Set.
- 막기 해제는 `bBlockActive=false` + (F7 결선 시) `bFreeze=0` 원복까지 한 쌍. F5 시점엔 막기 시전 경로가 없어 도달 불가 → **정적 검증이 유일 방어선**.

---

### [BLOCKER-5] `bFreeze=1` 세팅 시점 미정 — 즉시 세팅하면 사망 모션이 재생되지 않는다 (CONFIRMED)

**공백**: Director 지시 = "DYING(RowIndex 13, FrameCount 5) 재생 + **`bFreeze=1`**(idle 복귀 금지)". **언제** 1을 넣는지가 없다.

`bFreeze`는 [[plan]] F0⑥ 정의상 "**Time을 쓰지 않고 고정 프레임(마지막 유효 프레임 = FrameCount−1)을 샘플링**"한다. DYING 재생과 **동시에** 1을 세팅하면 프레임 0~3을 건너뛰고 **즉시 프레임 4로 팝** → **쓰러지는 동작 자체가 화면에 없다.** 오너의 ★필수 확인 문구가 "사망(**쓰러져** 고정)"인데 "쓰러지는 과정"이 사라진다.

**올바른 순서**(기존 HURT 타이머 구조를 그대로 재사용, 종단만 교체):
```
[DYING 분기]  SetScalar(TimeOffset = GetGameTimeInSeconds)
              SetScalar(RowIndex   = 13)
              SetScalar(FrameCount = 5)        ← ★HURT는 4다(motions.csv Row12) — 안 바꾸면 5프레임 중 4개만 돈다
              (bFreeze는 이 시점엔 0 유지)
           → RetriggerableDelay( 5/8 − 0.05 = 0.575s )      ← 기존 idle 복귀 타이머 자리
           → SetScalar(bFreeze = 1)                          ← idle 복귀 노드를 이걸로 치환
              ※ RowIndex를 0으로 되돌리지 않는다(되돌리면 IDLE 마지막 프레임에서 얼어붙어 "서 있는 시체")
```

**동반 함정(이미 문서화된 것)**: [[언리얼_MCP_실전노하우]] L130 —
> `SetScalarParameterValue` 노드는 `declaring_class=/Script/Engine.MaterialInstanceDynamic` **명시 필수** — 안 하면 MPC용 오버로드가 생성돼 **무음 실패**

→ 이 함정을 밟으면 **에러도 경고도 없이 bFreeze가 아예 안 써지고 시체가 계속 순환 재생**(꿈틀거림)한다. F5에서 이 노드를 **처음으로** 신규 생성하므로 발생 확률이 높다. → TC-F5-N16/N17.

**확신도**: CONFIRMED(셰이더 수식상 자명).

---

## ② 적대적 검토 — HIGH

### [H-1] TS1을 기존 `SetTurnCounter(+1)` **앞**에 스플라이스하지 않으면 사망 스킵이 TurnCounter를 올린다 (CONFIRMED)

현행 `EnterTurnStart`(Function Graph)의 실배선([[전투로그]] "구현 위치" 실측 기록):
```
IsValid(ActiveUnit) → [Is Valid 분기 진입 "직후"] SetTurnCounter(GetTurnCounter + 1) → MarkerOn(ActiveUnit) → …
```
즉 **`SetTurnCounter(+1)`가 IsValid 분기의 첫 노드**다. plan의 TS1(사망 스킵) → TS2(TurnCounter+1) 순서를 지키려면 **기존 노드 앞에 끼워 넣어야** 한다. "새 로직은 뒤에 붙인다"는 관성으로 `IsValid → SetTurnCounter → bAlive Branch`로 배선하면 **사망 스킵도 +1**이 된다.

**귀결**: [[광폭화_재검증]] §2 · TC-F1-03("TurnCounter는 EnterTurnStart IsValid 경로만 +1, **사망스킵 미증가**")과 **F9a 원장(23 유닛턴, B1†T5·A1†T6·B2†T11…)이 통째로 어긋난다**. 사망이 누적될수록 turn 번호가 부풀어 **광폭화(turn>30) 발동이 앞당겨지고**, F9a 원장 대조가 전부 FAIL한다. F5 단독 TC로 안 잡으면 F8/F9에서 원인 규명에 사이클을 태운다.

**검출**: B1 사망 후, A1의 **연속 두 턴 사이 `turn` 증분 = 살아있는 유닛 수(7)**. 8이면 위반. → TC-F5-N01/N04.

---

### [H-2] 스킵 경로의 exec **종단(early-out)** 이 명세에 없다 — 시체에게 커맨드가 열리고 큐가 2칸 튄다 (CONFIRMED 위험)

TS1/TS5는 "**즉시 EnterTurnEnd**"라고만 쓰여 있고, **그 뒤 exec를 끊는다는 말이 없다.** BP에서 Branch의 True 핀 → `EnterTurnEnd()` 호출 노드의 `then`을 TS2 이후로 이어 붙이면(흔한 배선):

1. 사망/기절 유닛이 `EnterTurnEnd`를 1회 호출 → **CurrentIndex +1**
2. 이어서 TS2(TurnCounter+1) · TS3 · TS6(MarkerOn·ActionCam·AwaitCommand)까지 실행 → **시체에게 커맨드 UI가 열린다**(플레이어가 시체로 공격 가능)
3. 그 턴이 정상 종료되며 `EnterTurnEnd` **재호출** → **CurrentIndex +1** → 인덱스가 2칸 전진 → **다음 유닛이 턴을 통째로 잃는다**

**확신도**: CONFIRMED(구조상 가능) / PLAUSIBLE(엔지니어가 실제로 밟을지).
**요구**: TS1 True·TS5 True 경로는 `EnterTurnEnd()` 호출 후 **exec 종단**(then 미연결). → TC-F5-N02(정적) + N03(런타임 큐 순회).

---

### [H-3] `EnterTurnEnd`가 이제 **진입점 3개** — TE2(δ틱)를 스킵 경로가 경유하는지가 STUN 정확성의 전부 (CONFIRMED)

진입점: ① 정상 턴(`EnterExecuting` then_1) ② **사망 스킵(TS1)** ③ **기절 스킵(TS5)**.

STUN dur=1이 "정확히 1턴"인 근거는 [[상태이상_확정]] §5-3의 단 한 문장 —
> **스킵 꼬리도 EnterTurnEnd를 경유하므로 반드시 차감된다**

엔지니어가 스킵 경로를 "EnterTurnEnd 호출" 대신 **"CurrentIndex만 +1하고 EnterTurnStart 재호출"** 로 최적화하면(짧고 자연스러운 유혹), TE2를 안 거친다 → `RemainingTurns`가 **절대 안 줄어든다** → 그 유닛은 **영원히 행동 불가** → §5-5가 "구조적으로 불가(CONFIRMED)"라고 못박은 **무한 기절 락이 배선 실수로 재현**된다.

**검출**: 정적(TS1/TS5 경로가 `EnterTurnEnd` 노드를 경유) + 런타임(STUN 부여 → **정확히 1턴만** 스킵, 2턴째 정상 행동). → TC-F5-N09/N10.

---

### [H-4] δ틱 위치 위반 시 ATK_DOWN dur=1이 **무효과**·dur=2가 **1회**로 줄어든다 (CONFIRMED — 舊 D5 함정의 재발)

ATK_DOWN은 **피부여자 자기 턴의 Executing(`ResolveHit` step4)** 에서 소비된다. 그래서 차감이 **자기 턴 종료(TE2)** 여야 한다.

TE2를 `EnterTurnStart`로 옮기면(체크 후 차감이라도):
- dur=1: 자기 턴 시작에 1→0 → **엔트리 제거** → 같은 턴 Executing의 step4가 엔트리를 못 찾음 → **약화 0회**
- dur=2: 2→1 → 그 턴 약화 1회 → 다음 자기 턴 1→0 제거 → **약화 총 1회**(정답 2회)

이것이 [[상태이상_확정]] §5-4가 "舊 system-ui 표(dur=1 무효과·+1 오프셋)는 **폐기**"라고 명시한 바로 그 함정이다. **다시 지으면 조용히 틀린다**(크래시·경고 0).

**검출(F5에서 가능 — 스킬 UI 불필요)**: 스캐폴드 `ApplyStatus(A1, "ATK_DOWN", 0.25, 2)` → A1의 **자기 턴 2회 연속** 기본공격 dmg = `floor(40 × 0.75 × 1.0) − 10 = 30 − 10 = 20` → **3회째 30으로 복귀**.
- `20, 20, 30` → **PASS**(δ 정상)
- `20, 30, 30` → TE2가 TurnStart(체크 후 차감)로 이설됨
- `30, 30, 30` → TE2가 TurnStart(체크 **전** 차감) 또는 GetOutgoingAtkMult 미소비
→ TC-F5-N08 ★

---

### [H-5] 게이트 마진 0.95s는 **구조적 불변식**이지만, 플래그를 유닛 이벤트로 옮기면 잠식된다 (CONFIRMED 구조 / PLAUSIBLE 실수)

`EnterExecuting`의 Sequence 2분기는 **같은 Sequence 노드에서 갈라진다** → PlayAttack의 내부 지연(+0.58s, [[W2_Executing개편]] §8)이 **양쪽에 동일 적용** → 마진은 Delay 값만으로 결정된다:

```
then_0 : Delay(0.25) → ResolveHit  … 플래그 확정 = Sequence+0.25s
then_1 : Delay(0.75) → WalkBack(즉시 반환) → Delay(0.45) → EnterTurnEnd  … 게이트 평가 = Sequence+1.20s
마진 = 1.20 − 0.25 = 0.95s  (불변 — W2 WT-12가 실측한 1.30s와 동일 논리)
```

**이 불변식이 깨지는 유일한 경로**: `bBattleOver` 세팅을 **`ResolveHit`(동기 Function) 밖으로 빼는 것.** 특히 DYING 처리를 하러 `PlayHurtReaction`(유닛, `RetriggerableDelay` 보유)에 승패 판정까지 함께 넣으면, 플래그가 latent 뒤에 세팅된다 → 세팅 시각 0.25+0.575 = **0.83s**(마진 0.37s로 축소). F6가 FrameCount를 데이터 구동으로 바꾸면(8프레임 모션 = 0.95s 유지) **역전**한다.

**요구**: `bBattleOver`/`WinningTeam` 세팅은 **`ResolveHit` step8 안(동기)** 에서만. `PlayHurtReaction`은 **연출 전용**(Manager 상태 쓰기 금지). → TC-F5-N12/N13.

---

### [H-6] step8 death 분기에 생존수 ForEachLoop을 끼우다 exec를 떨어뜨리면 **킬링블로우의 로그·쿨다운·8.5가 통째로 사라진다** (CONFIRMED 위험)

F4가 만든 step8 death 분기: `bAlive=false → ActiveStatuses Clear(+CLEAR 로그) → [8.5 합류] → 9`.
F5가 여기에 `ForEachLoop(TurnQueue)` 생존수 카운트를 **끼워 넣는다**. ForEachLoop은 `LoopBody`/`Completed` **두 출력**을 갖는데, 삽입 시 `Completed`를 원래의 다음 노드에 재연결하지 않으면 exec가 **조용히** 끊긴다(F4 사고와 같은 계열 — `delete_node`가 핀 연결 11곳을 끊은 사건, [[F4_중단_인수인계]] §1).

**귀결**: **킬링블로우만 BattleLog 라인이 없다** → F9a 원장에서 마지막 타격이 증발 · 쿨다운 미세팅 · effect 필드 미기록. 그런데 **전투는 정상 종료되므로 아무도 즉시 알아채지 못한다.**
**검출**: 킬링블로우 라인(`dmg=<N>|hp=0`)이 **반드시 1줄 존재**. → TC-F5-N14 ★

---

### [H-7] 시체를 때릴 수 있다 — 타겟 제외가 **2중**(ClickBox + 커밋 검증)이 아니면 턴이 증발한다 (CONFIRMED 위험)

F4의 `ResolveTargetPool`은 `bAlive` 필터를 갖지만, **`NotifyUnitClicked`의 수락 조건은 (E2 원본 기준) "상대팀인가"뿐**일 가능성이 크다. `ClickBox`를 NoCollision으로 못 바꾸거나 클릭 판정이 Sprite 콜리전을 쓰면 **시체 클릭이 커밋된다.**

커밋되면:
1. `ResolveHit(A1, 시체B1, 31000000)` → step0~7 정상 계산 → step8 `Hp = Max(0, 0−30) = 0` → **`Hp<=0` 재진입**
2. `bAlive=false` 재세팅 · `ActiveStatuses` 재Clear · **생존수 재카운트 → bBattleOver 재평가**(멱등이라 무해)
3. `PlayHurtReaction` → `bAlive==false` → **DYING을 처음부터 다시 재생**(누워 있던 시체가 다시 쓰러진다)
4. BattleLog `dmg=30|hp=0` **유령 라인** → F9a 원장 오염 + **플레이어 턴 낭비**

**요구(3중 방어)**: (a) 사망 시 `ClickBox` → NoCollision (b) `NotifyUnitClicked`가 **`ResolveTargetPool` 결과 포함 여부**로 수락(팀 비교만으론 부족) (c) 권고: `ResolveHit` 진입부 `Target.bAlive==false → 경고 로그 + return` 가드([[상태이상_확정]] E2가 "방어적으로 허용"한 것). → TC-F5-N15 ★

---

### [H-8] End 상태의 **기계 관측 수단이 없다** — TC-F5-01/05/10/11이 판정 불가 (CONFIRMED)

현행 로그에 **상태 전이 라인이 없다**([[E2_상태머신]]: "진단용 PrintString은 확인 직후 삭제 — 최종 코드에는 없음"). `BattleLog|`는 **타격 시에만** 나온다. 그런데 plan TC-F5-01의 판정방법은 "**로그(상태전이)**" — **존재하지 않는 로그를 전제한다.**

**대안(현재 가능)**: PIE `get_properties(Manager)`로 `BattleState==6 ∧ bBattleOver==true ∧ WinningTeam` 폴링(End는 **종단 상태**라 사후 관측 가능) + "30초 방치 후 BattleLog 라인 수 불변·TurnCounter 불변"으로 간접 증명. **가능하지만 비싸다.**

**권고**: `EnterEnd`에 **영구 1줄** 추가(4~6노드) —
```
BattleEnd|turn=<TurnCounter>|winner=<0|1>|survivors=<N>
```
F9a 원장 대조(승패 시점 확정)에도 어차피 필요하다. `BattleLog|` 프리픽스를 오염시키지 않으므로 기존 `extract_battle_log.py` 무영향(별도 grep — [[상태이상_확정]] §8-2의 StatusLog와 동일 취급).
**Director 결정 필요**: 로그 1줄 추가 vs PIE 폴링으로 갈음. → TC-F5-N23.

---

## ③ 적대적 검토 — MEDIUM

| # | 항목 | 내용 | 확신도 |
|---|---|---|---|
| M-1 | **`WinningTeam` 자료형** | bool이면 "미정" 상태를 표현할 수 없다(false = 적팀 승리 vs 미정 구분 불가). 반드시 **`bBattleOver`와 쌍으로만** 읽어야 한다(단독 조회 금지). Byte/Enum 승격은 A6 재량 | CONFIRMED |
| M-2 | **StatusLog `remaining=` 의미 모호** | 스키마는 "**차감후** 잔여턴"([[상태이상_확정]] §8-2)인데 **SKIP_TURN은 TS4/TS5에서 차감 없이** 방출된다 → SKIP_TURN 라인의 remaining이 1인지 0인지 미정. **정의 고정 권고**: APPLY=Duration / SKIP_TURN=**차감 전 현재값**(dur1이면 1) / EXPIRE=0 → STUN dur1의 감사 시퀀스 = `APPLY(1) → SKIP_TURN(1) → EXPIRE(0)` | CONFIRMED |
| M-3 | **TC-QA13("remaining 시퀀스로 지속 검증")은 관측점이 2개뿐** | TE2는 **중간 틱(2→1)을 로그로 남기지 않는다**(§8-2 "TICK 미기록"). ATK_DOWN dur=2의 관측 가능 라인은 APPLY(2)·EXPIRE(0) 둘뿐 → "단조감소"를 실제로 볼 수 없다. **ATK_DOWN 지속의 진짜 검증기는 데미지 값**(20/20/30, H-4) | CONFIRMED |
| M-4 | **`% 큐길이` 0 나눗셈은 도달 불가** | TurnQueue는 splice 금지(H2)라 Length는 상수 8. 또 BP `%`는 B=0에서 크래시가 아니라 **0 반환 + 경고**다. → TC는 "Length==8 유지 + `Modulo by zero` 경고 0건"으로 충분. **검토 결과: 크래시 축은 해당 없음**(TC-F5-05의 "크래시 없음"은 통과 예정) | CONFIRMED |
| M-5 | **사망 유닛의 HP 바 정책 미정** | 시체 머리 위에 `0/90` 바가 계속 뜬다(WidgetComponent는 죽어도 살아있음). plan에 정책이 없다 → **오너 판단 필요**(권고: 사망 시 Hide, InitBattle에서 복원 — BLOCKER-3(a)와 한 묶음) | CONFIRMED |
| M-6 | **`BattleState=6` 안전성** | BattleState는 **순수 Byte**(enum 아님)이고 분기는 `Branch(Equal)` 뿐([[E2_상태머신]] ②) → 망라적 Switch가 없어 6 추가는 안전. Byte 상한(255)도 무관. **정적 확인만 하면 통과** | CONFIRMED |
| M-7 | **EnterEnd의 "TurnMarker 전원 OFF"는 사실상 no-op** | 마커는 `EnterExecuting` 진입 시 이미 꺼진다([[W2_Executing개편]] §2) + 스킵 경로는 TS6(MarkerOn) 앞에서 빠져나가므로 애초에 안 켜진다 → End 시점에 켜진 마커가 없다. **비용 0의 방어로 유지 권장**(TC는 유지) | CONFIRMED |
| M-8 | **InitBattle 재호출 타이밍(verifier 절차)** | 전투 **진행 중** InitBattle을 부르면 in-flight Delay(0.35/0.75/0.45)가 살아 있어 이중 구동한다([[W2_Executing개편]] 함정 발견 1의 재판). → **TC-F5-11/N18/QA15는 반드시 End 도달 후에만 실행**(절차 규칙) | CONFIRMED |
| M-9 | **DYING 리터럴(13/5)은 F6 교체 대상** | F5는 RowIndex=13·FrameCount=5를 리터럴로 박는다. F6("리터럴→데이터 구동")이 `PlayAttack`만 바꾸고 **`PlayHurtReaction`의 DYING 리터럴을 놓치면** F6의 "무회귀" 판정이 헛돈다 → **F6 TC로 이월 등재** | CONFIRMED |
| M-10 | **HURT(FrameCount 4) ↔ DYING(FrameCount 5) 불일치** | motions.csv: Row12 hurt=**4프레임**, Row13 dying=**5프레임**. DYING 분기가 기존 HURT의 `SetScalar` 노드를 재사용하며 **RowIndex만 13으로 바꾸면 FrameCount는 4로 남는다** → 5프레임 중 4개만 순환하고, `bFreeze`가 고정하는 "마지막 프레임"이 **4번째(index 3)** 가 되어 **쓰러지다 만 자세**로 굳는다 | CONFIRMED |

---

### F5가 F4의 실적과 충돌하는 지점 (Director 질의 답)

| 축 | 판정 |
|---|---|
| **`bAlive=false` 이중 세팅?** | **충돌 없음.** F4 step8이 이미 `Target.bAlive=false`를 쓴다. F5는 **그 뒤에 생존수 카운트+플래그 세팅을 이어붙일 뿐** 재세팅하지 않는다(idempotent라 재세팅해도 무해하나, 노드 낭비 + H-6의 exec 절단 위험만 키운다). **TC-F5-N11이 "SetbAlive 노드가 death 분기에 정확히 1개"를 정적 확인.** |
| **`ActiveStatuses` Clear 이중?** | 상동 — F4가 step8에서 Clear(+CLEAR 로그). F5는 **추가하지 않는다.** |
| **`PlayHurtReaction` 개명 여파** | F5가 여기에 DYING 분기를 붙인다. **호출부는 `EnterExecuting` then_0 한 곳뿐**(F4 실적)이라 배선 충돌 없음. 단 **분기 위치**가 중요 — 아래 참조. |
| **DYING 분기 위치 vs VFX** | 히트 VFX·SFX가 `PlayHurtReaction` 안에 있다면, **DYING 분기를 이벤트 최상단에 두면 킬링블로우에서 VFX가 사라진다**(TC-F5-09 FAIL). → 분기는 **공용 VFX/SFX 재생 뒤**에 두거나 양 분기에 각각 배치. → TC-F5-N19 |
| **`bAlive` 판정 순서** | `ResolveHit`(Function, 동기)이 **먼저 끝난 뒤** `PlayHurtReaction`이 호출된다(then_0 직렬) → DYING 분기가 읽는 `bAlive`는 **이미 false**다. ✅ 이 순서가 뒤바뀌면(연출을 먼저 호출) **DYING이 영원히 안 나오고 HURT 후 idle 복귀**(서 있는 시체)한다 → TC-F5-N16이 호출 순서를 정적 확인 |
| **`SelectedTargets`(배열) vs 사망** | 사망자가 배열에 남아도 F5엔 무해(길이 1, 다음 턴 `EnterAwaitCommand`에서 Clear). A2 AoE에서 유의미 |
| **`DebugForceEffectChance` = −1 sentinel** | F4가 −1로 확정 → F5의 STUN TC는 **1.0 강제**로 결정론 복원 가능 ✅ |

---

## ④ TC 표 — A. 승계(plan §F5 TC-F5-01~12) · 판정방법 구체화

> **판정도구 약칭**(F4_TC 승계): **LOG**=엔진 로그 파싱(`D:\unreal\projectTP\Saved\Logs\projectTP.log` grep 또는 MCP `GetLogEntries`) / **SCF**=스캐폴드 직접호출 후 LOG / **MOCK**=PIE `set_properties`로 값 주입 후 LOG / **GRAPH**=MCP 정적 그래프 조회(`find_nodes`·`get_connected_subgraph`·`get_node_infos`) / **PIE**=PIE 인스턴스 프로퍼티 재조회(`ObjectTools.get_properties`, `UEDPIE_0` 월드) / **CMP**=컴파일 에러 0(`warnings_as_errors=true`) / **오너**=오너 육안(PIE).
> **스캐폴드 규약**(함정⑥): 유닛은 반드시 `GetTurnQueue()`→`Array Get(사본)`으로 획득 — **리터럴 오브젝트 레퍼런스 금지**(PIE 그림자 액터).
> **배정표**(F0③): A1·A2·B1·B2 = 전사2성(Hp90/Atk40/Def10) · A3·A4·B3·B4 = 마법사2성(Hp80/Atk42/Def6).
> **턴큐 순서**(E2 TC-11 실측): `[A1, B1, A2, B2, A3, B3, A4, B4]` — 착수 시 PIE로 1회 재확인할 것.
> **킬 레시피**(결정론): `MOCK B1.Hp=30` → A1 기본공격(dmg 30) → `hp=0` 정확 킬. 마법사 대상은 `MOCK Hp=34`.

| ID | 구분 | 조건 → 기대결과 (재현 시나리오) | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-01**★ | 기능 | **End 레이스 차단**: MOCK(B1~B3.bAlive=false, B4.Hp=30) → A1이 B4 킬 → 킬 시각(`BattleLog` 타임스탬프)과 게이트 시각의 델타 ≥0.5s → 최종 `BattleState==6` ∧ `bBattleOver==true`. **B분기가 EnterTurnEnd를 호출했음에도 TurnStart로 되돌아가지 않음**(이후 새 BattleLog 라인 0줄). **2회 재현** | MOCK+LOG(타임스탬프 델타) + PIE(BattleState/bBattleOver) + LOG(End 이후 라인 수 불변) | 대기 |
| **TC-F5-02** | 기능 | **사망유닛 턴스킵**: MOCK B1 킬 → 큐 순회로 B1 차례 도래 → **Executing 미진입**(B1이 attacker인 BattleLog 라인 0줄) · **마커 미점등** · **ActionCam 미부착**(CamCut 로그 없음) · 즉시 EnterTurnEnd(다음 유닛 턴이 정상 개시) | LOG(attacker=B1 0줄 + CamCut 부재) + PIE(TurnMarker visible=false) | 대기 |
| **TC-F5-03** | 기능 | **큐 길이 불변**: 사망 전/후 `GetTurnQueue().Length == 8` 유지(splice 금지, H2). TurnQueue에 Remove/Insert/Clear 노드 **0개**(InitBattle 제외) | PIE(Length) + GRAPH(배열 변경 노드 검색) | 대기 |
| **TC-F5-04**★ | 기능 | **index<현재 유닛 사망 → 순회 정합**: B1(idx1) 킬 후 **2사이클 완주** → attacker 시퀀스 = `A1,A2,B2,A3,B3,A4,B4, A1,A2,…`(B1 부재, **각 생존 유닛 정확히 1회/사이클**). 중복·누락 0 | LOG(attacker 시퀀스 전수) + PIE(CurrentIndex가 EnterTurnEnd당 정확히 +1) | 대기 |
| **TC-F5-05** | 기능 | **마지막 유닛 사망 프레임**: TC-F5-01 시나리오에서 승패 확정 + **`Modulo by zero` 경고 0건** + Length==8 유지 + 크래시/hang 0 | LOG(`grep -c "Modulo by zero"` = 0) + PIE | 대기 |
| **TC-F5-06** | 기능 | **시체 정지(기능판)**: 사망 유닛의 SpriteMID에서 `RowIndex==13` ∧ `FrameCount==5` ∧ `bFreeze==1`이 **사망 0.6초 후~30초 후 두 시점 모두 동일**. (MID 스칼라 조회 불가 시 대체: GRAPH로 DYING 분기가 `RowIndex=0` 복귀 노드에 **연결되지 않음**을 확인) | PIE(MID `scalarParameterValues`) 또는 GRAPH(복귀 경로 부재) | 대기 |
| **TC-F5-07**★ | 기능 | **사망자 타겟 불가**: 사망 B1에 대해 ① `ResolveTargetPool("ENEMY1", A1)` 반환 배열에 B1 **부재** ② B1의 `ClickBox` `collisionEnabled=="NoCollision"` ③ **SCF로 시체 클릭 강제**(`NotifyUnitClicked(B1)`) → **거부**(SelectedTargets 길이 0 유지 + 거부 로그 1줄), Executing 미진입 | SCF+PIE(풀 배열·콜리전·SelectedTargets) + LOG | 대기 |
| **TC-F5-08** | 기능 | **마커 전원 OFF**: End 도달 후 8기 전부 `TurnMarker.visible==false` | PIE(8기 순회) | 대기 |
| **TC-F5-09** | 기능 | **킬링블로우 VFX**: 마지막 타격에도 히트 VFX 스폰 로그/액터 발생(End 전이가 VFX를 삼키지 않음). **DYING 분기가 VFX 재생 노드보다 뒤**(정적) | GRAPH(분기 위치) + LOG/PIE(VFX 액터) | 대기 |
| **TC-F5-10** | 기능 | **양측 대칭 종료**: ① 적 전멸(위 시나리오) → `WinningTeam == true`(파티) ② **MOCK A1~A3.bAlive=false, A4.Hp=30** → B측이 A4 킬 → `WinningTeam == false`(적) + `BattleState==6`. **양 방향 모두** End 도달 | MOCK+PIE(WinningTeam/BattleState) 2회 | 대기 |
| **TC-F5-11**★ | 기능 | **비파괴 종료**: End 후 ① 8기 액터 전부 `IsValid`(destroy 0) ② `InitBattle()` 재호출 → **BLOCKER-3 결정에 따라 판정 기준 확정**: (a)안 = 8기 `Hp==MaxHp` ∧ `bAlive==true` ∧ `bFreeze==0` ∧ `RowIndex==0` ∧ ClickBox QueryOnly ∧ **1턴 정상 진행** / (b)안 = 크래시·에러 0으로 완주. **End 도달 후에만 실행**(M-8) | SCF+PIE(8기 전수) + CMP + LOG | 대기 |
| **TC-F5-12** | 기능 | **하이라이트 잔존 없음**: 하이라이트된 적이 그 타격에 사망 → 사망 직후·End 후 모두 8기 하이라이트 상태 전부 OFF | PIE(하이라이트 프로퍼티 8기) | 대기 |

---

## ⑤ TC 표 — B. 상태이상 통합 TC의 **F5 실행분**

> **F5 검증 전략(중요)**: F5엔 스킬 UI가 없고 `ResolveHit` 호출 노드의 `SkillId`가 **단일 리터럴 핀**이라, 이를 베기(31001000)로 바꾸면 **8기 전원이 베기를 쓴다**(1기만 통제 불가). → **틱/스킵 의미 검증은 `ApplyStatus` 스캐폴드 직접 부여**([[상태이상_확정]] §12-2가 "지속·틱 단독 검증용"으로 명시 승인한 2순위 훅)로 수행하고, **롤 경로(step8.5) 자체는 F4에서 이미 검증**(TC-SE01/SE05/QA09)됐다. **베기 전원 사용 런은 버리지 않고 "전원 기절 스트레스(E5)" TC로 재활용**한다(TC-F5-N05).

| ID | 구분 | 조건 → 기대결과 (F5 실행판으로 구체화) | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-SE02** | 기능 | **1회 스킵**: SCF `ApplyStatus(B1,"STUN",0,1)`(B1의 턴 도래 **전**) → B1 자기 턴: `StatusLog\|…\|event=SKIP_TURN` 1줄 + **B1이 attacker인 BattleLog 0줄** → **다음 B1 턴: 정상 공격 1줄** | SCF+LOG(StatusLog + BattleLog 부재/존재) | 대기 |
| **TC-SE03** | 기능 | **약화 2회**(스캐폴드판): SCF `ApplyStatus(A1,"ATK_DOWN",0.25,2)` → A1의 자기 턴 **2회 연속** `dmg=20`(vs 전사 Def10) → **3회째 `dmg=30`**. (파이어볼 롤 경로 자체는 **F7 이월**) | SCF+LOG(dmg 시퀀스 20/20/30) | 대기 |
| **TC-SE06** | 기능 | **기절 턴에도 쿨다운·막기 진행**(TS3 < TS4): SCF ① `SetSkillCooldown(B1,"31001000",1)` ② `B1.bBlockActive=true` ③ `ApplyStatus(B1,"STUN",0,1)` → B1 기절 턴 종료 후 **`GetSkillCooldown(B1,"31001000")==0`** ∧ **`B1.bBlockActive==false`**. 둘 중 하나라도 1/true면 **TS3가 TS4 뒤**(이중 페널티) | SCF+PIE(쿨다운 Map·bBlockActive) | 대기 |
| **TC-SE07** | 기능 | **기절 스킵 TurnCounter +1**: 기절 스킵 턴에도 `TurnCounter`가 증가(사망 스킵과 구분) → BattleLog `turn` 시퀀스에 **갭**이 생긴다(예: …turn=5, turn=**7**…) | LOG(turn 시퀀스) + PIE(TurnCounter) | 대기 |
| **TC-SE09** | 기능 | **재부여 = 갱신**: SCF `ApplyStatus(B1,"STUN",0,1)` 2연속 → `ActiveStatuses` 길이 **1**(중첩 없음) ∧ `remainingTurns==1`(연장 없음) ∧ `StatusLog … event=REFRESH` 1줄 | SCF+PIE(배열 길이) + LOG | 대기 |
| **TC-SE10** | 기능 | **기절자는 살아있다**: 기절 B1이 ① `ResolveTargetPool("ENEMY1",A1)` 풀에 **포함** ② 클릭 가능(ClickBox QueryOnly) ③ `bAlive==true` — 사망자와 명확히 구분 | SCF+PIE | 대기 |
| **TC-SE12** | 기능 | **로그 존재**: 1판에서 `StatusLog\|` 라인이 APPLY·SKIP_TURN·EXPIRE **3종 모두** 최소 1줄씩 방출 | LOG(`grep -o "StatusLog\|.*"`) | 대기 |
| **TC-QA07** | 기능 | **기절 턴 로그 갭 정상 수용**: 기절 턴은 BattleLog 라인이 **없고** turn 번호에 갭이 생긴다 → 원장 대조 스크립트가 이를 **결손이 아닌 정상**으로 처리(갭 위치에 StatusLog SKIP_TURN 존재로 상쇄 검증) | LOG+스크립트(교차 대조) | 대기 |
| **TC-QA13** | 기능 | **지속 = remaining 시퀀스**: STUN dur1의 감사 시퀀스 = `APPLY(remaining=1) → SKIP_TURN(remaining=1) → EXPIRE(remaining=0)`. **turn 차 역산 사용 금지**(m9). ⚠ M-2(SKIP_TURN의 remaining 의미) 확정 후 실행 | LOG(remaining 필드 시퀀스) | 대기(M-2 선결) |
| **TC-QA14**★ | 기능 | **복합 상태(STUN+ATK_DOWN)**: SCF `ApplyStatus(B1,"STUN",0,1)` + `ApplyStatus(B1,"ATK_DOWN",0.25,2)` → B1의 **기절 스킵 턴에도 ATK_DOWN이 차감**된다(TE2 경유) → B1의 **다음(정상) 턴 1회만** 약화(`dmg=20`), 그 다음 턴은 `dmg=30`. **스킵이 다른 상태의 틱을 막지 않음** | SCF+LOG(dmg 시퀀스) + PIE(remainingTurns 추적) | 대기 |
| **TC-QA15** | 기능 | **InitBattle 리셋**: TC-F5-N18로 확장 실행(BLOCKER-3) | — | **N18로 통합** |

---

## ⑥ TC 표 — C. **신규 예외상황 TC**(qa-critic 신규 20)

### C-0. 착수 첫 액션 (5분, 노드 1개도 만들기 전)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-N00**★ | 기능 | **선결 실측 4종**(BP 조회 가능해진 직후 즉시): ① `EnterTurnStart`(Function)가 **이미 `EnterTurnEnd`(Custom Event, Delay 보유) 호출 노드를 갖는가**(null-skip 경로) → 있으면 TS1/TS5의 신규 호출이 컴파일 보장됨. 없으면 **F5가 최초의 Function→latent-CustomEvent 호출**이라 컴파일 실패 가능(함정④/⑨) → 실패 시 `EnterTurnStart`를 Custom Event로 승격하는 대안 확정 ② `EnterTurnEnd`에 **MarkerOff 노드가 실재**하는가(plan ①의 전제) ③ `SetTurnCounter(+1)`가 IsValid 분기의 **첫 노드**인가(H-1의 전제) ④ TurnQueue 순서 = `[A1,B1,A2,B2,A3,B3,A4,B4]`인가 | GRAPH + PIE | 대기 |

### C-1. TS 파이프라인 순서 (Director 지시 — 순서 위반 검출)

| ID | 구분 | 조건 → 기대결과 (재현 시나리오) | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-N01**★ | 기능 | **TS1 < TS2(정적)**: `EnterTurnStart` exec 체인에서 **`bAlive` Branch 노드가 기존 `SetTurnCounter` 노드보다 앞**. 또 `bAlive` Get의 대상이 **새로 Set된 ActiveUnit**(직전 유닛 아님) | GRAPH(exec 순서 + 데이터 핀 소스) | 대기 |
| **TC-F5-N02**★ | 기능 | **스킵 경로 exec 종단(H-2)**: TS1 True · TS5 True 경로의 `EnterTurnEnd` 호출 노드는 **`then` 미연결**(TS2 이후로 흐르지 않음). MarkerOn·AwaitCommand로 가는 경로가 **존재하지 않음** | GRAPH(exec 추적) | 대기 |
| **TC-F5-N03**★ | 기능 | **큐 무결성(런타임)**: B1 킬 후 2사이클 → ① 매 `EnterTurnEnd`마다 CurrentIndex **정확히 +1**(2칸 점프 0회) ② 생존 7기가 사이클당 **정확히 1회씩** attacker로 등장 ③ **시체 B1에게 AwaitCommand가 열리지 않음**(`BattleState==2` 진입 로그/폴링 0회) | LOG(attacker 시퀀스) + PIE(CurrentIndex 폴링) | 대기 |
| **TC-F5-N04**★ | 기능 | **사망 스킵은 TurnCounter 미증가(H-1 런타임)**: B1 사망 후, **A1의 연속 두 턴 사이 `turn` 증분 == 7**(살아있는 유닛 수). **8이면 TS1이 TS2 뒤에 있다** → [[광폭화_재검증]] §2·TC-F1-03·F9a 원장 전부 붕괴 | LOG(turn 시퀀스 산술) | 대기 |
| **TC-F5-N05** | 기능 | **전원 기절 스트레스(E5)**: `ResolveHit` SkillId 핀=`31001000` + `DebugForceEffectChance=1.0` → 전 타격이 STUN 부여 → ① 무한 루프·hang·크래시 **0** ② 턴이 계속 전진(CurrentIndex 순환) ③ TurnCounter 계속 증가 ④ 각 유닛 **정확히 1턴만** 스킵 ⑤ 베기 피해(42)로 HP 단조 감소 → **유한 턴 내 End 도달**(G1+G2 무한 락 차단 실증). **종료 후 핀을 `31000000`으로 원복** | LOG(전 시퀀스) + PIE | 대기 |
| **TC-F5-N06** | 기능 | **TS3 실재 + TS3 < TS4(정적, BLOCKER-4)**: `EnterTurnStart`에 **쿨다운 스윕 루프**(SkillCooldowns Keys ForEach → `Max(0, V−1)`)와 **`SetbBlockActive(false)`** 노드가 실재하고, **둘 다 STUN 판정(TS4) Branch보다 앞**. 스윕이 `Keys` 배열을 먼저 뽑아 순회(순회 중 Map 변경 아님) | GRAPH | 대기 |
| **TC-F5-N07** | 기능 | **영구 막기 차단(TS3 위반 검출)**: SCF `B1.bBlockActive=true` + `ApplyStatus(B1,"STUN",0,1)` → B1의 기절 턴 **종료 후** `bBlockActive==false`. true로 남으면 **기절당한 막기 유닛이 영구 막기**(피해 반감 영구) | SCF+PIE | 대기 |

### C-2. δ틱 위치 (Director 지시 — 위치 위반 검출)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-N08**★ | 기능 | **δ틱 = 자기 턴 종료(H-4)**: SCF `ApplyStatus(A1,"ATK_DOWN",0.25,2)` → A1 기본공격 dmg 시퀀스 = **`20, 20, 30`**. `20,30,30` = TE2가 TurnStart(체크 후 차감)로 이설됨. `30,30,30` = 체크 **전** 차감(엔트리 즉시 소멸) 또는 step4 미소비 | SCF+LOG(3턴 dmg) | 대기 |
| **TC-F5-N09**★ | 기능 | **STUN dur=1 = 정확히 1턴**: `ApplyStatus(B1,"STUN",0,1)` → B1 스킵 **1회**, 그 다음 자기 턴 **정상 행동**. 2회 스킵이면 TE2 미실행(무한 기절 락 경로), 0회 스킵이면 차감이 판정보다 앞 | SCF+LOG | 대기 |
| **TC-F5-N10**★ | 기능 | **TE2가 무분기·ActiveUnit 한정·TE3 앞(정적, H-3)**: `EnterTurnEnd`에서 `TickStatusesAtTurnEnd` 호출이 ① **Branch 없이 항상 실행**(무분기) ② 대상이 **ActiveUnit 단수**(ForEachLoop(TurnQueue) 전체 아님 — 전체면 남의 상태까지 깎는다) ③ **`SetCurrentIndex` 노드보다 앞** ④ **3개 진입점(정상·TS1·TS5) 전부** 이 노드를 경유 | GRAPH(exec 추적 3경로) | 대기 |

### C-3. 레이스·타이밍 (Director 지시 — 마진 검증)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-N11**★ | 기능 | **bBattleOver 카운트 대상(BLOCKER-1)**: 생존수 ForEachLoop의 필터가 **`Element.bIsParty == Target.bIsParty` ∧ `Element.bAlive`**(Target과 **같은** 팀). `!=`(반대 팀)이면 **전투가 영원히 안 끝난다**. + death 분기에 `SetbAlive` 노드 **정확히 1개**(F4와 이중 세팅 아님) + 카운터 로컬 int 기본값 **0** | GRAPH(비교 노드 방향·핀 소스) + 런타임(TC-F5-01) | 대기 |
| **TC-F5-N12**★ | 기능 | **플래그 set-only(레이스 원천 차단)**: `ResolveHit` 서브그래프에 `EnterEnd`·`SetBattleState`·`EnterTurnEnd`·`EnterTurnStart` 호출 노드 **0개** + latent 노드 **0개**. `EnterEnd` 호출 노드는 **전 그래프에서 정확히 1개**이며 그 소유가 **`EnterTurnEnd`의 TE4 Branch True 핀** | GRAPH(2 BP 전수) | 대기 |
| **TC-F5-N13**★ | 기능 | **마진 실측(H-5)**: 매 턴 `BattleLog` 타임스탬프 < 그 턴의 `EnterTurnEnd` 도달 타임스탬프, **델타 ≥ 0.5s**(설계 0.95s). 킬링블로우 턴에서도 성립. + `PlayHurtReaction` 서브그래프에 `SetbBattleOver`/`SetWinningTeam` **0개**(플래그는 ResolveHit 안에서만) | LOG(타임스탬프 델타 전 턴) + GRAPH | 대기 |
| **TC-F5-N14**★ | 기능 | **킬링블로우 로그 생존(H-6)**: 킬 타격의 `BattleLog\|…\|dmg=<N>\|hp=0` 라인이 **정확히 1줄 존재**(step8에 ForEach를 끼우다 exec를 떨어뜨리면 이 줄이 사라진다) + 같은 라인에 `effectRoll=-1`(ON_HIT 스킬일 때) + 쿨다운 세팅됨 | LOG + PIE(쿨다운 Map) | 대기 |
| **TC-F5-N15**★ | 기능 | **시체 재타격 방어(H-7)**: SCF로 사망 B1을 강제 타겟 커밋 시도 → ① `NotifyUnitClicked` 거부(SelectedTargets 길이 0) ② (강행 시) `ResolveHit` 진입부 `bAlive` 가드로 **경고 로그 1줄 + return**, BattleLog **0줄**, DYING **재재생 안 함**, B1.Hp==0 불변 | SCF+LOG+PIE | 대기 |

### C-4. DYING·bFreeze (Director 지시 — FREEZE 누락/리셋 누락)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-N16**★ | 기능 | **DYING 분기 배선(BLOCKER-5)**: `PlayHurtReaction`에서 ① `bAlive` Branch가 **IsValid(SpriteMID) 가드 안쪽**([[E2_상태머신]] 기존 게이트) ② DYING 경로가 `RowIndex=0`(idle) 복귀 노드에 **연결되지 않음** ③ `bFreeze=1` 세팅이 **DYING 재생 직후가 아니라 RetriggerableDelay(≈0.575s) 뒤** ④ `SetScalarParameterValue`의 **`declaring_class=/Script/Engine.MaterialInstanceDynamic`** 명시(미명시 시 MPC 오버로드로 **무음 실패** — 노하우 L130) ⑤ 대상이 **SpriteMID**(MI 애셋 아님) | GRAPH(노드 속성·exec) + CMP | 대기 |
| **TC-F5-N17**★ | 기능 | **DYING 스칼라 3종(M-10)**: DYING 분기가 `RowIndex=13` **+ `FrameCount=5`**(HURT의 4를 그대로 두면 안 됨) **+ `TimeOffset=GetGameTimeInSeconds`**(0 방치 시 임의 프레임에서 시작) 3개 전부 세팅 | GRAPH(SetScalar 노드 3개·핀 값) | 대기 |
| **TC-F5-N18**★ | 기능 | **InitBattle 완전 리셋(BLOCKER-3·QA15 통합)**: End 도달 후 `InitBattle()` 재호출 → **(a)안 채택 시** 8기 전수: `Hp==MaxHp` ∧ `bAlive==true` ∧ `ActiveStatuses.Length==0` ∧ `SkillCooldowns` 전부 0(또는 빈 Map) ∧ `bBlockActive==false` ∧ `bFreeze==0` ∧ `RowIndex==0` ∧ ClickBox `QueryOnly` ∧ HP바 `MaxHp/MaxHp` + Manager: `SelectedTargets.Length==0` ∧ `bBattleOver==false` ∧ `CurrentIndex==0` ∧ `TurnCounter==0` → **재시작 후 1턴 정상 완주**. **(b)안 채택 시** 크래시·`Accessed None` 0으로 완주만 확인하고 나머지는 A6 이월 | SCF+PIE(8기+Manager 전수) + LOG | 대기 |
| **TC-F5-N19** | 기능 | **DYING 분기가 VFX를 삼키지 않음**: 킬링블로우에서도 히트 VFX/SFX가 발생(분기가 공용 VFX 노드 **뒤**에 위치하거나 양 분기에 각각 존재) | GRAPH + LOG/PIE(VFX 액터) | 대기 |

### C-5. End 상태·관측

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-N20**★ | 기능 | **BattleFinished payload(BLOCKER-2)**: 디스패처 실재 + payload 소스 핀이 **BLOCKER-2 결정과 일치**((a) `WinningTeam` 직결 / (b) `Not(WinningTeam)` 노드 경유). **A1엔 소비자가 없어 정적 검증이 유일 방어선** | GRAPH(핀 소스 추적) | 대기 |
| **TC-F5-N21** | 기능 | **BattleState=6 안전성(M-6)**: 전 그래프의 `BattleState` 비교 노드 열거 → 망라적 Switch/Clamp **부재**(Branch Equal뿐) → 6 추가가 기존 분기를 깨지 않음. `EnterEnd`가 `SetBattleState(6)` 실행 | GRAPH + PIE(BattleState==6) | 대기 |
| **TC-F5-N22** | 기능 | **End 입력 전면 잠금**: End 후 `bInputLocked==true` ∧ ① Attack 버튼 클릭 → `BLOCKED` 로그, 상태 불변 ② **CamToggle 클릭 → 무반응**(`NotifyCamToggleClicked`의 bInputLocked 가드 실재 확인 — plan §5-4는 "확인만" 요구) ③ 유닛 클릭 → 무반응 | SCF+LOG+PIE | 대기 |
| **TC-F5-N23**★ | 기능 | **End 기계 관측 수단(H-8)**: Director 결정에 따라 ① **`BattleEnd\|turn=…\|winner=…` 로그 1줄** 존재(권고) 또는 ② PIE 폴링만으로 판정 가능함을 확인(BattleState==6 ∧ 30초 방치 후 BattleLog 라인 수·TurnCounter 불변) | LOG 또는 PIE(폴링) | 대기(결정 선행) |
| **TC-F5-N24** | 기능 | **End 후 새 턴 미개시**: End 도달 후 **30초 방치** → 새 `BattleLog` 0줄 ∧ `TurnCounter` 불변 ∧ `CurrentIndex` 불변 ∧ `BattleState==6` 유지(EnterTurnStart가 다시 안 불린다) | LOG+PIE(2회 폴링) | 대기 |
| **TC-F5-N25** | 기능 | **무회귀 기반선**: F5 전후 ① 8기 Location/FaceLeft/Sprite **diff=0**([[F3_사전스냅샷]] 대조) ② 2 BP 컴파일 에러 0 ③ 걸음(`WalkArrive`/`WalkHome`)·카메라(`CamCut`) 로그가 기존과 동일 ④ **정상 턴(사망·기절 없는)의 BattleLog 값이 F4와 바이트 동일** | PIE(트랜스폼 diff) + CMP + LOG(회귀) | 대기 |

---

## ⑦ 비주얼 TC (오너 육안 — **게이트 불차단**)

| ID | 구분 | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|---|
| **TC-F5-V1**★ | 비주얼 | **사망(쓰러져 고정)·승패 — 한 판이 끝난다**(plan `[F5][오너]` 승계) | 오너 라이브(PIE) | 대기 |
| **TC-F5-V2**★ | 비주얼 | **쓰러지는 동작이 실제로 보인다**(BLOCKER-5): DYING 5프레임이 재생된 **뒤** 고정. 즉시 마지막 프레임으로 **팝**하면 FAIL | 오너 라이브(PIE) | 대기 |
| **TC-F5-V3** | 비주얼 | **시체 꿈틀거림 없음**: 킬 후 **수십 초 방치**해도 동일 프레임(순환 재생 0). bFreeze 무음 실패의 육안 검출기 | 오너 라이브(PIE) | 대기 |
| **TC-F5-V4** | 비주얼 | **킬링블로우 VFX 정상**: 마지막 타격에도 히트 이펙트가 뜬다 | 오너 라이브(PIE) | 대기 |
| **TC-F5-V5** | 비주얼 | **[결정 요청] 시체 위 HP 바**: `0/90` 바가 시체 머리 위에 계속 뜬다(M-5) — 숨길지 유지할지 **오너 판단** | 오너 라이브(PIE) | 대기 |
| **TC-F5-V6** | 비주얼 | **[사전 고지 — 버그 아님]** ① 스킬 선택 UI 없음(Attack 1버튼, F7) ② 승리 후 **Result 화면 없이 화면이 그대로 정지**(A6 이관, 의도) ③ **(BLOCKER-3을 (b)로 결정한 경우)** 재시작해도 시체가 안 일어남 | 오너 라이브(PIE, 고지 확인) | 대기 |

> **오너 라이브 안내 초안(Director용)**: "Attack → 적 클릭을 반복해 **적 1기를 3번 때려 죽여 보세요**(전사 상대 30씩 3방). ①**쓰러지는 애니메이션이 보이는지** ②쓰러진 뒤 **가만히 있는지(꿈틀거리면 버그)** ③그 시체를 **클릭해도 선택 안 되는지** ④**적 4기를 다 죽이면 전투가 멈추는지**를 봐주세요. **Result 화면 없이 그냥 멈추는 게 정상**입니다(A6에서 붙임)."

---

## ⑧ 이월 TC

| TC | 사유 | 검증 예정 |
|---|---|---|
| TC-SE03의 **파이어볼 롤 경로**(step8.5 → ATK_DOWN 부여) | F5엔 스킬 UI가 없어 파볼 단독 시전 불가(SkillId 핀이 전역 리터럴) — **틱 의미는 ApplyStatus 스캐폴드로 F5에서 검증** | F7 |
| TC-SE06의 **막기 시전 경로**(DMG_REDUCE step3) | 막기 스킬 버튼이 F7 — F5는 `bBlockActive` MOCK 주입으로 **해제 로직만** 검증 | F7 |
| TC-F5-N17의 **DYING 리터럴(13/5) → 데이터 구동 교체**(M-9) | F6이 `PlayAttack`만 바꾸고 `PlayHurtReaction`의 DYING 리터럴을 놓치기 쉬움 | F6 |
| TC-F5-N20의 **BattleFinished 소비자 검증** | A1엔 바인딩하는 쪽이 없음(정적 검증만 가능) | A6 |

---

## ⑨ 커버리지 근거 (검토한 축 — 빈손 OK 금지)

- **경계값**: Hp 정확히 0(킬 레시피 MOCK Hp=30) · `RemainingTurns` 1→0 전이(δ) · dur=1의 양끝(0회/2회 스킵) · `FrameCount−1`(bFreeze 고정 프레임) · 큐 인덱스 7→0 랩어라운드 · 생존수 0/1 경계
- **동시성/순서**: `then_0`(ResolveHit) ‖ `then_1`(EnterTurnEnd) 병렬 — **마진 0.95s는 같은 Sequence 분기라 구조적 불변**(N13) · 플래그를 latent 이벤트로 옮길 때의 잠식(H-5) · `ResolveHit` → `PlayHurtReaction` 호출 순서가 DYING 판정을 좌우(N16) · TE2/TE3 순서(N10) · TS1/TS2/TS3/TS4 순서(N01/N06)
- **동시 사망**: **알파에선 구조적으로 불가**(1타격=1대상, 반사·DoT·자해 없음, 자기 턴 중 피격 없음) → 검토 후 **해당 없음** 판정. A2 AoE에서 재검(E1: bBattleOver는 set-only, 루프 완주 후 관문에서만 전이)
- **0 나눗셈**: `% 큐길이` — Length는 상수 8(splice 금지) + BP `%`는 B=0에서 **크래시가 아니라 0 반환+경고** → **크래시 축 해당 없음**, 경고 0건 TC로 갈음(M-4) · `Hp/MaxHp`(HP바)는 F4에서 검증됨
- **null/참조**: 사망자 `SelectedTargets` 잔류 · `CachedUnitFrame` null · `SpriteMID` null(IsValid 게이트, E2 선례) · 빈 타겟 풀(BLOCKER-1의 소프트락 경로)
- **상태 누수**: `InitBattle` 미리셋 7항목(BLOCKER-3) · `bFreeze` 잔류 · `ClickBox` NoCollision 잔류 · ATK_DOWN 영구 잔류(TE2 누락) · MOCK 값 복원(Def/Hp/bAlive)
- **무한 루프**: 전원 기절(E5, N05) · 무한 기절 락(G1+G2 — 스킵도 반드시 −1이라는 불변식이 TE2에 의존, H-3) · 스킵 체인의 스택(각 반복이 `Delay(0.35)`를 통과하므로 스택 누적 없음 — **검토 후 통과**) · 시체만 남은 큐(BLOCKER-1이 유발하는 소프트락)
- **무증상 실패(silent)**: bBattleOver 미세팅 → 전투가 안 끝나는데 **에러 0**(BLOCKER-1) · bFreeze `declaring_class` 누락 → **무음 실패**(BLOCKER-5) · exec 절단으로 킬링블로우 로그만 증발(H-6) · TurnCounter 오증가 → **F8/F9에서야 터짐**(H-1) · BattleFinished payload 반전 → **A6에서야 터짐**(BLOCKER-2) · TS3 미구현 → **F7에서야 터짐**(BLOCKER-4)
- **명세-구현 불일치**: plan L382(반대 팀 카운트) vs 종료 조건 · plan §5-2(WinningTeam=승자) vs §5-4(payload=패자) · 상태이상_확정 §5-1("TS3 기존 불변") vs plan §F7-4(F7 소관) vs F4 실적(미구현) · plan TC-F5-01 판정방법("로그(상태전이)") vs 실제 로그 부재 · plan §15-3 InitBattle 리셋 목록 vs F5가 새로 만드는 상태들
- **오버플로**: `TurnCounter`(int32, 실플레이 도달 불가) · `BattleState`(Byte, 6 ≪ 255) · `Hp`(int32, 최대 132) → **전 축 해당 없음**(검토 후 통과)

---

## ⑩ verifier 실행 순서 규칙 (상태 오염 방지 — 위반 시 위양성)

1. **TC-F5-N00**(선결 실측 4종) — 노드 1개도 만들기 전.
2. **무회귀 기반선**(N25) — F5 착수 직후 1회(F4 정상 턴 로그와 바이트 대조).
3. **정적 TC 전부**(N01/N02/N06/N10/N11/N12/N16/N17/N19/N20/N21) — PIE 불필요, 컴파일만.
4. **런타임 기본 경로**: TC-F5-02/03/04 · N03/N04(사망 스킵·큐 순회) → **사망 상태를 남기지 않으려면 매 시나리오 후 PIE 재시작.**
5. **상태이상 TC**(SE02/03/06/07/09/10 · QA13/14 · N05/N07/N08/N09): ATK_DOWN이 붙은 채로 데미지 TC를 돌리면 정답지가 어긋난다(`20 ≠ 30`) → **각 시나리오 사이 PIE 재시작 필수**([[F4_TC]] M-4/N25와 동일 규칙).
6. **End TC**(TC-F5-01/05/10/11 · N13/N14/N18/N22/N23/N24) — **맨 마지막**. `InitBattle` 재호출 TC(N18)는 **반드시 End 도달 후**(전투 중 호출 시 in-flight Delay와 이중 구동, M-8).
7. MOCK으로 바꾼 값(`Hp`/`Def`/`bAlive`/`bBlockActive`/`DebugForceEffectChance`/SkillId 핀)은 **TC 종료 즉시 복원 + 복원 실증**(PIE 재조회).

---

## 관련 문서
[[plan]] · [[상태이상_확정]] · [[F4_TC]] · [[F4_중단_인수인계]] · [[E2_상태머신]] · [[전투로그]] · [[W2_Executing개편]] · [[광폭화_재검증]] · [[스탯_전투공식_v1]] · [[U단계_TC]] · [[언리얼_MCP_실전노하우]] · [[개발_워크플로우]]
