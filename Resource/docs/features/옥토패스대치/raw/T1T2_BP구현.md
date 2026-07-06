---
type: log
---

# T1+T2 — BP_BattleSpawnPoint 구현 + 8기 교체

gameplay-engineer 구현 로그. 승인된 plan(`humble-purring-glacier.md`) T1·T2 섹션 기준.

## T1 — MI 4종 + BP 생성

### MI_Enemy_B1~B4_flip (4종 생성)

경로: `/Game/Materials/MI_Enemy_B1_flip` ~ `MI_Enemy_B4_flip`
- 부모: `/Game/Materials/M_Sprite_Flipbook_Lit`
- **중요 발견**: `FlipX`는 plan 문서상 "static switch"로 추정됐으나 실제로는 **Scalar 파라미터**다(`set_scalar_parameter` 사용, `set_static_switch_parameter` 아님). `list_parameters`로 확인: GridX/GridY/RowIndex/FrameCount/FPS/EmissiveBoost/FlipX 전부 Scalar, SpriteTex만 Texture.
- 값: FlipX=1(override 활성 후 set), SpriteTex=T_Party_B1~B4(override 활성 후 set)
- 재조회 검증: 4종 모두 FlipX=1, SpriteTex 정확히 매핑됨.
- **기존 12종 MI 무변조 확인**: MI_Party_A1~A4(FlipX=0)/A1~A4_flip(FlipX=1)/Enemy_B1~B4(FlipX=0) 전부 재조회로 이전과 동일값 확인.

### BP_BattleSpawnPoint 생성

경로: `/Game/Blueprints/BP_BattleSpawnPoint` (부모=`/Script/Engine.Actor`)

컴포넌트:
- `Sprite`(StaticMeshComponent) — `set_parent_component`로 루트 승격(DefaultSceneRoot 자동 제거 확인). StaticMesh=SM_SpriteQuad, 상대회전(0,0,90)[pitch,yaw,roll], 상대스케일(6.48,2.59,1.0), Mobility=Movable.
- `Arrow`(ArrowComponent) — bHiddenInGame=true. CS에서 FaceLeft에 따라 relativeRotation yaw 0/180 설정(방향 시각 보조, 선택 기능 구현함).

변수(전부 instance_editable=true):
- `FaceLeft`(bool, CDO 기본=false)
- `SpriteRight`(MaterialInstance ref, CDO 기본=None)
- `SpriteLeft`(MaterialInstance ref, CDO 기본=None)

### DSL 문법 탐색 결과

- **최상위 문법**: `(event ConstructionScript ...)`가 유효(UserConstructionScript 그래프는 이미 `K2Node_FunctionEntry_0`이 존재하며 type_id=`|ConstructionScript`).
- **로케일 주의**: 이 프로젝트/엔진은 한글 로케일이라 node type_id의 카테고리명도 한글화되어 있다(`Development|PrintString`이 아니라 `개발|PrintString`, `Variables|Default|Get*`가 아니라 `Variables|디폴트|Get*`, `렌더링|머티리얼|SetMaterial` 등). `find_node_types`로 정확한 카테고리명을 먼저 조회해야 한다.
- **`select` DSL 표현식 미지원**: `(select cond a b)`가 문서에 나와 있지만 실제로는 `Utilities|Select does not exist` 에러 발생. 이 UE 버전/로케일에는 문서가 가정하는 범용 K2Node_Select type_id가 존재하지 않는다(타입별 특화 SelectFloat/SelectColor 등은 있으나 MaterialInterface용 범용 select 없음). **대안으로 if/else(Branch) 사용**.
- **`write_graph_dsl`의 exec 연결 결함(중대)**: 단일 PrintString 하나만 넣어도, 또는 if/else 전체를 한 번에 넣어도 **노드는 생성되지만 exec(실행) 핀 연결이 전혀 이뤄지지 않는다**(값/데이터 핀은 정확히 설정됨). `get_connected_subgraph`로 검증 시 FunctionEntry.then이 미연결로 확인. **워크어라운드**: `create_node`로 각 노드 개별 생성 → `get_node_infos`로 정확한 pin index_id 획득 → `connect_pins`로 모든 exec/data 연결을 수동 배선. 이 방식으로 실제 작동하는 그래프 완성.
- **`read_graph_dsl`도 신뢰 불가**: 정상적으로 연결된 그래프에서도 항상 빈 문자열(`""`)을 반환. 검증은 `get_connected_subgraph`/`get_node_infos`로만 수행.

