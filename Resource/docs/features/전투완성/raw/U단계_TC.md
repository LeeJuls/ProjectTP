---
type: qa
project: projectTP
feature: 전투완성
stage: U
status: TC 확정 대기
updated: 2026-07-14
---

# 전투HUD UMG 실장(U단계) — 예외상황 TC + 적대적 계획 리뷰

> 대상: 오너 승인 v5 계획(U1 배치=umg-engineer / U2 배선=umg-engineer / U3 실증=verifier).
> 기준 문서: [[spec]](`ui/battle/WBP_BattleHUD/spec.md`) · [[오너_UMG배치가이드]] · [[WBP_BattleHUD_골격생성_착수전스냅샷]] · [[F3_HP게이지_수정전스냅샷]] · [[언리얼_MCP_실전노하우]] §20~21(함정㉔·㉑·⑳·③·⑰).
> 이 문서는 **표시 계층(U단계) 예외 경로**만 다룬다. 정상 경로·전투 로직 TC는 U3 verifier 기본절차와 F4 몫. 판정방법의 **"시각캡처(CaptureViewport)"는 §18 함정⑫/§20 로 신뢰불가라 배제** — 시각 확인은 전부 **오너 육안(Designer 프리뷰/PIE)**으로 라우팅.
#projectTP/전투완성

---

## ① 계획 리뷰 (적대적)

### 치명 (착수 전 반드시 해소 — 이대로 개발하면 깨짐)

**[치명-1] HP 표시 아키텍처가 두 갈래 — spec은 "내장 8프레임+PWTS", U2는 "유닛별 WidgetComponent+PWTS삭제". 문서 레벨 CONFIRMED 모순.**
- spec §2/§5/§6-4 + 가이드 §4.2 = **WBP_BattleHUD.Panel_Battlefield 안에 WBP_UnitFrame 8개 인스턴스(UnitFrame_A1~B4)를 정적 좌표로 배치하고, 위치는 `RefreshAllUnitFramePositions`→`UpdateScreenPosition`(Project World To Screen)로 매 틱 갱신**하는 화면-오버레이 구조(§6-4에서 "동적 PWTS 채택" ✅확정).
- U2 v5 = **BP_BattleSpawnPoint의 per-actor `HpGaugeWidget`(WidgetComponent, space=Screen)의 WidgetClass를 WBP_UnitFrame_C로** 바꿔 액터마다 자기 WBP_UnitFrame을 렌더 + **`UpdateScreenPosition`/`RefreshAllUnitFramePositions` 스텁 삭제**.
- 두 경로는 **다른 8개 인스턴스**를 만든다. 결과:
  - WBP_BattleHUD가 뷰포트에 올라가면 → per-actor 8개(동적) + 내장 8개(가이드 §4.2 정적 좌표 150,358 등, PWTS 삭제로 카메라 추종 불가) = **최대 16 프레임 이중표시** + §6-4가 경고한 "카메라 전환 시 어긋남" 회귀 재현.
  - 안 올라가면 → U1이 배치한 내장 8개는 **死배치**(U1 노동 낭비).
- **어느 쪽이든** `RefreshAllUnitFramePositions` 삭제는 spec §6-4(동적 PWTS ✅확정)와 **정면 충돌**한다. → **U1 착수 전 Director가 "F3완결 HP 표시 = per-actor WidgetComponent 단일 경로"임을 명문화하고, 그렇다면 U1의 WBP_BattleHUD 내장 8프레임 배치를 (a)보류 또는 (b)"死배치 인지된 선배치"로 표기**해야 한다. 확신도 **CONFIRMED**(문서 대조).

**[치명-2] `SetHp` 배선의 정수 나눗셈 함정 — Int/Int면 비-만피 HP가 전부 0%.**
- `Unit.Hp`/`Unit.MaxHp`는 `DT_JobStats`에서 Integer(§7). `Bar_Hp.SetPercent(Hp/MaxHp)`를 **정수÷정수**로 배선하면 `48/90 = 0`(정수 나눗셈), `89/90 = 0` — 게이지가 **만피 전까지 항상 빈 채**, 만피에서만 1.0. 배선 시 **float 캐스트 강제**(`(float)Hp / (float)MaxHp`)를 명시 안 하면 BP 기본 와일드카드 승격에서 정수경로로 빠지기 쉽다. 확신도 **CONFIRMED**(BP 정수 나눗셈 표준 동작).
- 동반: `MaxHp==0`(스탯로드 실패 경로, 아래 정정-3) → `Hp/0` **0 나눗셈** → NaN/무한대 Percent(잠재 크래시/게이지 깨짐). 가드 필수.

### 정정 (계획에 빠졌거나 어긋난 것 — 절차에 못박아야)

