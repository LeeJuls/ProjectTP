---
type: raw
project: projectTP
feature: 전투완성
stage: 파트1_Start
status: 게이트 PASS 2026-07-16 23시경(파트1 완료) — Director 직접검증(GRAPH 핀 원문)·자산·PIE·오너 육안 5항목·T1 실증 전부 PASS. F9a 23턴 diff-0(P1-R01)은 오너 결정으로 파트2 이월. 파트2(SPD 턴 순서) 착수 가능
updated: 2026-07-16
---

# 파트1(Start 버튼) 착수 — 진행 기록

> 대상: 승인 계획서 `C:\Users\user\.claude\plans\humble-purring-glacier.md`(v3, 전 에이전트 8명 리뷰 반영, git 외부) §파트1 · [[파트1_Start_TC]](qa-critic TC 46건) · [[야간F9a_풀회귀_완료]](직전 게이트, 이번 작업의 기준선) · [[야간F7a_스킬메뉴_완료]](Attack 박스 폴백의 유래) · [[야간④_End버튼_완료]](박스 3함수 선례) · [[언리얼_MCP_실전노하우]] §34
> 이 문서는 **읽는 사람이 맥락 없이 이해**할 수 있도록, 왜 이 작업을 하는지부터 검증이 잡은 잠복 결함, Director 자신의 오류까지 숨기지 않고 기록한다. 세부 작업 목록·TC는 각 링크로.
#projectTP/전투완성

---

## 1. 왜 이 작업인가

전투가 **스킬 메뉴로 5스킬을 실전 사용**하는 데까지 왔다(F7a, [[야간F7a_스킬메뉴_완료]]). 그 결과 두 가지가 어긋났다:

1. **Attack 박스의 역할이 죽었다.** 스킬 메뉴가 생기기 전 임시 진입점이었던 박스가 지금은 메뉴와 병존하며, 클릭하면 `PendingSkillId=31000000`(기본공격) 하드코딩 폴백만 겸하는 반쪽짜리 버튼으로 남아 있다.
2. **전투 시작을 사람이 못 고른다.** 8/8 유닛이 자가등록을 마치면 `InitBattle`이 같은 실행 체인에서 곧바로 `EnterTurnStart`를 호출한다 — PIE를 켜는 순간 A1 턴부터 자동으로 굴러가고, "시작" 버튼을 누르는 절차 자체가 없다.

오너 요구는 명확했다: **"attack → start로 변경"**. 이 한 문장을 실행 가능한 작업으로 쪼개는 과정에서, SPD(속도) 턴 순서 정렬과 막기·치유 연출 오류라는 두 가지 별개 작업이 함께 딸려 나왔다(계획서가 이 셋을 파트1/2/3으로 구분). 이 문서는 **파트1(Start 버튼)** 착수 시점의 기록이다.

---

## 2. 오너 확정 결정 5건 + Director 판단

### 오너 확정 결정
| # | 결정 | 내용 |
|---|---|---|
| 1 | SPD 수치 | 유닛별 8기 **각각 90~97**(연속, 전원 상이). 8기가 전사2성×2팀+마법사2성×2팀뿐이라 `job_stats`(직업×등급 표) 하나만으로는 4기씩 동률이 나므로, 유닛별 개별 오버라이드가 필요하다(파트2에서 실행). |
| 2 | 박스의 운명 | **상황별 겸용**(Start/Cancel/End) + **임시 취급**. 로비 Start와 무관한 테스트 용도일 뿐이라 정식 UI로 승격하지 않는다. |
| 3 | 막기 연출 범위 | **연출 4건만**(파트3). 자세 유지는 머티리얼 `bFreeze` 신설+8개 MI 회귀가 필요해 범위 밖. |
| 4 | 동률 처리 | **규칙만 문서화, 구현 보류.** 8기 전원 SPD가 상이하므로 동률 자체가 발생할 수 없다(발생 못 하는 분기를 구현하면 死코드 규약 위반) — tiebreak 규칙은 **원 큐 인덱스순**(결정론)으로만 문서에 남긴다. |
| 5 | SPD 검증 담당 | **Director가 직접** 챙긴다 — 구현은 sonnet(gameplay-engineer), 게이트는 Director가 핀 원문을 직접 조회해 판정한다(서브에이전트 보고를 그대로 게이트로 인정하지 않음). |

