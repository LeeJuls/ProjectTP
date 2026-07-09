---
type: raw
project: projectTP
feature: UI파이프라인
agent: gameplay-engineer
updated: 2026-07-10
---

# A0 기술 스파이크 — UMG(WidgetBlueprint)를 MCP로 만들 수 있는가

> 알파의 메뉴 UI(대기실 등) 전량을 UMG WidgetBlueprint로 만들 계획(`알파_개발계획.md` §2.6①)인데, 이 프로젝트는 UMG를 한 번도 안 써봤고 MCP 툴셋 목록에 Widget/UMG 전용 툴셋이 안 보인다는 Director 리컨을 실증하는 A0 스파이크. **최종 판정(2026-07-10 재개 세션 완료): 부분성공 — `BlueprintTools.create`로 모달 없이 진짜 `WidgetBlueprint` 애셋 생성 확인, 단 `WidgetTree`/`RootWidget` 프로퍼티는 `ObjectTools`로 read/write 불가해 위젯트리 조작(자식 위젯 배치)은 막힘.** 1차 시도(2026-07-08)는 공유 MCP 브릿지 모달 마비로 인프라 차단·미완료였으나, 2026-07-10 단독 세션으로 재개해 완결했다 — 1차 시도 기록은 §1~6 보존, 재개 실행 상세는 §7. 상위: [[projectTP_허브]]
> 관련: [[언리얼_MCP_실전노하우]] · 1차 시도 당시 동시기 유사 인프라 차단 사례 [[A0_CSV파이프라인스파이크]](`docs/features/캐릭터시스템/raw/A0_CSV파이프라인스파이크.md`)
#projectTP/UI파이프라인

---

## 최종 판정 (한 줄)

**부분성공** — `BlueprintTools.create(asset_type={"refPath":"/Script/UMG.UserWidget"})`는 모달 없이 즉시 정상 동작하고, `AssetTools.find_assets(asset_type=/Script/UMGEditor.WidgetBlueprint)` 타입필터(+ 네거티브 컨트롤)로 생성물이 껍데기만 다른 일반 Blueprint가 아니라 **애셋 레지스트리 기준 진짜 WidgetBlueprint**임을 확정했다(§7-1·§7-2). 그러나 `WidgetTree`/`RootWidget`은 `ObjectTools`의 `list_properties`/`get_properties`/`set_properties` 전부에서 read·write가 막혀 있어(§7-3), 자식 위젯(Button/TextBlock) 배치 등 위젯트리 조작은 현재 노출된 MCP 표면으로는 불가능함이 실증됐다. "완전성공(트리 조작까지 가능)"도 "폴백확정(create 자체가 모달로 막힘)"도 아닌 정확히 명세의 부분성공 분류에 해당한다.

---

## 핵심 발견 (3줄)

1. **`create`로 실제 `WidgetBlueprint` 생성 확인, 모달 위험 없음** — `/Script/UMG.UserWidget`을 `asset_type`으로 넣으면 `BlueprintTools.create`가 즉시 정상 응답하며(§19 함정㉓이 우려한 "UserWidget도 모달을 유발할 수 있다"는 가설은 기각), `find_assets` 타입필터(양성+네거티브 컨트롤)로 생성물이 진짜 `/Script/UMGEditor.WidgetBlueprint` 컨테이너임을 확정했다.
2. **위젯트리 조작은 프로퍼티 API 레벨에서 막혀 있음** — `WidgetTree`/`RootWidget`은 `ObjectTools`의 `list_properties`/`get_properties`/`set_properties` 전부에서 접근 불가(읽기도 쓰기도 에러). 서브오브젝트 경로(`:WidgetTree`)로 오브젝트 실존은 확인되지만 그 이상(RootWidget 조회, 자식 위젯 추가) 진입 불가 — 전용 Widget/UMG MCP 툴셋이 여전히 없다는 사실과 결합하면, 위젯트리 구성은 현재 MCP 표면으로 불가능함이 실증됐다.
3. **1차 시도의 "공유 브릿지 모달 마비"는 재발하지 않음** — 재개 세션은 단독 사용(동시 세션 없음) 조건에서 진행했고, `create` 포함 전체 호출이 전부 즉시 정상 응답했다. 1차 세션의 마비가 "부적절한 asset_type(UserDefinedStruct) + 동시 다중 세션" 조합에서 기인했다는 기존 §19 함정㉓ 가설과 일치하는 결과다.

---

## 1. 배경 · 목표

알파는 대기실 등 메뉴 UI를 전부 UMG WidgetBlueprint로 만들 계획이다(`알파_개발계획.md` §2.6① — 월드공간 버튼은 전투 연출 전용으로 강등됨, 목표 경로 `/Game/UI/{Screens,Components,Textures}/`, `WBP_` 접두사, "spec.md 없이 UMG를 만들지 않는다"). 그런데 이 프로젝트는 UMG를 한 번도 안 써봤고(기존 UI는 전부 월드공간 Plane+TextRender+ClickBox 패턴), `list_toolsets`에 Widget/UMG 전용 툴셋이 안 보인다는 게 Director 리컨으로 이미 확인된 상태 — 이 스파이크는 "MCP만으로 WBP를 실제로 만들고 조작할 수 있는가"를 실증(완성 UI가 아니라 됨/안됨 판정)하는 것이 목적이다.

