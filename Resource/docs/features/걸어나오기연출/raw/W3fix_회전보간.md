---
type: raw
feature: 걸어나오기연출
stage: W3fix
updated: 2026-07-07
---

# W3fix — 걸음 왜곡 핫픽스: MoveComponentTo 회전 보간 미배선 수정
#projectTP/걸어나오기연출

승인 plan: `C:\Users\user\.claude\plans\humble-purring-glacier.md`(Director 직접 진단으로 원인 확정 완료 — 재조사 없이 수정+검증만 수행).

## 원인 (Director 확정, 이번 세션에서 그래프 재조회로 재확인)
`BP_BattleSpawnPoint` EventGraph의 `MoveComponentTo` 노드 2개:
- `K2Node_CallFunction_113`(x=-3400, y=-1200) — WalkBack 체인(HomeLocation으로 복귀)
- `K2Node_CallFunction_143`(x=500, y=-600) — WalkForward 체인(WalkTargetLoc으로 전진)

둘 다 `TargetRelativeRotation` 핀이 미배선 상태였다(`get_node_infos` 재확인: `"value":"0, 0, 0","connected_pins":[]`). `MoveComponentTo`는 위치와 회전을 함께 latent 보간하므로, 매 걸음마다 Sprite(루트, `relativeRotation.roll=90`인 스프라이트 쿼드)의 회전이 기본값 (0,0,0)으로 보간되어 눕혀짐 → 비균등 스케일(6.48, 2.59, 1)과 결합해 이동 중 꾸겨짐 + 도착 후 회전 0 고착으로 지속 왜곡.

## 수정
두 `MoveComponentTo` 각각에 대해 **MakeRotator 노드를 신규 생성**하고 `TargetRelativeRotation`에 배선(리터럴 문자열 직접 세팅은 Rotator 필드 순서 모호성 때문에 기각 — plan 지시대로 MakeRotator + 필드별 `set_pin_value` 채택).

1. **MakeRotator 노드 2개 생성** (`수학|로테이터|MakeRotator`, 정확한 `create_node` 문자열은 `find_node_types` 재조회로 확인):
   - `K2Node_CallFunction_167`(WalkBack용, `_113` 근처) — Pitch=0.0, Yaw=0.0, **Roll=90.0**(각 필드 `set_pin_value` 개별 호출로 명시 — 필드 index_id: Roll=0, Pitch=1, Yaw=2, 확인 후 세팅).
   - `K2Node_CallFunction_168`(WalkForward용, `_143` 근처) — 동일 값.
   - 세팅 후 `get_node_infos` 재조회로 Roll=90.0/Pitch=0.0/Yaw=0.0 전 필드 일치 확인(§7 함정③은 `ObjectTools.set_properties` 인라인 구조체 한정 버그이고, 그래프 노드 `set_pin_value`는 이 버그와 무관함을 재확인 — 문제 없이 1회 세팅으로 정확히 반영됨).
2. `connect_pins`로 각 MakeRotator의 `ReturnValue`(EGPD_Output, index_id=0) → 해당 MoveComponentTo의 `TargetRelativeRotation`(EGPD_Input, index_id=5)에 배선.
3. 배선 재조회(`get_node_infos`)로 확인: `_113.TargetRelativeRotation.connected_pins`에 `_167` 연결됨, `_143.TargetRelativeRotation.connected_pins`에 `_168` 연결됨.
4. `compile_blueprint(warnings_as_errors=true)` — BP_BattleSpawnPoint 에러 0, 경고 0.

## 검증 (WT-23)

### 스캐폴드 설계
BP_BattleManager BeginPlay(원래 완전히 빈 상태 — `이벤트추가|BeginPlay이벤트`의 `then` 핀 `connected_pins:[]` 확인 후 착수)에 임시 구성:
```
BeginPlay → Delay(3.0) → NotifyAttackButtonClicked() → Delay(0.3) → NotifyUnitClicked(GetTurnQueue()[1])
```
- `NotifyAttackButtonClicked`/`NotifyUnitClicked`는 자기 자신 BP(BP_BattleManager) 멤버라 `find_node_types` 반환 문자열(`함수호출|X`)이 `create_node`에 그대로 통과(§14 대조군 그대로 재확인).
- `ClickedUnit` 파라미터는 `GetTurnQueue()` → `Utilities|Array|Get(사본)`(Dimension1=1)로 동적 조회 — 리터럴 오브젝트 레퍼런스 사용하지 않음(§9 함정⑥ 회피, 어차피 이번 검증은 팀 로직이 아니라 회전값만 보는 것이라 인덱스 1 고정 사용은 plan 지시 그대로 채택).

### RotCheck 로그 삽입 지점 2곳 (BP_BattleSpawnPoint)
1. **WalkForward**: `_143`(MoveComponentTo).then과 `_154`(기존 WalkArrive PrintString) 사이에 삽입.
2. **WalkBack**: `_113`(MoveComponentTo).then과 `_159`(기존 idle 복귀 시작 SetScalarParameterValue) 사이에 삽입.

