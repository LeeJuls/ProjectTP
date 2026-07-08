---
type: raw
project: projectTP
feature: 캐릭터시스템
agent: gameplay-engineer
updated: 2026-07-08
---

# A0 기술 스파이크 — strings.csv → UE DataTable 임포트 실증

> `Resource/data/strings.csv`(git 추적)를 UE DataTable로 임포트하고 런타임 조회가 가능한지 확인하는 A0 스파이크. **최종 판정: 미완료(인프라 차단) — 절차 도중 unreal-mcp 연결이 끊겨 4~7단계를 실행하지 못함.** 상위: [[projectTP_허브]]
#projectTP/캐릭터시스템

---

## 최종 판정 (한 줄)

**"완전 성공/부분 성공/완전 실패" 3분류 중 어디에도 속하지 않는 4번째 상태 — 절차 1단계(기존 struct 재사용 가능성 확인)는 실행·확정했으나, 2단계(커스텀 struct 생성 시도)를 실제로 실행하기 직전 unreal-mcp MCP 연결이 끊겨 이후 전 단계(2 실행~7)를 수행하지 못했다.** 이는 "struct를 못 만든다"는 논리적 결론이 아니라 **도구 접속이 끊겨 시도 자체를 못 한 상태**이므로, 명세가 정의한 "완전 실패"(오너 수동 부트스트랩 폴백 필요)로 단정하지 않는다 — MCP 연결 복구 후 동일 절차 재개를 권장한다.

---

## 핵심 발견 (3줄)

1. **1단계 확정 완료**: `search_row_structs(struct_name="*")`로 엔진+프로젝트 전체의 TableRowBase 서브클래스를 전수 조회한 결과 15개(전부 `/Script/...` 엔진/플러그인 네이티브 struct, `/Game/` 경로 프로젝트 struct는 0개) — `Key,ko,ja,en`(전부 문자열) 스키마에 맞는 기존 struct는 **없음**을 확정. `"*String*"` 필터도 0건.
2. **2단계는 착수만 하고 실행 직전 차단됨**: `ObjectTools.search_subclasses`로 커스텀 struct 후보 클래스 `/Script/CoreUObject.UserDefinedStruct`는 확인했으나, 이름에 "StructFactory"가 들어간 클래스는 검색되지 않았다. `BlueprintTools.create`의 출력 스키마가 **항상 `/Script/Engine.Blueprint` 타입으로 고정**되어 있어(Blueprint 전용 팩토리로 추정), UserDefinedStruct 애셋 생성에 실제로 쓰일 수 있는지는 **미검증**(실제 호출이 "MCP server not connected" 에러로 실패, 로그상 서버에 도달조차 못 함 — 도구 자체의 거부가 아니라 전송 계층 단절).
3. **MCP 연결 단절 근본원인 정황**: UnrealEditor.exe(PID 31200)는 정상 실행 중(Responding=True), TCP 8000 포트는 `Test-NetConnection`으로 연결 성공 확인 — 즉 **엔진/MCP 서버 프로세스 자체는 살아있음**. 그러나 이 세션의 반복 `list_toolsets`/`create` 호출은 전부 "not connected"로 즉시 실패했고, 엔진 로그(`projectTP.log`)에 해당 실패 호출들의 dispatch 기록이 전혀 없음(클라이언트가 서버에 도달하기 전에 끊긴 것으로 추정). 결정적으로, 로그 말미(UTC 07:26~07:28, 로컬 16:26~16:28)에 **내가 호출한 적 없는 도구 호출들**(`get_execution_environment`, `AssetTools.find_assets`×2, `MaterialInstanceTools.list_parameters`(대상: `M_Sprite_Flipbook_Lit`))이 남아 있어, **동시에 다른 MCP 클라이언트 세션이 같은 서버에 접속해 있었을 가능성**이 유력한 근본원인 후보다(세션 충돌/치환으로 내 연결이 끊겼을 가능성). 근본 메커니즘은 미규명(후속 조사 과제).

---

## 1. 배경 · 목표