### 최종 CS 로직 (수동 배선)

```
FunctionEntry(ConstructionScript).then
  -> Branch.execute (Condition = GetFaceLeft)
     Branch.then(FaceLeft=true, 좌측)
       -> IsValid(SpriteLeft).exec
          "Is Valid" -> SetMaterial(self=GetSprite, ElementIndex=0, Material=SpriteLeft).execute
             .then -> SetRelativeRotation(self=GetArrow, NewRotation=(0,180,0))
          "Is Not Valid" -> (미연결, 스킵=기존 유지 — null 가드)
     Branch.else(FaceLeft=false, 우측)
       -> IsValid(SpriteRight).exec
          "Is Valid" -> SetMaterial(self=GetSprite, ElementIndex=0, Material=SpriteRight).execute
             .then -> SetRelativeRotation(self=GetArrow, NewRotation=(0,0,0))
          "Is Not Valid" -> (미연결, 스킵)
```

- `self`는 액터 self가 아니라 **컴포넌트 변수 getter**(GetSprite/GetArrow)를 명시적으로 사용 — plan 지적사항 반영.
- null 가드: CDO 상태(SpriteRight/Left=None)에서 실제로 SetMaterial 미호출 확인(overrideMaterials=[]로 유지).
- `compile_blueprint(warnings_as_errors=true)` 통과, 에러/경고 0.
- CDO 최종 확인: FaceLeft=false, SpriteRight=None, SpriteLeft=None(명세대로).

## T2 — 8기 교체

### ① 구 8기 실측 백업

`docs/features/옥토패스대치/raw/S2p_초기배치백업.md`에 구 8기(StaticMeshActor_0~7, 라벨 Party_A1~A4/Enemy_B1~B4) 트랜스폼·머티리얼 전체 기록.

### ② BP 8기 스폰

`add_to_scene_from_asset`, xform=location만(실측값 그대로), snap_to_ground=false. 라벨은 `name` 파라미터가 그대로 반영됨(별도 set_label 불필요했으나 사고 복구 과정에서 1건 명시적 재확인함).

### ③ 폴더 지정

`set_actor_folder`로 8기 전부 `BattleStage/SpawnPoints`. `get_actors_in_folder` 재조회로 8개 확인.

### ④ 인스턴스별 변수 설정

Party_A1~A4: FaceLeft=true, SpriteRight=MI_Party_A*, SpriteLeft=MI_Party_A*_flip
Enemy_B1~B4: FaceLeft=false, SpriteRight=MI_Enemy_B*, SpriteLeft=MI_Enemy_B*_flip

CS가 `set_properties` 직후 자동 재실행되어 정확한 머티리얼 적용 확인(Party 4기→flip 적용, Enemy 4기→non-flip 적용, 기존 8기와 동일 방향).

### ⑤ 검증 중 발견한 중대 결함 2건 (근본원인 추적 후 해결)

**결함 A — `add_to_scene_from_asset`가 xform 미지정 필드를 identity로 강제**: plan은 "xform=location만 지정하면 rotation/scale은 CDO 기본값 유지"를 가정했으나, 실제로는 컴포넌트의 relativeRotation/relativeScale3D가 **(0,0,0)/(1,1,1)로 강제 오버라이드**됐다(CDO 자체는 정상값 유지, 인스턴스만 오염). world bounds 신구 비교(±1%)에서 이 문제를 실측으로 검출 — plan이 설계한 이 검증 절차가 정확히 의도대로 작동함.

