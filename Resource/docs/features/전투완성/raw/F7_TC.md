---
type: qa
project: projectTP
feature: 전투완성
stage: F7
status: TC 확정 — Director BLOCKER 5건 게이트 판정 반영. 착수 대기(F6 게이트 통과가 선행). TC 실행=verifier, 게이트 판정=Director
updated: 2026-07-15
---

# F7(스킬 시스템 — 레고 조립식 3층) — 적대적 검토 + 단계별 TC

> 대상: [[plan]] §F7 · [[상태이상_확정]](δ틱·step4/6 채널·step8.5·ResolveTargetPool·E1~E16·검증훅 SSOT) · [[스탯_전투공식_v1]] §5(정답지)·§8(계약) · [[상태이상_카탈로그_밸런스]] §8-4(TC 시드) · [[F4_TC]](BLOCKER5/HIGH8 계승) · [[F5-2_TC]](TC 스타일·판정법 계승)
> **qa-critic 적대적 검토 산출물 — 검출·TC설계만.** TC 실행=verifier, 게이트 판정=Director. **본 문서는 Director가 BLOCKER 5건에 내린 판정을 정답지로 못박은 확정판이다.**
> **핵심 전제**: F4/F5/F5-2가 라이브 → F7은 **밸런스-크리티컬 라이브 코드의 리팩터**(그린필드 아님). 회귀 원장(23턴 even-trade)·데미지 셀은 보존해야 할 라이브 자산.
#projectTP/전투완성

---

## 0. 범위 & 2단계 분할 (Director 스코프 확정)

F7은 **2단계**로 쪼갠다. TC 표의 `[단계]` 컬럼이 이를 분류한다.

| 단계 | 범위 | 인터프리터 수술 |
|---|---|---|
| **F7a**(야간) | 스킬 **메뉴**(WBP_BattleHUD/SkillMenu) + `PendingSkillId` 배선 + **기존 인라인 판정 무접촉** | **없음** — 5원본 스킬을 메뉴→PendingSkillId→기존 TakeHit로 라우팅 |
| **F7b**(아침) | **인터프리터 수술** — 3층 DT + ApplySkillEffects(3-패스 버킷) + ResolveHit 시그니처 변경 + LookupChannel 제네릭화 + 부호 원자전환 | **전면** |

- F7a 검증 가능: **G01·U01·U02·U04·E02**. 나머지 대부분 F7b.
- **판정도구 약칭**: **GRAPH**=정적 노드조회(`find_nodes`·`get_connected_subgraph`·`get_node_infos`) / **LOG**=`projectTP.log` grep(또는 `GetLogEntries`) / **PIE**=인스턴스 프로퍼티(`get_properties`, `UEDPIE_0`) / **SCF**=스캐폴드 직접호출 후 LOG/PIE / **DT**=`get_rows` / **CSV**=`data/*.csv` 대조 / **CMP**=컴파일0(`warnings_as_errors=true`) / **MOCK**=값주입 후 LOG/PIE. **★**=게이트(진행차단). **[N]**=본 검토 신규.

---

## 1. Director BLOCKER 판정 → 정답지 반영 (재론 금지)

아래 5건은 Director가 게이트 판정을 완료했다. 본 TC의 정답지는 이 판정을 인코딩한다.

