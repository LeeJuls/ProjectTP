---
type: plan
feature: 턴제전투MVP
status: 진행중
updated: 2026-07-07
---

# 📋 턴제전투MVP 세부 plan

> 청사진: [[청사진]] · 프로세스: [[개발_워크플로우]]
> **원본**: 이 문서는 오너 승인 세션 plan(`C:\Users\user\.claude\plans\humble-purring-glacier.md`, 파일명 "humble-purring-glacier")의 전사본이다. 승인판이 원본이며 모순 시 그쪽이 우선한다.
#projectTP/턴제전투MVP

## Context (원문)
4v4 배치(배치_1) 위 첫 전투 마일스톤. **오너 확정**: 턴이 캐릭터 하나씩 순환, 자기 턴에 Attack 버튼 → 적 타겟 클릭 → 공격 모션 → 피격 모션 → 다음 턴. **전원 수동 핫시트**(적 턴도 오너 조작, AI 없음). 데미지/HP/사망/이동연출 ❌, 무한 순환. MVP 후 "구조 재정비 vs 진행" 결정 예정 → **교체 가능 경계**(턴 로직=Manager 내부만, 유닛=얇은 인터페이스, 입력=클릭 이벤트)로 짓는다. 실행 전부 sonnet/haiku.

이 판은 **system-ui-designer 설계 + gameplay-engineer(GE) 실현성 검증 + qa-critic(QA) 적대 검수** 통합 — 설계의 미확인 전제 2건(커스텀이벤트 파라미터·enum)을 실측으로 적발·우회 확정했고, RetriggerableDelay 레이스는 **큐 계산으로 무충돌 증명**(최소 마진 0.35s)됨.

## 확정 사실·실측
- 애니(8종 균일): IDLE1 Row0 6f / ATK1 Row5 6f(타이머 0.70s) / **HURT Row12 4f(타이머 0.45s = 4/8−0.05, QA-H1 단일화)**
- 재사용: MID SetScalar 패턴(TimeOffset→FrameCount→RowIndex, 오철자 무음무시), RetriggerableDelay, EmissiveBoost 파라미터(기존), ClickBox 콜리전(QueryOnly+Visibility Block), ST_UI, 배치_1
- **MCP 제약 실측(GE)**: enum 생성 불가→**byte**(GE-C1) / 커스텀이벤트에 오브젝트 파라미터 불가→**NotifyUnitClicked는 Function Graph로**(GE-C2, E0 파일럿 최우선) / 링 프리미티브 없음→원판 발광 마커(GE-H1) / **런타임 SetText 무반영→라벨은 TextRender 2개(에디터 프리셋 "Attack"/"Cancel")+SetVisibility 토글**(GE-1) / 오브젝트 배열 변수 가능(ARRAY)하나 원소는 **인덱스별 개별 set_properties+파일럿**(GE-H3) / **GetAllActorsOfClass 금지(순서 무보장)** — 큐는 instance-editable 배열 수동 지정(GE-M1)

## 설계 확정판 (QA 필수수정 7건 반영)

### 상태머신 — BattleState: byte 0~5 (Manager 소유, 종료 상태 없음=무한 순환)
| # | 상태 | 진입 액션 | 허용 입력 | 전이 |
|---|---|---|---|---|
| 0 | Init | **전 유닛 self-register 8/8 완료 게이트 후**(QA-H5: BeginPlay 순서 비의존) 큐 빌드(null 슬롯 compact 제외), i=0, 전 유닛 발광0·마커 숨김, 잠금 | 없음 | → TurnStart. **큐 길이 0이면 에러 로그·정지**(QA-M1) |
| 1 | TurnStart | ActiveUnit=큐[i], 마커 ON(팀색), 잔여 하이라이트 OFF, 잠금 유지 | 없음 | 즉시 → AwaitCommand |
| 2 | AwaitCommand | **단일 진입 함수 EnterAwaitCommand()가 항상 잠금 해제**(QA-C3: 해제를 Delay 체인 성공에만 의존 금지), 버튼 표시(라벨 "Attack" = TextRender A 가시), SelectedTarget=null | 버튼 클릭만 | 버튼 → AwaitTarget |
| 3 | AwaitTarget | 상대팀 4기 EmissiveBoost ON(정적), 라벨 "Cancel"(TextRender B 가시·A 숨김) | 상대팀 유닛 클릭 / 버튼(취소) | 유효 타겟 → Executing / 취소 → AwaitCommand(**발광 전체 OFF 명시**, QA-M1-14) |
| 4 | Executing | **핸들러 최선두에서 bInputLocked=true(상태 전이보다 먼저 — QA-C2 이중진입 차단)**, 발광 OFF, 버튼 숨김+**콜리전 OFF 동반**(QA-M2), PlayAttack() → Sequence 분기: Delay(0.25)→**IsValid(SelectedTarget) 가드(QA-C1)**→TakeHit() / Delay(0.75)→TurnEnd | 없음(전 클릭 무시) | 체인 완료 → TurnEnd |
| 5 | TurnEnd | **① ActiveUnit 마커 OFF → ② i=(i+1) % 큐실제길이**(순서 고정 QA-H4, **modulo 상수 8 금지** QA-M1-11), Delay(0.35) | 없음 | → TurnStart. ActiveUnit null이면 즉시 skip |