### 사전 확인 (필독 문서)
`언리얼_MCP_실전노하우.md`(전체 364줄, §1~18 전량 읽음)를 확인했다. §18 `set_entry` dirty 버그, `import_file` 삭제 함정 등은 StringTable/DataTable 전용이라 이번 스파이크와 직접 관련은 없었지만, **이번 스파이크가 겪은 "MCP 브릿지 전체 마비" 현상은 이 문서에 아직 기록되지 않은 새로운 패턴**이라 §19로 추가할 가치가 있다고 판단(§6 참고, Director 확인 후 편입 권장).

---

## 2. 실행한 절차와 결과

### 2-1. 위젯 관련 클래스 탐색 (완료·확정)

**`list_toolsets` — Widget/UMG 전용 툴셋 없음 확정.** 21개 전체 목록:
`AgentSkillToolset, ConfigSettingsToolset, EditorAppToolset, LogsToolset, PluginToolset, ActorTools, AssetTools, BlueprintTools, CurveTableTools, DataAssetTools, DataTableTools, MaterialTools, MaterialInstanceTools, ObjectTools, PrimitiveTools, SceneTools, SkeletalMeshTools, StaticMeshTools, StringTableTools, ProgrammaticToolset, TextureTools`
— "Widget"/"UMG"/"UI"를 이름에 포함한 항목 0개. Director 리컨과 정확히 일치.

**`ObjectTools.search_subclasses(base_class={"refPath":"/Script/UMG.UserWidget"}, class_name="")`** — 성공, 36건 반환. 전부 엔진/플러그인 콘텐츠(`VREditorBaseUserWidget`, `EditorUtilityWidget`, Landmass/PCG/AudioWidgets/Datasmith/TakeRecorder 등 에디터 유틸리티·플러그인 위젯)이고 **`/Game/` 경로 프로젝트 자산은 0건** — 프로젝트에 UserWidget 서브클래스가 아직 없다는 걸 확정.

**`AssetTools.find_assets(folder_path="/Game/UI", name="", recursive=true)`** — 성공, `["/Game/UI/ST_UI"]` 1건만 반환(StringTable). `/Game/UI/Screens`·`/Game/UI/Components`·`/Game/UI/Textures` 하위에 WidgetBlueprint 애셋 0건 — 예상대로 UMG 미사용 상태 재확인. (단, `list_folders`/`exists`로 폴더 자체의 존재를 직접 재검증하려던 시도는 §2-3의 차단으로 실패 — `알파_개발계획.md` line 163이 "골격 생성 완료(2026-07-08)"라 명시하므로 폴더 자체는 존재할 것으로 추정하나, 이번 세션에서 기계적으로 재확인하지는 못했다.)

**`ObjectTools.search_subclasses(base_class={"refPath":"/Script/Engine.Blueprint"}, class_name="Widget")`** — 성공, "Blueprint의 서브클래스 중 Widget이 들어간 것"으로 검색해 4건 확보. 이것이 실제 **WidgetBlueprint 애셋 타입 후보군**이다:
```
/Script/UMG.UserWidgetBlueprint
/Script/UnrealEd.BaseWidgetBlueprint
/Script/UMGEditor.WidgetBlueprint
/Script/Blutility.EditorUtilityWidgetBlueprint
```
즉 **`UWidgetBlueprint`류 클래스 자체는 리플렉션에 정상 존재**한다 — 문제는 이걸 다루는 전용 MCP 툴이 없다는 것이지, 엔진에 그 개념이 없는 게 아니다.

### 2-2. `BlueprintTools.create` 스키마 분석 (완료·실제 호출은 미도달)

```json
{
  "folder_path": "string",
  "asset_name": "string",
  "asset_type": {"refPath": "<Class soft path>"}
}
→ returnValue: {"refPath": "<Blueprint soft path>"}  // 출력 타입이 /Script/Engine.Blueprint로 고정
```
출력 타입이 **항상 `/Script/Engine.Blueprint`로 고정**돼 있다는 점은 [[A0_CSV파이프라인스파이크]]가 struct 생성 가능성을 검토할 때도 동일하게 지적한 특징이다 — 이는 이 툴이 범용 `FKismetEditorUtilities::CreateBlueprint` 계열(부모클래스만 바꿔 일반 UBlueprint를 생성)로 구현됐을 가능성을 시사하며, `asset_type`이 "만들 애셋의 종류(WidgetBlueprint냐 일반 Blueprint냐)"가 아니라 "새 Blueprint의 **부모 클래스**"로 쓰일 개연성이 있다(스키마상의 추정, 실제 호출로 검증 못함 — 아래 §2-3 참조). 이게 맞다면:
- `asset_type=/Script/UMG.UserWidget`(부모클래스 방식)으로 시도하는 게 정공법일 가능성.
- `asset_type=/Script/UMGEditor.WidgetBlueprint`(2-1에서 찾은 "애셋 컨테이너 클래스" 자체를 넣는 방식)는 개념적으로 안 맞을 수 있음(부모클래스 자리에 Blueprint 컨테이너 클래스를 넣는 셈) — 이 조합이 바로 §2-3에서 관찰된 것과 같은 계열의 "부적절한 클래스 → 모달 다이얼로그" 위험을 유발할 수 있다는 가설(미검증, 이월).

