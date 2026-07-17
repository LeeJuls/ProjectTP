---
type: owner_guide
project: projectTP
scope: mvp_development
status: active
created: 2026-07-17
updated: 2026-07-17
current_gate: Start_P1-R01
current_gate_as_of: 2026-07-17
related_review: "[[Codex_전체_읽기전용_리뷰_2026-07-16]]"
---

# MVP 개발 핵심 운영 가이드

> 관련 전체 리뷰: [[Codex_전체_읽기전용_리뷰_2026-07-16]]
>
> 목적: Claude와 Codex를 활용해 projectTP의 전투 MVP를 빠르게 개발하면서도 변경을 격리하고, 검증하고, 복구할 수 있도록 오너가 지켜야 할 기준을 한곳에 둔다.

### 문서 유지 규칙

- §1과 §3~9는 반복해서 사용하는 운영 원칙이다.
- §2와 §10은 `current_gate_as_of` 시점의 현재 게이트다. 작업 상태가 바뀌면 원본 TC를 먼저 갱신하고 이 두 절을 함께 바꾼다.
- 현재 게이트의 정본은 [[features/전투완성/raw/파트1_Start_TC|파트1 Start TC]]의 `P1-R01`이며, 기대 전투 원장의 정본은 [[features/전투완성/raw/야간F9a_풀회귀_완료|야간 F9a 풀회귀 완료]] §2다. 이 문서는 실행용 요약이며 원본 판정을 대체하지 않는다.

## 1. MVP의 단일 목표

현재 전투 MVP는 기능 수보다 아래 흐름을 반복해서 안정적으로 완주하는 것이 중요하다.

```text
전투 대기
→ Start
→ 턴 시작
→ 스킬 선택
→ 대상 선택
→ 피해·회복·막기
→ 사망 처리
→ 승패 결정
→ End
→ 재시작
```

신규 기능보다 한 판의 정확성, 반복성, 복구 가능성을 우선한다.

## 2. 지금 당장 할 일

### 2.1 Start 기준선 보완

현재 최우선 작업은 Start 완료 주장 상태에서 이월된 `P1-R01`을 실행하는 것이다.

#### 범위와 동결선

