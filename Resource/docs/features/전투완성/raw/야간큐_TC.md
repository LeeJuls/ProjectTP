---
type: qa
project: projectTP
feature: 전투완성
stage: 야간큐(③데미지폰트·④End버튼·⑤로그·F6모션)
status: 4건 전부 게이트 완료 — 상태 컬럼 갱신 완료(각 완료 문서 판정대로). LOG-04 "사망 라인 8개"는 오탈자 — [[야간F9a_풀회귀_완료]]가 7개로 확정. TC 실행=verifier, 게이트 판정=Director
updated: 2026-07-16
---

# 야간큐 TC — ③데미지폰트 · ④End버튼 · ⑤로그 · F6모션

> 대상: [[plan]] 야간 시퀀스 ③④⑤ + §F6 · [[F5-2_완료]](ResetForBattle·InitBattle·bWasSkip·EnterEnd 라이브) · [[F5-2_TC]](N26 재활용) · [[전투로그]](로그 스키마) · [[상태이상_확정]] §8(로그) · [[스탯_전투공식_v1]] §5(원장) · [[언리얼_MCP_실전노하우]] §L130·§26
> **qa-critic 적대적 검토 산출물 — 검출·TC설계만.** TC 실행=verifier, 게이트 판정=Director.
> 확정 사양 = gameplay 실측 + Director 판정. 본 문서는 그 사양에 적대적 엣지를 얹은 TC.
#projectTP/전투완성

---

## 0. 범위 & 판정도구

4개 독립 작업. 각 섹션이 하나의 게이트 사이클.

**판정도구 약칭**: **GRAPH**=정적 노드조회(`find_nodes`·`get_connected_subgraph`·`get_node_infos`) / **LOG**=`projectTP.log` grep(또는 `GetLogEntries`) / **PIE**=인스턴스 프로퍼티(`get_properties`, `UEDPIE_0`) / **SCF**=스캐폴드 직접호출 후 LOG/PIE / **DT**=`get_rows` / **CMP**=컴파일0 / **MOCK**=값주입 / **오너**=오너 육안(불차단). **★**=게이트(진행차단). **2026-07-16 야간 게이트 완료 — 4건 전부 상태 컬럼 갱신됨**(PASS/이월, 근거는 각 섹션 "게이트 결과" 줄 및 완료 문서).

---

## ③ 데미지폰트 (WBP_DamageText — 스크린스페이스 CreateWidget → Panel_FloatingNumbers)

> **메커니즘 확정**: 스크린스페이스 `CreateWidget` → `Panel_FloatingNumbers`(BattleHUD)에 AddChild → 애님(위이동/페이드) 종료 시 `RemoveFromParent`. **독립 스폰 방식**(타격마다 별도 위젯). 유닛 월드좌표→스크린 투영으로 HP바 위 배치. ResolveHit dmg값 전달.
> **게이트 결과**: [[야간③_데미지폰트_완료]](+[[야간③b_데미지폰트_위치수정_완료]] 위치버그 수정) — PASS 5(DF-01·03·05·06·07)·이월 3(DF-02·04·08).