이 두 후보(및 `WidgetBlueprint`류 4종 전부)를 **여러 개 순차로 실제 호출해 뭐가 되고 안 되는지 확인하는 것이 계획**이었으나, 첫 실제 호출 시도(폴더 존재 확인) 단계에서 §2-3의 차단에 걸려 **단 한 번도 `create`를 호출하지 못했다.**

### 2-3. 실제 생성 시도 → 인프라 차단 (진입 직전 차단, 내가 발동한 게 아님)

절차대로 `create` 호출 전에 대상 폴더(`/Game/UI/Components`)가 실존하는지 `AssetTools.list_folders`로 먼저 확인하려 했다:

| 호출 | 결과 |
|---|---|
| `list_folders(root_path="/Game/UI", recursive=true)` | 타임아웃 |
| `list_folders(root_path="/Game/UI", recursive=true)` (재시도) | 타임아웃 |
| `exists(path="/Game/UI/Components")` | 타임아웃 |
| `exists(path="/Game/UI/Components")` (재시도) | **`MCP server "unreal-mcp" is not connected`** |
| `list_toolsets()` (연결 자체 재확인, 수 분 간격으로 2회) | 둘 다 동일 에러 |

**원인 진단(직접 실행한 것)**:

| 확인 항목 | 방법 | 결과 |
|---|---|---|
| 에디터 프로세스 생존 | `Get-Process -Id 31200` | `Responding=True` — OS 메시지펌프는 살아있음(완전 크래시/데드락은 아님) |
| 엔진 로그 최신 활동 | `projectTP.log` tail + 파일 크기/mtime 추적 | 마지막 `LogModelContextProtocol` dispatch 라인이 **UTC 07:28:31(KST 16:28:31) `editor_toolset.toolsets.blueprint.BlueprintTools.create`에서 정지**, 이후 13분+ **단 한 줄도 추가되지 않음**(파일 4994줄 고정, `Get-Item.LastWriteTime`도 07:28:32 고정) — 평소 5~7분 간격으로 찍히던 `LogEOSSDK` 주기 tick조차 완전히 멈춤. 엔진의 정상 프레임/틱 기반 백그라운드 작업 전체가 정지한 것으로 판단. |
| 로그상 "낯선" 호출 존재 | 07:26~07:28 구간 상세 대조 | `list_toolsets`×3, `describe_toolset`×15, `data_table.DataTableTools.search_row_structs`×2, `material_instance.MaterialInstanceTools.list_parameters`×1(`/Game/Materials/M_Sprite_Flipbook_Lit` 대상 `LogScript` 경고 동반) 등 **이 세션에서 내가 호출한 적 없는 툴 호출**이 다수 확인됨 → 동시에 다른 MCP 클라이언트 세션이 같은 서버에 접속해 있었음이 사실상 확정. |
| 다른 스파이크와의 시점 대조 | [[A0_CSV파이프라인스파이크]] 원문 대조 | 그 문서도 **정확히 같은 시간대(UTC 07:26~07:28)**에 동일 증상("not connected", 로그에 자기가 안 부른 호출들 다수, `get_execution_environment`/`find_assets`×2/`MaterialInstanceTools.list_parameters` 등)을 독립적으로 보고했고, **그 세션 자신의 마지막 호출도 `BlueprintTools.create(asset_type=UserDefinedStruct)`**였다 — 즉 이번 스파이크와 그 스파이크가 **동시에 실행되며 같은 공유 브릿지를 두고 충돌**했고, 로그의 마지막 `create` dispatch는 그 세션(또는 제3의 동시 세션)의 호출일 개연성이 매우 높다(내 자신의 `create` 호출은 이 시점까지 단 한 번도 발동되지 않았음 — 위 표에서 확인). |
| **모달 다이얼로그 직접 확인(신규 증거, CSV 스파이크엔 없던 부분)** | Win32 `EnumWindows`(PID 31200 소유 윈도우 전수) | 제목 **"메시지"**, class **`UnrealWindow`**, hWnd `0x2E0852`, 가시(visible)·활성(enabled) 상태의 윈도우가 메인 에디터 창(hWnd `0x2B0B72`, "projectTP - 언리얼 에디터")의 **소유(owned) 윈도우**로 열려 있음을 확인. rect `(606,435)-(1100,584)`(494×149px, 전형적인 짧은 메시지+버튼 1개짜리 다이얼로그 크기). **13분+ 경과 후에도 `IsWindow=true`로 계속 존재**(수 차례 재확인). |
| 다이얼로그 내용 판독 시도 | `EnumChildWindows(0x2E0852)` | **자식 윈도우 0개** — Slate가 텍스트/버튼을 네이티브 Win32 컨트롤로 노출하지 않음(자체 렌더링). |
| 다이얼로그 내용 판독 시도(2) | `System.Windows.Automation.AutomationElement.FindAll(Descendants)` | **자식 엘리먼트 0개** — UI Automation 접근성 트리도 비어 있음(이 엔진 빌드에서 Slate 접근성이 노출되지 않는 것으로 추정). |