- 근본원인: 스폰 시 rotation/scale 미지정 → 엔진이 identity로 인스턴스 오버라이드 생성(CDO 상속이 아니라 오버라이드 값 자체가 identity로 굳음).
- 해결: 스폰 후 각 인스턴스의 Sprite 컴포넌트에 `set_properties`로 relativeRotation(roll=90)·relativeScale3D(x=6.48,y=2.59) 재적용.

**결함 B — `set_properties`가 구조체(Vector/Rotator) 값의 다중 필드를 한 번에 못 받음**: `{"roll": 90}`처럼 단일 필드는 정확히 반영되지만, `{"pitch":0,"yaw":0,"roll":90}`처럼 3필드를 동시에 주면 **전부 무시**되거나(관찰1), `{"x":0.001,"y":0.001,"z":0.001}`처럼 3필드 벡터를 주면 **일부만 반영**(관찰2: x만/또는 x,y만 반영되고 나머지 필드는 이전 값 유지)되는 비결정적 결함을 재현 확인. **워크어라운드: 벡터/로테이터의 각 필드를 개별 `set_properties` 호출로 분리**(roll만, x만, y만 순차 호출)하면 100% 안정적으로 반영됨. 이후 모든 트랜스폼 설정은 이 방식으로 통일.

이 결함 진단 과정에서 실험적으로 만든 임시 액터(BP_BattleSpawnPoint_C_1, 원래 SpawnPoint_Party_A2)를 삭제→재생성 시도 중 원본을 완전히 잃어버리는 사고가 있었으나, 라벨·트랜스폼·변수를 모두 재설정하여 즉시 복구(신규 refPath: BP_BattleSpawnPoint_C_9). 8기 전체 최종 재검증 완료.

### world bounds 신구 비교 (결정적 검증)

`get_actor_bounds`(액터 전체)는 ArrowComponent(bHiddenInGame=true, 에디터 전용 방향 표시)가 포함되어 부풀려진 값(예: X폭 290 vs 정상 648)을 반환하는 것을 확인했다 — 이건 **게임플레이/렌더링에 영향 없는 에디터 전용 편차**다(bounds 계산 로직이 hidden-in-game 컴포넌트도 포함하기 때문). Arrow를 배제한 순수 검증을 위해:
1. Arrow의 relativeScale3D를 사실상 0으로 만들어 bounds에서 배제 → 정상값(100,100,~0 근사) 확인.
2. 8기 각각과 동일한 위치·회전·스케일·메시(SM_SpriteQuad)로 임시 StaticMeshActor를 만들어 bounds 대조 → **8기 전부 구 액터와 완전 일치(오차 0%)**. 이중적용(스케일 중복) 없음 확정.

### ⑥ 구 StaticMeshActor 8기 삭제

`remove_from_scene` 8회. 재조회로 구 스타일 액터(`StaticMeshActor_N`) 0개, BP_BattleSpawnPoint 인스턴스 정확히 8개 확인. 배경 StaticMeshActor 총수 1615→1607(정확히 8 감소, 무오염).

### ⑦ octopath 저장 + 신규 에셋 저장

`save_assets(["/Game/Stages/map_battle_octopath"])`. `is_dirty` 재확인 false.

**plan 보완**: plan은 "octopath만 저장"을 지시했으나, T1에서 만든 신규 에셋(MI_Enemy_B1~B4_flip 4종, BP_BattleSpawnPoint)이 여전히 dirty=true 상태였다(레벨 저장과 별개로 에셋 자체 저장 필요). 에디터 재시작 시 유실 방지를 위해 추가로 `save_assets`로 5개 전부 저장, 재확인 dirty=false. plan이 "octopath만"이라 명시한 건 T2(레벨 저장) 단계에 한정된 지시로 해석하고, T1 신규 에셋은 별도 저장이 맞다고 판단함 — Director 확인 요망.

### ⑧ village dirty 확인 — **plan-실제 불일치 발견**

