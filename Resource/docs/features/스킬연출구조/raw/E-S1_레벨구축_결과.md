---
type: gate
project: projectTP
feature: 스킬연출구조
updated: 2026-08-11
status: S1 PASS — S2 착수
---

# E-S1 — 스파이크 레벨 구축 결과 (`map_battle_fxlab`)

> 상위: [[E_스파이크_plan]] · TC: [[E_TC]] §S1 · 선행: [[E-S0_노드프로브_결과]]

## 게이트 판정: **PASS**

| TC | 판정 | 실측 |
|---|---|---|
| **E-S1-01** 라이브 무손상 | ✅ | `map_battle_octopath.umap` **git 추적상 diff 0**. `3,848,264 B` · mtime **07-17 13:05** 그대로 |
| **E-S1-02** 공유 애셋 무변경 | ✅ | Content 저장소 변경 집합이 **정확히 `{map_battle_fxlab.umap}` 1개**. `M_Sprite_Flipbook_Lit`·`MI_FX_*`·`BP_BattleSpawnPoint`·`DT_Motions` 전부 불변 |
| **E-S1-03** PIE 안정성 | ✅ | **2분** 무입력(요구 30초의 4배), `Accessed None` **0건** |
| **E-S1-04** 액터 수 | ✅ | Manager/AttackButton/CamToggle **0** · SpawnPoint **8** · AttackPoint **2** |
| **E-S1-05** 8기 렌더 | ✅ | 8기 전원 `bVisible=true` · `bHiddenInGame=false` · `SM_SpriteQuad` 유효 · 고유 `OverrideMaterials`(`MI_Party_A1~A4`·`MI_Enemy_B1~B4_flip`) |

> ★**SHA256 대신 git으로 판정했다.** scene-builder 세션에 해시 도구가 없어 verifier 이관을 요청했으나, **git 추적 diff가 더 강한 증거**다 — 내용 해시가 같아야 diff 0이 나온다.

## 삭제한 액터 3종 (되돌릴 수 있게 트랜스폼 기록)

| 액터 | 라벨 | 위치 | 회전 | 스케일 |
|---|---|---|---|---|
| `BP_BattleManager_C_0` | BattleManager | (0, -7100, 630) | (0,0,0) | (1,1,1) |
| `BP_AttackButton_C_0` | UI_AttackButton | (-38, -7300, 420) | (90, 84, 0) | (4,2,1) |
| `BP_CamToggleButton_C_0` | UI_CamToggle | (-650, -7300, 420) | (90, 84, 0) | (3,1.5,1) |

보호 대상 무손상: `environment/*` **13기** · `BattleStage/Camera` 2기(`BattleCamera`=CameraActor_0, `ActionCam_Dynamic`=CameraActor_3).

## ★DoF가 왜 꺼져 있었나 — 원인 규명

**값 7개는 이미 들어 있었고 `bOverride_*` 플래그만 false**였다. [[S3_룩패스]]의 *"적용 후 원복"*이 **값이 아니라 override만 껐던 것**이다.

그리고 ★**문서 B안 목록에 없던 `depthOfFieldEnabled`(+ `bOverride_DepthOfFieldEnabled`)가 없으면 DoF 자체가 렌더에 반영되지 않는다** — 이번에 추가 적용했다.

| 문서 표기 | 실제 UE 5.8 프로퍼티 | 값 |
|---|---|---|
| FocalDistance | `depthOfFieldFocalDistance` | 1100 |
| FocalRegion | `depthOfFieldFocalRegion` | 250 |
| NearTransitionRegion | `depthOfFieldNearTransitionRegion` | 300 |
| FarTransitionRegion | `depthOfFieldFarTransitionRegion` | 400 |
| Scale | `depthOfFieldScale` | 1.0 |
| NearBlurSize / FarBlurSize | `depthOfFieldNearBlurSize` / `...FarBlurSize` | 3.0 / 3.0 |
| **(문서 누락)** | **`depthOfFieldEnabled`** | **true** ← 없으면 위 7개가 무효 |

대상: `PostProcessVolume_Unbound`(`bUnbound=true` · `bEnabled=true` · `BlendWeight=1` — 전역 적용).
명명 규칙: 값은 camelCase(`depthOfField*`), override 플래그는 `bOverride_DepthOfField*`(PascalCase).

## ★8기 유닛 — 정적 렌더 PASS / 런타임 초기화 스킵 (예정된 결과)

런타임 실측(대표 2기):
```
Hp=0  MaxHp=0  Atk=0  Def=0  Spd=0
ManagerRef=None  SpriteMId=None  HomeLocation=(0,0,0)
CharName="이름5"/"이름7"(placeholder)
```

→ 매니저 삭제로 초기화가 **완전히 스킵**됐다. [[E0_에이전트피드백_Director판정]]이 예측한 **가짜 GREEN**(`IsValid(ManagerRef)` Not Valid 분기 미배선)이 실측으로 재확인됐다 — **에러는 안 뜨고 초기화만 사라진다.**

**판정: (b) 배경 더미로 그대로 사용.** 조치 불필요.
- 정적 렌더가 되므로 **밀도 비교(1순위 목적)에 충분**하다
- 실제 연출은 S3의 **대역 액터**(`BP_FxLabDummy`)가 담당한다
- ⚠ `SpriteMId=None`이라 **플립북이 안 돈다(정지 프레임)** → *"8fps 캐릭터 vs 20fps VFX"* 시간 밀도 비교는 **여기서 불가**. 이미 유효범위에 기록된 항목이다

## 이월

- **`FxLab/` 아웃라이너 폴더** — UE 폴더는 액터가 최소 1개 있어야 유지되고 `SceneTools`에 빈 폴더 생성 툴이 없다. **S2에서 `BP_FxLabQuad` 배치 시 함께 생성**
- 라이팅·PP는 DoF 외 미적용(hd2d 이어받기 가능)