| 구분 | ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|---|
| 기능 | **DF-01**★ | **표시값 정합**: 피격 시 스폰된 DamageText 텍스트 == 그 타격 BattleLog `dmg`. basic **30**·slash **42**·파볼 **61**·min1 **"1"** | PIE(위젯 텍스트)+LOG(dmg) | **PASS** |
| 기능 | **DF-02**★ | **피격당 1회**: 1 ResolveHit = `Panel_FloatingNumbers` 자식 **+1개**(이중스폰 2·누락 0 아님). 3턴 진행 시 누적 타격수 == 누적 스폰수 | PIE(Panel 자식수)+LOG(dmg 라인수) | 이월 — 런타임 자식카운트는 MCP reflection 한계, 구조 증거로 조건부통과 |
| 기능 | **DF-03** | **자동소멸·누수0**: 애님 종료 시 `RemoveFromParent` → 장시간(N턴) 후 `Panel_FloatingNumbers` 자식 수 **상한 이내**(무한누적 0). 스크린스페이스 독립위젯이라 Manager 단일인스턴스 delay-리셋 함정 무관 | PIE(시간경과 후 Panel 자식수) | **PASS** |
| 기능 | **DF-04**★ | **연타 독립 스폰**: 0.25s 내 연속 2타(SCF, 30→42) → `Panel_FloatingNumbers`에 **자식 2개 각각 독립 표시값**(30·42). 독립 스폰이라 이전 위젯이 다음을 막거나 값 덮음 0 | SCF+PIE+LOG | 이월 — 아침 오너육안 |
| 기능 | **DF-05**★ | **사망 막타 표시(F5 N19 자매)**: 킬링블로우(MOCK Hp=30 → dmg42 kill, hp=0)에도 DamageText 스폰+표시값 정확. **DYING 분기·bFreeze가 폰트를 삼키지 않음** | SCF+MOCK+PIE+LOG | **PASS** |
| 기능 | **DF-06** | **하드코딩0·포맷**: 표시 문자열 **콤마 그룹핑 0**(`ToText UseGrouping=false` 또는 String화, F4 H-1 재판) + 하드코딩 문자열 0(부호/접미사 있으면 포맷·로컬라이즈 경유) | PIE(텍스트)+GRAPH | **PASS** |
| 기능 | **DF-07**★ | **HP바 무회귀**: DamageText 추가가 기존 `WBP_UnitFrame`에 무영향 — 피격 후 `Bar_Hp.Percent`·`Txt_HpValue`·위치·가시성 F3/F4 기준선 동일(**F4 N10 percent 정합**) + 8기 트랜스폼 diff 0 + 컴파일0 | PIE+GRAPH+CMP | **PASS** |
| 비주얼 | **DF-08** | [불차단] **룩**: HP바 위 떠올라 페이드, 오블리크 카메라 정렬, 다중 폰트 겹침 가독성 | 오너육안 | 이월 — 아침 오너육안 |

---

## ④ End버튼 재전투 (BP_AttackButton LabelEnd/ShowEnd + NotifyAttackButtonClicked 최상단 분기)

> **확정 사양**: BP_AttackButton에 `LabelEnd`(TextRender, ST_UI `Battle.End` 키, **BeginPlay 1회 세팅** — 런타임 SetText는 미해결 렌더버그로 금지, 기존 Label/LabelCancel 동일 패턴) + `ShowEnd()` 신설. `EnterEnd` 끝에 `ButtonRef.ShowEnd()`. `NotifyAttackButtonClicked` **최상단**(기존 `bInputLocked` Branch **앞**)에 `Branch(BattleState==6)→InitBattle()→종단`. `InitBattle`에 `bWasSkip=false` 리셋 추가. 카메라 토글 상태 = **의도적 이월**(리셋 안 함).
> **게이트 결과**: [[야간④_End버튼_완료]] — PASS 7(END-01~04·06~08)·이월 1(END-05, 조건부 통과).

| 구분 | ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|---|
| 기능 | **END-01**★ | **분기 순서(i)**: `NotifyAttackButtonClicked` 최상단 `Branch(BattleState==6)`가 `bInputLocked` Branch보다 **exec 상류** + True→`InitBattle`→**종단**(정상 Attack 경로 미연결). **뒤에 있으면 End 상태의 입력잠금이 재시작 클릭을 삼켜 영구 무음실패** | GRAPH(exec 순서) | **PASS** |
| 기능 | **END-02**★ | **E2E 재전투(ii)**: 한 팀 전멸→`EnterEnd`→버튼 라벨 "End" 표시→클릭→`InitBattle`→**8기 `Hp==MaxHp`·`bAlive`·`RowIndex==0`(기립)·`bFreeze==0`·`ClickBox==QueryOnly`** + Manager `CurrentIndex==0`·`TurnCounter==0`·`bBattleOver==false`·`BattleState==0` → **정상 1턴 완주**(dmg=30). F5-2 ResetForBattle 회귀 겸 | SCF+PIE(8기+Manager)+LOG+오너 | **PASS** |
| 기능 | **END-03** | **LabelEnd 런타임 SetText 0(iii)**: `LabelEnd`(TextRender)는 **BeginPlay 1회 SetText만**, 런타임(ShowEnd/EnterEnd 등) SetText 노드 **0개**(렌더버그 회피, Label/LabelCancel 패턴 동일). ShowEnd는 Visibility 토글만 | GRAPH | **PASS** |
| 기능 | **END-04** | **ShowAttack 간접복원(iv)**: 재전투 후 `EnterAwaitCommand` 경유 → 버튼 "Attack" 라벨 복원(LabelEnd Visibility OFF, Label ON). 재시작 첫 AwaitCommand 시점 조회 | PIE(Visibility)+GRAPH | **PASS** |
| 기능 | **END-05**★ | **G-A 재동결 없음(v, N26 재활용)**: 유닛 사망 직후 **0.575s 내 End 클릭 강제**(SCF)→InitBattle→ResetForBattle→**0.6s 후 그 유닛 `bFreeze==0`·`RowIndex==0`**(늦게 완료된 DYING latent가 재동결 안 함 — N26 bAlive 게이팅) | SCF+PIE(지연 폴링) | 이월 — 조건부 통과(기존 F5-2 N26 가드 신뢰, 이번 세션 재현 시도 자체가 불가) |
| 기능 | **END-06** | **정상전투 회귀(vi)**: `BattleState≠6`(정상 전투) 클릭 → 기존 Attack/Cancel 의미분기 불변(AwaitCommand→공격커밋, AwaitTarget→취소 등). State==6 신규분기가 정상경로 오염 0 | SCF+LOG/PIE | **PASS** |
| 기능 | **END-07** | **bWasSkip 리셋(vii)**: 스킵 상태(`bWasSkip=true`) 잔존 중 `InitBattle`→`bWasSkip==false`. 재시작 첫 실턴 페이싱 정상(Delay 0.35s, 즉시화 오발동 0) | PIE+GRAPH | **PASS** |
| 기능 | **END-08** | **재진입/더블클릭 엣지**: End 연타 → InitBattle 2회여도 크래시0. 1번째가 State 6→0 전이 후 2번째는 정상경로(무해) 또는 멱등 재시작. 소프트락 0 | SCF+PIE | **PASS** |