| # | 판정 | TC 반영 |
|---|---|---|
| **BL-1** EvaluateCondition | 공란/ALWAYS = **선행 명시 분기**로 `(true,1.0)` 반환(switch default **도달 불가** 구조가 계약). 미지 Property/Op = **로그+엔트리 스킵**(fail-closed) | F7-C01(선행분기 실재+basic 30) · F7-C05(스킵 확정) |
| **BL-2** 부호규약 | **원자 전환** + F7-N01 게이트 그대로. step4(OUT_MULT)만 `(1+value)`, step6 막기는 레거시 `(1−BlockValue)` 유지 | F7-N01 · F7-R04/R05 · F7-B03 |
| **BL-3** ResolveHit 계약 | 시그니처 = **`(Attacker,Target,DamageCoeff)`**(DT조회 제거, `DamageCoeff=Value×CondMult` 수취). 쿨다운 게이트·세팅 + BattleLog 방출 = **ApplySkillEffects 캐스트레벨(캐스트당 1회)**. 캐스트당 BattleLog 1줄(block/heal도 라인 생성) — **정확 필드 스키마는 F7b 착수 시 Director-qa 합의 확정** | F7-R01/R07 · F7-L01(스키마 확정 선행) |
| **BL-4** 채널 디스패치 | **CONFIRMED**(gameplay 실측: GetOutgoingAtkMult·TS4에 `EqualExactly "ATK_DOWN"/"STUN"` 리터럴 실존) → **LookupChannel 제네릭화 F7b 필수** | F7-G02(리터럴 제거 확인) |
| **BL-6/MJ-4** 막기·버프 | **막기 = 레거시 유지**(IN_MULT 채널 알파구현 = ApplyStatus **채널 케이스**가 bBlockActive/BlockValue(=−DefaultValue) 세팅, StatusId 리터럴 0, 해제 TS3 무변경, δ 미편입). **ATK_UP = 캐스트 한정**(dur1·skip없음·PRE 같은턴 step4 반영·자기턴종료 만료). **skip 마커 미도입**(δ 무분기 불변 유지). **F_ActiveStatus 완전 무변경**(bSkipNextDecrement 제외) | F7-S01(막기 레거시) · F7-S02(ATK_UP 캐스트한정) · F7-S03/S04(δ 무분기) · F7-B01 |

**MJ 부수 판정**: MJ-2 = **3-패스 버킷**(PRE→ON→POST pass별 ForEach+EqualExactly, 정렬노드 불사용) → F7-T01. MJ-7 = **RowName `_N` 오름차순 저작 규약**(DAMAGE<STATUS) V-rule → F7-K03(DT 검증). MJ-6 = mult step4 곱 **내부** 확정 → F7-C04. MD-5 = ApplySkillEffects **1회 호출** → F7-K05. **컨벤션**: `HP_PCT=0~100 정수`, 공란/ALWAYS=무조건.

---

## 2. 발견 목록 요약 (심각도순 — §1 판정으로 정답지 확정됨)

### BLOCKER (판정 완료 — 정답지 반영)
- **BL-1** EvaluateCondition 무Cond/default가 `(true,1.0)` 아니면 **전 기본공격 0딜/스킵**(진행불가). → 선행분기+fail-closed 확정.
- **BL-2** 부호 반쪽 마이그레이션 → ATK_DOWN/ATK_UP **정반대 증폭**(silent·balance-fatal). → 원자전환+N01 게이트.
- **BL-3** ResolveHit이 per-entry에 쿨다운/로그/PowerRate를 품으면 **block/heal 영구쿨0=힐스톨 회귀·다중타 자기차단·무DAMAGE 로그유실**. → 캐스트레벨 승격.
- **BL-4** GetStatMult가 토큰리터럴 필터면 **ATK_UP 무음드롭 + 초점1 위반**. → LookupChannel 제네릭.
- **BL-6** SELF_BUFF δ 즉시만료 + δ무분기 충돌. → 막기 레거시·ATK_UP 캐스트한정·skip 미도입.

### MAJOR
- **MJ-2** 엔트리 처리순서 미보장 → PRE 밀림. → 3-패스 버킷.
- **MJ-5** F_SkillsRow 재편+재임포트 광역회귀(MotionRow/dangling/제거컬럼 리더/DT_JobStats 불가침). → F7-R06/R07.
- **MJ-6** Cond MULT 삽입점이 step4 밖이면 정답지 상이·Def/block 오작용. → step4 내부.
- **MJ-7** within-ON DAMAGE→STATUS 미보장 → 라이더가 미격대상 롤·감사왜곡. → RowName V-rule.