알파는 게임 데이터를 CSV(git 추적, `Resource/data/`)로 관리하고 UE DataTable로 임포트해 쓰는 방침이다(`알파_개발계획.md` §2.5·2.55 — uasset은 Content/가 git 제외라 버전관리 불가가 근거). 이 스파이크는 `DataTableTools.import_file`이 CSV를 직접 DataTable로 임포트할 수 있는지, 특히 **schema 파라미터에 필요한 TableRowBase 서브클래스 struct를 프로젝트에 아직 갖고 있지 않은 상태에서 MCP만으로 확보 가능한지**를 실증하는 것이 핵심 미지수였다.

### 대상 파일
`D:\unreal\Resource\data\strings.csv` — 24행(헤더 포함), 컬럼 `Key,ko,ja,en`. `ja`/`en` 컬럼은 현재 전부 빈 값, `ko`만 채워짐. 예: `Job.Warrior,전사,,` / `Skill.Slash,베기,,` / `Skill.Slash.Desc,대상에게 공격력의 130퍼센트 물리 피해. 쿨다운 1턴.,,`.

### 안전수칙 (사전 확인)
`언리얼_MCP_실전노하우.md` §18 함정 ㉑을 사전에 확인함 — 기존 애셋과 같은 경로에 `import_file`을 재시도하면 실패 에러를 반환하면서도 **부작용으로 기존 애셋을 무음 삭제**한 전례(ST_UI 사고)가 있다. 이번 스파이크는 대상 경로(`/Game/Data/DT_Strings_SpikeTest*`)에 기존 애셋이 전혀 없는 **최초 생성**이라 이 함정과 무관하지만, 절차 문서에 재차 명시된 대로 "혹시 재시도 시 delete→create 순서 준수"를 계획에 반영해뒀다(실제로는 이 스파이크가 2단계 진입 전에 중단되어 `import_file` 자체를 호출하지 않았으므로 이 위험은 발생하지 않았음).

---

## 2. 실행한 절차와 결과

### 2-1. 기존 struct 재사용 가능성 확인 (완료)

`DataTableTools.search_row_structs(struct_name="*")` 호출 결과 (전체 15건, 전수):

```
/Script/GameplayTags.GameplayTagTableRow
/Script/GameplayTags.RestrictedGameplayTagTableRow
/Script/UMG.RichTextStyleRow
/Script/UMG.RichImageRow
/Script/Engine.MLLevelSetModelAndBonesBinningInfo
/Script/Engine.MLLevelSetModelInferenceInfo
/Script/Engine.MirrorTableRow
/Script/MassEntityTestSuite.FarmVisualDataRow
/Script/Synthesis.ModularSynthPreset
/Script/PCG.PCGAnimBankDataRow
/Script/NNEDenoiser.NNEDenoiserBaseMappingData
/Script/NNEDenoiser.NNEDenoiserInputMappingData
/Script/NNEDenoiser.NNEDenoiserOutputMappingData
/Script/NNEDenoiser.NNEDenoiserTemporalInputMappingData
/Script/NNEDenoiser.NNEDenoiserTemporalOutputMappingData
```

전부 엔진/플러그인 네이티브 struct이고, 4개 문자열 컬럼(`Key,ko,ja,en`)에 대응하는 구조가 하나도 없다(GameplayTagTableRow는 태그 1개, RichTextStyleRow/RichImageRow는 UI 스타일용, 나머지는 ML/PCG/오디오 등 전혀 무관한 도메인). `"*String*"` 부분일치 필터로 재검색해도 **0건**.

**부가 확인**: 이 전수 검색 결과에 `/Game/` 경로(프로젝트 자산)가 단 하나도 없다는 사실 자체가, 명세 2단계의 "다른 프로젝트 폴더(`/Game/Data/`)에 이미 뭔가 구조체 비슷한 게 있는지" 확인도 겸한다 — **TableRowBase 서브클래스로 등록된 프로젝트 struct는 현재 0개**로 확정.

**판정**: 기존 struct 재사용 **불가**. 커스텀 struct 신규 생성이 필요.

### 2-2. 커스텀 struct 생성 시도 (착수만 함, 실행 전 차단)

`BlueprintTools.create`가 명세에서 제안한 "struct 팩토리 클래스를 asset_type에 넣어보는" 경로의 후보로 지목됐다. 실제 호출 전에 두 가지를 확인했다:

