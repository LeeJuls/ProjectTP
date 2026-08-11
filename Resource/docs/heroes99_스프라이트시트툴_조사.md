---
type: reference
project: projectTP
updated: 2026-08-12
status: active
---

# heroes99 스프라이트시트 툴 조사 — GitHub 소스 교차검증

> 오너 단서: *"이 툴을 참고하면 좀 더 다양한 기능도 알 수 있을 거야."* (`https://yhkk.itch.io/heroes99-spritesheet-tool`)
> 목적: [[heroes99_에셋_전수탐색]]의 **육안 해독**을 이 툴의 **GitHub 소스코드(데이터)**로 교차검증. MCP 무접촉, 웹 조사 + 로컬 파일 읽기(버전 확인·비교용)만 수행. 에셋 다운로드·수정·커밋 없음.
> #projectTP/art-pipeline

---

## 0. 총평 (한 문장)

**우리 해독은 프레임·모션 정의에서 100% 일치했다.** GitHub 소스(`app.js`)에 애니메이션 정의가 **데이터로 하드코딩**돼 있었고, 17행·102프레임·ATTACK1 6프레임(가이드 8칸 중 유효 6칸) 전부 우리 해독과 **정확히 일치**한다. 다만 **레이어 z-order는 3파전 불일치**를 발견했다 — 우리 문서(`layer.gif` 육안 해독) vs 우리 `compose2.py` vs GitHub 툴 소스가 세 곳 다 조금씩 다르다(§②). ★라이선스는 itch.io 페이지에서 **원문 그대로 확인**했다(§⑥) — 상업적 이용 가능, 재판매·AI 학습 금지.

---

## ① 애니메이션 정의 — 코드에 있는가

**있다.** GitHub 소스 `src/app.js`에 `ANIMATION_BLUEPRINTS` 배열로 **완전히 데이터화**돼 있다. 원문(발췌):

```js
const FRAME = { width: 100, height: 40, columns: 8, rows: 17, sheetWidth: 800, sheetHeight: 680 };

const ANIMATION_BLUEPRINTS = [
  { id: "idle_1", label: "Idle 1", playback: "loop", ranges: [[1, 1, 6]] },
  { id: "idle_2", label: "Idle 2", playback: "loop", ranges: [[2, 1, 6]] },
  { id: "run_1", label: "Run 1", playback: "loop", ranges: [[3, 1, 8]] },
  { id: "run_2", label: "Run 2", playback: "loop", ranges: [[4, 1, 8]] },
  { id: "jump", label: "Jump", playback: "once", ranges: [[5, 1, 4]] },
  { id: "fall_loop", label: "Fall Loop", playback: "loop", ranges: [[5, 5, 7]] },
  { id: "jump_end", label: "Jump End", playback: "once", ranges: [[5, 8, 8]] },
  { id: "attack_1", label: "Attack 1", playback: "once", ranges: [[6, 1, 6]] },
  { id: "attack_2", label: "Attack 2", playback: "once", ranges: [[7, 1, 6]] },
  { id: "attack_3", label: "Attack 3", playback: "once", ranges: [[8, 1, 4]] },
  { id: "air_attack_1", label: "Air Attack 1", playback: "once", ranges: [[9, 1, 6]] },
  { id: "air_attack_2", label: "Air Attack 2", playback: "once", ranges: [[10, 1, 4]] },
  { id: "casting_1", label: "Casting 1", playback: "once", ranges: [[11, 1, 2]] },
  { id: "cast_loop_1", label: "Cast Loop 1", playback: "loop", ranges: [[11, 3, 5]] },
  { id: "casting_2", label: "Casting 2", playback: "once", ranges: [[12, 1, 2]] },
  { id: "cast_loop_2", label: "Cast Loop 2", playback: "loop", ranges: [[12, 3, 5]] },
  { id: "hurt", label: "Hurt", playback: "once", ranges: [[13, 1, 4]] },
  { id: "dying", label: "Dying", playback: "once", ranges: [[14, 1, 5]] },
  { id: "dash", label: "Dash", playback: "once", ranges: [[15, 1, 2]] },
  { id: "dash_loop", label: "Dash Loop", playback: "loop", ranges: [[15, 3, 5]] },
  { id: "dash_end", label: "Dash End", playback: "once", ranges: [[15, 6, 8]] },
  { id: "block", label: "Block", playback: "hold", ranges: [[16, 1, 5]] },
  { id: "roll", label: "Roll", playback: "once", ranges: [[17, 1, 8]] },
];
```