### Director 판단 (오너 질의에 대한 답)
| 질의 | 판단 | 근거 |
|---|---|---|
| SPD 턴 순서를 만드나 | **한다** | 오너가 말한 "SPD 순 턴"은 **실시간 ATB가 아니다**. 로드맵이 정한 알파↔베타 축은 "턴제(정지)냐 실시간 ATB냐"이고, SPD 정렬은 정지형 턴제 그대로(옥토패스 방식) 순서만 바꾸는 것이다. |
| 실시간 ATB(게이지)도 만드나 | **안 한다** | 로드맵 결정: "턴제→ATB 전환은 베타에 그대로 남는다(서버 전환과 묶어 재작업 1회로 압축)". SPD 정렬은 ATB의 전 단계 성격이라, 나중에 게이지만 얹으면 된다. |
| Start와 SPD를 한 작업으로 묶나 | **쪼갠다** (초기 판단을 정정 — §4 참고) | Start는 턴 순서·데미지를 안 바꾸므로 **F9a 23줄 원장이 그대로 나와야 한다** = 파트1 단독으로 diff-0 게이트를 공짜로 얻는다. 묶으면 이 게이트를 버리게 되고, 원장이 틀어졌을 때 원인이 절차(박스→메뉴 전환) 때문인지 값(정렬) 때문인지 분리할 수 없게 된다. |
| 박스를 정식 UI로 승격하나 | **임시로 유지**(오너 판단 채택) | Start 라벨은 기존 TextRender 3개(`Label`/`LabelCancel`/`LabelEnd`) 재사용만으로 끝나 새 컴포넌트 추가가 0건이라 비용이 낮고, F7b에서 어차피 박스를 폐기할 계획이 이미 있다. |

---

## 3. ★검증이 잡은 잠복 결함 3건

착수 전 실측(qa-critic + Director)이 계획서 초안 자체에 있던 잠복 결함 3건을 찾아냈다 — **이 문서의 핵심 가치**는 "작업을 어떻게 했다"가 아니라 "손대기 전에 뭘 밟을 뻔했는지"를 남기는 데 있다.

### (A) Spd=0 레이스 — BLOCKER
`BP_BattleSpawnPoint`의 **DT 스탯 로드가 `RegisterUnitReady`보다 뒤**에 있다. `RegisterUnitReady`는 `Branch(RegisteredCount==8) → InitBattle()` 구조라, **8번째로 등록되는 유닛의 `BeginPlay` 실행 한복판에서 `InitBattle`이 동기 실행**되고, 그 순간 그 유닛의 `Spd`는 아직 초기화 전이라 **0**이다.

지금까지 안 터진 이유는 우연이다 — HP는 `ResetForBattle`이 0으로 죽여도 `BeginPlay` 꼬리가 곧바로 `SetHp(90)`으로 자가치유하기 때문에 무해했다. 하지만 **정렬 값은 자가치유되지 않는다** — 한 번 계산되면 그대로 얼어붙는다. 게다가 8번째로 등록되는 유닛이 누구인지는 UE 엔진이 순서를 보장하지 않으므로, **PIE를 켤 때마다 어느 유닛이 Spd=0에 걸리는지 달라진다.**

**해법**: 정렬 로직을 `InitBattle`이 아니라 파트1이 신설하는 `StartBattle()`에 둔다. 사람이 Start를 누르는 시점에는 이미 8기의 `BeginPlay`가 전부 끝나 있으므로, 이 레이스는 구조적으로 존재할 수 없게 된다. **즉 파트1이 파트2(SPD)의 블로커를 먼저 구조적으로 제거한다.**

