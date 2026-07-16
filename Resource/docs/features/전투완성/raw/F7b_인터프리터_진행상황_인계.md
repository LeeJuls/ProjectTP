---
type: raw
project: projectTP
feature: 전투완성
stage: F7b-인터프리터
status: 진행중(골격 완료, 애플리케이터 수술 대기)
updated: 2026-07-16
---

# F7b 인터프리터 진행상황 인계 — 골격 완료, 애플리케이터 수술 대기

> 대상: [[F7_스킬아키텍처_확정]] · [[F7_TC]] · [[F7b_struct부트스트랩_완료]] · [[야간작업_총결산_2026-07-16]]
> F7b 코드층(인터프리터) 작업이 여러 세션에 걸치므로, 다음 세션이 정확히 이어받을 수 있도록 현재 상태·남은 청크·주의사항을 인계하는 문서.
#projectTP/전투완성

---

## 1. 완료 (이번 세션)

- **struct 3종 · 데이터 3층** 완료 — 커밋 `0ca6b71`, 태그 `save/F7b-데이터층`.
- **인터프리터 골격 4함수** 신설 (`BP_BattleManager`, 신규 · 회귀 0 · 컴파일 0 · 핀 원문 검증):

| 함수 | 노드수 | 내용 |
|---|---|---|
| `EvaluateCondition` | 57 | `ALWAYS` 선행분기 · `HP_PCT` GATE/MULT · fail-closed |
| `ResolveEntryTargets` | 16 | `SELF`/`SINGLE_*`/`ALL_*` STUB |
| `ApplyEffectEntry` | 18 | ★`DAMAGE`/`HEAL`/`STATUS` **STUB = 로그만** |
| `ApplySkillEffects` | 118 | `GetDataTableRowNames` + 접두어매칭 수집 · 3패스 버킷 PRE→ON→POST · 엔트리별 조건/확률/애플리케이터 호출 |

- 4함수는 **어디서도 미호출** — `EnterExecuting` 무접촉 = 회귀 0.
- 세이브포인트: `_savepoints/F7b_인터프리터골격/`.

## 2. 툴 제약 발견 (다음 세션 필수 인지 — 노하우 후보)

1. 이 MCP는 `K2Node_GetDataTableRow` · `SwitchOnString` 등 특수 K2Node를 `create_node`로 노출하지 않는다 → `GetDataTableColumnAsString`(컬럼 전체) + `Get`(인덱스) + `MakeStruct` 합성으로 대체(`ResolveHit` 선례와 동일).
2. 심볼릭 연산자(`+`,`-`,`*`,`/`,`<`,`>`,`==`,`>=`)는 `K2Node_PromotableOperator` 생성이 불가 → `InRange(Float)` · named 라이브러리 함수(`SafeDivide`/`NearlyEqual`/`AND`/`OR`/`NOT`)로 대체. 비교는 비율공간(0~1)에서 수행.
3. 배열 `VariableSet` 입력핀 미연결 = 컴파일 에러 → 0요소 `MakeArray`를 명시적으로 연결해야 한다.
4. `is_dirty`가 `save_assets` 성공 후에도 `true`로 보고되는 현상 관측 → uasset mtime 교차검증으로 확인(저장 자체는 정상).

## 3. 남은 청크 (순서 · 위험도)

- **④ [최고위험] 애플리케이터 실연결**: `ApplyEffectEntry`의 `DAMAGE`→`ResolveHit`(=§8 damage core 통짜, `DamageCoeff = Value × Mult` 인자화) · `HEAL`→회복 · `STATUS`→`ApplyStatus`(채널 케이스, 막기=`bBlockActive`). ★[[F7_스킬아키텍처_확정]] §4·§8 준수. `ResolveHit` 수술은 원래 컬럼제거와 동세션 원칙이나, **우리는 additive-only(`Effect*` 병존)라 인라인 F7a 판정이 여전히 작동 중 — 수술 강제성 없음**, 신중히 진행. 가짜GREEN 방어(비기본값 관통 테스트) · 핀 원문 확인 필수.
- **⑤** 쿨다운 게이트/세팅을 `ApplySkillEffects` 최상위로 이동(캐스트당 1회, 멀티히트 자충돌 예방) + `BattleLog` 방출을 캐스트 레벨로.
- **⑥** `TS4` · `GetOutgoingAtkMult`의 `"STUN"`/`"ATK_DOWN"` 리터럴 → `LookupChannel`(`DT_StatusEffects.Channel` 조회)로 제네릭화.
- **⑦** `EnterExecuting` 재배선: `ResolveHit` 콜 → `ApplySkillEffects` 콜(`PendingSkillId`). ★이 시점이 인라인→인터프리터 전환 지점(가장 큰 회귀 표면).
- **⑧** 프루브 2종 E2E(버프후공격=Timing · 집중일격=`HP_PCT` MULT) + 기존 5스킬 정답지 회귀(30/42/61/막기15/힐-33 · 23턴 원장).
- **⑨** Category 탭 (F7a 이월분).
- **⑩** 구 `Effect*` 컬럼 제거(인터프리터 검증 완료 후 최종 단계) + 스캐폴드(`Hp`·`TurnCounter` Instance Editable) 원복.

## 4. 정답지 (회귀 기준)

F7a E2E 실측값 그대로 유지 — 기본 30 · 베기 42+STUN · 파볼 61+ATK_DOWN · 막기 피격 15 · 치유 -33(클램프) · turn40 광폭화 50. **인터프리터 전환 후에도 동일해야 한다.**

---

## 관련
[[F7_스킬아키텍처_확정]] · [[F7_TC]] · [[F7b_struct부트스트랩_완료]] · [[야간작업_총결산_2026-07-16]]
