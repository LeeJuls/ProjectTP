---
type: raw
feature: 공격버튼데모
stage: D1
status: 완료
updated: 2026-07-06
---

# D1 — M_Sprite_Flipbook_Lit에 TimeOffset 추가 (수행 기록)

## 0. Subtract 클래스 확인
`list_expression_classes(search="Subtract")` → `/Script/Engine.MaterialExpressionSubtract` 1건. 중단 조건 아님, 진행.

## 1~3. 노드 추가 + 배선
| 노드 | refPath | 좌표(X,Y) | 속성 |
|---|---|---|---|
| ScalarParameter(신규) | `MaterialExpressionScalarParameter_7` | (-2340, 0) | ParameterName=`TimeOffset`, DefaultValue=0 |
| Subtract(신규) | `MaterialExpressionSubtract_0` | (-2200, 0) | 입력핀 `["A","B"]` |

기존 참조 좌표(조회 실측): Time_0(-2340,162), Multiply_0(-2080,162), ScalarParameter_4/FPS(-2340,324), Floor_0(-1820,162), ScalarParameter_6/FlipX(-1560,650), OneMinus_0(-1300,650). 신규 노드는 Y=0(빈 여백)에 배치해 겹침 없음.

배선 3건:
- `Time_0("")` → `Subtract_0.A`
- `ScalarParameter_7("")` → `Subtract_0.B`
- `Subtract_0("")` → `Multiply_0.A` (기존 Time_0→Multiply_0.A 직결 자동 대체됨, disconnect 불필요 확인)

## 4. 재조회 이중검증 (2회, 결과 동일)
`get_expression_inputs(Multiply_0)`:
- A = `Subtract_0`
- B = `ScalarParameter_4`(FPS, **불변 확인**)

`get_expression_inputs(Subtract_0)`:
- A = `Time_0`
- B = `ScalarParameter_7`(TimeOffset)

1차/2차 조회 결과 완전 일치 — 배선 확정.

## 5. Recompile
`recompile(M_Sprite_Flipbook_Lit)` → 에러 없음, 성공.

## 6. MI 상속 검증
`get_referencers("/Game/Materials/M_Sprite_Flipbook_Lit")` → **16종 확정** (예상과 일치):
- `MI_Party_A1, A2, A3, A4`
- `MI_Enemy_B1, B2, B3, B4`
- `MI_Party_A1_flip ~ A4_flip`
- `MI_Enemy_B1_flip ~ B4_flip`

각 MI에 대해 `ObjectTools.get_properties(instance, ["ScalarParameterValues"])`로 override 배열 직접 조회(override 상태를 정확히 판별하기 위해 `get_scalar_parameter`의 effective-value만으로는 불충분하다고 판단 — override 여부는 `ScalarParameterValues` 배열 존재로 판별):

| MI 그룹 | override된 파라미터 | TimeOffset override |
|---|---|---|
| `MI_Party_A1~A4`, `MI_Enemy_B1~B4` (8종) | `FPS`=8 만 | 없음 → 부모(0) 상속 |
| `_flip` 8종 | `FlipX`=1 만 | 없음 → 부모(0) 상속 |

보조로 `get_scalar_parameter(instance, "TimeOffset")`도 16종 전체 조회 — 전원 effective value = 0 (상속 정황 일치).

**결론: 16종 전원 TimeOffset override=false, 기본 0 상속 확인.**

## 7. 렌더 회귀 캡처
- 시작 시 현재 로드 레벨: `/Game/Stages/map_battle_village` (지시서 절차 진입 전 상태).
- a. `map_battle_octopath` 로드 → CaptureViewport(location(-90,-7850,750), rotation(pitch-6,yaw84,roll0), annotations 전부 0/null, bShowUI=false) → `D1_octopath_idle.png`. **육안 판정: 정상** — 양측 캐릭터 idle 포즈, 도트 뭉개짐/텍스처 손상 없음.
- b. `map_battle_village` 로드 → 캡처 전 `GetCameraTransform()`으로 현재 뷰포트 확인(location(0,-7850,750), rotation(pitch-6,yaw90,roll0) — 이미 정면대치 구도) → 그 값을 명시적으로 CaptureViewport에 전달(3파라미터 모두 명시) → `D1_village_idle.png`. **육안 판정: 정상** — 정면대치 idle 정상, 마스터 recompile 무오염 실증.
- c. `map_battle_octopath` 재로드 → `get_current_level()`로 재확인 완료. D2 인계를 위해 에디터는 octopath 상태로 남김.

## 8. 저장
- `save_assets(["/Game/Materials/M_Sprite_Flipbook_Lit"])` → `true`.
- 레벨은 저장하지 않음. `is_dirty` 조회 결과: `map_battle_octopath`=false, `map_battle_village`=false, `M_Sprite_Flipbook_Lit`=false(저장 후 클린 확인).

## 발견한 함정 / 특이사항
- `get_scalar_parameter`(MaterialInstanceTools)는 override 여부와 무관하게 유효값(부모 상속 포함)만 반환하므로, "override=false 확인"이라는 요구를 충족하려면 `ObjectTools.get_properties`로 `ScalarParameterValues` 배열의 존재 유무를 직접 봐야 한다. 지시서 6번 항목은 이 방식으로 수행함 — effective-value만 보고 "override 없음"이라 결론내리면 오탐 가능성 있음(우연히 0으로 override된 경우와 구분 불가).
- CaptureViewport 반환 base64가 약 600만자로 매 호출 tool-results txt로 spill됨 — 지시서 파이프라인(`decode_capture.py`) 그대로 작동, 문제 없음.
- 별도 함정 발견 없음. 지시서의 확정 사실(Time_0 유일 소비처, 출력핀 무명 등)은 전부 재조회로 재확인되어 일치.
