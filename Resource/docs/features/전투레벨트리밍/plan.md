---
type: plan
project: projectTP
stage: B
updated: 2026-07-12
status: 완료
---

# 전투 레벨 트리밍 (`map_battle_octopath`)

## Context
테스트로 올려둔 전투 레벨이 `map_village_day`(Fantastic_Village_Pack 원본 마을) 전체를 복제해 만들어져, 실제 게임에 쓰는 것(`BattleStage` 15개+`environment` 13개=28개)보다 훨씬 많은 장식 소품(`assets/` 1,718개)을 그대로 안고 있었다. 레벨 복잡도·에디터 성능·아웃라이너 시야 정리를 위해, 다이오라마 카메라가 실질적으로 보지 않는 소품만 골라 레벨에서 제거했다(원본 메시 애셋 자체는 무변경 — 벤더팩 디스크 용량은 별개 문제, 이번 범위 아님).

계획 전문(리뷰 이력 포함): `C:\Users\user\.claude\plans\humble-purring-glacier.md`(Part B). 3에이전트(qa-critic·scene-builder·art-pipeline) + gameplay-engineer·hd2d-art-director·verifier 리뷰를 거쳐 실행.

## 핵심 발견
- **카메라는 2대뿐**(계획 초안의 "ActionCamParty/ActionCamEnemy 고정 2기" 전제는 틀렸음 — art-pipeline·scene-builder가 독립적으로 정정): `DefaultCamera`(고정) + `ActionCam_Dynamic`(공격자·피격자 기준 매공격 재계산, `BP_BattleManager_C_0`에서 공식 라이브 확정: `camLoc = A - axis*350 + lat*250 + (0,0,250)`).
- 화톳불·화로 등 조명/파티클 무드 소품은 `assets/FX` 폴더가 아니라 `assets/props`에 무작위로 섞여 있어, **폴더 기준이 아니라 컴포넌트(PointLight/Particle) 기준 필터**가 필요했다(실측으로 확인).

## 절차 및 결과
1. **백업**: UE 애셋 `/Game/Stages/_archive/map_battle_octopath_full`(3중 확인: duplicate=True+exists=True+액터수 1718 일치) + 물리 `.umap` 복사본 스크래치패드 보존(`C:\Users\user\AppData\Local\Temp\claude\D--unreal-Resource\7246227d-0e35-430a-a874-e287b4339af8\scratchpad\map_battle_octopath_backup_20260712.umap`, 7,203,408 bytes) — **정리는 오너 판단, 장기 보존 원하면 별도 위치로 이동 권장**.
2. **범위판정**: 32개 공격자×피격자 조합(4v4 양방향)으로 `ActionCam_Dynamic` 포즈 포락선 계산 → AABB(keep-box) + 컴포넌트 필터(광원/파티클 보유 소품은 좌표 무관 별도 분리) + 스카이라인(건물 29+망루 10=39개) 별도 분리.
3. **Dry-run**: 좌표기준 대상 1,642개 중 Tier1(보수적, 5개)/Tier2(실용적, 1403개) 산출, 캡처 5장으로 오너 사전 승인 요청.
4. **오너 승인**: Tier2 채택(2026-07-12).
5. **실행**: 파일럿 30개 → 본 청크 7회(200×6+173) → **1,403/1,403 성공, 실패 0**, 서킷브레이커 미발동.
6. **저장**: `AssetTools.save_assets` 성공, `is_dirty=false` 확인.
7. **검증**: verifier PIE 정상(참조 에러 0) + 액터수 일치(`assets`=315, `BattleStage`=15, `environment`=13 무변경) + 연못(`water_1`/`water_2`) 삭제 부위 육안 대조(삭제 전후 동일 포즈, scene-builder+Director 직접 확인) — crater·이음새 없이 자연스러움.
8. **오너 최종 육안 확인**: "잘 동작한다" (2026-07-12).

## 최종 수치
| 항목 | 삭제 전 | 삭제 후 |
|---|---|---|
| `BattleStage/` | 15 | 15 (무변경) |
| `environment/` | 13 | 13 (무변경) |
| `assets/` | 1,718 | 315 |

## 부산물 (별개 이슈, 다른 태스크로 이월)
캡처 검증 중 `ActionCam_Dynamic`의 일부 근접컷(적 공격 각도 등)에서 카메라가 근처 돌벽에 바짝 붙어 화면 상당 부분을 가리는 프레이밍 문제를 발견 — 이번 트리밍과 무관한 기존 카메라 이슈. 대기 중인 "카메라-VF(오너 육안+수치 튜닝)" 작업에서 다룰 것.

## 재현/롤백 경로
- UE 백업: `/Game/Stages/_archive/map_battle_octopath_full`
- 물리 백업: 위 scratchpad 경로(`map_battle_octopath_backup_20260712.umap`)
- 롤백 필요 시 전체 복원 또는 개별 액터만 백업에서 재삽입 가능(전체를 되돌릴 필요 없음).