**결론(정황 근거지만 신뢰도 높음)**: `BlueprintTools.create`가 (Widget 계열이든 UserDefinedStruct든) "일반적이지 않은" `asset_type`으로 호출되면 엔진 내부에서 **블로킹 네이티브 모달 다이얼로그**(제목 "메시지")를 띄우는 경로를 타는 것으로 강하게 추정된다. 이 모달은 Slate의 중첩 이벤트루프 안에서만 돌기 때문에 OS 레벨에서는 "Responding"이지만, **엔진의 정상 틱/MCP 커맨드 디스패치는 완전히 멎는다** — 그리고 이 MCP 브릿지는 (최소한 이번 관찰상) **단일 커맨드 큐를 여러 클라이언트가 공유**하는 것으로 보여, 한 세션이 이 모달을 띄우면 **다른 모든 세션의 요청도 함께 마비**된다. 사람이 에디터에서 그 다이얼로그를 직접 닫아주기 전까지는 어떤 MCP 클라이언트도 복구 불가능해 보인다.

프로젝트 규칙("3회 실패 시 중단 → 아키텍처 재검토하고 Director 호출")에 따라 이 시점에서 재시도를 중단했다(list_folders 2회 + exists 2회 + list_toolsets 2회 = 총 6회 실패, 약 15분에 걸쳐 간격을 두고 시도). 다이얼로그를 직접 닫는 것(데스크톱 자동화 클릭)은 시도하지 않았다 — ①내용을 읽을 수 없어 어떤 버튼이 안전한지 불확실하고, ②공유 세션에 임의 입력을 주입하는 것은 이 프로젝트 관례상 Director 전용 영역(`언리얼_MCP_실전노하우.md` §6)이라 gameplay-engineer 권한 밖으로 판단했다.

### 2-4~6단계: 미실행

애셋 생성(`WBP_SpikeTest`) 자체가 안 됐으므로, `get_class`/`list_properties`로 애셋 구조 확인, `WidgetTree`/`RootWidget` 프로퍼티 조작 시도, 버튼+텍스트 배치, `add_component_bound_event`로 OnClicked 배선, `compile_blueprint` — **전부 시도조차 못 했다.**

다만 스키마 검토만으로 미리 확인해둔 것:
- **`ActorTools.add_component`는 구조적으로 위젯트리에 쓸 수 없을 가능성이 높다**(실제 호출로 검증은 못 함, 타입 추론): 이 툴의 반환 타입이 `/Script/Engine.ActorComponent`로 고정돼 있는데, UMG의 `UWidget`(Button/TextBlock 등)은 `UVisual : UObject` 계열이라 `UActorComponent`를 상속하지 않는다 — 즉 위젯을 "컴포넌트"로 붙이는 개념 자체가 이 엔진 클래스 계층과 안 맞는다. 위젯트리 조작이 필요하다면 `ObjectTools.set_properties`로 `WidgetTree`/`RootWidget` 프로퍼티에 구조체/오브젝트 레퍼런스를 직접 넣는 경로만 남는데, 이 경로는 전혀 실증 못 함.
- **`ProgrammaticToolset`도 우회로가 못 된다**: `get_execution_environment`로 확인한 결과 이 배치 실행기는 **이미 등록된 MCP 툴만 오케스트레이션** 가능하고(`execute_tool(tool_name, json)`), import 가능한 모듈은 `json/math/re/time/copy/datetime`뿐이라 **raw `unreal` 파이썬 모듈 접근이 원천 차단**돼 있다. 즉 전용 Widget 툴이 없는 이상 `WidgetTree`를 직접 코드로 조립하는 백도어도 없다 — 이번 스파이크가 실패하면 대안은 결국 "오너 수동 골격 생성"뿐이라는 뜻.

---

## 3. 판정 상세

명세 3분류에 억지로 끼워맞추지 않는다:
- **완전 성공 아님**: 애셋 생성·위젯트리 조작·컴파일 전부 미도달.
- **부분 성공 아님(명세가 정의한 의미로는)**: "애셋 생성은 되는데 위젯트리 조작이 막힘" 같은 **기술적 한계**가 드러난 게 아니라, **툴 호출 자체가 인프라 문제(공유 브릿지 마비)로 실행되지 못함**.
- **완전 실패 아님**: "asset_type 후보를 다 시도해봤는데 전부 에러"라서 막힌 게 아니다 — 단 하나의 `create` 후보도 실제로 시도하지 못했다. `WidgetBlueprint`류 클래스가 실제로 만들어지는지/안 만들어지는지 자체가 미확인이므로, 지금 "오너 수동 골격 필요"로 단정하는 건 시기상조.
- **실제 상태 = 미완료(인프라 차단)**, [[A0_CSV파이프라인스파이크]]와 동일 계열의 결론.

**단, 이번 조사로 명세의 절반(1단계: 클래스/툴셋 탐색)은 확정적으로 끝났다** — 재개 시 2-1은 재조사 불필요, 바로 `create` 실호출부터 시작하면 된다.

---

## 4. 오너/Director를 위한 권고 조치

