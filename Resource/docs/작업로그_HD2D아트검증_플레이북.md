---
type: log
project: projectTP
updated: 2026-06-28
tags: [playbook, hd2d, mcp, paper2d]
---

# 📒 작업 로그 & 플레이북 — HD-2D 아트 선검증 (S0)

> 목적: 이번 S0(아트 선검증) 전 과정을 **재현 가능하게** 기록. 제로베이스 재구축 시 그대로 따라하거나, 무엇을 다르게 할지 판단하는 근거.
> 허브: [[projectTP_허브]] / 결과 렌더: `docs/renders/HD2D_validation_hero.png`
> ⚠ 이번은 **검증용 1회성**. 실제 제작은 제로베이스 가능성 높음 → "재구축 권장" 섹션 참고.

---

## 0. 한 줄 결과
heroes99 32px 도트 → UE5.8 HD-2D 렌더 **성공**. 픽셀퍼펙트 + Lit 라이팅 + 캐스트 섀도우 + 디오라마 포스트프로세스로 옥토패스식 룩 확보. **이 에셋으로 진행 가능(GO).**

![[HD2D_validation_hero.png]]
![[HD2D_validation_wide.png]]

---

## 1. 환경 / 셋업 (재현 전제)

| 항목 | 값 |
|---|---|
| 엔진 | `D:\unreal\UE_5.8` (5.8.0, 커스텀/standalone 빌드) |
| 프로젝트 | `D:\unreal\projectTP\projectTP.uproject` (BP 전용, 컴파일 불필요) |
| 활성 플러그인 | `Paper2D`, `ModelContextProtocol`, `ToolsetRegistry`, `EditorToolset`, `PluginToolset`, `ConfigSettingsToolset` |
| MCP | UE5.8 공식. HTTP `http://127.0.0.1:8000/mcp`. Claude 설정 `D:\unreal\Resource\.mcp.json` (type:http) |
| 실행 | `D:\unreal\projectTP\_Launch_MCP.bat` (에디터 + `-ExecCmds="ModelContextProtocol.StartServer 8000"`) |
| 이미지 도구 | Python 3.13 + **Pillow 12.2** (오너 AppData) |

### MCP 노출 툴셋 (핵심)
`AssetTools, TextureTools, MaterialTools, MaterialInstanceTools, ObjectTools, SceneTools, ActorTools, StaticMeshTools, PrimitiveTools, BlueprintTools, ProgrammaticToolset(Python 오케스트레이션), EditorAppToolset(카메라·스크린샷·PIE), LogsToolset, PluginToolset, ConfigSettingsToolset`

> ⚠ **툴셋 플러그인을 .uproject에 켜야** MCP에 노출됨. 안 켜면 `AgentSkillToolset` 하나만 보임 → EditorToolset 등 추가 후 **에디터 재시작** 필수.

---

## 2. 에셋 구조 (heroes99) — 분석 결과