**[정정-1] HpGaugeText(F3 월드공간 TextRenderComponent "90/90") 처리 누락 → 이중표시 위험.**
- spec §0 표는 WBP_UnitFrame이 "**기존 F3 임시 HP(`HpGaugeText` — 액터부착 월드공간 TextRenderComponent)를 대체**"한다고 명시. 그러나 U2 v5는 `HpGaugeWidget`(WidgetComponent)만 재배선하고 **`HpGaugeText` 비활성/제거를 언급하지 않는다**. 둘 다 살아있으면 유닛 머리 위에 월드 텍스트 + WBP_UnitFrame이 **동시 표시**.
- ⚠ 컴포넌트 인벤토리 불일치: 골격생성 스냅샷 §2 CDO 목록엔 `HpGaugeWidget`만(=`Arrow·TurnMarker·ClickBox·EffectQuad·HpGaugeWidget·Sprite`), F3_HP게이지 스냅샷엔 `HpGaugeText`가 8기에 존재. **현재 두 컴포넌트가 공존하는지 확정 필요**. 확신도 **PLAUSIBLE**(현 컴포넌트 인벤토리 미실측 — TC-U10에서 실측).

**[정정-2] 함정㉔ — "8기 인스턴스 오버라이드 정리"를 CDO 세팅만으로 끝내면 재발.**
- 골격생성 §3: 레벨 8기 인스턴스의 `HpGaugeWidget`은 이미 `space=World`/`widgetClass=None`/`drawSize=(500,500)`/`relLoc=(0,0,0)`로 **CDO와 다른 per-instance 오버라이드**를 보유. 함정㉔(§20)상 **CDO의 widgetClass를 WBP_UnitFrame_C로 바꿔도 이 8기엔 전파 안 됨**. → U2 절차에 "**8기 각각 개별 `set_properties`(§7 함정⑪ 준수, 개별 호출) 후 PIE 재조회**"를 명문화. 세팅해야 할 4필드: `widgetClass=WBP_UnitFrame_C`·`space=Screen`·`drawSize`(정상값)·`relativeLocation`(머리 위 오프셋, CDO=0,96.5,0). 확신도 **CONFIRMED**(§20 실측 노하우).

**[정정-3] `WBP_HpGauge` 폐기는 "referencer 0"이 **삭제 전 게이트**여야 하고, 참조는 최소 2곳.**
- 골격생성 §4: `widgetClass` 외에 **EventGraph의 `Cast To WBP_HpGauge`(K2Node_DynamicCast_2) 노드가 별도로 WBP_HpGauge 타입을 하드 참조**. widgetClass만 WBP_UnitFrame으로 바꾸면 이 Cast가 **런타임 상시 실패(무증상)** → SetHp 미호출. 폐기 전 **widgetClass + Cast 노드 둘 다 재타깃**해 referencer가 0인지 확인해야. 삭제 후 참조 잔존 시 dangling → 컴파일/로드 실패, 그리고 **`Content/`는 .gitignore라 git 복구 불가**(함정㉑). 확신도 **CONFIRMED**.

**[정정-4] SkillMenu 높이 — spec(Y=Auto/Size To Content)과 가이드(Y=200 고정) 불일치.** 행 선택 시 `Txt_RowDesc`(wrap) 펼침으로 콘텐츠가 200px 초과하면 고정 높이면 **하단 클리핑**. 배치 시 Border를 Auto-size로 두거나 여유폭 확인 필요. 확신도 **CONFIRMED**(문서 대조).

### 기우 (과잉경계 방지 — 이건 괜찮다)

- **create_widget 재개 안전성**: §21·umg-engineer 노트상 create_widget은 기존 위젯 **이름 기준 스킵**이라 중단-재개 안전. 단 **이름 정합이 전제**(정정 아님, 아래 TC-U01은 이름 어긋남/루트 중복만 겨눔).
- **파일럿 잔여물 "미저장"**: 미저장이면 에디터 재시작 시 소실 → 오히려 clean slate. 상태가 **bimodal**(잔여물 有/無)이니 U1 첫 `get_widget_tree` 선조회로 분기하면 족함 — 잔여물 자체는 치명 아님.
- **bIsVariable MCP 세팅**: §21에서 `set_widget_properties({bIsVariable:true})`+query 재확인 **실증됨**. "MCP로 안 될까" 걱정은 기우. 단 "세팅≠반영"이라 query 재확인은 유지(TC-U02).
- **폰트 폴백**: 기본 폰트 폴백 자체는 crash 아님(레이아웃 메트릭만 변동). 가이드의 "레이아웃 지장 없음"은 낙관이나 치명 아님 — 오너 육안으로 족함(TC-U04).

---

## ② TC 표 (TC-U01 ~ TC-U13)