1. **최우선 — 물리적 차단 해제**: 이 문서 작성 시점(KST 16:41) 기준 `projectTP - 언리얼 에디터` 창에 **"메시지" 제목의 작은 팝업(494×149px)이 열려 있다.** 오너가 에디터를 직접 보고 그 창을 닫아야(또는 필요한 응답을 클릭해야) MCP 브릿지가 복구될 것으로 추정된다. 복구 후 `list_toolsets()` 같은 무해한 호출로 연결을 먼저 재확인할 것.
2. **동시 세션 직렬화 검토**: [[A0_CSV파이프라인스파이크]]와 이 스파이크가 **같은 시간대에 같은 공유 에디터를 향해 동시 실행**되며 서로의 요청을 마비시켰을 개연성이 높다(로그상 교차오염 확정, 인과관계는 추정). MCP 브릿지가 다중 세션을 안전하게 격리하지 못하는 것으로 보이므로, **당분간 여러 에이전트가 unreal-mcp를 동시에 쓰지 않도록 조율(직렬화)**하는 걸 권고한다.
3. **재개 절차**: 연결 복구 확인 후 `BlueprintTools.create(folder_path="/Game/UI/Components", asset_name="WBP_SpikeTest", asset_type={"refPath": "/Script/UMG.UserWidget"})`부터 시도할 것을 제안한다(부모클래스 해석 가설 기준 — §2-2 참고, 확신도는 중간). 실패하면 `/Script/UMGEditor.WidgetBlueprint` 등 나머지 3종도 순차로(**병렬 아님** — 이번 마비의 트리거 자체가 `create`였을 가능성이 있으므로, 한 번에 하나씩 시도하고 매 호출 후 응답이 정상 오는지 확인 후 다음으로 진행) 시도.
4. **모달 유발 위험 고지**: `create`에 "정상적인 blueprintable 부모클래스가 아닐 수 있는" `asset_type`(구조체·에디터 전용 클래스 등)을 넣으면 **블로킹 모달로 전체 브릿지가 죽을 수 있다**는 게 이번 세션(간접)+CSV 세션(직접)에서 공통 관찰됐다. 후속 세션은 이 위험을 인지하고, 한 번에 한 후보씩·재시도 전 반드시 연결 확인을 습관화할 것.
5. **생성된 테스트 애셋 없음**: 이번 세션에서는 `WBP_SpikeTest`를 포함해 어떤 애셋도 실제로 생성되지 않았다(create 호출 자체가 발동되지 못함) — "생성한 애셋 삭제 금지" 지침은 해당사항 없음. 기존 애셋(`ST_UI` 포함)도 전혀 조회 외 변조하지 않았다.
6. **`언리얼_MCP_실전노하우.md` 갱신 후보**: 이번에 확인된 "모달 다이얼로그로 인한 공유 브릿지 전면 마비 + Win32/UIA 둘 다로 내용 판독 불가" 패턴을 §19 함정으로 편입할 가치가 있다고 판단 — Director 확인 후 편입 권장(이 스파이크 문서에서는 편입까지 하지 않고 후보로만 제안).

---

## 5. 사용한 MCP 툴 스키마 메모 (재개 시 참고용)

- `ObjectTools.search_subclasses(base_class: Class ref, class_name: string) -> Class[]` — `class_name`은 필수지만 빈 문자열 허용(전수 조회 가능, 이번에 확인).
- `AssetTools.find_assets(folder_path, name, asset_type?, recursive=true, tags?) -> string[]`
- `AssetTools.list_folders(root_path, recursive=true) -> string[]` — 이번엔 타임아웃으로 결과 미확보.
- `AssetTools.exists(path) -> bool` — 이번엔 타임아웃/연결끊김으로 결과 미확보.
- `BlueprintTools.create(folder_path, asset_name, asset_type: Class ref) -> Blueprint ref`(출력 타입 `/Script/Engine.Blueprint`로 고정 — WidgetBlueprint 전용 팩토리를 타는지 미검증, 다음 재개 시 최우선 확인 대상).
- `BlueprintTools.get_default_object(blueprint) -> Object ref`, `list_variables`, `list_graphs` 등 — WBP 애셋에 대해 통하는지 미검증(일반 Blueprint 대상으로는 정상 동작하는 것으로 기존 세션들에서 이미 다수 실증됨).
- `ActorTools.add_component(owner, component_type: Class ref, name) -> ActorComponent ref` — 반환 타입이 `ActorComponent`로 고정돼 있어 `UWidget`(UMG) 계열엔 구조적으로 부적합해 보임(미검증 추론, §2-4 참고).
- `ProgrammaticToolset.execute_tool_script` — 등록된 툴만 오케스트레이션, `unreal` 모듈 직접 접근 불가(허용 모듈: `json/math/re/time/copy/datetime`) — Widget 전용 백도어 없음.

### 확보한 클래스 refPath 후보 (재개 시 그대로 사용 가능)
```
/Script/UMG.UserWidget                          # UserWidget 부모클래스(런타임)
/Script/UMG.UserWidgetBlueprint                  # WidgetBlueprint 후보 1
/Script/UnrealEd.BaseWidgetBlueprint              # WidgetBlueprint 후보 2
/Script/UMGEditor.WidgetBlueprint                 # WidgetBlueprint 후보 3 (정공법으로 가장 유력)
/Script/Blutility.EditorUtilityWidgetBlueprint    # WidgetBlueprint 후보 4 (에디터 전용, 런타임 UI엔 부적합할 수 있음)
```

---

## 6. 이월 과제 (후속 조사)

