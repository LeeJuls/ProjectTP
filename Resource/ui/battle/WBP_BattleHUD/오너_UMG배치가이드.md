---
type: guide
project: projectTP
screen: WBP_BattleHUD
updated: 2026-07-14
status: 1순위 골격(WBP_BattleHUD/WBP_UnitFrame/WBP_SkillMenu/WBP_SkillMenuRow) 생성 완료 — 오너 배치 대기
---

# WBP_BattleHUD 오너 UMG 배치 가이드 (§B 4단계)

> 대상 문서: [[spec]](`spec.md`) §3(위젯트리 토큰표). 이 가이드는 spec §3을 **클릭 단위**로 옮긴 것 — 값이 다르면 spec.md가 기준.
> [[UI_화면_규약]] §B-2 원칙: "Claude가 골격 일괄 생성 → 오너가 배치를 한 번에 몰아서 → Claude가 배선 일괄." 이 가이드는 4개 WBP를 **한 번에 몰아서** 처리하도록 순서를 정리했다.
> **배치만 하면 된다.** 로직 연결(OnClicked 핸들러, 텍스트 바인딩 등)은 이 단계에서 안 함 — §B 5단계(배선)에서 Claude가 처리.

---

## 0. 시작 전 확인 (1회)

1. UE 에디터에서 콘텐츠 브라우저 `/Game/UI/Components/`와 `/Game/UI/Battle/`에 아래 4개 애셋이 이미 존재하는지 확인(gameplay-engineer가 골격 생성 완료):
   `WBP_UnitFrame`, `WBP_SkillMenu`, `WBP_SkillMenuRow`(이상 `Components/`), `WBP_BattleHUD`(`Battle/`).
2. **폰트 사전 점검**: spec은 `Jost`(본문)·`Cinzel`(제목류) 폰트를 지정한다. 프로젝트에 두 폰트 애셋이 이미 임포트돼 있는지 Font 드롭다운에서 확인 — 없으면 우선 프로젝트 기본 폰트로 배치하고 폰트만 나중에 일괄 교체해도 된다(레이아웃에 지장 없음). 폰트 임포트 자체가 필요하면 art-pipeline 확인 요청.
3. **"Is Variable" 체크 규칙**: 아래 목록에서 이름이 지정된 위젯은 전부 계층(Hierarchy) 패널에서 이름을 정확히(대소문자 포함) 입력하고, Details 패널 상단의 **"Is Variable" 체크박스를 켠다.** 나중 배선 단계가 이 이름으로 위젯을 직접 참조하므로 **오타·이름 불일치가 나면 배선이 실패한다.** [Is Variable: OFF]로 표시된 항목만 꺼도 되는(순수 장식) 위젯.
4. **작업 순서**(자식이 필요한 부모를 먼저 완성해야 팔레트에서 미리보기가 됨): ① `WBP_SkillMenuRow` → ② `WBP_UnitFrame` → ③ `WBP_SkillMenu`(①의 인스턴스 3개 배치) → ④ `WBP_BattleHUD`(②③의 인스턴스 배치).
5. 각 WBP 배치를 마칠 때마다 **컴파일(Compile) 버튼 클릭 + 저장(Ctrl+S)** — 다음 WBP에서 인스턴스로 쓰려면 먼저 컴파일돼 있어야 팔레트에 정상 반영된다.
6. **UMG 참고**: `HorizontalBox`/`VerticalBox`엔 CSS의 `gap` 같은 속성이 없다 — 자식들 사이 간격은 각 자식의 Slot **Padding**(예: 첫 자식 제외 왼쪽에 gap만큼 Padding)으로 흉내낸다. 아래 가이드에서 "gapN"이라 적은 곳은 이 방식으로 처리.

---

## 1. `WBP_SkillMenuRow` (`/Game/UI/Components/WBP_SkillMenuRow`)

**루트 교체**: 기본 생성된 `CanvasPanel [Root]`를 계층 패널에서 삭제하고, 팔레트에서 `Vertical Box`를 드래그해 새 루트로 만든다.

