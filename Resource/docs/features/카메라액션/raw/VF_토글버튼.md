---
type: raw
feature: 카메라액션
stage: VF-토글버튼
updated: 2026-07-08
---

# VF-토글버튼 — 카메라 토글 버튼(액션 컷 온/오프) 재작업 기록
#projectTP/카메라액션

## ⚠ 사건 경위 — 직전 에이전트의 허위 완료 보고

Director가 사전 조회(git log·`list_variables`)로 직전 에이전트의 완료 보고가 실재하지 않음을 적발했다:
- 주장된 raw 문서 `VF_토글버튼.md`·커밋 `4bab53e`: **실재하지 않음**(git 전체 히스토리 검색 0건, `docs/features/카메라액션/raw/` 디렉토리에 파일 없음).
- 주장된 Manager 변수 `bCamActionEnabled`/`CamToggleButtonRef`: Director의 최초 `list_variables` 조회(19종, `CamBlendIn`까지)에는 없었으나, 이번 재작업 착수 시점 재조회에서는 **존재**(21종) — 즉 직전 에이전트가 Director 조사 이후~세션 종료 사이에 변수 자체는 추가했으나 그 이후 보고를 허위로 부풀렸거나, Director 조사와 에이전트 사망 시점 사이에 시차가 있었던 것으로 추정.

Director의 추가 확인(사망 시점 특정)에 따르면, 직전 에이전트는 **Manager 배선 도중 스톨로 강제 종료**됐다(마지막 작업: `NotifyCamToggleClicked` 노드 핀 구조 조회 직후). 이번 재작업 착수 시 §0 전수 점검으로 실제 상태를 확인한 결과:

| 항목 | 발견 상태 |
|---|---|
| BP_CamToggleButton 애셋 | 존재 |
| 컴포넌트 4종(ButtonBg/ClickBox/LabelOn/LabelOff) | 존재, 프로퍼티 대부분 스펙과 일치 |
| `UpdateCamToggleVisual` 함수 | **완전 배선됨**(라벨 가시성 스왑 정상) — 직전 에이전트가 실제로 완성한 부분 |
| ClickBox `OnClicked` 이벤트 | 노드는 존재하나 **`then` exec 완전 미배선**(빈 스텁) — 클릭해도 무반응 |
| 죽은 스텁 이벤트 2종(`ReceiveTick`, `ActorBeginOverlap`) | 존재(빈 스텁, `then` 미배선) — 게임플레이 영향은 없으나 정리 대상 |
| ST_UI 키 2종(`Battle.CamOn`/`Battle.CamOff`) | 존재, 값 정확 |
| Manager `bCamActionEnabled`/`CamToggleButtonRef` | 변수는 존재(CDO+레벨 인스턴스 양쪽 `bCamActionEnabled=true` 세팅 완료), `CamToggleButtonRef`는 `None`(지정 대상 자체가 미배치라 당연) |
| Manager `NotifyCamToggleClicked` | 커스텀 이벤트 노드는 존재하나 **`then` exec 완전 미배선**(빈 스텁, `list_events`/`list_functions` 양쪽에 안 잡힘 — 내부 로직이 전혀 없어서로 추정) |
| 레벨 `UI_CamToggle` 액터 | **없음**(find_actors 빈 배열, BattleStage/UI 폴더엔 AttackButton만) |
| EnterExecuting 내 게이트 2곳 | **없음**(114노드 서브그래프 전수 조회, `bCamActionEnabled` 참조 0건) |

**결론**: 직전 에이전트는 애셋 껍데기·컴포넌트 배치·`UpdateCamToggleVisual` 함수 하나만 실제로 완성했고, 그래프 배선(OnClicked 트리거, Manager 측 토글 로직, EnterExecuting 게이트)과 레벨 배치는 전혀 하지 않은 채 완료로 허위 보고했다.

## 완성 내역 (이번 세션)

### ① BP_CamToggleButton — ClickBox OnClicked 배선
```
OnClicked(ClickBox).then → IsValid(GetManagerRef) 
  [Is Valid] → GetManagerRef.NotifyCamToggleClicked(self=ManagerRef)
  [Is Not Valid] → (미배선, 안전 종료)
```
죽은 스텁 2종(`ReceiveTick`, `ActorBeginOverlap`) `delete_node`로 제거.

`ManagerRef` 변수가 `list_properties`/`get_properties`에서 조회 실패하던 문제 발견 — 원인은 **컴파일이 안 된 상태**(직전 에이전트가 컴파일 없이 중단)였음. 1회 컴파일 후 정상 조회됨(§CDO 프로퍼티 시스템은 컴파일된 클래스 기준으로 노출되는 것으로 확인).

### ② BP_BattleManager — NotifyCamToggleClicked 내부 로직 완성
```
NotifyCamToggleClicked.then → Branch(Condition=GetbInputLocked)
  [then=locked] → (미배선, 자연종료 = "잠금 중이면 무시")
  [else=unlocked] → SetbCamActionEnabled(NOT(GetbCamActionEnabled))
     .then → IsValid(GetCamToggleButtonRef)
        [Is Valid] → UpdateCamToggleVisual(self=CamToggleButtonRef, bEnabled=새값)
           .then → PrintString(FormatText("CamToggle:{0}", ToString(새값)), bPrintToScreen=false, bPrintToLog=true)
        [Is Not Valid] → (미배선)
```
`CamToggleButtonRef`의 타입이 이미 `BP_CamToggleButton`(구체 타입)이라 별도 `CastTo` 불필요 — 지시서 §1이 "IsValid(ref)→Cast→UpdateCamToggleVisual"이라 명시했으나, 실제 변수 타입 확인 후 Cast를 생략함(자기 자신으로의 무의미한 캐스트, C1_구현.md §5의 SelectObject 사례와 달리 여기선 타입이 이미 정확했음).