1. **최우선**: `BlueprintTools.create`로 실제 `WBP_SpikeTest`가 생성되는지 — 4종 클래스 후보 중 어느 것이 성공하는지, 성공 시 실제 애셋 클래스가 `WidgetBlueprint`인지 아니면 그냥 부모클래스만 다른 일반 `Blueprint`인지(=디자인 타임 위젯트리 편집기가 없는 무용지물인지) 확정.
2. 생성 성공 시 `ObjectTools.set_properties`로 `WidgetTree`/`RootWidget` 프로퍼티에 자식 위젯(Button/TextBlock/CanvasPanel)을 실제로 심을 수 있는지 — 구조체/오브젝트 참조 형태 조작 문법부터 실증 필요.
3. `add_component_bound_event`(컴포넌트 바운드 이벤트)가 Button의 `OnClicked` 같은 델리게이트에도 통하는지(현재 스키마상 `component` 파라미터가 `ActorComponent` 타입으로 고정돼 있어 Button이 여기 해당하는지부터 불확실).
4. 이번 세션의 "모달로 인한 공유 브릿지 전면 마비" 근본 메커니즘(어떤 정확한 `asset_type` 조건이 모달을 유발하는지) — 재현 시 이번처럼 즉시 차단되지 말고, **가능하면 오너가 에디터를 지켜보는 상태에서 1회씩** 시도해 다이얼로그 문구를 육안으로 확보하는 게 근본원인 규명에 결정적일 것.
5. Slate 모달 콘텐츠를 스크린샷 없이 기계적으로 읽는 방법 — 이번엔 Win32/UIA 둘 다 실패했다. UE 자체의 접근성(Accessibility) 기능을 프로젝트 설정에서 켜면 UIA 트리가 노출되는지는 미검증(엔진 설정 변경이 필요해 이번 스파이크 범위 밖으로 판단, 별도 조사 과제로 이월).

---

## 7. 재개 실행 결과 (2026-07-10, MCP 단독 세션)

> Director가 `BlueprintTools.create(asset_type=UserDefinedStruct)`를 직접 1회 호출해 300초 무응답(모달)을 재현·확정한 뒤(§19 함정㉓ 확정), 이 스파이크를 **단독 세션**(동시 사용 없음)으로 재개했다. §2-1에서 확보한 클래스 후보를 그대로 사용해 2단계(실제 `create` 호출)부터 시작했다.

### 7-0. 재개 전 연결 확인

- `list_toolsets()` — 정상 응답(21개+ 툴셋, 1차 세션 목록과 일치 + `BehaviorTreeTools` 추가 확인). Widget/UMG 이름의 툴셋은 이번에도 0개.
- `describe_toolset(editor_toolset.toolsets.blueprint.BlueprintTools)` → `create` 툴 정식 스키마 재확인: `asset_type`은 "The specific kind of Blueprint to make."(§5 메모와 일치, `folder_path`/`asset_name`/`asset_type` 3개 필수 파라미터).

### 7-1. `create` 1회 호출 — 분기 B 확정(모달 미발생)

```
create(folder_path="/Game/UI/Components", asset_name="WBP_Probe", asset_type={"refPath":"/Script/UMG.UserWidget"})
→ {"returnValue":{"refPath":"/Game/UI/Components/WBP_Probe.WBP_Probe"}}
```

**즉시 정상 응답, 무응답·모달 0건.** 절차서가 우려한 "UserWidget도 UserDefinedStruct처럼 모달을 유발할 수 있다"는 가설은 **기각됐다** — Blueprintable UObject(UserWidget)는 non-Blueprintable 구조체(UserDefinedStruct)와 달리 `BlueprintTools.create`의 정상 경로를 탄다. 이 1회 호출 이후 이번 세션에서 `create`는 다시 호출하지 않았다(지침 준수).

### 7-2. 실제 애셋 클래스 판별 — WidgetBlueprint 확정