plan은 "village·village_day dirty=false 확인"을 지시했으나, **`/Game/Stages`에는 `map_battle_octopath`와 `map_battle_village` 2개만 존재**한다(`map_village`, `map_village_day`라는 이름의 레벨은 프로젝트에 없음). `map_battle_village`의 dirty는 false로 확인했으나, plan이 가리킨 정확한 대상이 이것인지, 아니면 다른 프로젝트/과거 문서의 이름 잔재인지 Director 확인 필요.

## 캡처 검증

`CaptureViewport`(captureTransform=location(-90,-7850,750)/rotation(pitch-6,yaw84,roll0), annotations 전부 0/null, bShowUI=false) → tool-results → `decode_capture.py`로 디코드 → `raw/T2_교체후.png` 저장.

이미지 확인: 8기 캐릭터 정상 렌더링, 사선 배치(초기 배치) 유지, 이중적용/크기이상 흔적 없음. 화면에 붉은 화살표(레벨의 기존 다른 요소로 추정, 이번 작업과 무관) 및 좌하단 월드좌표 기즈모(뷰포트 고정 UI, bShowUI와 무관하게 항상 표시)가 보이나 T1/T2 산출물과 무관.

## 산출물 요약

| 항목 | 경로 |
|---|---|
| MI 4종 | `/Game/Materials/MI_Enemy_B1_flip` ~ `MI_Enemy_B4_flip` |
| BP | `/Game/Blueprints/BP_BattleSpawnPoint` |
| 레벨 | `/Game/Stages/map_battle_octopath` (저장됨) |
| 백업 문서 | `docs/features/옥토패스대치/raw/S2p_초기배치백업.md` |
| 캡처 | `docs/features/옥토패스대치/raw/T2_교체후.png` |

## 명세와 다르게 구현한 부분 (qa-critic 대조용)

1. **CS 로직 구현 방식**: plan은 `(select FaceLeft SpriteLeft SpriteRight)` 표현식 사용을 지시했으나, 이 엔진/로케일 환경에서 해당 DSL 표현식이 매핑하는 `Utilities|Select` type_id가 존재하지 않아 **if/else(Branch) 구조로 대체**. 최종 동작(FaceLeft 진실값 기준 SpriteLeft/Right 선택 + null가드 + SetMaterial)은 명세 의도와 동일.
2. **DSL 일괄 작성 대신 노드별 수동 배선**: `write_graph_dsl`의 exec 연결 결함으로 인해, 최종 그래프는 `create_node`+`connect_pins` 조합으로 노드 하나하나 명시적으로 생성·배선함. 결과 그래프 구조는 plan 설계와 동일.
3. **T2 세부 절차 순서 변경**: plan의 "④검증→⑤백업→⑥삭제" 순서에서, 검증 단계 중 발견한 트랜스폼 오염 문제(결함 A)를 해결하기 위해 ④와 ⑤ 사이에 "Sprite 컴포넌트 rotation/scale 재적용" 스텝이 추가됨. 백업 문서에는 이 재적용 이후의 최종 정상 상태를 기록.

## 알려진 제약 / TODO

- **`set_properties`의 다중 필드 구조체 설정 결함**은 이 MCP 서버(ProgrammaticToolset이 아닌 ObjectTools 자체)의 문제로 보이며, 향후 이 프로젝트에서 Vector/Rotator/LinearColor 등 구조체 프로퍼티를 설정할 때는 **반드시 필드별 개별 호출**을 표준 절차로 삼아야 한다. verifier/qa-critic도 이 패턴을 인지할 것.
- **`get_actor_bounds`는 hidden-in-game 컴포넌트(Arrow 등)를 포함**하므로, 향후 world bounds 비교 검증 시 액터 전체가 아니라 필요시 컴포넌트 단위 또는 Arrow 배제 후 비교가 안전.
- **`read_graph_dsl`은 신뢰 불가(항상 빈 문자열)** — 그래프 검증은 `get_connected_subgraph`/`find_nodes`+`get_node_infos` 조합으로만 수행할 것.
- village/village_day 레벨명 불일치는 Director 확인 대기.
