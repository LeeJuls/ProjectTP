---
type: raw
project: projectTP
feature: 전투완성
stage: 야간F7a
status: 게이트 PASS 2026-07-16 야간
updated: 2026-07-16
---

# 야간F7a 완료 — 스킬메뉴 실전배선 게이트 통과

> 대상: [[F7_스킬아키텍처_확정]] §7-1(F7a 스코프 원안)·§11-2(메뉴 플랫리스트 판정) · [[F7_TC]] G01·U01·U02·U04·E02(F7a 검증대상) · [[언리얼_MCP_실전노하우]] §32
> 스킬메뉴를 목업(정적 3행)에서 실전 배선으로 전환한 결과를 기록한 문서. `EnterAwaitTarget`이 하드코딩하던 `"ENEMY1"` 리터럴을 `PendingTargetToken`으로, `EnterExecuting`이 하드코딩하던 SkillId 리터럴을 `NotifySkillSelected`/Attack박스 세팅으로 교체해 기존 5스킬을 실전 구동시키고 쿨다운을 실장했다. Attack박스는 이번 단계에서 폐기하지 않고 병존시킨다(폐기는 F7b).
#projectTP/전투완성

---

## 1. 무엇이 됐나 — 스코프 & 구현 체인

**스코프**: 스킬메뉴 실전 배선(플랫 3행). 하드코딩 제거 2건 — `EnterAwaitTarget`의 `"ENEMY1"` 리터럴 → `PendingTargetToken`, `EnterExecuting`의 SkillId 리터럴 → `NotifySkillSelected`/Attack박스 세팅. 기존 5스킬을 실전 구동, 쿨다운 실장. Attack박스는 폐기하지 않고 **병존**(폐기는 F7b로 이월).

**구현 3스텝**:
1. **Manager 함수군**
   - `NotifySkillSelected` 신설 — 가드 3중(`bInputLocked` · `State` · 쿨다운).
   - `EnterAwaitTarget` 토큰화 — 하드코딩 `"ENEMY1"` 제거, `PendingTargetToken`으로 교체.
   - `NotifyUnitClicked`에 `ResolveTargetPool` 멤버십 판정 추가 — **ALLY 클릭을 여는 열쇠**(치유 등 아군 타겟팅에 필요).
   - `EnterExecuting`은 F6이 만든 `PendingSkillId` 고정 Set을 우회해 실제 선택값을 반영하도록 재배선.
2. **Menu/Row 배선**
   - `SetActiveUnit` 스텁을 재사용해 본체 구현 — lazy `ManagerRef` 확보 + `JobId`로 `DT_JobStats`의 `skillIds` 파싱 + 3행 스탬프 + `DT_Strings` 라벨 + 쿨다운 비활성화.
   - Row `AssignOnClicked` → `ManagerRef.NotifySkillSelected`(`SkillIdNum`을 Integer로 통일).
   - `ST_UI`에 `Skill.*` 라벨 키 5종 추가 — 이 과정에서 **strings.csv ↔ ST_UI 싱크 갭**을 발견(원인 규명은 F7b로 이월).
3. **Manager 표시 제어**
   - `EnterAwaitCommand`: `SetActiveUnit` 호출 + `Visible`.
   - `Executing`/`End`: `Collapsed`.

## 2. 결함 4건 검출·수정 서사 (E2E 6차까지, 핵심 서사)

E2E 반복 6차에 걸쳐 결함 4건과 보너스 1건을 검출·수정했다.

### ① Menu.SetActiveUnit lazy-init의 `GetAllActorsOfClass.then` 미연결
`SetActiveUnit`이 lazy `ManagerRef`를 확보하는 체인에서 `GetAllActorsOfClass`의 `then` 실행핀이 다음 노드에 연결되지 않은 상태였다 — 컴파일은 통과했지만 본체가 실행되지 않았다. Director가 직접 1와이어로 연결.

### ② 목업 잔재 히트테스트
표시 전용으로 만들었던 Row 인스턴스 등 위젯 8개에 `SelfHitTestInvisible`류 설정이 그대로 남아, 실전 배선 전환 후에도 클릭이 통과(투과)했다. 컨테이너 `SelfHitTestInvisible`/버튼 `Visible`/버튼 내부 요소 `HitTestInvisible`의 정석 구성으로 8위젯 전부 정리.