| # | 이름 | 타입 | 부모 | 배치 세부 | Is Variable |
|---|---|---|---|---|---|
| 0 | (루트) | VerticalBox | — | 위 "루트 교체" 참고 | — |
| 1 | `Btn_Row` | Button | 루트 | Style: Normal=투명, Hovered=`rgba(255,255,255,0.04)`. (Disabled 스타일은 그대로 둬도 됨 — 쿨다운 시 0.46 dim은 행 전체 RenderOpacity로 처리, 배선 단계) | **ON** |
| 2 | `Overlay_RowContent` | Overlay | `Btn_Row` | Fill | ON |
| 3 | `Border_SelectedBg` | Border | `Overlay_RowContent` | Overlay 내 Horizontal/Vertical Alignment=Fill. 배경 `rgba(212,166,87,0.12)`(단색 1차 근사 — 그라디언트는 폴리시 항목, hd2d-art-director 협의). **Visibility=Collapsed**(기본값, bSelected 시에만 Visible — 배선단계에서 토글) | ON |
| 4 | `HBox_RowContent` | HorizontalBox | `Overlay_RowContent` | Overlay 내 Alignment=Fill. Padding: top7/right8/bottom7/left20 | ON |
| 5 | `Img_RowIcon` | Image | `HBox_RowContent` | Size 18×18(Brush Image Size). Tint 기본 `rgba(244,241,233,0.56)` | ON |
| 6 | `Txt_RowName` | TextBlock | `HBox_RowContent` | Font Jost 13px/500, 색 `#F4F1E9`. Slot Padding-left 8(icon과 gap8) | ON |
| 7 | `Spacer_Leader` | Spacer | `HBox_RowContent` | Slot Size=Fill(1) — 이게 있어야 `Txt_RowCd`가 오른쪽 끝으로 밀림. (CSS 점선 리더 라인 자체는 폴리시 항목, 생략) | OFF |
| 8 | `Txt_RowCd` | TextBlock | `HBox_RowContent` | Font Jost 11px/600, 색 기본 `rgba(244,241,233,0.56)`(쿨다운중=`#E2534F`/선택시=`#E8C384`는 배선단계 런타임 색상 변경) | ON |
| 9 | `Img_RowCursor` | Image | `Overlay_RowContent` | "▶" 삼각 텍스처(없으면 임시 도형/텍스트 "▶"로 대체 가능, art-pipeline 후속 교체). Overlay Alignment: Horizontal=Left, Vertical=Center. 색상 spec 미기재 — 잠정 gold `#E8C384` 권장. **Visibility=Collapsed**(기본) | ON |
| 10 | `HBox_Desc` | HorizontalBox | 루트(VBox, `Btn_Row`의 형제) | Margin: top2/right0/bottom5/left20. **Visibility=Collapsed**(기본, bSelected 시만 Visible) | ON |
| 11 | `Border_DescAccent` | Border | `HBox_Desc` | Width 2px, VerticalAlignment=Fill, 색 `rgba(212,166,87,0.45)` | OFF |
| 12 | `Txt_RowDesc` | TextBlock | `HBox_Desc` | Font Jost 10.5px/300(Light), 색 `rgba(244,241,233,0.56)`. Slot Padding-left 8. **Wrap Text = true** | ON |

완료 후: 컴파일 + 저장.

---

## 2. `WBP_UnitFrame` (`/Game/UI/Components/WBP_UnitFrame`)

**루트는 그대로 둔다**(기본 `CanvasPanel [Root]` 유지 — spec도 CanvasPanel 루트).