### MEDIUM
- **MD-1** 킬링블로우 `effectRoll=-1` sentinel 유실(silent skip). → F7-K02.
- **MD-2** 무DAMAGE 캐스트 로그유실+턴당 라인수 불변식 재정의. → F7-L01.
- **MD-3** SELF 스킬 AwaitTarget 진입 시 hang. → F7-U01.
- **MD-4** STUB/미지 default가 라이브 미도달 → 폴백 자체 미실증(잠재 크래시). → F7-Z01.
- **MD-6** 0엔트리 SkillId 무음 whiff. **MD-7** StatusEffectId FK dangling 크래시. → F7-B04.

### MINOR/엣지
- HitCount 0=무피해(F7-E01) · HP_PCT 경계/0나눗셈(F7-C06) · TickTiming 정합(F7-B01) · Cost 무소비(F7-E02) · Category orphan(F7-U02) · 혼합타겟/DoT STUB(이월).

---

## 3. TC 표 (단계별)

### G. SkillId/StatusId 리터럴 분기 0 (초점1)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7a | **G01**★ | 메뉴 처리경로(WBP_BattleHUD/SkillMenu)에서 `Equal/NotEqual(Int\|Str\|Byte)`·`Switch`·`Select` 중 한 피연산자가 **구체 SkillId 리터럴**(7종 id/RowName/문자열)인 노드 **0개**. 슬롯→`PendingSkillId` 라우팅은 Category/PrimaryTargetGroup 데이터 구동. 허용예외=명명 폴백멤버 Get | GRAPH | 대기 |
| F7b | **G02**★ | **LookupChannel 제네릭화(BL-4)**: GetOutgoingAtkMult·step6·TS4·ApplyStatus·TickStatuses에서 `EqualExactly(statusToken, "STUN\|ATK_DOWN\|ATK_UP\|DMG_REDUCE")` 리터럴 **0개** — 채널분기는 `DT_StatusEffects[token].Channel` 조회. (실측상 현재 리터럴 실존 → 제거 확인) | GRAPH | 대기 |
| F7b | **G03** | 존재하는 전 Switch/Branch 선택자가 **메커닉 enum**(EffectType/Timing/Channel/TargetGroup/ScaleMode/Property/Op/Result)만 — SkillId/StatusId 위 분기 아님. 각 스위치 default 존재 | GRAPH | 대기 |

### T. Timing 순서 — 3-패스 버킷 (초점2·MJ-2)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **T01**★ | **3-패스 구조 실재(MJ-2)**: ApplySkillEffects가 `Timing EqualExactly PRE→ON→POST` **3개 ForEach 버킷**으로 순회(**정렬노드 불사용**). 각 패스 내 순회=RowName 순 | GRAPH | 대기 |
| F7b | **T02**★ | **PRE→ON 같은캐스트 반영**: buff-then-attack 확정시전 → PRE ATK_UP이 ActiveStatuses에 먼저 → ON DAMAGE step4가 증가Atk 조회. `base=floor(Atk×(1+ATK_UP)×DamageCoeff×Berserk)` 손계산 일치 | SCF+LOG | 대기 |
| F7b | **T03** | PRE ApplyStatus에 latent(Delay) 0개 — ON의 채널조회 전 write 동기완료 | GRAPH | 대기 |

