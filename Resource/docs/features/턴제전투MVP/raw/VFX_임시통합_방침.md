---
type: decision
feature: 턴제전투MVP
status: 활성 (구조 재설계 전까지)
updated: 2026-07-07
---

# ⚠ VFX 임시 통합 방침 (오너 지시 — 별도 기록)

> 오너 원문: "vfx는 나중에 구조를 다시 잡아야 하니까 여기선 **눈 구별 가는 정도만** 해도 됨."
#projectTP/턴제전투MVP

## 방침
- 이번 VFX 통합(Smear 공격 이펙트 + Hit 피격 이펙트)은 **의도적으로 임시(throwaway-grade)** 구현이다. 품질 기준 = "공격/피격이 눈으로 구별되는 정도". 폴리싱·정확한 타이밍 싱크·변형 다양성(각 3종 변형 활용)·풀링 등은 하지 않는다.
- **VFX 구조 재설계가 별도 백로그로 예약됨** — 시점: 전투 연출 본격화(걸어나오기·스킬 등) 때. 그때 이 임시 구현은 대체 대상이며, 유지보수 노력을 들이지 말 것.
- 후속 작업자 주의: 이 임시 구현의 형태(유닛 BP에 이펙트 쿼드 부착 + SubUV 원샷)는 **아키텍처 선례가 아니다.** 재설계 시 풀링/나이아가라/전용 이펙트 매니저 등을 처음부터 검토할 것.