### (B) ShowCancel 콜리전 부재
실측: `ShowCancel` 함수는 **7노드**(`SetVisibility`×3뿐)인데 `ShowAttack`은 **10노드**다. `ShowCancel`에는 `SetCollisionEnabled`가 없다 — **지금 Cancel 버튼이 눌리는 유일한 이유는, 그 직전에 실행된 `ShowAttack`이 켜둔 콜리전을 우연히 물려받고 있기 때문**이다. 파트1이 `EnterAwaitCommand`의 `ShowAttack()` 호출을 `HideAll()`로 바꾸는 순간(작업10), `HideAll`(콜리전 끔) → `ShowCancel`(콜리전 안 켬)이 되어 **Cancel 버튼이 영구히 눌리지 않는 타겟팅 소프트락**이 발생한다. 그래서 **콜리전 복구(작업2)가 폴백 은퇴(작업9)보다 반드시 먼저**여야 한다(§6).

### (C) END-02 위증
기존 [[야간큐_TC]]의 `END-02` 항목은 `InitBattle` 실행 중 `BattleState==0`을 관측했다고 PASS로 기록돼 있었다. 그런데 `InitBattle`은 Function Graph(동기 실행)이고, `SetBattleState(0)` 직후 곧바로 `EnterTurnStart()`가 같은 체인에서 실행된다 — **즉 런타임에 `BattleState==0`을 볼 수 있는 프레임이 원리상 존재하지 않는다.** 그런데도 PASS로 기록됐다는 것은 **에디터 스냅샷(CDO 기본값이 마침 0)을 읽고 런타임 관측으로 착각**했다는 뜻이다(qa 규약 QA-H6 위반 — "런타임에 도달 불가능한 상태를 관측했다고 기록하지 말 것").

⚠ **파트1이 State 0(대기)을 실체화해도 이 위증 패턴은 재발할 수 있다.** `BattleState`의 CDO 기본값이 **0**이기 때문에, "InitBattle 완료 후 대기 중"과 "InitBattle이 아직 실행조차 안 됨"이 `BattleState==0` 단독으로는 구분되지 않는다. 그래서 파트1의 새 판정 TC(P1-P01)는 `BattleState==0`이 아니라 **`bInputLocked==true`를 유일한 판별자**로 쓴다(`bInputLocked`의 CDO 기본값은 `false`이고, `InitBattle` 안의 세터 1개만이 이를 `true`로 뒤집기 때문). 상세: [[파트1_Start_TC]] N7.

---

## 4. Director 오류 4건 + 위험도 판단 역전 1건 (자기 정정 — 숨기지 말 것)

착수 전 계획서 작성·검토 과정에서 Director 본인이 낸 판단 오류다. 실측으로 반증됐으므로 여기 정정해 남긴다.

1. **`QA-H4`의 "순서 고정"을 턴 순서로 오독**했다. "갱신하라"고 지시할 뻔했으나, 실제로 `QA-H4`가 말하는 "순서"는 턴이 도는 순서가 아니라 **노드 실행 순서**(마커 OFF → 인덱스 증가, 뒤집으면 *다음* 유닛의 마커를 잘못 끄게 됨)였다 — 이건 **정렬 작업(파트2)이 절대 건드리면 안 되는 보존 대상**이지 갱신 대상이 아니다. 인용한 라인 번호도 틀렸다(L47 → 실제 L34).
2. **"대기 중 메뉴가 기본값대로 노출될 위험이 있다"**고 판단했으나 사실이 아니었다 — 실측상 메뉴 디자이너 기본값이 **이미 Collapsed**다. 다만 이 사실을 근거로 "그럼 안 넣어도 된다"로 정정하지는 않았다 — 명시적 `SetVisibility(Collapsed)` 노드는 그대로 넣기로 하되, 그 근거를 "노출 방지"에서 **"우연한 성립을 명시적 선언으로 바꾼다"**(현재는 두 개의 외부 사실—메뉴 기본값·EnterEnd의 기존 처리—에 우연히 기대어 성립 중인 상태를 회귀에도 안전하게 만든다)로 바꿨다.
3. 파트3(막기·치유 연출)의 Smear(참격 잔상) 게이팅 지점을 서술하면서 **BP 경로를 표기하지 않았다** — 이후 검토자가 엉뚱한 BP에서 해당 로직을 찾아 헤매는 사고로 이어질 뻔했다(계획서 §파트3 표 4행에 "착수 전 Director 확인" 각주로 이미 반영).
4. **"Start와 SPD를 한 작업으로 묶으면 원장 재작성이 1회로 끝난다"**고 판단했으나 **오답**이었다 — 쪼개도 재작성은 어차피 1회이고, 오히려 쪼개야만 파트1 단독의 diff-0 게이트(§2 판단표)를 얻을 수 있다. 이 오류는 착수 전에 정정되어 "쪼갠다" 결정으로 반영됐다.
5. **위험도 판단 역전**: 계획서 초안의 위험 표는 *"`ShowStart`/`ShowCancel` 콜리전 누락 → 게임 시작 불가"*로 두 함수를 같은 위험도로 묶었다. 그런데 실측 결과 `ShowStart` 쪽은 **틀렸다** — `ClickBox` 컴포넌트의 기본 콜리전 값이 이미 `QueryOnly`라서, `SetCollisionEnabled`를 빠뜨려도 Start는 **정상적으로 클릭된다**(무증상). 진짜 위험은 "게임 시작 불가"처럼 시끄럽게 터지는 쪽이 아니라, **PIE를 통과하면서 조용히 잠복하는 쪽**이라 오히려 더 나쁘다 — PIE 테스트 통과가 콜리전 노드의 존재를 증명해주지 못하기 때문이다(GRAPH 조회만이 유일한 탐지 수단, [[파트1_Start_TC]] N3). 반대로 `ShowCancel` 쪽 위험 판단은 §3-(B)와 정확히 일치해 **100% 정확했다**.