### C. Condition 평가 (초점3·BL-1·MJ-6)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **C01**★ | **[CRITICAL] 무Cond 선행분기(BL-1)**: EvaluateCondition에 공란/ALWAYS를 `(apply=true,mult=1.0)`로 반환하는 **선행 명시 Branch**(switch default **이전**) 실재. 런타임 basic dmg=**30**(0/1 아님). **switch default 도달불가 구조가 계약** | GRAPH+LOG | 대기 |
| F7b | **C02** | GATE-false 엔트리(스캐폴드) → 그 엔트리 무적용 + 크래시0 + 타 엔트리 정상 진행 | SCF+LOG | 대기 |
| F7b | **C03**★ | **MULT(집중일격)**: 대상 HP_PCT≥50 → mult=2.0(dmg 2배), <50 → mult=1.0. **경계 정확 50 → ×2(≥ 포함)**. `dmg(HP≥50) = 2×base − Def` 관계·경계·단일floor 확인(Value 미확정 → 관계로 판정) | MOCK+SCF+LOG | 대기 |
| F7b | **C04** | **mult 삽입점(MJ-6)**: `DamageCoeff=Value×CondMult`가 step4 곱(Atk×OutMult×DamageCoeff×Berserk, **단일floor·Def 이전**)에 진입. Def후/floor후 별도곱 아님 | GRAPH+LOG | 대기 |
| F7b | **C05** | **미지 Property/Op 폴백(BL-1)**: 스캐폴드 Cond.Property=RACE(STUB)/Op=미지 → **로그+엔트리 스킵**(fail-closed 확정) + 크래시0. 통과 아님 | SCF+LOG | 대기 |
| F7b | **C06** | HP_PCT 엣지: `HP_PCT=0~100 정수`, MaxHp>0(0나눗셈0), **현재HP(엔트리 데미지 적용 전)** 사용, Subject=TARGET인데 무타겟(SELF)엔트리 → 폴백 | GRAPH+SCF | 대기 |

### D. Chance 롤 결정론 (초점4)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **D01**★ | **DebugForceEffectChance 재사용**: sentinel −1=엔트리Chance, ≥0=**전엔트리 오버라이드**(**per-entry 롤지점**에서 읽음, 스킬당 1회 아님). =0→STATUS APPLY 0줄, =1→프루브 전 APPLY | GRAPH+SCF+LOG | 대기 |
| F7b | **D02** | effectRoll 사후감사: 실확률 1판에서 STATUS 엔트리별 `(roll<Chance)⇔applied`. `effectRoll=-1` 라인 감사제외. 다중 STATUS 엔트리는 엔트리별 roll 기록 존재 | LOG | 대기 |
| F7b | **D03** | 롤방향/경계: `roll≥Chance` 미적용(roll<Chance만). force=1→항상적용·force=0→항상미적용 | SCF+LOG | 대기 |

### R. 회귀 불변 (초점5·BL-3)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **R01**★ | **데미지 셀 바이트동일**: `DebugForceEffectChance=0`, 5원본 재표현 후 SCF 셀 — basic **30/34**·slash **42/46**·fireball **61/65**·block피해 **61→30**·heal **+33**. (41=single정밀도/30=int절삭 원인분리 계승). ResolveHit 시그니처 `(Attacker,Target,DamageCoeff)` 경유 | SCF+LOG | 대기 |
| F7b | **R02**★ | **23턴 원장 불변**: 기본공격 스캐폴드 완주 → B1†T5·A1†T6·…·B4†T23, A4승. F9a 원장 **diff=0** | LOG | 대기 |
| F7b | **R03**★ | **heal 미스케일**: ATK_DOWN 걸린 마법사 heal = **33 불변**(HEAL 애플리케이터 OUT_MULT 미경유) | SCF+LOG | 대기 |
| F7b | **R04**★ | **block 부호(레거시)**: 막기 활성대상 피격 ×0.5(파볼 61→30). step6 레거시 `(1−BlockValue)`, `BlockValue=−DefaultValue`(−0.5→+0.5). **91이면 부호미스** | SCF+LOG | 대기 |
| F7b | **R05** | **ATK_DOWN 부호·δ**: OUT_MULT `(1+(−0.25))=0.75` 약화매트릭스(전사basic 30→20·파볼 61→43) + dur=2 약화행동 2회(remaining 2→1→0). **1.25 증폭이면 부호미스** | SCF+LOG+PIE | 대기 |
| F7b | **R06** | **F6 모션 무회귀(MJ-5)**: F_SkillsRow 재편·재임포트 후 PlayAttack MotionRow 조회 정상(ATK1 delay 0.70) + DT_Skills dangling 0 | GRAPH+LOG | 대기 |
| F7b | **R07**★ | **캐스트레벨 승격+리더 갱신(BL-3/MJ-5)**: 쿨다운 게이트·세팅+BattleLog가 **ApplySkillEffects 캐스트레벨**(ResolveHit 내부 아님). 舊 EffectType/PowerRate/EffectChance/Value/Duration Get 잔존 0. 컴파일0. **DT_JobStats/DT_Motions 미재임포트**(8기 스탯 불변) | GRAPH+CMP+PIE | 대기 |