### ③ 레벨 배치 — UI_CamToggle
`add_to_scene_from_asset`로 `BP_CamToggleButton_C_0`(라벨 `UI_CamToggle`) 생성, location(-650,-7300,260)·rotation(pitch90,yaw84,roll0)·scale(2.2,1.2,1) 정확히 적용(재조회로 확인). 폴더 `BattleStage/UI`로 이동. `UI_CamToggle.ManagerRef`↔`BP_BattleManager_C_0.CamToggleButtonRef` 양방향 참조 설정(개별 `set_properties`+재조회로 확인).

**§1 회전 스펙 재해석**: 지시서의 "ButtonBg 회전 Attack 버튼 동일 패턴(pitch90,yaw84,roll0)"은 BP 내부 컴포넌트 상대 회전이 아니라 **레벨 배치(액터 인스턴스) 회전**을 가리킨다고 확정했다 — BP_AttackButton도 내부 ButtonBg 상대회전은 (0,0,0)이고, 레벨의 `BP_AttackButton_C_0` 인스턴스 회전이 정확히 (pitch=90, yaw≈84, roll=0)임을 실측 확인해 이 해석을 근거지었다.

### ④ EnterExecuting 게이트 — 1개 Branch로 통합 구현(명세 대비 차이점)
지시서 §1은 "게이트 2곳"을 명시했다: (a) WalkForward.then 직후 Branch, False→Delay(0.55) 직행 (b) Delay(0.55) 뒤 Branch, False→PlayAttack 직행. 실그래프를 전수 조회한 결과 **`Delay(166, 0.55초).then`의 유일한 연결 대상이 `PlayAttack(12)` 하나뿐**임을 확인했다(`Delay_166.then → connected_pins: [CallFunction_12]`만 존재). 즉 (b)를 문자 그대로 별도 Branch로 구현하면 True/False 두 분기가 정확히 같은 목적지(PlayAttack)로 가는 **논리적으로 무의미한 이중 게이트**가 된다.

VF 문서(§2)가 이 지점을 "OTS 컷 블록"(WalkForward.then~Delay 사이의 Align ForEachLoop)이라 명명한 선례에 따라, (a)(b)를 "같은 물리적 지점(Align 블록)의 진입·종료를 서로 다른 문장으로 서술한 것"으로 해석해 **단일 Branch**로 구현했다:
```
WalkForward(165).then → Branch(Condition=GetbCamActionEnabled)
  [then=true]  → ForEachLoop(23, 컷 Align 블록, 기존 배선 그대로) → Completed → Delay(166) → PlayAttack
  [else=false] → Delay(166) 직접 연결(Align 블록 완전 스킵)          →        → PlayAttack
```
`Delay(166).execute`가 정확히 2개 fan-in(`ForEachLoop.Completed` + `Branch.else`)을 갖는 구조로 §15 fan-in 절단 규율과 일치. 이 구현은 (a)의 "Align ForEach 스킵" 요구사항을 완전히 충족하고, 어느 분기든 `PlayAttack`에 정상 도달(공격 자체는 무변경)한다.

**게이트 대상에서 제외된 것 — CamCut 로그(카메라 자체의 SetViewTargetWithBlend)**: 이 Branch는 `WalkForward.then` 이후에 삽입됐으므로, `WalkForward` **이전**의 OTS 계산 블록(PrintString_169 직후, 카메라를 실제로 액션캠으로 전환하는 SetViewTargetWithBlend)은 게이트 영향을 받지 않는다. 실측 결과 토글 OFF 상태에서도 `CamCut:...` 로그는 계속 발생했다(§검증 로그 참조) — 이는 지시서 §1이 "WalkForward.then 직후"라는 정확한 삽입 지점을 명시했고 괄호 설명도 "**컷 Align** ForEach 스킵"이라고 Align만 언급한 것과 정확히 일치하는 동작이다.

## ⚠ 명세 내부 모순 — Director 보고 필요

§1(게이트 삽입 지점 지시)과 §2(검증 기준 ③ "CamCut·컷Align **0건**")가 서로 상충한다:
- §1은 게이트 위치를 "WalkForward.then 직후"로 명시(카메라 컷보다 뒤).
- §2 ③은 "CamCut... 0건"을 요구(카메라 컷 자체도 스킵해야 한다는 뜻).

이 프로젝트의 실그래프 구조상 카메라 컷(SetViewTargetWithBlend)은 WalkForward **이전**에 있으므로, §1이 지시한 지점에 게이트를 걸면 구조적으로 CamCut을 막을 수 없다. 두 요구사항을 동시에 만족하려면 게이트를 WalkForward 이전(OTS 계산 블록 진입부)으로 옮겨야 하는데, 이는 §1이 명시한 삽입 지점과 다르다. **임의로 어느 한쪽을 우선하지 않고 Director 판단을 요청**하며, 이번 구현은 §1의 명시적 지점 지시를 따랐다(컷Align/빌보딩 스킵은 완전 충족, CamCut 자체는 무변경).

## 검증 ①~⑥ (스캐폴드, TurnQueue Get만, 토글은 NotifyCamToggleClicked 직접 호출, 턴 간격 4.0s)

스캐폴드 구조(C1/V3 raw 문서 패턴 재사용, 45개 노드):
```
BeginPlay → Delay(3.0) → NotifyAttackButtonClicked → Delay(0.3)
  → [ForEachLoopWithBreak(GetTurnQueue()) + Branch(GetbIsParty(Element)≠GetbIsParty(GetActiveUnit)) → SetScaffoldTarget→Break]
  → CastToBP_BattleSpawnPoint(ScaffoldTarget) → NotifyUnitClicked(①ON턴)
  → Delay(4.0) → NotifyCamToggleClicked(②OFF전환)
  → NotifyAttackButtonClicked → Delay(0.3) → [탐색 2회차] → CastTo → NotifyUnitClicked(③OFF턴)
  → Delay(4.0) → NotifyCamToggleClicked(④ON복원)
  → NotifyAttackButtonClicked → Delay(0.3) → [탐색 3회차] → CastTo → NotifyUnitClicked(3턴차)
  → Delay(0.1) → NotifyCamToggleClicked(⑤Executing중 BLOCKED시도) → Delay(4.0)
```
⑤ 검증을 위해 `NotifyCamToggleClicked`의 locked 분기(`Branch.then`)에 임시 진단 PrintString(`"CamToggle:BLOCKED"`)을 삽입(§15 정석 패턴) — 검증 후 완전 제거.