### 타이밍 (1턴 ≈1.10s)
ATK 시작 t=0(0.70s 타이머) / **임팩트 t=0.25s에 TakeHit**(공격 중반 싱크 — 옥토패스 체감) / 피격 타이머 0.45s → 둘 다 t≈0.70 idle 복귀 / t=0.75 TurnEnd / +0.35s → 다음 턴. **레이스 무충돌 증명(QA)**: 피격 유닛의 자기 턴 PlayAttack은 최소 t+1.10 — TakeHit revert(t+0.70)와 ≥0.35s 마진(전제: TurnEnd 0.35s 스킵 불가+잠금 유지 — 이동연출 삽입 시 재검증, QA-H2 스텁 불변식).

### 입력·UI 정책
- 유효 타겟=상대팀만(**bIsParty(bool) 판정** — 이름 파싱 금지). 아군/자신 클릭 무시(무피드백, 폴리시 이월).
- 취소=버튼 재클릭 단일안. 연타=상태 왕복(무해, 프레임 홀짝 이슈는 TC-22/35로 커버).
- 마커: 원판+Unlit 발광(링 불가 — GE-H1), **팀색 MID 컬러 파라미터 1개**(Party 청록/Enemy 주황), Z는 실측 스윕 보정(D2 라벨 사례). 화면에 항상 ≤1개.
- 모드 구분 2중화(QA-H3): 라벨(Attack/Cancel) + 상대 4기 발광=타겟 모드 신호.
- 로컬라이제이션: `Battle.Cancel` 키 신규(ST_UI). TextRender B에 에디터 LOCTABLE 임포트로 세팅(검증된 경로).

### 엣지 규칙 (설계 10 + QA 추가 11~14)
연출 중 클릭 무시 / 연타 무해 / 타겟팅 중 버튼=취소 / 큐 구조상 연속 동일 턴 불가 / PIE 재시작 Init 능동 리셋 / null 슬롯 compact+skip / Executing 진입 불변식(SelectedTarget non-null)+IsValid 이중 방어 / **11: 큐 길이 0 가드·modulo=실길이** / 12: 타겟 0기(사망 확장 시) 이월 / **13: 버튼·유닛 ClickBox 화면 비중첩 확인** / **14: 취소 경로 발광 OFF**

## 구현 명세 (신규 산출물)
- **BP_BattleManager**(신규 액터, 레벨 1개): 변수 BattleState(byte)·bInputLocked(bool)·CurrentIndex(int)·TurnQueue(BP_BattleSpawnPoint ref **배열**, instance-editable — 원소 8개는 레벨에서 A1,B1,A2,B2.. 순 수동 지정, 인덱스별 개별 세팅)·ActiveUnit·SelectedTarget(ref)·RegisteredCount(int) / **NotifyUnitClicked(Unit ref) = Function Graph**(GE-C2)·NotifyAttackButtonClicked·상태 진입 함수들(EnterAwaitCommand 단일화) / Executing 타이머는 Sequence 분기(fan-out 금지, add_node_pin으로 핀 추가)
- **BP_BattleSpawnPoint 확장**(CS 무변경): TakeHit(HURT 패턴, declaring_class 명시)·SetTurnMarker(bool)·SetHighlight(bool→EmissiveBoost)·bIsParty(bool, instance-editable)·TurnMarker 컴포넌트(원판+M_UI_TurnMarker Unlit 발광, MID 컬러)·ClickBox(BoxComponent 몸통 크기)+OnClicked→Manager.NotifyUnitClicked(self)·BeginPlay 끝에 Manager에 self-register. dangling Tick/ActorBeginOverlap 스텁 삭제.
- **BP_AttackButton 재배선**: TargetSpawnPoint.PlayAttack 직결 **제거**(유령 공격 방지 — GE-7) → Manager.NotifyAttackButtonClicked. Label(기존 "Attack")+**LabelCancel(TextRender 신규, 에디터 프리셋 "Cancel")** SetVisibility 토글. Manager ref(instance-editable).
- 스트링테이블 `Battle.Cancel` / 마커 머티리얼 M_UI_TurnMarker / 레벨: Manager 1기 배치+refs.

