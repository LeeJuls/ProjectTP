---
type: spec
project: projectTP
feature: 전투UI
screen: WBP_BattleHUD
updated: 2026-07-15
status: design_v2 오너 확정(approved.html) — 1순위 WBP 골격 생성 완료(§B 3단계, WBP_BattleHUD/WBP_UnitFrame/WBP_SkillMenu/WBP_SkillMenuRow), 오너 UMG 배치 대기(§B 4단계, `오너_UMG배치가이드.md` 참고), 2순위는 명세만 선반영. WBP_UnitFrame(HP 게이지)은 U단계로 배치+배선 완료 — F3 완결([[U단계_HP게이지_UMG_실장]])
---

# WBP_BattleHUD spec.md

> §C-1 "전사 기준" 문서. 상위 규약: [[UI_화면_규약]] §B(제작 파이프라인 5단계)·§C-1(폴더 구조)·§D(명명)·§E(재사용 컴포넌트: WBP_UnitFrame/WBP_DamageNumber 후보)·§G(문자열 UI_BATTLE_*) · 명명 상세: [[네이밍_폴더_규약]] §9(위젯 트리 요소).
> 승인 디자인: `approved.html`(= `design_v2.html`과 동일, 오너 확정 2026-07-14) · 이전판: `design_v1.html`(가로 3카드 커맨드박스 — v2에서 세로 리스트로 교체).
> 데이터 SSOT 교차: [[전투완성/청사진]]·[[전투완성/plan]] §F2(DT_JobStats/DT_Skills 필드)·§F3(현재 임시 HP 구현)·§F7(스킬 슬롯 재바인딩 아키텍처) — 이 화면이 **대체/드롭인**하는 기존 임시 구현의 SSOT.
> 소관: system-ui-designer(이 문서). 구현: gameplay-engineer. UMG 수동 배치: 오너(§B 4단계). 수치: balance-designer(§7).
#projectTP/전투UI

---

## 0. 구현 우선순위 (오너 지시 2026-07-14 반영)

오너 지시: **"전투 메뉴만 리뉴얼, 나머지 HUD는 지금 그대로 이후 개선."** 이 spec.md 자체는 승인된 design_v2 전체를 다룬다(§C-1 "spec.md=전사 기준" 원칙상 화면 전체가 문서화 대상) — 아래 표는 **지금 UMG에 배치·배선할 범위**만 가른다. 2순위 항목도 토큰·바인딩 노트까지 이 문서에 이미 명세해뒀으므로, 착수 시 재설계 없이 바로 실행 가능하다.

| 우선순위 | 대상 | 처리 |
|---|---|---|
| **1순위(지금)** | `WBP_SkillMenu` + `WBP_SkillMenuRow`(전투 메뉴 세로 리스트) | §3-1·§3-2 상세 스펙대로 신규 배치 |
| **1순위(지금)** | `WBP_UnitFrame`(HP 유닛프레임, 8인스턴스) | §3-3 상세 스펙대로 신규 배치. **기존 F3 임시 HP(`HpGaugeText` — 액터 부착 월드공간 TextRenderComponent, `raw/F3_HP게이지_수정전스냅샷.md` 참고)를 대체** |
| 2순위(이후) | `WBP_TurnOrderBar`(턴순서 바) | §3-4 — 토큰만 선반영, 배치는 보류 |
| 2순위(이후) | `WBP_BerserkBadge`(광폭화 배지) | §3-5 — 토큰만 선반영 |
| 2순위(이후) | 상태이상 아이콘/태그(`Img_StatusIcon`/`Txt_StatusTag`) | **WBP_UnitFrame 자식으로 자리는 1순위에서 함께 배치**(§3-3, Collapsed 기본) 권장 — 바인딩만 2순위. §0-1 참고 |
| 2순위(이후) | `WBP_DamageNumber`(데미지/힐 부동숫자) | §3-6 — 토큰만 선반영 |
| 미분류(2순위에 준함, §6-5) | 타겟팅 커서(`WBP_TargetCursor`) | §3-7 — Director/오너 확인 요청(우선순위 리스트에 명시적 언급 없었음) |

### 0-1. "지금 배치, 나중 배선" 권장 (§B-2 배치 효율화 원칙 적용)

[[UI_화면_규약]] §B-2: "Claude가 골격을 일괄 생성 → 오너가 배치를 한 번에 몰아서 → Claude가 배선을 일괄." 이 원칙에 따라 **WBP_UnitFrame 위젯 트리 자체는 상태이상 아이콘/태그 자리까지 포함해 1순위에서 한 번에 배치**할 것을 권장한다(§3-3 트리 참고, `Img_StatusIcon`/`Txt_StatusTag`는 `Visibility=Collapsed` 기본값으로 배치만 해두고 이벤트 바인딩은 2순위로 미룸). 이렇게 하면 2순위 착수 시 오너가 UMG 디자이너를 다시 열어 자식 위젯을 **추가 배치**할 필요 없이 Claude가 바인딩만 하면 된다. **단, 이건 권장이지 강제 아님** — 오너가 1순위 범위를 문자 그대로 "HP+이름만"으로 최소화하고 싶다면 §3-3에서 해당 두 자식만 제외하고 배치해도 무방(2순위 시 재오픈 1회 필요해질 뿐, 구조는 동일).

---

## 1. 스코프 경계 (중요 — 착수 전 필독)

`design_v2.html`은 3D 씬을 컨텍스트로 함께 그리지만, **이 spec(UMG 대상)은 화면 오버레이 HUD 요소만이다.**