`ranges`는 `[row(1-based), startCol, endCol]`. `createFrameCatalog()`가 이 목록을 순서대로 순회하며 전역 프레임 번호(`guideIndex`, 1부터 연속 증가)를 매긴다.

### ★대조표 — 우리 해독(17행) vs 코드(23 클립 → 17행)

| 행 | 우리 해독(원프레임) | 코드 guideIndex(재계산) | 일치 | 코드가 추가로 쪼갠 서브클립 |
|---|---|---|---|---|
| IDLE1 | 1–6(6) | 1–6(6) | ✅ | — |
| IDLE2 | 7–12(6) | 7–12(6) | ✅ | — |
| RUN1 | 13–20(8) | 13–20(8) | ✅ | — |
| RUN2 | 21–28(8) | 21–28(8) | ✅ | — |
| JUMP(+FALL LOOP) | 29–36(8), LOOP=33–35 | jump 29–32(4)+**fall_loop 33–35(3)**+**jump_end 36(1)** | ✅(LOOP 구간까지 정확 일치) | **신규**: 착지 프레임(36)이 `jump_end`로 별도 분리 |
| **ATTACK1** | 37–42(6), 가이드 8칸 중 **실유효 6** | **[6,1,6] → 37–42(6)**, 열7·8은 애니 정의에 미포함 | ✅✅ **코드가 "실유효 6"을 그대로 증명** | — |
| ATTACK2 | 43–48(6) | 43–48(6) | ✅ | — |
| ATTACK3 | 49–52(4) | 49–52(4) | ✅ | — |
| AIR ATK1 | 53–58(6) | 53–58(6) | ✅ | — |
| AIR ATK2 | 59–62(4) | 59–62(4) | ✅ | — |
| CASTING1(+LOOP) | 63–67(5), LOOP=65–67 | casting_1 63–64(2)+**cast_loop_1 65–67(3)** | ✅(LOOP 구간 정확 일치) | — |
| CASTING2(+LOOP) | 68–72(5), LOOP=70–72 | casting_2 68–69(2)+**cast_loop_2 70–72(3)** | ✅(LOOP 구간 정확 일치) | — |
| HURT | 73–76(4) | 73–76(4) | ✅ | — |
| DYING | 77–81(5) | 77–81(5) | ✅ | — |
| DASH(+LOOP) | 82–89(8), LOOP=84–86 | dash 82–83(2)+**dash_loop 84–86(3)**+**dash_end 87–89(3)** | ✅(LOOP 구간 정확 일치) | **신규**: 복귀 프레임(87–89)이 `dash_end`로 별도 분리 |
| BLOCK | 90–94(5) | 90–94(5), playback=**"hold"** | ✅ | **신규**: 재생 타입이 loop/once가 아닌 **"hold"**(자세 유지형)로 명시 |
| ROLL | 95–102(8) | 95–102(8) | ✅ | — |

**합계 102프레임, 17행 — 완전 일치.** ★놓친 모션 없음: 코드도 정확히 17행·102프레임이고, 새로운 행/모션은 없다. 다만 코드는 우리 문서보다 **한 단계 더 세밀한 23개 "재생 클립" 단위**(재생 타입 once/loop/hold 구분 포함)로 나눠 관리한다 — 특히 JUMP·DASH의 "착지/복귀" 서브프레임과 BLOCK의 "hold" 재생 타입은 우리 문서에 없던 **신규 정보**다(모션 자체가 새로운 게 아니라 기존 행 안의 **서브클립 분류**가 새로움).

---

## ② 레이어 합성 규칙 — ★3파전 불일치 발견

### z-order 코드 원문 (`getLayerStack()`, back-to-front 배열 = 뒤에 올수록 위에 그려짐)

```js
return [
  layer("weapon_bot", weapon?.bot),
  layer("skin", skin),
  layer("hair_bot", hair?.bot),
  layer("face", face),
  layer("cloth_bot", cloth?.bot),
  layer("cloth_top", cloth?.top),
  layer("hair_top", hair?.top),
  layer("weapon_top", weapon?.top),
];
```
`renderComposite()`는 이 배열을 순서대로 `ctx.drawImage()`하므로 **배열 뒤쪽이 최종적으로 위(앞)**에 온다.