### K. 사망 라우팅 (초점6·MJ-7)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **K01**★ | **per-entry bAlive**: DAMAGE가 대상 kill → 후속 ON/POST 엔트리 `ForEach(bAlive)`가 시체 제외(STATUS APPLY 0) | GRAPH+SCF+LOG | 대기 |
| F7b | **K02**★ | **킬링블로우 sentinel(MD-1)**: DAMAGE가 죽인 대상 → STATUS 엔트리 스킵 시 **`effectRoll=-1` 기록 유지**(silent skip 금지) + ActiveStatuses Clear(시체 상태0). 이것이 DAMAGE→STATUS 순서의 런타임 증거 | SCF+MOCK+LOG+PIE | 대기 |
| F7b | **K03** | **within-ON 순서 V-rule(MJ-7)**: slash/fireball 엔트리 RowName `_N` 오름차순에서 **DAMAGE `_N` < STATUS `_N`**(라이더가 타격 후). DT 저작규약 검증 | DT | 대기 |
| 이월 | **K04** | [A2] AoE 죽음라우팅: ENEMY_ALL DAMAGE 일부 kill → 후속 STATUS 재해석 생존자만. 알파 STUB(데이터0) | 이월 | 이월 |
| F7b | **K05** | **단일 호출(MD-5)**: EnterExecuting이 `ApplySkillEffects(Caster,SkillId,SelectedTargets[])` **1회** 호출 — 舊 outer ForEach 이중루프 아님(A2 N² 방지) | GRAPH | 대기 |

### S. SELF_BUFF·막기 (초점7·BL-6)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **S01**★ | **막기 레거시 회귀(BL-6)**: block 시전 → `bBlockActive=true`(ApplyStatus IN_MULT 채널케이스, StatusId 리터럴0) → 상대턴 피격 ×0.5(파볼 61→30) → **자기 다음턴 TS3 해제**(기존 H1 그대로, δ 미편입). ActiveStatuses에 block 엔트리 **부재** | SCF+LOG+PIE | 대기 |
| F7b | **S02**★ | **ATK_UP 캐스트한정(BL-6)**: buff-then-attack ATK_UP = dur1·**skip없음**·PRE→같은턴 step4 반영→자기턴종료 TE2 만료. **캐스터 다음 자기턴 basic공격 = 미증폭(정상딜)이 정답**. StatusLog APPLY(turn T)+EXPIRE(turn T) | SCF+LOG+PIE | 대기 |
| F7b | **S03** | **skip 마커 미도입(BL-6)**: TickStatusesAtTurnEnd에 "부여턴?" 분기·`bSkipNextDecrement` 필드 **0개**(δ 무분기 불변 유지). ON_HIT(STUN/ATK_DOWN, 상대턴 부여)는 피해자 자기턴 정상차감 | GRAPH+SCF | 대기 |
| F7b | **S04** | **δ 무분기 회귀**: STUN(1스킵후 만료)·ATK_DOWN(2행동)·E15 복합상태(STUN+ATK_DOWN 동시) 전부 회귀0 | SCF+LOG | 대기 |