---

## 5. 검증이 추가로 찾아낸 것 — 계획서에 없던 신규 발견 14건

착수 전 qa-critic 적대적 검토([[파트1_Start_TC]])가 계획서에 없던 결함 14건(High 3·Medium 7·Low 4)을 추가로 찾았다. 전량은 TC 문서를 참고하되, 파트2 착수자가 특히 주의해야 할 것만 요약한다:

- **N1(High)**: 작업8(Start 분기 추가)과 작업9(폴백 은퇴)는 **둘 다 적용돼야 안전**하다 — 하나만 적용되면 Start 클릭이 "전투 시작"과 "기본공격 커밋"을 동시에 실행해버려 **원장이 에러 없이 조용히 오염**된다. 그래서 이 둘은 결합 게이트(P1-G07)로 묶어 판정한다.
- **N7(High)**: §3-(C)의 END-02 위증은 파트1 이후에도 재발 가능 — 반드시 `bInputLocked==true`를 판별자로 쓸 것.
- **N11(High)**: [[야간큐_TC]]의 `END-04`(재전투 후 라벨 복원 PASS 기록)·`END-06`(공격 커밋 예시)은 파트1 적용 후 **문면 그대로는 거짓**이 된다 — 계획서가 이 재정의를 빠뜨렸던 것을 P1-R02·R03으로 보강했다.
- **N4·N5(Medium)**: `Menu_SkillMenu`는 Manager 변수가 아니라 **HUD의 바인드 위젯**(접근은 `GetMenu_SkillMenu(self=HUDRef)`)이고, `EnterAwaitCommand`와 `EnterAwaitTarget`의 `MacroInstance_2`는 **같은 이름, 다른 매크로**(각각 `IsValid`/`ForEachLoop`)다 — 이름만 보고 배선하면 오배선.

---

## 6. 작업 12개 목록 (순서를 강제하는 이유)

계획서 §파트1의 작업 목록(전문은 계획서 원문 참고, 요지만 재수록). **순서를 임의로 바꾸면 안 되는 지점 3곳**을 먼저 밝힌다:

1. **콜리전 복구가 폴백 은퇴보다 먼저**: 작업2(`ShowCancel`에 `SetCollisionEnabled` 추가)는 §3-(B) 소프트락 때문에 작업9(폴백 은퇴, `EnterAwaitCommand`의 `ShowAttack→HideAll` 교체)보다 반드시 먼저 끝나 있어야 한다.
2. **작업8과 작업9는 결합 게이트**: §5-N1대로, 이 둘은 개별 완료가 아니라 **둘 다 끝난 상태를 하나로 묶어** 검증한다(P1-G07).
3. **중간 PIE 금지**: 작업7(`bInputLocked`을 `true`로 뒤집음)과 작업8(Start 분기 추가) 사이에 테스트를 끼우면 "눌러도 반응 없음"(잠금만 걸리고 우회로가 아직 없는 상태)으로 보인다 — **12개를 전부 끝내고 단일 PIE로 검증**한다.