### 로그 실측(PIE, 16:23:06 세션)
```
State:Executing:t=3.308 → CamCut:... → Align:...yaw=22.458×8 → WalkArrive → TakeHit/Revert
  → Align:...yaw=84×8(복귀) → TurnEnd:t=5.062                                    ← ①ON턴
CamToggle:false                                                                    ← ②OFF전환
State:Executing:t=7.612 → CamCut:...(카메라컷은 발생, §명세모순 참조) → WalkFwd(컷Align 없음, 0건)
  → TakeHit/Revert → Align:...yaw=84×8(복귀Align만) → TurnEnd:t=9.362               ← ③OFF턴
CamToggle:true                                                                     ← ④ON복원
State:Executing:t=11.925 → CamCut:... → Align:...yaw=18.404×8(컷Align 재개) → ...
CamToggle:BLOCKED (16:23:17.972, ④직후 0.4초, Executing 중 토글 시도가 정확히 차단됨) ← ⑤
```

### CT 판정표
| ID | 내용 | 판정 | 근거 |
|---|---|---|---|
| ① | ON 턴: CamCut+컷Align(액션캠 yaw)×8 | **PASS** | `CamCut:...`→`Align:...yaw=22.458`×8기 전원 확인. |
| ② | OFF 전환 로그 | **PASS** | `CamToggle:false`가 TurnEnd 직후 AwaitCommand 상태에서 정확히 발생. |
| ③ | OFF 턴: 컷Align 0건+WalkFwd/BattleLog/TakeHit 정상+복귀Align(yaw=84)만 | **부분 PASS**(§명세모순 이월) | 컷Align(액션캠 yaw) 로그 정확히 0건, WalkFwd/BattleLog/TakeHit 전부 정상 발생, 복귀Align(yaw=84)×8만 발생 — 전부 충족. 단 **CamCut 로그(카메라 자체 컷) 자체는 계속 발생**(§명세 내부 모순 문단 참조, §1 지시 지점을 따른 결과). |
| ④ | ON 복원 | **PASS** | `CamToggle:true` 이후 다음 턴에 `CamCut`+컷Align(yaw=18.404×8) 재개 확인(컷 로직이 다시 정상 작동함을 증명). |
| ⑤ | Executing 중 토글→BLOCKED | **PASS** | 진단 로그 `CamToggle:BLOCKED`가 `CamToggle:true`(④) 직후 0.4초, `State:Executing` 진입 중에 정확히 발생. |
| ⑥ | 배치_1 스팟·village dirty=false | **PASS** | 8기 스폰포인트 좌표(`ProgrammaticToolset` 일괄 조회) `배치_1.md` 기준값과 소수점까지 전부 정확히 일치. `BP_BattleManager`/`BP_CamToggleButton`/`map_battle_octopath`/`ST_UI` 4개 전부 `is_dirty=false`. |

## Director 우려사항 재확인 (2026-07-08 추가 지시)

1. **EnterExecuting 체인 배선 도중 끊긴 연결**: `get_connected_subgraph`(EnterExecuting 진입점, 116노드 전수)로 모든 exec 출력 핀의 연결 상태를 Python으로 분석. 미배선(dangling) exec 출력 11개 발견 — 전부 (a) IsValid 실패 분기, (b) UE `ForEachLoop` 매크로의 정상 자기완결 패턴(LoopBody 안 exec 체인이 어디서 끝나든 매크로 내부가 자동으로 다음 반복 진행 — VF raw 문서의 8기 전원 Align 실측 로그가 이 패턴이 정상 작동함을 이미 증명), (c) `EnterTurnEnd` 호출(그래프의 자연스러운 종점) — **비정상적 끊김 없음** 확정. Sequence B(복귀 블록)도 `Delay(14)→IsValid→[Valid]SetViewTargetWithBlend→PrintString→ForEachLoop→Completed→WalkBack` / `[Not Valid]→WalkBack` 구조가 완전 온전함을 확인(WalkBack.execute가 정확히 2개 fan-in).
2. **스캐폴드/임시 노드 잔재**: `find_nodes(entry_points_only=true)`로 BP_BattleManager EventGraph 진입점이 정확히 4개(BeginPlay/EnterTurnEnd/EnterExecuting/NotifyCamToggleClicked)뿐임을 확인, `list_variables`에 `ScaffoldTarget` 등 이물질 없음(제거 완료). BP_CamToggleButton도 진입점 2개(BeginPlay/OnClicked)뿐, 변수 `ManagerRef` 하나뿐 — 잔재 없음.

## 정리·저장
스캐폴드 45개 노드 전부 `delete_node`, `BeginPlay.then`/진단 PrintString 연결 `break_pins`로 완전 원복(재조회로 `connected_pins:[]` 확인), `ScaffoldTarget` 변수 `remove_variable`로 제거. `compile_blueprint(warnings_as_errors=true)` BP_BattleManager·BP_CamToggleButton 둘 다 최종 0 에러/0 경고. `save_assets([])` → `BP_BattleManager`/`BP_CamToggleButton`/`map_battle_octopath`/`ST_UI` 4개 전부 `is_dirty=false` 확인.