| 구분 | CSS 클래스 | 소관 |
|---|---|---|
| **이 spec 대상**(WBP_BattleHUD) | `.turn-order-bar` · `.berserk-badge` · `.unit-frame` · `.status-icon` · `.status-tag` · `.target-cursor` · `.floating-number` · `.command-box`(v2 세로 리스트) | system-ui-designer(이 문서) → gameplay-engineer 구현 |
| **비대상**(기존 3D 스프라이트 파이프라인, 이미 구현됨) | `.bg-sky`/`.bg-village`/`.bg-vignette`/`.bg-grain`/`.motes` · `.unit-sprite` · `.ground-shadow` · `.turn-mark` · `.head-arrow` | 옥토패스대치/기본전투무대 feature 소관, 무관 |

이 경계를 넘는 것 — 예: "unit-sprite도 UMG로 만들어야 하나?" — 는 **아니다**. 캐릭터 렌더링은 기존 BP_BattleSpawnPoint 3D 액터가 계속 담당한다.

---

## 2. 위젯 구조 제안 (전체)

```
WBP_BattleHUD  [루트, CanvasPanel — /Game/UI/Battle]
├─ Panel_TurnOrderBar        [WBP_TurnOrderBar 인스턴스]              (2순위)
├─ Panel_BerserkBadge        [WBP_BerserkBadge 인스턴스]              (2순위, Visibility 조건부)
├─ Panel_Battlefield         [CanvasPanel — 유닛프레임 8개의 부모 컨테이너]  ⚠(무효 — §6-4 재확정 참조)
│   ├─ UnitFrame_A1 … UnitFrame_A4   ×4  [WBP_UnitFrame 인스턴스]     (1순위)  ⚠(무효 — §6-4 재확정 참조)
│   └─ UnitFrame_B1 … UnitFrame_B4   ×4  [WBP_UnitFrame 인스턴스]     (1순위)  ⚠(무효 — §6-4 재확정 참조)
├─ Panel_FloatingNumbers     [CanvasPanel — 빈 컨테이너, 런타임 CreateWidget으로 WBP_DamageNumber 동적 추가/제거] (2순위)
├─ Panel_TargetCursor        [WBP_TargetCursor 인스턴스, 런타임 가시성 토글]  (미분류, §6-5)
└─ Menu_SkillMenu            [WBP_SkillMenu 인스턴스]                 (1순위)
```

신규 재사용 컴포넌트(`/Game/UI/Components`에 위치, [[UI_화면_규약]] §C-2):

| WBP | §E 상태 | 인스턴스 수 | 우선순위 |
|---|---|---|---|
| `WBP_UnitFrame` | §E "후보"로 이미 등재 — 이 문서가 정식 스펙 | 8(캔버스 배치) | 1순위 |
| `WBP_SkillMenu` | 신규(§E 미등재, 이 문서가 신설 제안) | 1 | 1순위 |
| `WBP_SkillMenuRow` | 신규(WBP_SkillMenu의 자식 컴포넌트) | 3(고정, §5-2 근거) | 1순위 |
| `WBP_TurnOrderBar` | 신규 | 1 | 2순위 |
| `WBP_BerserkBadge` | 신규 | 1 | 2순위 |
| `WBP_DamageNumber` | §E "후보"로 이미 등재 — 이 문서가 정식 스펙 | 0~N(동적 스폰) | 2순위 |
| `WBP_TargetCursor` | 신규 | 1(재사용, 위치만 이동) | 미분류 |

> **명명 확장 제안(확인 필요)**: [[네이밍_폴더_규약]] §9 위젯 트리 표에 `HorizontalBox`/`VerticalBox` 약어가 없다. 이 문서는 기존 패턴을 따라 `HBox_`/`VBox_`를 사용(예: `HBox_Hp`·`VBox_Frame`) — §9 확장 필요 시 별도 확인, 이 문서 저자가 §9 자체를 편집하지는 않음(스코프 밖).

---

## 3. 요소별 토큰표

공통 전제: 캔버스 기준 **1280×720**(design_v2 stage 크기), 좌표는 Anchor=(0,0)/Alignment=(0,0)/Position=(left,top) px 기준(달리 명시 없으면). **⚠ UMG DPI Scale/Reference Resolution 프로젝트 세팅이 1280×720 기준 1:1인지는 gameplay-engineer 확인 필요**(A0/기존 문서에 명시된 값 없음 — 이 spec의 모든 px 값은 "디자인 기준 px"이며 실제 UMG는 프로젝트 DPI 커브에 따라 스케일될 수 있음).

색상은 CSS 커스텀 프로퍼티(`--tp-*`, [[네이밍_폴더_규약]] §11)를 UMG `LinearColor`/hex로 표기. **블러(backdrop-filter)·이중 테두리·글로우 박스섀도우 등 장식 디테일은 UMG 기본 브러시로 완전 재현 불가** — 이 문서는 레이아웃 토큰까지만 책임지고, 시각 폴리시(그라디언트 브러시/9-slice/블러 근사)는 **hd2d-art-director·art-pipeline 협의 대상**으로 각 항목에 명시한다.

### 3-1. WBP_SkillMenu (1순위) — 전투 메뉴 컨테이너

design_v2 신규(v1의 가로 3카드 `command-box`를 대체). CSS 소스: `.command-box`(v2판, 우하단 세로 리스트).

| 항목 | 값 |
|---|---|
| 배치(Canvas Slot, WBP_BattleHUD 기준) | Anchor Min/Max=(1,1)/(1,1)(우하단 고정) · Alignment=(1,1) · Position=(-32,-24) — CSS `right:32px;bottom:24px` |
| Size | X=320(고정) · Y=Auto(Size To Content, 내부 VerticalBox가 콘텐츠에 맞춰 흐름) |
| 배경(`Border_Menu`) | 색 `--tp-panel-bg` = `#090B10` @ 84% alpha · 테두리 1px `#D4A657`(gold) @ 55% alpha · corner radius 10 |
| 내부 패딩(`VBox_Menu`) | top14 / left-right18 / bottom15 |
| 장식(4모서리 L자 골드 브래킷) | **폴리시 항목** — 1차 구현 생략 가능, art-pipeline 판단(9-slice 텍스처 권장) |

