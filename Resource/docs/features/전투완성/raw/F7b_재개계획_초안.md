---
type: plan
project: projectTP
feature: 전투완성 → 캐릭터시스템 인프라
status: v2 — gameplay·qa 피드백 반영(Critical 4·High 7 전 수용, 2026-07-18). 오너 S4 착수 승인 완료. 실작업(BP 수술)은 S1 원장 봉인 후
created: 2026-07-17
updated: 2026-07-18
supersedes: "v1(f654a5f) — 게이트 재정의·⑤ additive 명문화·로그 스키마 확정·④⑩ 분할·Method A 정식 청크화"
basis: gameplay 라이브 실측 2회(2026-07-17/18) + qa 적대 검증 2회 + MVP 가이드 §2.2/§3.1/§3.4/§3.5
---

# F7b 재개 계획 v2

> **위치**: F7b는 A1의 짐이 아니라 **A2의 인프라**다(additive-only 병존 — `EnterExecuting`은 지금도 구식 `ResolveHit` 직접 호출, 인터프리터 4함수는 ⑦까지 **어디서도 미호출 = dead code**). 이 사실이 v2 게이트 설계의 출발점이다.

## 착수 전제 (순서 고정)

1. **S1 원장 봉인 선행** — 오너 even-trade 런 ↔ [[SPD원장_오라클_v1]] 전 행 diff 0. 기준선 없이 `BP_BattleManager` 수술 금지
2. ~~오너 S4 착수 승인~~ ✅ 2026-07-18 승인
3. ~~피드백 라운드~~ ✅ gameplay(기술)·qa(논리) 완료 → 본 v2가 그 반영본

## ★게이트 대원칙 (v1에서 재정의 — qa C2)

- **④⑤⑥은 dead code를 만든다** → even-trade 오라클-diff 0은 "옳다"가 아니라 **"라이브를 안 건드렸다"는 음성대조**일 뿐. PASS 근거 아님.
- **④⑤⑥의 정합 검증 = 함수 직접 호출(SCF)** — 비기본값(coeff≠1.0 등)을 관통시켜 실반영 확인(1.0 폴백 은폐 방지).
- **오라클-diff가 유효해지는 최초 지점 = ⑦ 직후, DAMAGE 한정.** HEAL·STATUS·막기·채널은 even-trade가 영원히 못 잡는다 → **5스킬 회귀(30/34·42+STUN·61+ATK_DOWN·막기15·치유−33)를 ⑧이 아니라 ⑦ 게이트에서 즉시 실행**.
- HEAL 회귀는 기계로: **GRAPH**(핀 원문 — 체인 보존+step2 고아 SpawnDamageNumber 0) + **LOG**(MOCK 만피 → hpBefore==hpAfter·적용델타 0). **시각(초록 +0)만 F9b 오너 몫** — 청크마다 오너 호출 불요.

## 로그 스키마 — 확정 (Director 결정, §8-9 미결 해소)

| 항목 | 확정 |
|---|---|
| 필드명 | **라이브 유지**: `action`/`target`/`dmg`/`hp` — 가이드 §3.4는 **개념 참조**로 격하(리터럴 필드명 아님). 신규(`hpBefore` 등)는 **append만** |
| `dmg` 계약 | **RAW**(원시 판정값) — 오버킬 행(T14 dmg=32, hp 26→0)·파트4 치유(`dmg=−33`, 화면은 적용델타) 분리 유지. 적용값으로 바꾸면 오라클-diff가 깨진다 |
| 엔트리별 롤 | **`ApplySkillEffects`가 `EffectLog\|` 별도 라인으로 방출** — 롤은 이미 거기서 소비되므로. **`ApplyEffectEntry` 시그니처 무변경**(gameplay Critical: 현재 파라미터 7개에 Chance/Roll 없음 — 시그니처 확장+3콜사이트 수술을 회피하는 결정) |
| 하위 호환 대상 | `extract_battle_log.py`는 **라인 필터일 뿐 필드 미파싱 = 무위험**(qa 실측). 진짜 정합 대상 = **오라클-diff 비교기(미구축)** + SPD원장 §7 CSV 컬럼 매핑. `EffectLog\|`는 별도 grep(야간⑤ 선례) |
| 선행 | **이 스키마 합의가 ⑤ 착수의 선행조건**(F7_TC L01) — 본 절이 그 합의문. 이의 시 ⑤ 착수 전 재론 |
| 재확인 1건 | §8-6 "무DAMAGE 캐스트 무로그" vs 파트4 치유 `dmg=−33` 실로그 — 착수 시 실로그로 정합 확인(L1) |

