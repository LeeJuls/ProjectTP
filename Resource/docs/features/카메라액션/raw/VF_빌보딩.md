---
type: raw
feature: 카메라액션
stage: VF
updated: 2026-07-08
---

# VF — OTS 종이 효과 결함 수정(컷 스냅 빌보딩) 기록
#projectTP/카메라액션

## 증상
V3까지 완료된 OTS 동적 어깨너머 컷에서, 액션 캠 각도로 컷될 때 스프라이트 쿼드가 종이처럼 비스듬히 보이는 결함이 있었다(빌보딩 부재).

## 근본 원인(Director 확정)
스프라이트 쿼드(Sprite 루트, 회전 `(0,0,roll90)`)는 기본 캠(yaw84) 전용으로 고정된 회전값을 갖는다 — 카메라가 기본 각도(yaw84)에 있을 때만 판이 정면으로 보이도록 설계된 상수 회전이었다. 액션 캠이 동적으로 계산된 다른 yaw로 이동해 컷하면, 스프라이트 판은 여전히 기본 캠 기준 회전을 유지하므로 새 카메라 각도에서는 비스듬한 판(종이 효과)으로 보인다.

## 해법 — 컷 순간 8기 전원 스냅 빌보드
빌보드 회전은 스프라이트가 그리는 텍스처 자체를 바꾸지 않는다(항상 같은 그림, 카메라를 향하도록 판만 돌아감). 따라서 컷이 발생하는 순간 스냅(순간 전환)으로 8기 전원의 Sprite 회전을 그 순간의 액션 캠 yaw에 맞춰 재계산해도, 시각적으로 프레임 점프가 생기지 않는다(그림이 이미 카메라를 향하는 것처럼 정면으로 보이던 걸 유지할 뿐). 틱(매프레임 갱신) 없이 컷 진입·복귀 두 시점에만 스냅하는 것으로 충분하다.

**걷기와 충돌하지 않는 이유**: 걷기(WalkForward 전진, WalkBack 복귀)는 전부 기본 캠 상태(yaw84)에서 일어난다 — OTS 컷은 걷기가 완료된 뒤(WalkForward.then 발화 시점, latent MoveComponentTo 완료 후)에만 발생하고, 복귀 Align도 WalkBack이 시작되기 **전**에 실행되도록 순서를 강제했다. 따라서 §15 함정⑱(MoveComponentTo가 TargetRelativeRotation을 함께 latent 보간해 회전을 덮어씀)과 절대 겹치지 않는다.

## 구현

### ① BP_BattleSpawnPoint — 신규 Function `AlignSpriteToCamYaw`
Function Graph(`add_function_graph`) + float 파라미터 `CamYaw`(input, `add_function_param`).

본문 배선:
```
FunctionEntry.then → SetWorldRotation(self=GetSprite) → PrintString(log)
FunctionEntry.CamYaw → Subtract(A=CamYaw, B=84.0) → MakeRotator(Pitch=0, Yaw=결과, Roll=90) → SetWorldRotation.NewRotation
```
기본 캠(yaw84)일 때 델타=0 → `MakeRotator(0,0,90)` = 정규 회전값과 정확히 일치(복원). 84.0은 이 무대의 스프라이트↔카메라 기준 오프셋 상수.

**§17 함정⑲ 회피 순서**: Subtract 노드(프로모터블) 생성 직후 A핀(CamYaw)을 먼저 `connect_pins`로 연결해 노드를 `float-float`로 승격시킨 뒤(이 시점 B핀도 float 타입으로 확정됨), B핀에 `set_pin_value(B, "84.0")`을 호출 — 재조회로 B핀 값이 정확히 "84.0"으로 반영됐음을 확인. (참고: B핀을 먼저 세팅하는 순서는 노드가 아직 와일드카드 상태라 `set_pin_value` 자체가 "Could not set value" 에러로 실패함을 실측 확인 — 이번 사례는 "A 먼저 연결(안전한 float-float 승격) → B 세팅" 순서가 함정⑲을 피하면서도 유효했다. 함정⑲의 위험 시나리오는 "Vector×Float 스칼라곱인데 A 연결 후 B가 Vector로 오승격"인 경우였고, 이번은 A/B 둘 다 float라 위험이 없었다.)

로그: `Align:<GetDisplayName(GetOwner(Sprite))>:yaw=<CamYaw>` 형식, `bPrintToScreen=false`/`bPrintToLog=true`(log만).