**자식 트리**:
```
WBP_SkillMenu [루트: CanvasPanel]
 └─ Border_Menu (Border, 배경+테두리+radius10)
     └─ VBox_Menu (VerticalBox, padding 14/18/15/18)
         ├─ HBox_Header (HorizontalBox, gap12)
         │   ├─ Border_Portrait (Border 42×42, radius8, 배경 black@35%, 테두리 1px gold)
         │   │    └─ Img_Portrait (Image — 행동 유닛 초상, §5 데이터 노트 참고)
         │   └─ VBox_HeaderText (VerticalBox)
         │       ├─ Txt_TurnLabel   ("턴" — 키 UI_BATTLE_TURN, §3-1a 폰트)
         │       └─ Txt_UnitName    (예: "전사 I" — §5 바인딩 노트 참고, 로컬라이즈 키 아님·조합 문자열)
         ├─ Border_Divider (1px, VBox margin 10/0/9/0, 색 --tp-panel-border-strong @ 30%, 그라디언트는 폴리시 항목)
         └─ VBox_SkillList (VerticalBox — WBP_SkillMenuRow 고정 3개 자식, §5-2 근거)
             ├─ Row_Skill0 [WBP_SkillMenuRow 인스턴스]
             ├─ Row_Skill1 [WBP_SkillMenuRow 인스턴스]
             └─ Row_Skill2 [WBP_SkillMenuRow 인스턴스]
```

**3-1a. 텍스트 토큰**:

| 위젯 | 폰트 | 크기 | 굵기 | 자간 | 색 | 문자열키/바인딩 |
|---|---|---|---|---|---|---|
| `Txt_TurnLabel` | Jost | 9px | 500(Medium) | 0.22em, 대문자 | `#E8C384`(gold-strong) | `UI_BATTLE_TURN`("턴") — ⚠ 턴순서바의 동일 키와 **폰트/크기 다름**(별개 위젯, §3-4 참고, 공유 아님) |
| `Txt_UnitName` | Cinzel | 16px | 600(SemiBold) | 0.03em | `#F4F1E9`(text) | 조합 문자열, §5 참고(로컬라이즈 키 아님) |

### 3-2. WBP_SkillMenuRow (1순위) — 스킬 리스트 행 (★가장 상세)

CSS 소스: `.skill-row-item`(+`.selected`/`.on-cooldown` 상태) + `.row-desc`(선택 시만 노출).

**행 전체는 클릭 가능 → UMG `Button`을 루트로 사용**(CSS `:hover` 상태 → Button의 Hovered 스타일로 대응, `cursor:pointer` → Button 기본 동작).

```
WBP_SkillMenuRow [루트: VerticalBox]
 ├─ Btn_Row (Button — 전체 행, Normal=투명·Hover=rgba(255,255,255,0.04)·Disabled=아래 표)
 │   └─ Overlay_RowContent (Overlay)
 │       ├─ Border_SelectedBg (Border, 전체 채움 — Visibility: bSelected일 때만 Visible)
 │       │     배경: 골드 그라디언트 근사(gradient 90deg rgba(212,166,87,0.20)→rgba(212,166,87,0.05)) — **폴리시 항목**, 1차는 단색 rgba(212,166,87,0.12) 근사 허용
 │       ├─ HBox_RowContent (HorizontalBox, padding top7/right8/bottom7/left20, gap8)
 │       │   ├─ Img_RowIcon   (Image, 18×18 — 스킬 아이콘, §5 바인딩 노트)
 │       │   ├─ Txt_RowName   (TextBlock — 스킬명, §3-2a)
 │       │   ├─ Spacer_Leader (Spacer 또는 Fill-slot 빈 위젯 — CSS 점선 리더 라인, **폴리시 항목**, 생략 가능)
 │       │   └─ Txt_RowCd     (TextBlock — 쿨다운, §3-2a, Visibility: CooldownTurns==0인 스킬은 Collapsed)
 │       └─ Img_RowCursor (Image — "▶" 삼각 커서, Anchor 좌측중앙, Visibility: bSelected일 때만 Visible)
 └─ HBox_Desc (HorizontalBox, margin top2/right0/bottom5/left20 — Visibility: bSelected일 때만 Visible)
     ├─ Border_DescAccent (Border, width2px, 색 rgba(212,166,87,0.45), VerticalAlignment=Fill)
     └─ Txt_RowDesc (TextBlock, padding-left8, wrap=true — §3-2a)
```

**3-2a. 텍스트/색 토큰**:

| 위젯 | 폰트 | 크기 | 굵기 | 색(기본) | 색(선택 시) | 색(쿨다운 중) |
|---|---|---|---|---|---|---|
| `Txt_RowName` | Jost | 13px | 500 | `#F4F1E9`(text) | `#E8C384`(gold-strong)+굵기600 | 동일(투명도만 하강, 아래) |
| `Txt_RowCd` | Jost | 11px | 600 | `rgba(244,241,233,0.56)`(text-muted) | `#E8C384`(gold-strong) | `#E2534F`(crimson-strong) |
| `Txt_RowDesc` | Jost | 10.5px | 300(Light) | `rgba(244,241,233,0.56)`(text-muted) | — | — |
| `Img_RowIcon` | — | 18×18 | — | `rgba(244,241,233,0.56)`(text-muted) tint | `#E8C384`(gold-strong) tint | — |

**행 전체 RenderOpacity**: 기본 1.0 · `bOnCooldown=true`일 때 0.46(CSS `.on-cooldown{opacity:.46}`) · 이때 `Btn_Row.IsEnabled=false`(클릭·hover 무효화 동시 처리).

**문자열키**: `Txt_RowName`/`Txt_RowDesc`는 **UI_BATTLE_* 키가 아니라 `DT_Skills.NameKey`/`DescKey` 동적 바인딩** — §4-2·§5 참고(중요, 착수 전 필독).