### 세 소스의 z-order(위→아래, 화면에서 앞→뒤) 비교

| 순위 | ①우리 문서(`layer.gif` 육안 해독) | ②우리 `compose2.py`(실사용 스크립트) | ③GitHub 툴 `app.js` |
|---|---|---|---|
| 1(최상단) | WEAPON TOP | WEAPON TOP | WEAPON TOP |
| 2 | CLOTH TOP | **HAIR TOP** | **HAIR TOP** |
| 3 | HAIR TOP | **CLOTH TOP** | **CLOTH TOP** |
| 4 | CLOTH BOT | FACE | **CLOTH BOT** |
| 5 | HAIR BOT | SKIN | FACE |
| 6 | FACE | CLOTH BOT | HAIR BOT |
| 7 | SKIN | WEAPON BOT | SKIN |
| 8(최하단) | WEAPON BOT | HAIR BOT | WEAPON BOT |

**판단(근거 포함):**
- **WEAPON TOP이 최상단**이라는 점은 3곳 모두 일치 — 확정.
- **2·3위(HAIR TOP vs CLOTH TOP 순서)**: 우리 문서만 "CLOTH TOP이 위"라고 읽었고, **독립적으로 작성된 두 코드(우리 `compose2.py` + 외부 `app.js`)는 둘 다 "HAIR TOP이 위"로 일치**한다. `layer.gif`는 프레임이 누적 표시되는 애니메이션 GIF라 "라벨이 나타나는 순서"를 back-to-front/front-to-back 어느 쪽으로 읽어야 하는지 자체가 모호하다 — **육안 해독 쪽이 오독일 가능성이 높다.** → **HAIR TOP > CLOTH TOP이 맞다고 판단**(코드 2곳 일치 vs 육안 해독 1곳).
- **4~8위(CLOTH BOT·HAIR BOT·FACE·SKIN·WEAPON BOT의 상대 순서)**: 이 구간은 **`compose2.py`와 `app.js`조차 서로 다르다**(예: `compose2.py`는 FACE·SKIN을 중간에, `app.js`는 FACE를 6위·SKIN을 거의 최하단에 배치). 이 구간은 **판정 보류** — 코드 2곳이 불일치하므로 "코드가 항상 맞다"고 가정할 수 없다. 실제 파츠(어깨패드 큰 갑옷 등 `cloth_top`이 두꺼운 조합)로 두 순서를 렌더링해 육안 비교하는 **실증이 필요**하다(이번 조사는 웹조사+문서 범위라 렌더 실험은 하지 않았다 — art-pipeline 후속 작업으로 제안).
- 참고로 기존 `_composed/hero_knight_idle1.png`(`compose2.py` 결과물, 이미 존재하는 파일 열람만 함)를 봤으나 100×40px로 너무 작아 이 구간 순서 검증에는 **증거력 없음**(선택한 파츠 조합에 hair_top/cloth_top 겹침이 크지 않아 판별 불가).

### 오프셋·앵커·피벗 — ★없음 (확인)

`app.js` 전체를 읽었으나 **offset/anchor/pivot 관련 필드가 코드에도 JSON 스키마에도 전혀 없다.** 합성은 예외 없이 `ctx.drawImage(image, 0, 0)` — 모든 레이어 PNG를 캔버스 `(0,0)`에 그대로 겹친다. 즉 **정렬은 런타임 오프셋이 아니라 "각 파츠 PNG 파일 자체가 이미 800×680 풀시트 크기이고, 캐릭터가 올바른 위치에 미리 그려져 있다"는 방식**으로 해결된다(우리 `compose.py`/`compose2.py`의 `Image.alpha_composite` 방식과 동일한 전제). 이는 우리가 겪은 VFX 위치 문제(`E_TC` 밀도 불일치)의 원인이 heroes99 캐릭터 레이어가 아니라 **별도 VFX 팩과 heroes99 그리드가 애초에 다른 좌표계**라는 기존 결론([[heroes99_에셋_전수탐색]] §3-3)과 **부합**한다 — heroes99 자체엔 오프셋 규칙이 "없는 것"이 정상이다.