> 판정 시점은 대부분 U3(verifier 실행). "대상"은 **어느 스테이지의 산출물을 검증하는지**. 상태 전부 대기.
> 판정도구 약칭: **WT**=`get_widget_tree` 대조 / **QP**=`query_widget_properties` 재조회 / **OP**=unreal-mcp `ObjectTools.get_properties`(PIE/레벨 인스턴스) / **REF**=애셋 referencer 조회 / **CMP**=컴파일 결과 0 / **PIE**=PIE 런타임 값/로그 / **육안**=오너 Designer프리뷰·PIE 육안.

| ID | 심각도 | 조건 → 기대결과 (재현 시나리오) | 판정방법 | 대상 | 상태 |
|---|---|---|---|---|---|
| **TC-U01** | High | **파일럿 잔여물·루트 중복/이름충돌**: WBP_SkillMenuRow에 파일럿 잔여물(RootVBox+Btn_Row)이 남은 상태에서 배치 실행 → 최종 트리 = spec §3-2 그대로(**루트 VerticalBox 정확히 1개**, 하위 12위젯, orphan/중복 루트 0, 잘못된 부모 0). 특히 계획이 쓰는 루트 이름 ≠ 잔여 "RootVBox"면 루트 2개 또는 detached 위젯이 생기는지 확인 | WT(spec §3-2와 구조 diff) + U1 **첫 호출 전 `get_widget_tree` 선조회**로 시작상태(잔여물 有/無) 기록 | U1 | 대기 |
| **TC-U02** | High | **bIsVariable 세팅≠반영**: 4 WBP의 Is-Variable-ON 목록(가이드 표) 전 위젯에 대해 set 호출 성공이 아니라 **재조회로 `bIsVariable==true` 실증**. 특히 create_widget이 **스킵한 잔여 Btn_Row**에도 반영됐는지. 미반영 위젯은 U2 배선 참조 불가 | QP(각 위젯 bIsVariable 재조회) | U1 | 대기 |
| **TC-U03** | Medium | **save 영속성/미저장 잔존**: `save_asset` 후 애셋을 **리로드(또는 is_dirty 재조회)** 했을 때 위젯 트리가 그대로 유지(에디터 메모리에만 있고 디스크 미반영이면 U2가 빈/구 트리를 만남). 함정⑳(is_dirty 미클리어) 계열 | 리로드 후 WT + is_dirty 재조회 | U1 | 대기 |
| **TC-U04** | Low | **폰트 폴백 레이아웃 붕괴**: Jost/Cinzel 부재로 기본 폰트 폴백 시 (a) SkillMenuRow 한 줄(`Img_RowIcon`+`Txt_RowName`+`Spacer_Leader(Fill)`+`Txt_RowCd`)에서 이름/CD 클리핑·의도치 않은 줄바꿈 없음 (b) `Txt_HpValue` "90/90" 잘림 없음 (c) 헤더 `Txt_UnitName` 넘침 없음 | 육안(Designer 프리뷰) + 가능하면 QP(desired size) | U1 | 대기 |
| **TC-U05** | Medium | **SkillMenu 높이 Auto vs 200 클리핑**: 한 행을 선택 상태로 만들어 `HBox_Desc`(`Txt_RowDesc` wrap)를 펼쳤을 때 콘텐츠가 `Border_Menu` 고정 Y=200(가이드)을 초과해도 **하단 클리핑 없음**(= Border가 Auto-size거나 여유). spec은 Y=Auto인데 가이드는 200 고정 | 육안(Designer, Desc Visible 강제) + QP(Border desired/실측 높이) | U1 | 대기 |
| **TC-U06** | Low | **구조 정합(2순위 자리 선배치)**: `Img_StatusIcon`의 부모가 **`Panel_Root`**(★VBox_Frame 아님, 가이드 §2 경고) + `Img_StatusIcon`·`Txt_StatusTag` 기본 **Visibility=Collapsed** 실증(지금 안 뜸). 부모 어긋나면 2순위 바인딩 시 아이콘 위치 오배치 | WT(부모 확인) + QP(Visibility=Collapsed) | U1 | 대기 |
| **TC-U07** | Critical | **함정㉔ 8기 인스턴스 오버라이드 잔재**: U2 후 **레벨 8기 각각(PIE 재조회)** `HpGaugeWidget`의 `widgetClass==WBP_UnitFrame_C` · `space==Screen` · `drawSize`=정상값(≠500×500 잔재) · `relativeLocation`=머리위 오프셋. **CDO만 확인하고 통과시키지 말 것** — CDO=true라도 8기가 None/World/500×500로 남으면 HP 전면 미표시(F3완결 불가) | OP(8기 각 인스턴스 개별 조회 — CDO 아님) | U2 | 대기 |
| **TC-U08** | High | **Cast 무증상 실패 + 스탯로드 키 정합**: BeginPlay Cast를 WBP_UnitFrame으로 재타깃했는데 조용히 실패하면 위젯이 **U1 placeholder "90/90"을 그대로** 보임(전사는 우연히 맞아 못 잡음). **판별 타깃=마법사 유닛**: PIE에서 마법사(MaxHp80) WBP_UnitFrame의 `Txt_HpValue=="80/80"`(placeholder 90/90 아님)·전사=="90/90". 틀리면 Cast실패 또는 `.id`필드 조회(F2: id 항상 0, RowName으로 조회해야) 회귀 | PIE(유닛별 WBP_UnitFrame 인스턴스 Txt_HpValue/Bar_Hp 조회) | U2 | 대기 |
| **TC-U09** | High | **SetHp 정수/0 나눗셈**: `SetHp(48,90)` 주입 → `Bar_Hp.Percent≈0.53`(정수나눗셈이면 0.0). + `SetHp(x,0)`(스탯로드 실패로 MaxHp=0) 주입 → **NaN/크래시 없이** 가드(Percent 0 또는 안전값), 게이지·텍스트 깨지지 않음 | PIE(Bar_Hp.Percent 실측) + CMP(0나눗셈 가드 노드 존재) | U2 | 대기 |
| **TC-U10** | High | **유닛당 HP 표시 소스 정확히 1개(이중표시)**: 한 유닛 머리 위 HP 표시 인스턴스 수 = **1**. (a) `HpGaugeText`(F3 월드텍스트)가 잔존·bVisible이면 WBP_UnitFrame과 이중 → HpGaugeText 비활성/제거 확인 (b) WBP_BattleHUD 내장 8프레임(치명-1)이 뷰포트에 동시 렌더되지 않음 | OP(HpGaugeText 존재/bVisible + HpGaugeWidget) + 육안(머리위 텍스트 2개 겹침 여부) | U2 | 대기 |
| **TC-U11** | High | **WBP_HpGauge 폐기 안전 게이트**: **삭제 직전** WBP_HpGauge referencer==0(widgetClass 재타깃 + EventGraph `Cast To WBP_HpGauge` 노드 재타깃 **둘 다** 완료 확인). 삭제 후 `BP_BattleSpawnPoint` 컴파일 에러 0. referencer>0인데 삭제하면 dangling(Content gitignore→복구불가, 함정㉑) | REF(삭제 전 0 게이트) + CMP(삭제 후 0) | U2 | 대기 |
| **TC-U12** | High | **스텁 삭제가 컴파일 깨뜨림**: `UpdateScreenPosition`(WBP_UnitFrame)·`RefreshAllUnitFramePositions`(WBP_BattleHUD) 삭제 후 **두 WBP 모두 컴파일 0** + 이 함수들을 부르던 **잔존 호출 노드(Tick/BeginPlay/Timer)가 없음**(있으면 unresolved call/컴파일 에러). 치명-1과 연동 | CMP(2 WBP) + WT/노드 조회(orphan 호출 0) | U2 | 대기 |
| **TC-U13** | Medium | **Screen space drawSize 잘림/겹침(시각)**: per-actor 위젯이 (a) WBP_UnitFrame 내용(이름+HP바+HP값)을 **잘림 없이** 담고 (b) 인접 유닛 프레임을 **전면 가리지 않음**(500×500 잔재면 화면 전체 겹침). DefaultCamera·ActionCam 근접컷 둘 다 | 육안(PIE, 2카메라) + OP(8기 drawSize 값 교차) | U2 | 대기 |