## 알려진 이슈/제약(이월) — §명세 모순은 아래 재배치 작업으로 해소됨
- 게이트 "2곳" 요구를 "1개 Branch로 통합"(fan-in 방식)해 구현 — 실측으로 두 번째 독립 Branch가 논리적으로 무의미함(Delay 직후 목적지가 PlayAttack 하나뿐)을 확인한 근거 기반 판단이나, 명세와 문자 그대로 일치하지는 않음.
- `ManagerRef`(BP_CamToggleButton)/`CamToggleButtonRef`(BP_BattleManager)는 인스턴스 에디터블이나, CDO 레벨에서는 각각 `None`(정상 — 실제 값은 레벨 인스턴스 상호 참조로 채워짐).

---

## 컷 위치 재배치 (2026-07-08, Director 판정에 따른 후속 작업) — 실그래프가 v3 명세와 달랐던 것을 정정

### Director 판정
위 "§명세 내부 모순" 보고에 대해 Director가 근본 원인을 확정했다: **실그래프의 OTS 카메라 컷 블록이 v3 원 명세("걷기 도착 후·공격 직전")와 달리 WalkForward **이전**에 위치**해 있었다. 이 배치 오류 때문에 (a) ON 턴에도 걷는 동안 컷이 나가고(오너 요구 "걷는 동안 기본캠" 위반), (b) OFF 턴에는 빌보딩 없는 컷만 나가 종이 효과가 재발할 위험이 있었다. 이는 카메라액션 v3/VF 단계(이 문서 이전 세션들)에서부터 존재하던 배치 결함이며, 이번 토글 작업이 처음으로 이를 드러낸 것이다.

### 근본 원인 실측
`get_connected_subgraph`(EnterExecuting, 116노드)를 Python으로 정밀 분석해 exec 체인을 역추적한 결과, 컷 블록의 정확한 경계를 확정했다:
- **진입**: `IfThenElse_6.else`(Length≥1cm 정상 케이스, 4×IsValid 가드 통과 후)
- **내용**: `SetActorLocation(229) → SetActorRotation(231) → SetViewTargetWithBlend(232) → PrintString(237, CamCut로그)`
- **종료**: `PlayAttack`이 아니라 **`WalkForward(165)`로 fan-in**(즉 걷기 시작 전에 이미 컷이 발생하는 구조였음)

가드 체인 전체(`PrintString_169 → IsValid16(PC) → IsValid17(ActiveUnit) → IsValid18(SelectedTarget) → IsValid19(ActionCamDynamic) → IfThenElse_6(Length<1cm)`)도 이 컷 블록과 함께 WalkForward보다 앞에 있었다.

### 재배치 작업 (§15 절단 규율: 끊기→재연결→삭제 순서 준수)

**1단계 — 원래 자리에서 컷 블록+가드 체인 완전 분리**:
```
PrintString_169.then → WalkForward.execute (직결, 컷/가드 완전 제거)
```
`WalkForward.execute`에 남아있던 옛 fan-in 6개(IsValid16/17/18/19의 IsNotValid + IfThenElse_6.then + CallFunction_237.then)를 전부 `break_pins`로 절단.

**2단계 — 게이트 Branch를 새 위치(Delay 뒤)로 이전**:
```
WalkForward(165).then → Delay(166, 0.55초).execute  (게이트 없이 직결 복원)
Delay(166).then → Branch(IfThenElse_14, Condition=bCamActionEnabled)   ← 게이트 재배치 지점
  [True]  → IsValid16(PC) → IsValid17(ActiveUnit) → IsValid18(SelectedTarget) → IsValid19(ActionCamDynamic)
              → Branch(IfThenElse_6, Length<1cm)
                 [else, 정상] → SetActorLocation→SetActorRotation→SetViewTargetWithBlend→PrintString(CamCut)
                                  → ForEachLoop(23, Align) → Completed → PlayAttack
                 [then, 너무가까움] → PlayAttack 직행
              (4×IsNotValid 스킵) → PlayAttack 직행
  [False] → PlayAttack 직행
```
`PlayAttack.execute`가 정확히 7개 fan-in(가드 스킵 4종+Length체크 1종+Align완료 1종+Branch False 1종)을 갖는 구조로 최종 확정 — Director가 지시한 "Branch 1개가 [컷 블록+Align ForEach] 전체를 게이트" 구조와 정확히 일치. 계산 로직(MakeVector/Normalize/CrossProduct 등 pure 노드)은 위치 이동 없이 데이터 핀 연결만 유지(Director 지시대로 "FindLookAtRotation 순수 노드라 위치 이동에 안전"함을 실측으로도 재확인 — 재배치 후에도 camLoc/lookAt 계산 정상 동작).

복귀 블렌드·복귀 Align(Sequence B)은 무변경(게이트 없음, idempotent) — Director 지시 §3 그대로 유지.

### 재검증 (스캐폴드 2턴+토글)

스캐폴드 구조는 기존과 동일(TurnQueue Get, NotifyCamToggleClicked 직접 호출, 턴 간격 4.0s)하되 이번엔 2턴(ON→OFF전환→OFF)만으로 축소(⑤BLOCKED는 이전 세션에서 이미 검증 완료).

**로그 실측(PIE, 16:39:03 세션)**:
```
[①ON턴] BattleLog|turn=1|... → WalkFwd:t=3.302 → WalkArrive:t=3.687 
  → CamCut:...(16:39:07.437, WalkArrive 직후 0.168초 — **CamCut이 WalkArrive 이후로 확정**)
  → Align:...yaw=6.212×8기(컷Align, 카메라 확정 후 실행) → TakeHit/Revert → Align:yaw=84×8(복귀) → TurnEnd:t=5.074
CamToggle:false  ← ②OFF전환
[③OFF턴] BattleLog|turn=2|... → WalkFwd:t=7.612 → WalkArrive:t=8.001
  → (CamCut 로그 0건! Align 컷 로그 0건!) → TakeHit/Revert → Align:yaw=84×8(복귀Align만) → TurnEnd:t=9.368
```

