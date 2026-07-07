# 카메라액션 — 공격 액션 컷 (팀별 액션캠 2기, 오너 직접 배치)

> 승인 원본: `C:\Users\user\.claude\plans\humble-purring-glacier.md`. gameplay-engineer(sonnet) 실행 시점(2026-07-07) 전사.

## VF 갱신 (2026-07-08) — 카메라 토글 버튼(액션 컷 온/오프)
VF 단계(OTS 종이 효과 수정) 완료 후, 오너 요청으로 **런타임 온/오프 토글 UI**(`BP_CamToggleButton`, 레벨 액터 `UI_CamToggle`)를 추가했다. 버튼 클릭 시 `bCamActionEnabled`(Manager, 기본 true)를 토글 — false면 공격 시 컷 Align(빌보딩) ForEachLoop 블록을 완전히 건너뛰고 곧장 Delay→PlayAttack으로 직행(카메라 자체의 SetViewTargetWithBlend 컷은 무변경, 스프라이트 빌보딩만 스킵). `bInputLocked`(Executing 중)면 토글 요청 무시(로그 없이 자연 종료). 상세 기록: [[raw/VF_토글버튼]]. **직전 세션에서 이 작업이 부분 완료(허위 완료 보고) 상태로 방치됐다가 재작업으로 완성됨** — 상세는 raw 문서 참조.

## v3 갱신 (2026-07-08) — 2단계 카메라: 걷는 동안 기본캠 → 공격 순간 동적 어깨너머(OTS) 컷
아래 원문(C0/C1, 팀별 고정 앵글 2기)은 v3에서 **철거**되고, `ActionCam_Dynamic` 1기 + 실좌표 기하 계산(공격자·타겟 위치 기반 매 공격마다 동적 산출)으로 대체됐다. 승인 plan: `C:\Users\user\.claude\plans\humble-purring-glacier.md`(V0~V3 단계). 상세 기록: [[raw/V1_철거]] · [[raw/V2_구축]] · [[raw/V3_게이트]] · [[../../카메라연출_원칙]]. 튜닝 파라미터 6종(`CamBack`/`CamLateral`/`CamHeight`/`CamLookBias`/`LookAtZOffset`/`CamBlendIn`)은 `BattleManager` Details에서 오너가 직접 조정.

## Context
오너 확정: **액션 컷만**(쉐이크는 후속), **앵글은 오너 직접 배치**. 공격(Executing) 동안 팀별 근접 앵글로 부드럽게 전환 → 턴 끝에 기본 카메라 복귀 — 옥토패스식 컷 감성. 구현 핵심은 `SetViewTargetWithBlend`(엔진이 위치·회전·FOV 보간 제공)라 코드가 얇고, 카메라는 **엔진 CameraActor 인스턴스 2기**(BP 불필요 — 에디터 선택 시 픽처인픽처 미리보기 자동 지원 = 오너 앵글 잡기 최적). 실행 sonnet/haiku.