| 호출 | 결과 | 해석 |
|---|---|---|
| `AssetTools.get_asset_class(/Game/UI/Components/WBP_Probe)` | `"WBP_Probe_C"` | **생성된 클래스명**을 반환(컨테이너 타입 아님) — 이 툴 자체 설명 예시("HeroCharacter_C")와 일치하는 설계된 동작으로, Blueprint 자산에 대해 컨테이너가 아닌 생성된 클래스를 보고함 |
| `ObjectTools.get_class({"refPath":".../WBP_Probe.WBP_Probe"})` | `.../WBP_Probe.WBP_Probe_C` | 동일하게 생성된 클래스로 리다이렉트. 이후 `get_properties` 에러 메시지(`'/Game/UI/Components/WBP_Probe.Default__WBP_Probe_C'`)로 **이 ref가 내부적으로 생성 클래스의 CDO로 리졸브됨**을 확인 — 이 레이어는 Blueprint ref를 "런타임 인스턴스"처럼 추상화하는 것으로 판단됨 |
| **`AssetTools.find_assets(folder_path="/Game/UI/Components", name="WBP_Probe", asset_type={"refPath":"/Script/UMGEditor.WidgetBlueprint"})`** | `["/Game/UI/Components/WBP_Probe"]` **매치** | **결정적 증거 — 애셋 레지스트리 기준 실제 클래스가 `/Script/UMGEditor.WidgetBlueprint`** |
| 네거티브 컨트롤: 동일 호출을 `asset_type={"refPath":"/Script/Blutility.EditorUtilityWidgetBlueprint"}`(형제클래스, §5의 후보4)로 | `[]` 매치 없음 | 필터가 허위양성이 아님을 확인 — 형제 클래스는 정확히 배제됨. 위 매치가 신뢰할 수 있는 근거임을 뒷받침 |
| `BlueprintTools.get_parent({"refPath":".../WBP_Probe.WBP_Probe"})` | `{"refPath":"/Script/UMG.UserWidget"}` | 요청한 부모클래스가 정확히 설정됨 |
| `BlueprintTools.compile_blueprint({"refPath":".../WBP_Probe.WBP_Probe"})` | 에러 없음(`returnValue: null`) | 정상 컴파일되는 유효한 Blueprint(껍데기가 아님) |
| `BlueprintTools.list_graphs({"refPath":".../WBP_Probe.WBP_Probe"})` | `[".../WBP_Probe.WBP_Probe:EventGraph"]` | 정상적인 Blueprint 편집 구조(EventGraph) 존재 |
| `BlueprintTools.list_variables({"refPath":".../WBP_Probe.WBP_Probe"})` | `[]` | 정상 응답(변수 없음, 에러 아님) — 이 API가 WBP 애셋에도 정상 동작함을 확인(§5 이월 항목 해소) |

**판정**: `BlueprintTools.create(asset_type=/Script/UMG.UserWidget)`는 **진짜 `WidgetBlueprint` 애셋을 생성한다** — §2-2의 "부모클래스 해석" 가설이 맞았을 뿐 아니라, 생성물이 껍데기만 다른 일반 `Blueprint`가 아니라 애셋 레지스트리가 인식하는 정식 `UMGEditor.WidgetBlueprint` 컨테이너임을 `asset_type` 필터(양성+음성 대조)로 직접 실증했다. `get_asset_class`/`get_class`가 "생성된 클래스명"을 보고하는 것은 이 판별과 무관한 별개의 설계된 추상화였다(오판 방지를 위해 기록).

### 7-3. 위젯트리 조작 가능성 — 여기서 막힘(정확한 차단 지점 특정)

| 호출 | 결과 |
|---|---|
| `ObjectTools.list_properties({"refPath":".../WBP_Probe.WBP_Probe"})` | `UWidget` 계열 프로퍼티 약 30개 반환(`colorAndOpacity`, `visibility`, `slot`, `navigation`, `renderTransform`, `toolTipWidget` 등) — **`WidgetTree`/`RootWidget`은 목록에 없음** |
| `ObjectTools.get_properties(..., properties=["WidgetTree","RootWidget"])` | 에러: `the following properties could not be read: WidgetTree, RootWidget` |
| 동일 호출을 camelCase(`["widgetTree","rootWidget"]`)로 재시도 | 동일 에러 — **네이밍 컨벤션 문제가 아님을 확인** |
| `ObjectTools.set_properties({"refPath":".../WBP_Probe.WBP_Probe"}, values='{"widgetTree": null}')` | 에러: `the following properties could not be set: widgetTree` — **쓰기도 동일하게 불가** |
| **`ObjectTools.get_class({"refPath":".../WBP_Probe.WBP_Probe:WidgetTree"})`**(서브오브젝트 경로 표기, `list_graphs`의 `:EventGraph` 표기에서 착안) | **`{"refPath":"/Script/UMG.WidgetTree"}`로 정상 리졸브됨** — 오브젝트 자체는 실존하고 개별 주소 지정 가능함을 확인 |
| `ObjectTools.list_properties({"refPath":".../WBP_Probe.WBP_Probe:WidgetTree"})` | 빈 문자열(`""`) — 노출된 프로퍼티 0개(에러는 아님, 정상적으로 "없음") |
| `ObjectTools.get_properties({"refPath":".../WBP_Probe.WBP_Probe:WidgetTree"}, properties=["rootWidget"])` | 에러: `could not be read: rootWidget` — 서브오브젝트를 직접 찍어도 동일하게 막힘 |
| `ObjectTools.get_class({"refPath":".../WBP_Probe.WBP_Probe:WidgetTree:RootWidget"})`(2단 체이닝 시도) | 파라미터 에러: `is not valid Object for property 'instance'` — 체이닝 미지원(안전한 실패, 인프라 영향 없음) |

**막힌 지점 특정**: `WidgetTree`(및 그 안의 `RootWidget`)는 C++ 상 `Transient`+non-Edit 지정 프로퍼티로 추정되며, `ObjectTools`의 `list_properties`/`get_properties`/`set_properties`가 공통으로 사용하는 프로퍼티 가시성 필터(디테일 패널 노출 기준과 유사한 것으로 추정)를 통과하지 못해 **read·write 모두 불가**하다. `WidgetTree` 오브젝트 자체는 서브오브젝트 경로(`:WidgetTree`)로 개별 존재 확인까지는 가능하지만, 그 안의 `RootWidget`이나 다른 프로퍼티로는 어떤 방식으로도 진입하지 못했다. 자식 위젯(Button/TextBlock)을 추가하려면 최소한 `RootWidget`을 읽거나 쓸 수 있어야 하는데 그 경로 자체가 막혀 있어 **위젯 배치의 다음 단계(신규 Button/TextBlock 인스턴스 생성 및 트리 삽입)는 시도할 방법조차 찾지 못했다.**

