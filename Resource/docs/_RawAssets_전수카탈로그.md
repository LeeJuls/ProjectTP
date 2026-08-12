---
type: reference
project: projectTP
updated: 2026-08-12
status: WIP
---

# 🗂 `_RawAssets` 전수 카탈로그

> `D:\unreal\Resource\_RawAssets\` 5개 폴더(heroes99·vfx·tilesets·ui-packs·_mockups) 전수 조사. 오너 지시: "기왕 탐색하는 거 확실하게, 기록은 바로바로."
> 조사 방식: **파일시스템 조회 + Pillow 실측만**(MCP·언리얼 무접촉, uasset 무접촉·수정 0건). 유료 에셋 원본 이미지는 문서에 복사하지 않음 — 경로·수치만 기록.
> heroes99는 [[heroes99_에셋_전수탐색]]에서 이미 전수 조사됨 — **본 문서는 그 문서가 "미해독"으로 남긴 것만 재확인**하고 나머지는 링크로 대체(중복 조사 금지 준수).
> 관련: [[projectTP_허브]] · [[에셋_후보_카탈로그]] · [[D4.5a_VFX재고_실측]] · [[E_TC]] · [[features/HD2D배경/raw/2D배경_기각_교훈_2026-08-10\|2D배경_기각_교훈]] · [[features/HD2D배경/raw/목업_유효범위_판정\|목업_유효범위_판정]]
#projectTP/에셋 #projectTP/art-pipeline

---

## 0. 오너 질문에 대한 답 (한 문장)

**밀도 6.48에 가장 가까운 미사용 후보를 하나 찾았다.** `vfx/Holy VFX 01-02/Holy VFX 01/`(32px 네이티브 셀)이 현재 `EffectQuad` 스케일(2.4) 기준 **7.50 uu/텍셀(1.16×)**로, legacy(5.00, 0.77×)·신규 3종(3.75, 0.58×)보다 1.0×에 훨씬 가깝다(§4). 완전 일치는 아니지만(0.16 vs 0.23·0.42 오차), **밀도 문제를 더 적게 남기는 미사용 팩이 실재한다** — 자세한 근거·한계는 §4·§3-2 참조.

그 외 핵심 소득: **`heroes99_에셋_전수탐색.md`의 legacy VFX 출처 서술 정정**(§3-2), **`_mockups`의 8개 파일이 실제로 `Content/Sprites/Tileset/`에 임포트돼 있음을 확인**(단 전투배경 용도는 오너가 이미 기각, §5), **UI 팩 3종 내용물 최초 확인**(§6).

---

## 1. 총괄 표

| 폴더 | 용량 | 파일 수 | 용도 | 사용 여부 |
|---|---|---|---|---|
| `heroes99/` | 22M | 802(png791·gif7·py2·aseprite2) | 캐릭터 파츠(스킨/헤어/의상/무기) + 합성 스크립트 | **부분 사용** — 상세 [[heroes99_에셋_전수탐색]] |
| `vfx/` | 29M | 244(png226·gif16·aseprite2) | 이펙트 스프라이트 4개 하위팩 | **2/4 팩만 사용**, 그 안에서도 극히 일부(§3) |
| `tilesets/` | 70M | 193(png184·tset8·txt1) | 배경 타일셋 2세대(구/신) × 2브랜드 | **임포트했으나 전투배경 기각**(오너, 2026-08-10). 로비 등 타용도 재검토 가능(§5) |
| `ui-packs/` | 21M | 6(unitypackage3·zip1·rar1·png1) | UI HUD·아이콘 킷 | **미사용**(포맷 변환 필요, 최초 내용 확인 완료 — §6) |
| `_mockups/` | 2.4M | 22(전부 png) | HD2D배경 기능의 오프라인 목업 산출물 | 목업 트랙 **종결**. 단 `parts/` 8개는 실제 `Content/`에 임포트되어 보존 중(§5) |

---

## 2. heroes99 — 1차 조사가 "미해독"으로 남긴 것만 재확인

전체 상세는 [[heroes99_에셋_전수탐색]] 참조(중복 조사 안 함). 이번에 새로 확인한 것:

### 2-1. `clothcolor.aseprite` / `haircolor.aseprite` — 여전히 미해독

Pillow `Image.open()`이 `cannot identify image file`로 실패(포맷 미지원 확인). 시스템 Python 3.13.13 환경에 aseprite/psd 전용 파서 라이브러리가 설치돼 있지 않음(`pip list`에 관련 패키지 0건). → **결론 불변**: Aseprite 앱(또는 CLI) 없이는 열 수 없다. 신규 색상 변형이 필요해지면 그때 Aseprite 확보가 선행 조건.

### 2-2. `_composed/` 폴더 내용물

| 파일/폴더 | 정체 | 상태 |
|---|---|---|
| `party/T_Party_A1~B4.png`(8개, 800×680) | **실제 라이브 캐릭터 8기 텍스처** | 사용 중 |
| `compose.py` / `compose2.py` | 합성 스크립트(레이어 순서 hair_bot→weapon_bot→cloth_bot→skin→face→cloth_top→hair_top→weapon_top) | 재현용 자산, 보존 |
| `hero_knight.png`(800×680) · `hero_knight_idle1.png`(100×40) · `hero_m1_cloth1_c1.png`(800×680) | 합성 스크립트 초기 개발 산출물(허브 문서 §"합성 캐릭터" 예시로 언급된 그 파일) | **개발 스크래치, 미사용**(party/로 대체됨) |
| `A0_spike/`(5개) | 파이프라인 검증 스파이크(5레이어 조합 8배 프리뷰 등) | **미사용**, 검증 기록으로만 가치 |
| `test_combo/`(9개, test1~3) | 파츠 조합 테스트(교차성별 포함) | **미사용**, party/ 확정 전 실험 |

→ 전부 party/ 8종으로 수렴하기 전의 개발 과정 산출물. 삭제 대상은 아니나(재현 가능성 보존), 라이브 경로는 `party/`뿐이다.

---

## 3. `vfx/` — ★1순위 (전수 조사)

### 3-1. 구조 · 라이선스

| 하위팩 | 파일 수 | 용량 | 원본 흔적 | 문서·라이선스 |
|---|---|---|---|---|
| `Free/`(Part1~15) | 196(png180+gif16) | 29M | `Free Preview All.gif` 벤더 카탈로그 | **없음** |
| `Hit Effect 01/` | 4 | 24K | `Hit Effect 1.aseprite` 원본 포함 | **없음** |
| `Holy VFX 01-02/` | 37 | 48K | Impact/Initial/Repeatable 3단 + `Separated Frames/` | **없음** |
| `Smear VFX 01/` | 7 | 18K | `Smear VFX 01.aseprite` 원본 포함 | **없음** |

`vfx/` 전체에 readme·license·txt·md·pdf **0개**(전수 검색 확인). [[에셋_후보_카탈로그]]가 이미 지적한 "라이선스 파일 없음, 구매처 확인 필요"가 재확인됨 — **Steam 출시 전 필수 확인 항목**.

### 3-2. ★출처 정정 — legacy `T_FX_Smear`/`T_FX_Hit`는 `Free/`가 아니다

[[heroes99_에셋_전수탐색]] §4-1이 "라이브 `T_FX_Smear`/`T_FX_Hit`는 `Free/Part1·13·14` 소스"라 적었는데, 이번 Pillow 실측 결과 **이 서술은 틀렸다.**

| 텍스처 | 실제 소스(더 이른 시점의 1차 자료로 확인) | 실측 |
|---|---|---|
| `T_FX_Smear` | `Smear VFX 01/Smear 01 Horizontal 1.png` | **240×48px, 48px 셀 × 5프레임** |
| `T_FX_Hit` | `Hit Effect 01/Hit Effect 01 1.png` | **336×48px, 48px 셀 × 7그리드(6프레임 유효, 1셀 완전투명)** |

근거: `docs/features/턴제전투MVP/raw/VFX_임시통합_방침.md`(더 이른 시점 작성)가 이미 이 경로를 명시(`T_FX_Smear ← Smear VFX 01\Smear 01 Horizontal 1.png`, `T_FX_Hit ← Hit Effect 01\Hit Effect 01 1.png`)하고 있고, `data/drafts/vfx_draft.csv`의 `63000100`(GridX=5,GridY=1,FrameCount=5)·`63000200`(GridX=7,GridY=1,FrameCount=6) 값이 이 실측과 정확히 일치한다. `Free/`의 63000300~500(신규 3종)은 `Part 1/03.png`·`Part 13/612.png`·`Part 14/652.png`가 맞다(이건 원래 문서 서술도 맞았음) — **혼동된 것은 legacy 2개뿐**이었다. `heroes99_에셋_전수탐색.md`에 정정 필요.

### 3-3. `Free/` 180장 — 이미 전수 실측됨, 중복 안 함

[[D4.5a_VFX재고_실측]](`data/drafts/vfx_inventory_raw.csv`, 180행)가 이미 그리드(GridX 5~23 가변·GridY=9 고정·64px 셀)·색상행 일관성·이상치를 전수 실측했다. 본 문서에서 재측정하지 않음.

### 3-4. `Hit Effect 01` / `Smear VFX 01` / `Holy VFX 01-02` 실측 (신규)

| 파일 | 크기 | 네이티브 셀 | 프레임 수 | 비고 |
|---|---|---|---|---|
| `Hit Effect 01 1/2/3.png` | 336×48 | 48px | 7그리드/6유효(1셀 alpha=0) | 3종 전부 동일 크기(색 변형 추정) |
| `Smear 01 Horizontal 1/2/3.png` | 240×48 | 48px | 5 | 가로형 |
| `Smear 01 Vertical 01/02/03.png` | 288×48 | 48px | 6그리드(alpha bbox상 5유효+1투명 추정) | 세로형, Horizontal과 셀폭 다름(48 고정, 열수만 6) |
| `Holy VFX 01 Impact.png` | 224×32 | 32px | 7 | `Separated Frames/Impact1~7` 존재와 일치 |
| `Holy VFX 01 Initial.png` | 64×32 | 32px | 2 | `Initial1~2`와 일치 |
| `Holy VFX 01 Repeatable.png` | 256×32 | 32px | 8 | `Repeatable1~8`과 일치 |
| `Holy VFX 02.png` | 768×48 | **48px** | 16 | `Holy VFX 01`과 셀 크기가 다름(01=32px, 02=48px) |

→ **`Holy VFX 01`만 32px 네이티브 셀**이고 나머지(`Hit Effect 01`·`Smear VFX 01`·`Holy VFX 02`)는 legacy와 동일한 48px 셀이다. 이 차이가 §4 밀도 대조의 핵심.

### 3-5. 사용 현황

| 항목 | 상태 |
|---|---|
| `T_FX_Smear`(← `Smear VFX 01`) | **라이브 사용** |
| `T_FX_Hit`(← `Hit Effect 01`) | **라이브 사용** |
| `T_FX_CastAtk`/`CastSupport`/`ProjectileArcane`(← `Free/`) | **D6 임포트 대기**(설계 완료, [[E_TC]] S2' 단계) |
| `Free/` 나머지 177장 | **미사용** |
| `Holy VFX 01-02/`(37장 전부) | **미사용** |
| `Smear VFX 01`의 Vertical 3종, `Hit Effect 01`의 2/3번(색변형 추정) | **미사용**(1번만 씀) |

---

## 4. ★밀도 대조표 — 캐릭터 6.48 uu/텍셀 기준

### 4-1. 산출 방법 (기존 실측 역산으로 검증)

`EffectQuad`는 `/Engine/BasicShapes/Plane.Plane`(네이티브 100×100uu)에 `SetWorldScale3D`를 걸어 쓴다(`VFX_임시통합_방침.md` 실측: 현재 스케일 **2.4**). 따라서 **월드 쿼드 크기 = 100 × 2.4 = 240uu**(스케일과 무관하게 고정된 사각 평면), **uu/텍셀 = 240 ÷ 네이티브 셀px**. 이 식은 기존 실측 2점과 정확히 일치해 검증됨: legacy 48px → 240/48=**5.00**(기존 문서값과 일치) · 신규 64px → 240/64=**3.75**(기존 문서값과 일치). 캐릭터 쪽 **6.48**은 별도 컨벤션(`SM_SpriteQuad` 스케일 자체가 uu/텍셀, [[언리얼_MCP_실전노하우]] 실측)이라 VFX 쪽과 산식은 다르지만, "같은 스케일 값에서 캐릭터와 같은 밀도로 보이려면 몇 배 키워야 하는가"라는 목적은 동일하게 비교 가능하다.

### 4-2. 대조표

| 소스 | 네이티브 셀(px) | 현재 스케일(2.4) 기준 uu/텍셀 | 배율(÷6.48) | 6.48 도달 필요 스케일 |
|---|---|---|---|---|
| 캐릭터(heroes99, 기준) | 100×40 | **6.48**(정의) | 1.00× | 2.4(기준 자체) |
| legacy `Hit Effect 01`/`Smear VFX 01`/`Holy VFX 02` | 48 | 5.00 | **0.77×** | 3.11(기존 실측 "1.30×" = 3.11/2.4) |
| 신규 3종(`Free/`, GridX 무관 전부 64px) | 64 | 3.75 | **0.58×** | 4.15(기존 실측과 일치) |
| **`Holy VFX 01`(미사용)** | **32** | **7.50** | **1.16×** | **2.07(★현재 2.4보다 오히려 작게)** |

### 4-3. 판정

**`Holy VFX 01`이 이번 조사에서 발견한, 1.0×에 가장 가까운 팩이다.** 절대 오차로 비교하면 legacy 0.23 · 신규 0.42 · Holy VFX01 **0.16**로 가장 작다. 완전 일치(37px 셀이어야 정확히 6.48)는 아니고, **legacy·신규와 반대 방향으로 벗어나 있다**(legacy·신규는 "작게 보임" 0.58~0.77×, Holy VFX01은 "크게 보임" 1.16×) — 이 자체가 [[E_TC]] E-H9("전역 스케일 1값으로 legacy·신규를 동시에 못 맞춘다")를 한 번 더 실증한다: 3팩이 전부 다른 방향/크기로 어긋나 있어 **팩별(또는 vfxId별) 스케일 오버라이드가 필수**라는 기존 결론이 강화된다.

⚠ **한계**: 이 계산은 "같은 `EffectQuad` 컨벤션(고정 240uu 쿼드)을 그대로 쓴다면"이라는 가정 위에 있다. Holy VFX 01은 아직 임포트도 MI 배선도 안 된 상태라 **실측이 아니라 기존 실측치의 외삽**이다 — 실제 채택 시 S2'급 임포트 검증(Filter/Mip/Compression 5종 legacy 대조, [[E_TC]] E-S2T-02)이 선행돼야 한다.

### 4-4. `tilesets`·`ui-packs` 밀도

- **tilesets**: 이미 [[에셋_후보_카탈로그]]·[[features/HD2D배경/raw/목업_유효범위_판정\|목업_유효범위_판정]]에서 전수 계산 완료(캐릭터 27~29텍셀 vs 타일 48텍셀, 텍셀 파리티 불가 판정 CONFIRMED) — 재계산 안 함. 본 문서에서 재확인한 것은 **모든 Winlu 계열 시트가 48px 그리드로 일관**된다는 것뿐(§5-1).
- **ui-packs**: HUD/아이콘은 스크린 스페이스(2D 캔버스)로 쓰일 예정이라 uu/텍셀 개념이 적용되지 않는다(월드 스프라이트가 아님). 대신 §6에 네이티브 해상도만 기록.

---

## 5. `tilesets/` — 구조 재확인 + 신규 발견(`_mockups` 연결고리)

### 5-1. 구조 · 세대

| 폴더 | 파일 수 | 용량 | 생성 시점(mtime) | 정체 |
|---|---|---|---|---|
| `A2 terrain old version/` | 3 | 1.4M | **2023-08** | 구버전 잔재, `Fantasy Exterior - Other Engines`로 대체됨 |
| `Winlu exterior Old version/` | 45 | 10M | **2023-08** | 구버전 잔재, `Winlu exterior remaster`로 대체됨 |
| `Fantasy Exterior - Other Engines/` | 73 | 42M | 2026-07 | A1~A5 풀세트 + GreenEdition/RedEdition 변형 |
| `Winlu exterior remaster/` | 72 | 17M | 2026-07 | 최신판. `A4 walls warning!.txt` 포함(RPG Maker 벽 충돌판정 안내 — **라이선스 아님**, 버그성 안내문) |

→ **구버전 2폴더(48개 파일, 11.4M)는 완전히 대체된 잔재**다. 새로 작업 시작할 때 신버전(`Fantasy Exterior - Other Engines` / `Winlu exterior remaster`)만 보면 된다. 캐탈로그가 언급한 `8D_Characters.zip`(8방향 캐릭터, 21MB)은 **로컬에 실재하지 않음** — 구매 목록에는 있었을 가능성이나 미다운로드/미보관 상태(미확인, 재확인 필요).

Pillow 실측: `A2 - Terrain And Misc.png`(2496×1920) · `A4 - Walls.png`(1104×1488) · `Fantasy_Outside_B.png`(768×768) · `!$Big_Trees.png`(576×1152) — 전부 **48px 배수**(2496/48=52, 1920/48=40 등). 신·구버전 동일 그리드 규약 확인.

### 5-2. 사용 현황 — 전투배경 기각, 로비 등은 재검토 가능

[[features/HD2D배경/raw/2D배경_기각_교훈_2026-08-10\|2D배경_기각_교훈]] 재확인: 오너가 엔진 실배치 후 **"엄청 안 어울린다. 레벨은 3D로"** 판정, **전투 배경은 재론하지 않음**으로 확정. `Content/Sprites/Tileset/` 8종·`Content/Materials/Tileset/` MI 6+`M_GroundTiled`는 삭제하지 않고 보존(실증 기록 + `M_GroundTiled`는 3D 무대에도 재사용 가능한 범용 머티리얼).

### 5-3. ★신규 확인 — `_mockups/parts/` 8개 = `Content/Sprites/Tileset/` 8종의 원본

이번 조사에서 파일명·픽셀 크기를 대조해 **정확히 일치**함을 확인(스모킹건):

| `_mockups/parts/` | 실측 크기 | ↔ | `Content/Sprites/Tileset/` |
|---|---|---|---|
| `tile_ground_dirt_48.png` | 48×48 | → | `T_Tile_GroundDirt.uasset` |
| `tile_ground_grass_48.png` | 48×48 | → | `T_Tile_GroundGrass.uasset` |
| `tile_wall_merlon_48.png` | 48×48 | → | `T_Tile_WallMerlon.uasset` |
| `tile_wall_stone_144.png` | 144×144 | → | `T_Tile_WallStone.uasset` |
| `prop_tower_stone.png` | 96×330 | → | `T_Prop_TowerStone.uasset` |
| `prop_tree_bush.png` | 167×243 | → | `T_Prop_TreeBush.uasset` |
| `prop_tree_pine.png` | 131×214 | → | `T_Prop_TreePine.uasset` |
| `prop_tree_wide.png` | 174×240 | → | `T_Prop_TreeWide.uasset` |

mtime도 인과관계와 일치(`_mockups/parts/` 2026-07-31 생성 → `Content/Sprites/Tileset/*.uasset` 2026-08-10 임포트). 즉 **오프라인 목업용으로 오려낸 부품(`docs/scripts/mockup/mockup_extract_parts.py`, 원본은 `Fantasy Exterior - Other Engines/`)이 그대로 실제 임포트 텍스처가 됐다** — 목업과 실제 자산 사이에 재작업 없이 파이프라인이 이어졌다는 뜻. 다만 이 텍스처들 자체가 가리키는 최종 용도(전투배경)는 기각됐으므로, **"쓰는 것"이 아니라 "임포트는 됐으나 채택 안 된 보존 자산"**으로 분류해야 정확하다.

---

## 6. `ui-packs/` — 최초 내용 확인 (미조사 → 조사 완료)

[[에셋_후보_카탈로그]] §UI팩3종이 "포맷 변환 필요, 내용 미조사"로 남겨둔 것을 `.unitypackage`(=tar.gz, Python `tarfile`로 무해제 열람 가능)로 직접 열어 확인했다. **UE 임포트·해제·수정 없음**(tarfile 스트림 조회만, 원본 무변경).

### 6-1. `pixelhudui_free_v10.unitypackage`(8.35MB) — "Pixel UI HUD: Fantasy RPG Kit"

- **내용**(README 전문 확인): 스프라이트 82장 + 프리팹 2 + 폰트 3종(Noto Serif R/M/B, SDF 포함) + 애니메이션 1 + 데모씬 1.
- **구성**: 상태바(2스타일×9색)·아이콘 18종(소모품/도구/재료/시스템)·패널/슬롯/버튼/프레임/인디케이터.
- **육안 확인**(`Icon_Consumable_Apple.png` 128×128 추출 확인): **진짜 픽셀아트**(도트 음영·디더링 있음, 업스케일 벡터 아님) — 프로젝트 아트 문법과 결이 맞는다.
- **라이선스**: 자체 텍스트 라이선스는 없음("Thank you for your purchase"로 보아 구매/유료 배포물). 내장 **Noto Serif 폰트만 SIL Open Font License 1.1** 전문 확인(`Font/LICENSE_NotoSerif.txt`) — 상업 사용 가능, 폰트 자체 판매만 금지.
- **판정**: UI 정식 제작 단계에서 **1순위 후보**(픽셀아트 결 일치 + 완성된 상태바/아이콘 세트). 단 unitypackage 추출 작업(GUID 폴더 → 원본 파일명 복원, 이번 조사로 pathname 매핑은 이미 확보됨) 필요.

### 6-2. `gui_fantasy_kit.unitypackage`(7.90MB) — "GUI_Fantasy_Kit"

- **내용**: 37개 PNG(HP/마나/스태미나 바 3종+필, 인벤토리 슬롯 3사이즈, 팝업창 2종, 아이콘 8종 등) + Unity 데모 씬.
- **육안 확인**(`sword-icon.png` 142×184, `hp-bar.png` 627×103 추출 확인): **페인팅풍 고해상도 아이콘**(금속 하이라이트·그라데이션 셰이딩, 안티에일리어싱 강함) — **픽셀아트가 아니다**. 돌 재질 HP바도 조각·마블링 텍스처가 있는 "AAA 판타지 UI" 톤.
- **라이선스**: readme·license 파일 0개(41개 pathname 전수 확인).
- **판정**: **스타일 불일치** — 프로젝트가 픽셀아트 캐릭터·이펙트로 일관하는 방향과 어긋난다. 급할 때 임시 대체재 정도로만 고려, 정식 채택 비권장.

### 6-3. `2d_icons_pictoiconpack01.unitypackage`(4.09MB) — "Layer Lab 2D Icons - PictoIconPack01"

- **내용**: 아이콘 **221종 × 4해상도(64/128/256/512px) = 884개 PNG** + 데모씬 + 스크립트 2개(`PanelControl.cs`/`PanelView.cs`).
- **육안 확인**(`Icon_PictoIcon_Sword` 128×128 추출·알파채널 분석): **흰색(255,255,255) 단색 실루엣 벡터 아이콘**(런타임 틴트 전제 디자인). Bluetooth·Calendar·Bookmark 등 범용 앱 아이콘이 다수 섞여 있고 게임 특화(Sword·Shield·Battle·Bomb 등)는 일부.
- **라이선스**: readme·license 파일 0개.
- **판정**: 시스템/범용 UI 아이콘(설정·알림 등) 용도로는 즉시 쓸 수 있음(단색이라 프로젝트 톤 컬러 `#E8C384`로 틴트하면 스타일 충돌이 적다). 게임 특화 아이콘(스킬 아이콘 등)은 별도 소스 필요.

### 6-4. `Pixel UI pack 3.zip`/`.rar`/`All.png`(합계 0.19MB)

- `.zip` 내부: `00.png`~`07.png` + `All.png`(=폴더 최상위에 이미 풀려 있는 것과 동일). `All.png` 실측 **1312×304px**, 육안 확인 결과 **깔끔한 플랫/벡터 스타일**(체력바·보석·랭크뱃지·원형 쿨다운 게이지·별점) — 도트 노이즈 없음, "Pixel UI"라는 이름과 달리 픽셀아트는 아니다.
- `.rar`는 **미해제**(시스템에 unrar 없음) — 파일명·크기가 `.zip`과 별도이나 이름상 동일 팩의 중복 아카이브로 추정(미검증).
- **판정**: 미사용. 스타일은 gui_fantasy_kit보다 프로젝트 톤에 가깝지만(플랫한 UI 크롬은 흔히 픽셀 게임에도 허용) 최종 판단은 UI 정식 제작 단계에서.

### 6-5. 종합

| 팩 | 픽셀아트 여부 | 라이선스 | 프로젝트 적합도 |
|---|---|---|---|
| `pixelhudui_free_v10` | ✅ 진짜 픽셀아트 | README만(자체 조항 없음) + 폰트 SIL OFL | **높음** — 1순위 |
| `gui_fantasy_kit` | ❌ 페인팅풍 | 없음 | 낮음 |
| `2d_icons_pictoiconpack01` | △ 벡터 실루엣(틴트 전제) | 없음 | 중간(시스템 아이콘 한정) |
| `Pixel UI pack 3` | △ 플랫 벡터 | 없음 | 중간 |

---

## 7. ★쓸 수 있는데 안 쓰는 것 — 상위 5개 (+참고)

| #    | 항목                                                             | 왜 값진가                                                                                                                                                                        |
| ---- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | **`Holy VFX 01`(32px 셀, 37장)**                                 | §4에서 확인한 **밀도 최근접 미사용 팩**(1.16×, legacy·신규보다 1.0×에 가까움). 게다가 Initial→Repeatable→Impact **3단 구성**이 캐스팅→지속→착탄 스킬 타이밍과 그대로 대응([[에셋_후보_카탈로그]] 기존 지적) — 밀도와 구조 두 축 모두에서 최우선 검토 대상 |
| 2    | **heroes99 ATTACK2·AIR ATK1의 내장 슬래시 트레일**                      | [[heroes99_에셋_전수탐색]]에서 이미 발견됐으나 미채택 — 신규 합성 0으로 즉시 재사용 가능(RowIndex 전환만)                                                                                                      |
| 3    | **`vfx/Free/` 177장(180장 중 3장만 사용 예정)**                         | D4.5a로 전수 실측까지 끝난 재고. 색상 9행 내장이라 스킬별 신규 그리기 없이 즉시 배정 가능                                                                                                                      |
| 4    | **`pixelhudui_free_v10`(진짜 픽셀아트 HUD 킷)**                       | UI 3화면 중 6개가 미구현(`_A1Temp` 임시)인 상태에서 스타일이 맞는 완성 HUD 세트가 이미 확보돼 있음. unitypackage 추출만 하면 됨(이번 조사로 내부 파일 매핑 완료)                                                                 |
| 5    | **`Winlu`의 `Objects/`(문·나무·조각상 등 독립 스프라이트)**                   | 전투배경은 기각됐지만 [[에셋_후보_카탈로그]]가 명시한 대로 **로비 실내(벽·바닥 위주) 용도는 별도 판정 대상**. 배경 투명·그림자 베이크 완료라 즉시 임포트 가능한 소품만 따로 쓸 수 있음                                                               |
| (참고) | `Fantasy Exterior`의 `GreenEdition`/`RedEdition`(계절·바이옴 팔레트 변형) | 지형 전체 세트의 보너스 변형본 — 완전 미조사·미사용, 필요 시점 되면 추가 조사 필요                                                                                                                            |

---

## 8. 라이선스 요약

| 팩 | 라이선스 문서 | 판정 |
|---|---|---|
| `heroes99/` | 없음(로컬 파일 0건) | **못 찾음** — 구매처 재확인 필요 |
| `vfx/`(Free·Hit·Holy·Smear 4팩 전부) | 없음(로컬 파일 0건) | **못 찾음** — Steam 출시 전 필수 확인([[에셋_후보_카탈로그]] 기존 지적 재확인) |
| `tilesets/`(Winlu 계열) | 로컬엔 없음. 단 [[에셋_후보_카탈로그]]에 판매 페이지 기재 문구 인용됨("상업적 사용 가능·수정 가능") | 로컬 파일로는 **못 찾음**, 판매 페이지 문구는 2차 확인 필요(구매 시점 캡처, 페이지 변경 가능성) |
| `ui-packs/pixelhudui_free_v10` | README.md 있음(자체 조항 없음) + 내장 **Noto Serif = SIL OFL 1.1**(전문 확인) | 폰트만 명문 라이선스, 스프라이트 자체 조항은 **못 찾음** |
| `ui-packs/gui_fantasy_kit` | 없음 | **못 찾음** |
| `ui-packs/2d_icons_pictoiconpack01` | 없음 | **못 찾음** |
| `ui-packs/Pixel UI pack 3` | 없음 | **못 찾음** |

→ **8개 팩 중 7개가 "로컬 라이선스 문서 없음".** 유일한 예외는 pixelhudui의 내장 폰트뿐이다. Steam 출시 전 **구매 내역·마켓 페이지에서 전 팩 라이선스 재확인이 필요**하다는 기존 결론([[에셋_후보_카탈로그]])이 이번 전수 조사로 다시 한번 확인됐다.

---

## 9. 놓치고 있던 것 (신규 카테고리 점검)

`_RawAssets/` 전체 확장자 전수 스캔(png/gif/py/aseprite/tset/txt/zip/rar/unitypackage 외 **0건**) 결과:

- **사운드(wav/mp3/ogg) — 0개.** 프로젝트에 로컬 확보된 사운드 원본 에셋이 **전혀 없다.** SFX는 `data/sfx_draft.csv`에 설계 데이터만 있고 실제 음원 소스는 미조사/미보유 상태로 보인다(이번 조사 범위 밖이나 향후 반드시 짚어야 할 공백).
- **폰트(ttf/otf) — heroes99·vfx·tilesets·_mockups엔 0개.** `ui-packs/pixelhudui_free_v10` 안에 Noto Serif 3종만 유일하게 존재(§6-1). 프로젝트 UI 방향(Cinzel/Jost, [[에셋_후보_카탈로그]] 언급)에 필요한 폰트 파일 자체는 `_RawAssets`에 **보관돼 있지 않다** — 별도 확보 필요.
- **`8D_Characters.zip`(8방향 캐릭터, 카탈로그 문서가 언급) — 로컬에 실재하지 않음.** 구매 여부·다운로드 여부 재확인 필요(§5-1).

---

## 10. 확인 못 한 것 (정직 기록)

- `Pixel UI pack 3.rar` 내부 — unrar 미설치로 미해제. `.zip`과 동일 내용으로 추정되나 **미검증**.
- `gui_fantasy_kit`·`2d_icons_pictoiconpack01`·`Pixel UI pack 3`의 실제 상업 라이선스 조항 — 로컬 파일 0건, Unity/구매처 계정 재확인 필요.
- `tilesets`(Winlu) 라이선스 — 판매 페이지 문구는 [[에셋_후보_카탈로그]]에 인용돼 있으나 **로컬 문서 근거는 없음**, 페이지가 바뀌었을 가능성 배제 못 함.
- `Holy VFX 01`(§4·§7 밀도 최근접 후보)의 실제 임포트 필터/밉맵/압축 검증 — **미실행**(외삽 계산일 뿐, [[E_TC]] E-S2T-02급 검증 전까지 "채택 가능"이 아니라 "유력 후보"로만 취급할 것).
- `8D_Characters.zip` 존재 여부 — 로컬 부재만 확인, 구매 이력 자체는 미확인.
- 사운드 에셋의 실제 조달 계획 — 이번 조사 범위 밖, 존재 자체의 공백만 기록(§9).

---

## 산출물

| 항목 | 내용 |
|---|---|
| 조사 방식 | Python 3.13(`C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe`) + Pillow 12.2.0 + `tarfile`(unitypackage=tar.gz 무해제 열람) + `zipfile`. MCP·UE 접촉 0건 |
| 원본 접촉 | 읽기만. 수정·이동·삭제 0건. unitypackage는 스트림에서 직접 read, 디스크에 압축 해제 안 함(라이선스 준수 목적) |
| 추출 산출물 위치 | 세션 스크래치패드(`C:\Users\user\AppData\Local\Temp\claude\...\scratchpad\`) — 프로젝트 폴더 미오염, 유료 에셋 이미지 자체는 본 문서에 포함 안 함 |
| 커밋 | 안 함(PM 담당) |