---

## ③ 커버리지 근거 (검토한 축)

- **경계값**: HP 48/90·89/90(정수나눗셈), MaxHp=0(0나눗셈·스탯로드 실패), drawSize 500×500 잔재 vs 정상 — TC-U09/U07/U13.
- **동시성/이중 소스**: 내장8 vs per-actor8(치명-1), HpGaugeText vs HpGaugeWidget(정정-1) — TC-U10.
- **순서 의존**: WBP_HpGauge 폐기 전 referencer 0 게이트, 스텁 삭제와 호출부 정합 — TC-U11/U12.
- **상태 누수/잔재**: 파일럿 RootVBox+Btn_Row, 8기 per-instance 오버라이드(함정㉔), 미저장 잔존 — TC-U01/U07/U03.
- **무증상 실패(silent)**: Cast 상시실패 + placeholder 마스킹, bIsVariable 세팅≠반영 — TC-U08/U02.
- **명세-구현 불일치**: spec(내장+PWTS) vs U2(per-actor+PWTS삭제), spec(Auto) vs 가이드(200), spec(HpGaugeText 대체) vs U2(미언급) — 치명-1/정정-4/정정-1.

## 관련 문서
[[spec]] · [[오너_UMG배치가이드]] · [[WBP_BattleHUD_골격생성_착수전스냅샷]] · [[F3_HP게이지_수정전스냅샷]] · [[언리얼_MCP_실전노하우]] · [[전투완성/plan]]