각 지점 체인: `GetSprite → GetWorldRotation(self) → ToString(Rotator) → FormatText("RotCheck:{0}:arrive/home:rot={1}", 인자0=기존 GetDisplayName 노드 fan-out, 인자1=회전문자열) → ToString(Text) → PrintString`.

**명세 조정 1건**: plan은 "Sprite GetRelativeRotation을 로그"라 명시했으나, `GetRelativeRotation`은 `find_node_types`가 여러 형식(`Class|씬컴포넌트|GetRelativeRotation`, `Variables|트랜스폼|GetRelativeRotation`)으로 반환함에도 전부 `create_node`에서 "does not exist"로 실패(§10/§14 패턴과 유사하나 이번엔 엔진 네이티브 SceneComponent 함수라 그 해법들이 적용 안 됨, `declaring_class` 명시도 무효). 3종 형식 전부 실패 확인 후, Sprite가 이 액터의 **루트 컴포넌트**(부모 없음)라는 구조적 사실에 근거해 `GetWorldRotation`(성공 확인된 `트랜스포메이션|GetWorldRotation`)으로 대체 — 루트 컴포넌트는 Relative=World이므로 검증 목적(roll=90 유지 확인)에 동일하게 유효. 실제 회전 미스매치 원인(`TargetRelativeRotation` 미배선)과 무관한 순수 로깅 방식의 차이이며 결과 값 자체는 동일.

### 실행 결과
`IsPIERunning` 확인(false) → `EditorPerformanceSettings.bThrottleCPUWhenNotForeground` 확인(false, 변경 불필요) → `StartPIE(warmup=2s)` → 로그(UTC `date -u` 08:32:19와 로그 타임스탬프 `2026.07.07-08.32.2x` 정확히 대조해 §10 지연/UTC 착시 배제) 확인:

```
[2026.07.07-08.32.24:199] State:Executing:t=3.4
[2026.07.07-08.32.24:199] WalkFwd:SpawnPoint_Party_A1:t=3.4:target=X=-350.000 Y=-6750.000 Z=633.453
[2026.07.07-08.32.24:535] RotCheck:SpawnPoint_Party_A1:arrive:rot=P=0.000000 Y=0.000000 R=90.000000   ← 도착 직후, roll=90 유지
[2026.07.07-08.32.24:535] WalkArrive:SpawnPoint_Party_A1:t=3.733:loc=X=-350.000 Y=-6750.000 Z=633.453
[2026.07.07-08.32.26:199] RotCheck:SpawnPoint_Party_A1:home:rot=P=0.000000 Y=0.000000 R=90.000000     ← 복귀 직후, roll=90 유지
[2026.07.07-08.32.26:199] WalkHome:SpawnPoint_Party_A1:loc=X=-1020.000 Y=-7380.000 Z=633.453
```

**도착(arrive) roll=90, 복귀(home) roll=90 — 양쪽 모두 유지 확인.** 수정 전이었다면 두 로그 모두 roll=0(MakeRotator 미배선 상태의 기본값)으로 나왔을 것.

`StopPIE` 실행 → 스캐폴드(BP_BattleManager BeginPlay 6노드) 전부 `delete_node`로 제거, BeginPlay `then` 핀 `connected_pins:[]`로 원복 확인, BP_BattleManager 재컴파일 0. RotCheck 로그 관련 신규 10노드(양쪽 5개씩)도 `break_pins`로 원래 직결(`_143.then→_154`, `_113.then→_159`) 복원 후 전부 `delete_node`로 제거, BP_BattleSpawnPoint 재컴파일 0 — 핵심 수정(MakeRotator 2개 + 배선)만 남고 진단용 임시 노드는 완전히 제거됨.

## 저장
`save_assets([])` → BP_BattleSpawnPoint `is_dirty=false`, BP_BattleManager `is_dirty=false`, map_battle_octopath `is_dirty=false` 전부 확인.

## 알려진 이슈/제약
- `GetRelativeRotation`(SceneComponent) 함수는 이 MCP `create_node`에서 어떤 문자열 형식으로도 생성 불가로 확정(3종 시도 전부 실패) — 루트 컴포넌트 한정으로 `GetWorldRotation` 대체가 유효하나, **비루트 컴포넌트의 RelativeRotation을 그래프에서 직접 조회해야 하는 향후 케이스**에서는 별도 우회(예: `GetRelativeTransform`으로 자기 자신 기준 상대 트랜스폼을 구해 회전만 Break)가 필요할 수 있음(이번 세션에서는 검증 불요, 이월).
- 이번 수정은 W1에서 이미 8기 전원이 동일 그래프 구조(WalkForward/WalkBack)를 공유한다는 사실(W1 raw 문서 확인)에 근거해 Party_A1 1기 실측으로 8기 전체에 대한 구조적 보증으로 간주. 개별 유닛 8기 전수 로그 재현은 이번 세션 범위 밖(비범위 아님, 단지 동일 그래프 공유 구조상 불필요 판단).