| # | 작업 | 비고 |
|---|---|---|
| 1 | `ST_UI`에 `Battle.Start` 키 추가 + `data/st_ui.csv` 미러 | [[언리얼_MCP_실전노하우]] §34(81) 경로로 강제 dirty·mtime 검증 |
| 2 | `ShowCancel`에 `SetCollisionEnabled(QueryOnly)` 복구 | §3-(B) 때문에 9번보다 먼저 |
| 3 | `ShowStart()` 신설(`ShowAttack` 복제) | 3라벨 SetVisibility + 콜리전 |
| 4 | `compile_blueprint(BP_AttackButton)` | 6번에서 `ButtonRef.ShowStart()` 노드를 만들려면 선행 필요 |
| 5 | `BeginPlay`의 Key 핀을 `"Battle.Start"`로 | |
| 6 | `StartBattle()` 신설(`EnterTurnStart()` 호출을 InitBattle 꼬리에서 이관) | **파트2 정렬이 들어올 자리** |
| 7 | `InitBattle` 종단화(EnterTurnStart 호출 절단·잠금 리터럴 true·`ShowStart()`+메뉴 Collapsed 꼬리) | |
| 8 | `NotifyAttackButtonClicked`에 Start 분기 추가(`bInputLocked` 체크보다 상류) | 작업9와 결합 게이트(N1) |
| 9 | F7a 폴백 은퇴(`IfThenElse_1`은 보존, `then` 체인 3노드만 미연결로) | 작업8과 결합 게이트(N1) |
| 10 | `EnterAwaitCommand`의 `ShowAttack()`→`HideAll()` 교체 | |
| 11 | `EnterAwaitTarget` 꼬리에 메뉴 Collapsed 추가 | State 3에서 메뉴가 죽은 UI로 남는 것 방지 |
| 12 | (덤) `EnterExecuting`의 `IsValid` 분기 4개 exec 미연결 해소 | F4부터 잠복하던 것과 같은 계열의 행업 함정 |

> 참고: 계획서 원문은 이 목록을 소개하며 "11개를 다 하고 단일 PIE로 검증"이라 적었는데 목록 자체는 12개다(작업12 "덤"이 이후에 추가되며 문장이 갱신되지 않은 것으로 추정) — 작업12도 §3-(B)·(A)와 같은 "PIE 전 필수 수정" 성격이라, 이 문서는 **12개 전부를 PIE 전 완료 대상**으로 명시해 둔다.

---

## 7. 게이트

- **TC 46건** = [[파트1_Start_TC]] 참조(GRAPH 20·자산 4·PIE 12·회귀 10 + 오너 육안 5건 별도/불차단).
- **★최강 게이트**: **F9a 23턴을 스킬 메뉴 경유로 재수집 → [[야간F9a_풀회귀_완료]] 원장과 diff 0.** 파트1은 턴 순서·데미지 값을 전혀 바꾸지 않으므로, 23줄이 attacker/target/dmg/hp까지 바이트 단위로 그대로 나와야 통과다. 이 빌드를 **파트2(SPD)의 새 기준선**으로 봉인한다. → **[결과] 2026-07-16 23시경 오너 결정으로 파트2 이월**(§9-6) — 파트1 자체는 T1 실증(§9-5)+GRAPH 편집범위 봉인([[파트1_Start_TC]] P1-G20)으로 게이트 PASS 판정.
- TC 실행은 verifier, 게이트 판정은 Director(2단 검증 원칙 — qa-critic의 논리 검증과 verifier의 실증은 서로 다른 검증).

---

## 8. 상태 (착수 시점 기록 — 완료 결과는 §9 참고)