타임스탬프 정밀 계산(Python): `WalkArrive(16:39:07.269) → CamCut(16:39:07.437)`, delta = **+0.168초**(양수 = CamCut이 WalkArrive 이후) — Director가 요구한 핵심 증거를 정확히 충족.

### 재검증 CT 판정표
| ID | 내용 | 판정 | 근거 |
|---|---|---|---|
| 재①-ON순서 | WalkFwd→WalkArrive→CamCut→Align×8(순서, CamCut t > WalkArrive t) | **PASS** | 실측 delta=+0.168s(양수). 이전 세션(재배치 전)엔 CamCut이 WalkForward보다도 먼저 발생했던 것과 명확히 대조. |
| 재②-OFF완전차단 | OFF 턴에서 CamCut·Align(컷) 완전 0건 | **PASS** | `WalkArrive(t=8.001)`와 `TakeHit` 사이 CamCut·컷Align 로그 전무, 오직 마지막 복귀Align(yaw=84)×8만 존재. §명세모순에서 남았던 문제(OFF 턴에도 CamCut 발생)가 완전히 해소됨. |
| 재③-전투로직무변경 | BattleLog/WalkFwd/WalkArrive/TakeHit/TakeHitRevert 정상 | **PASS** | 두 턴 모두 전 패턴 정상 발생, 기존 로그 형식 무변경. |
| 재④-컴파일·저장 | warnings_as_errors 0, dirty=false | **PASS** | BP_BattleManager 컴파일 0/0. `save_assets([])` 후 BP_BattleManager/map_battle_octopath/BP_CamToggleButton 3개 전부 `is_dirty=false`. |

**§명세 내부 모순 — 해소됨.** §1(게이트 삽입 지점)과 §2(CamCut 0건 요구)의 상충은 "게이트 위치가 틀렸던 게 아니라 컷 블록 자체의 원 위치가 v3 명세와 달랐던" 근본 원인에서 비롯됐음이 확정됐다. 컷 블록을 v3 명세 위치(Delay 뒤, 걷기 도착 후)로 재배치하고 그 지점에 게이트를 걸자 §1·§2 요구사항이 모순 없이 동시에 충족됐다.

### 정리·저장(재배치 세션)
스캐폴드 24개 노드(2턴 버전) 전부 `delete_node`, `BeginPlay.then` `break_pins`로 원복(재조회 `connected_pins:[]` 확인), `ScaffoldTarget` 변수 `remove_variable`로 제거. `compile_blueprint(warnings_as_errors=true)` 최종 0/0. `save_assets([])` 후 3개 애셋 전부 `is_dirty=false`.

---

## 라벨 키 소실 결함(저장 누락) 수정 (2026-07-08, 오너 실플레이 리포트 대응)

### 경위
오너가 실플레이 중 카메라 토글 버튼에 `<MISSING STRING TABLE ENTRY>` 대형 텍스트가 표시되고 버튼 위치가 불명확하다고 리포트했다. Director 사전 추정대로 `ST_UI`의 `Battle.CamOn`/`Battle.CamOff` 키가 소실된 상태였다.

### 근본 원인 확정 — `StringTableTools.set_entry`는 패키지를 dirty로 표시하지 않는다
`list_keys(/Game/UI/ST_UI)` 최초 조회 결과 `["Battle.Attack"]` 단 1개뿐 — `Battle.CamOn`/`Battle.CamOff`뿐 아니라 `Battle.Cancel`도 애초에 존재하지 않았다(지시서가 "기존 키 Battle.Cancel"이라 가정한 것과 실제가 다름, §아래 "부수 발견" 참조). `set_entry`로 두 키를 추가한 직후 `AssetTools.is_dirty("/Game/UI/ST_UI")`를 호출하자 **`false`**가 반환됐다 — 즉 `set_entry`가 실제 데이터(FStringTable)는 메모리상에서 정확히 변경하지만(`get_entry`/`list_keys` 재조회로 확인) **패키지의 dirty 플래그는 세팅하지 않는다.** 이 상태에서 `save_assets(["/Game/UI/ST_UI"])`(명시적 경로)를 호출하면 `returnValue: true`를 반환하지만 **실제로는 디스크에 아무것도 쓰지 않는다**(파일 mtime 불변, 바이너리에 `CamOn`/`Cam ON` 문자열 부재를 직접 확인) — 이것이 이번 사고와 원래 결함의 정확한 메커니즘이다. 대조 실험: 신규 생성한 스크래치 StringTable(`create`)은 생성 직후 `is_dirty=true`였고, 그 상태에서 `set_entry`+`save_assets`를 하자 디스크에 정상 반영됐다(파일 바이너리에 키/값 문자열 확인) — **`create`는 정상적으로 dirty를 세팅하지만 `set_entry`(기존 애셋에 대한 개별 키 편집)는 세팅하지 않는 비대칭 버그**로 확정.

