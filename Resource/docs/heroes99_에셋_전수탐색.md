---
type: reference
project: projectTP
updated: 2026-08-11
status: active
---

# heroes99 에셋 전수탐색 — "이펙트가 이미 포함돼 있는 거 아니야?" 조사

> 오너 질문에 대한 답을 찾기 위한 `_RawAssets` 전수 탐색. 관련: [[전투VFX_방향]] · [[D4.5a_VFX재고_실측]] · [[D4.5b_VFX행배정]] · [[E_TC]] · [[D2_구현]]
> 조사 방식: **파일시스템 조사 + Pillow 실측만**(MCP·언리얼 무접촉, uasset 무접촉). 스크립트는 스크래치패드에서 실행, 프로젝트 오염 없음.
#projectTP/스킬연출구조 #projectTP/art-pipeline

---

## 0. ★오너 질문에 대한 답 (한 문장)

**부분적으로 그렇다.** heroes99엔 "이펙트" 카테고리 자체는 없지만(별도 폴더·`parts.csv` 행 0개), **ATTACK1·ATTACK2·AIR ATK1 3개 모션에서 무기(`weapon_top`) 레이어 프레임 그 자체에 참격 궤적(슬래시 트레일)이 그려져 있다** — 이건 캐릭터·무기와 같은 텍스처, 같은 좌표계, 같은 프레임이라 위치·타이밍이 자동으로 맞는다. 그리고 **이 트레일은 이미 라이브 게임에 나오고 있다**(`BP_BattleSpawnPoint.PlayAttack`이 `RowIndex=5`로 이 행을 재생 중, [[D2_구현]] 실측). 반면 지금 별도로 붙이고 있는 `T_FX_Smear`/`T_FX_Hit`는 **heroes99가 아니라 전혀 다른 팩**(`_RawAssets\vfx\Free\`, 180장 범용 이펙트 시트)에서 온 것이고, 밀도도 다르다(0.77×, [[E_TC]] 기실측). 즉 **오너 가설이 맞다** — heroes99 자체 트레일과 외부 Smear를 동시에 쓰고 있어 이중 레이어가 되고, 타이밍 기준점도 서로 다른 팩에서 왔다.

단, **타격(피격) 스파크/충격 이펙트는 heroes99에 없다** — 그건 외부 팩(Hit Effect 01, Holy VFX 01-02, Free)에서 가져오는 게 맞는 접근이다. "이펙트 전체가 heroes99에 있다"는 아니고 **"공격 스윙 트레일만 heroes99에 이미 있다"**가 정확한 답이다.

---

## 1. 폴더 트리 + 파일 수·용량

`D:\unreal\Resource\_RawAssets\` 전수(git 저장소 루트, 비공개):

| 폴더 | 용량 | 파일 수 | 내용 |
|---|---|---|---|
| `heroes99/` | 22M | **802**(png 791·gif 7·py 2·aseprite 2) | ★캐릭터 파츠 팩(스킨/얼굴/헤어/의상/무기) + 합성 스크립트 |
| `vfx/` | 29M | 244 | 이펙트 스프라이트 4개 하위 팩(아래 §4-1) |
| `tilesets/` | 70M | 193 | 배경 타일셋(A2 terrain·Fantasy Exterior·Winlu exterior 신/구) |
| `ui-packs/` | 21M | 6 | UI 아이콘·HUD 킷(`.unitypackage`·`.rar`/`.zip`, 미해제) |
| `_mockups/` | 2.4M | 22 | HD2D배경 기능의 오프라인 합성 목업(별도 기능, heroes99와 무관) |

**heroes99 확장자 breakdown**: png 791 · gif 7(문서용) · py 2(`compose.py`/`compose2.py`, 합성 스크립트) · aseprite 2(`clothcolor.aseprite`/`haircolor.aseprite`, 색상 마스터 원본, Pillow로 열리지 않음 — Aseprite 프로그램 필요, 미해독).

**문서·라이선스 파일**: heroes99 폴더 최상위/하위 어디에도 `.txt`/`.md`/`.pdf`/`.json`/`license`/`readme` 파일이 **0개**다. `parts.csv`(`D:\unreal\Resource\data\parts.csv`, 388행)는 heroes99 원본에 딸린 게 아니라 **이 프로젝트가 자체 제작한 카탈로그**로 보인다(프로젝트 규약에 맞춘 컬럼 구조 — `Id,#id_txt,Category,StyleNo,ColorNo,GenderTag,JobTags,AssetPathBot,AssetPathTop`). → **라이선스 조항은 로컬 파일로 확인 불가**(구매처 페이지 등 외부 확인 필요, 추측 금지).

### heroes99 파츠 카탈로그 (parts.csv 388행 실측)

| Category | 종류 수 | 색상 변형 | 파일 수(대략) |
|---|---|---|---|
| Skin | — | 6색(c1~c6) | 6 |
| Face | — | 7종(c1~c7) | 7 |
| Hair | 남 m1~m14(14종) + 여 f1~f9(9종) = 23종 | 각 10색(c1~c10) | 230행 (bot+top 쌍) |
| Cloth | s1~s17(17종) | 각 8색(c1~c8) | 136행 (일부만 top 있음 — 아래) |
| Weapon | 5종(sword×3형·spear·wand) | wand만 4색 | 8행 |

- **의상 top 유무**: cloth1~6, 9~11, 16~17은 **bot만** 있음(민소매/하의류 추정), cloth7~8, 12~15는 **bot+top 쌍**(상의류). `_composed/compose.py`가 cloth1로 합성한 초기 테스트가 상반신 노출로 보였던 원인이 이것(cloth1은 top 자산 자체가 없음 — 결함 아님, 팩 설계).
- **무기 5종 vs `weapon_types.gif`**: csv StyleNo 1~5 = **SWORD·AXE·DAGGER(순서 미상, weapon1~3) / SPEAR(weapon4) / WAND(weapon5)**. `weapon_types.gif`가 정확히 이 5개 라벨(SWORD/SPEAR/WAND/AXE/DAGGER)을 보여줘 **8행/5종 구성이 그대로 일치** 확인.

---

## 2. 문서 3개 해독 결과

### 2-1. `frameguide_v2.png` (1600×1360, 8열×17행 그리드를 2배로 확대한 주석 이미지) ★핵심

Read 툴로 직접 열람(이미지는 UE·MCP 없이도 시각 확인 가능). **17개 모션, 총 102프레임**이 각 행에 이름표와 함께 나열돼 있다. 프레임 번호는 **행마다 처음부터 다시 배정**(그리드 8칸을 다 안 채우면 나머지 칸은 회색/미사용, 다음 모션은 무조건 다음 행에서 시작 — 열 위치와 프레임번호가 8배수로 안 맞아도 정상).

| # | 모션 | 프레임 범위 | 프레임 수 | 비고 |
|---|---|---|---|---|
| 0 | IDLE 1 | 1–6 | 6 | |
| 1 | IDLE 2 | 7–12 | 6 | |
| 2 | RUN 1 | 13–20 | 8 | |
| 3 | RUN 2 | 21–28 | 8 | |
| 4 | JUMP(+FALL LOOP) | 29–36 | 8 | FALL LOOP=33–35 박스 |
| 5 | **ATTACK 1** | 37–42 | 6(가이드 표기는 8이나 실제 유효 6, 아래 §3) | **39·40에 슬래시 트레일** |
| 6 | **ATTACK 2** | 43–48 | 6 | **45·46에 트레일** |
| 7 | ATTACK 3 | 49–52 | 4 | 트레일 없음(찌르기형) |
| 8 | **AIR ATK 1** | 53–58 | 6 | **55·56에 트레일**(ATTACK1과 픽셀 동일) |
| 9 | AIR ATK 2 | 59–62 | 4 | 트레일 없음 |
| 10 | CASTING 1(+CAST LOOP) | 63–67 | 5 | LOOP=65–67 |
| 11 | CASTING 2(+CAST LOOP) | 68–72 | 5 | LOOP=70–72 |
| 12 | HURT | 73–76 | 4 | |
| 13 | DYING | 77–81 | 5 | |
| 14 | DASH(+DASH LOOP) | 82–89 | 8 | LOOP=84–86 |
| 15 | BLOCK | 90–94 | 5 | |
| 16 | ROLL | 95–102 | 8 | |

17행 = 실제 파일 그리드(8열×17행, 셀 100×40px, 시트 800×680px)와 정확히 일치.

### 2-2. `list_of_animation_full.gif` (550×630, 48프레임)

프레임 추출 결과 **17개 모션 아이콘이 3열×6행으로 배열된 카탈로그**(IDLE1/IDLE2/JUMP, RUN1/RUN2, ATTACK1/2/3, AIR ATK1/2, CASTING1/2/DASH, HURT/DYING, BLOCK/ROLL). `BLOCK`·`ROLL`에 `NEW!!` 라벨 — v2에서 추가된 모션임을 시사(파일명 `frameguide_v2`와 일치). **frameguide_v2.png의 17개와 정확히 같은 목록** — 우리가 아는 17종이 전부이고, 숨겨진 추가 모션은 없다.

### 2-3. `weapon_types.gif` (584×222, 50프레임)

5개 무기 아이콘: **SWORD, SPEAR, WAND, AXE, DAGGER**. §1의 `parts.csv` Weapon 8행(StyleNo 5종)과 **정확히 일치** — 카운트·구성 모두 확인.

### 2-4. 기타 문서 이미지

| 파일 | 내용 |
|---|---|
| `layer.gif`(326×228, 198프레임) | **합성 레이어 순서를 직접 애니메이션으로 시연**하는 문서. 프레임을 순서대로 보면 `WEAPON TOP → CLOTH TOP → HAIR TOP → CLOTH BOT → HAIR BOT → FACE → SKIN → WEAPON BOT` 순으로 라벨이 누적 표시됨(캐릭터가 한 겹씩 완성). `_composed/compose2.py`의 레이어 순서·art-pipeline 역할서의 합성 순서와 **정확히 일치** — 별도 "EFFECT" 레이어는 이 8개 목록에 없음(추가 카테고리 부재 재확인). |
| `samples.gif`(584×144, 165프레임) | 파츠 조합 미리보기(캐릭터 걷기 3종 등) — 전투 이펙트 없음, 순수 외형 샘플 |
| `color_variations.gif`(584×144, 144프레임) | 색상 변형 미리보기 3캐릭터 — 이펙트 없음 |
| `bg.png`(384×180) | 숲/잔디/물 배경 그림. **캐릭터 파츠와 무관한 벤더용 배경 이미지**(itch.io 프리뷰 배경으로 추정) — 현재 프로젝트 미사용, scene-builder 참고용으로 남겨둠 |
| `catalog_cloth.png`(576×1152) | Cloth1~17 × C1~C8 스와치 표(17행×8열) — parts.csv와 정합 |
| `catalog_hair.png`(1472×960) | 헤어 스와치 표(미상세 확인, 치수만 실측) |
| `bannercrt.gif`/`bannerplain.gif`(600×360, 96프레임) | 벤더 홍보 배너(레트로 CRT 필터 버전 포함) — 게임 에셋 아님 |
| `clothcolor.aseprite`/`haircolor.aseprite` | 색상 변형 마스터 원본(Aseprite 네이티브, Pillow 미해독) — **미사용, Aseprite 있으면 신규 색상 추가 가능** |

---

## 3. ★타이밍·위치에 쓸 수 있는 근거 (수치 실측)

### 3-1. 슬래시 트레일이 실재함 — Pillow 픽셀 실측

`weapon1_top.png`(800×680, 8×17그리드)에서 ATTACK1 각 프레임의 **비어있지 않은 픽셀 bbox 면적**을 셀 단위(100×40)로 실측(스크립트: 스크래치패드 `crop_frames2.py`/`crop_frames4.py`, 원본 무수정):

| 로컬 프레임(원프레임번호) | 1(37) | 2(38) | **3(39)** | **4(40)** | 5(41) | 6(42) |
|---|---|---|---|---|---|---|
| weapon1(sword) bbox 면적(px²) | 208 | 196 | **740** | **588** | 126 | 128 |
| weapon2(sword변형) | 252 | 208 | **759** | **726** | 240 | 260 |
| weapon3(sword변형) | 120 | 140 | **234** | **240** | 102 | 135 |
| weapon4(spear) | 748 | 559 | **1550** | **1104** | 552 | 616 |
| weapon5(wand) | 435 | 300 | **600** | **520** | 312 | 350 |

**5종 무기 전부**에서 로컬 3~4번째 프레임(원프레임 39~40)이 bbox 면적 최대치 — **참격 궤적(흰빛 아크)이 이 두 프레임에 그려져 있음을 시각 확인**(예: weapon1_top 39번 프레임만 잘라보면 칼자루에서 뻗어나가는 반투명 흰 곡선 궤적이 단독으로 보인다). `weapon_bot` 레이어에는 이 구간에서 픽셀이 전혀 없음(bbox=None 전부) — **트레일은 무조건 `weapon_top` 레이어에만 존재**.

같은 실측을 ATTACK2(43–48)·AIR ATK1(53–58)에도 적용: AIR ATK1의 bbox 값(740, 588 at 로컬3·4)이 ATTACK1과 **완전히 동일**(같은 픽셀 데이터 재사용 — 지상 공격 애니를 공중 공격에 그대로 씀). ATTACK2는 로컬4(46번, 656px²)가 최대, 로컬3(45번, 231px²)이 근접 2위 — 패턴은 동일(3~4번째 프레임 부근)하나 피크 위치가 한 프레임 늦음. ATTACK3·AIR ATK2는 최대값이 232px² 수준(찌르기형 — 트레일 없음, 결론: **모든 근접공격에 트레일이 있는 건 아니다**, 스윙형 3종에만 있음).

### 3-2. 이 트레일이 이미 라이브에 나오고 있다 — 코드 실측 대조

[[D2_구현]](`docs/features/공격버튼데모/raw/D2_구현.md`) 실측: `BP_BattleSpawnPoint.PlayAttack`이 캐릭터 본체 `SpriteMID`에 `RowIndex=5.0`을 세팅한다. **RowIndex=5(0-based)는 frameguide 6번째 행 = ATTACK1**과 정확히 일치. 후속 핫픽스 기록(같은 문서 L236, Director 실측)은 **"ATTACK1 실프레임 6개인데 FrameCount=8로 잘못 세팅돼 있었다"**(시트 마지막 2셀이 완전 투명)를 발견해 `FrameCount 8→6`, `RetriggerableDelay(재생시간) 0.95s→0.70s`로 수정 — 이번 조사의 §2-1 실측(ATTACK1 유효 프레임 6개, 열6·7은 회색)과 **완전히 일치**한다. 즉 **캐릭터 본체 텍스처(`T_Party_A1`~`B4`)는 이미 heroes99의 8×17 풀시트 그대로 임포트돼 있고, 공격 시 ATTACK1 행(트레일 포함)이 실제로 화면에 재생 중**이다.

- 트레일 등장 구간(추정, 0.70s를 6프레임 등분 가정): 로컬 3~4번째 프레임 ≈ **전체 재생시간의 약 33~50% 지점**.

### 3-3. 외부 Smear/Hit는 heroes99가 아니라 별개 팩

- [[D4.5a_VFX재고_실측]]: ~~`T_FX_Smear`/`T_FX_Hit`는 `_RawAssets\vfx\Free\` 소스~~ → ★**정정(2026-08-12): 진짜 출처는 `Smear VFX 01/`·`Hit Effect 01/`**(§4-1 정정 블록 참조). `Free\`(itch.io류 범용 180장 팩, Part1~15)는 **신규 3종의 출처**다. 5프레임(Smear, GridX=5)·6프레임(Hit, GridX=7 grid에 6프레임)짜리 서브UV 시트, 벤더 자체 색상행 9종 내장 — **heroes99와 폴더·명명·그리드 규약이 완전히 다르다**(heroes99는 8×17 캐릭터 그리드, vfx/Free는 64px 셀에 열 5~23·행 9 가변 그리드).
- [[E_TC]](`E-S5-06`, `E-H9`, CONFIRMED): **밀도 실측** — 캐릭터 스케일 기준 등가 uu/텍셀은 **6.48**, legacy Smear/Hit는 **5.00 uu/텍셀(0.77×, 즉 캐릭터보다 작게 그려짐)**, 신규 후보 3종은 **3.75 uu/텍셀(1.73× 필요)**. "전역 스케일 1값으로는 legacy와 신규를 동시에 6.48로 못 맞춘다"는 것도 이미 CONFIRMED 판정. → **같은 heroes99 팩이면 밀도가 저절로 맞았을 것**이라는 오너 가설의 반증 사례가 이미 실측으로 존재한다.
- [[D4.5b_VFX행배정]]: `PlayAttack` 이벤트가 캐릭터 RowIndex 전환과 **같은 커스텀 이벤트 안에서** `SmearMID` 표시(`SetVisibility(TRUE)`→`RetriggerableDelay(0.45)`→`FALSE`)도 함께 트리거한다(`IsAttackFamily(모션)==TRUE` 게이트). `전투완성/BP정리_통합명세`(H18)는 `PlayAttack` 내부에 `0.70/0.55/0.45×2` 타이머가 섞여 있음을 재확인, H30은 **`SmearMID`/`HitMID`가 같은 `EffectQuad` 1장을 공유해 동시 표시가 물리적으로 불가능**한 구조적 결함까지 지적한다.

---

## 4. 현재 쓰는 것 / 안 쓰는 것 대조표

### 4-1. `_RawAssets/vfx/` 4개 하위 팩 — 전부 heroes99와 무관, 별개 구매 자산

| 팩 | 파일 수 | 용량 | 원본 흔적 | 현재 사용 |
|---|---|---|---|---|
| `Free/`(Part1~15) | 196 | 29M | 64px 셀, 9색×가변열 서브UV, `Free Preview All.gif` 벤더 카탈로그 | **사용 중** — **신규 3종**(`T_FX_CastAtk`/`CastSupport`/`ProjectileArcane`)만. ~~`T_FX_Smear`·`T_FX_Hit`도 이 팩~~ ← **정정, 아래 참조** |
| `Hit Effect 01/` | 4 | 24K | `Hit Effect 1.aseprite` 원본 포함 | ★**사용 중** — 라이브 `T_FX_Hit`의 **진짜 원본**. ~~미사용(Free/Part13·14 소스)~~ |
| `Holy VFX 01-02/` | 37 | 48K | Impact/Initial/Repeatable 3단 + `Separated Frames` 폴더 | **미사용** — ★**밀도 최근접 후보**([[_RawAssets_전수카탈로그]] §0) |
| `Smear VFX 01/` | 7 | 18K | `Smear VFX 01.aseprite` 원본 포함, Horizontal/Vertical 6종 | ★**사용 중** — 라이브 `T_FX_Smear`의 **진짜 원본**. ~~이름이 유사해 헷갈리기 쉬우나 원본이 아님~~ |

> ★**정정 (2026-08-12) — legacy 2종의 출처를 틀리게 적었다.**
> 원안은 `T_FX_Smear`/`T_FX_Hit`가 `Free/` 팩에서 왔다고 썼는데(위 취소선), **실측으로 반증됐다.** 진짜 출처는 **폴더 이름 그대로** `Smear VFX 01/`과 `Hit Effect 01/`이다.
>
> **근거 3중**:
> | | Smear | Hit |
> |---|---|---|
> | 원본 파일 | `Smear 01 Horizontal 1.png` **240×48** | `Hit Effect 01 1.png` **336×48** |
> | 48px 셀 환산 | **5프레임** (240/48) | **7그리드** (336/48) |
> | `vfx_draft.csv` 실제 값 | `GridX=5` `FrameCount=5` ✅ | `GridX=7` `FrameCount=6` ✅ |
>
> **원인**: `Free/` 180장 전수 조사 중 legacy도 거기서 왔다고 **실측 없이 추정**했다. 폴더명이 `Smear VFX 01`·`Hit Effect 01`로 명백했는데 *"이름이 유사해 헷갈리기 쉽다"*며 오히려 **반대로 결론냈다.**
>
> ★**교훈**: 이름이 정확히 일치하는 후보를 *"헷갈리기 쉬우니 아닐 것"*으로 배제하려면 **배제할 실측 근거**가 있어야 한다. 없으면 그 후보가 정답일 가능성이 가장 높다.
>
> 신규 3종(`63000300`~`500`)의 `Free/` 출처 서술은 **맞다** — 혼동은 legacy 2개뿐이다.

### 4-2. heroes99 — 현재 쓰는 것 / 안 쓰는 것

| 항목 | 상태 |
|---|---|
| 캐릭터 본체(스킨/헤어/의상/무기 합성 풀시트) | **쓰는 중** — `T_Party_A1~B4` 8기 (`_composed/party/*.png` → 임포트) |
| IDLE(RowIndex=0) | **쓰는 중**(기본 표시) |
| **ATTACK1(RowIndex=5, 슬래시 트레일 포함)** | **쓰는 중**(`PlayAttack`) — 단, 트레일이 "쓰인다"는 인지 없이 우연히 같이 재생되고 있을 가능성 高(§3-2) |
| ATTACK2·AIR ATK1(동일 트레일 보유) | **미사용** — 코드에 RowIndex 6·8 전환 로직 없음(확인된 범위 내) |
| ATTACK3·AIR ATK2(트레일 없는 찌르기형) | **미사용** |
| IDLE2·RUN1·RUN2·JUMP·CASTING1/2·DASH·BLOCK·ROLL | **미사용**(캐릭터가 걷지도, 구르지도, 캐스팅 자세도 아직 취하지 않음) |
| HURT·DYING 행 | 코드상 `PlayHurtReaction`이 `HitMID`(외부 VFX)는 트리거하는 것을 확인했으나, 캐릭터 본체 RowIndex를 HURT/DYING(12/13)으로 전환하는지는 **이번 조사 범위(문서)에서 미확인** — 추측 금지 |
| `bg.png`(배경) | **미사용** |
| `clothcolor.aseprite`/`haircolor.aseprite`(색상 마스터) | **미사용**(Aseprite 필요) |
| `catalog_cloth.png`/`catalog_hair.png`(스와치 표) | **미사용**(파츠 선택 시 참고 자료로만 가치) |

---

## 5. 파급 — 지금 진행 중인 작업(잔상 위치·타이밍 튜닝)에 무엇을 의미하는가

1. **원인 재규명**: 잔상(Smear) 위치·타이밍이 안 맞는 근본 원인은 "튜닝 부족"이 아니라 **애초에 heroes99와 무관한 별도 팩(밀도 0.77×)을 heroes99 캐릭터에 억지로 맞추고 있기 때문**이라는 오너 가설이 **실측으로 뒷받침된다**([[E_TC]] CONFIRMED). 매직넘버 `Delay 0.45/0.55/0.70`도 서로 다른 3곳(외부 VFX의 FrameCount/FPS=10, heroes99 ATTACK1의 실프레임 6개, 그리고 이 둘을 섞어 쓰는 `PlayAttack` 내부 체인)에서 독립적으로 나온 값이라 **정합될 이유가 원래 없었다**.
2. **당장 쓸 수 있는 근거**: heroes99 ATTACK1(및 ATTACK2·AIR ATK1)의 트레일 프레임 위치(로컬 3~4/6, §3-1)는 **외부 VFX 타이밍 대신 참조 기준으로 쓸 수 있는 1차 자료**다. `PlayAttack`의 `RetriggerableDelay(0.70)`도 이미 heroes99 실측(FrameCount=6)에서 역산된 값이라 이 부분은 이미 올바르다 — 문제는 그 위에 얹힌 **외부 Smear의 `0.45`가 heroes99 타이밍과 무관한 별도 숫자라는 점**이다.
3. **검토 제안**(결정은 gameplay-engineer/Director 몫, art-pipeline은 근거만 제공): 근접 스윙 계열(평타·강타)에 대해서는 **외부 Smear 텍스처를 계속 덧씌우는 대신, 캐릭터 본체가 이미 갖고 있는 ATTACK1 트레일을 "그 자체로 이펙트"로 채택**하는 안이 있다 — 위치·스케일·타이밍 정합 문제가 정의상 발생하지 않는다(같은 텍스처, 같은 쿼드). 다만 **타격(피격) 스파크는 heroes99에 없으므로 외부 팩(Hit Effect 01/Holy VFX/Free) 사용은 계속 유효**하다 — 이번 조사가 "외부 VFX 전면 배제"를 뜻하진 않는다.
4. **미사용 자원**: ATTACK2·AIR ATK1(동일 트레일)·CASTING1/2·DASH·BLOCK·ROLL 7개 모션 행이 이미 캐릭터 텍스처 안에 있는데 코드가 아직 안 씀 — 스킬 다양화(캐스팅 연출, 회피 애니메이션 등) 시 **신규 합성 없이 RowIndex 전환만으로 즉시 활용 가능**.

---

## 6. 확신할 수 없는 것 (정직 기록)

- `clothcolor.aseprite`/`haircolor.aseprite` 내부 구조 — Pillow로 열리지 않아 **미해독**. Aseprite CLI/앱 필요.
- heroes99 라이선스 조항 — 로컬 파일에 **readme/license 없음**, 확인 불가. 구매처(마켓) 페이지 재확인 필요.
- `catalog_hair.png`의 정확한 행렬 구성(치수만 실측, 라벨 미판독).
- HURT·DYING 행이 캐릭터 본체 RowIndex 전환에 쓰이는지 — 문서 근거 없음(MCP 조회 금지 범위라 이번 조사에서 못 닫음).
- ATTACK2 트레일 피크가 ATTACK1과 정확히 같은 로컬 프레임(3번째)인지 vs 1프레임 늦은 4번째인지 — bbox 실측상 4번째가 근소 우위(656 vs 231)로 나왔으나, **육안 확인은 ATTACK1만 했고 ATTACK2는 bbox 수치로만 판단**했다. 정밀 재생 타이밍이 필요하면 art-pipeline이 ATTACK2 프레임도 육안 크롭 확인 권고.

---

## 산출물

| 항목 | 경로 |
|---|---|
| 조사 스크립트(재현 가능, 스크래치패드) | `crop_frames.py`~`crop_frames4.py` — 세션 스크래치패드(임시, 프로젝트 미포함) |
| 원본 미접촉 | heroes99·vfx 폴더 어떤 파일도 수정·이동·삭제 없음. 이미지 자체는 문서에 복사하지 않음(경로·메타데이터만 기록) |
| 참고: 밀도·타이밍 선행 실측 | [[D4.5a_VFX재고_실측]] · [[D4.5b_VFX행배정]] · [[E_TC]] · [[D2_구현]] · [[전투VFX_방향]] |