- 이 단계는 **검증 전용**이다. F7b와 파트2 SPD를 포함한 모든 프로젝트 에셋 수정을 동결한다.
- Blueprint, DataTable, 설정, 맵을 저장·컴파일·수정하지 않는다. 쓰기가 허용되는 것은 런타임 로그, 비교 결과, 화면 캡처, graph export 사본, 리뷰 문서뿐이다.
- 에디터에 의도하지 않은 dirty asset이 생기면 저장하지 말고 즉시 중단한다. 기존 dirty 상태가 있었다면 오너에게 먼저 보고해 구분한다.
- 프로젝트 안의 기존 증거를 덮어쓰지 않는다. 새 증거 묶음은 `D:\unreal\review_agent\evidence\2026-07-17_Start_P1-R01\` 아래에 보존한다.

#### 고정 입력

1. Start로 전투를 시작한다.
2. 행동 직전 `activeUnit`이 아래 기대 공격자와 같은지 확인한다.
3. 매 유닛턴 스킬 메뉴에서 기본 공격 `31000000`의 **공격**을 선택한다. Slash·Fireball 등 다른 스킬을 고르면 이 TC가 아니다.
4. 살아 있는 적 중 인덱스가 가장 낮은 대상을 선택한다.
5. 사망 유닛의 스킵은 유닛턴 수를 올리지 않는다.
6. 정확히 23유닛턴까지 진행한다.

#### 독립 기대 원장

| T | 공격자 | 대상 | dmg | hpAfter | 사망 |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | A1 | B1 | 30 | 60 | false |
| 2 | B1 | A1 | 30 | 60 | false |
| 3 | A2 | B1 | 30 | 30 | false |
| 4 | B2 | A1 | 30 | 30 | false |
| 5 | A3 | B1 | 32 | 0 | true |
| 6 | B3 | A1 | 32 | 0 | true |
| 7 | A4 | B2 | 32 | 58 | false |
| 8 | B4 | A2 | 32 | 58 | false |
| 9 | A2 | B2 | 30 | 28 | false |
| 10 | B2 | A2 | 30 | 28 | false |
| 11 | A3 | B2 | 32 | 0 | true |
| 12 | B3 | A2 | 32 | 0 | true |
| 13 | A4 | B3 | 36 | 44 | false |
| 14 | B4 | A3 | 36 | 44 | false |
| 15 | A3 | B3 | 36 | 8 | false |
| 16 | B3 | A3 | 36 | 8 | false |
| 17 | A4 | B3 | 36 | 0 | true |
| 18 | B4 | A3 | 36 | 0 | true |
| 19 | A4 | B4 | 36 | 44 | false |
| 20 | B4 | A4 | 36 | 44 | false |
| 21 | A4 | B4 | 36 | 8 | false |
| 22 | B4 | A4 | 36 | 8 | false |
| 23 | A4 | B4 | 36 | 0 | true |

정답지는 이번 런타임 구현과 독립된 [[features/전투완성/raw/야간F9a_풀회귀_완료|F9a 23턴 원장]]을 사용한다. 비교 도구는 관측 로그를 추출·정규화만 해야 하며, 게임의 현재 피해 계산 코드를 재사용해 기대값을 만들면 안 된다.

#### 증거 묶음

- `01_raw_runtime.log`: 가공하지 않은 원본 런타임 로그
- `02_parsed_23turn.csv`: 23줄의 attacker, target, damage, hpAfter, died 추출본
- `03_diff.txt`: 기대 원장과의 비교 결과
- `04_final_state.txt`: BATTLE_END 1줄과 최종 생존자·HP
- `05_runtime_errors.txt`: 오류가 없으면 `0 errors`, 있으면 원문 전체
- `06_asset_state_before.txt`, `07_asset_state_after.txt`: dirty/변경 에셋 목록
- `08_graph_exports/`: 현재 `BP_BattleManager`, `BP_AttackButton`, `ST_UI`의 읽기 전용 graph export 사본

#### 합격·실패·중단 기준

합격은 다음을 모두 만족해야 한다.

- 23줄의 attacker, target, damage, hpAfter가 모두 일치한다.
- T5·6·11·12·17·18·23에만 `died=true`가 있다.
- `State|turn=23|event=BATTLE_END|winner=A`가 정확히 1줄이다.
- 최종 생존자는 A4, HP는 8이다.
- 런타임 오류와 `Accessed None`이 0건이다.
- 검증 전후 프로젝트 에셋 변경이 0건이다.

행동 전 `activeUnit` 불일치, 첫 원장 불일치, 예상하지 않은 스킬·대상, 턴 카운터 불일치, 런타임 오류, 23턴 종료 실패 또는 새 dirty asset을 발견하면 즉시 중단한다. 실패 증거를 그대로 보존하고 같은 세션에서 수정하지 않는다.

23턴 검사를 SPD 작업과 합치면 실패 원인이 Start인지 SPD인지 분리할 수 없다. 오너가 이월을 유지한다면 후속 결과는 `Start+SPD 결합 변경`으로만 판정할 수 있음을 명시한다.

### 2.2 권장 작업 순서

```text
Start P1-R01 봉인
→ 파트2 SPD 구현
→ SPD 전용 회귀 봉인
→ F7b BattleLog 계약 확정
→ F7b 인터프리터 전환
→ F7b 회귀 봉인
→ 파트3 연출
```

한 작업의 기준선과 완료 증거가 만들어지기 전에는 다음 작업을 같은 Blueprint에 넣지 않는다.

## 3. 반드시 지킬 개발 원칙

### 3.1 하나의 Blueprint에는 한 번에 한 작업만

특히 `BP_BattleManager`에 여러 기능을 동시에 넣지 않는다.

1. 작업 시작 기준선 고정
2. 허용된 에셋만 수정
3. graph 증거 확보
4. PIE 실증
5. 회귀 원장 대조
6. 오너 확인
7. 에셋 스냅샷 봉인
8. 다음 작업 시작

### 3.2 first-party 에셋을 복구 가능하게 보존

현재 `/projectTP/Content/` 전체가 Git ignore 상태라 문서 커밋만으로 실제 Blueprint 구현을 복구할 수 없다.

최소 보존 대상:

- `BP_BattleManager`
- `BP_BattleSpawnPoint`
- `BP_AttackButton`
- 전투 HUD와 SkillMenu 관련 Widget
- 자체 DataTable과 UserDefinedStruct
- `map_battle_octopath`
- `ST_UI`
- 자체 Material과 전투 데이터 에셋

유료·third-party 원본과 first-party 수정 자산을 분리하고, Git LFS·Perforce 또는 검증된 별도 백업 방식 중 하나를 오너가 정한다.

검증 질문:

> 현재 에디터와 PC를 잃어도 이 상태를 정확히 복구할 수 있는가?

답이 아니오라면 다음 기능으로 넘어가지 않는다.

### 3.3 전투 판정과 UI 분리

- 피해, 회복, 막기 계산은 전투 로직이 소유한다.
- HP와 상태는 전투 상태가 정답이다.
- UI 텍스트와 게이지 값으로 전투 결과를 판정하지 않는다.
- 사망과 승패는 UI 이벤트가 아니라 전투 코어에서 결정한다.
- UI가 없어도 로그만으로 한 판 결과를 재현할 수 있어야 한다.

### 3.4 결정론과 구조화 로그 유지

전투 로그의 권장 필드:

```text
runId
turn
state
attacker
skillId
targets
effect
damageOrHeal
hpBefore
hpAfter
statusApplied
died
winner
```

확률 효과는 다음도 기록한다.

```text
randomSeed
roll
chance
result
```

같은 데이터와 seed로 실행하면 같은 결과가 나와야 한다.

### 3.5 데이터 정본 하나만 사용

F7b 전환 후 책임:

- 스킬 메타: `DT_Skills`
- 효과 엔트리: `DT_SkillEffects`
- 상태 정의: `DT_StatusEffects`
- 표시 문자열: 확정된 문자열 DataTable
- 판정: Blueprint effect interpreter

전환 기간에 구형·신형 필드가 함께 존재할 수는 있지만, 현재 런타임이 읽는 정본은 하나로 고정한다.

### 3.6 MCP 읽기 전용 경계

리뷰에서 승인 가능한 도구:

```text
list
get
read
inspect
describe
```

승인하지 않을 작업:

```text
write
create
add
update
set
delete
rename
save
compile
reimport
execute
```

MCP read-only는 현재 서버 강제가 아니라 승인 규율에 의존하므로 호출마다 확인한다.

## 4. 테스트를 다섯 층으로 분리

| Layer | 확인 내용 | 잡는 문제 |
| --- | --- | --- |
| Data | 중복 ID, 누락 키, orphan reference | 데이터 계약 오류 |
| Graph | 함수, 핀, 실행선, 기본값 | Blueprint 배선 오류 |
| Runtime | PIE 실제 상태, HP, 콜리전 | 에디터와 런타임 차이 |
| Regression | 기준 원장과 자동 diff | 기존 전투 동작 회귀 |
| Owner | 조작감, 가독성, 연출, 재미 | 자동화가 판정할 수 없는 품질 |

노드나 문자열이 존재한다는 사실만으로 런타임 성공이나 asset 동일성을 판정하지 않는다.

## 5. MVP 완료 기준

- [ ] Start 전 자동 전투가 시작되지 않는다.
- [ ] Start 1회로 전투가 정확히 시작된다.
- [ ] 8명의 초기 HP와 상태가 정확하다.
- [ ] 턴 순서가 결정론적이다.
- [ ] 5개 기본 스킬이 실제 메뉴를 통해 동작한다.
- [ ] 적·아군·자신 대상 규칙이 정확하다.
- [ ] 피해, 회복, 막기, 쿨다운이 정확하다.
- [ ] 사망자는 행동·선택·피격 대상에서 제외된다.
- [ ] 한 팀이 전멸하면 전투가 정확히 종료된다.
- [ ] End 후 재시작하면 모든 전투 상태가 초기화된다.
- [ ] 두 번 이상 연속 전투해도 이전 상태가 남지 않는다.
- [ ] 런타임 오류와 `Accessed None`이 없다.
- [ ] 기준 원장과 예상 결과가 일치한다.
- [ ] 현재 구현을 복구할 에셋 백업이 있다.

## 6. MVP에서 미룰 것

- 실시간 ATB
- 온라인 PvP와 서버 구조
- GAS 전환
- 대규모 C++ 이관
- AoE 완전 구현
- 화려한 VFX와 카메라 추가
- 최종 게임패드 UI
- 전체 다국어 번역
- 1000캐릭터 대량 생성
- 병목 측정 전 세부 성능 최적화

## 7. AI 작업 요청 형식

```text
Goal:
이번 작업에서 만들어야 하는 결과