1. **`BlueprintTools.create`의 스키마**:
   ```json
   {
     "inputSchema": {"folder_path": "string", "asset_name": "string", "asset_type": "/Script/CoreUObject.Class 레퍼런스"},
     "outputSchema": {"returnValue": "/Script/Engine.Blueprint 레퍼런스"}
   }
   ```
   출력 타입이 **`/Script/Engine.Blueprint`로 고정**되어 있다. 이는 이 툴이 "asset_type을 부모클래스로 하는 새 Blueprint(UBlueprint 애셋)를 만드는" 용도로 설계됐을 가능성이 높음을 시사한다(즉 asset_type은 "생성할 애셋의 팩토리·타입"이 아니라 "새 Blueprint의 부모 클래스"일 개연성). 다만 이는 스키마 구조로부터의 추정이며, **실제 호출로 검증하지 못했다**(아래 2-3 참조).

2. **`ObjectTools.search_subclasses`로 struct 관련 후보 클래스 탐색**:
   - `base_class=/Script/CoreUObject.Object, class_name="UserDefinedStruct"` → 4건: `/Script/CoreUObject.UserDefinedStruct`, `/Script/CoreUObject.UserDefinedStructEditorDataBase`, `/Script/UnrealEd.UserDefinedStructEditorData`, `/Script/EngineAssetDefinitions.AssetDefinition_UserDefinedStruct`.
   - `base_class=/Script/CoreUObject.Object, class_name="StructFactory"` → **0건**(명세가 언급한 `/Script/UnrealEd.UserDefinedStructFactory` 계열 이름으로는 검색되지 않음. 정확한 클래스명이 다르거나, 이 검색 API가 UFactory 계열을 이 방식으로 노출하지 않을 가능성 — 둘 다 미확정).

### 2-3. 실제 생성 호출 시도 → MCP 연결 단절로 실패

가장 유력한 후보(`/Script/CoreUObject.UserDefinedStruct`)를 `asset_type`으로 넘겨 `BlueprintTools.create(folder_path="/Game/Data", asset_name="S_Strings_SpikeTest", asset_type={"refPath": "/Script/CoreUObject.UserDefinedStruct"})`를 호출했으나, 결과는:

```
Error: MCP server "unreal-mcp" is not connected
```

이후 가장 단순한 호출(`list_toolsets`, 파라미터 없음)로 연결 자체를 재확인했으나 **동일 에러가 10회 연속** 재현됐다(약 15분에 걸쳐 간격을 두고 재시도).