## 단계·게이트 (TC는 qa 35종 — E0에서 기능폴더 문서로 전사)
| 단계 | 내용 | 게이트(핵심 TC) | 담당 | 상태 |
|---|---|---|---|---|
| E0 | **파일럿 프로브**: ①Function Graph+add_object_function_param+compile(GE-C2 — 실패 시 즉시 중단·Director 보고) ②배열 원소 1~2개 인덱스별 세팅 ③byte 변수. + 기능폴더 `docs/features/턴제전투MVP/` 생성(청사진·설계·TC 전사) | 프로브 3종 성공 | ge(sonnet) | **완료** — 프로브 3종 모두 성공(원소 세팅 문법은 실측과 상이, [[raw/E0_프로브]] 참고) |
| E1 | 유닛 확장(TakeHit·마커·하이라이트·ClickBox·bIsParty·register) | TC-01~10: TakeHit 0.45s·IsValid 가드·양 RetrigDelay 무충돌·마커 팀색·아군클릭 무시·**village/배치도구 회귀** | ge(sonnet)→verifier(haiku) | **구현 완료(자가검증 부분적)** — BeginPlay 확장(마커 트랜스폼·팀색·ClickBox) 배선·컴파일 0, 손상 인스턴스 오버라이드 8기 전량 복구, bAbsolute* 플래그로 비균등스케일 전단 해결. 스캐폴드 제거·저장 완료. **PIE CaptureViewport 캡처 신뢰성 미해결로 verifier 정밀 재검증 필요**([[raw/E1_유닛확장]] 참고) — TC-01~08은 verifier가 PIE get_properties 직접 재조회로, 시각 확인은 에디터 레벨 우회 캡처 또는 오너 육안 권장 |
| E2 | Manager 상태머신+큐+버튼 재배선 E2E | TC-11~19: 등록 8/8 게이트·1턴 흐름 타임스탬프·**최속 8턴 무충돌**·마커 1개 불변·modulo 실길이·null skip | ge(sonnet)→verifier(haiku) | **구현 완료(자가검증 부분적)** — InitBattle·5개 상태 진입 함수/이벤트·NotifyUnitClicked·NotifyAttackButtonClicked·BP_AttackButton 3함수 전부 배선·컴파일 0. 스캐폴드 2턴 자동진행 PIE 검증: TC-11·12·19·무효입력 PASS. **TC-13(타이밍) 재현성 있는 편차(Executing+0.25s·TurnEnd+0.317s) 원인 미규명으로 보류. TakeHit 재측정 중 SpriteMID 런타임 무효화라는 신규 회귀 발견(BP_BattleSpawnPoint 소관, PlayAttack 애니메이션도 영향받을 가능성) — verifier 정밀 재검증 및 F단계 전 재조사 필수**([[raw/E2_상태머신]] 참고) |
| E3 | 폴리시·엣지(잠금 순서·취소 발광 OFF·숨김 콜리전·재시작 리셋)+풀 회귀 | TC-20~35: 이중진입 방지·잠금 순서 정적 확인·상태누수·**공격버튼데모 회귀·배치_1 회귀·village 최종** | ge→verifier | **개발+자가검증 완료** — TC-08·13(부분)·14·16~18·20~25·30~34 전부 PASS(스캐폴드+정적 확인, [[raw/E3_게이트]] 참고). 직전 세션의 240초 워치독 잔여 스캐폴드(BeginPlay 오염 48노드) 전수 복구 후 재실행. TC-13은 재현성 있는 편차 관찰되나 로직 실패로 이어지지 않음(보류). TC-28/29/05·06·07(육안·장기)은 F단계로 이월. **verifier 실증 및 Director 게이트 판정 대기** |
| F | **오너 라이브 확인**(PIE 직접 핫시트 플레이 — 스크린샷 없음) + 방향부합 판정 → 이후 "구조 재정비 vs 진행" 논의 | TC-M-방향부합 | 오너+Director | 라이브 테스트에서 확정된 결함 5건(치명 2·시인성 2·정리 1)+보너스 로그 1건 핫픽스 완료 — **①Sprite/TurnMarker 콜리전 NoCollision화(클릭 방패 해소) ②LabelCancel 트랜스폼·텍스트·색상 Label 기준값과 완전 일치화(§7 함정③ 재현·우회) ③마커 스케일 확대(0.5,0.35→1.2,0.8) ④하이라이트 EmissiveBoost 2.0→6.0 ⑤State 디버그 프린트 10개 노드 Screen=false 통일(Log=true 유지) +보너스: NotifyUnitClicked 유효클릭 경로 로그 신규**. 3 BP 컴파일 에러 0, 관련 에셋 전부 dirty=false 확인, [[raw/F_라이브결함]] 참고. **화면출력 미노출·클릭 경로 실동작의 시각 확인은 지시에 따라 스캐폴드 없이 오너 실플레이로 이월** — 오너 판정 대기 |