### B. 부트스트랩 정합 (초점8)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **B01** | **struct 2종 실측 + F_ActiveStatus 무변경**: F_SkillEffectRow(SkillId·Timing·Order·TargetGroup·EffectType·ScaleMode·Value·StatusEffectId·Chance·Cond{Subject·Property·Op·Value·Result·Mult}) + F_StatusEffectRow(StatusId·Channel·StatTarget·DefaultValue·DefaultDuration·TickTiming·StackPolicy…). **F_ActiveStatus = statusToken/value/remainingTurns만**(bSkipNextDecrement 신규필드 **부재**) | MCP list_properties | 대기 |
| F7b | **B02** | DT_SkillEffects RowName=엔트리별 유니크(SkillId 컬럼 필터조회), 조회=GetRowNames→ForEach→match | DT+GRAPH | 대기 |
| F7b | **B03**★ | **부호 원자전환(BL-2)**: F_ActiveStatus.value가 OUT_MULT 상태에 **부호포함** 저장(ATK_DOWN −0.25/ATK_UP +0.5) + step4 리더 `Π(1+value)`. 舊 `(1−value)` 리더 잔존 0. (막기는 δ 미편입이라 value 무관) | MCP+GRAPH | 대기 |
| F7b | **B04**★ | **V-rule 데이터검증**: (a)전 castable SkillId ≥1 엔트리(0=무음 whiff) (b)STATUS StatusEffectId ∈ DT_StatusEffects(dangling FK 0) (c)ON_HIT Chance∈(0,1] (d)DAMAGE ScaleMode=ATK·Value>0 (e)토큰 발급목록내 (f)RowName `_N` 오름차순 DAMAGE<STATUS | DT+CSV | 대기 |
| F7b | **B05** | DT_Skills 컬럼: MotionRow(F6)/CooldownTurns/Category/PrimaryTargetGroup 실재. **PowerRate 이설**(엔트리 Value로) — DT_Skills.PowerRate 제거 확인 + ResolveHit이 DamageCoeff 인자수취(DT 재조회 노드 0) | DT+GRAPH | 대기 |

### Z. 死코드/폴백 가드 (초점9)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **Z01**★ | **STUB default 실증(MD-4/MD-7)**: 스캐폴드 데이터로 Channel=DOT·TargetGroup=ENEMY_ALL·ScaleMode/EffectType 미지·StatusEffectId 부재 각1회 → **로그+무효과+크래시/Accessed None 0**. 폴백 핸들러 자체를 실증 | SCF+LOG | 대기 |
| F7b | **Z02** | 死코드0(라이브): 라이브 데이터 STUB토큰 0건, default=방어용 단일핸들러(per-token 死분기 아님) | DT+GRAPH | 대기 |
| F7b | **Z03** | 무한루프/재귀0: ApplySkillEffects·EvaluateCondition·ResolveEntryTargets 자기재귀0 · ResolveHit↔ApplySkillEffects 동명재귀0(BLOCKER-5 계승, 개명 유지) + PIE 1턴 완주 | GRAPH+PIE | 대기 |

### N. 부호규약 수치동일 (초점10·BL-2)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **N01**★ | **부호통일 수치불변**: block ×0.5(파볼61→30)·ATK_DOWN 최종×0.75(약화매트릭스 전 셀)이 舊 결과와 **바이트동일**. **step4 OUT_MULT 데이터부호(−0.25)+공식(1+value)**, **step6 막기 레거시(1−BlockValue, BlockValue=−DefaultValue)** 둘 다 확인. step4 한쪽만 바뀌면 ATK_DOWN×1.25 증폭 | SCF+LOG | 대기 |

