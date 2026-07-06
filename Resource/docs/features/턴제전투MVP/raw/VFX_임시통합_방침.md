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