### ② BP_BattleManager — 호출 2곳
**OTS 컷 블록**(`WalkForward(165).then`과 `Delay(166, 0.55초).execute` 사이에 삽입 — "PlayAttack 앞"의 정확한 지점을 놓고 원 지시서와 실그래프 사이에 사소한 해석 여지가 있었음, §알려진 이슈 참조):
```
WalkForward.then → ForEachLoop(GetTurnQueue()) → IsValid(원소) → AlignSpriteToCamYaw(BreakRotator(FindLookAtRotation(camLoc,lookAt)).Yaw) → Completed → Delay(0.55) → PlayAttack
```
FindLookAtRotation(230)은 기존 camLoc/lookAt 계산에 이미 쓰이던 pure 노드를 fan-out 재사용(신규 게터 불필요).

**복귀 블록**(Sequence B: `SetViewTargetWithBlend(DefaultCamera).then → PrintString(244).then`과 `WalkBack(167).execute` 사이 — 기존 `MacroInstance_20`발 스킵 경로 fan-in은 그대로 보존, `244→167` 연결만 절단 후 재배선):
```
PrintString(244).then → ForEachLoop(GetTurnQueue()) → IsValid(원소) → AlignSpriteToCamYaw(BreakRotator(GetActorRotation(DefaultCamera)).Yaw) → Completed → WalkBack
```

두 호출 모두 `Class|BPBattleSpawnPoint|AlignSpritetoCamYaw`(§13/§14 함정⑮이 정확히 예측한 형식) 문자열로 `create_node` 즉시 성공.

### ③ 보너스 — 공중에 뜬 그림자 제거
CDO `set_properties`로 `castShadow=false`(단일 스칼라 bool, §7 함정③과 무관 — 안전) 적용 대상 5개:
- `BP_AttackButton`: `ButtonBg`, `Label`, `LabelCancel`
- `BP_BattleSpawnPoint`: `TurnMarker`, `EffectQuad`

`Sprite` 본체(BP_BattleSpawnPoint)는 `castShadow=true` 그대로 유지(캐릭터 그림자 보존, 지시서 요구사항). 5개 전부 `set_properties` 성공 후 `get_properties` 재조회로 반영 확인.

### ④ 컴파일
`BP_BattleSpawnPoint`, `BP_BattleManager`, `BP_AttackButton` 3종 전부 `compile_blueprint(warnings_as_errors=true)` 0 에러/0 경고.

## 검증(스캐폴드 2턴)
C1/V3 raw와 동일한 패턴(`BeginPlay → Delay(3.0) → NotifyAttackButtonClicked → Delay(0.3) → [ForEachLoopWithBreak(TurnQueue)+Branch(상대팀 탐색)→SetScaffoldTarget→Break] → CastToBP_BattleSpawnPoint → NotifyUnitClicked → Delay(4.0) → ...(2회차 반복)`), 26개 노드, `ScaffoldTarget` 변수 1종.

### 로그 실측(PIE, StartPIE warmupSeconds=3 + 12초 대기)
```
CamCut:A=(A1)...T=(B1)...cam=...   ← 턴1 컷
Align:SpawnPoint_Party_A1:yaw=22.458
Align:SpawnPoint_Enemy_B1:yaw=22.458
... (8기 전원 동일 yaw)
WalkArrive:SpawnPoint_Party_A1:t=3.699
TakeHit/TakeHitRevert
CamBack:t=4.616
Align:...yaw=84 (8기 전원, 복귀)
WalkHome:SpawnPoint_Party_A1
State:TurnEnd → TurnStart → AwaitCommand
CamCut:A=(B1)...T=(A1)...cam=...   ← 턴2 컷(적)
Align:...yaw=-173.394 (8기 전원)
WalkArrive:SpawnPoint_Enemy_B1:t=8
TakeHit/TakeHitRevert
CamBack:t=8.92
Align:...yaw=84 (8기 전원, 복귀)
WalkHome:SpawnPoint_Enemy_B1
State:TurnEnd → TurnStart → AwaitCommand
```

