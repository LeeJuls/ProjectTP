---
type: log
feature: 옥토패스대치
step: S1
updated: 2026-07-06
---

# S1 flip 구현 — FlipX 파라미터 + flip MI 4종 (art-pipeline)

> 상위: [[../plan|옥토패스대치 plan]] §1·§2 명세 그대로 구현.
> 목적: 아군 4기(화면 우측=월드 -X)를 flip MI로 좌향 렌더. 기존 8종 MI·정면대치 레벨은 절대 무변조(C1).

## 1. 그래프 조사 — get_expression_inputs 부정확성 실증

작업 전 마스터 `M_Sprite_Flipbook_Lit` 배선을 `get_expression_inputs`로 조회했을 때, **동일한 노드(`Add_0`)에 대해 두 번의 호출에서 B입력이 다르게 반환**됨을 실측 확인(수정 전: B=`ScalarParameter_0`/GridX, 배선 후 재조회: B=`Fmod_1`). B입력을 전혀 건드리지 않았는데도 값이 바뀐 것이므로, 이 도구의 반환이 신뢰 불가능함이 실증됨(plan §2 경고와 일치).

교차검증 수단:
- **레이아웃 좌표**(`materialExpressionEditorX/Y`)로 데이터 흐름 방향(왼→오) 재구성 — 파라미터 재사용 노드는 신뢰 불가하지만, 일반 연산 노드 인접성은 유효.
- **`get_property_input`**(MP_BaseColor/MP_OpacityMask/MP_EmissiveColor)으로 최종 출력 체인 불변 확인.
- 결론: **`Add_0`의 A입력 = `ComponentMask_0`(baseU)** 임은 최초 조회·레이아웃·재조회 3자 모두 일치 — 이 지점만 신뢰하여 교체 대상으로 확정. B입력(GridX 관련 col 오프스트 추정)은 일절 미터치.

## 2. 마스터 `M_Sprite_Flipbook_Lit` 수정

경로: `/Game/Materials/M_Sprite_Flipbook_Lit`

### 추가 노드 3종
| 노드 | 클래스 | 좌표(X,Y) | 설정 |
|---|---|---|---|
| `ScalarParameter_6` | `MaterialExpressionScalarParameter` | (-1560, 650) | ParameterName=**FlipX**, DefaultValue=**0** |
| `OneMinus_0` | `MaterialExpressionOneMinus` | (-1300, 650) | — |
| `LinearInterpolate_0` | `MaterialExpressionLinearInterpolate` | (-1040, 650) | Lerp(A,B,Alpha) |

기존 노드와 겹치지 않도록 Y=650(기존 그래프는 Y=0~486 사용)에 배치.

### 배선 (`connect_expressions` 명시 호출, 순서대로)
1. `ComponentMask_0` 출력 → `OneMinus_0` 입력(None)
2. `ComponentMask_0` 출력 → `LinearInterpolate_0.A`
3. `OneMinus_0` 출력 → `LinearInterpolate_0.B`
4. `ScalarParameter_6`(FlipX) 출력 → `LinearInterpolate_0.Alpha`
5. **`LinearInterpolate_0` 출력 → `Add_0.A`** (기존 `ComponentMask_0`→`Add_0.A` 연결을 교체 — col 오프셋 더하기 전 지점, 명세 그대로)

### 배선 재검증 (연결 직후 `get_expression_inputs` 재조회)
```
Add_0:              A=LinearInterpolate_0, B=Fmod_1        (A만 교체됨, B 불변)
LinearInterpolate_0: A=ComponentMask_0, B=OneMinus_0, Alpha=ScalarParameter_6
OneMinus_0:          입력(None)=ComponentMask_0
```
`MP_BaseColor`/`MP_OpacityMask`/`MP_EmissiveColor` 체인은 수정 전후 완전히 동일(`TextureSampleParameter2D_0`, `Multiply_1`) — 최종 출력 배선 불변 확인.

### 불변 확인 — col/GridX/GridY/RowIndex/FPS/Emissive 배선
수정 전/후 `get_expression_inputs` 대조 결과 아래 전부 무변화:
- `Add_1`(V축+RowIndex 경로): A=ComponentMask_1, B=ScalarParameter_2(RowIndex)
- `Divide_0`/`Divide_1`: A=Add_0/Add_1, B=Divide_0/Divide_1(GridX/GridY 나누기 체인)
- `Fmod_0`: A=Floor_0, B=ScalarParameter_0(GridX)
- `Fmod_1`: A=Fmod_0, B=ScalarParameter_0(GridX)
- `AppendVector_0`: UVs=Divide_0
- `Multiply_1`(Emissive): A=TextureSampleParameter2D_0.RGB, B=ScalarParameter_5(EmissiveBoost)

### recompile
`MaterialTools.recompile` 호출 → 에러 없음(반환 null, 예외 미발생).

## 3. flip MI 4종 신규 생성

경로: `/Game/Materials/` (부모=마스터 `M_Sprite_Flipbook_Lit`)

| MI | SpriteTex | FlipX(override) |
|---|---|---|
| `MI_Party_A1_flip` | `/Game/Sprites/T_Party_A1` | 1 |
| `MI_Party_A2_flip` | `/Game/Sprites/T_Party_A2` | 1 |
| `MI_Party_A3_flip` | `/Game/Sprites/T_Party_A3` | 1 |
| `MI_Party_A4_flip` | `/Game/Sprites/T_Party_A4` | 1 |

절차: `create`(부모=마스터) → `set_parameter_override`(FlipX, override=true) → `set_texture_parameter`(SpriteTex) → `set_scalar_parameter`(FlipX=1) → **재조회로 적용 확인**(`get_scalar_parameter`/`get_texture_parameter`). 4종 전부 FlipX=1, SpriteTex 대응 텍스처 정확히 적용 확인됨(override 미적용 사례 없음).