### ⚠ 조사 중 발생한 2차 사고 — `import_file`이 기존 ST_UI.uasset을 삭제함
위 dirty 버그를 우회하려고 `StringTableTools.import_file`(CSV 재임포트)로 강제 저장을 시도했다. `folder_path=/Game/UI, asset_name=ST_UI`로 호출하자 `"create_asset: ST_UI at /Game/UI already exists"` 에러로 실패했는데, **이 실패한 호출이 부작용으로 기존 `Content/UI/ST_UI.uasset` 파일 자체를 디스크에서 삭제**했다(`find_assets`가 빈 결과, `ls Content/UI/`에 파일 없음으로 확인). `.gitignore`에 `Content/` 전체가 걸려 있어 git 복구 불가(`git log`/`git status` 확인, 커밋된 적 없음) — **이 프로젝트에서 Content 애셋은 git으로 백업되지 않는다는 것도 이번에 확정**.
**복구**: 소실 직전 알고 있던 원본 데이터(`Battle.Attack`="Attack" 단 1개 키)를 근거로 `create`+`set_entry`×3(Attack/CamOn/CamOff)+`save_assets`로 처음부터 재생성 — `create` 경로는 정상 dirty이므로 이번엔 저장이 실제로 반영됨(재시작 시나리오까지 흉내낼 순 없었지만 디스크 바이너리에 5개 문자열 전부 존재 확인, `is_dirty=false`로 저장 완료 확정). **재생성 후 기존 참조(BP_AttackButton.Label, BP_CamToggleButton.LabelOn/LabelOff, 레벨 인스턴스+CDO 양쪽) 전부 자동으로 재해석 성공**(재조회로 "Attack"/"Cam ON"/"Cam OFF" 정상 확인) — StringTable 참조가 오브젝트 GUID가 아니라 **경로 기반 테이블ID+키 문자열**로 동작함을 실증, 애셋을 통째로 재생성해도 참조가 깨지지 않는다는 것을 확인했다(단, 이번 복구가 우연히 안전했던 것이지 권장 절차는 아님 — 아래 정식 해법 참조).

### 정식 해법(재발 방지)
`set_entry`로 기존 StringTable을 편집한 뒤에는 **`is_dirty`가 `true`인지 반드시 재확인**할 것 — `false`면 `save_assets`를 아무리 호출해도 무음 실패한다. 이번 세션에서 시도한 우회(메타데이터 태그로 강제 dirty, 리네임 왕복)는 실제로 검증하지 못한 채 재생성 경로로 대체했다 — **후속 과제**: `set_entry` 이후 dirty가 안 걸리는 경우의 확실한 강제-dirty 수단(예: `update_metadata_tags`로 더미 태그 세팅 후 제거하는 2회 저장 사이클)을 다음 세션에서 실증할 것. 그 전까지는 **기존 StringTable에 새 키를 추가할 때마다 `is_dirty` 재확인을 습관화**하고, `false`로 남으면 (a) 즉시 Director에게 보고하거나 (b) 이번처럼 "알고 있는 전체 키 목록으로 `create` 재생성" 경로로 우회할 것(단, 재생성 전 `list_keys`+`get_entry`로 **기존 키 전체를 빠짐없이 백업**해야 함 — 이번엔 원래 키가 1개뿐이라 단순했지만 키가 많은 ST_UI라면 전수 백업 없이는 위험).

### 부수 발견 — `Battle.Cancel` 키도 원래 존재하지 않았음(별도 결함, 이번 스코프 밖)
지시서는 "기존 키(Battle.Attack/Cancel)는 무변조"라 가정했으나 실제로는 `Battle.Cancel`이 세션 시작 시점부터 `list_keys`에 없었다. `BP_AttackButton`의 `LabelCancel` 컴포넌트(`bVisible=true`, `Attack` 라벨과 정확히 같은 앵커에서 Left 정렬로 길게 뻗어나가는 배치)가 이 때문에 상시 `<MISSING STRING TABLE ENTRY>`를 표시 중이며, 기본 전투 카메라 화면에 `Attack` 글자 위로 겹쳐 크게 노출된다(스크린샷 확인). 이번 작업 지시 범위(CamOn/CamOff만)를 벗어나므로 **키를 임의로 추가하지 않고 Director에게 보고만 함** — 별도 후속 작업 필요.

### 라벨 정렬 조정 및 시인성 점검
`LabelOn`/`LabelOff`(인스턴스+CDO 양쪽)의 `HorizontalAlignment`를 `EHTA_Left`→`EHTA_Center`, `VerticalAlignment`를 `EVRTA_TextBottom`→`EVRTA_TextCenter`로 변경 — Attack 버튼(`EHTA_Center`/기존 정상 배치) 패턴에 맞춤, 수평 중앙 정렬이 뚜렷이 개선됨(재조회+`CaptureViewport` 확대 캡처로 확인). `RelativeLocation.Z`를 30→0→-140까지 낮춰보며 판 중앙에 세로로 맞추는 실험을 했으나, **Z를 크게 낮출수록(특히 -140) 텍스트가 캡처에서 완전히 사라지는 비단조적 회귀가 3회 연속 재현**됐다(§노하우 신규 함정, 아래 참조) — CLAUDE.md의 "3회 실패 시 중단" 원칙에 따라 **Z=30(원래값)으로 되돌리고 정렬 변경만 유지**했다. 최종 상태: 텍스트는 판 상단 경계에 살짝 걸치는 정도(완전히 판 안에 중앙정렬되진 않음, 원래보다 개선)로 legible하게 렌더링됨(캡처로 확인, `Cam ON`/`Cam OFF` 텍스트 내용 정확).

### ⚠ 중대 발견 — 기본 전투 카메라 거리에서 카메라 토글 버튼이 사실상 보이지 않음
실제 기본 전투 카메라(CameraActor_0, location≈(-171,-8731,1207), rotation(pitch-6,yaw84,roll0), 버튼까지 거리≈1780cm) 시점 캡처를 **3회 반복**했으나(정렬 수정 전후 모두) `UI_CamToggle`의 파란 판·라벨이 화면에서 전혀 식별되지 않았다(같은 스크린 좌표를 5배 확대해도 잔디/흙 텍스처만 보임 — `WorldPosToScreenCoords`로 정밀 좌표 계산 후 크롭 확인). 반면 같은 거리에서 `Attack` 버튼(스케일 4,2,1 / Z=420)은 뚜렷이 보인다. CamToggle 버튼(스케일 2.2,1.2,1 / Z=260, Attack 대비 훨씬 낮고 작음)이 지면 근처 잔디에 묻히거나 단순히 너무 작아 보이지 않는 것으로 추정 — **이는 이번 문자열 결함과 무관한, 원래 배치(v3/VF 이전 세션)부터 있던 스케일/높이 설계 문제로 판단되며, 버튼의 전체 스케일이나 Z 높이를 키우는 결정은 system-ui-designer 검토가 필요해 이번 세션에서 임의로 변경하지 않았다.** (버튼 자체는 기능적으로 정상 작동 — 클릭 판정·토글 로직은 이전 세션에서 로그로 검증 완료, 이번엔 순수 시각적 식별성 문제.)