**쿨다운 포맷**: `UI_BATTLE_COOLDOWN_FORMAT` = `"CD {0}"`, `{0}` 값의 의미는 §6-1 엣지케이스 참고(확인 필요 항목).

### 3-3. WBP_UnitFrame (1순위) — HP 유닛프레임 (★가장 상세)

CSS 소스: `.unit-frame`(+`.ally`/`.enemy`) + `.status-icon` + `.status-tag`. **8개 인스턴스**(A1~A4 아군, B1~B4 적), `bIsAlly`(bool, 인스턴스별 Exposed 변수)로 스타일 분기.

```
WBP_UnitFrame [루트: CanvasPanel]
 └─ Panel_Root (CanvasPanel, anchor fill)
     ├─ Border_Frame (Border, anchor fill — 배경 --tp-panel-bg, 테두리/radius는 bIsAlly로 분기 §3-3b)
     │   └─ VBox_Frame (VerticalBox — padding은 §3-3b)
     │       ├─ Txt_Name        (TextBlock — Visibility: bIsAlly?Visible:Collapsed) ⚠**삭제됨**(아래 노트 참고)
     │       ├─ HBox_Hp         (HorizontalBox, gap6)
     │       │    ├─ Bar_Hp      (ProgressBar — height7, radius4, 배경 rgba(0,0,0,0.5))
     │       │    └─ Txt_HpValue (TextBlock — "90/90") ⚠**삭제됨**(아래 노트 참고)
     │       └─ Txt_StatusTag   (TextBlock — §0-1 권장: 1순위에 자리만 배치, Visibility=Collapsed 기본)
     └─ Img_StatusIcon (Image, 20×20 원형 — Anchor=(1,0), Position≈(+8,-8)(모서리 오버랩) — §0-1 권장: 1순위에 자리만 배치, Visibility=Collapsed 기본)
```

> **✅ 구현 반영(오너 간소화 지시, 2026-07-15)**: "정보가 많아서 간소화" — 최종 구현은 `Txt_Name`·`Txt_HpValue` 위젯을 **삭제**했고 `Border_Frame` 배경도 투명화(BrushColor Alpha=0)했다. **현재 화면에 표시되는 것은 `Bar_Hp`(HP 게이지 막대) 하나뿐**이다. `Txt_StatusTag`/`Img_StatusIcon`(2순위 예약, Collapsed)은 위 트리 그대로 보존됐다. 상세: [[U단계_HP게이지_UMG_실장]].

**3-3a. 8인스턴스 배치(design_v2 좌표 그대로, §6-4 위치추적 방식 확인 필요와 함께 읽을 것)**:

| 인스턴스명(제안) | 목업 라벨 | Front/Back | 위치(X,Y) | 변형 |
|---|---|---|---|---|
| `UnitFrame_A1` | 전사 I | front, current | (150,358) | — |
| `UnitFrame_A2` | 마법사 I | front | (300,328) | — |
| `UnitFrame_A3` | 전사 II | back | (195,187) | RenderTransform Scale=0.82, Pivot=(0.5,0.0) |
| `UnitFrame_A4` | 마법사 II | back | (70,212) | RenderTransform Scale=0.82, Pivot=(0.5,0.0) |
| `UnitFrame_B1` | (적, 이름 비표시) | front | (1010,358) | — |
| `UnitFrame_B2` | (적) | front | (860,328) | — |
| `UnitFrame_B3` | (적) | back | (965,187) | RenderTransform Scale=0.82, Pivot=(0.5,0.0) |
| `UnitFrame_B4` | (적) | back | (1090,212) | RenderTransform Scale=0.82, Pivot=(0.5,0.0) |

> **⚠ 슬롯↔실제 SpawnPoint 대응 미확정**: 위 인스턴스명(A1~A4/B1~B4)은 목업의 시각 배치(앞줄/뒷줄, 전사/마법사) 기준 **추정 매핑**이다. F0③ 배정표(A1/A2=전사, A3/A4=마법사)와 목업의 "전사I(앞)/전사II(뒤)" 라벨이 정확히 어느 SpawnPoint 인스턴스에 대응하는지는 **scene-builder/gameplay-engineer 확인 필요**(3D 스폰 좌표와 이 HUD 좌표는 별도 시스템 — §6-4).

**3-3b. 변형별 스타일(bIsAlly 분기)**:

| 항목 | Ally | Enemy |
|---|---|---|
| `Border_Frame` Size X | 110 | 92 |
| `VBox_Frame` padding | top8/right10/left10/bottom7 | top6/right8/left8/bottom6 |
| `Border_Frame` 테두리 | 1px `#D4A657` @ 55% | 1px `#C7D5EB` @ 20% |
| `Border_Frame` radius | 6 | 6 |
| `Txt_Name` Visibility | Visible | Collapsed(적은 이름 비표시 — 목업 그대로) |
| `Bar_Hp` Fill 색 | 그라디언트 `#B8863C→#E8C384`(폴리시 항목, 1차 단색 `#E8C384` 근사) | 그라디언트 `#3D9A31→#8FE06A`(폴리시 항목, 1차 단색 `#8FE06A` 근사) |
| 이중 테두리/하단 크림슨 언더라인 장식 | **폴리시 항목**(hd2d-art-director 판단, 생략 가능) | 상동 |
| 현재 턴 강조(`bIsCurrentTurn`) | 외곽 글로우 `0 0 0 1px gold, 0 0 24px gold@55%` — **폴리시 항목**(UMG Border 커스텀 브러시/머티리얼 필요), 1차는 테두리색만 gold로 강조 가능 | (적은 자기 턴 강조 로직 없음) |

**3-3c. 텍스트 토큰**:

| 위젯 | 폰트 | 크기 | 굵기 | 자간 | 색 |
|---|---|---|---|---|---|
| `Txt_Name` | Jost | 10.5px | 500 | 0.04em | `rgba(244,241,233,0.56)`(text-muted) |
| `Txt_HpValue` | Jost | 10px | 600 | tabular-nums(⚠ UMG 폰트 feature 미지원 시 생략 가능, 폴리시 항목) | `#F4F1E9`(text) |
| `Txt_StatusTag`(2순위) | Jost | 8px | 400 | 0.03em | 상태별: 공격력약화=`#FFD3CF` on `rgba(194,75,68,0.30)` / 기절=`#FBF0B8` on `rgba(232,217,122,0.24)` |

**3-3d. `Txt_HpValue` 폭 안전마진**: 현재 목업 값은 2자리("90/90"/"48/90") 기준. balance가 향후 3자리 HP(100+)를 도입하면 TextBlock 폭이 부족할 수 있음 — Auto-size 또는 여유폭 권장(경고성 노트, 지금 조치 불요).

### 3-4. WBP_TurnOrderBar (2순위 — 토큰만 선반영)

CSS 소스: `.turn-order-bar`(+`.turn-chip` 8개). 배치: Anchor=(0.5,0)/Alignment=(0.5,0)/Position=(0,18)(상단 중앙). Size: Auto(내부 HorizontalBox). 배경 `--tp-panel-bg`, 테두리 1px gold@45%, radius 999(pill).

| 위젯 | 내용 |
|---|---|
| `Txt_TurnLabel` | "턴" — Cinzel 13px 600, 0.16em, 대문자, 색 `#E8C384`. **키 `UI_BATTLE_TURN` 재사용(§3-1a와 동일 키, 다른 폰트/크기 — 공유 위젯 아님, 주의)** |
| `Txt_TurnNum` | TurnCounter 값(예: "31") — Cinzel(부모 상속) 13px, 색 `#F4F1E9`, tabular-nums. **로컬라이즈 대상 아님**(런타임 숫자) |
| `HBox_Chips` | `Img_Chip`×8(또는 향후 `WBP_TurnChip` 서브컴포넌트로 재분해 가능, 지금은 강제 안 함) — ally=골드 다이아, enemy=크림슨 다이아, current=36×36 확대+골드 글로우(폴리시 항목) |

### 3-5. WBP_BerserkBadge (2순위 — 토큰만 선반영)

CSS 소스: `.berserk-badge`. 배치: Anchor=(1,0)/Alignment=(1,0)/Position=(-34,20). Visibility: `TurnCounter > 30`일 때만 Visible(그 외 Collapsed). 배경 크림슨 그라디언트(폴리시 항목, 단색 `rgba(56,14,14,0.88)` 근사 가능), 테두리 1px `rgba(226,90,79,0.55)`, radius6.

| 위젯 | 내용 |
|---|---|
| `Txt_BerserkMain` | `GetLocalizedString(UI_BATTLE_BERSERK)` + `" T" + TurnCounter` 문자열 결합(둘 다 동색이라 TextBlock 1개로 처리 가능) — Cinzel 12.5px 700, 0.06em, 대문자, 색 `#FFDCCF` |
| `Txt_BerserkBonus` | `"+" + Round((BerserkMult-1)*100) + "%"` — Cinzel(상속) 700, 색 `#E2534F`(crimson-strong). **BerserkMult 공식은 balance 소관**([[광폭화_재검증]] §7, `1+0.05×max(0,TurnCounter-30)`) — UI는 표시만, §7 참고 |

### 3-6. WBP_DamageNumber (2순위 — 토큰만 선반영)

CSS 소스: `.floating-number`(+`.dmg`/`.heal`). 런타임 `CreateWidget`으로 대상 유닛 위치 근처에 동적 스폰, 애니메이션 종료 후 자동 제거(`RemoveFromParent`).

| 항목 | 값 |
|---|---|
| `Txt_Amount` | Jost, 22px, 700(Bold), tabular-nums. 색: 피해=`#FF6B62` / 회복=`#8FE06A` |
| 텍스트 포맷 | 피해="-{amount}", 회복="+{amount}" — **숫자 부호는 로컬라이즈 대상 아님**, 순수 포맷 |
| 애니메이션 | Translate Y: +10→0→-26→-36px, Opacity: 0→1→1→0, Scale: 0.85→1→1→0.95, 총 2.4s(`WidgetAnimation`으로 CSS `@keyframes floatUp` 재현) |
| 스폰 위치 | 대상 `WBP_UnitFrame` 상단 기준 Y-30px(§6-4 위치추적 방식과 연동) |

### 3-7. WBP_TargetCursor + 기타 미분류 요소 (§6-5 확인 필요)

CSS 소스: `.target-cursor`(다이아몬드+"타겟" 캡션). 유효 타겟 하이라이트 시(`EnterAwaitTarget` 상태) 마우스 호버/포커스된 유닛 위 -34px에 표시.

| 위젯 | 내용 |
|---|---|
| `Img_Diamond` | 13×13, 회전45°, 색 `#E2534F`(crimson-strong) |
| `Txt_TargetCaption` | "타겟" — Jost 8.5px 600, 0.18em, 대문자, 색 `#FFB4AE` on `rgba(9,11,16,0.75)`. 키 `UI_BATTLE_TARGET` |

> `.head-arrow`(머리 위 화살표, v2 신규)·`.turn-mark`(지면 다이아)는 §1 스코프 경계상 **3D 스프라이트 파이프라인 소관**(WBP 아님) — 이 문서 대상 아님, 재확인용으로만 언급.

---

## 4. 문자열 키 목록

### 4-1. `UI_BATTLE_*` 신규 등록 대상 (strings.csv/DT_Strings, 하드코딩 금지)

design_v2 HTML 주석 기준 12종. 아래 표는 **실제로 `UI_BATTLE_*` 네임스페이스에 신규 등록해야 하는 키만** 추린 것(§4-2에서 제외되는 4종은 여기 없음).