위치: `D:\unreal\Resource\_RawAssets\heroes99\`

- **레이어드 합성 시스템** (완성 시트 아님). 부위별 PNG를 겹쳐 한 캐릭터:
  - `skin/skin_c{1-6}.png` (피부톤)
  - `cloth/cloth{1-17}/cloth{N}_{bot,top}/cloth{N}_c{1-8}_{bot,top}.png` (의상 17, top/bot, 8색)
  - `hair/{m1-m14,f1-f9}/{name}_{bot,top}/{name}_c{1-10}_{bot,top}.png` (헤어 23, top/bot, ~10색)
  - `face/face_c{1-7}.png`
  - `weapon/weapon{1-5}/weapon{N}_{bot,top}/weapon{N}_{bot,top}.png` (무기 5, 색 없음)
- **bot/top = 뒤/앞 렌더 순서** (캐릭터 기준 뒤·앞 레이어)
- 부위 시트 크기: **800×680px RGBA**
- **그리드: 8칸 × 17행, 셀 100×40px** (= 800/8, 680/17)
- 행 순서: `IDLE1, IDLE2, RUN1, RUN2, JUMP(+FALL루프 33-35), ATTACK1, ATTACK2, ATTACK3, AIR ATK1, AIR ATK2, CASTING1(+루프65-67), CASTING2(+루프69-72), HURT, DYING, DASH(+루프83-86), BLOCK, ROLL`
- 프레임 번호 1~102+ 순차. idle1 = 좌상단 셀(0,0,100,40)
- 참고 파일: `frameguide_v2.png`(1600×1360 = 2배 가이드), `list_of_animation_full.gif`, 스타일 고르기용 `catalog_cloth.png`·`catalog_hair.png`

### 레이어 합성 순서 (뒤→앞)
`hair_bot → weapon_bot → cloth_bot → skin → face → cloth_top → hair_top → weapon_top`

---

## 3. 합성 (Pillow) — 재현

스크립트: `_RawAssets/heroes99/_composed/compose2.py`
- 각 레이어를 빈 RGBA 캔버스에 `Image.alpha_composite`로 순서대로 합성
- 이번 캐릭터: skin_c1 + cloth15_c1(top/bot) + hair m5_c7(top/bot) + weapon1(top/bot) + face_c1
- 산출: `hero_knight.png`(전체 800×680 시트), `hero_knight_idle1.png`(셀 0,0,100,40 크롭)
- idle1 셀 내 캐릭터 실제 bbox: (29,7,52,34) ≈ **23×27px**

---

## 4. UE 임포트 → 픽셀퍼펙트 (핵심)

1. `TextureTools.import_file(folder_path="/Game/Sprites", asset_name, source_file=절대경로)` — 디스크 PNG를 Texture2D로.
2. `ObjectTools.set_properties`로 **반드시** 아래 설정 (안 하면 도트 뭉개짐):
   - `Filter = TF_Nearest`
   - `MipGenSettings = TMGS_NoMipmaps`
   - `CompressionSettings = TC_EditorIcon` (UI RGBA 무압축, sRGB 유지)

생성됨: `/Game/Sprites/T_Hero_Knight_Idle1`, `T_Hero_Knight_Sheet`

---

## 5. 스프라이트 머티리얼 (`/Game/Materials/M_Sprite_Lit`)

`MaterialTools` + `ObjectTools`로 그래프 구성:
1. `create_material`
2. `ObjectTools.set_properties`: `BlendMode=BLEND_Masked`, `TwoSided=true` (Lit은 기본 → 씬 라이팅 받음 = HD-2D 통합 핵심)
3. `add_expression` (class `/Script/Engine.MaterialExpressionTextureSampleParameter2D`) → `Texture`=idle1, `ParameterName="SpriteTexture"`, `SamplerType=SAMPLERTYPE_Color`
4. `connect_to_output`: 출력 `RGB → MP_BaseColor`, `A → MP_OpacityMask`
5. `recompile`

> 파라미터 텍스처라 나중에 **MaterialInstance로 캐릭터별 텍스처 스왑** 가능.

---

## 6. 씬 조립 + ⚠ 최대 함정

### 함정: 기본 레벨이 오픈월드 템플릿
시작 레벨에 **Landscape 130+ 프록시 + SkyAtmosphere + VolumetricCloud + SkyLight + DirectionalLight + ExpHeightFog**가 이미 있음 → **밝은 하늘이 전부 washout**. 첫/둘째 시도가 떠 보이고 과노출된 원인.

### 해결: 하늘 제거 + 고공 격리
1. 템플릿 하늘/라이트/구름/안개 액터 **삭제** (`SceneTools.remove_from_scene`) → 배경이 검게 됨.
2. 디오라마를 **z=10000 고공**에 재배치 → 아래 랜드스케이프와 분리, 프레임 밖.
3. 스프라이트 평면: `/Engine/BasicShapes/Plane`을 `/Game/Meshes/SM_SpriteQuad`로 **복제**(엔진 에셋 보존) → `StaticMeshTools.set_material(slot "lambert1", M_Sprite_Lit)`. 평면을 **roll=90**으로 세워 -Y(카메라) 향함. scale (3.75,1.5,1)로 스프라이트 비율.
4. 바닥: 같은 식으로 `SM_Ground` 복제 + `M_Ground`(다크 Constant3Vector ~0.03 → BaseColor).
5. 라이트: `DirectionalLight`(키, pitch-38 yaw55) + `SkyLight`(필) — **인텐시티/색은 기본값** (컴포넌트 단위 튜닝 미적용, §8 한계).
6. `ExponentialHeightFog` 약하게.
7. `PostProcessVolume` `bUnbound=true`, Settings:
   - `AutoExposureMin/MaxBrightness = 1.0` (노출 고정 → washout 제거)
   - `BloomIntensity = 0.45`, `VignetteIntensity = 0.45`
   - `ColorSaturation = 1.15`, `ColorContrast = 1.08`

---

## 7. 카메라 & 스크린샷 워크플로

- `EditorAppToolset.CaptureViewport(captureTransform, annotations, bShowUI)` — ⚠ **세 인자 모두 필수**(스키마상 optional이지만 누락 시 에러). 주석 끄기: `gridSpacing=0, maxLabelDistance=0, classFilter=null, maxLabels=0`.
- 반환 base64 PNG가 커서 인라인 불가 → tool-results 파일로 저장됨 → **Python base64 디코드 → Read로 확인**.
- 히어로 샷 카메라: loc(0,-92,10069), rot(pitch-2, yaw90, roll0).
- 대량 호출 효율화: `ProgrammaticToolset.execute_tool_script`로 여러 툴을 한 스크립트에 묶음.

---

## 8. 시행착오 & 한계 (재구축 시 주의)

| # | 이슈 | 교훈 |
|---|---|---|
| 1 | .bat 한글 주석이 cmd(CP949)에서 깨짐(`됱?`) | 배치는 **영어 ASCII + CRLF**만. [[batch-files-english-only]] |
| 2 | .bat echo의 괄호 `(port 8000)`가 파싱사고(`'rt'`) | 배치 echo에 **괄호·특수문자 금지** |
| 3 | .uproject 더블클릭 시 -106(엔진 선택) | 커스텀 엔진 → `.bat`로 **UnrealEditor.exe 직접 실행** |
| 4 | 검은 런처 창 닫으면 에디터 종료 | 부모 프로세스 → **최소화만**, 닫지 말 것 |
| 5 | 툴셋 안 켜면 MCP에 기능 거의 없음 | EditorToolset 등 .uproject 추가 후 **재시작** |
| 6 | VC++ 14.50 미설치로 에디터 안 뜸 | `Engine/Extras/Redist/.../vc_redist.x64.exe` 설치 |
| 7 | 기본 레벨=오픈월드 → washout | **깨끗한 레벨**에서 시작 또는 하늘 제거+격리(§6) |
| 8 | 첫 폴리시 과노출(블룸 과다) | 노출 고정 + 블룸 ≤0.45 |
| 9 | 컴포넌트 단위 머티리얼/라이트 오버라이드 툴 못 찾음 | 메시 **에셋 복제 후 set_material**로 우회. 라이트 인텐시티/색 튜닝은 미해결 과제 |
| 10 | `ProgrammaticToolset`의 dict는 `.get(default)` 미지원 | `[]` 직접 접근. import 모듈 제한(json/math/re/time/datetime/copy) |
| 11 | CaptureViewport 인자 전부 필수 | 위 §7 |

---

## 9. 만들어진 산출물 (정리)

- 디스크: `_RawAssets/heroes99/_composed/{compose.py, compose2.py, hero_knight.png, hero_knight_idle1.png, hero_m1_cloth1_c1.png}`
- UE 에셋: `/Game/Sprites/T_Hero_Knight_*`, `/Game/Materials/M_Sprite_Lit·M_Ground`, `/Game/Meshes/SM_SpriteQuad·SM_Ground`
- 씬(z=10000): StageGround, HeroSprite, KeySun, FillSky, StageFog, PPV (※ 미저장 `/Temp/Untitled` 레벨 — 저장 안 하면 휘발)
- 렌더: `docs/renders/HD2D_validation_{hero,wide}.png`

---

## 10. 제로베이스 재구축 시 권장 (Keep / Change)

**그대로 가져갈 것 (Keep)**
- 픽셀퍼펙트 텍스처 3종 설정(Nearest/NoMip/TC_EditorIcon) — 표준화
- Lit + Masked + 양면 스프라이트 머티리얼, **파라미터화**해 MaterialInstance로 캐릭터별 스왑
- 레이어 합성 순서 & Pillow 자동화(파라미터화: skin/cloth/hair/face/weapon/color 인자)
- PPV 레시피(노출고정 + 약블룸 + 비네트 + 채도/대비)

**바꿀 것 (Change)**
- **깨끗한 전용 배틀 레벨**에서 시작(오픈월드 템플릿 X). 레벨을 에셋으로 저장.
- 정적 평면 대신 **Paper2D 플립북**(또는 PaperZD)으로 idle/공격 애니메이션. (MCP에 Paper2D 전용 툴 없음 → 플립북 생성은 별도 방안 필요: UE Python/수작업/추가 툴셋)
- **픽셀-퍼-유닛 스케일 규약**을 처음에 정의(이번엔 임의 scale 3.75/1.5). 카메라/스프라이트/무대 스케일 일관성.
- 라이트 인텐시티/색 **컴포넌트 튜닝** 방법 확보(ActorTools 심화 또는 Blueprint 라이트 액터).
- 동적 음영 원하면 **노멀맵 생성**(Laigter/Sprite DLight).
- 무대를 **서브레벨/블루프린트**로 모듈화.
- 합성 결과를 `/Game` 밖 원본 관리(`_RawAssets/_composed`)로 유지, 임포트 자동화 스크립트화.

---

## 11. 재현 체크리스트 (요약)
1. 에디터 실행(.bat) → MCP 8000 확인 → 툴셋 노출 확인
2. (필요시) heroes99 레이어 → Pillow 합성 → 단일 시트
3. 텍스처 임포트 + 픽셀퍼펙트 3설정
4. M_Sprite_Lit (Masked/양면/Lit, TexParam→BaseColor+OpacityMask)
5. **깨끗한 레벨** + 다크 바닥 + 세운 스프라이트 평면(roll90) + 키/필 라이트 + 안개 + PPV(노출고정/블룸0.45/비네트)
6. 카메라 세팅 → CaptureViewport → base64 디코드 → 확인 → 반복 튜닝