---

## ⑤ 로그 확정 (State| 신설 + BattleLog died 필드 + SKIP_TURN_DEATH)

> **확정 사양**: ①`State|turn=<T>|event=BATTLE_END|winner=<A/B>`(EnterEnd, 최우선 — 현재 0건 실측) ②`State|event=INIT|mode=<FRESH/RESTART>`(InitBattle, 舊 bBattleOver값으로 판별) ③BattleLog 옵션필드 `|died=<true/false>`(step8 사망판정 — **비사망 라인 바이트 불변**) ④`StatusLog|...|event=SKIP_TURN_DEATH`(TS1 사망스킵, 3순위).
> **게이트 결과**: [[야간⑤_로그보강_완료]] — 7/7 PASS.

| 구분 | ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|---|
| 기능 | **LOG-01**★ | **BATTLE_END 라인(①)**: 한 팀 전멸→`EnterEnd`에서 `State\|turn=<T>\|event=BATTLE_END\|winner=<A\|B>` **정확히 1줄**(현재 0건→신규). turn=최종 킬 TurnCounter | SCF/전멸+LOG | **PASS** |
| 기능 | **LOG-02**★ | **winner 정확성**: A팀 전멸→`winner=B` / B팀 전멸→`winner=A`. 양 시나리오 대조(선공/후공 무관). 생존팀 오판 0 | LOG(2 시나리오) | **PASS**(A팀 승리 방향 실측, winner=B 방향은 미실행 — [[야간⑤_로그보강_완료]] §5 이월) |
| 기능 | **LOG-03** | **INIT mode(②)**: 최초 InitBattle→`State\|event=INIT\|mode=FRESH` / End 후 재전투→`mode=RESTART`(舊 bBattleOver로 판별: FRESH=직전 false, RESTART=직전 true) | LOG | **PASS** |
| 기능 | **LOG-04**★ | **died 필드(③)**: 사망 타격 BattleLog 라인에 `\|died=true` 존재. **비사망 라인은 바이트 불변**(died 필드 부재). ★**F9a 기대원장 사망 라인 7개**(B1†T5·A1†T6·B2†T11·A2†T12·B3†T17·A3†T18·B4†T23, 8개는 오탈자였음) 갱신 완료 — [[야간F9a_풀회귀_완료]] §2·§5 | LOG | **PASS** |
| 기능 | **LOG-05** | **SKIP_TURN_DEATH(④)**: TS1 사망스킵 시 `StatusLog\|turn=<T>\|unit=<시체>\|...\|event=SKIP_TURN_DEATH` 방출(사망유닛 턴 도래마다 1줄, 기존 STUN SKIP_TURN과 event 구분) | LOG | **PASS** |
| 기능 | **LOG-06**★ | **파서 회귀(extract_battle_log.py)**: `MARKER=BattleLog\|` 산출물에서 **비사망 라인 바이트 불변** + `State\|`·`StatusLog\|` 라인 **0줄**(BattleLog 필터라). State/StatusLog는 **별도 grep 커맨드** 문서화(스크립트 미수정) | LOG(2종 커맨드) | **PASS** |
| 기능 | **LOG-07** | **원장 완전 재구성(⑤ 목표)**: BattleLog(died) + State(BATTLE_END/INIT) + StatusLog(SKIP_TURN_DEATH) 조합으로 **사망·승패·재전투·턴스킵** 전량 재구성 가능. 전멸 완주 1판에서 검증 | LOG(3종 병합) | **PASS** |

