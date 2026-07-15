---
type: raw
project: projectTP
feature: 전투완성
stage: 야간④
status: 게이트 PASS 2026-07-16 야간
updated: 2026-07-16
---

# 야간④ 완료 — End버튼 재전투 게이트 통과

> 대상: [[야간큐_TC]] ④ · [[F5-2_완료]](ResetForBattle·InitBattle·bWasSkip·EnterEnd) · [[언리얼_MCP_실전노하우]] §29
> 전멸 시 월드에 남은 Attack 박스를 End 라벨로 전환하고, End 클릭으로 `InitBattle`을 재호출해 재전투 루프를 여는 기능을 실장·검증한 결과를 기록한 문서. 야간큐 4건(③데미지폰트·④End버튼·⑤로그·F6모션) 중 두 번째 게이트.
#projectTP/전투완성

---

## 1. 무엇이 됐나 — 스코프 & 확정 메커니즘

**스코프**: 전멸 시 월드 Attack 박스 → End 라벨 전환. End 클릭 → `InitBattle` 재전투 루프.

**구현**:
- **ST_UI `Battle.End`** = `"End"` 신설 — `StringTableTools`로 키 추가 후 `update_metadata_tags`로 강제 dirty 처리해 저장까지 검증(`StringTableTools` 단독 호출만으로는 dirty가 서지 않아 우회가 필요했음).
- **`BP_AttackButton.LabelEnd`**(신규 `TextRenderComponent`) + **`ShowEnd()`** 함수 신설 — 기존 `Label`/`LabelCancel` 패턴을 그대로 복제해 **`BeginPlay` 1회만 `SetText`**([[언리얼_MCP_실전노하우]] §6이 확인한 "런타임 `SetText`가 렌더에 무반영"인 미해결 렌더버그를 회피하는 확정 패턴).
- **`EnterEnd`** 끝에 `ButtonRef.ShowEnd()` 호출 추가.
- **`NotifyAttackButtonClicked`** **최상단**(기존 `bInputLocked` Branch보다 앞)에 `Branch(BattleState==6) → InitBattle() → 종단` 삽입 — ★이 위치는 최적화가 아니라 **구조적 확정**(근거는 §2).
- **`InitBattle`**에 `bWasSkip=false` 리셋 추가.

## 2. `NotifyAttackButtonClicked` 최상단 분기 — 구조적으로 필수인 순서

`Branch(BattleState==6)`을 기존 `bInputLocked` 체크보다 **exec 상류**에 둔 것은 취향이 아니라 필수 조건이다. End 상태에는 직전 전투의 `bInputLocked=true`가 그대로 남아 있을 수 있는데, 이 분기가 `bInputLocked` 체크 **뒤**에 있었다면 그 잠금이 재시작 클릭 자체를 삼켜 **End 화면이 영구 무음실패로 고착**됐을 것이다(야간큐 TC END-01이 정확히 이 위험을 지목한 항목). `True` 분기는 `InitBattle()` 호출 후 **곧장 종단**시켜, End 상태의 클릭이 정상 Attack 커맨드 경로로 잘못 흘러드는 일을 원천 차단했다.

## 3. 수정 이력 3건 (버그 → 해결)

구현 중 PIE 실측으로 드러난 버그 3건.

| # | 증상 | 원인 | 해결 |
|---|---|---|---|
| ① | `ClickBox` 콜리전 영구 잠김 | `HideAll`은 콜리전을 끄기만 하고 `ShowAttack`만 다시 켜는 **비대칭 쌍** 구조 — End 경로엔 재활성화 로직 자체가 없었음 | `ShowEnd()`에 `SetCollisionEnabled(QueryOnly)` 추가 |
| ② | `LabelEnd` 값 미반영 | 기배치 레벨 인스턴스에 컴포넌트 **템플릿 값이 소급 전파되지 않음**([[언리얼_MCP_실전노하우]] §20 함정㉔의 TextRender 전반 확장 — §29 **(54)**로 일반화) | 레벨 인스턴스에 값 **개별 직접 재적용** |
| ③ | `LabelEnd` 리셋 누락 | 기존 `Show*`/`HideAll`이 신설 컴포넌트의 존재를 몰라 "End"+"Attack" 라벨이 동시 표시되며 겹침(§29 **(57)**) | 3개 함수 전부에 `SetVisibility(false)` 대칭 추가 |

## 4. TC 판정표