---

## ③ 시트 레이아웃 + JSON 스키마

**셀·그리드**: `FRAME = {width:100, height:40, columns:8, rows:17, sheetWidth:800, sheetHeight:680}` — 우리 문서의 "8열×17행, 셀 100×40px, 시트 800×680px"와 **완전 일치**.

**JSON export 스키마**(`buildExportData()` 원문 구조, 필드명 그대로):

```
{
  version: "heroes99-sprite-sheet-tool@1.1.0",   // 툴 자체 버전(heroes99 팩 버전 아님)
  generatedAt, source:{rootName,pngCount,unmatchedPngCount},
  sheet:{width,height,frameWidth,frameHeight,columns,rows,frameCount,cellCount},
  selection:{skin,face,hair:{style,color},cloth:{...},weapon:{...}},
  visibility:{ hair_bot, weapon_bot, skin, face, cloth_bot, cloth_top, hair_top, weapon_top },
  layers:[{order,slot,label,path,style,color,part}],           // 실제 사용된 8개 레이어
  cells:[{row,col,x,y,w,h,guideIndex,animationId,animationLabel}],  // 136칸(8×17) 전부
  frames:[{guideIndex,animationId,animationLabel,row,col,x,y,w,h}], // 유효 102프레임
  animations:[{id,label,playback,rowRanges:[{row,startCol,endCol}],frameCount,guideFrames,frames}] // 23클립
}
```

**폴더/파일명 규칙(정규식, 원문)** — 우리 로컬 `_RawAssets/heroes99` 폴더 구조와 대조:

| 카테고리 | 코드 정규식 | 로컬 실측 예시 | 일치 |
|---|---|---|---|
| skin | `^skin\/skin_c(\d+)\.png$` | `skin/skin_c1.png`~`c6` | ✅ |
| face | `^face\/face_c(\d+)\.png$` | `face/face_c1.png`~`c7` | ✅ |
| hair | `^hair\/([mf]\d+)\/\1_(top\|bot)\/\1_c(\d+)_(top\|bot)\.png$` | `hair/m5/m5_top/m5_c7_top.png` | ✅ |
| cloth | `^cloth\/(cloth\d+)\/\1_(top\|bot)\/\1_c(\d+)_(top\|bot)\.png$` | `cloth/cloth15/cloth15_bot/cloth15_c1_bot.png` | ✅ |
| weapon | `^weapon\/(weapon\d+)\/\1_(top\|bot)\/\1(?:_c(\d+))?_(top\|bot)\.png$` (색상 **선택적**) | `weapon/weapon1/weapon1_top/weapon1_top.png`(무색상) vs `weapon/weapon5/weapon5_top/weapon5_c1~c4_top.png`(4색) | ✅ — 정규식의 "무기만 색상 선택적" 규칙이 로컬 실측(무기1~4 무색상, 무기5=완드만 4색)과 **정확히 일치** |

폴더 구조·명명 규칙 100% 일치. 코드는 folder-scan 기반이라 "root 폴더명이 `Heroes99_v1.2/`면 그 프리픽스를 벗겨낸다"는 하드코딩도 있다(`normalizeRelativePath`) — ④ 버전 확인에 사용.

---

## ④ 버전

- **툴이 요구하는 버전**: 코드에 `"Heroes99_v1.2/"`가 리터럴 문자열로 하드코딩(`normalizeRelativePath`), README도 "select your local `Heroes99_v1.2` folder"라고 명시. **v1.2 고정.**
- **itch.io 원본 파일명**: 상품 페이지의 다운로드 파일이 `Heroes99_v1.2.zip`(본문 파일 목록 16MB, 데브로그 첨부는 15MB로 표기 차이 있음 — 재업로드에 따른 itch.io 표시 오차로 추정, 확정 못함).
- **로컬 `_RawAssets/heroes99`에 리터럴 버전 문자열은 없다**(PNG/GIF 메타데이터도 Pillow로 확인했으나 `srgb`만 있고 tEXt/버전 청크 없음, 파일명에도 버전 표기 없음) — 이 부분은 **전수탐색 문서의 기존 결론과 동일**(readme/license 0개).
- **그러나 내용 시그니처가 v1.2와 정확히 일치**: 데브로그(`au-pixel.itch.io/heroes99/devlog/927617`, 2025-04-18 게시) 원문:
  > "Weapon Block Animation / Dodge Roll Animation / Added Catalog for hair and cloth for easier maneuver / Sprite sheet is now split by Animation and this format will stay for future update"

  이 4가지가 v1.2에서 **새로 추가된 것**이다. 로컬 폴더는 이미 **BLOCK·ROLL 행(16·17행)**, **`catalog_hair.png`/`catalog_cloth.png`**, **애니메이션별 분리 폴더 구조**(`hair/`, `cloth/`, `weapon/`가 각각 톱/봇 하위분리)를 **전부 갖고 있다** — v1.1 이하였다면 이 중 다수가 없어야 정상이다. → **정황증거로 v1.2가 맞다고 판단**하나, 리터럴 버전 문자열로 확정한 것은 아니다(추측과 정황증거는 구분해 기록).
