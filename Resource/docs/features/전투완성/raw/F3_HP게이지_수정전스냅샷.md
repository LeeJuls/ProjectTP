---
type: log
---

# F3 HP게이지 수정 착수 전 스냅샷 (Director 진단 반영 롤백 지점)

Director가 오너 라이브 확인에서 "HP 게이지 안 보임"을 직접 MCP로 진단(2026-07-14). 원인: `bAbsoluteLocation/Rotation/Scale=true`로 세팅한 절대좌표 방식이 실제로는 회귀였음 — 8기 모두 월드 좌표 `(actorX, 0, 0)` 근방(캐릭터 위치 Y/Z 무시)에 고정되고, 회전도 pitch90(눕힘)이라 안 보였다.

## 수정 착수 직전 8기 HpGaugeText 상태 (전부 동일 패턴)

| 라벨 | bAbsoluteLocation | bAbsoluteRotation | bAbsoluteScale | RelativeLocation | RelativeRotation | Text |
|---|---|---|---|---|---|---|
| SpawnPoint_Party_A1 | true | true | true | (-1020, 0, 0) | (pitch90, yaw0, roll0) | "90/90" |
| SpawnPoint_Party_A2 | true | true | true | (-920, 0, 0) | (pitch90, yaw0, roll0) | "90/90" |
| SpawnPoint_Party_A3 | true | true | true | (-690, 0, 0) | (pitch90, yaw0, roll0) | "80/80" |
| SpawnPoint_Party_A4 | true | true | true | (-808.025, 0, 0) | (pitch90, yaw0, roll0) | "80/80" |
| SpawnPoint_Enemy_B1 | true | true | true | (979.149, 0, 0) | (pitch90, yaw0, roll0) | "90/90" |
| SpawnPoint_Enemy_B2 | true | true | true | (1010, 0, 0) | (pitch90, yaw0, roll0) | "90/90" |
| SpawnPoint_Enemy_B3 | true | true | true | (990, 0, 0) | (pitch90, yaw0, roll0) | "80/80" |
| SpawnPoint_Enemy_B4 | true | true | true | (960, 0, 0) | (pitch90, yaw0, roll0) | "80/80" |

relativeScale3D은 8기 전부 (1,1,1)로 정상.

## 원인 분석 (재확인)
- 액터/Sprite(루트) 자체가 `roll=90`(HD-2D 스프라이트 컨벤션), `bAbsolute*=false`(정상, 카메라 정면 정렬 완성 상태).
- HpGaugeText는 Sprite의 자식인데 `bAbsoluteLocation/Rotation=true`로 세팅해 부모 좌표계에서 이탈 → RelativeLocation이 그대로 월드좌표로 취급됨.
- RelativeLocation.X만 실제 값(-1020 등)이고 Y/Z=0인 이유: 이전 세션에서 시각 캡처 우회를 위해 `ObjectTools.set_properties`로 직접 미러링을 시도하다 함정③(인라인 구조체 1필드만 반영)에 걸려 X/Pitch만 반영되고 나머지가 기본값(0)으로 남은 상태가 **그대로 저장됨** — 이게 결정적 실수(코스메틱이라 판단해 정리 안 하고 save했음).

## 롤백 절차
문제 발생 시 위 표의 값으로 8기 HpGaugeText의 `bAbsoluteLocation/Rotation/Scale`/`RelativeLocation`/`RelativeRotation`을 복원(단, 이 상태 자체가 "깨진" 상태였으므로 실질적 롤백 지점이라기보다 감사 기록용).