## 검증 방침 (QA-H6 — 어기면 전 TC 무효)
- **런타임 상태(BattleState·잠금·큐·MID 파라미터)는 get_properties로 읽으면 에디터 스냅샷만 나옴** → 판정은 **PrintString+GetLogEntries 로그 매칭** 또는 **오너 육안**만. get_properties는 정적 프로퍼티(그래프 노드 값·콜리전 설정·마커 색 소스)에만.
- 결정적 트리거 필요 시 임시 스캐폴드(BeginPlay+Delay) 심고 제거(D3 정석). village 회귀는 각 게이트 맨 마지막.
- 컴파일은 매 단계 warnings_as_errors 에러 0.

## 산출물·문서·커밋
기능폴더 `docs/features/턴제전투MVP/`(청사진·설계 문서·TC·raw 로그 — E0부터). 커밋 `[C] feat(턴제전투MVP): ...` 단계별, push는 오너 확인. 신규 노하우는 실전노하우.md에.

## 비범위
데미지·HP·사망·승패 ❌ / 걸어나오기 연출 ❌(Executing 삽입 지점 예약 — 삽입 시 레이스 마진 재검증 필수) / ATB ❌(TurnStart 선택 로직 교체 지점 예약) / AI ❌ / 무효클릭 피드백·발광 펄스·장기 float(TC-29 관찰만) 폴리시 이월.

## 진행 체크리스트
- [x] E0 파일럿 프로브 3종 + 기능폴더 문서 생성
- [x] E1 개발 (마커/클릭박스 배선·손상복구·bAbsolute* 해결 — [[raw/E1_유닛확장]])
- [ ] E1 게이트 통과 (verifier 실증 → Director 판정 — PIE 캡처 신뢰성 이슈 감안 필요)
- [x] E2 개발 (Manager 상태머신 전체 구현·자가검증 — [[raw/E2_상태머신]])
- [ ] E2 게이트 통과 (verifier 실증 → Director 판정 — SpriteMID 회귀는 후속 세션에서 완전 규명·기각됨, [[raw/E2_상태머신]] "E2-후속" 참고)
- [x] E3 개발 (폴리시·엣지 전체 구현·자가검증, 직전 세션 워치독 잔여 복구 후 재실행 — [[raw/E3_게이트]])
- [ ] E3 게이트 통과 (verifier 실증 → Director 판정 대기)
- [x] F 라이브 결함 핫픽스 5건+보너스 1건 (클릭방패·LabelCancel·마커확대·하이라이트강화·프린트정리 — [[raw/F_라이브결함]])
- [x] 전투 로그 파일 기록 (화면표시 없음, BattleLog| 라인+추출스크립트, TurnCounter 변수 신규 — [[raw/전투로그]])
- [ ] F 오너 라이브 확인 + 방향부합 판정
- [x] VFX 임시통합 1단계: Smear/Hit 텍스처·MI 임포트 (오너 방침 "눈 구별만" — [[raw/VFX_임시통합_방침]])
- [x] VFX 임시통합 2단계: BP_BattleSpawnPoint EffectQuad+MID 배선, PlayAttack/TakeHit Sequence 분기 재생, 임시 스캐폴드 2턴 검증 후 제거 — [[raw/VFX_임시통합_방침]] "2단계 배선 완료" 참고. VFX 시각 판정(눈 구별 수준 충족 여부)은 오너 육안 이월