## 설계
### 구성
- **CameraActor 2기 배치**: `ActionCam_Party`(아군 공격 컷용) / `ActionCam_Enemy`(적 공격 컷용), 폴더 `BattleStage/Camera`. FOV ~55(기본 90보다 타이트). **기본 앵글(Director 산출, 오너가 이후 자유 드래그)**: 각 팀 공격 포인트(±350, −6750)를 바라보는 근접 샷 — 시작값 예: ActionCam_Party ≈ (−80, −7450, 620) / yaw≈75 / ActionCam_Enemy 미러 ≈ (+80, −7450, 620) / yaw≈105 — C0에서 에디터 캡처 자가확인으로 "공격 포인트의 유닛이 화면 중앙·크게" 보이게 미세조정 후 확정.
- **Manager 변수 3개**(instance-editable): `DefaultCamera`(=CameraActor_0), `ActionCamParty`, `ActionCamEnemy` — 레벨에서 지정.
### 배선 (BP_BattleManager — 2곳만)
- **EnterExecuting**: 잠금/마커OFF/발광OFF/버튼숨김 직후(WalkForward 앞) — `GetPlayerController(0)` → IsValid → **SetViewTargetWithBlend(타깃 = ActiveUnit.bIsParty ? ActionCamParty : ActionCamEnemy — Select 노드, BlendTime 0.4, ease)**. 캠 ref가 null이면 스킵(IsValid 가드 — 블렌드 없이 기본캠 유지, 우아한 폴백). PrintString(log) "CamCut:<party/enemy>:t=".
- **EnterTurnEnd 진입 액션**: `SetViewTargetWithBlend(DefaultCamera, BlendTime 0.3)` — **단일 복귀 지점**(QA-C3 교훈 재적용: 복귀를 Executing 체인 성공에 결속하지 않음 → null-skip 턴 경로에서도 항상 기본캠 보장, 이미 기본캠이면 무해 no-op). PrintString "CamBack:t=".
- 타이밍 궁합: 컷 블렌드 0.4s ≈ 걸음 도착(0.33~0.4s)과 동시 안착 → 공격을 근접 앵글로 관람. 복귀 0.3s는 턴 텀(0.35s) 안에 완료.
### 회귀 안전
PIE 시작 시점은 기존 autoActivate(BattleCamera) 그대로 — 무변경. 캠 미지정/삭제 시 블렌드 스킵으로 기존 화면 유지. 걸음·공격·이펙트 로직 일절 무변경.

## 단계
| 단계 | 내용 | 게이트 | 담당 |
|---|---|---|---|
| C0 | `SetViewTargetWithBlend` 노드 프로브(표준 함수 — 확인만) + CameraActor 2기 배치·기본 앵글 산출(에디터 캡처 자가확인: 공격 포인트 유닛이 중앙·크게) + Manager 변수 3종·레벨 refs | 프로브 성공+컴파일 0 | ge(sonnet) |
| C1 | Manager 배선 2곳(Executing 컷·TurnEnd 복귀)+게이트: 스캐폴드 2턴 — CamCut(팀별 올바른 캠 로그)·CamBack 타임라인, null 캠 1기 임시 해제→스킵 폴백 확인→복원, PIE 재시작 기본캠, 배치_1·village 회귀 | 미니 TC 전부 PASS | ge(sonnet)→verifier 겸임 |
| CF | **오너 육안**: PIE로 컷 느낌 확인 + **ActionCam 2기 직접 드래그·회전으로 앵글 튜닝**(선택 시 미리보기 창 활용). 블렌드 시간(0.4/0.3)도 체감 조정 가능 | 오너 판정 | 오너 |

## 미니 TC (경량 — 소형 기능 선례)
CT-01 아군 턴 컷=ActionCamParty·적 턴=ActionCamEnemy(로그) / CT-02 TurnEnd마다 기본캠 복귀(null-skip 턴 포함) / CT-03 캠 ref null→블렌드 스킵·정상 진행 / CT-04 PIE 시작 기본캠(autoActivate 무변경) / CT-05 컷 블렌드 완료 ≤ 공격 시작(로그 t) / CT-06 걸음·공격·이펙트 로직 무변경(컴파일 0+기존 로그 패턴 유지) / CT-07 배치_1 좌표·village dirty 회귀. 판정: 로그+오너 육안(컷 미감).

## 문서·커밋 (wiki 룰)
`docs/features/카메라액션/`(간이 청사진+plan+raw) 신규. 배치가이드에 "ActionCam 2기 드래그/미리보기" 1줄 추가. 커밋 `[C] feat(카메라액션): ...` 단계별, push는 오너 확인.

## 비범위
쉐이크 ❌(후속 — CameraShake 에셋 프로브 필요) / 턴 시작 팬·스킬 클로즈업 ❌ / 타겟 리액션 컷(피격자 앵글) ❌(오너가 앵글로 커버 가능, 필요시 후속) / DoF·시네마틱 카메라 ❌.