## 청크 정의 v2

### [MA] Method A 자동 시나리오 (정식 청크로 편입 — 자체 게이트·세이브포인트)
- **구조**: `EnterAwaitCommand`/`EnterAwaitTarget` 말단 훅 → `NotifySkillSelected`/`NotifyUnitClicked` 직접 호출. ⚠ **둘 다 Function Graph라 Delay(latent) 불가**(gameplay 실측) → 타이밍 필요 시 **EventGraph 신규 커스텀 이벤트 경유**.
- **토글**: `bAutoScenarioActive`(기본 false, **Instance Editable — 광폭화 TurnCounter와 같은 스캐폴드 관례**).
- **시나리오 데이터**: `NotifyUnitClicked`는 액터 레퍼런스 요구 → **슬롯ID/CharName 기반 + 런타임 리졸버 헬퍼**(하드코딩 금지).
- **선행 트레이스**: `NotifySkillSelected`의 SELF 스킵 조건(`EnterAwaitTarget` 미경유 케이스) — 버프후공격 프루브가 걸린다.
- **게이트**: MA-1★ 재생 원장 ↔ 오너 수동 원장 **전 행 diff 0**(≠0이면 **도구 폐기·⑧ 수동 폴백**) / MA-2 `EnterExecuting`·`ResolveHit`·`EventGraph` 노드수 무변(무접촉 증명) / MA-3 기본 false에서 수동 클릭 경로 무회귀. ※ 도구 검증은 기본공격 패턴 한정 — SELF/조건부 프루브 커버는 ⑧에서 별도.

### ⑥ LookupChannel 제네릭화 — ④ 무의존 실측 확인, 선행 OK
게이트: 리터럴("STUN"/"ATK_DOWN") 0개 + **SCF 회귀**(베기 STUN·파볼 ATK_DOWN×0.75 불변 — 오라클 무감각 영역).

### ⑤ 쿨다운·로그 캐스트 레벨 — **additive 명문화** (gameplay·qa 동시 Critical)
- `ApplySkillEffects`(dead code)에 **추가만**. **`ResolveHit`의 인라인 쿨다운·BattleLog 방출은 ⑦까지 유지 — 제거 금지**(제거 시 ⑦ 전까지 라이브 쿨다운·로그 파손).
- 게이트: 무DAMAGE 캐스트도 캐스트당 1줄 불변식 + 인라인 방출 무손실(이중 방출 0 — dead라 자연 충족, ⑦ 후 재확인).

### ④ 애플리케이터 실연결 — **2분할** (gameplay High: STUB엔 적용 로직 자체가 0줄)
- **④a 적용 로직 신설**: DAMAGE→`ResolveHit(Attacker,Target,DamageCoeff)` 재배선(DT 재조회 0·step4~8 보존) / **HEAL 적용 신설**(Def·min1 미경유, MaxHp 클램프 — 현재 어디에도 없음) / STATUS→`ApplyStatus`.
- **④b 파트4 힐 표시 포팅**: `HpBefore`는 **`ResolveHit` 로컬변수라 함수 경계를 못 넘는다 → `ApplyEffectEntry`에 재선언**. pure 재평가(GetHp 이중 평가) exec 순서(SetHpBefore → SetHp → Delta) 정확 재현. 이관 후 step2에 **고아 SpawnDamageNumber 0** 확인. 크로스그래프 동명노드 함정 — **항상 그래프 한정 refPath**.
- **선행 대사**: `ResolveHit` 169 vs 기준 149 — **find_nodes(title="")+get_node_infos 내용 판별**(위치·인덱스로 판단 금지: `PromotableOperator_17/18/19`는 위치상 파트4 인접이나 내용은 **BerserkMult(F8)** — 실증됨). `read_graph_dsl`은 빈 문자열 반환(비신뢰). "149"가 F8 전/후 어느 시점 스냅인지 확인. **미확정 노드 잔존 시 삭제 수술 금지.**
- 게이트: SCF coeff≠1.0 관통(가짜 그린 방지)★ + HEAL GRAPH/LOG 기계 검증★ + 오라클-diff 0(음성대조로만 기록).