### CT 판정
| ID | 내용 | 판정 | 근거 |
|---|---|---|---|
| CT-VF-01 | 컷 시점 8기 Align 로그(액션캠 yaw) | **PASS** | 턴1 yaw=22.458×8, 턴2 yaw=-173.394×8. |
| CT-VF-02 | 복귀 시점 8기 Align 로그(기본캠 yaw=84±) | **PASS** | 턴1·턴2 모두 정확히 yaw=84×8. |
| CT-VF-03 | 걷기 로그가 Align 이후 순서 정상 | **PASS** | `WalkFwd(t=3.306)`→`Align×8`(같은 타임스탬프대)→`WalkArrive(t=3.699)` — Align이 WalkForward.then 발화(=이동 완료) 즉시 실행되고 그 후 다음 단계(PlayAttack 진입 전 Delay)로 흐름. |
| CT-VF-04 | 복귀 Align이 WalkBack(`WalkHome`) 로그보다 먼저 | **PASS** | `CamBack(t=4.616)`→`Align×8(같은 타임스탬프대)`→`WalkHome(15:39:55:217)`. |
| CT-VF-05 | 기존 CamCut/공식 로그 무변경 | **PASS** | `CamCut:A=...:T=...:cam=...:back=350:lat=250:height=250:bias=0.7:zoff=120:blend=0.25` 포맷 그대로. |
| CT-VF-06 | 컴파일 0 | **PASS** | 3종 BP 전부 0 에러/0 경고(스캐폴드 삽입 전·후 각 1회, 총 4회 컴파일 전부 통과). |
| CT-VF-07 | PIE 후 8기 Sprite 회전 (0,0,90) 복원 | **PASS(정적 근거)** | 마지막 턴 종료 후 복귀 Align 로그(yaw=84, 델타=0)가 논리적으로 이를 증명 + 에디터 8기 인스턴스(PIE와 무관) `relativeRotation` 전수 조회 결과 `(pitch=0,yaw=0,roll=90)`(정규값) 확인. |
| CT-VF-08 | 배치_1 회귀(8기 좌표·존재) | **PASS** | `find_actors(name="SpawnPoint_")` 8기 전원(`BP_BattleSpawnPoint_C_0/2/3/4/5/6/7/9`) 확인, 배치_1.md 내부명 기준값과 일치. |

## 알려진 이슈/제약
- **"PlayAttack 앞" 삽입 지점의 해석**: 지시서는 "OTS 컷 블록 끝 ... Completed → PlayAttack으로 연결"이라 명시했으나, 실그래프에는 `WalkForward.then`과 `PlayAttack.execute` 사이에 기존 `Delay(0.55)`(공격 애니메이션 타이머, W2 문서가 이미 문서화한 기존 시스템)가 존재했다. Align 삽입을 `WalkForward.then`과 이 `Delay(0.55)` **사이**(Delay보다 먼저)로 결정함 — 근거: (a) 원인 설명이 명시한 "걷기 완료 후"라는 조건과 정확히 일치(`WalkForward.then`은 latent MoveComponentTo 완료 후 발화, §14 확정 사실), (b) "PlayAttack 앞"이라는 조건 자체는 만족(Delay도 PlayAttack 이전 단계), (c) Align이 즉시 실행 함수(latent 아님)라 Delay 앞/뒤 어느 쪽에 넣어도 시각적 차이가 없음. Director 승인 없이 진행했으므로 verifier/qa-critic 대조 시 재확인 권장.
- CastFailed 안전망(두 CastToBP_BattleSpawnPoint 노드의 `CastFailed` exec 출력)은 이론상 도달 불가(캐스트가 항상 성공)이므로 미배선 상태로 유지(C1 raw 문서의 기존 관례와 동일).
- `Utilities|Array|ForEachLoop`(Break 없는 단순 버전)를 AlignSpriteToCamYaw 호출 2곳에 사용 — TurnQueue 8기 전원을 예외 없이 순회해야 하므로 Break가 필요 없는 것이 설계 의도와 일치(전원 스냅이 목적).

## 정리·저장
스캐폴드 26개 전부 `delete_node`, `BeginPlay.then` `break_pins`로 완전 원복(`connected_pins:[]` 재확인), `ScaffoldTarget` 변수 `remove_variable`로 제거. `compile_blueprint(warnings_as_errors=true)` 최종 0 에러/0 경고. `save_assets([])` → `BP_BattleManager`/`BP_BattleSpawnPoint`/`BP_AttackButton`/`map_battle_octopath` 4개 전부 `is_dirty=false` 확인.

핵심 배선(①·②)은 `get_node_infos` 재조회로 스캐폴드 제거 후에도 정확히 보존됨을 최종 확인.