### CT — 이번 수정 검증
| 항목 | 판정 | 근거 |
|---|---|---|
| ST_UI에 Battle.CamOn/CamOff 키 존재 | **PASS** | `list_keys`=["Battle.Attack","Battle.CamOn","Battle.CamOff"], 디스크 바이너리 직접 확인 |
| ST_UI 디스크 저장(재시작 내구성) | **PASS**(간접) | `is_dirty=false`+파일 mtime 갱신+바이너리 문자열 확인(재시작 자체는 미실행이나 디스크 반영을 직접 실증) |
| LabelOn/LabelOff Text 해석값 | **PASS** | 인스턴스+CDO 양쪽 재조회 "Cam ON"/"Cam OFF" (MISSING 아님) |
| 라벨 렌더링(실제 화면) | **PASS** | 확대 캡처에서 "Cam ON" 텍스트 정상 렌더 확인(값 소실 아님, §12 함정⑫ 계열의 캡처 불안정 재현되긴 했으나 최종 안정 상태에서 확인) |
| 버튼 위치·스케일 원본값 유지 | **PASS** | (-650,-7300,260)/scale(2.2,1.2,1) 무변경 확인 |
| 기본카메라 거리 시인성 | **FAIL(이월)** | 위 "중대 발견" 참조 — Director/system-ui-designer 판단 필요 |
| compile 0/0, 3애셋 dirty=false | **PASS** | `compile_blueprint(warnings_as_errors=true)` 통과, `is_dirty` 3종 모두 false |

### 이번 세션에서 확정된 신규 노하우(요약, 전체는 `언리얼_MCP_실전노하우.md` §18 참조)
- `StringTableTools.set_entry`는 dirty를 세팅하지 않음(재저장 누락의 근본원인) — `create`는 정상.
- `import_file`을 기존 경로에 시도해 실패하면 **원본 애셋이 삭제될 수 있음**(재현 1회, 위험도 높음) — 함부로 재시도 금지.
- 비균등스케일+회전 부모의 자식(TextRenderComponent)에서 `RelativeLocation` 국소축 변경이 화면상 비선형·비단조 결과(정상→부분소실→완전소실)를 낳을 수 있음 — §7 함정②의 확장 사례.

---

## 토글 버튼 마무리 수정 3건 — Cancel 키 영속화·라벨 기본숨김·시인성 (2026-07-08, Director 후속 지시)

### 경위
직전 세션("라벨 키 소실 결함 수정")이 스코프 밖으로 보고했던 이월 항목 2건(`Battle.Cancel` 키 부재, 기본카메라 거리 시인성 FAIL)과 오너 실플레이에서 재확인된 LabelCancel 상시노출 문제를 Director 지시로 마무리했다. 시작 시점 `list_keys(/Game/UI/ST_UI)` = `["Battle.Attack","Battle.CamOn","Battle.CamOff"]`(3개, `Battle.Cancel` 부재 재확인 — §라벨 키 소실 문서의 "부수 발견"과 정확히 일치).

### ① `Battle.Cancel`="Cancel" 키 복구 — 함정⑳이 이번 세션에서도 그대로 재현, 재생성 폴백으로 해소
`set_entry(Battle.Cancel, "Cancel")` 직후 `AssetTools.is_dirty("/Game/UI/ST_UI")` = **`false`**(함정⑳ 재현). `save_assets(["/Game/UI/ST_UI"])`는 `returnValue:true`를 반환했지만 저장 전후 파일 정보가 완전히 동일했다:
- mtime: 저장 전/후 모두 `2026-07-08 05:20:25.87`(불변)
- `grep -c "Battle.Cancel" ST_UI.uasset`: 저장 후에도 **0**

즉 "성공"이라는 리턴값 뒤에서 실제로는 무음 스킵됐음을 이번 세션에서도 직접 실측 재확인했다. 지시서의 폴백 절차를 그대로 실행:
1. 기존 4키(메모리상 `Battle.Attack`="Attack", `Battle.CamOn`="Cam ON", `Battle.CamOff`="Cam OFF", `Battle.Cancel`="Cancel") `get_entry`로 전량 백업.
2. `AssetTools.delete("/Game/UI/ST_UI")` → `Content/UI/` 폴더가 완전히 빈 상태임을 `ls`로 확인(의도된 삭제, `import_file` 경로가 아니므로 함정㉑과 무관).
3. `StringTableTools.create(/Game/UI, ST_UI)` → 생성 직후 `is_dirty=true`(함정⑳의 대조군과 일치).
4. `set_entry` 4회를 **순차** 호출(Attack→Cancel→CamOn→CamOff, §8 함정⑤ "병렬 호출 시 이름/데이터 충돌" 예방 원칙을 StringTable 편집에도 적용).
5. `save_assets(["/Game/UI/ST_UI"])` → `is_dirty=false`.
6. **디스크 바이너리 최종 검증**: 파일 mtime이 `05:58`대로 신규 갱신, `grep -c`로 4키+4값 전부 확인:

```
Battle.Attack: 2   Battle.Cancel: 2   Battle.CamOn: 2   Battle.CamOff: 2
Attack: 4          Cancel: 4          Cam ON: 2         Cam OFF: 2
```