### U. 메뉴·실행흐름 (초점4·F7a 주력)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7a | **U01**★ | **SELF 즉시실행(MD-3)**: block/SELF PrimaryTargetGroup 슬롯 → NotifySkillSelected → **AwaitTarget 미진입, 즉시 Executing**(SelectedTargets=[caster]). 클릭 대기 hang 0 | GRAPH+PIE | 대기 |
| F7a | **U02** | 메뉴 동적행: Category 탭 필터 → 슬롯 라벨 **DT_Strings(NameKey)**(하드코딩0) + 쿨다운 스킬 bEnabled=false + orphan Category 스킬 처리(숨김/폴백) | GRAPH+PIE | 대기 |
| F7a | **U04**★ | **메뉴 5스킬 라우팅 무회귀**: 메뉴에서 basic/slash/fireball/block/heal 선택 → `PendingSkillId` 세팅 → **기존 인라인 TakeHit** 경유 → 데미지 무변화(basic 30·slash 42·파볼 61·block피해 30·heal +33). F7a는 인터프리터 무접촉 | SCF+LOG | 대기 |
| 비주얼 | **U03** | [불차단] 메뉴 4카테고리 사용감·막기 포즈·스킬 연출 — 오너 육안(아침) | 오너육안 | 대기 |

### L. 로그 (초점4·BL-3)

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **L01**★ | **캐스트당 로그 완전성(BL-3)**: block/heal(무DAMAGE)도 원장 라인 생성(캐스트당 BattleLog 1줄 원칙) → 행동 재구성 가능. **정확 필드 스키마는 F7b 착수 시 Director-qa 합의 확정이 선행**(본 TC는 스키마 확정 후 실행). 턴당 라인수 불변식 정의 | LOG | 대기 |
| F7b | **L02** | StatusLog 신규: ATK_UP APPLY/EXPIRE 방출(별도 grep, `extract_battle_log.py` 미수정) | LOG | 대기 |

### E. 기타 엣지

| 단계 | ID | 조건 → 기대 | 판정 | 상태 |
|---|---|---|---|---|
| F7b | **E01** | HitCount 미설정/0 → **1 폴백**(0히트=무피해 방지, F6 FrameCount≥1 선례). 알파 전 스킬 HitCount=1 | DT+GRAPH | 대기 |
| F7a | **E02** | Cost 무소비(MP없음) — Cost 컬럼 미소비, 전 스킬 Cost=0 | DT+GRAPH | 대기 |

---

## 4. 게이트 TC 구체 판정법

| 게이트 | 구체 PASS/FAIL |
|---|---|
| **C01 무Cond 선행분기** | GRAPH: EvaluateCondition에서 공란/ALWAYS→`(true,1.0)` 반환 노드가 **switch 노드보다 exec 상류**. LOG: basic SCF dmg==30. **dmg=1(min1 은폐)이면 default가 mult=0 반환 = FAIL** |
| **N01/R01 부호·셀** | SCF 각 셀 grep: `action=32001000\|dmg=61` 등 정확값 1줄. 막기중 전사에 파볼 → `dmg=30`(91이면 부호미스 FAIL). ATK_DOWN 마법사 basic → `dmg=20`(부호미스면 증폭값) |
| **R02 23턴 원장** | `extract_battle_log.py` 산출물이 F9a 프리즈 원장과 `diff` 0줄. attacker 시퀀스·turn·dmg·hp 전부 일치 |
| **G02 채널 제네릭** | GRAPH: GetOutgoingAtkMult·TS4 서브그래프에 `EqualExactly(_, "ATK_DOWN"\|"STUN")` 리터럴 노드 `grep` 0개. 채널조회 노드(`GetDataTableRow(DT_StatusEffects)`→Channel) 실재 |
| **T02 PRE→ON** | SCF buff-then-attack(DebugForceEffectChance=1) → ON dmg가 `floor(Atk×(1+ATK_UP)×coeff)−Def`. ATK_UP 미반영(그냥 base)이면 FAIL |
| **S02 ATK_UP 캐스트한정** | SCF: buff-then-attack 시전 후 **같은 유닛 2연속 자기턴** basic 공격 관찰 → 1회차(버프캐스트 ON) 증폭 / 2회차(다음 자기턴) **미증폭 정상딜**. 2회차도 증폭이면 leak=FAIL. StatusLog EXPIRE가 캐스트 turn에 존재 |
| **S01 막기 레거시** | SCF block(A1) → 상대(B1) 파볼 A1 타격 → `dmg=30`. A1 다음턴 TS3 후 상대 재파볼 → `dmg=61`(해제 확인). PIE: A1.ActiveStatuses에 block 토큰 부재 + bBlockActive 전이 정상 |
| **K02 킬링블로우** | MOCK B1.Hp=30 → SCF slash(dmg42>30) → `hp=0\|effectRoll=-1\|effectApplied=false` + PIE B1.ActiveStatuses.Length==0. effectRoll 필드 결측이면 sentinel 유실=FAIL |
| **Z01 폴백 실증** | SCF STUB토큰 데이터 각1회 → `grep -c "Accessed None"`==0 + 크래시0 + 해당 엔트리 무효과(대상 상태/HP 불변) + 경고로그 1줄 |
| **U04 메뉴 라우팅** | 메뉴 5스킬 클릭경로 SCF/PIE → PendingSkillId 세팅 → BattleLog 데미지 셀 무변화. F7a에서 인터프리터 노드(ApplySkillEffects) 부재 확인 |