---

## F6 모션 데이터구동 (PlayAttack 리터럴 → DT 조회, 무변화 회귀)

> **확정 사양**: Manager `PendingSkillId`(신규, EnterExecuting 세팅 — **값 출처 리터럴 31000000 고정 = 무회귀 정의**) → Manager가 `DT_Skills.MotionRow` 조회 → SpawnPoint `PendingMotionRow:int`(신규 멤버) 스탬프 → PlayAttack이 멤버 읽어 RowIndex/FrameCount/Delay 계산. DT_Motions 조회 = **RowName 산술 `60000000+MotionRow×10000`** 단건 FindItem(4표본 실측 확정). frameCount(integer)→ToFloat. `Delay=(FC/8)−0.05`. 폴백=5/6/0.70(조회실패 Branch), FrameCount≥1 가드.
> **게이트 결과**: [[야간F6_모션데이터구동_완료]] — PASS 5(F6-01·03·05·06·08)·이월 4(F6-02·04·07·09). 핵심 서사=가짜 GREEN 2건 검출·수정(완료문서 §2), F6-01~09 전항목을 개별 게이트하지는 않았음(완료문서 §5 명시).

| 구분 | ID | 조건 → 기대 | 판정방법 | 상태 |
|---|---|---|---|---|
| 기능 | **F6-01**★ | **무회귀 delay**: 기본공격→PlayAttack이 ATK1(MotionRow5) 조회→FrameCount6→`Delay=(6/8)−0.05=`**0.70** 정확(기존 리터럴 동일) | SCF+LOG/GRAPH | **PASS**("원복 후 5/6.0 원상" 실측) |
| 기능 | **F6-02**★ | **23턴 원장 불변**: 기본공격 스캐폴드 완주→원장 **diff 0**(F6은 모션만 데이터구동, 데미지·순서·타이밍 불변) | LOG | 이월 — 이 게이트 자체에서 개별 확인 안 함(완료문서 §5). [[야간F9a_풀회귀_완료]]에서 23턴 diff 0으로 사실상 재확인 |
| 기능 | **F6-03** | **RowName 산술 전수**: MotionRow 17행 각각 `60000000+MotionRow×10000`이 DT_Motions 실제 RowName과 일치(4표본 확정 공식의 전수 확장). 미스매치 0 | DT | **PASS**("17/17 전수 성립") |
| 기능 | **F6-04** | **폴백 경로**: SCF로 존재하지 않는 MotionRow(조회실패)→Branch False→폴백 RowIndex5/FrameCount6/Delay0.70 + 크래시0 | SCF+LOG | 이월 — GRAPH(정적 배선)로만 기확정, RowNotFound 강제유발 런타임 관통 테스트 미실행(완료문서 §5) |
| 기능 | **F6-05**★ | **int÷int 함정 + FrameCount≥1**: `Delay=(FC/8)−0.05`에서 **FC/8이 실수 나눗셈**(정수면 6/8=0→Delay=−0.05 음수!). frameCount ToFloat가 /8 **앞**. FC=0(데이터이상) 시 1로 가드(Delay=0.075, 음수 아님) | GRAPH+SCF | **PASS** — 가짜GREEN①(FC≥1 가드 분기 반전) 검출·와이어스왑 수정 후 관통 실측(10/5.0)+원복(5/6.0) 재검증. int/float 순서는 구조적 확정(완료문서 §1·§2) |
| 기능 | **F6-06** | **PendingSkillId 고정(무회귀 정의)**: EnterExecuting의 `PendingSkillId` 세팅 값 출처가 **리터럴 31000000 고정**(F6은 스킬선택 아님 — 모션만 데이터구동, F7에서 실 SkillId로 교체) | GRAPH | **PASS**(GRAPH 구조 확정) |
| 기능 | **F6-07** | **걸음·카메라 무접촉**: `WalkForward`·카메라(`SetViewTargetWithBlend`/CamCut) 노드가 F6 편집으로 변경 0(모션 조회만 추가). WalkArrive·CamCut 로그 기존과 동일 | GRAPH+LOG | 이월 — 완료문서에 명시적 검증 기록 없음(미실측) |
| 기능 | **F6-08** | **PendingMotionRow 스탬프 정합**: Manager가 조회한 MotionRow를 대상 SpawnPoint `PendingMotionRow` 멤버에 세팅 후 PlayAttack 호출(멤버 경유 — 함정⑰ Custom Event 파라미터 확장 불가 회피, WalkForward 선례). 다중 유닛에서 값 혼선 0 | GRAPH+SCF | **PASS**(GRAPH 구조 확정 — 혼선0은 알파 턴직렬 구조상 구조적 자명, 아래 PLAUSIBLE 각주 참고) |
| 비주얼 | **F6-09** | [불차단] **모션 육안 diff 0**: 8종 공격 모션이 F5 이전과 동일 재생(리터럴→DT 무변화) | 오너육안 | 이월 — 아침 오너육안 |