## 소재 (오너 구매·배치)
- `D:\unreal\Resource\vfx\Smear VFX 01\` — 공격용. 48×48 셀 가로 스트립. Horizontal 3종(240×48, **5프레임**)·Vertical 3종(288×48, **5프레임+투명1셀**)
- `D:\unreal\Resource\vfx\Hit Effect 01\` — 피격용. 336×48 스트립 3종(**6프레임+투명1셀**)
- 프레임 수는 알파 실측값(가이드 아님 — 실전노하우 §6 원칙). 임시 통합은 각 1종(변형 1번)만 사용.

## 임시 구현 형태 (요약)
기존 검증 파이프라인 재활용: 픽셀퍼펙트 임포트 → `M_Sprite_Flipbook_Lit` 자식 MI(GridY=1, 행 선택 없음) → 유닛 BP에 빌보드 이펙트 쿼드(기본 숨김) → PlayAttack 시 Smear / TakeHit 시 Hit을 TimeOffset frame0 재생 → 지속시간 후 숨김.

---

## 1단계 임포트 완료 (2026-07-07, art-pipeline)

### 알파 실측 (Pillow, 48×48 셀 기준)
| 소재 | 셀 수(그리드) | 실측 유효 프레임 | 비고 |
|---|---|---|---|
| Smear 01 Horizontal 1.png (240×48) | 5 | **5** (전 셀 opaque_px>0) | 지시서 FrameCount=5와 일치 |
| Hit Effect 01 1.png (336×48) | 7 | **6** (셀6 opaque_px=0, max_alpha=0 — 완전 투명) | 지시서 FrameCount=6과 일치 |

### 임포트 애셋
| 애셋 | 경로 | 원본 소스 |
|---|---|---|
| T_FX_Smear | `/Game/VFX/T_FX_Smear` | `D:\unreal\Resource\vfx\Smear VFX 01\Smear 01 Horizontal 1.png` |
| T_FX_Hit | `/Game/VFX/T_FX_Hit` | `D:\unreal\Resource\vfx\Hit Effect 01\Hit Effect 01 1.png` |

두 텍스처 모두 재조회 확인된 픽셀퍼펙트 세팅:
```
filter: TF_Nearest
mipGenSettings: TMGS_NoMipmaps
compressionSettings: TC_EditorIcon
```
(참조: 기존 `T_Party_A1`과 동일 세팅 패턴 확인 후 적용)

### MI 파라미터 (부모: `/Game/Materials/M_Sprite_Flipbook_Lit`)
| 파라미터 | MI_FX_Smear | MI_FX_Hit |
|---|---|---|
| SpriteTex | T_FX_Smear | T_FX_Hit |
| GridX | 5 | 7 |
| GridY | 1 | 1 |
| RowIndex | 0 | 0 |
| FrameCount | 5 | 6 |
| FPS | 15 | 15 |
| FlipX | 0 | 0 |
| EmissiveBoost | 3.0 | 3.0 |

경로: `/Game/VFX/MI_FX_Smear`, `/Game/VFX/MI_FX_Hit`. 전 파라미터 `get_scalar_parameter`/`get_texture_parameter` 재조회로 목표값 100% 일치 확인.

### 저장 상태
신규 4애셋(`T_FX_Smear`, `T_FX_Hit`, `MI_FX_Smear`, `MI_FX_Hit`) `save_assets` 후 `is_dirty=false` 확인. 기존 MI 16종·마스터 `M_Sprite_Flipbook_Lit`은 조회만(무변조). village 맵 2종(`map_village_day`/`map_village_night`) `is_dirty=false` 유지 확인(작업 전후 동일).

### 사용 도구
MCP `TextureTools.import_file` / `ObjectTools.set_properties`+`get_properties`(텍스처 픽셀퍼펙트 세팅) / `MaterialInstanceTools.create`+`set_scalar_parameter`+`set_texture_parameter`+`get_scalar_parameter`+`get_texture_parameter` / `AssetTools.is_dirty`+`save_assets`. 알파 실측은 Python 3.13(`C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe`) + Pillow, heredoc(`<<'EOF'`)로 Windows 경로 리터럴 보존.

---

## 2단계 배선 완료 (2026-07-07, gameplay-engineer)

### 구현 요약 — BP_BattleSpawnPoint 확장
- 컴포넌트 `EffectQuad`(StaticMeshComponent, `/Engine/BasicShapes/Plane.Plane`) 신규 추가. 변수 `SmearMID`·`HitMID`(MaterialInstanceDynamic ref) 신규 추가.
- BeginPlay 체인 끝(기존 마지막 노드 `SetCollisionEnabled`)에 이어붙임: `SetAbsolute(true,true,true)`(§7 함정②의 개별 3함수가 아니라 UE5.4+ 통합 함수 1개로 처리) → `SetWorldRotation(Pitch90,Yaw84,Roll0)`(TurnMarker와 동일 빌보드 각 재사용) → `SetWorldLocation(GetActorLocation + MakeVector(0,-80,20))` → `SetWorldScale3D(1.8,1.8,1)` → `SetVisibility(false)` → `SetCollisionEnabled(NoCollision)` → `CreateDynamicMaterialInstance(EffectQuad,0,MI_FX_Smear)`→`SetSmearMID` → `CreateDynamicMaterialInstance(EffectQuad,0,MI_FX_Hit)`→`SetHitMID`.
- `PlayAttack`: 기존 3연쇄(TimeOffset/FrameCount/RowIndex SetScalar) 직후, 기존 RetriggerableDelay(0.70) 앞에 `Utilities|FlowControl|시퀀스`(Sequence) 삽입. 분기A=기존 체인 그대로(무변경). 분기B(신규)=`SetMaterial(EffectQuad,0,SmearMID)`→`SmearMID.SetScalarParameterValue(TimeOffset,GetGameTimeInSeconds)`(declaring_class=MaterialInstanceDynamic 명시)→`EffectQuad.SetVisibility(true)`→`RetriggerableDelay(0.30)`→`SetVisibility(false)`.
- `TakeHit`: 기존 3연쇄 직후, 기존 RetriggerableDelay(0.45) 앞에 동일 패턴 Sequence 삽입. 분기B(신규)=`SetMaterial(EffectQuad,0,HitMID)`→`HitMID.SetScalarParameterValue(TimeOffset,now)`→`SetVisibility(true)`→`RetriggerableDelay(0.35)`→`SetVisibility(false)`.
- 큐 구조상 동일 유닛의 공격/피격 최소 간격(≥1턴≈1.1s)이 재생시간(0.30/0.35s)보다 훨씬 길어 EffectQuad 공유에 충돌 없음(E3 레이스 증명과 동일 논리).

### 함정 노트 추가
- `find_node_types`가 반환하는 type_id 문자열이 **컨텍스트에 따라 실제로 `create_node`에 먹히지 않는 경우**가 있었다(다른 블루프린트의 커스텀 이벤트를 호출하는 CallFunction 노드 `함수호출|PlayAttack` 검색 결과 — context_pins를 채워야만 검색되지만 그 문자열 자체로는 `create_node`가 "does not exist" 에러). 실제 해법은 **이미 그래프 안에 존재하는 동일 목적 노드를 `find_nodes`(title 검색)로 찾아 `get_node_infos`로 정확한 type_id를 역산**하는 것 — 예: BP_BattleManager EventGraph 안의 기존 PlayAttack 호출 노드에서 진짜 type_id가 `|PlayAttack`(파이프만, 카테고리 접두사 없음)임을 확인 후 그 문자열로 재시도 성공. **자기 자신의 블루프린트 함수**(예: `NotifyUnitClicked`)는 반대로 `함수호출|<함수명>` 문자열이 `create_node`에 그대로 먹혔다 — 다른 블루프린트의 커스텀 이벤트 호출과 자기 자신의 함수 호출은 `create_node` 컨텍스트 요구사항이 다른 것으로 추정(후속 조사 과제로 이월).
- `Utilities|Array|Get(사본)`(Array Get) 노드는 배열을 연결하기 전엔 와일드카드지만, `Array` 입력 핀에 타입이 있는 배열을 연결하는 즉시 `Output` 핀이 해당 원소 타입으로 자동 승격됨(§9 프로모터블 오퍼레이터와 유사한 재해석 패턴, 승격 방향이 입력→출력이라는 점만 다름).
- `find_node_types`에 `context_pins`로 기존 핀을 채워 검색하면 프로모터블 연산자(`유틸리티|연산자|추가` 등)가 실제 승격된 형태로 바로 검색됨 — §9에서 관찰된 "미연결 상태에서 엉뚱한 오버로드" 문제를 사전에 우회하는 실전 팁으로 추가 확정.

### 검증 — 임시 스캐폴드(BP_BattleManager BeginPlay) 2턴 자동 진행
`GetTurnQueue`(런타임 배열, §9 함정⑥ 회피 — 리터럴 오브젝트 레퍼런스 미사용)로 얻은 실제 유닛 참조만 사용: `BeginPlay→Delay(2.5)→NotifyAttackButtonClicked→Delay(0.3)→NotifyUnitClicked(TurnQueue[1])→Delay(1.5)→NotifyAttackButtonClicked→Delay(0.3)→NotifyUnitClicked(TurnQueue[0])`. StartPIE(warmup 8s) 후 `GetLogEntries`(`LogBlueprintUserMessages`)로 완전한 2턴 사이클 확인:
```
Registered:1~8 → State:Init → State:TurnStart → State:AwaitCommand
State:AwaitTarget:t=2.733 → UnitClicked:...B1:valid → BattleLog|turn=1|attacker=A1|target=B1|action=ATTACK1
State:Executing:t=3.067 → TakeHit:...B1 → TakeHitRevert:...B1
State:TurnEnd → State:TurnStart → State:AwaitCommand → State:AwaitTarget:t=4.733
UnitClicked:...A1:valid → BattleLog|turn=2|attacker=B1|target=A1|action=ATTACK1
State:Executing → TakeHit:...A1 → TakeHitRevert:...A1 → State:TurnEnd → State:TurnStart(3턴째 진입 확인) → State:AwaitCommand
```
로그에 정확히 2회의 PlayAttack 개시(BattleLog 라인)와 2회의 TakeHit/TakeHitRevert 쌍이 확인됨(이펙트 자체는 로그 미기록 — 방침대로 시각 판정은 오너 이월). 검증 후 스캐폴드 노드 12개(Delay×4, NotifyAttackButtonClicked×2, NotifyUnitClicked×2, GetTurnQueue×2, ArrayGet×2) 전량 `delete_node`로 제거, BeginPlay의 `then` 핀이 원래(unconnected) 상태로 복구됨을 `get_node_infos` 재조회로 확인. 양쪽 블루프린트 재컴파일(`warnings_as_errors=true`) 에러 0.

### 저장 상태(2단계)
`BP_BattleSpawnPoint`·`BP_BattleManager` 전체 `save_assets` 후 관련 에셋(`BP_BattleSpawnPoint`·`BP_BattleManager`·`MI_FX_Smear`·`MI_FX_Hit`·`T_FX_Smear`·`T_FX_Hit`) 및 레벨(`map_battle_octopath`) `is_dirty=false` 확인. village 맵 2종(`map_village_day`/`map_village_night`) `is_dirty=false` 유지(회귀 없음).

---

## 미표시 결함 수사 및 근본수정 (2026-07-07, gameplay-engineer — 오너 리포트 "이펙트가 전혀 안 보임")

### 근본 원인 확정
2단계에서 배선한 BeginPlay VFX 셋업 세그먼트(`SetAbsolute`→`SetWorldRotation`→`SetWorldLocation`→`SetWorldScale3D`→`SetVisibility`→`SetCollisionEnabled`→CDMI×2→`SetSmearMID`/`SetHitMID`)와 `PlayAttack`/`TakeHit`의 Sequence 분기B(`SetMaterial`→`SetScalarParameterValue`→`SetVisibility(true)`→`RetriggerableDelay`→`SetVisibility(false)`)는 **정적 그래프 추적(`get_connected_subgraph`) 결과 처음부터 전 구간 완벽하게 배선되어 있었다** — 방침 문서 기록과 100% 일치, 고아 세그먼트·끊긴 exec 없음.

실제 근본 원인은 **`EffectQuad`(StaticMeshComponent) 자체의 `staticMesh` 프로퍼티가 레벨에 배치된 8개 인스턴스 전부에서 `None`**이었던 것(`ObjectTools.get_properties`로 실측). 대조군 `TurnMarker`(같은 BeginPlay에서 세팅되는 StaticMeshComponent)는 `staticMesh=/Engine/BasicShapes/Plane.Plane`으로 정상. `BP_BattleSpawnPoint` 블루프린트 클래스 자체의 SCS 템플릿(`EffectQuad_GEN_VARIABLE`, CDO 경유 조회)은 `staticMesh` 정상 보유 — 즉 **클래스 정의는 무죄, 레벨 배치 인스턴스 8개만 결함**이었다(정확한 유입 경로는 미규명 — 컴포넌트를 클래스에 추가하는 시점과 8기 액터가 레벨에 이미 배치돼 있던 시점의 선후관계 문제로 추정, 후속 조사 과제로 이월). `reset_properties`는 이 프로퍼티에 효과 없었음 — `set_properties`로 `/Engine/BasicShapes/Plane.Plane` 명시 지정 후 재조회로 8기 전원 정상 확인.

렌더링할 지오메트리 자체가 없으면 그래프 로직이 아무리 정확해도(`SetVisibility(true)`, 유효한 MID 바인딩) 화면에 아무것도 그려지지 않는다 — 이것이 "이펙트가 전혀 안 보임" 증상의 유일한 원인이었다.

### 수정 내용
1. **StaticMesh 재할당(근본 수정)**: 8기 전 유닛(`BP_BattleSpawnPoint_C_0,2,3,4,5,6,7,9`)의 `EffectQuad.staticMesh`를 `set_properties`로 `/Engine/BasicShapes/Plane.Plane` 명시 지정, 전수 재조회 확인.
2. **에디터 인스턴스 청소**: 진단 과정에서 인스턴스에 직접 세팅했던 `relativeLocation`/`relativeRotation`/`relativeScale3D`/`overrideMaterials`/`bAbsolute*`를 SCS 원본 초기값(`(0,0,0)`/`(0,0,0)`/`(1,1,1)`/`[]`/`false,false,false`)으로 복원(BeginPlay가 실행되면 그래프가 이 값을 정확히 재계산하므로 게임 실행엔 영향 없음 — 순수하게 "저장된 에디터 값"의 일관성 확보 목적).
3. **오너 요청 겸사 조정 적용**: `MI_FX_Smear`/`MI_FX_Hit`의 `FPS` 15→**10**, `PlayAttack` 분기B `RetriggerableDelay` 0.30→**0.45**, `TakeHit` 분기B 0.35→**0.55**(원본 미변경), BeginPlay `SetWorldScale3D` 입력 `MakeVector` (1.8,1.8,1)→**(2.4,2.4,1)**. 전부 `set_pin_value`/`MaterialInstanceTools`로 세팅 후 `get_node_infos`/`get_scalar_parameter` 재조회 확인.
4. **진단 프린트 1개 유지(Director 지시)**: 신규 Custom Event `DiagVFXSetup`을 BeginPlay 체인 끝(`SetHitMID` 직후)에 배선. `IsValid(SmearMID)`/`IsValid(HitMID)` 각각 분기해 `게임|PrintText`(bPrintToScreen=false, bPrintToLog=true)로 `"VFXSetup:<라벨>:SmearMID=True/False(INVALID)"` 형태 로그(라벨은 `GetSprite→GetOwner→GetDisplayName` pure 체인, 4개 FormatText로 fan-out). PIE 재검증 결과 8기 전원 `SmearMID=True`·`HitMID=True` 정상 발화 확인.

### 시각 실증 — 결정적 판별 테스트(§4 방법론)
1. **독립 대조 테스트**: `SceneTools.add_to_scene_from_asset`로 EffectQuad와 무관한 신규 액터(`TEST_VFXDiag_Plane`, SM_Plane+MI_FX_Smear)를 씬에 직접 배치 → 스케일 5로 확대 후 카메라를 충분히 가깝게(대상 거리 ≈150~250cm) 두자 명확한 스머 궤적 렌더 확인. **머티리얼/텍스처 자체는 처음부터 완전 무죄**임을 재확인(`CaptureAssetImage`로도 이미 확인됨).
2. **EffectQuad 자체 시각 확인**: 8기 중 1기(`BP_BattleSpawnPoint_C_4`)의 EffectQuad를 에디터(비-PIE) 상태에서 방침값 그대로(`bAbsolute*=true`, `relativeRotation=(Pitch90,Yaw84,Roll0)`, `relativeScale3D=(2.4,2.4,1)`, `overrideMaterials=[MI_FX_Smear]`) 세팅 후 카메라를 대상 거리 ≈150~350cm로 근접시켜 캡처 → **명확한 스머 이펙트 렌더 확인**(캐릭터 머리 위로 흰 궤적). 원래 방침 회전값(Pitch90/Yaw84/Roll0)으로도, Sprite와 동일한 회전(0,0,90)으로도 둘 다 정상 렌더됨 — **회전값은 결함 원인이 아니었다**(§4 방법론 "만든 사람의 가설을 반증하라" — 애초에 회전이 원인이라는 가설 자체가 성립 안 함을 실험으로 확정).
3. **결론**: EffectQuad 컴포넌트·회전·배선 전부 무죄. 이전 캡처 실패들은 카메라-대상 거리가 과도(500cm 이상)해 스케일 2.4의 얇은 플레인이 화면상 거의 안 보이는 크기였기 때문(프레이밍 실수) — 이 자체도 §11에 노하우로 등재.

### PIE 실사용 경로(클릭 기반) 검증 — 로그·프로퍼티로 실증, 스크린샷은 인프라 제약으로 미확보
스캐폴드(`BeginPlay→Delay(2.5)→NotifyAttackButtonClicked→Delay(0.3)→NotifyUnitClicked(TurnQueue[N])`)로 실제 클릭 경로를 재현. `TurnQueue` 등록 순서가 Party/Enemy 교대(`_C_0,4,9,5,2,6,3,7` = A1,B1,A2,B2,A3,B3,A4,B4)임을 실측 확인 후 인덱스 1(B1, 상대팀)로 정확히 타겟팅 → `UnitClicked:valid`→`BattleLog`→`State:Executing`→`TakeHit`→`TakeHitRevert` 전체 1턴 사이클 정상 완료.

**PIE 인스턴스(`UEDPIE_0_...` 접두사, §9 함정⑥ 회피) 직접 조회로 실시간 실증**: 공격 개시 직후 즉시 조회 시 공격자(`_C_0`) EffectQuad `bVisible=true`, `overrideMaterials=[MID_MI_FX_Smear_0]`(런타임 생성된 다이나믹 MID가 정확히 바인딩됨) 확인. 타겟(`_C_4`)도 동일 패턴으로 `MID_MI_FX_Hit_0` 바인딩 확인. **재생 중인 순간의 스크린샷 확보는 실패** — `CaptureViewport`(4~5MB base64 이미지) 자체의 왕복 지연이 수십 초 단위로 커서, RetriggerableDelay를 진단용으로 90초까지 늘려도 "캡처 요청→응답 도착" 사이에 재생 창이 끝나버림(실측: `UnitClicked` 로그 시각과 다음 `get_properties` 조회 시각 사이 UTC 경과 46~110초, 게임 내 목표 재생시간 12~90초 전부 소진). §7 이슈 D(PIE 캡처 대상 불일치)와는 다른 신규 함정으로 §11 확정.

**검증 완결성 판단**: 그래프 배선 정적 검증 + 컴포넌트 프로퍼티 실측(정상값) + 독립 렌더 대조 테스트(무죄 확인) + PIE 런타임 프로퍼티 실측(`bVisible=true`, MID 바인딩 확인)의 4중 교차검증으로 **VFX가 실제 게임플레이에서 정상 트리거·렌더된다는 근거는 충분히 확보**됐다고 판단. 순간 포착 스크린샷은 verifier 재시도 과제로 이월.

### 사다리 로그 최종 상태
Director 지시 진단 사다리 (1)(2)(3) 중, 정적 전수 추적(1) 단계에서 이미 배선이 100% 정상임이 확정되어 (b)(c) 임시 프린트(`FXSmear:<라벨>`, `FXSmearVis:<라벨>`)는 심지 않음(불필요 — 배선 결함 가설 자체가 기각됨). (a) `VFXSetup` 로그만 최종 구현·유지, 8기 전원 `SmearMID=True`/`HitMID=True` 정상 발화 확인.

### 조정값 적용 확인 요약
| 항목 | 이전 | 이후 | 확인 방법 |
|---|---|---|---|
| MI_FX_Smear FPS | 15 | **10** | `get_scalar_parameter` |
| MI_FX_Hit FPS | 15 | **10** | `get_scalar_parameter` |
| PlayAttack 분기B RetrigDelay | 0.30 | **0.45** | `get_node_infos` |
| TakeHit 분기B RetrigDelay | 0.35 | **0.55**(원본 유지) | `get_node_infos` |
| EffectQuad SetWorldScale3D | (1.8,1.8,1) | **(2.4,2.4,1)** | `get_node_infos` |
| EffectQuad.staticMesh(8기) | None | **/Engine/BasicShapes/Plane.Plane** | `get_properties` 전수 |

### 컴파일·저장 최종 상태
`BP_BattleSpawnPoint`·`BP_BattleManager` 양쪽 `compile_blueprint(warnings_as_errors=true)` 에러 0. `save_assets([])` 전체 저장 후 `BP_BattleSpawnPoint`·`BP_BattleManager`·`MI_FX_Smear`·`MI_FX_Hit`·`map_battle_octopath` `is_dirty=false` 확인. village 관련 에셋(`map_village_day`·`map_village_night`·`map_battle_village`) `is_dirty=false` 유지(회귀 없음). 스캐폴드 노드(BP_BattleManager EventGraph, Delay×2/NotifyAttackButtonClicked/NotifyUnitClicked/GetTurnQueue/ArrayGet 총 6개) 전량 `delete_node` 제거, BeginPlay `then` 핀 원상(미연결) 복구 확인.

### 알려진 제약/TODO(이월)
- EffectQuad `staticMesh`가 애초에 왜 레벨 인스턴스에서만 유실됐는지(클래스 SCS는 정상) 근본 메커니즘 미규명 — 향후 유사 컴포넌트 추가 시 "레벨 인스턴스 StaticMesh 실측 확인"을 체크리스트에 추가 권장.
- 짧은(0.3~0.6초) VFX 재생 순간의 PIE 스크린샷 확보는 이번 MCP 조합(`CaptureViewport` 왕복 지연)으로는 재현성이 낮음 — verifier가 다른 수단(예: Duration을 훨씬 길게 임시 고정 + 폴링 간격 최소화, 혹은 Windows 데스크톱 자동화로 고속 연사 캡처, §6 "PIE 실클릭 검증" 패턴 참조) 사용 검토 필요.