---

## 5. 커버리지 근거 & PLAUSIBLE 플래그

**검토 축(빈손 통과 아님)**: 경계값(HP_PCT 정확50·roll==Chance·floor 41/30·HitCount 0·MaxHp 0나눗셈) · 동시성/순서(3-패스 버킷·PRE→ON 동기·within-ON DAMAGE<STATUS·1회 호출) · null/FK(StatusEffectId dangling·빈 targetpool) · 상태전이/누수(막기 레거시 TS3·ATK_UP 캐스트한정·δ 무분기) · 부호/타입(step4 1+value / step6 1−BlockValue·int×float 절삭) · 무음실패(min1 은폐·토큰필터 드롭·무DAMAGE 로그유실·제거컬럼 리더단절) · 死코드(STUB default 실증) · 회귀(23턴 원장·데미지 셀·F6 모션·DT_JobStats 불가침).

**PLAUSIBLE(통과 아님 — verifier 실측 확정 요망)**:
- **K03 RowName 순회 순서**: `GetRowNames`가 RowName `_N` 오름차순을 **형식적으로 보장하지 않음**(TMap 순회). CSV 임포트가 통상 삽입순 유지라 실무상 성립하나, **K02(킬링블로우 라이더 억제)가 런타임 증거**로 이를 교차확인 — K02 FAIL 시 순회순서 붕괴 의심.
- **L01 로그 스키마**: 캐스트당 1줄 원칙은 확정이나 **정확 필드 셋이 미확정**(F7b 착수 시 Director-qa 합의 선행). 그 전엔 L01 실행 불가(스키마 확정이 게이트 선행조건).
- **S02 ATK_UP 수명**: dur1·skip없음으로 캐스트한정 확정됨(Director). Value(PowerRate) 수치는 balance 미확정 → T02/C03은 **관계식**으로 판정(절대값 아님).

**놓친 버그가 통과된 버그보다 나쁘다** — 위 3건 전부 TC 등재(K02/L01/S02·T02·C03).

---

## 관련
- [[plan]] §F7 · [[상태이상_확정]](δ·채널·step8.5·E1~E16) · [[스탯_전투공식_v1]] §5·§8 · [[상태이상_카탈로그_밸런스]] §8-4
- [[F4_TC]](BLOCKER5/HIGH8 계승) · [[F5_TC]] · [[F5-2_TC]](스타일·판정법 계승) · [[F5-2_완료]](라이브 함수 인벤토리)
- [[언리얼_MCP_실전노하우]] §L130·§23·§26