전용 Widget/UMG MCP 툴셋 부재(1차 세션 §2-1에서 확정, 이번 세션 `list_toolsets`로 재확인 — 여전히 0개)와 종합하면, **위젯트리 조작의 유일한 후보 경로(`ObjectTools` 프로퍼티 조작)가 실제로 막혀 있음이 실증**됐다. `ActorTools.add_component`가 구조적으로 부적합하다는 1차 세션의 스키마 기반 추론(§2-4, `UWidget`이 `UActorComponent`를 상속하지 않음)은 이번 세션에서 재검증하지 않았으나(반환 타입 고정이라는 명확한 스키마 근거가 이미 있어 실호출 불필요로 판단), 결론에 영향 없음.

### 7-4. 애셋 저장

`WBP_Probe`는 생성 직후 dirty 상태(`AssetTools.is_dirty` → `true`)였다. "생성된 애셋은 남겨둬라"는 지침에 따라 `AssetTools.save_assets(["/Game/UI/Components/WBP_Probe"])`로 디스크에 저장했고, 저장 후 `is_dirty` → `false`로 확인했다. 기존 애셋(`ST_UI` 등)은 조회조차 하지 않았다 — 무변조.

### 7-5. 최종 판정 — 부분성공

- **완전성공 아님**: 위젯트리에 자식 위젯(Button/TextBlock)을 실제로 심는 것까지는 도달하지 못함.
- **폴백확정(완전실패) 아님**: `create` 자체는 대성공 — 모달 0건, 진짜 `WidgetBlueprint` 생성을 `asset_type` 필터로 직접 확인.
- **부분성공**:
  - 성공한 것 — ① `create`가 안전하게 동작(모달 없음, §19 함정㉓의 "UserWidget도 위험할 수 있다"는 우려 기각) ② 생성물이 진짜 `/Script/UMGEditor.WidgetBlueprint`(껍데기만 다른 일반 Blueprint 아님, 양성+음성 대조로 확정) ③ 정상 컴파일·`EventGraph` 존재·`list_variables`/`get_parent` 등 기존 BP 툴 정상 작동.
  - 막힌 것 — `ObjectTools`의 프로퍼티 read/write API로는 `WidgetTree`/`RootWidget`에 접근 불가(읽기·쓰기 전부 에러, camelCase/PascalCase 무관, 서브오브젝트 경로로도 `RootWidget`까지는 못 들어감). 전용 Widget MCP 툴셋은 여전히 없음.

**즉 "WBP 애셋 골격(빈 껍데기)은 MCP로 안전하게 만들 수 있으나, 그 안에 디자인타임 위젯(Button/TextBlock 등)을 MCP만으로 채워 넣는 것은 현재 노출된 MCP 표면적으로는 불가능"으로 확정.** 알파의 UMG 계획을 이 경로만으로 끝까지 실행할 수는 없다 — 위젯트리 구성(레이아웃 배치)부터는 오너가 에디터에서 직접 하거나, cpp-engineer가 전용 브릿지를 추가해야 한다.

### 7-6. 후속 권고

1. 메뉴 UI의 WBP 애셋 **골격 생성 자동화**(`create` + `compile_blueprint` + `save_assets`)는 MCP로 안전하게 가능 — 확정. 여러 화면의 빈 WBP 골격을 일괄 생성하는 용도로는 바로 활용 가능.
2. 그 안의 실제 레이아웃(Button/TextBlock/CanvasPanel 배치, 앵커/사이즈 조정)은 **오너가 UMG 디자이너에서 수동으로** 해야 한다 — 이번에 검증된 MCP 표면으로는 불가능함이 명확히 실증됨(7-3).
3. `BlueprintTools.add_component_bound_event`가 Button의 `OnClicked` 델리게이트에 통하는지는 여전히 미검증이다(위젯을 심을 방법 자체가 없어 테스트 대상이 없었음) — 오너가 수동으로 위젯을 배치한 뒤, **기존 위젯에 대해** 이 이벤트 바인딩 툴이 통하는지는 별도로 재확인할 가치가 있다(이월).
4. `언리얼_MCP_실전노하우.md` §19 갱신 권고(Director 확인 후 편입): "`BlueprintTools.create`는 `UserDefinedStruct` 같은 non-Blueprintable 클래스에 쓰면 모달로 전체 브릿지가 마비되지만(함정㉓), `UserWidget`처럼 정상 Blueprintable 부모클래스는 안전하게 동작하고 실제 `WidgetBlueprint`를 만든다. 단, 만들어진 뒤 `WidgetTree`/`RootWidget` 프로퍼티는 `ObjectTools`의 get/list/set_properties로 접근 불가(read/write 모두 막힘) — 서브오브젝트 경로(`:PropName`)로 오브젝트 존재 확인까지는 가능하나 그 이상 진입 못 함."
5. 생성된 애셋: `/Game/UI/Components/WBP_Probe`(저장 완료, dirty 아님) — 후속 검증이나 재조사에 재사용 가능하도록 삭제하지 않고 남겨뒀다.