**원인 진단(실행한 것)**:
| 확인 항목 | 방법 | 결과 |
|---|---|---|
| 에디터 프로세스 생존 | `Get-Process -Id 31200` | `Responding=True` (정상) |
| MCP 서버 포트 리스닝 | `Get-NetTCPConnection -State Listen` | `127.0.0.1:8000` LISTEN, PID 31200(에디터)과 일치 |
| TCP 3-way handshake | PowerShell `Test-NetConnection -ComputerName 127.0.0.1 -Port 8000` | `TcpTestSucceeded=True` |
| bash 환경의 HTTP curl | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/` | `000`(연결 실패) — 단, bash 도구 자체의 네트워크 샌드박스 제약일 가능성 있어 이 결과 하나만으로 서버 이상을 단정하지 않음(SSE 프로토콜을 curl 단순 호출로 파싱 못하는 것은 §1 노하우에도 기존 기록된 알려진 제약) |
| 엔진 로그(`projectTP.log`) 최신 상태 | `LogModelContextProtocol` 태그 grep, 파일 라인 수 추적 | 마지막 dispatch 기록이 UTC 07:28:31(로컬 16:28:31)에서 멈춘 뒤, 이후 내가 실행한 반복 `list_toolsets` 시도들에 대응하는 **새 로그 라인이 전혀 추가되지 않음**(파일 라인 수 4993 고정) — 내 실패 호출들이 서버에 도달조차 못했음을 시사(클라이언트 측 전송 단절) |
| 로그상 "낯선" 호출 존재 여부 | 마지막 30여 줄 상세 확인 | `get_execution_environment`, `AssetTools.find_assets`×2, `MaterialInstanceTools.list_parameters`(`material` 인자에 `/Game/Materials/M_Sprite_Flipbook_Lit` 관련 `LogScript: Warning` 동반) 등 **이번 세션에서 내가 호출한 적 없는 툴 호출들**이 다수 확인됨 — 나의 실제 호출 순서(`list_toolsets`→`describe_toolset`×4→`search_row_structs`×2→`search_subclasses`×2→`create`)와 로그상 순서·개수가 불일치 |

**결론(정황 근거, 미확정)**: 엔진·포트·프로세스는 모두 정상인데 내 클라이언트만 지속적으로 "not connected"이고, 동시에 내가 호출하지 않은 툴 호출들이 로그에 남아있다는 점을 종합하면 **다른 MCP 클라이언트 세션이 같은 서버(포트 8000)에 동시 접속해 있었고, 그로 인해 내 세션이 치환되었거나 충돌했을 가능성**이 가장 유력한 가설이다. 다만 이 MCP 서버 구현이 다중 세션을 지원하는지, 세션 치환이 실제 메커니즘인지는 이번 조사로 확정하지 못했다(근본 메커니즘 미규명, 후속 조사 과제로 이월).

이 시점에서 프로젝트 규칙("3회 실패 시 중단 → 아키텍처 재검토하고 Director 호출")에 따라 재시도를 중단했다(총 10회 시도, 약 15분).

### 2-4~7단계: 미실행

`DataTableTools.create`(커스텀 struct로 빈 DataTable 생성), `DataTableTools.import_file`(CSV 임포트), `get_rows`/`list_rows`(검증), 런타임 조회 스캐폴드(BeginPlay + GetDataTableRow + PrintString + PIE) 전부 **시도조차 못 했다**. 아래는 명세가 요청한 "가상 struct 경로 가정 시뮬레이션 서술"이다(실제 실행 아님, 표시를 명확히 구분):

- (시뮬레이션) 4단계: `DataTableTools.create(folder_path="/Game/Data", asset_name="DT_Strings_SpikeTest", schema=<확보된 struct>)` — struct가 `Key/ko/ja/en` 4개 FString 필드를 가진다면 스키마상 문제없이 생성될 것으로 예상되나 미검증.
- (시뮬레이션) 5단계: `DataTableTools.import_file(folder_path="/Game/Data", asset_name="DT_Strings_SpikeTest2", source_file="D:\\unreal\\Resource\\data\\strings.csv", schema=<struct>)` — CSV 컬럼명이 `Key,ko,ja,en`인데 struct 필드명과 대소문자까지 정확히 일치해야 매핑될 가능성이 높다는 점은 명세의 경고대로이며, **이번 조사로 이 매핑 규칙 자체를 실증하지 못했다** — struct 필드명을 CSV 헤더와 정확히 동일하게(`Key`,`ko`,`ja`,`en`) 만드는 것을 최우선으로 시도해야 한다는 점만 권고로 남긴다.
- (시뮬레이션) 6단계: `get_rows`로 `Job.Warrior`/`Skill.Slash` 등 재조회 후 원본 CSV와 대조, `list_rows`로 전체 23개 데이터 행(헤더 제외) 수 일치 확인 — 미실행.
- (시뮬레이션) 7단계: BP_BattleManager 등에 임시 GetDataTableRow+PrintString 스캐폴드 삽입 → PIE → 로그 확인 → 스캐폴드 전량 제거(§9 원복 규율) — 미실행. 애초에 struct/DataTable 자체가 없어 스캐폴드를 심을 대상도 없음.

---

## 3. 판정 상세

명세가 정의한 3분류에 억지로 끼워맞추지 않고 아래처럼 정리한다:

- **완전 성공 아님**: 4~7단계 미실행.
- **부분 성공 아님**: "struct는 확보했지만 임포트 매핑 문제"처럼 구체적 기술 결함이 드러난 게 아니라, **툴 호출 자체가 인프라 문제로 실행되지 못함**.
- **완전 실패(명세가 정의한 의미) 아님**: 이 분류는 "struct 자체를 못 만듦(엔진 기본 struct도 안 맞음)"을 뜻하는데, 이번 조사가 확정한 것은 "**기존** struct는 없다"(1단계, 확정)와 "**신규 struct 생성은 시도조차 못 함**"(2단계, 미확정)이다. `BlueprintTools.create`가 실제로 UserDefinedStruct를 만들 수 있는지 없는지조차 실증하지 못한 채 중단됐으므로, 오너 수동 부트스트랩 폴백을 지금 확정 권고하는 것은 시기상조다.
- **실제 상태 = 미완료(인프라 차단)**: MCP 연결이 복구되는 대로 **2-3에서 멈춘 지점부터 그대로 재개**하는 것이 가장 효율적이다(1단계 결과는 재사용 가능, 재조사 불필요).

---

## 4. 오너/Director를 위한 권고 조치

1. **MCP 연결 복구 확인**: 이 스파이크를 재개하기 전에 `mcp__unreal-mcp__list_toolsets` 같은 최소 호출이 정상 응답하는지 먼저 확인. 만약 동시 세션 충돌이 원인이라면, **같은 시간대에 다른 에이전트/세션이 unreal-mcp를 동시 사용하지 않도록** 조율(직렬화)하는 것이 재발 방지책일 수 있다(단, 이번 조사로 다중 세션 충돌을 확정하지 못했으므로 재발 시 추가 근거 수집 필요).
2. **재개 시 다음 호출부터 시작**: `BlueprintTools.create(folder_path="/Game/Data", asset_name="S_Strings_SpikeTest", asset_type={"refPath": "/Script/CoreUObject.UserDefinedStruct"})`. 이 호출이 실패(로직적 거부)한다면 그 에러 메시지를 근거로 "MCP로 UserDefinedStruct 생성 불가"를 확정하고, 그때 비로소 명세의 "완전 실패" 폴백(오너가 에디터에서 최초 1회 수동으로 Table Row Struct 애셋 — 컬럼 Key/Ko/Ja/En, 전부 FString — 생성)을 권고한다.
3. **수동 폴백을 미리 준비해두는 것은 유효**: 위 재시도가 다시 실패하거나 반복 차단될 경우를 대비해, 오너가 에디터에서 수동으로 만들 struct 사양을 미리 확정해둔다 — 필드명은 CSV 헤더와 정확히 일치(`Key`, `ko`, `ja`, `en`, 전부 FString/Text), 부모는 `TableRowBase`. 이 스펙은 이번 조사(1단계)로 이미 확정된 정보이므로 재조사 불필요.
4. **생성된 테스트 애셋 없음**: 이번 세션에서는 struct/DataTable 어느 것도 실제로 생성되지 않았다(생성 호출이 인프라 에러로 실패) — "생성한 애셋 삭제 금지" 지침은 해당사항 없음(생성물 자체가 없음). 기존 애셋도 전혀 변조하지 않았다.

---

## 5. 사용한 MCP 툴 스키마 메모 (재개 시 참고용)

- `DataTableTools.search_row_structs(struct_name: string="*") -> ScriptStruct[]`
- `DataTableTools.create(folder_path, asset_name, schema: ScriptStruct ref) -> DataTable`
- `DataTableTools.import_file(folder_path, asset_name, source_file, schema: ScriptStruct ref) -> Object[]`
- `DataTableTools.get_rows(data_table, row_names: string[]) -> JSON string`
- `DataTableTools.list_rows(data_table) -> string[]`
- `ObjectTools.search_subclasses(base_class: Class ref, class_name: string) -> Class[]` — `class_name`은 **필수 파라미터**(부분일치 필터, 빈 문자열 허용 여부는 미확인).
- `BlueprintTools.create(folder_path, asset_name, asset_type: Class ref) -> Blueprint`(출력 타입 고정 — UserDefinedStruct 생성 용도로 실제 동작하는지 미검증, 다음 재개 시 최우선 확인 대상).

---

## 6. 이월 과제 (후속 조사)

1. `BlueprintTools.create`가 `asset_type=UserDefinedStruct`로 실제 UserDefinedStruct 애셋을 만들 수 있는지 실증(재개 1순위).
2. 이번 세션의 MCP 연결 단절 근본원인(동시 세션 충돌 가설) 검증 — 재현 시 어느 시점에 다른 세션이 접속했는지 로그 타임스탬프 상관관계로 추가 확인.
3. `import_file`의 CSV↔struct 필드 매핑 규칙(대소문자·정확 일치 요구 여부) 실증 — 이번엔 도달하지 못함.