## 4. 기존 8종 MI·레벨 무변조 확인 (C1)

`get_scalar_parameter(FlipX)`로 8종 전부 조회 — **전부 0**(부모 DefaultValue 상속, 미오버라이드):
`MI_Party_A1`, `MI_Party_A2`, `MI_Party_A3`, `MI_Party_A4`, `MI_Enemy_B1`, `MI_Enemy_B2`, `MI_Enemy_B3`, `MI_Enemy_B4`.

작업 착수 전 `MI_Party_A1`의 FlipX도 0으로 사전 확인(기준값). 이번 S1에서 8종 MI에 대해 `set_*` 계열 호출을 전혀 수행하지 않았으므로 논리적으로도 무변조 보장.

## 5. 자체검증 — flip 렌더 육안 확인 (임시변경 → 원복)

레벨: `/Game/Stages/map_battle_octopath`(이미 로드 상태, `get_current_level`로 확인). 대상: `StaticMeshActor_0`(라벨=`Party_A1`, `StaticMeshComponent0`).

| 단계 | overrideMaterials | 조작 |
|---|---|---|
| 사전 확인 | `MI_Party_A1` | `get_properties`로 원본값 기록 |
| 임시 변경 | `MI_Party_A1_flip` | `set_properties`(overrideMaterials) → 즉시 재조회로 적용 확인 |
| 캡처 1(원경) | `MI_Party_A1_flip` | CaptureViewport, cam=(-600,-7850,750)/(pitch-6,yaw90,roll0) |
| 캡처 2(근접) | `MI_Party_A1_flip` | CaptureViewport, cam=(-600,-7300,760)/(pitch0,yaw90,roll0) |
| **원복** | `MI_Party_A1` | `set_properties`로 복귀 → 즉시 재조회로 확인 |
| 캡처 3(비교, 근접·동일 앵글) | `MI_Party_A1`(원복 후) | CaptureViewport, 캡처2와 동일 카메라 |
| 원복 최종 재확인 | `MI_Party_A1` | 작업 종료 직전 재조회 |

### 캡처 이미지 경로(스크래치패드, 세션 임시 — 산출물 아님)
- 원경(flip): `C:\Users\user\AppData\Local\Temp\claude\D--unreal-Resource\7246227d-0e35-430a-a874-e287b4339af8\scratchpad\S1_flip_check1.png`
- 근접(flip): `C:\Users\user\AppData\Local\Temp\claude\D--unreal-Resource\7246227d-0e35-430a-a874-e287b4339af8\scratchpad\S1_flip_check2_close.png`
- 근접(원본, 비교용): `C:\Users\user\AppData\Local\Temp\claude\D--unreal-Resource\7246227d-0e35-430a-a874-e287b4339af8\scratchpad\S1_original_check2_close.png`

### 육안 판정
근접 캡처 2장(flip vs 원본, 동일 카메라·동일 시각) 비교 결과: 캐릭터의 좌우 비대칭 디테일(무릎 보호대 밝은 회색부, 어두운 소매, 이마 장식 위치)이 **정확히 좌우 반전**되어 나타남 — FlipX=1이 실제로 스프라이트를 좌우 반전시킴을 시각 확인. 두 캡처의 캐릭터 포즈(팔/다리 자세)가 거울상 대칭 관계로 보여 **동일 애니메이션 프레임**임이 시사됨 — col 오프셋 로직이 유지된 채 U축만 반전됐다는 뜻으로, 명세가 우려한 "프레임 재생순서 역전" 버그는 관찰되지 않음. 도트(픽셀) 뭉개짐 없음(Nearest 필터 유지 확인, 근접 캡처에서 픽셀 경계 선명).

### 원복 확인
작업 종료 직전 재조회: `StaticMeshActor_0.StaticMeshComponent0.overrideMaterials = [{"refPath":"/Game/Materials/MI_Party_A1.MI_Party_A1"}]`, `get_label(StaticMeshActor_0) = "Party_A1"` — 원복 정확히 확인됨.

## 6. 저장

`save_assets`(대상: 마스터 1 + flip MI 4종만, 레벨 제외):
```
/Game/Materials/M_Sprite_Flipbook_Lit
/Game/Materials/MI_Party_A1_flip
/Game/Materials/MI_Party_A2_flip
/Game/Materials/MI_Party_A3_flip
/Game/Materials/MI_Party_A4_flip
```
반환 `true`. 저장 후 `is_dirty` 재확인: 5개 전부 `false`(저장 완료).

**레벨(`map_battle_octopath`)은 명세 5항에 따라 의도적으로 저장하지 않음** — `is_dirty` 확인 결과 `true`(dirty 상태 유지). 이는 문제가 아님: 임시 변경(overrideMaterials)이 이미 원본값으로 원복되어 실제 콘텐츠 차이는 없고, 레벨을 저장하든 discard하든 최종 상태는 동일함. dirty 플래그는 세션 중 "변경 후 되돌림" 이력이 남긴 잔여물.

## 산출물 요약

| 항목 | 경로/값 |
|---|---|
| 수정 자산 | `/Game/Materials/M_Sprite_Flipbook_Lit`(FlipX 파라미터+OneMinus+Lerp 추가, Add_0.A 재배선) |
| 신규 자산 4종 | `/Game/Materials/MI_Party_A1_flip`, `A2_flip`, `A3_flip`, `A4_flip` |
| FlipX 파라미터 | ParameterName=`FlipX`, DefaultValue=`0`(마스터), 4종 MI 전부 override=1 |
| 기존 8종 MI | 무변조 확인(FlipX=0 상속, 미오버라이드) |
| 레벨 | 임시변경→원복 확인, 저장 안 함(명세 준수) |