- **참고**: itch.io 댓글에서 발견한 **제3의 정보** — 같은 페이지에 다른 제작자(`hyperdoxical`)의 유사 툴(`Character Assembler`)도 있고, 이 툴도 "Compatible with Heroes99 v1.2"라고 명시했다. 두 독립 커뮤니티 툴 모두 v1.2를 타겟팅한다는 정황도 추가 근거.

**v1.2 이후 신규 변경**: 위 데브로그가 가장 최근(최신) 데브로그로 확인됨(그 이전 글은 "Mockup Added & Free Animated Monsters Uploaded", 2024-10-23). **v1.3 이상은 존재하지 않는다**(2026-08-12 기준, itch.io 페이지 재확인).

---

## ⑤ 우리가 안 쓰고 있는 기능·자원

| 항목 | 툴/팩이 제공 | 우리 프로젝트 사용 여부 |
|---|---|---|
| JSON export/import 라운드트립(파츠 선택 상태 저장·복원) | 있음 | **미사용** — `compose2.py`는 하드코딩된 파츠 경로 리스트, JSON 기반 데이터 파이프라인 아님 |
| Random 파츠 조합 버튼 | 있음 | **미사용**(해당 없음 — 우리는 `parts.csv` 큐레이션 방식) |
| 재생 타입 구분(loop/once/**hold**) | 코드에 명시(BLOCK=hold) | **미사용** — 기존 BP 쪽 RowIndex/FrameCount 방식이 재생 타입(특히 "hold" 자세유지형)을 구분하는지 이번 조사 범위에서 확인 못함, gameplay-engineer 확인 필요 |
| JUMP의 착지(`jump_end`, 1프레임) / DASH의 복귀(`dash_end`, 3프레임) 서브클립 | 코드에 명시 | **미사용**(JUMP·DASH 자체가 아직 미구현 — §④ 전수탐색 문서 4-2 재확인) |
| 애니메이션 종류 자체(IDLE2·RUN1/2·JUMP·CASTING1/2·DASH·BLOCK·ROLL) | 텍스처에 이미 존재 | **미사용** — 기존 전수탐색 문서 결론과 동일, 신규 발견 없음 |

새로 드러난 것은 "카테고리·모션 종류"가 아니라 **"재생 방식(once/loop/hold)과 행 내부 서브클립 분리"**라는 세밀도 차이다. 코드 관점에서 우리가 못 쓰고 있는 건 주로 **BLOCK의 "hold" 재생 방식**과 **JUMP/DASH의 진입-루프-종료 3단 구조**다.

---

## ⑥ ★라이선스 — itch.io 원문 그대로 인용

`https://au-pixel.itch.io/heroes99` "LICENSE" 섹션 **원문 전체**:

> "You can use this asset pack in both free and commercial projects. You can modify the assets as you need.
>
> You can showcase the assets in tutorials in social medias as long as a link is included: https://au-pixel.itch.io/heroes99
>
> You may not repackage and resell the assets, no matter how much they are modified - this includes as NFT's.
>
> You may not use these assets to train AI."

**요약(해석은 참고용, 원문이 우선)**:
- 무료·상업 프로젝트 모두 사용 가능, 수정 가능.
- 튜토리얼/SNS에 쇼케이스할 땐 원본 링크 포함 필요(게임에 내장해 배포하는 일반적 사용에는 이 조건이 적용되는지 itch.io 페이지에 별도 명시 없음 — 안전하게는 게임 크레딧에 링크 포함 권장, 단 이건 이번 조사의 판단이지 원문 강제조항 확인은 아님).
- **재판매·재패키징 금지**(수정 정도와 무관, NFT 포함).
- **AI 학습 금지**.

**GitHub 저장소(`yhc509/heroes99-spritesheet-tool`) README의 라이선스 관련 원문**:
> "Follow the license and usage terms from the original asset page, including restrictions on repackaging, resale, and AI training."

툴 자체(코드)에는 별도 라이선스 명시가 없고, itch.io 원본 팩의 조건을 그대로 따르라고만 되어 있다. **AI 코드/문서 생성 고지**는 itch.io 상세 설명 어딘가가 아니라 **GitHub 저장소 자체 설명**에 있었다(아래 참고).

**부가 확인**: 저장소 설명에 "Code and documentation generated with assistance from OpenAI ChatGPT/Codex. No AI-generated art assets are included."라는 고지가 있다 — **툴 코드는 AI 보조로 작성됐지만 아트 에셋은 AI 생성물이 아니다**라는 뜻. heroes99 원본 아트 자체의 AI 생성 여부와는 무관한 별개 고지다.

**저장소 구조 판단**: 이 프로젝트는 `_RawAssets`(비공개 LFS)와 `Content`(비공개 LFS)에 원본·합성 에셋을 두고 공개 저장소(`ProjectTP`)엔 소스코드만 두는 구조([[저장소_구조_규약]])다. "재판매·재패키징 금지" 조항은 **원본 에셋 파일 자체를 별도 상품으로 재판매/재배포**하는 것을 금지하는 것으로 읽히며, 게임에 내장해 컴파일된 형태로 배포하는 것은 라이선스가 명시적으로 허용한 "commercial projects" 사용에 해당한다고 판단된다(단, 이는 이번 조사자의 해석이며 법률 자문이 아니다). **비공개 저장소에 원본을 두고 공개 저장소엔 코드만 두는 현재 구조는 이 라이선스 조건과 상충하지 않는다**고 판단된다.

---

## 대조표 요약 (①~⑥ 종합)

| # | 항목 | 우리 기존 해독 | 코드/원문 확인 | 판정 |
|---|---|---|---|---|
| ① | 모션 수·프레임 수 | 17행·102프레임 | 17행·102프레임(23 서브클립) | **일치** |
| ① | ATTACK1 유효 프레임 | 37–42(6), "가이드는 8이나 실유효 6" | `[6,1,6]`=37–42(6) | **일치**(코드가 우리의 자체 정정을 재확인) |
| ① | 놓친 모션 | (없다고 판단) | 없음, 단 서브클립(hold/jump_end/dash_end) 세분화는 신규 정보 | **일치 + 신규 세부정보** |
| ② | z-order 최상단 | WEAPON TOP | WEAPON TOP | **일치** |
| ② | z-order 2·3위 | CLOTH TOP > HAIR TOP | HAIR TOP > CLOTH TOP (코드 2곳 일치) | **불일치 — 코드 쪽이 맞다고 판단**(근거: 독립된 두 코드가 일치, 육안 해독은 GIF 프레임 순서 해석의 모호성 있음) |
| ② | z-order 중하단(FACE/SKIN/CLOTH BOT/HAIR BOT/WEAPON BOT) | 문서: 순서 A | `compose2.py`≠`app.js`(서로도 불일치) | **판정 보류** — 렌더 실증 필요(후속 작업 제안) |
| ② | 오프셋·앵커·피벗 | (미확인) | **없음**(전 레이어 (0,0) 드로우, PNG 자체가 풀시트 정렬) | **신규 확인** |
| ③ | 시트 크기·셀 크기 | 800×680, 100×40, 8×17 | 동일 | **일치** |
| ③ | JSON 스키마 | (몰랐음) | 상세 스키마 확보(§③) | **신규 확보** |
| ④ | 로컬 팩 버전 | (readme 없어 확인 불가) | v1.2 정황증거 다수 일치(BLOCK/ROLL/catalog/분리폴더) | **정황상 v1.2로 판단**(리터럴 문자열 확정은 아님) |
| ⑤ | 미사용 자원 | 모션 7종 미사용 | 동일 + "hold" 재생타입, jump_end/dash_end 서브클립 미사용 | **일치 + 신규 세부정보** |
| ⑥ | 라이선스 | "확인 불가"로 기록 | itch.io 원문 확보(§⑥) | **신규 확보 — 상업사용 가능/재판매·AI학습 금지** |

---

## ★기존 문서(`heroes99_에셋_전수탐색.md`)에서 고쳐야 할 항목 목록 (PM 판단용 — 직접 수정하지 않음)

1. **§2-4 `layer.gif` 해독 정정 후보**: "`WEAPON TOP → CLOTH TOP → HAIR TOP → ...`" 중 **CLOTH TOP과 HAIR TOP의 순서가 뒤바뀐 것으로 보인다**(§② 근거). `HAIR TOP → CLOTH TOP` 순으로 정정 검토 요망.
2. **§2-4 같은 줄의 "별도 EFFECT 레이어는 이 8개 목록에 없음" 서술**은 여전히 유효(코드에도 8개 슬롯만 존재, `weapon_bot/skin/hair_bot/face/cloth_bot/cloth_top/hair_top/weapon_top`) — **수정 불필요**, 재확인만.
3. **§3-1 ATTACK1 "실유효 6" 각주**에 "GitHub 툴 소스(`ANIMATION_BLUEPRINTS`)가 `[6,1,6]`으로 6프레임만 정의해 이를 독립적으로 재확인함"이라는 **근거 보강 각주 추가 후보**(교차검증 출처 명시).
4. **§6 "확인할 수 없는 것" 중 라이선스 항목**: "구매처(마켓) 페이지 재확인 필요"로 남아있는데, 이번 조사로 **itch.io 라이선스 원문을 확보**했으므로 해당 항목을 이 문서(`heroes99_스프라이트시트툴_조사.md`) §⑥ 링크로 대체 검토.
5. **신규 추가 후보**(기존 문서에 없던 정보): JUMP·DASH 행이 "진입-루프-종료" 3단 서브클립 구조라는 점, BLOCK이 once/loop가 아닌 "hold" 재생 타입이라는 점 — 향후 해당 모션 구현 시 참고하도록 §4-2(현재 쓰는 것/안 쓰는 것 표)에 각주 추가 검토.

---

## 조사 방법 기록

- **웹 조사**: `WebSearch`/`WebFetch` + 브라우저(Read-only 네비게이션)로 다음 페이지 직접 확인 — GitHub 저장소 루트·`src/` 디렉터리·`raw.githubusercontent.com/.../app.js`(전문)·`raw.githubusercontent.com/.../README.md`(전문), itch.io 툴 페이지, itch.io 원본 팩 페이지(설명+댓글+구매 파일 목록), itch.io 데브로그(`MAJOR UPDATE` 글, 2025-04-18).
- **로컬 확인(읽기만)**: `_RawAssets/heroes99/_composed/compose.py`·`compose2.py` 전문 읽기(비교용), 폴더 구조 실측(`weapon/`·`skin/` 하위), PNG/GIF 메타데이터 확인(Pillow `.info`, 버전 문자열 없음 재확인), 기존 산출물 `hero_knight_idle1.png` 열람(신규 렌더 생성 없음).
- **하지 않은 것**: 에셋 다운로드, 원본 파일 수정/이동, git 커밋, 신규 합성 렌더링 실험(z-order 중하단 판정 보류 사유), MCP(`unreal-mcp`) 호출.

## 참고

- [[heroes99_에셋_전수탐색]] — 이번 조사가 교차검증한 원본 해독 문서.
- GitHub: `https://github.com/yhc509/heroes99-spritesheet-tool` (branch `main`, 파일: `src/app.js`·`src/index.html`·`src/styles.css`·`README.md`)
- itch.io 툴: `https://yhkk.itch.io/heroes99-spritesheet-tool`
- itch.io 원본 팩: `https://au-pixel.itch.io/heroes99` (현재 파일: `Heroes99_v1.2.zip`)
- itch.io 데브로그: `https://au-pixel.itch.io/heroes99/devlog/927617/major-update-heroes-99-character-pack` (2025-04-18, v1.2 변경사항)