> **✅ 확정 반영(gameplay-engineer, 2026-07-14, WBP 골격 생성 세션)**: 아래 6종 전부 `data/strings.csv` + `DT_Strings`에 등록 완료(ko값 기입, ja/en은 기존 관행대로 공란). 이중등록 없음(§4-2의 6종은 `Skill.*`/`Job.*` 기등록 재사용, 신규 등록 안 함) — 확인은 `DataTableTools.get_rows`로 실측.

| 키 | 용도 | 위젯 | ko 값(목업 기준) |
|---|---|---|---|
| `UI_BATTLE_TURN` | "턴" 라벨 | `Txt_TurnLabel`(턴순서바+메뉴헤더, 2곳 재사용) | 턴 |
| `UI_BATTLE_BERSERK` | 광폭화 라벨 | `Txt_BerserkMain` | 광폭화 |
| `UI_BATTLE_TARGET` | 타겟 캡션 | `Txt_TargetCaption` | 타겟 |
| `UI_BATTLE_STATUS_ATK_DOWN` | 상태이상 태그 | `Txt_StatusTag`(atk-down) | 공격력약화 |
| `UI_BATTLE_STATUS_STUN` | 상태이상 태그 | `Txt_StatusTag`(stun) | 기절 |
| `UI_BATTLE_COOLDOWN_FORMAT` | 쿨다운 포맷 문자열 | `Txt_RowCd` | "CD {0}" |

### 4-2. ⚠ 중요 정정 — 나머지 6종은 `UI_BATTLE_*`가 아니라 기존 콘텐츠 키 재사용

design_v2 목업 HTML 주석은 아래 6개도 `UI_BATTLE_*`로 표기했지만(§G의 예시 문구도 동일 — `UI_BATTLE_ATTACK` 등), **실제로는 이미 [[전투완성]] F2 데이터 파이프라인이 `Skill.*`/`Job.*` 네임스페이스로 `strings.csv`(→`DT_Strings`)에 등록·검증 완료된 값들이다**(`data/skills.csv`·`data/strings.csv` 실측 확인). 동일 문자열을 두 키로 이중 관리하면 번역 드리프트가 생기므로, **`UI_BATTLE_*`로 신규 등록하지 말고 기존 키를 그대로 바인딩**할 것:

| 목업 주석 키(오표기) | 실제 사용할 키 | 현재 strings.csv 값 |
|---|---|---|
| `UI_BATTLE_ROLE_WARRIOR` | `Job.Warrior` | 전사 |
| `UI_BATTLE_ROLE_MAGE` | `Job.Mage` | 마법사 |
| `UI_BATTLE_ATTACK` | `Skill.Attack` | 공격 |
| `UI_BATTLE_SLASH` | `Skill.Slash` | 베기 |
| `UI_BATTLE_GUARD` | `Skill.Block` | 막기 |
| `UI_BATTLE_SKILL_DESC_SLASH` | `Skill.Slash.Desc` | 대상에게 공격력의 130퍼센트 물리 피해. 쿨다운 1턴. |

> **주의**: `Skill.Slash.Desc`의 실제 등록 값("대상에게 공격력의 130퍼센트 물리 피해. 쿨다운 1턴.")은 목업 표시 텍스트("적에게 강한 물리 피해(강타)")와 **문구가 다르다**(목업이 짧은 flavor-text, 실데이터는 수치 설명형). SSOT는 strings.csv이므로 **실제 UMG 화면은 목업과 다른(더 긴) 설명 문구가 뜨는 게 정상**이다 — 결과물이 목업과 픽셀 다르다고 버그로 오인하지 말 것. 문구 톤을 맞추고 싶으면 balance-designer가 strings.csv 값을 수정(이 문서 소관 아님).
>
> **[[UI_화면_규약]] §G 예시 문구 관련**: §G의 BattleHUD 스타터 키 예시("`UI_BATTLE_SKILL`·`UI_BATTLE_ATTACK`" 등)는 §G 원문이 "정식 목록은 전투 HUD 명세에서 표준화"라고 스스로 위임한 자리다 — 이 문서(§4)가 그 표준화이며, 위 정정이 우선한다. §G 원문 문구 자체를 고치는 건 이 문서 스코프 밖(Director 확인 시 별도 편집).

### 4-3. `UI_BATTLE_SKILL` 폐기 (v1→v2)

v1의 스킬 섹션 킥커 `UI_BATTLE_SKILL`("스킬")은 v2에서 리스트 헤더가 캐릭터명(`Txt_UnitName`)으로 대체되며 삭제됨 — **신규 등록 불요**, 이미 v1에서만 쓰이던 키이므로 strings.csv에 아직 없다면 등록하지 않는다.

---

## 5. 데이터 바인딩 노트

실제 배선(§B 5단계, 이벤트그래프/바인딩)은 이후 MCP 작업 — 아래는 **"무엇을 무엇에 바인딩할지"의 사전 명세**.