- **2026-07-16 22:17 착수**(세이브포인트 생성시각 실측 기준) — gameplay-engineer(sonnet)가 구현 중.
- **백업**: `D:\unreal\_savepoints\파트1_Start_착수전\` — `BP_AttackButton.uasset`·`BP_BattleManager.uasset`·`BP_BattleSpawnPoint.uasset`(BP 3종) + `ST_UI.uasset` + `autosave_참고\`(자동저장 참고본 2: `BP_BattleManager_Auto0_2133.uasset`·`BP_BattleSpawnPoint_Auto8_2046.uasset`).
- 다음 단계: 12개 작업 완료 → 단일 PIE 검증 → verifier가 TC 46건 실증 → Director 게이트(★F9a diff-0 포함) → 통과 시 파트2(SPD) 착수.

---

## 9. 게이트 결과 — PASS (2026-07-16 23시경)

> §8이 착수 시점 기록이라면 이 절은 **종료 시점 기록**이다. 전부 실측 — Director 직접 검증(GRAPH 핀 원문) + verifier 실증(PIE) + 오너 육안. 게이트 판정은 Director.

### 9-1. Director 직접 검증 (핀 원문) — GRAPH PASS

서브에이전트 보고를 게이트로 인정하지 않고, Director가 `get_node_infos` 원문을 직접 조회해 확정했다.

- `FunctionEntry_0.then → IfThenElse_2` 직결 = **Start 분기가 최상단**. `IfThenElse_2.else → IfThenElse_3(State==6) → … → IfThenElse_0(bInputLocked)` — 잠금 체크보다 상류로 확정(치명 위험 R3 해소).
- `PromotableOperator_2` = `수학|바이트|Equal(Byte)`(와일드카드 자동 승격), **B 핀 value="0"** — 조건식이 진짜 `BattleState==0`.
- `CallFunction_4(StartBattle)`: type_id=`|StartBattle`, **`then: connected_pins=[]`** = 미종단 종단 확인.
- `IfThenElse_1` **생존**, `then: []`(폴백 절단), **`else → CallFunction_1(EnterAwaitCommand)`** 무손상 — 같은 Branch 양쪽 핀 커플링(N1/§3-(B))을 정확히 회피.
- 4함수 콜리전 대칭: `ShowStart`/`ShowCancel`/`ShowEnd` = **QueryOnly**, `HideAll` = **NoCollision**(`ShowCancel`은 이번에 신규 복구 — 기존엔 `SetCollisionEnabled` 부재였음, §3-(B)).
- `InitBattle.VariableSet_1.bInputLocked = "true"`(false→true 플립), `CallFunction_5(EnterTurnStart).execute = []`(절단, 노드는 고아 존치).
- `EnterAwaitCommand`: `CallFunction_4(ShowAttack)` execute·then 모두 `[]` = **완전 고아**, `CallFunction_7(HideAll)`이 체인 활성.

### 9-2. 자산

| 자산 | 착수 전 | 착수 후 |
|---|---|---|
| `BP_AttackButton.uasset` | 161,658 bytes | **184,262 bytes**(22:41) |
| `BP_BattleManager.uasset` | 2,389,751 bytes | **2,438,048 bytes**(22:41) |
| `ST_UI.uasset` | 3,615 bytes | **3,781 bytes**(22:24) |

ST_UI 바이너리 grep: `Battle.Start` **2회**(기존 키와 동일 패턴), 기존 5키 전부 생존. `data/st_ui.csv` 미러 완료.

### 9-3. PIE (verifier)

**P1-P01 PASS**: `State|event=INIT|mode=FRESH` + `State:Init:t=0` 이후 **BattleLog 0줄** = 자동 전투 미실행. **2회 재현.**

### 9-4. 오너 육안 (2026-07-16 23시경) — 전부 PASS

| # | 확인 항목 | 결과 |
|---|---|---|
| 1 | 자동시작 0 · 박스 "Start" | PASS |
| 2 | Start→턴 시작+메뉴 | PASS |
| 3 | 박스 "Cancel" 且 **실제 클릭됨**(최대 회귀 지점 — 콜리전 복구 실증) | PASS |
| 4 | 적 클릭→데미지 | PASS |
| 5 | 전투 끝→"End"→Start 대기 | PASS |

오너 코멘트: *"전부 완료(문제 없음, 일단 기본 공격만 사용)"*

### 9-5. T1 실증 (Director 로그 대조)

`projectTP.log` 22:57~22:58 KST 세션:

- `BattleLog|turn=15|attacker=SpawnPoint_Party_A1|target=SpawnPoint_Enemy_B1|action=31000000|dmg=30|hp=0|died=true` → **메뉴 경유 기본공격 dmg=30 = 원장 값 그대로**.
- `State|turn=17|event=BATTLE_END|winner=A` → `State|event=INIT|mode=RESTART` → `State:Init:t=125.902` → **그 뒤 BattleLog 0줄** = **End 클릭 후 자동 재시작 안 함**(파트1 목적 실증).
- 상태 전이 정상: AwaitCommand → AwaitTarget → TurnEnd → TurnStart 순환.
- 부수: 베기(42)·파이어볼(65)·ATK_DOWN 롤도 정상 동작 확인(오너가 함께 사용).

### 9-6. ★23턴 diff 0 — 오너 결정으로 파트2 이월

원래 파트1 최강 게이트(§7, [[파트1_Start_TC]] P1-R01)였으나, **오너 결정**(2026-07-16): *"T1만 실증, 23턴은 파트2에서."*

근거:
1. 파트1이 데미지·턴순환 코드를 무접촉했음은 **핀 원문으로 이미 증명**(§9-1, [[파트1_Start_TC]] P1-G20).
2. 지금 23턴을 뽑아도 파트2(SPD 정렬)가 순서를 바꿔 곧 무효화된다 — 곧 버릴 데이터.
3. 폴백 제거로 이제 메뉴 클릭 46회가 필요해 자동화 비용이 크다.

파트2에서 새 원장 수집 시 **한 번에** 처리한다.

### 9-7. Director 판정 1건 — TC 문구 결함

`P1-G13`이 *"`EnterAwaitCommand.CallFunction_4.type_id == '|HideAll'`"*를 **노드 ID 문자 그대로** 요구했으나, **`delete_node` 금지 정책 + 노드 함수 retarget 도구 부재**로 문면 그대로는 만족 불가하다. 실측상 의도는 완전 충족(`ShowAttack` 도달 불가·`HideAll` 활성) → **Director가 PASS 판정**.

qa-critic 스스로 세운 N13(*"노드 **수** 기반 판정 금지"*, [[파트1_Start_TC]] N13)과 **같은 부류의 결함** — 노드 ID 기반 판정도 정책과 양립 불가하다. → TC 문구를 *"체인에서 도달 가능한 `Show*`/`HideAll` 호출이 `HideAll` 하나"*로 정정([[파트1_Start_TC]] P1-G13에 반영 완료).

### 9-8. 개발자가 정직하게 올린 이탈 3건 (전부 Director 수용)

1. **작업12 목적지**: 기존 "IsValid 실패 → 로그+정지" 템플릿이 없어 신규 PrintString 4개 생성(N6 준수 = 상태 전이 없음).
2. **`P1-P01` 보강 LOG**(`State|event=INIT|mode=FRESH`)는 12작업 목록 밖이라 미추가 — 단 **실제 로그엔 이미 존재**(⑤ 로그보강 산출물). 주 판별자 `bInputLocked==true`는 작업7이 제공.
3. **도구 버그**: `AssetTools.update_metadata_tags`의 `remove_tags`가 `set_tags`를 함께 줘도 `set_tags:null`을 주입해 실패 → 무해한 `_dirty_touch` 마커 존치(유사 마커 존치 선례 있음). → [[언리얼_MCP_실전노하우]] §34(83)에 반영 완료.

---

## 10. 다음 단계

파트1 게이트 통과 — **파트2(SPD 턴 순서 정렬) 착수 가능**. 파트2 착수 시 SPD 정렬 후 재계산된 턴 순서로 원장을 새로 수집해 §9-6이 이월한 diff-0 검증을 대체한다.

---

## 관련
- [[파트1_Start_TC]] · [[plan]] · [[청사진]]
- [[야간F9a_풀회귀_완료]] · [[야간F7a_스킬메뉴_완료]] · [[야간④_End버튼_완료]] · [[야간작업_총결산_2026-07-16]]
- [[언리얼_MCP_실전노하우]] §34
- 정정 반영: [[features/걸어나오기연출/raw/W2_Executing개편|W2_Executing개편]] · [[features/걸어나오기연출/TC|걸어나오기연출 TC]] (TurnQueue 속도정렬 오진 정정)