[[야간큐_TC]] ④(END-01~08) 8건 판정 결과:

| ID | 판정 | 근거 |
|---|---|---|
| **END-01**★ | PASS | GRAPH — `Branch(BattleState==6)`가 `bInputLocked` 체크보다 exec 상류, 구조적 확정(§2) |
| **END-02**★ | PASS | E2E 실측 — End 클릭→`InitBattle` 발동, B1~B4 Hp/bAlive 완전 복원(MOCK hp=1→MaxHp 복원 확인), turnCounter 리셋 |
| **END-03** | PASS | GRAPH — `ShowEnd`는 Visibility 토글만, 런타임 `SetText` 노드 0개(`BeginPlay` 1회 세팅) |
| **END-04** | PASS | 수정이력③ 적용 후 라벨 겹침 해소(프로퍼티+렌더 증거) — 런타임 경로 직접 관측은 없어 GRAPH 확인으로 갈음 |
| **END-05**★ | 조건부 통과(이월) | 기존 F5-2 N26(G-A 재동결 가드) 구현 신뢰 — 이번 세션 재현 시도 자체가 불가했음 |
| **END-06** | PASS | 자연관측 — 재전투 후 더블클릭의 2번째 클릭이 새 전투의 정상 Attack으로 소비됨(정상분기 오염 0) |
| **END-07** | PASS | GRAPH — `InitBattle`에 `bWasSkip=false` 추가 확인 |
| **END-08** | PASS | SCF+PIE — 연타해도 `InitBattle` 1회만 발동(멱등), 크래시 0 |

11턴 이상 런타임 에러 0([[언리얼_MCP_실전노하우]] §28 함정㊾ 기준 — 한국어 로케일 패턴 "None에 액세스"로 스캔).

**수용 사항** (TC 미세 갭이나 이번 게이트에서 문제 삼지 않기로 한 것):
- 더블클릭 2번째 클릭 = 새 전투의 정상 Attack으로 소비되는 것은 **자연 동작**(END-06 근거 그 자체).
- END-05(G-A 타이밍)는 F5-2에서 이미 구현된 N26 가드를 신뢰 — 이번 세션에서 재현 실험 자체를 할 수 없었음.
- `HideAll` 경로 자체는 런타임에서 직접 관측하지 못함 — GRAPH 확인(노드 배선 정적 확인)으로 갈음.

## 5. 오진 사례 기록 (교훈)

중간 실증자가 "유닛 `ClickBox`의 Visibility 콜리전 채널 누락 리그레션"으로 오진해 보고했다 — 근거는 `get_properties`로 조회한 `collisionResponses.responseArray`에 `Visibility` 채널이 안 보인다는 것이었다. **Director가 직접 재조회로 반증**: 실제 프로퍼티엔 `Visibility:Overlap`이 존재했다. 실제 원인은 클릭 좌표 오조준(로그에 `ignored (same team or self)` 도달 — 클릭 자체는 처리되고 대상 판정만 어긋남)과 창 가림이었다.

**교훈**(§29 **(58)**로 일반화):
- `responseArray`는 프로파일 기본값과의 **diff만** 나열한다 — 채널 부재 ≠ 무응답.
- **검증된 좌표 > 재계산** — PIE 실측 이력이 있는 좌표를 이론적 재계산으로 기각하지 않는다.
- 서브에이전트가 CONFIRMED로 보고해도 **교차 증거가 모순되면 Director가 직접 진단**한다.

## 6. 스캐폴드 잔존물

`BP_BattleSpawnPoint.Hp` = **Instance Editable 플래그**(verifier MOCK 가속용으로 켜둔 것) — **F9a 스캐폴드 정리 시 원복 대상**으로 명기해둔다.

## 7. 세이브포인트

`D:\unreal\_savepoints\야간45_End버튼_로그\`(4애셋).

## 8. 이월 — 아침 오너 육안

- End 라벨 룩
- 재전투 체감(전환 타이밍·페이싱)

---

## 관련
- [[야간큐_TC]] ④ (TC 설계 원본 — END-01~08)
- [[F5-2_완료]] (ResetForBattle·InitBattle·bWasSkip·EnterEnd 컨텍스트)
- [[언리얼_MCP_실전노하우]] §29 (야간④·⑤ 신규 함정 5건)
- [[야간③_데미지폰트_완료]] (같은 야간 세션, 앞 게이트)
- [[야간⑤_로그보강_완료]] (같은 야간 세션, 다음 게이트)