| 위젯 | 바인딩 소스 | 갱신 트리거(권장) |
|---|---|---|
| `WBP_UnitFrame.Txt_Name` | `GetLocalizedString(Job.<JobName>)` + `" " + 로마숫자(동일직업 내 순번)` — ⚠ 로마숫자(I/II)는 로컬라이즈 키 아님, 동일 Job 유닛 구분용 서수 포맷 로직(§6-2 확인 필요) | 유닛 스폰 시 1회 |
| `WBP_UnitFrame.Bar_Hp` / `Txt_HpValue` | `Unit.Hp` / `Unit.MaxHp`(F3에서 이미 로드된 액터 멤버 변수, `DT_JobStats` 기원) | `TakeHit` 결과 반영 시(이벤트 기반 권장, Tick 폴링 지양) |
| `WBP_UnitFrame` 위치(Canvas Slot Position) | 유닛의 3D 월드 위치 → `Project World To Screen Location` | §6-4 참고(정적 vs 동적 확인 필요) — ⚠(무효 — §6-4 재확정 참조) |
| `WBP_UnitFrame.Txt_StatusTag`/`Img_StatusIcon`(2순위) | `Unit.ActiveStatuses[0]`(`F_ActiveStatus`: statusToken/value/remainingTurns) | 상태 APPLY/EXPIRE 시(`StatusLog` 이벤트) |
| `WBP_SkillMenu.HBox_Header` | 현재 `ActiveUnit`(AwaitCommand 상태의 행동 유닛) | 턴 전환 시(`EnterAwaitCommand` 진입) |
| `WBP_SkillMenu` 전체 Visibility | `BattleState == AwaitCommand`일 때만 Visible, 그 외(`AwaitTarget`/`Executing`/상대 턴) Collapsed 또는 Hit-Test Invisible | 상태 전이마다 |
| `Row_Skill0~2` (`WBP_SkillMenuRow`×3) | `ActiveUnit.SkillIds`(";"분리) → `ParseIntoArray(";")` → 인덱스 0~2 → `GetDataTableRow(DT_Skills, SkillId)` | `EnterAwaitCommand` 진입 시(기존 F7 §7-2 슬롯 재바인딩 로직과 동일 패턴 재사용) |
| `Row.bOnCooldown`(Btn_Row.IsEnabled 역) | `GetSkillCooldown(ActiveUnit, SkillId) == 0 AND 유효타겟 ≥ 1`(F7 §7-2 `bEnabled` 공식 그대로) | 상동 |
| `Row.Btn_Row` OnClicked | `NotifySkillSelected(SkillId)` 호출만(로직 없음 — F7 §7-1 아키텍처 제약: "타겟킨드 해석·유효타겟풀 계산은 전부 BP_BattleManager 소유") | 클릭 시 |
| `Row.Txt_RowName`/`Txt_RowDesc` | `GetLocalizedString(Skill.NameKey)` / `GetLocalizedString(Skill.DescKey)` — §4-2 참고, `UI_BATTLE_*` 아님 | 상동 |
| `Row.Txt_RowCd` | §6-1 확인 필요(정의값 vs 잔여값) | 자기 턴 시작마다(쿨다운 스윕) |
| `WBP_BerserkBadge` Visibility/텍스트 | `TurnCounter`(기존 변수, [[전투완성/plan]] F1 §확정: 유닛턴 카운트) | 매 턴(`EnterTurnEnd` §5-2) |
| `WBP_DamageNumber` 스폰 | `TakeHit` 결과의 `LogDmg`(피해 양수/회복 음수/막기 0 — 부호 규약은 [[전투완성/plan]] §4-3) | `TakeHit` 호출 직후 |

---

## 6. 엣지케이스 / 확인 필요 사항

방어적 설계 원칙에 따라 미리 명시(qa-critic 후속 검증 대상, 여기서는 1차 식별).

