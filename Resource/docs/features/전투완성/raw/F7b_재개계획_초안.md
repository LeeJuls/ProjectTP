---
type: plan_draft
project: projectTP
feature: 전투완성 → 캐릭터시스템 인프라
status: 초안 — S4 오너 착수 승인 + 에이전트 피드백 라운드(gameplay·qa) 선행 필수
created: 2026-07-17
supersedes: "[[F7b_인터프리터_진행상황_인계]] §3 (청크 실측 재산정 반영)"
basis: gameplay 라이브 실측(2026-07-17) + qa A1 판정 + MVP 가이드 §2.2/§3.4/§3.5
---

# F7b 재개 계획 (초안)

> **위치 재정의**: F7b는 A1의 짐이 아니라 **A2의 인프라**다. additive-only 병존으로 인라인 F7a 판정이 여전히 작동 중(gameplay 재확인 2026-07-17 — `EnterExecuting`이 구식 `ResolveHit` 직접 호출, 4함수 노드수 골격 세션과 정확히 일치·무접촉). 1000조합 30원자 모델(balance#1 결재 후)이 이 인터프리터 위에 올라간다.

## 착수 전제 (순서 고정 — 가이드 §2.2·§3.1)

1. **SPD 오라클 원장 봉인 선행** (오너 S1) — 기준선 없이 `BP_BattleManager` 수술 금지
2. **오너 S4 착수 승인**
3. 이 초안에 대한 **gameplay·qa 피드백 라운드** → upgrade → 착수

## 청크 재산정 (2026-07-17 라이브 실측 기준)

| 청크 | 내용 | 실측·정정 | 위험 |
|---|---|---|---|
| ④ | 애플리케이터 실연결 (`ApplyEffectEntry` 18노드 STUB → DAMAGE/HEAL/STATUS 실배선) | STUB 확인(ResolveHit 호출 0건). **`ResolveHit` 169노드**(인계문서 149 + 파트4 힐표시 6 + **미상 14**) | **최고** |
| ⑤ | 쿨다운 게이트/세팅·BattleLog 방출을 캐스트 레벨로 | 미착수 확인 | 중 |
| ⑥ | `"STUN"`/`"ATK_DOWN"` 리터럴 → `LookupChannel` 제네릭화 | 2곳 확인(`GetOutgoingAtkMult`·`EnterTurnStart`) | 저 |
| ⑦ | `EnterExecuting` 재배선 (`ResolveHit`→`ApplySkillEffects`) | **정정: "1노드 스왑" 아님** — `Target`(단일)→`SelectedTargets`(배열) 타입 불일치, `GetSelectedTargets` 신규 배선 + `Attacker`→`Caster` 확인 | **최대 회귀 표면** |
| ⑧ | 프루브 2종 E2E + 5스킬 회귀 | 데이터 완비 확인(`DT_SkillEffects` 10행·`DT_StatusEffects` 6행) | 중 |
| ⑨ | Category 탭 (F7a 이월) | 미착수 확인 | 저 |
| ⑩ | 구 `Effect*` 컬럼 제거 + 스캐폴드 원복(`Hp`·`TurnCounter`) | 구/신 컬럼 병존 확인 | 저 |

### 🚨 ④ 필수 조항 — 파트4 힐 표시 포팅 (신규, 인계문서에 없음)

인계문서 §8-5의 수술 계획(step2 HEAL 숏컷 삭제→`ApplyEffectEntry` HEAL 케이스 이관)은 **파트4(2026-07-17) 이전에 작성**돼 힐 표시 로직의 존재를 모른다. step2 꼬리에 파트4가 심은 6노드가 산다:
`VariableSet_5(SetHpBefore)` → `SetHp` → … → `PromotableOperator_20(Hp재조회−HpBefore)` → `PromotableOperator_21(0−Delta)` → `CallFunction_4(SpawnDamageNumber#2)`
**조항 없이 §8-5 원문대로 수술하면 "힐 +N 초록" 기능이 조용히 삭제된다** (gameplay CONFIRMED). → ④ 지시서에 **"HEAL 이관 시 HpBefore 캡처·적용델타 계산·SpawnDamageNumber 호출을 새 HEAL 케이스로 함께 포팅 + 이관 후 만피 힐 `+0` 초록 회귀 확인"**을 명문화한다.

### ④ 선행 대사 — ResolveHit +14노드 출처 확정

169−149=20 중 파트4分 6노드만 특정됨. **수술 전 `_savepoints/F7b_인터프리터골격/` 백업과 그래프 대조**로 잔여 +14의 출처(측정 방식 차이인지 실제 추가인지)를 확정한다. 미확정 노드가 있는 채로 삭제 수술 금지.

## 로그 스키마 확정안 (§8-9 미결 해소)

MVP 가이드 §3.4 권장 필드를 채택한다:
```
runId · turn · state · attacker · skillId · targets · effect · damageOrHeal
· hpBefore · hpAfter · statusApplied · died · winner
확률 효과: randomSeed · roll · chance · result
```
- **기록 레벨**: 캐스트 요약은 `ApplySkillEffects`(⑤에서 이동), **엔트리별 roll은 `ApplyEffectEntry`**(STATUS 엔트리마다 `effect=`/`effectRoll=`/`effectApplied=`) — 인계문서 §8-9의 미결을 "엔트리 레벨"로 확정 제안
- `hpBefore`는 파트4가 힐 경로에 이미 도입한 로컬변수 패턴과 정합 — DAMAGE 경로에도 동일 패턴 확장
- 기존 원장 파서(`extract_battle_log.py`)와의 하위 호환: 기존 필드명 유지, 신규 필드는 append (파서 회귀 방지)
- 결정론: 같은 seed+데이터 → 같은 로그 (가이드 §3.4)

## Method A — 자동 시나리오 스캐폴드 (회귀 인프라)

- **구축 시점**: SPD 오라클 원장 봉인(S1) **후**, F7b ④ 착수 **전** — 회귀를 사람 클릭 없이 반복하기 위한 도구를 먼저 세운다
- **구조**: `EnterAwaitCommand`/`EnterAwaitTarget` 말단에 `bAutoScenarioActive`(기본 false) 분기 → `NotifySkillSelected(SkillId)`/`NotifyUnitClicked(Unit)` 직접 호출 (~20-40노드). `EnterExecuting`·`ResolveHit`·`EventGraph` 무접촉 — 실제 판정 게이트(쿨다운·타겟풀)를 그대로 통과하므로 우회 없음
- **도구 검증**: 스캐폴드 재생 원장 ↔ 오너 수동 원장(S1) **전 행 diff 0** → 도구 정본화. 이후 F7b ⑧ 회귀·A2 회귀 스위트를 이 도구로 실행
- **원복**: ⑩에서 `Hp`·`TurnCounter`와 함께 스캐폴드 일괄 원복 여부 판정 (재사용 가치 평가 후)

## 게이트 설계 (영구 교정 포함)

- 청크별 게이트: GRAPH(핀 원문) → 컴파일 0 → PIE 스팟 → **회귀 = 오라클-diff 전 행** (★관측-봉인 금지 — qa Critical. 사망턴·승자·최종HP 일치는 PASS 근거 아님)
- ⑦은 **단독 커밋·단독 게이트** (인계문서 원칙 유지 — 최대 회귀 표면)
- 각 청크 전 uasset `_savepoints/` 백업 + manifest (SP1 절차 계승)

## 제안 순서

```
[S1 원장 봉인] → Method A 구축·검증 → ⑥(저위험) → ⑤ → ④(+힐표시 포팅·+14 대사) → ⑦(단독) → ⑧(Method A로 회귀) → ⑨ → ⑩(+스캐폴드 원복 판정)
```
인계문서 원순서(④부터)와 다름: 저위험 청크로 도구·리듬을 먼저 세우고 최고위험 ④를 중반에 — **피드백 라운드에서 gameplay가 재판정할 것**.

## A2 연계

- balance#1(S3 결재) → 30원자 카탈로그가 `DT_Skills`/`DT_SkillEffects`에 올라감 → 인터프리터가 실행 기반
- AoE M1(ENEMY_ALL/ALLY_ALL 실행분기)은 A2 이월 유지 — F7b 범위 아님