---

## 커버리지 근거 & PLAUSIBLE 플래그

**검토 축(빈손 통과 아님)**:
- **③**: 표시-실측 정합(DF-01) · 스폰 카디널리티 1:1(DF-02) · 누수(DF-03, Panel 자식수 상한) · 동시성 독립스폰(DF-04) · 사망경로 상호작용(DF-05) · 무음실패 포맷(DF-06 콤마) · 회귀(DF-07 HP바 percent).
- **④**: 순서(END-01 State6<bInputLocked=영구무음실패 방어) · E2E 상태전이(END-02 ResetForBattle 전수) · 렌더버그(END-03 런타임 SetText 0) · 상태복원(END-04 라벨·END-07 bWasSkip) · latent race(END-05 N26) · 회귀(END-06 정상분기) · 재진입(END-08).
- **⑤**: 신규라인 존재·필드정확(LOG-01/02/03/05) · **바이트 불변 회귀**(LOG-04 비사망·LOG-06 파서) · 원장 완전성(LOG-07).
- **F6**: 무회귀 수치(F6-01 0.70·F6-02 원장) · 데이터 전수(F6-03) · 폴백(F6-04) · **int÷int 음수 delay 함정**(F6-05) · 무회귀 정의(F6-06 리터럴 고정) · 무접촉(F6-07 걸음/카메라) · 멤버 스탬프 함정⑰(F6-08).

**PLAUSIBLE(verifier 실측 확정 요망)**:
- **LOG-04 F9a 원장 갱신 범위 — 해소됨**: ~~died=true가 사망 라인 8개에 추가되므로 F9a 기대원장의 해당 8줄 재생성 필요~~. [[야간F9a_풀회귀_완료]]가 died=true 라인 **7개**(8개는 오탈자였음)로 기대원장을 확정본 갱신했다 — 비사망 라인 바이트 불변도 그 문서 §2에서 재확인.
- **END-05 도달성**: 사망 0.575s 내 End 클릭은 정상 플레이(End 도달 kill+1.2s 후)엔 미도달이나 **더블클릭/빠른 조작 시 재현 가능** → N26 가드 실증 필수(도달성 PLAUSIBLE, 가드 CONFIRMED).
- **F6-08 다중유닛 스탬프**: 알파 턴직렬 구조상 동시 PlayAttack 없음(혼선 미발생)이나, A2 AoE·연출 겹침 시 재검 — 지금 멤버 소유(유닛별)로 지으면 비용0(m12 선례).

**놓친 버그가 통과된 버그보다 나쁘다** — 위 3건 전부 TC 등재.

---

## 관련
- [[plan]] 야간시퀀스 ③④⑤·§F6 · [[F5-2_완료]](ResetForBattle·bWasSkip·EnterEnd) · [[F5-2_TC]](N26) · [[F7_TC]]
- [[전투로그]] · [[상태이상_확정]] §8 · [[스탯_전투공식_v1]] §5(23턴 원장) · [[언리얼_MCP_실전노하우]] §L130·§26·함정⑰