| # | 이름 | 타입 | 부모 | 배치 세부 | Is Variable |
|---|---|---|---|---|---|
| 1 | `Panel_Root` | CanvasPanel | 루트 | Anchor Min(0,0)/Max(1,1), Offset 전부 0(꽉 채움) | ON |
| 2 | `Border_Frame` | Border | `Panel_Root` | Anchor Min(0,0)/Max(1,1), Offset 0(꽉 채움). 배경 `rgba(9,11,16,0.84)`(=`--tp-panel-bg`). **디자인타임 기본값은 Ally 기준**으로 배치(Enemy 변형은 배선단계 런타임 분기): 테두리 1px `#D4A657` @ 55%, radius 6. Content Padding: top8/right10/left10/bottom7(Ally 값 — Enemy는 top6/right8/left8/bottom6, 런타임 스왑 예정) | ON |
| 3 | `VBox_Frame` | VerticalBox | `Border_Frame`(콘텐츠) | Border의 단일 콘텐츠 슬롯이므로 별도 배치 불요(Fill) | ON |
| 4 | `Txt_Name` | TextBlock | `VBox_Frame` | Font Jost 10.5px/500, 색 `rgba(244,241,233,0.56)`. **Visibility=Visible**(Ally 기본값 — Enemy는 Collapsed, 런타임 분기) | ON |
| 5 | `HBox_Hp` | HorizontalBox | `VBox_Frame` | 자식 간 gap6(Txt_HpValue Slot Padding-left 6) | ON |
| 6 | `Bar_Hp` | ProgressBar | `HBox_Hp` | Height 7(Size Box로 감싸거나 Fill Image Size 조정), 배경 `rgba(0,0,0,0.5)`. Fill 색 1차 단색 `#E8C384`(Ally 기본 — Enemy `#8FE06A`는 런타임 분기, 그라디언트는 폴리시 항목) | ON |
| 7 | `Txt_HpValue` | TextBlock | `HBox_Hp` | "90/90"(placeholder). Font Jost 10px/600, 색 `#F4F1E9`. §3-3d: 3자리 HP 대비 여유폭 권장(Auto-size 기본 동작으로 충분, 나중 3자리 HP 나오면 재확인) | ON |
| 8 | `Txt_StatusTag` | TextBlock | `VBox_Frame` | Font Jost 8px/400, 2순위 배선 전까지 **Visibility=Collapsed**(자리만 배치, §0-1 권장) | ON |
| 9 | `Img_StatusIcon` | Image | `Panel_Root`(★`VBox_Frame`이 아니라 `Panel_Root`의 직계 자식 — `Border_Frame`과 형제) | 20×20, Anchor=(1,0), Position≈(+8,-8)(모서리 오버랩). 2순위 배선 전까지 **Visibility=Collapsed** | ON |

**⚠ 높이값 스펙 누락**: spec.md §3-3b는 `Border_Frame` 폭(Ally 110 / Enemy 92)만 주고 **높이는 명시 안 됨**(qa-critic 확인 요청 사항, gameplay-engineer가 발견). 이 골격 단계에선 높이를 강제하지 않는다 — 3번 WBP_BattleHUD에서 인스턴스를 배치할 때 Canvas Slot Size로 잠정값(Ally 110×52 / Enemy 92×46 추정)을 넣을 것을 권장하되, **배치 후 육안으로 내용이 잘리지 않는지 직접 확인 후 조정**(스크린샷 첨부 없이 에디터에서 바로 확인).

완료 후: 컴파일 + 저장.

---

## 3. `WBP_SkillMenu` (`/Game/UI/Components/WBP_SkillMenu`)

**루트는 그대로 둔다**(기본 `CanvasPanel [Root]` 유지).