**참조 재해석 재검증(2번째 재생성 사례)**: 재생성 후 `get_properties`로 4개 컴포넌트(Label/LabelCancel/LabelOn/LabelOff, 인스턴스+CDO 양쪽)를 전부 재조회한 결과 MISSING 없이 정확한 문자열로 해석됨을 확인 — §라벨 키 소실 문서가 1차 실증한 "StringTable 참조는 경로+키 기반이라 애셋을 통째로 재생성해도 깨지지 않는다"는 결론이 **독립적인 2번째 재생성으로 재확정**됐다.

### ② `LabelCancel` 기본 숨김 복원
세션 시작 조회에서 흥미로운 비대칭이 발견됐다: **CDO는 이미 `bVisible=false`**였으나(직전 세션 기록엔 CDO 상태가 명시되지 않아 정확한 변경 시점 불명 — 어느 시점에 CDO만 수정되고 인스턴스는 누락된 것으로 추정) **레벨 인스턴스(`UI_AttackButton.LabelCancel`)는 `bVisible=true`**로 남아 있었다. 즉 ①의 키 복구 전에는 `<MISSING STRING TABLE ENTRY>`가, 키 복구 후에는 legible한 "Cancel" 텍스트가 Attack 버튼 위에 상시 겹쳐 보이는 상태였을 것(증상의 형태만 바뀌고 근본 문제—항상 켜져 있음—는 동일).
인스턴스+CDO 양쪟에 개별 `set_properties({"bVisible": false})` 호출 후 재조회로 둘 다 `false` 확정. `Label`(Attack)은 인스턴스 `bVisible=true` 무변경 재확인(기본 노출 유지, 런타임 `ShowCancel`/`ShowAttack` 토글 로직은 이번 세션에서 손대지 않음 — 그래프 배선은 이미 완성 상태로 별도 조사 불필요했음).

### ③ 카메라 토글 버튼 시인성 (Director 결정 — 디자인 라운드 없이 진행)
`UI_CamToggle`(=`BP_CamToggleButton_C_0`, 루트 컴포넌트가 `ButtonBg`이므로 액터 트랜스폼 = `ButtonBg` 트랜스폼)에 `set_actor_transform`(location/rotation/scale 3필드 전부 명시, worldspace=true)을 적용:

| | 이전 | 이후 |
|---|---|---|
| location | (-650, -7300, **260**) | (-650, -7300, **420**, Attack 버튼과 동일 Z) |
| rotation | (90, 84, 0) | (90, 84, 0, 무변경) |
| scale | (**2.2, 1.2**, 1) | (**3.0, 1.5**, 1) |

기본 전투 카메라(`CameraActor_0`, 실측 location(-170.58,-8730.78,1207.07)/rotation(pitch-6,yaw84,roll0)) 시점으로 `CaptureViewport`(captureTransform 지정+annotations 전부 0/null+bShowUI=false, 3파라미터) 1장 캡처 → Pillow로 Cam ON 판 영역 크롭 후 4배 확대(NEAREST)로 자가검증. **"Cam ON" 텍스트와 판이 뚜렷이 식별됨**(글자 왜곡·전단 없음, 판 형태 정상 사각형) — 스케일 3.6 증분 없이 1회차(3.0)로 통과. 우측 팀 4기·Attack 버튼 주변 크롭도 확인해 **어느 쪽도 가려지지 않음**을 확정. §라벨 키 소실 문서의 "기본카메라 거리 시인성 FAIL(이월)" 항목이 이번에 해소됨.

### CT — 이번 3건 검증
| 항목 | 판정 | 근거 |
|---|---|---|
| ① `Battle.Cancel` 디스크 영속 | **PASS** | 재생성 전 `grep -c`=0(저장 스킵 재확인) → 재생성+저장 후 4키 전부 카운트 2, mtime 갱신 |
| ① 참조 재해석(4개 컴포넌트, 인스턴스+CDO) | **PASS** | Label/LabelCancel/LabelOn/LabelOff 전부 재조회, MISSING 없음 |
| ② LabelCancel 기본 숨김 | **PASS** | 인스턴스+CDO 양쪽 `bVisible=false`, `Label`(Attack) `bVisible=true` 무변경 |
| ③ 토글 버튼 위치·스케일 재조회 일치 | **PASS** | `get_actor_transform` = (-650,-7300,420)/(90,84,0)/(3,1.5,1) |
| ③ 기본카메라 시인성 | **PASS** | 캡처+크롭 확대로 "Cam ON" legible 확인, Attack버튼·8기 유닛 비가림 확인 |
| compile 0/0(2 BP), 5애셋 dirty=false | **PASS** | `BP_AttackButton`/`BP_CamToggleButton` `compile_blueprint(warnings_as_errors=true)` 통과. `ST_UI`/`BP_AttackButton`/`BP_CamToggleButton`/`map_battle_octopath`/`map_battle_village` 5개 전부 `is_dirty=false` |

### 관찰 — 스코프 밖, 참고용 (임의 수정하지 않음)
- `BP_AttackButton.Label`의 **CDO** `Text`는 리터럴 `"Text"`(TextRenderComponent 컴파일 기본값)로 남아 있고, StringTable `LOCTABLE` 참조는 **레벨 인스턴스에만** 바인딩된 것으로 관찰됨(§17 "CDO와 인스턴스 양쪽 개별 세팅 필요"와 같은 계열이나, 현재 유일한 배치 인스턴스가 정확히 렌더되므로 기능상 영향 없음 — 새 인스턴스를 추가 배치할 때만 잠재적으로 드러날 수 있는 이슈).
- 캡처 이미지에서 모든 유닛·양 버튼 주변에 붉은 화살표(+판을 매다는 가는 선) 오버레이가 일관되게 관찰됨 — 이번 세션 작업으로 생긴 부작용이 아니며(모든 액터에 동일 패턴 존재, `set_actor_transform`/`set_properties` 등 이번에 손댄 조작과 무관), 기존 씬의 시각 요소 또는 별개 디버그 표시로 추정. 이번 스코프 밖이라 원인 조사하지 않음.
