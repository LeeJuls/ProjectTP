---
type: log
project: projectTP
feature: 전투완성
stage: U
status: 완료 — F3(HP 게이지) 완결. WBP_HpGauge·위치추적 스텁 삭제 완료, 컴파일 에러 0
updated: 2026-07-15
---

# U단계 — 전투HUD UMG 실장 (HP 게이지, F3 완결)

> 대상: [[spec]](`ui/battle/WBP_BattleHUD/spec.md`) §3-3(WBP_UnitFrame)·§6-4(위치추적 방식) · [[오너_UMG배치가이드]] §2 · TC: [[U단계_TC]](qa-critic 작성, 본 문서와 별개 보존) · 선행 기록: [[WBP_BattleHUD_골격생성_착수전스냅샷]] · [[F3_HP게이지_수정전스냅샷]] · MCP 노하우: [[언리얼_MCP_실전노하우]] §22.
> [[전투완성/plan]] F3(스탯 로드+HP 게이지) 스테이지의 최종 완결 기록. F3b(액터부착 월드공간 TextRenderComponent, 3회 실패 — [[F3_HP게이지_수정전스냅샷]] 참고)를 폐기하고 UMG WidgetComponent(Screen space)로 재구현했다.
#projectTP/전투완성

---

## 1. 결과 요약

**F3(HP 게이지) 완결.** 3회 실패했던 TextRender 방식을 폐기하고 UMG WidgetComponent(Screen space)로 재구현해 성공했다. PIE에서 8기 전원 머리 위에 HP 바 표시를 확인했고, 오너가 육안으로 승인했다(Director MCP 실측 확인 완료).

## 2. 최종 구현 상태

### 2-1. `WBP_UnitFrame` (`/Game/UI/Components/WBP_UnitFrame`)

위젯트리:
```
Root [CanvasPanel]
 └─ Panel_Root [CanvasPanel]
     └─ Border_Frame [Border]  (투명, BrushColor A=0)
         └─ VBox_Frame [VerticalBox]
             └─ HBox_Hp [HorizontalBox]
                 └─ Bar_Hp [ProgressBar]   ← 화면에 표시되는 유일한 위젯
             (Txt_StatusTag [TextBlock, Collapsed] — F7 상태이상용 예약, 보존)
     (Img_StatusIcon [Image, Collapsed] — 2순위 예약, 보존)
```

**오너 지시로 간소화(2026-07-15)**: "정보가 많아서 간소화" — `Txt_Name`(유닛명)·`Txt_HpValue`("90/90" 숫자) 위젯을 **삭제**하고 `Border_Frame`의 검은 배경을 **투명화**했다. 관련해 쓸모가 없어진 노드 7개(`SetText`×2, `FormatText`×1, `ToText`×2, `VariableGet`×2)도 함께 제거했다. `Txt_StatusTag`(Collapsed, F7 상태이상용 예약)·`Img_StatusIcon`(Collapsed)은 그대로 보존했다.

부수효과: `SetUnitInfo`의 `DisplayName="Unit"` 하드코딩 placeholder가 이 삭제로 함께 사라져, 전역 CLAUDE.md "UI 문자열 하드코딩 금지" 규칙 위반 상태가 자동으로 해소됐다.

**함수**:
- `SetHp(NewHp: int, NewMaxHp: int)`: `Hp`/`MaxHp` 멤버 대입 → `Branch(NewMaxHp > 0)` → true: `Conv_IntToFloat`×2 + `Divide` → `Bar_Hp.SetPercent(Percent)` / false: `SetPercent(0.0)`. (텍스트 표시부는 위 간소화로 제거됨)
- `SetUnitInfo(DisplayName: text, InIsAlly: bool)`: `bIsAlly` 멤버 대입만 남음(`Txt_Name` 삭제로 `SetText` 호출 제거). `DisplayName` 파라미터는 시그니처만 유지(F7에서 재활용 예정).

### 2-2. `BP_BattleSpawnPoint`

- EventGraph의 dangling `Cast To WBP_HpGauge`를 `retarget_node_class`로 `WBP_UnitFrame_C`로 교체.
- BeginPlay 배선: `Cast.then` → `SetUnitInfo` → `SetHp(Hp, MaxHp)` → `CachedUnitFrame`(신규 변수, `WBP_UnitFrame_C` 참조 타입) 캐싱.
- 8기 레벨 인스턴스의 `HpGaugeWidget`(WidgetComponent): `WidgetClass=WBP_UnitFrame_C` · `Space=Screen` · `DrawSize` 아군 110×56 / 적군 92×56.

## 3. 핵심 노하우 — 위젯 위치 확정 (재발 방지 기록)

> MCP 툴 함정으로서의 상세 서술은 [[언리얼_MCP_실전노하우]] §22(함정㉖·㉗)에 정식 등재했다. 여기서는 이 작업의 맥락에서 요약한다.