| # | 항목 | 내용 | 권장(잠정) |
|---|---|---|---|
| 6-1 | **`row-cd` 숫자의 의미** | 목업은 "베기"(사용가능, CD1)와 "막기"(쿨다운중, CD2) 둘 다 `DT_Skills.CooldownTurns` 정의값과 정확히 일치하는 숫자를 보여줌 — 스냅샷만으론 "정의값 상시표시"와 "잔여값표시"가 구분 안 됨(막 사용 직후엔 둘이 같은 값이라서). **권장**: 사용 가능(쿨다운 0) 상태면 `DT_Skills.CooldownTurns`(정의/예고값), 쿨다운 중이면 `GetSkillCooldown(unit,skillId)`(실제 잔여값) 표시 — 플레이어에게 더 유용. **✅ 확정(gameplay-engineer, 2026-07-14)**: 권장안 그대로 채택. `WBP_SkillMenuRow.SetCooldown(CooldownText, bInOnCooldown)` 골격에서 값 산출(정의값 vs 잔여값 분기)은 **호출부**(`WBP_SkillMenu`의 행 리바인드 로직, §B 5단계 배선 시 구현) 책임으로 설계 — Row는 이미 포맷된 텍스트만 받는다. |
| 6-2 | **동일 Job 중복 유닛 표기(전사 I/II)** | "I"/"II" 로마숫자는 어느 필드에서 오는가 — 현재 DT_JobStats/스폰 로직에 순번 필드 없음(F0③ 배정표는 JobId만 규정). UI 표시용 파생 로직(같은 팀 내 동일 Job 등장 순서로 서수 계산) 신설 필요 — 로컬라이즈 키가 아니라 **표시 로직**임을 gameplay-engineer 확인 요청. |
| 6-3 | **기본 선택 행(메뉴 오픈 시 커서 위치)** | 목업은 "베기"(2번째 행)가 기본 선택 상태로 그려짐 — 우연인지 의도인지 불명. **권장**: 메뉴 오픈 시 기본 선택 = 첫 번째 사용 가능(쿨다운 0 & 유효타겟 有) 스킬 행. 첫 스킬(공격)은 CooldownTurns=0 고정이라 "전부 쿨다운 중" 엣지는 발생 안 함(안전). UX 확정은 qa-critic/오너 확인 요청. |
| 6-4 | **WBP_UnitFrame 위치추적 방식(정적 vs 동적) — ★설계 결정 필요** | 기존 F3 임시 HP(`HpGaugeText`)는 **액터 부착 월드공간**이라 카메라 상태(DefaultCamera/ActionCam 근접컷)와 무관하게 항상 유닛 위에 붙어 있다. 이 문서 §3-3a의 좌표(예: A1=150,358)는 design_v2 목업의 **정적 스냅샷**일 뿐이다. WBP_BattleHUD를 CanvasPanel 화면 오버레이로 만들면서 위치를 고정 px로 박으면, ActionCam 근접컷 등 카메라 변화 시 유닛과 프레임이 어긋나는 **회귀** 가능성이 있다([[전투완성/plan]] F3 TC-F3-04가 이미 이 이슈로 "부분 PASS·이월"). **권장**: `Project World To Screen Location`으로 매 틱(또는 카메라 전환/유닛 이동 이벤트 시)마다 각 `UnitFrame_*`의 Canvas Slot Position을 갱신 — §3-3a 좌표는 기본 카메라 기준 참고값으로만 사용. **✅ 확정(gameplay-engineer, 2026-07-14)**: 권장안(동적 PWTS) 채택. 골격 단계에서 훅 포인트 선배치 — `WBP_UnitFrame.UpdateScreenPosition(WorldLocation: Vector)`(자기 Slot을 CanvasPanelSlot으로 캐스트해 Position 갱신, self-contained) + `WBP_BattleHUD.RefreshAllUnitFramePositions()`(오너가 8개 UnitFrame을 배치해 `UnitFrame_A1~B4` 변수가 생긴 뒤 루프 구현, §B 5단계). Tick 기반이냐 카메라 전환 이벤트 기반이냐(성능 트레이드오프)는 5단계 구현 시 확정. **재확정(Director, 2026-07-14 U-v5)**: 동적 PWTS 폐기 → per-unit WidgetComponent(Space=Screen) 채택. `BP_BattleSpawnPoint.HpGaugeWidget`(F3b)의 widgetClass를 `WBP_UnitFrame_C`로 교체; 위치추적·카메라정면·off-screen클램프는 엔진 보장, 골격 스텁 삭제(死코드0). → §2 Panel_Battlefield 8-UnitFrame 자식 및 §5 "WBP_UnitFrame 위치←PWTS" 행은 무효(UnitFrame은 HUD캔버스 밖 액터별 WidgetComponent 거주; 데미지숫자·타겟커서의 프레임기준 위치는 액터 월드위치 PWTS로 재귀속). **구현 완료(2026-07-15, U단계)**: ProjectWorldToScreen 동적 갱신 방식은 최종 미채택 — WidgetComponent(Screen space) 단일 경로로 확정 구현됐다. 위치추적·빌보드는 엔진이 보장해 별도 Tick 갱신 로직이 불요함을 실증했고, 스텁 `WBP_UnitFrame.UpdateScreenPosition`·`WBP_BattleHUD.RefreshAllUnitFramePositions`는 삭제 완료. 상세: [[U단계_HP게이지_UMG_실장]]. |
| 6-5 | **미분류 요소 우선순위 귀속** | 오너 지시의 2순위 리스트(턴순서바/광폭화배지/상태이상아이콘/데미지부동숫자)에 `WBP_TargetCursor`·머리위화살표·지면다이아가 명시적으로 없음. 이 문서는 TargetCursor를 "2순위에 준함"으로 잠정 분류(§0 표) — **Director/오너 확인 요청**, 다른 처리를 원하면 정정. |
| 6-6 | **동시 다중 상태이상 아이콘 슬롯 1개 한정** | 목업은 유닛당 상태이상 아이콘 슬롯 1개만 설계(`Img_StatusIcon` 단수). 한 유닛이 STUN+ATK_DOWN을 동시에 가질 수 있는지는 [[상태이상_확정]](상태이상 SSOT) 확인 필요 — 가능하다면 아이콘 다중표시(가로나열) 또는 우선순위 1개만 표시 중 선택 필요. **2순위 착수 시** balance-designer/qa-critic 확인 요청(지금 결정 불요). |
| 6-7 | **전투 메뉴와 전열 적 프레임 겹침(v2 자체 인지 사항)** | design_v2 spec-note 원문: 우하단 이동한 메뉴가 전열 적 유닛(x:1010~1102) 상단과 세로 약 16px 내외 겹칠 수 있음 — 반투명+z-index로 가독성 문제는 없다고 판단되나, UMG 구현 시 실측 재확인 권장(§3-1 Position 확정 후 `UnitFrame_B1` 실제 렌더 위치와 겹침 여부 재확인). |

---

## 7. 수치 스키마 참조 (balance-designer)

이 화면이 필요로 하는 수치는 **이미 [[전투완성]] F2 데이터 파이프라인에 존재** — 신규 수치 작업 불요, 아래는 이 화면이 소비하는 필드의 참조 매핑표(변경 시 이 화면도 영향받음을 인지용).

| 이 화면이 읽는 값 | 출처 | 타입/범위 |
|---|---|---|
| `Unit.Hp` / `Unit.MaxHp` | `DT_JobStats.Hp`(액터 로드값) | Integer, 현재 6행(72~113 관측) |
| 스킬 CooldownTurns | `DT_Skills.CooldownTurns` | Integer, 0~3 관측(공격0/베기1/파이어볼2/막기2/치유3) |
| 스킬 잔여 쿨다운 | `GetSkillCooldown(unit, skillId)` 런타임 함수 | Integer, 0~CooldownTurns |
| 광폭화 배율 | `BerserkMult = 1+0.05×max(0,TurnCounter−30)` | Float, [[광폭화_재검증]] §7 SSOT |
| 데미지/힐 표시값 | `TakeHit`의 `LogDmg`(부호규약: 피해+/회복-/막기0) | Integer, [[전투완성/plan]] §4-3 |
| 상태이상 잔여턴 | `F_ActiveStatus.remainingTurns` | Integer, [[상태이상_확정]] SSOT |

이 화면 스펙 작성 중 **신규로 필요해진 값은 없음**(전부 기존 F2/F1 산출물로 커버됨). 단 §6-1(쿨다운 표시 의미)이 balance 쪽 "쿨다운 표시 정책" 결정에 해당한다면 balance-designer도 확인 대상.

---

## 관련 문서
[[UI_화면_규약]] · [[네이밍_폴더_규약]] · [[전투완성/청사진]] · [[전투완성/plan]] · [[광폭화_재검증]] · [[상태이상_확정]] · [[projectTP_허브]]
