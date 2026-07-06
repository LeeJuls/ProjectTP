---
type: log
---

# S2p — BP_BattleSpawnPoint 8기 교체 초기 배치 백업

T1(BP 구현) + T2(8기 교체) 완료 시점 기록. 오너가 배치가이드(T3)에서 실수 시 "리셋해줘" 요청하면 이 문서의 값으로 복원한다.

## 구 8기(StaticMeshActor) — 삭제 전 원본 트랜스폼

| 라벨 | Location | Rotation | Scale | 머티리얼(교체 전) |
|---|---|---|---|---|
| Party_A1 | (-600, -6990, 613.453) | (0,0,90) | (6.48,2.59,1) | MI_Party_A1_flip |
| Party_A2 | (-450, -6908, 621.331) | (0,0,90) | (6.48,2.59,1) | MI_Party_A2_flip |
| Party_A3 | (-300, -6794, 635.827) | (0,0,90) | (6.48,2.59,1) | MI_Party_A3_flip |
| Party_A4 | (-150, -6705, 678.488) | (0,0,90) | (6.48,2.59,1) | MI_Party_A4_flip |
| Enemy_B1 | (150, -6695, 612.482) | (0,0,90) | (6.48,2.59,1) | MI_Enemy_B1 |
| Enemy_B2 | (300, -6806, 615.425) | (0,0,90) | (6.48,2.59,1) | MI_Enemy_B2 |
| Enemy_B3 | (450, -6892, 630.955) | (0,0,90) | (6.48,2.59,1) | MI_Enemy_B3 |
| Enemy_B4 | (600, -7010, 642.68) | (0,0,90) | (6.48,2.59,1) | MI_Enemy_B4 |

Party 4기는 원래 flip(왼쪽 보기) 상태, Enemy 4기는 non-flip(오른쪽 보기) 상태였다 — 이게 "초기 배치"(사선 대치) 기준값.

## 신규 8기(BP_BattleSpawnPoint 인스턴스) — 최종 배치 상태

에셋: `/Game/Blueprints/BP_BattleSpawnPoint`
폴더: 아웃라이너 `BattleStage/SpawnPoints`

⚠ **FaceLeft 열은 2026-07-06 오너 요청으로 반전됨**(아래 값이 현재·복원 기준값). 원래 T1/T2 직후엔 Party=true/Enemy=false(서로 마주봄)였으나, 오너가 "party와 enemy 바라보는 방향을 반대로" 요청 후 확인("방향 맞아")해 이 반전 상태가 새 기준. "리셋해줘"는 아래 표(반전 후) 기준으로 복원할 것 — 마주보던 옛 상태로 되돌리지 말 것.

| 라벨 | 내부 오브젝트명 | Location | FaceLeft(현재) | SpriteRight | SpriteLeft |
|---|---|---|---|---|---|
| SpawnPoint_Party_A1 | BP_BattleSpawnPoint_C_0 | (-600, -6990, 613.453) | **false** | MI_Party_A1 | MI_Party_A1_flip |
| SpawnPoint_Party_A2 | BP_BattleSpawnPoint_C_9 | (-450, -6908, 621.331) | **false** | MI_Party_A2 | MI_Party_A2_flip |
| SpawnPoint_Party_A3 | BP_BattleSpawnPoint_C_2 | (-300, -6794, 635.827) | **false** | MI_Party_A3 | MI_Party_A3_flip |
| SpawnPoint_Party_A4 | BP_BattleSpawnPoint_C_3 | (-150, -6705, 678.488) | **false** | MI_Party_A4 | MI_Party_A4_flip |
| SpawnPoint_Enemy_B1 | BP_BattleSpawnPoint_C_4 | (150, -6695, 612.482) | **true** | MI_Enemy_B1 | MI_Enemy_B1_flip |
| SpawnPoint_Enemy_B2 | BP_BattleSpawnPoint_C_5 | (300, -6806, 615.425) | **true** | MI_Enemy_B2 | MI_Enemy_B2_flip |
| SpawnPoint_Enemy_B3 | BP_BattleSpawnPoint_C_6 | (450, -6892, 630.955) | **true** | MI_Enemy_B3 | MI_Enemy_B3_flip |
| SpawnPoint_Enemy_B4 | BP_BattleSpawnPoint_C_7 | (600, -7010, 642.68) | **true** | MI_Enemy_B4 | MI_Enemy_B4_flip |

액터 자체(root) 트랜스폼: rotation=(0,0,0), scale=(1,1,1) — identity. Sprite 컴포넌트(루트로 승격됨)의 relativeRotation=(0,0,90), relativeScale3D=(6.48,2.59,1)이 시각적 회전/스케일을 담당한다.

**주의**: 내부 오브젝트명(BP_BattleSpawnPoint_C_N)은 액터를 삭제·재생성하면 새 번호로 바뀐다(위 C_9가 그 예 — 원래 C_1이었으나 디버깅 중 삭제·재생성됨). 복원 시 라벨로 식별할 것.

## 리셋 절차 (오너 "리셋해줘" 요청 시)

각 SpawnPoint 액터를 아웃라이너에서 라벨로 찾아:
1. Details 패널에서 Transform(Location) = 위 표의 값으로 재입력
2. FaceLeft = 위 표의 값으로 재입력 (다른 항목은 Construction Script가 자동 재계산)

## 검증 이력

- 8기 위치·회전·스케일·변수·적용 머티리얼: gameplay-engineer가 `get_properties`/`get_actor_transform` 재조회로 확인 완료.
- world bounds 신구 비교: 액터 전체 `get_actor_bounds`는 ArrowComponent(에디터 전용 방향 표시, bHiddenInGame=true) 포함으로 부풀려진 값이 나오는 것을 확인했으나, Sprite 컴포넌트만 별도로 동일 트랜스폼의 임시 StaticMeshActor로 대조한 결과 8기 전부 구 액터와 완전 일치(0% 오차, 이중적용 없음).