**함정**: 레벨 인스턴스 컴포넌트의 `RelativeLocation`은 **MCP로 수정 불가**하다. `ObjectTools.set_properties`·`reset_properties` 둘 다 `true`를 반환하지만 실제 값은 바뀌지 않음을 4회 실측으로 확인했다. CDO(`BP_BattleSpawnPoint_C:HpGaugeWidget_GEN_VARIABLE`) 자체는 수정되지만, 레벨의 8개 인스턴스가 개별 오버라이드를 붙들고 있어 CDO 값을 상속받지 않는다. Construction Script에 `SetRelativeLocation`을 넣어도 실패한다(액터 재구성 순서상 인스턴스 오버라이드가 나중에 다시 덮어씀).

**해결**: **`BeginPlay`에서 `SetRelativeLocation`을 호출**한다 — 모든 재적용이 끝난 뒤 실행되므로 무엇도 이 값을 덮어쓰지 못한다. 이것이 유일하게 작동한 경로였다.

**스프라이트 로컬축 함정(핵심)**: `HpGaugeWidget`의 부모가 **`Sprite`(루트, yaw 정렬됨 + 스케일 `(6.48, 2.59, 1)`인 비균등 스케일)**라, 로컬축이 직관과 다르다. Z가 "위"가 아니고, **Y가 화면 수직축(음수=위)**이다. 게다가 **아군/적군 스프라이트가 서로 마주보게 회전돼 있어 X축 부호가 팀마다 반전**된다 → 팀 공통 단일 오프셋은 원리적으로 불가능하다.

**최종 확정값**(오너가 PIE에서 F8로 빙의 해제한 뒤 기즈모로 직접 맞춘 값을 Director가 실측 채집): **아군 `(-7.716049, -34.722008, 0)` / 적군 `(+7.716049, -27.0, 0)`**. `수학|벡터|SelectVector` 노드로 `bIsParty` 분기해 주입(BeginPlay). PIE 라이브 값으로 8기 전원 검증 완료.

**저장 함정**: PIE 실행 중엔 `save_assets`가 "Asset does not exist" 에러를 반환한다(조회는 되는데 저장만 막힘). PIE 종료 후엔 정상 저장된다.

**검증 함정**: 에디터 월드 경로(`/Game/Stages/map_battle_octopath...`)의 `get_properties`는 **직렬화된 초기값만** 보여준다 — BeginPlay가 런타임에 바꾼 실제 값을 보려면 **PIE 월드 경로(`/Game/Stages/UEDPIE_0_map_battle_octopath...`)**를 조회해야 한다.

## 4. 폐기·정리

- `/Game/UI/Battle/WBP_HpGauge`(F3b 임시 위젯): 레퍼런서 0 확인 후 **삭제 완료**.
- `WBP_BattleHUD.RefreshAllUnitFramePositions`, `WBP_UnitFrame.UpdateScreenPosition`(빈 스텁): **삭제 완료**. [[spec]] §6-4가 서술하던 ProjectWorldToScreen 동적갱신 방식은 **채택 안 함** — WidgetComponent(Screen space)가 엔진 레벨에서 위치추적·빌보드를 보장하므로 불필요하다고 판단.
- 컴파일 에러 0(`BP_BattleSpawnPoint`, `WBP_UnitFrame`, `WBP_BattleHUD`), 전부 저장 완료.

## 5. 도구 함정 요약 — bluecode 실패 → 저수준 노드 API 대체

`UmgMcp`의 `bluecode_apply`/`bluecode_connect`는 함수 파라미터 참조·위젯 `SetText` 액션 매칭에서 반복 실패했다("No Blueprint action matched", 파라미터를 리터럴로 오파싱). **대체 경로 = `unreal-mcp` `BlueprintTools`의 저수준 노드 API**(`create_node`/`connect_pins`/`set_pin_value`/`get_node_infos`/`delete_node`/`retarget_node_class`) — 이 경로는 전부 정상 작동했다. 핵심 요령: **함수 파라미터는 이름 문자열이 아니라 `FunctionEntry` 노드의 출력 핀으로 직접 connect**한다. 상세: [[언리얼_MCP_실전노하우]] §22(함정㉘).

## 6. 검증 상태

- 컴파일 에러 0(BP_BattleSpawnPoint / WBP_UnitFrame / WBP_BattleHUD) — 전부 저장 완료.
- PIE에서 8기 전원(A1~A4, B1~B4) 머리 위 HP 바 표시 — Director MCP 실측 확인.
- 오너 육안 승인(PIE 라이브 확인) 완료.

## 관련 문서
[[spec]] · [[오너_UMG배치가이드]] · [[U단계_TC]] · [[WBP_BattleHUD_골격생성_착수전스냅샷]] · [[F3_HP게이지_수정전스냅샷]] · [[언리얼_MCP_실전노하우]] · [[전투완성/plan]] · [[청사진]]