Non-goals:
이번에 절대 건드리지 않을 범위

Allowed assets:
수정 가능한 Blueprint와 문서

Invariants:
반드시 유지돼야 하는 기존 동작

Verification:
통과해야 하는 GRAPH, PIE, LOG, 회귀 테스트

Stop conditions:
불확실하거나 실패했을 때 수정하지 말고 오너를 호출할 조건
```

권장 역할:

- Claude Implementer: 허용 범위 구현
- Verifier: 정의된 TC와 로그 실증
- Codex Reviewer: 읽기 전용 독립 리뷰
- Owner: 우선순위, 플레이 감각, 최종 승인

에이전트 수보다 각 역할이 책임지는 산출물이 명확한지가 중요하다.

## 8. 매 작업 종료 체크리스트

- [ ] 이번 작업은 한 기능만 변경했다.
- [ ] 허용된 Blueprint 외에는 수정하지 않았다.
- [ ] 저장된 에셋을 다시 열어 변경을 확인했다.
- [ ] Blueprint compile 오류가 없다.
- [ ] PIE에서 실제로 재현했다.
- [ ] 기존 전투 원장과 비교했다.
- [ ] 오너가 직접 플레이했다.
- [ ] 변경 에셋을 복구할 수 있다.
- [ ] 현재 상태 문서를 한 곳만 갱신했다.
- [ ] 다음 작업과 섞이지 않은 기준선을 만들었다.

## 9. 오너가 반복해서 물어야 할 질문

1. 이 변경의 정답은 무엇인가?
2. 무엇이 반드시 유지되어야 하는가?
3. 실패하면 어디까지 되돌릴 수 있는가?
4. 다른 PC에서도 동일하게 재현할 수 있는가?
5. 다음 변경과 섞이기 전에 어떤 증거를 남겨야 하는가?

## 10. 현재 단일 최우선 행동

> **Start 상태에서 이월된 P1-R01 F9a 23턴 원장 `diff 0`을 확보하고, 해당 Blueprint 기준선을 안전하게 보존한다. 그 후에 파트2 SPD를 시작한다.**