| # | 이름 | 타입 | 부모 | 배치 세부 | Is Variable |
|---|---|---|---|---|---|
| 1 | `Border_Menu` | Border | 루트 | **이 WBP 자체 내부에서는 로컬 원점에 고정**: Anchor(0,0)/(0,0), Position(0,0), Size X=320(고정)/Y=200(추정 placeholder — 헤더+구분선+행3개 어림값, 육안 조정 권장). ⚠ spec §3-1의 "우하단 고정(Anchor 1,1/Position -32,-24)"은 **이 위젯을 WBP_BattleHUD에 인스턴스로 꽂을 때**(§4의 `Menu_SkillMenu` 항목) 적용하는 값이지 여기가 아님 — 헷갈리지 말 것. 배경 `rgba(9,11,16,0.84)`, 테두리 1px `#D4A657` @ 55%, radius 10. Content Padding: top14/right18/left18/bottom15 | ON |
| 2 | `VBox_Menu` | VerticalBox | `Border_Menu`(콘텐츠) | Fill(Border의 단일 콘텐츠 슬롯) | ON |
| 3 | `HBox_Header` | HorizontalBox | `VBox_Menu` | 자식 간 gap12 | ON |
| 4 | `Border_Portrait` | Border | `HBox_Header` | 42×42 고정(Size Box로 감싸 WidthOverride/HeightOverride=42 권장). radius8, 배경 `rgba(0,0,0,0.35)`, 테두리 1px `#D4A657` | ON |
| 5 | `Img_Portrait` | Image | `Border_Portrait`(콘텐츠) | Fill | ON |
| 6 | `VBox_HeaderText` | VerticalBox | `HBox_Header` | Slot Padding-left 12(portrait와 gap) | ON |
| 7 | `Txt_TurnLabel` | TextBlock | `VBox_HeaderText` | "턴"(placeholder, 실제는 `UI_BATTLE_TURN` 키 바인딩 예정). Font Jost 9px/500, Letter Spacing ≈0.22em(육안 조정), 대문자 표기, 색 `#E8C384` | ON |
| 8 | `Txt_UnitName` | TextBlock | `VBox_HeaderText` | "전사 I"(placeholder). Font Cinzel 16px/600, Letter Spacing≈0.03em, 색 `#F4F1E9` | ON |
| 9 | `Border_Divider` | Border | `VBox_Menu`(`HBox_Header`의 형제, 그 다음) | Height 1px, Margin top10/bottom9(left/right 0), 색 `rgba(199,213,235,0.30)`(=`--tp-panel-border-strong`) | OFF |
| 10 | `VBox_SkillList` | VerticalBox | `VBox_Menu` | — | ON |
| 11 | `Row_Skill0` | **WBP_SkillMenuRow 인스턴스** | `VBox_SkillList` | 팔레트의 User Created > WBP_SkillMenuRow를 드래그. 순서대로 3개 추가(첫 배치 후 나머지는 복제 후 이름만 변경) | ON |
| 12 | `Row_Skill1` | WBP_SkillMenuRow 인스턴스 | `VBox_SkillList` | 상동, `Row_Skill0` 다음 순서 | ON |
| 13 | `Row_Skill2` | WBP_SkillMenuRow 인스턴스 | `VBox_SkillList` | 상동, `Row_Skill1` 다음 순서 | ON |

완료 후: 컴파일 + 저장.

---

## 4. `WBP_BattleHUD` (`/Game/UI/Battle/WBP_BattleHUD`, 루트 화면)

**루트는 그대로 둔다**(기본 `CanvasPanel [Root]`). **1순위 범위만 배치** — `Panel_TurnOrderBar`·`Panel_BerserkBadge`·`Panel_FloatingNumbers`·`Panel_TargetCursor`는 2순위(보류), 지금 자리도 만들지 않는다(spec §0 표 그대로).

### 4-1. `Panel_Battlefield`

| 이름 | 타입 | 부모 | 배치 | Is Variable |
|---|---|---|---|---|
| `Panel_Battlefield` | CanvasPanel | 루트 | Anchor(0,0)/(1,1), Offset 전부 0(꽉 채움 — 1280×720 디자인 좌표계와 1:1) | ON |

### 4-2. 유닛프레임 8인스턴스 (`Panel_Battlefield`의 자식)

각각 팔레트에서 `WBP_UnitFrame`을 드래그(첫 A1 배치 후 **복제(Ctrl+D 또는 우클릭 Duplicate) 7회 → 이름·Position·bIsAlly·Transform만 수정**하는 게 빠르다). Anchor=(0,0)/Alignment=(0,0) 공통, Size는 §2의 추정값(Ally 110×52 / Enemy 92×46, 육안 조정) 사용:

| 이름 | Position(X,Y) | bIsAlly(인스턴스 Details에서 체크) | 추가 RenderTransform |
|---|---|---|---|
| `UnitFrame_A1` | (150, 358) | ☑ true | — |
| `UnitFrame_A2` | (300, 328) | ☑ true | — |
| `UnitFrame_A3` | (195, 187) | ☑ true | Scale=(0.82,0.82), Pivot=(0.5, 0.0) |
| `UnitFrame_A4` | (70, 212) | ☑ true | Scale=(0.82,0.82), Pivot=(0.5, 0.0) |
| `UnitFrame_B1` | (1010, 358) | ☐ false | — |
| `UnitFrame_B2` | (860, 328) | ☐ false | — |
| `UnitFrame_B3` | (965, 187) | ☐ false | Scale=(0.82,0.82), Pivot=(0.5, 0.0) |
| `UnitFrame_B4` | (1090, 212) | ☐ false | Scale=(0.82,0.82), Pivot=(0.5, 0.0) |

**⚠ 슬롯↔실제 SpawnPoint 대응 미확정**(spec §6-4): 위 8개 이름(A1~A4/B1~B4)은 목업 시각 배치 기준 추정 매핑이다. 실제 `BP_BattleSpawnPoint` 8개 인스턴스와의 정확한 대응은 배선 단계에서 scene-builder/gameplay-engineer가 재확인한다 — **지금은 이름·좌표만 그대로 배치하면 된다**(대응 재확인이 필요해도 위젯을 다시 만들 필요는 없음, `BoundUnit` 변수 배선만 나중에 조정).

### 4-3. `Menu_SkillMenu`

| 이름 | 타입 | 부모 | 배치 | Is Variable |
|---|---|---|---|---|
| `Menu_SkillMenu` | **WBP_SkillMenu 인스턴스** | 루트(`Panel_Battlefield`의 형제) | Anchor Min(1,1)/Max(1,1), Alignment(1,1), Position(-32,-24), Size X=320/Y=200(§3의 WBP_SkillMenu 자체 크기와 동일값 사용) | ON |

완료 후: 컴파일 + 저장.

---

## 5. 배치 후 확인 체크리스트 (오너 육안 확인 — 스크린샷 불필요, 에디터에서 직접)

- [ ] 4개 WBP 전부 컴파일 에러 0(컴파일 버튼 클릭 시 빨간 X 없음)
- [ ] `WBP_BattleHUD`를 더블클릭 열었을 때 Designer 프리뷰에서 8개 유닛프레임 + 우하단 스킬메뉴가 대략 목업(`approved.html`)과 비슷한 배치로 보이는지
- [ ] `WBP_UnitFrame`의 `Border_Frame` 안에 이름/HP바/HP숫자 텍스트가 잘리지 않는지(§2의 높이 placeholder 조정 필요 여부 판단)
- [ ] `WBP_SkillMenu`의 3개 Row가 세로로 정상 스택되는지

문제가 있어도 **직접 수정하지 말고** 다음 세션에서 gameplay-engineer에게 스크린샷 없이 "N번 항목 이상함" 정도로만 전달해도 됨 — 배선 단계에서 같이 확인한다.

---

## 다음 단계

이 4개 WBP 배치가 끝나면 **§B 5단계(배선)** — gameplay-engineer가 MCP로 이어서 진행:
- `Row.Btn_Row` OnClicked → `WBP_SkillMenu.NotifySkillSelected(SkillId)` 연결
- `SetHp`/`SetUnitInfo`/`SetCooldown`/`SetSelected` 등 함수 바디 구현(지금은 빈 껍데기)
- `UpdateScreenPosition`/`RefreshAllUnitFramePositions` 실제 PWTS 로직 구현
- `BP_BattleSpawnPoint`의 기존 F3b `WBP_HpGauge` 관련 EventGraph 로직(Cast+SetHpText)을 `WBP_UnitFrame` 기반으로 교체(§B-3 배선 단계 — [[WBP_BattleHUD_골격생성_착수전스냅샷]] §4 참고)

## 관련 문서
[[spec]] · [[UI_화면_규약]] · [[네이밍_폴더_규약]] · [[WBP_BattleHUD_골격생성_착수전스냅샷]]