### ③ `SetInputMode` 프로젝트 전체 0건
이번이 프로젝트 **최초의 진짜 UMG 버튼**이었는데, 지금까지 월드 액터(Attack박스) 클릭만 쓰던 프로젝트라 Slate가 클릭 자체를 미수신했다(호버조차 발생 안 함). `InitBattle`에 `SetInputMode(GameAndUI)` 추가로 해결.

### ④ Manager.NotifySkillSelected `FunctionEntry.then` 미연결
①과 동일 패턴 — `NotifySkillSelected` 함수의 `FunctionEntry.then`이 본체에 연결되지 않아 호출은 되지만 본체가 실행되지 않았다. Director가 직접 1와이어로 연결.

### ⑤ 보너스 — SELF 스킬 소프트락 (F4부터 잠복하던 미연결 then)
막기(SELF 대상) 스킬을 선택하면 소프트락에 걸렸다. 원인은 카메라 컷의 "거리<1.0" 퇴화 분기가 **F4 단계부터 미연결 상태로 잠복**해 있던 것 — 8기의 실전 배치 거리는 항상 1.0을 훨씬 초과해 이 분기가 지금까지 한 번도 실행되지 않았는데, SELF 스킬(캐스터-대상 거리=0)이 처음으로 이 분기에 도달하며 소프트락으로 발현됐다. 카메라 미발동 경로가 합류하도록 연결 1개를 추가해 해결.

이 5건은 [[언리얼_MCP_실전노하우]] §32 함정(66)~(69)의 출처가 됐다(①④→(66), ②→(68), ③→(67), ⑤→(69)).

## 3. 검증 — 판정표 (6차 최종)

| 항목 | 결과 |
|---|---|
| 메뉴 3행 스탬프·라벨 | 공격/베기/막기, `ST_UI` 라벨 정상 |
| 베기 | 42 데미지 + STUN(`effectRoll=0.003` applied) |
| 파이어볼 | 61 데미지 + ATK_DOWN + 캐스팅 모션(`PendingMotionRow` 10 / `FrameCount` 5.0) |
| 막기 | SELF 즉시시전 + `bBlockActive` + 피격 15 반감 |
| 치유 | -33 힐, HP 59→90(클램프) |
| 쿨다운 재사용 차단 | 행 비활성화(1차 방어)·함수 가드(도달 불가 안전망) 정합 확인 |
| 월드 클릭 회귀 | 무손상 |
| Executing 메뉴 숨김 | 화면 증거로 확인 |
| 에러 | 0 |

쿨다운·Row 프로퍼티 조회는 PIE 조회값이 stale해 액터 프로퍼티(`SkillCooldowns`)·화면 증거로 교차판정했다([[언리얼_MCP_실전노하우]] §32 함정(70)). 쿨다운 행 클릭 차단은 Slate 레벨(`bEnabled=false`)에서 이미 소진되어 함수 내부 거절 로그는 도달 불가 안전망임을 확인했다(§32 함정(71)).

## 4. 세이브포인트

`D:\unreal\_savepoints\야간F7a_스킬메뉴\`(4애셋).

## 5. 이월 (F7b) — 아침 오너 육안

- Category 탭.
- Attack박스 폐기 / End 이주.
- Menu의 `NotifySkillSelected(Name)` 스텁 정리.
- Row 구 `SkillId(Name)` 변수 정리.
- SELF 스킬 카메라 연출.
- `strings.csv` ↔ `ST_UI` 싱크 갭 원인 규명.
- 유닛 `JobId` 명명 정리(실값이 캐릭터ID로 쓰이고 있음).
- 아침 육안: 메뉴 사용감·스킬 4종 연출.

---

## 관련
- [[F7_스킬아키텍처_확정]] §7-1(F7a 스코프 원안) · §11-2(메뉴 플랫리스트 판정)
- [[F7_TC]] G01·U01·U02·U04·E02(F7a 검증대상 TC)
- [[언리얼_MCP_실전노하우]] §32 (야간F7a 신규 함정 6건 — (66)~(71))