### ⑦ EnterExecuting 재배선 — 단독 커밋·단독 게이트 (최대 회귀 표면)
- `Target`(단일)→`SelectedTargets`(배열) 타입 불일치 → `GetSelectedTargets` 신규 배선 + `Attacker`→`Caster` 확인. `ApplySkillEffects` 캐스트당 정확 1회.
- **게이트**: 오라클-diff 전 행(DAMAGE 최초 유효)★ + **5스킬 회귀 즉시**★(HEAL/STATUS 최초 라이브 지점 — ⑧로 미루지 않음).
- **롤백 스톱**: 실패 시 `EnterExecuting→ResolveHit` 원복 — ⑩a 전까지 구컬럼 병존 = 인라인 복구선 생존.

### ⑧ 프루브 E2E — 버프후공격(PRE/ON)·집중일격(HP_PCT≥50 MULT, 경계 50)·ATK_UP 캐스트한정·킬링블로우 + **Method A로 오라클 20행 재생 diff 0**.

### ⑨ Category 탭 — 탭 필터·orphan 폴백·ST_UI 키(하드코딩 0). 시각은 F9b.

### ⑩ **2분할** (qa Critical: 비가역 경계)
- **⑩a Effect\*/PowerRate 구컬럼 제거** — ⚠ **유일 롤백 경로를 자르는 비가역 수술**. **선행 체크리스트**: 전 ★게이트 GREEN + 5스킬 회귀 PASS + 오라클-diff 0 — **하나라도 미결이면 착수 금지(스톱)**. 제거 후 舊리더 잔존 0·컴파일 0·무음 전멸 0.
- **⑩b 스캐폴드 처분** — **기본 = 존치**(Method A·MOCK은 **A2 회귀 스위트가 재사용** — F9a §6 이연 사유 계승, A2 마감 시 처분 재판정). `bAutoScenarioActive=false`·Instance Editable은 쉬핑 무해. **⑩a와 동시 파괴 수술 금지**(가이드 §3.1).

## 실행 순서 (확정)

```
[S1 원장 봉인(오너)] → MA(도구 구축·검증) → ⑥ → ⑤(additive) → ④a→④b → ⑦(단독) → ⑧ → ⑨ → ⑩a → (A2 마감 후 ⑩b)
```

## 세이브포인트 관례 (신설 — 이번 +14 고고학의 재발 방지)

청크별 uasset 백업 = `_savepoints/` + **manifest.txt(SHA256)** + **`find_nodes(title="") 전체 refPath·type_id 텍스트 스냅샷 동봉`** — 다음 세션이 텍스트 diff로 노드 대사 가능(`F7b_인터프리터골격` 백업에 이게 없어서 이번에 고고학이 필요했다).

## A2 연계

- balance#1 결재(2026-07-18 완료)와 **F7b ⑧ 게이트는 무관** — 프루브용 DT(`DT_SkillEffects` 10행·`DT_StatusEffects` 6행)는 이미 완비. 30원자 데이터 반입은 F7b 완료 후 A2에서.
- AoE M1은 A2 이월 유지.

## 부록 — qa TC 골격 (본 TC는 착수 시 qa가 제작)

S1: OR-1★ / MA: MA-1★·2·3 / ⑥: G02★·R-CH★ / ⑤: SCHEMA★(선행)·L01★·DEAD★ / ④: N14★(선행)·HEAL-PORT★·HEAL-DATA·DMG-CORE★·FAKEGREEN★·NEG★ / ⑦: WIRE★·K05★·OR-DMG★·R5★·ROLLBACK / ⑧: T02★·C03★·S02★·K01/02★·OR-FULL★ / ⑨: U02·VIS / ⑩: GATE-ALL★(선행)·COL-RM★·SCAFFOLD★
