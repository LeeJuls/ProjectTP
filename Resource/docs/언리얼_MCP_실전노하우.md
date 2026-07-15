---
type: reference
project: projectTP
updated: 2026-07-15
---

# 🛠️ 언리얼 MCP 실전 노하우

> UE 5.8을 unreal-mcp로 조작하며 실제로 겪은 함정·해법·방법론. **UE MCP 작업 전 필독.**
> art-pipeline / scene-builder / hd2d-art-director / gameplay-engineer / verifier / cpp-engineer 공용.
> 관련: [[HD2D_기법_지식베이스]] · [[개발_워크플로우]] · [[UI_화면_규약]]
#projectTP/노하우

---

## 1. 스크린샷 확보 파이프라인 (필수 절차)

`CaptureViewport` / `CaptureAssetImage` / `CaptureEditorImage`의 base64 PNG는 **400~600만 자**라 에이전트 컨텍스트 토큰을 무조건 초과한다.

**표준 절차** (이것만 쓴다):
1. `call_tool CaptureViewport`(EditorAppToolset) 호출 — 결과가 크면 harness가 **tool-results `.txt` 파일**에 자동 저장하고 경로를 준다.
2. 그 파일을 **Read 하지 말 것**(라인이 너무 김). 대신:
   `python D:\unreal\Resource\docs\scripts\decode_capture.py <tool-results.txt> <out.png>`
3. `Read <out.png>` 로 확인.

- **CaptureViewport 파라미터 3개 모두 필수**: `captureTransform`, `annotations`(순수 이미지는 gridSpacing/gridExtent/gridHeight/maxLabelDistance=0, classFilter=null, maxLabels=0), `bShowUI=false`.
- ❌ **raw HTTP 직접호출 금지**: 이 서버는 POST 응답을 SSE 스트림(빈 즉시응답+별도채널)으로 주므로 urllib 단순 파싱 실패. harness MCP 클라이언트만 프로토콜을 제대로 처리.
- 서브에이전트가 스크린샷 검증하려면 **Bash 도구 필수**(decode 실행). hd2d-art-director엔 Bash 부여됨.
- 특정 캐릭터/영역 확대는 Pillow로 crop→`resize(..., NEAREST)`. 픽셀 행별 RGB 덤프도 Pillow.

---

## 2. MCP 툴 함정 (파라미터·동작이 스키마와 다름)

| 툴 | 함정 | 올바른 사용 |
|---|---|---|
| `ObjectTools.get_properties` | 필드명이 `object`가 아님 | `instance`(refPath) + `properties`(문자열 배열) |
| `ObjectTools.set_properties` | 필드명이 `propertiesJson`이 아님 | `instance` + **`values`**(JSON **문자열**) |
| `ActorTools.set_actor_transform` | ⚠ 미지정 필드를 **identity로 덮어씀**(스키마 설명과 반대) | location·rotation·scale **전부 명시**. 안 그러면 스케일·회전 날아감 |
| PPV 세팅 | 개별 프로퍼티가 아니라 통짜 | `Settings` 프로퍼티(JSON dict). 값 적용하려면 **`bOverride_X: true`를 반드시 함께** |
| `MaterialTools.recompile` | 필드명이 `material`이 아님 | `material_or_function` |
| `StaticMeshTools.set_material` | **메시 에셋을 영구 변경** | 금지 → 컴포넌트 `OverrideMaterials` 배열에 set_properties |
| `find_actors` | 이름/태그 말고도 | `bounds`(min/max/isValid) 로 **공간 쿼리** 가능 — 배치 검증에 유용 |
| 그래프 편집 후 | 미반영 | `MaterialTools.recompile` 1회 호출 |

### ProgrammaticToolset (배치 실행 — 왕복 절약에 강력)
- `get_execution_environment` 먼저 1회. `execute_tool(tool_name, json_string)` 로 호출, `run()`이 dict 반환.
- **import 제한**: `json, math, re, time, copy, datetime`만. (Pillow·os·base64 불가 → 이미지 작업은 바깥 Bash에서)
- ⚠ 반환 객체는 `_StrictDict`: **`.get(key, default)` 미지원** → `x[key] if key in x else ...` 로. 일반 `dict.get()`도 default 인자 금지.
- 8기 일괄 이동·MI 일괄 조회·지형 트레이스 루프 등에 최적.

### 레벨 상태
- `get_current_level`로 로드 확인, `load_level`로 전환. **에디터 재시작하면 `/Temp/Untitled`로 리셋**되므로 재시작 후 첫 작업은 반드시 `load_level`.
- 실험 후 `AssetTools.save_assets(asset_paths=[])`로 **전체 dirty 저장**.

---

## 3. 픽셀아트 / HD-2D 렌더 설정 (스프라이트가 깨끗하게 나오려면)

이 순서로 확인하면 대부분의 "도트가 이상함"이 잡힌다:

1. **에디터 스크린퍼센티지 = Manual 100%** — EditorPerformanceSettings에서 자동 다운스케일 끄기. (자동이면 도트 미세 뭉갬)
2. **VRS 3종 off** — `DefaultEngine.ini [SystemSettings]`: `r.VRS.Enable=0`, `r.VRS.EnableSoftware=0`, `r.Nanite.SoftwareVRS=0`. **재시작 필요.**
3. **텍스처**: Nearest + NoMipmaps + TC_EditorIcon (도트 보존).
4. **스프라이트 머티리얼**: Masked + TwoSided + Lit, **Roughness=1 / Specular=0**(반사광 제거 — 스프라이트 정석). RGB→BaseColor, A→OpacityMask.
5. **AA**: 픽셀아트엔 FXAA 또는 None. (단, AA는 대부분의 스프라이트 글리치의 원인이 **아니다** — 아래 z-fight 먼저 의심)
6. ⭐ **여러 스프라이트 일렬 배치 시 → 깊이축 2~3cm 스태거** (공면 z-fight 방지, 최중요. [[HD2D_기법_지식베이스]] 함정표 참조).

---

## 4. 근본원인 진단 방법론 (16종 배제로도 못 잡던 걸 잡은 방법)

> 실행 에이전트(sonnet)가 "설정을 하나씩 꺼보는" 배제법으로 16종을 시도하고도 실패한 버그를, 아래 방법으로 잡았다. **표면(셰이딩/설정)이 아니라 구조(지오메트리/데이터)를 의심할 때의 정석.** 이 방법론은 **두 차례 실전 검증**됐다(§4-1 원 사례, §4-2 재검증 사례).

1. **이분법으로 층을 가른다**: 원본 데이터 vs 엔진 렌더 / 정지 vs 애니 / 단독 vs 다수. 한 번의 비교로 절반의 가설을 죽인다. (예: 원본 PNG가 깨끗 → 데이터 무죄 → 렌더 문제 확정)
2. **결정적 판별 테스트 = 변수 격리**:
   - **MI 스왑 테스트**: 두 오브젝트의 머티리얼을 맞바꾼다. 문제가 **자리(트랜스폼)에 붙으면** 머티리얼 무죄, 지오메트리/배치 유죄.
   - **단독 배치 테스트**: 이웃을 제거한다. 혼자서 멀쩡하면 **상호작용(겹침·z-fight)** 이 원인.
3. **픽셀 법의학**: 스크린샷/텍스처를 Pillow로 열어 **RGB 또는 알파채널을 실측**한다. 줄 색·투명도가 원인을 지목한다 — 배경색=투과, 제3의 팔레트색=z-fight(다른 프레임/오브젝트가 비침), 회색밴딩=압축, **알파=0인 "유령 셀"=존재하지 않는 애니 프레임을 재생 중**.
4. **"만든 사람의 가설을 반증하라"**: 실행자가 세운 가설(여기선 "모션블러/velocity")을 **그 가설이 틀렸음을 증명하는 실험**(정지화면 재현)으로 먼저 죽인다. 가설을 지지하는 실험만 하면 영원히 못 잡는다.
5. **증상의 조건을 전부 만족하는 단일 원인**을 찾을 때까지: "위치·높이에 민감 + 어두운 캐릭터 심함 + 모든 렌더설정에 면역 + 단독 재현 불가" → 이 4개를 동시에 설명하는 건 공면 z-fight뿐이었다.

### 4-1. 원 사례 — 기본전투무대 S5 "글리치 대전"
줄무늬/찢김 버그. sonnet이 렌더 설정 16종 배제 실험을 전부 시도하고도 실패 → Fable이 직접 수사(오너 특별 승인) → 공면 쿼드 z-fight로 확정, 3cm Y 스태거로 완치. [[HD2D_기법_지식베이스]] 함정표 참조.

### 4-2. 재검증 사례 — 공격버튼데모 애니 깜빡임 (2026-07-06)
**증상**: 오너가 실사용 중 "공격 버튼 누르면 무기 내려친 다음 캐릭터가 한 번 깜빡인다"고 실시간 리포트.

**여기까지 sonnet 위임만으로 막혀있던 지점**: 최초 조사(파이프라인 탐색 단계)가 frameguide 이미지를 육안으로 읽고 "ATTACK1 = 약 8프레임(명시적으로 보여짐)"이라 결론 — 픽셀 실측 없이 hedge된 표현으로 남음. 이후 구현(gameplay-engineer, sonnet)이 이 수치를 그대로 신뢰해 FrameCount=8로 구현했고, D3 게이트의 실클릭 검증도 포즈 위주 육안 판정이라 짧은 랩/투명 프레임을 놓쳤다. **두 차례의 sonnet 작업 모두 같은 미검증 전제를 공유**했다.

**Director가 직접 개입한 이유와 방법**: 오너 리포트를 듣고 "8칸을 순회하는데 실제 그려지는 컷은 그보다 적어, 남은 칸이 투명 렌더될 때 깜빡으로 보인다"는 가설을 즉시 세웠다(방법론 5번 — 증상 "정확히 한 번 깜빡"이 "빈 프레임 1~2개"와 정확히 부합). 이 확인은 sonnet에게 재위임할 수도 있었지만, Director가 직접 Bash로 Pillow 스크립트를 짜 실행했다 — 이유는 (a) 셀별 알파채널 불투명 픽셀 카운트라는 검증이 스크립트 한 방으로 끝나는 결정적 방법이라 위임 왕복이 더 비쌌고, (b) "약 8프레임"이라는 hedge 자체가 이전 조사가 육안 판단이었음을 뜻해 재위임해도 같은 모호함이 반복될 위험이 있었기 때문. 실행 결과 8종 캐릭터 전원 **ATK1=6f, ATK2=6f, ATK3=4f**(가이드의 8은 오표기, 마지막 2셀 완전 투명)를 1회 실행으로 동시 확정 → FrameCount 8→6·타이머 0.95→0.70s 핫픽스로 즉시 해결.

**일반화 — Director가 직접 나서야 하는 신호(3개 동시 충족 시)**:
1. 검증 수단이 짧고 결정적(스크립트 1회 실행으로 원인이 확정됨).
2. 이전 sonnet 조사 결과에 이미 hedge 언어("약", "~로 보임", "명확치 않음")가 남아있어, 재위임이 같은 모호함을 반복할 위험이 있음.
3. 오너가 실사용 중 실시간 리포트 중이라 빠른 응답의 가치가 큼.

세 조건이 겹치면 "Fable/Opus는 노동하지 않는다" 원칙의 예외로 직접 Bash를 여는 편이 재위임보다 빠르고 정확하다 — S5·이번 사례 둘 다 이 패턴. 기술적 수정 내용은 이 문서 §6("공격버튼데모에서 추가 검증된 노하우") 참조.

---

## 5. 이 프로젝트의 검증된 실측값 (복붙용)

- 카메라(4v4 정면): location (0, -7850, 750), rotation (pitch -6, yaw 90, roll 0)
- 스프라이트 쿼드: SM_SpriteQuad, rotation (0, 0, 90), scale (6.48, 2.59, 1.0) — 셀 100×40 비율 2.5:1
- 배치: X 간격 150, 중앙갭 300, **Y는 3cm씩 스태거**, snap_to_ground 후 z=지면+129.5

---

## 6. 공격버튼데모에서 추가 검증된 노하우 (2026-07-06)

### 스프라이트시트 프레임 수는 가이드 문서가 아니라 **알파 실측**이 정답
팩 공식 frameguide가 "ATTACK1=8프레임"이라 표기했지만 **실물 시트는 6프레임+투명 셀 2개**였다(8종 공통: ATK1 6f/ATK2 6f/ATK3 4f). FrameCount를 가이드 수치로 잡으면 꼬리 투명 셀이 렌더돼 **캐릭터가 깜빡**인다(오너가 발견, Director가 직접 진단 — 과정은 §4-2). 새 애니 행을 쓸 때는 반드시 Pillow로 셀별 불투명 픽셀 수를 실측해 FrameCount를 정할 것:
`cell = alpha.crop((col*100, row*40, ...)); n = count(p>8)` — idle 행(6f)으로 방법 교차검증 가능. 타이머는 `실프레임수/FPS − 0.05`.

### 스프라이트 애니 검증의 함정 — idle 기준 오판 (Director 실사례)
**포즈로 애니 상태를 판정할 땐 반드시 그 캐릭터의 idle 레퍼런스 캡처와 대조하라.** 캐릭터마다 idle 스탠스가 다르다(예: A1 idle=웅크리고 검 낮게 — "공격 자세처럼" 보임). 실사례: 공격 후 "웅크린 자세"를 보고 복귀 실패로 오판 → 정적 그래프 분석(정상)과 모순 발생 → idle 레퍼런스(D1_octopath_idle.png)와 대조로 오판 확정. **판독 전 순수 idle 캡처 1장을 기준으로 확보하는 게 정석.** 공격 판정의 가장 확실한 시그널은 포즈가 아니라 **검격 이펙트(흰 스윙 궤적) 프레임**.

### TextRenderComponent 3종 함정
- **단면(one-sided) 렌더**: 회전이 부모 상속으로 법선이 하늘/반대편을 향하면 아예 안 보임 → "에디터가 TextRender를 안 그린다"는 오진을 유발했다. 실원인은 항상 회전부터 확인.
- WorldSize는 거리 스케일 필수(500cm 거리면 ~50).
- 화면상 위치 조정: 원근 카메라(pitch≠0)에선 **z(수직)보다 x(카메라 이격)가 화면 위치에 지배적**일 수 있음 — x 우선 조정, z는 미세조정용.
- **런타임 `SetText`(BP)가 렌더에 무반영**인 특이 사례 발생(5가지 재배선 무효) → **에디터 프로퍼티로 Text를 직접 설정**해 우회. 원인 미규명(후속 과제).

### FText 스트링테이블 참조를 MCP로 설정
`set_properties`의 값으로 **`LOCTABLE("/Game/UI/ST_UI", "Battle.Attack")`** 임포트 문자열을 주면 스트링테이블 참조 FText가 설정된다(성공 실증). 재조회 시 해석된 문자열("Attack")로 보이므로 참조 유지 여부는 이 API만으론 구분 불가.

### BP 그래프 배선 (D2/D3 실증 추가분)
- **exec 출력 핀은 fan-out 불가**(하나의 exec 출력 → 여러 입력 연결 안 됨). 데이터 핀만 fan-out 가능.
- `SetScalarParameterValue` 노드는 `declaring_class=/Script/Engine.MaterialInstanceDynamic` 명시 필수 — 안 하면 MPC용 오버로드가 생성돼 무음 실패.
- **재클릭 리스타트 패턴 = RetriggerableDelay**(재발화 시 대기 리셋). TimerHandle 변수는 `add_variable` 지원 목록 밖이라 이 패턴이 더 단순.
- `find_node_types`는 context_pins에 따라 존재하지 않는 type_id를 반환할 수 있음 → 실패 시 다른 context 조합으로 재검색.
- MCP엔 **PIE 콘솔 명령 주입 수단 없음** → 런타임 이벤트의 결정적 트리거가 필요하면 **임시 스캐폴드(BeginPlay+Delay→이벤트 호출) 심고 검증 후 제거**가 정석.

### 데스크톱 자동화로 PIE 실클릭 검증 (Director 전용)
- Windows-MCP `Click`의 `loc` 파라미터가 문자열화 결함으로 사용 불가 → **PowerShell user32(SetCursorPos+mouse_event) 우회**.
- 반드시 `SetProcessDPIAware()` 선행(150% DPI에서 물리↔논리 좌표 불일치 방지). 창 전환은 EnumWindows로 실제 창 제목 확인 후 ShowWindow(9)+SetForegroundWindow.
- 클릭 직후 고속 연사 캡처는 .NET `Graphics.CopyFromScreen`으로 같은 스크립트 안에서(Windows-MCP 스크린샷 왕복은 느려서 1초 애니 창을 놓침). 캡처 간 sleep에 **캡처 자체 소요(~0.3s)를 가산**해 실시각 계산.
- 작업 후 오너 화면 원상복구(창 최소화·원래 앱 전면) 매너.

---

## 7. 턴제전투MVP E1에서 추가 검증된 노하우 (2026-07-07)

### 함정 ① `find_node_types`/`get_node_type_pins`가 그래프에 dangling 노드를 실제로 생성함
`find_node_types`(단순 타입 검색)는 안전하지만, **`get_node_type_pins`는 그래프에 임시 노드를 실제로 만들었다가 나중에 조용히 GC되는 경우가 있다** — 그 사이 `refPath`(예: `K2Node_CallFunction_45`)를 저장해뒀다가 이후 `connect_pins`에 쓰면 `"is not valid EdGraphNode"` 에러로 실패한다(실전 재현: GetActorLocation 핀 조회 후 그 노드로 connect 시도 → 실패, 재확인하니 그래프에서 사라져 있었음). **대응**: 노드 타입만 알고 싶을 땐 `get_node_type_pins`를 쓰되, 실제로 그래프에 심을 노드는 **반드시 `create_node`로 별도 재생성**하고 그 반환 refPath만 신뢰할 것. `find_node_types`(타입 문자열만 반환)는 이 함정이 없음.

### 함정 ② 비균등 스케일(non-uniform scale)+회전을 동시에 가진 부모의 자식에 `SetWorldRotation`/`SetWorldScale3D`를 쓰면 전단(shear)으로 왜곡됨
스프라이트 쿼드처럼 `relativeScale3D`가 (6.48, 2.59, 1) 같은 비균등값이면서 `relativeRotation.roll=90`도 있는 부모 컴포넌트에, 자식 컴포넌트(마커·클릭박스 등 UI 오버레이)를 붙이고 `SetWorldRotation`/`SetWorldScale3D`로 "정확한 월드 트랜스폼"을 세팅해도, **relative* 값 자체는 수치상 정확히 역산되지만 실제 렌더 지오메트리는 전단(shear)되어 거대하고 뒤틀린 평면처럼 보인다**(원판이 카메라를 향한 정상 형태가 아니라 옆으로 늘어진 벽처럼 보임). 이는 Unreal 컴포넌트 트랜스폼 조합의 근본 한계(회전+비균등스케일 조합에서 "월드 스케일"은 well-defined 개념이 아님)다.
**해법**: 자식 컴포넌트에 **`bAbsoluteLocation`·`bAbsoluteRotation`·`bAbsoluteScale`를 전부 `true`**로 설정(엔진이 정확히 이 상황을 위해 제공하는 플래그) — 부모의 회전·스케일 상속을 원천 차단하고 `relative*` 값이 곧 월드값으로 취급된다. 이후 `SetWorldRotation`/`SetWorldLocation`/`SetWorldScale3D` 호출 결과가 `relativeLocation`/`relativeRotation`/`relativeScale3D`에 **그대로(전단 없이) 정확히** 반영됨(실측: `SetWorldScale3D(2.5,1.75,1)` 호출 후 `relativeScale3D`가 정확히 `(2.5,1.75,1)`로 나옴 — bAbsolute 없이는 부모 스케일로 나눈 이상한 값이 나왔었음). **비균등 스케일 부모에 UI 오버레이성 자식을 붙이는 모든 경우에 우선 점검할 것.**

### 함정 ③ `ObjectTools.set_properties`로 Vector/Rotator 같은 인라인 구조체 프로퍼티를 세팅하면 매번 정확히 1개 필드만 반영됨(어느 필드인지는 비결정적)
기존 §2/§6 서술("Vector의 첫 필드만 반영")은 **부정확했다** — 실측 재현 결과, `{"relativeScale3D": {"x":0.8,"y":0.8,"z":0.8}}` 같은 호출을 반복해도 **매 호출마다 정확히 1개 필드만 실제로 바뀌고 나머지 2개는 직전 값을 유지**하며, 어느 필드가 반영되는지는 키 순서 등으로 결정되지 않는 것으로 관찰됨(같은 페이로드를 다른 키 순서로 여러 번 호출하면 결국 다른 필드가 반영되기도 함). 다만 **배열 프로퍼티**(`overrideMaterials` 등)는 전체를 리스트로 재할당하면 항상 정확히 반영됨 — 이 버그는 **인라인 구조체(Vector/Rotator/LinearColor 등)에만 국한**된다.
**해법**: 목표 값이 전 필드 동일(예: 균등 스케일 0.8,0.8,0.8)이면 문제가 드러나지 않을 수 있으니 반드시 **세팅 후 `get_properties`로 재조회해 전 필드 일치를 확인**하고, 불일치 시 **동일 페이로드를 키 순서만 바꿔 2~4회 반복 호출** — 매 호출 후 재확인해 전 필드가 목표값과 일치할 때까지 반복하는 것이 유일하게 검증된 해법. **그래프 노드(SetWorldLocation 등 BP 함수 호출)는 이 버그와 무관**(MakeVector로 개별 float를 조합해 넘기므로 정상 동작) — 이 버그는 오직 MCP `set_properties`로 인스턴스 프로퍼티를 "직접" 세팅할 때만 해당.

### 미해결 이월 — `CaptureViewport`가 PIE 게임 월드가 아니라 에디터 레벨(원본)을 캡처하는 것으로 보이는 정황
PIE 세션 중 `get_current_level`이 빈 문자열을 반환하는 현상과 함께, PIE 인스턴스(`UEDPIE_0_...`)에서 `get_properties`로 트랜스폼이 완전히 정확함을 확인해도 그 시점의 `CaptureViewport` 스크린샷에는 반영되지 않는 사례가 재현됐다(`playMode: PlayMode_InViewPort`로 실행해도 동일). 반면 **PIE를 끄고 에디터 레벨(비-PIE) 인스턴스에 직접 동일 값을 세팅**하면 캡처에 정확히 반영된다. 즉 이 MCP 조합에서 PIE 중 스크린샷 자가검증은 **신뢰할 수 없을 가능성**이 있다 — 근본 메커니즘은 미규명. **런타임 로직(BeginPlay 등) 자체의 정확성은 `get_properties`로 PIE 인스턴스를 직접 재조회해 검증**하고, **시각적(픽셀) 확인이 꼭 필요하면 PIE를 끄고 에디터 레벨에 같은 값을 세팅한 뒤 캡처**하는 우회가 이번엔 유효했다(단, 인라인 구조체는 함정③에 걸리므로 병용 주의).

---

## 8. 턴제전투MVP E2에서 추가 검증된 노하우 (2026-07-07)

### 함정 ④ latent 노드(Delay 계열)는 Function Graph에서 사용 불가 — Custom Event(EventGraph)로 우회해야 함
UE 표준 제약: **Delay/RetriggerableDelay 같은 latent 노드는 Blueprint Function Graph에서 호출할 수 없다**(함수는 동기 실행이 전제). `find_node_types`로 함수 그래프 컨텍스트에서 `유틸리티|플로컨트롤|Delay`를 검색하면 결과가 항상 빈 배열이고, **같은 Blueprint의 EventGraph 컨텍스트로 검색하면 정상 발견**된다 — 이 차이 자체가 latent 노드 사용 가능 여부의 실측 판별법이다. 설계 단계에서 "함수 그래프"로 명시된 상태 진입 로직 중 Delay가 필요한 것이 있다면, 실제로는 **Custom Event(EventGraph)로 구현**하고 다른 곳에서는 `함수호출|<이벤트명>` 형태로 그대로 호출하면 된다(커스텀 이벤트도 CallFunction 노드처럼 호출 가능해 설계 의도인 "이름 붙은 진입점"은 그대로 유지됨).

### 함정 ⑤ `add_event`를 병렬(동시) 호출하면 `event_name`이 무시되고 기본 이름으로 생성될 수 있음
서로 다른 두 Custom Event를 **같은 메시지 안에서 병렬로** `add_event` 호출하면, 그중 하나가 실제로는 지정한 이름이 아니라 기본 이름(`커스텀이벤트`)으로 생성되는 경우가 재현됐다. 엔진 로그에 `LogBlueprint: Warning: User provided name was invalid 이미 사용 중인 이름입니다. - node named 커스텀이벤트`가 남는다 — 두 호출이 동시에 "이름 미지정 상태"로 처리되며 이름 충돌이 발생하는 것으로 추정. **탐지**: `add_event` 호출 후 `get_node_infos`로 생성된 노드의 `type_id`(예: `AddEvent|Custom|EnterExecuting`)가 지정한 이름과 일치하는지 반드시 재확인할 것 — `AddEvent|Custom|커스텀이벤트`로 나오면 실패다. **해법**: 같은 이름으로 `add_event`를 (단독으로) 재호출하면 이번엔 정확한 이름의 새 노드가 생성된다(리네임이 아니라 별도 신규 노드 생성) → 기존 배선을 새 노드로 옮기고 잘못된 이름의 노드를 `delete_node`로 제거. **예방**: 여러 Custom Event를 만들 땐 반드시 순차(1개씩) 호출하거나, 병렬 호출 후 전수 이름 검증을 습관화할 것.

### `set_pin_value`로 함수 호출 노드의 오브젝트 파라미터에 리터럴 레퍼런스를 직접 지정 가능
`NotifyUnitClicked(ClickedUnit)`처럼 오브젝트 타입 파라미터 핀에 `set_pin_value`로 레벨 인스턴스의 소프트 경로 문자열(예: `/Game/Stages/map_battle_octopath.map_battle_octopath:PersistentLevel.BP_BattleSpawnPoint_C_4`)을 직접 주면 정확히 반영된다(`get_node_infos` 재조회로 확인). 스캐폴드에서 특정 유닛을 하드참조로 지정할 때 별도의 "리터럴 오브젝트 레퍼런스" 노드를 만들 필요 없이 이 방법으로 충분하다.

### 프로모터블 오퍼레이터(Equal/NotEqual/+)는 미연결 상태에서 엉뚱한 오버로드로 생성되지만 데이터 연결 후 자동 재해석됨
`유틸리티|연산자|같음(==)` 같은 프로모터블 노드를 `create_node`로 막 생성하면 초기 표시가 `게임플레이태그|Equal(GameplayTagContainer)`처럼 전혀 의도하지 않은 타입으로 나온다(오브젝트/이넘 문맥 등 첫 번째로 매치된 오버로드로 추정). **당황하지 말 것** — 실제 데이터 핀(Bool/Int/Byte 등)을 연결하고 나서 `get_node_infos`로 재조회하면 `수학|부울|NotEqual(Boolean)`, `수학|인티저|Equal(Integer)`, `수학|바이트|Equal(Byte)` 등으로 정확히 자동 승격되어 있다. 연결 직후 반드시 재조회해 타입이 의도대로 승격됐는지 확인하는 습관이 필요하다.

### `find_node_types`의 latent 노드 검색은 그래프 컨텍스트(Function vs EventGraph)에 따라 결과가 달라진다 — 사전 점검 도구로 활용 가능
위 함정④의 실측 방법 자체가 하나의 진단 기법이 된다: 특정 노드 타입이 어떤 그래프 종류에서 쓸 수 있는지 확신이 없으면, **Function Graph와 EventGraph 양쪽에서 `find_node_types`를 같은 검색어로 호출해 결과를 비교**하라 — 한쪽에서만 나오면 그 노드는 해당 그래프 종류 전용이다.

---

## 9. 턴제전투MVP E2-후속 SpriteMID 재수사에서 확정된 노하우 (2026-07-07)

### 함정 ⑥ `set_pin_value`로 세팅한 리터럴 오브젝트 레퍼런스는 PIE 세션 중에도 PIE 인스턴스로 리매핑되지 않고 에디터 원본("그림자") 액터를 계속 가리킨다 — BeginPlay 상태 의존 로직 검증 시 가짜 회귀를 낳는 최우선 용의점
§7/§8에서 "성공 실증"으로 기록한 패턴(`set_pin_value`로 함수 호출 노드의 오브젝트 파라미터에 레벨 인스턴스 소프트 경로 문자열을 직접 지정)에는 중대한 함정이 있다: **이 리터럴은 PIE 접두사(`UEDPIE_0_`)가 없는 에디터 원본 레벨 경로**(예: `/Game/Stages/map_battle_octopath.map_battle_octopath:PersistentLevel.BP_BattleSpawnPoint_C_4`)이고, **PIE를 시작해도 이 하드코딩된 레퍼런스는 자동으로 PIE 카피로 리다이렉트되지 않는다** — 즉 그래프 안에서 이 값을 self로 쓰면, 실제로는 **BeginPlay가 한 번도 실행되지 않은 에디터 원본 액터**(런타임 상태가 전부 기본값/None인 "그림자" 액터)를 계속 참조하게 된다.

**증상**: 이 그림자 액터의 `self`로 커스텀 이벤트(예: `TakeHit`)를 호출하면 이벤트 자체는 정상 진입(`DIAG_D: TakeHit ENTERED` 같은 로그가 정확한 액터 이름으로 찍힘)하지만, BeginPlay가 채웠어야 할 멤버 변수(예: `SpriteMID`)는 전부 `None`이라 그 이후의 `IsValid` 가드가 항상 실패한다. 이때 로그의 액터 이름 prefix(`[BP_BattleSpawnPoint_C_4]`, `GetName()` 결과)는 PIE/에디터 구분 접두사를 표시하지 않으므로 **"진짜 그 액터에서 실행됐다"는 착시**가 발생하고, 조사자는 BeginPlay 로직 자체를 의심하게 되는 함정에 빠진다.

**결정적 판별법(반증 실험)**: 의심스러운 상황에서 `ObjectTools.get_properties`로 **PIE 인스턴스**(`find_actors`로 얻은 `UEDPIE_0_...` 접두사 경로)와 **에디터 원본**(접두사 없는 경로) 양쪽의 같은 프로퍼티를 동시에 조회해 비교하라 — PIE 인스턴스는 유효한데 에디터 원본이 `None`이면서 그래프 내부 로직은 여전히 `None`으로 판정한다면, **그래프가 참조하는 `self`가 에디터 원본(그림자)임이 100% 확정**된다.

**해법**: 리터럴 오브젝트 레퍼런스로 self를 지정하지 말고, **PIE 런타임에 실제로 채워지는 배열/변수를 경유**해 액터를 획득할 것 — 예: `GetTurnQueue()`(BeginPlay 시점에 8/8 유닛이 실제로 self-register한 배열) → `Utilities|Array|Get(사본)`으로 인덱스 접근. 이렇게 하면 그 값은 항상 **현재 PIE 월드의 실제 인스턴스**이므로 리매핑 문제 자체가 발생하지 않는다. **실제 게임플레이 경로(마우스 클릭 → `NotifyUnitClicked(ClickedUnit)` 같은 함수 파라미터로 액터가 전달되는 경우)는 이 함정과 원천적으로 무관** — 함정은 오직 MCP가 그래프에 **정적으로 미리 박아넣는 리터럴** 레퍼런스에서만 발생한다.

**이 함정과 E1 이슈 D(CaptureViewport의 PIE/에디터 레벨 캡처 대상 불일치)는 근본적으로 같은 계열**이다: 이 MCP 서버 조합에서 "에디터가 알고 있는 액터 경로"와 "PIE가 실제로 실행 중인 액터 인스턴스"가 명확히 분리되어 있고, 도구별로 어느 쪽을 대상으로 삼는지가 다르다(`get_properties`/`find_actors`는 인자로 준 경로 그대로 조회하지만 PIE 시작 후엔 반드시 `UEDPIE_0_` 접두사 경로를 별도로 얻어야 하고, 그래프에 미리 박아넣은 리터럴은 이 갱신이 일어나지 않는다). **PIE 상태 의존 로직을 자가검증할 때는 리터럴 대신 항상 런타임 조회 경로를 쓸 것.**

### 함정 ⑦ `EditorPerformanceSettings.bThrottleCPUWhenNotForeground=true`(기본값)이면 MCP가 에디터와 통신하는 동안 PIE 게임 틱이 사실상 정지할 수 있다
MCP 클라이언트가 에디터와 반복 통신하는 동안 에디터 창(PIE 포함)이 실질적으로 "백그라운드"로 취급되는 것으로 보인다. 이 설정이 `true`(프로젝트 기본값)인 상태에서 BeginPlay→`Delay(4.0)`→커스텀이벤트 호출 형태의 진단 스캐폴드를 심으면, **30초 이상 대기해도 Delay가 전혀 발화하지 않는** 현상이 재현됐다(게임 시간 자체가 사실상 멈춤). `ConfigSettingsToolset`으로 `Editor`/`General`/`EditorPerformanceSettings` 섹션의 이 프로퍼티를 `false`로 끄면 즉시 정상 발화한다.
**주의**: 껐다고 편차가 완전히 사라지는 것은 아니다 — 실측 재현에서 설정 4.0초짜리 Delay가 **약 3.37초**(-16%, 오히려 더 빠르게)에 발화했다. E1/E2가 별도로 보고한 "+0.25~0.32초 느려짐" 편차와는 부호·크기가 다르므로, **스로틀링은 "PIE 자가검증 세션에서 반드시 꺼야 하는 전제조건"이지 타이밍 편차의 유일한 원인은 아니다** — PIE 게임시간 계산 자체에 별도 오차 요인이 있을 가능성이 남아있다(후속 조사 필요).
**절차**: `GetSectionPropertyValues`로 현재값 확인 → 필요시 `SetSectionProperties`로 `false` 설정 → 진단 종료 후 **원래 값으로 복원**(에디터 로컬 설정 변경은 허용되나, 진단 목적 임시 변경이면 되돌리는 게 안전).

---

## 10. 턴제전투MVP F단계 라이브 결함 핫픽스에서 확정된 노하우 (2026-07-07)

### 함정 ⑧ 투명 스프라이트 쿼드의 `BlockAllDynamic` 콜리전이 "클릭 방패"가 되어 뒤쪽 유닛의 클릭을 전부 흡수한다
`BP_BattleSpawnPoint`의 `Sprite`(SM_SpriteQuad, 648cm 대형 평면)와 `TurnMarker` 컴포넌트가 기본 콜리전 프리셋(`BlockAllDynamic`)을 유지한 채 배치되면, PC의 클릭 트레이스(`Visibility` 채널)가 이 평면에서 항상 먼저 블로킹 히트를 반환한다. 스프라이트 자체가 시각적으로는 투명 배경(알파 마스크)을 가진 부분이라도 **콜리전은 알파와 무관하게 쿼드 전체 형태로 존재**하므로, 카메라와 실제 클릭 대상(유닛의 `ClickBox`) 사이에 이 평면이 걸쳐 있으면 `ClickBox`까지 트레이스가 도달하지 못해 **클릭 자체가 조용히 실패**한다(에러도 로그도 없음 — 그냥 아무 반응이 없는 것처럼 보인다).

**증상의 특징**: 일부 유닛(카메라에 가까운 쪽)은 클릭이 되고 안쪽 유닛은 안 되는 등 **위치에 따라 재현성이 갈린다**(트레이스 경로 상에 스프라이트 평면이 끼는지 여부에 따라 결정되므로). 이것이 "특정 유닛만 클릭 안 됨" 같은 산발적 버그 리포트로 이어지기 쉽다.

**해법**: 시각적 스프라이트/마커처럼 **클릭 판정에 관여할 필요가 없는 컴포넌트는 `SetCollisionEnabled(NoCollision)`을 BeginPlay 체인 끝에 명시적으로 추가**한다. 콜리전 프로퍼티는 구조체가 아니라 enum 단일값이라 §7 함정③(인라인 구조체 set_properties 비결정성)에 걸리지 않고, `create_node`(`콜리전|SetCollisionEnabled`)+`connect_pins`로 그래프에 안전하게 추가할 수 있다(에디터 인스턴스 프로퍼티로 직접 세팅하는 것보다 그래프 노드가 정석 — CLAUDE.md의 "구조체/콜리전은 BeginPlay 그래프 노드로" 원칙과 일치). **여러 스프라이트 쿼드를 겹쳐 배치하는 HD-2D 연출에서는 이 패턴이 반복될 가능성이 높으므로, 새 스프라이트 액터를 만들 때마다 "이 콜리전이 클릭을 막을 수 있는가"를 기본 점검 항목에 넣을 것.**

### `read_graph_dsl`이 특정 그래프에서 빈 문자열을 반환할 수 있음 — `find_nodes`(entry_points_only)+`get_connected_subgraph` 조합으로 우회
`BlueprintTools.read_graph_dsl`은 DSL 텍스트로 그래프 전체를 읽어오는 강력한 도구이지만, 실전에서 이미 완성된 대형 EventGraph(BeginPlay 체인 38노드 등)에 대해 **에러 없이 빈 문자열(`""`)만 반환**하는 사례가 재현됐다(원인 미규명 — DSL 변환기가 특정 노드 타입 조합을 조용히 스킵하는 것으로 추정). 이 경우 `list_events`로 구현된 이벤트 목록을 먼저 확인하고, `find_nodes(graph, title="", entry_points_only=true)`로 진입점 노드들을 얻은 뒤 각각에 `get_connected_subgraph`를 호출하면 동일한 정보를 노드/핀 단위 JSON으로 안전하게 얻을 수 있다. 대형 그래프 전체를 한 번에 읽으려 하지 말고 **이벤트 체인 단위로 쪼개 조회**하는 편이 결과 크기(토큰) 관리 측면에서도 유리하다.

### PIE 세션 로그가 GetLogEntries에 한동안 반영되지 않다가 다음 세션에서 갑자기 나타나는 현상 관찰(원인 미규명, 조건부 재현)
StartPIE(warmup 2s) 직후 `GetLogEntries`를 호출했을 때 최신 로그가 수 시간 전 타임스탬프에 멈춰있고, 그 뒤 StopPIE까지 실행한 세션 전체가 로그에 전혀 나타나지 않은 사례가 1회 관찰됐다. 그러나 **바로 다음 StartPIE 시도에서는 정상적으로 최신 로그(`Registered:1~8→State:Init→TurnStart→AwaitCommand`)가 즉시 반영**되어, 두 세션의 유일한 차이(warmup 시간 2s vs 3s, 또는 단순 재시도)로는 재현조건을 확정할 수 없었다. StopPIE 후 `get_current_level`이 정상값을 반환하는 것으로 로그 시스템 자체(파일 tail 메커니즘)의 이상은 배제됨. **대응**: 검증 목적의 StartPIE 직후 로그가 비어 보이면, 로직 결함으로 단정하지 말고 먼저 `StopPIE→재시도` 1회로 재현성을 확인할 것 — 이번 사례처럼 다음 시도에서 정상 반영되면 이 노하우 문단의 현상이었을 가능성이 높다. 근본 원인은 후속 조사 과제로 남긴다(이월).

**정정(2026-07-07, VFX 2단계 배선에서 반증 실험)**: 위 현상을 "로그 지연"으로 오판할 뻔한 사례가 재현됐으나, 실제 원인은 **로그 타임스탬프가 UTC 기준이고 시스템 로컬 시각(KST 등 UTC+N)과 날짜 표기가 어긋난 것**이었다. 예: 로컬 시각 `2026-07-07 08:48`(UTC+9)에 기록된 로그가 `[2026.07.06-23.48...]`로 남는다(UTC로는 아직 전날 23시대). `GetLogEntries` 결과가 "오래된 날짜"로 보여도 **먼저 `date -u`로 UTC 현재 시각과 대조**할 것 — 초 단위까지 정확히 일치하면 로그는 정상 반영된 것이고 단순히 날짜 표기 착시다. 이 착시 때문에 불필요하게 StopPIE→재시도를 반복할 위험이 있으니, §10의 "지연 반영" 가설보다 이 UTC 표기 확인을 **우선** 시도할 것.

---

## 11. 턴제전투MVP VFX 임시통합 2단계에서 확정된 노하우 (2026-07-07)

### 함정 ⑨ 다른 블루프린트의 커스텀 이벤트를 호출하는 CallFunction 노드는 `find_node_types`(context_pins 포함) 검색 결과 문자열을 그대로 `create_node`에 넣으면 실패한다 — 기존 노드 역산이 유일한 해법
`find_node_types`에 `context_pins`(호출 대상 오브젝트 레퍼런스 핀)를 채워 검색하면 다른 블루프린트의 커스텀 이벤트 호출 노드(예: `BP_BattleSpawnPoint`의 `PlayAttack`)가 `함수호출|PlayAttack` 형태로 정확히 검색된다. 그러나 이 문자열을 그대로 `create_node`(context_pins 없이, `declaring_class`로 대상 클래스를 명시해도)에 넣으면 **"does not exist" 에러로 실패**한다 — `find_node_types`가 성공적으로 찾아낸 타입 식별자가 `create_node`에는 그대로 재사용 불가능한 컨텍스트 종속 문자열인 것으로 추정된다.

**해법(실증됨)**: 이미 같은 그래프(또는 같은 블루프린트의 다른 그래프) 안에 **동일 목적으로 호출하는 기존 노드가 반드시 존재**한다(그렇지 않으면애초에 그 커스텀 이벤트가 발동될 방법이 없다). `find_nodes(graph, title="<이벤트명>")`으로 그 기존 CallFunction 노드를 찾고, `get_node_infos`로 실제 `type_id`를 역산하면(이번 사례에서 `|PlayAttack` — 파이프만 있고 카테고리 접두사 없음, `함수호출|PlayAttack`과 다름) 그 정확한 문자열로 `create_node`가 즉시 성공한다.

**대조군 — 자기 자신의 블루프린트 함수 호출은 이 함정이 없음**: `NotifyUnitClicked`처럼 **같은 블루프린트 안에 정의된 함수**를 EventGraph에서 호출하는 CallFunction 노드는 `find_node_types`가 반환한 `함수호출|NotifyUnitClicked` 문자열이 `create_node`에 그대로 먹혔다(별도 역산 불필요). 즉 이 함정은 **"다른 블루프린트의 커스텀 이벤트를 호출"하는 특정 케이스에만 해당**하는 것으로 보인다(근본 메커니즘은 미규명, 후속 조사 과제로 이월). **실전 절차**: 다른 블루프린트의 커스텀 이벤트를 스캐폴드 등에서 호출해야 할 때는 먼저 `find_node_types`로 문자열을 얻어 시도하고, "does not exist" 에러가 나면 **즉시 기존 호출 노드 역산으로 전환**할 것(같은 접근을 반복 재시도하지 말 것 — 3회 규칙 낭비 방지).

### `Utilities|Array|Get(사본)` 노드는 입력 배열을 연결하는 즉시 출력 핀이 원소 타입으로 자동 승격된다
`create_node`로 막 생성한 Array Get 노드는 `Array`(와일드카드 배열)/`Output`(와일드카드) 핀 상태다. 여기에 타입이 있는 배열(예: `BP_BattleSpawnPoint` 배열인 `TurnQueue`)을 `Array` 입력 핀에 연결하면, **별도 조작 없이 `Output` 핀이 즉시 해당 원소 타입(`BP_BattleSpawnPoint` 오브젝트 레퍼런스)으로 자동 승격**된다(§9에서 확인된 프로모터블 오퍼레이터의 "데이터 연결 후 자동 재해석"과 동일 계열이지만, 입력에서 출력으로 타입이 전파되는 방향이라는 점이 다르다). 연결 직후 `get_node_infos`로 재조회해 승격을 확인하는 습관은 여기서도 유효하다.

### `find_node_types`에 `context_pins`로 기존 핀을 지정해 검색하면 프로모터블 연산자가 승격된 형태로 바로 나온다 — 사전 확인 팁
§9에서는 "생성 후 데이터 연결하면 자동 재해석된다"는 점만 확인했으나, 이번 사례에서 **검색 단계에서부터 `context_pins`에 실제 연결하려는 데이터 핀(예: `GetActorLocation`의 Vector 출력)을 채워 넣으면 `find_node_types`가 이미 승격된 형태**(`수학|벡터|vector+vector` 등, 미승격 상태의 `유틸리티|시간관리|FrameNumber+Int` 같은 엉뚱한 오버로드가 아님)로 결과를 반환한다는 것을 확인했다. 프로모터블 연산자를 다룰 때는 빈 `context_pins`로 검색하지 말고, 실제 연결 대상 핀을 미리 채워 검색하는 편이 이후 재확인 스텝을 하나 줄여준다.

---

## 12. 턴제전투MVP VFX 미표시 결함 수사에서 확정된 노하우 (2026-07-07)

### 함정 ⑩ `get_node_infos`가 보여주는 `type_id`(예: `|SetSpriteMID`, `|GetTurnQueue`, `개발|PrintText`)는 사람이 읽기용 축약 표기이며 `create_node`에 그대로 넣으면 실패할 수 있다 — 항상 `find_node_types`로 정확한 문자열을 재조회할 것
기존 그래프 노드를 `get_node_infos`로 조회했을 때 나오는 `type_id`(카테고리 접두사가 생략된 경우가 많음 — `|SetSmearMID`, `|GetHitMID`, `|PlayAttack` 등)를 그대로 복사해 `create_node`에 넣으면 "does not exist" 에러가 반복 재현된다(§11 함정⑨는 "다른 BP 커스텀 이벤트 호출"이라는 특정 케이스였지만, 이번엔 **같은 블루프린트 안의 멤버 변수 Get/Set, PrintText, Delay 등 흔한 노드에서도 동일 패턴이 광범위하게 재현**됐다 — 예: `게임|PrintText`로 시도 실패, 정확한 문자열은 `개발|PrintText`; `유틸리티|플로컨트롤|Delay`로 시도 실패, 정확한 문자열은 오타 없이 재확인 시 정상; `Utilities|Text|FormatText`로 검색 시 빈 배열, 한글 `Utilities|Text|포맷텍스트`로 검색해야 나옴). **결론**: `get_node_infos`의 `type_id`는 참고용 표시 문자열일 뿐 `create_node` 입력으로 신뢰하지 말 것 — 새 노드를 만들 때는 항상 **먼저 `find_node_types`(그래프 컨텍스트 지정)로 정확한 문자열을 얻고**, 그 결과를 그대로 `create_node`에 사용한다. 검색어는 영어/한글 둘 다 시도(카테고리가 한글로만 번역된 경우가 다수 존재).

### 함정 ⑪ 인라인 구조체가 아닌 여러 개의 최상위 불리언/스칼라 프로퍼티를 하나의 `set_properties` 호출로 동시에 지정해도 그중 일부만 반영될 수 있다 — §7 함정③의 확장판
§7 함정③은 "인라인 구조체(Vector/Rotator 등) 내부 필드가 매번 1개만 반영"되는 현상이었는데, 이번 사례에서 **서로 다른 최상위 프로퍼티 3개(`bAbsoluteLocation`/`bAbsoluteRotation`/`bAbsoluteScale`, 전부 독립된 bool 필드)를 한 번의 `set_properties({"bAbsoluteLocation":true,"bAbsoluteRotation":true,"bAbsoluteScale":true})` 호출로 동시에 넘겼을 때도 일부만 반영**되는 현상이 재현됐다(실측: 1회차 호출 후 `bAbsoluteLocation=true`만 반영되고 나머지 둘은 `false`로 남음). 즉 이 비결정성 버그는 구조체 내부 필드에 국한되지 않고, **한 번의 호출에 담긴 여러 프로퍼티 키 전반**에 적용될 수 있는 것으로 확장 확인됐다. **해법은 §7과 동일**: 각 프로퍼티를 **개별 `set_properties` 호출로 하나씩** 세팅하거나, 여러 개를 한 번에 보낸 뒤 반드시 `get_properties`로 재조회해 전부 목표값과 일치하는지 확인하고 불일치 항목만 추가로 개별 재호출한다.

### 함정 ⑫ 언리얼 에디터 창이 최소화(`IsIconic=true`)된 상태에서는 `CaptureEditorImage`가 실패하고 `CaptureViewport`도 최소화 직전의 스테일 프레임을 반환하는 것으로 의심된다
MCP 클라이언트가 에디터와 장시간 통신하는 동안(§9 함정⑦의 스로틀링과 별개로) 실제 OS 창 상태가 최소화로 전환되는 경우가 있었다(`user32.dll IsIconic` 확인, 창 좌표가 `(-21333,-21333)` 같은 표준 최소화 오프스크린 좌표로 이동). 이 상태에서 `CaptureEditorImage`는 `"Failed to capture any editor windows"` 에러를 반환했고, `CaptureViewport`는 에러 없이 이미지를 반환했지만 **그 내용이 실제 현재 씬이 아니라 다른(이전) 씬처럼 보이는 정황**이 있었다. **진단 순서**: 캡처 결과가 의심스러우면 (1) PowerShell `user32.dll`(`IsIconic`/`GetForegroundWindow`/`GetWindowRect`)로 창 상태를 직접 확인 → (2) 최소화 상태면 `ShowWindow(hwnd, 9)`(SW_RESTORE)+`SetForegroundWindow(hwnd)`로 복원 → (3) `CaptureEditorImage`가 성공하는지로 복원 여부를 검증한 뒤 → (4) `CaptureViewport` 재시도. 단, 창을 복원해도 캡처 내용이 즉시 기대와 다르면(이번 사례처럼) **레벨/배경 자체가 실제로 그런 모습일 가능성**을 먼저 배제할 것(아래 함정⑬ 참조 — "이상해 보이는 배경"을 성급히 캐시 문제로 오판하지 말 것).

### 함정 ⑬ "이상한 배경이 캡처됨" = 캐시/레벨 불일치가 아니라 실제 레벨 콘텐츠일 수 있다 — `GetVisibleActors`로 먼저 액터 소속을 교차검증할 것
PIE 중 `CaptureViewport`로 얻은 이미지가 예상과 다른 배경(성벽·목책·초가지붕 등 "마을" 스타일)을 보여줘서 "PIE가 잘못된 레벨을 캡처하고 있다"(§7 이슈 D 재현)고 즉시 판단했으나, **실제로는 이 배경 자체가 해당 배틀 레벨의 정상적인 디자인 콘텐츠**였다(기존 완성 스크린샷 문서와 대조해 확인). 오판의 원인은 배경 외관만으로 "이건 다른 레벨"이라고 결론짓고, `GetVisibleActors`가 이미 정확한 레벨의 액터 1880개(배틀 스폰포인트 포함)를 반환하고 있다는 반대 증거를 무시한 것이었다. **교훈**: 캡처된 배경이 예상과 다르면 성급히 "잘못된 레벨/캐시"로 결론짓지 말고, 먼저 `GetVisibleActors`(또는 `find_actors`)로 **실제 그 씬의 액터 목록이 기대한 레벨 소속인지**부터 교차검증하라 — 배경 외관은 특히 여러 아트팩이 공유되는 프로젝트(마을 성문 배경을 배틀 무대로 재사용하는 등)에서 신뢰할 수 없는 판별 근거다.

### `CaptureViewport`의 왕복 지연이 매우 커서(수십 초 단위) 0.3~0.6초짜리 짧은 VFX 재생 순간을 스크린샷으로 잡기 매우 어렵다
PIE 게임 내 짧은 이펙트 재생 구간을 시각적으로 확인하려고 재생시간(RetriggerableDelay Duration)을 진단 목적으로 3초→12초→90초까지 단계적으로 늘렸음에도 **매번 캡처 이미지에 이펙트가 없었다**. 원인은 `CaptureViewport` 자체(4~5MB base64 PNG 인코딩+전송)의 왕복 시간이 실측 46~110초에 달했기 때문 — `UnitClicked` 로그의 UTC 타임스탬프와 그 직후 `get_properties`/`CaptureViewport` 호출이 실제로 반영된 시점의 UTC(`date -u`)를 대조해 이 지연을 실측 확인했다. **진단 시 유용했던 우회**: 캡처 대신 **PIE 인스턴스 프로퍼티를 직접 실시간 조회**(`get_properties`로 `bVisible`, `overrideMaterials`의 다이나믹 MID 바인딩 등)하면 왕복 1회로 "지금 이 순간 이펙트가 재생 중인가"를 확정할 수 있다 — 이 방법으로 `bVisible=true`와 정확한 MID 바인딩을 여러 차례 실측해 VFX 트리거 자체는 정상 작동함을 실증했다(순간 스크린샷 확보는 실패했지만 로직 정상성 증거로는 충분). **결론**: 짧은 트랜지언트 이펙트의 "눈으로 보이는 증거"가 필요하면 캡처 왕복 지연을 감안해 재생시간을 매우 길게(60초 이상) 잡거나, Windows 데스크톱 자동화로 고속 연사 캡처(§6 "PIE 실클릭 검증" 패턴, `.NET Graphics.CopyFromScreen`)를 사용하는 게 유일하게 재현성 있는 방법으로 보인다 — MCP `CaptureViewport` 단독으로는 재현성이 낮다.

---

## 13. 걸어나오기연출 W0+W1에서 확정된 노하우 (2026-07-07)

### 함정 ⑭ BP 그래프 도구(BlueprintTools)의 blueprint refPath는 `.BP명` 접미사가 필요하고, 액터 도구(ActorTools/SceneTools)는 레벨 경로, CDO는 `Default__BP_X_C` — **도구군별로 참조 형식이 전혀 다르다**
같은 블루프린트 에셋을 가리켜도 호출하는 툴셋에 따라 정확한 `refPath` 형식이 다르다:
- `BlueprintTools`(그래프 편집): `/Game/Blueprints/BP_X.BP_X`(패키지 경로.에셋명, 접미사에 에셋명 반복).
- `ActorTools`/`SceneTools`(레벨 인스턴스): `/Game/Stages/map_battle_octopath.map_battle_octopath:PersistentLevel.BP_X_C_0`(레벨 경로:PersistentLevel.인스턴스명, 클래스명 뒤 `_C_숫자`).
- CDO(Class Default Object, `get_default_object`로 얻음): `/Game/Blueprints/BP_X.Default__BP_X_C`.
- 컴포넌트 CDO(actor add_component 등의 반환값): `/Game/Blueprints/BP_X.BP_X_C:ComponentName_GEN_VARIABLE`(actor 클래스명+ `_C:` + 컴포넌트명 + `_GEN_VARIABLE`).
혼동하면 "not valid Actor/Blueprint for property" 에러가 즉시 난다 — 에러 메시지 자체가 어느 형식이 필요한지 알려주지 않으므로, 툴셋 종류(그래프 편집=BlueprintTools용 / 인스턴스 조작=Actor·SceneTools용 / 프로퍼티 조회=ObjectTools+CDO)를 먼저 확인하고 그에 맞는 refPath를 준비할 것.

### 함정 ⑮ `find_node_types`가 반환하는 문자열은 "다른 블루프린트의 신규(이 세션에서 막 만든) 멤버"에 대해서는 여러 형식(`함수호출|X`, `|X`, `Class|ClassName|X`)으로 나오고 그중 정확히 하나만 `create_node`에서 유효하다 — 정답 형식은 `Class|<블루프린트명(언더스코어 제거+파스칼케이스)>|<멤버명>`
§11 함정⑨(다른 BP 커스텀 이벤트 호출은 기존 노드 역산이 유일한 해법)의 근본 원인을 이번에 확정했다: 문제는 "커스텀 이벤트냐 함수냐"가 아니라 **"그 멤버가 이미 그래프 어딘가에서 호출된 적이 있느냐"**다. 완전히 새로 만든 함수(`GetAttackPointForTeam`)와 신규 변수(`AttackPointOverride`)를 다른 블루프린트에서 그래프 노드로 만들려 하면, `find_node_types`가 반환한 문자열(`함수호출|GetAttackPointforTeam`, `|GetAttackPointForTeam`, `Variables|디폴트|GetPartyAttackPoint` 등)을 그대로 `create_node`에 넣어도 전부 "does not exist"로 실패한다(5회 이상 실패 재현). 유일하게 성공한 형식은 **`Class|BPBattleManager|GetAttackPointForTeam`**(원래 블루프린트명 `BP_BattleManager`에서 언더스코어를 제거하고 파스칼케이스로 만든 `BPBattleManager`) — 이는 `find_node_types`가 신규 항목에 한해 별도로 반환하는 `Class|BPBattleSpawnPoint|SetAttackPointOverride` 같은 문자열과 정확히 같은 패턴이다. **실전 절차**: 다른 BP의 신규 멤버(변수 Get/Set, 함수)를 그래프에서 참조해야 할 때, 먼저 `find_node_types`로 여러 후보 문자열을 얻은 뒤 **`Class|<원블루프린트명에서 언더스코어 제거>|<멤버명>` 형식을 최우선으로 시도**할 것 — 이 형식이 나머지 형식들(`함수호출|X`, `|X`, `Variables|디폴트|X`)보다 신규 항목에 대해 신뢰도가 높다. 참고로 이 문제는 에셋을 `save_assets`로 저장해도 해결되지 않았다(엔진의 BlueprintActionDatabase 캐시 갱신 시점 문제로 추정, 근본 메커니즘은 미규명).

### 함정 ⑯ bool 멤버 변수명이 `b` 접두어로 시작하면(예: `bIsParty`), 자동생성 Get/Set 노드의 `create_node` 문자열에서는 `b`가 제거된다(`GetIsParty`/`SetIsParty`이지 `GetbIsParty`가 아님)
`bIsParty`라는 변수의 게터를 그래프 노드로 만들려고 `Variables|디폴트|GetbIsParty`, `|GetbIsParty` 두 형식 모두 시도했으나 둘 다 "does not exist"로 실패했다. `find_node_types`로 "Party"라는 부분 문자열로 검색하자 `Variables|디폴트|GetIsParty`(`b` 없음)가 나왔고 이것으로 `create_node`가 성공했다. 반면 `get_node_infos`로 기존 그래프의 같은 게터 노드를 조회하면 `type_id`가 `|GetbIsParty`(b 포함, §10 함정⑩의 "축약 표기"에 해당)로 표시된다 — 즉 **표시용 문자열과 생성용 문자열이 이 케이스에서도 다르다**. **실전 절차**: bool 변수(`b` 접두어 관례)의 Get/Set 노드를 새로 만들 때는 변수명에서 `b`를 뗀 이름으로 먼저 시도할 것(`bIsParty`→`GetIsParty`, `bInputLocked`→`GetbInputLocked`가 아니라 `GetInputLocked`일 가능성 등 — 매번 `find_node_types`로 재확인 권장, 일반화된 규칙이 100% 보장되는지는 미확정).

### 함정 ⑰ 커스텀 이벤트(EventGraph, `AddEvent|Custom|X`)는 파라미터를 추가할 수 없다(`add_node_pin`이 "does not support adding pins" 에러 반환) — 함수 그래프로 전환하거나 멤버 변수로 상태를 전달할 것
`add_node_pin`은 문서상 "Switch/Sequence/Make Array 등 동적 핀 추가·제거를 지원하는 노드"용이라고 되어 있는데, 이 목록에 커스텀 이벤트는 없다 — 실제로 시도하면 `Node "이벤트명" does not support adding pins.`로 즉시 실패한다. 커스텀 이벤트에 입력 파라미터가 꼭 필요하면 (a) `add_function_graph`로 함수 그래프를 만들어 `add_function_param`/`add_object_function_param`을 쓰거나(단, 함수 그래프는 §7 함정④처럼 latent 노드 사용 불가), (b) 이 프로젝트의 기존 관례(`PlayAttack`/`TakeHit`/`MarkerOn` 등 전부 무파라미터)를 따라 **호출 전에 멤버 변수를 세팅해두고 이벤트 안에서 그 변수를 읽는 상태 기반 패턴**으로 우회한다. 이번 사례(`WalkForward`)에서는 (b)를 채택해 계산용 멤버 변수(`WalkTargetLoc`)를 신설했다 — 같은 유닛이 중첩 호출될 일이 없는 턴제 구조라 레이스 문제는 없었다.

### MoveComponentTo(latent)의 output pin은 `then` 1개뿐이며, 이것이 곧 "이동 완료 후" 콜백으로 정확히 동작한다(실측 확인)
`컴포넌트|MoveComponentTo` 노드는 exec 입력이 3개(`Move`/`Stop`/`Return`)인데 exec 출력은 `then` 1개뿐이다(Completed/Stopped 같은 별도 이름의 델리게이트 출력이 없음). 설계 단계에서 "Completed 핀 있음"으로 전제했던 것과 표면적으로 다르지만, 실측(로그 타임스탬프)으로 확인한 결과 `then`이 정확히 "OverTime(예: 0.4초) 경과 후 이동 완료 시점"에 발화한다(예: `WalkFwd` 로그 t=3.067 → `WalkArrive` 로그 t=3.4, 정확히 그 사이 MoveComponentTo가 실행되고 완료 후 다음 exec인 로그 PrintString이 발화). 즉 이 노드는 진짜 latent이며 `then` = Completed로 취급해도 안전하다. 다만 실측 소요시간이 설정값보다 짧게 나오는 편차(0.4s 설정에 0.333s 실측, -16.75%)가 관찰됐다 — §9 함정⑦에서 보고된 "스로틀 꺼도 편차가 있다"는 현상과 같은 계열로 추정(PIE 게임시간 계산 자체의 오차 요인 미규명, 후속 조사 과제로 이월).

### 새 액터/컴포넌트 배치 전 8기(또는 N기) 일괄 실측이 설계 문서의 "예상값"을 크게 벗어날 수 있다 — 반드시 실측 후 채택
승인 plan 문서는 8기 스폰포인트의 Y좌표를 "약 −7150 부근"으로 예상했으나, `find_actors`+`get_actor_transform` 8회 실측 결과 실제 범위는 **−6861.80 ~ −7630.34**(폭 768.5cm)로 예상과 크게 달랐다. 예상치를 그대로 신뢰해 새 마커 좌표를 정했다면 z-fight 가드 계산이나 "10cm+ 이격" 요구사항이 실패했을 것 — **설계 문서의 좌표 예상값은 항상 실측으로 재검증하고, 실측값을 최종 채택 근거로 문서에 남길 것**(이번 사례처럼 예상과 실측의 괴리 자체가 크면 반드시 명시적으로 기록).

---

## 14. 걸어나오기연출 W2에서 확정된 노하우 (2026-07-07)

### 함정⑮의 일반화 재확인 — "이전 세션에서 만든" 다른 BP의 커스텀 이벤트도 `create_node`에는 `Class|<블루프린트명(언더스코어 제거)>|<멤버명>` 형식이 최우선 유효(빈 `context_pins`로 검색)
§13 함정⑮은 "이 세션에서 방금 만든 신규 멤버"에 한정된 현상처럼 기술됐으나, 이번 W2에서 **이전 세션(W1)에 이미 만들어 놓고 실제로 여러 차례 호출된 적 있는 `WalkForward`/`WalkBack`/`MarkerOff`**(전부 W1 raw 문서에 성공 호출 기록이 있음)를 이번 세션(W2)에서 **새로운 호출 지점**(Manager EventGraph의 다른 위치)에 추가하려 했을 때도 동일한 패턴이 재현됐다: `get_node_infos`가 보여주는 축약 표기(`|MarkerOff`)를 그대로 `create_node`에 넣으면 실패하고, `find_node_types`에 **context_pins를 채워서** 검색하면 `함수호출|MarkerOff` 같은 형태가 나오지만 이 역시 `create_node`에서 실패한다. **빈 `context_pins`(`[]`)로 검색해야만** `Class|BPBattleSpawnPoint|MarkerOff` 형식이 나오고 이것만 성공한다(같은 세션 내 `WalkForward`/`WalkBack`도 동일하게 재현). **결론**: "신규냐 기존이냐"가 아니라 **"다른 블루프린트의 멤버를 그래프 노드로 새로 생성하려는 모든 경우"**에 이 패턴이 적용되는 것으로 일반화 확정 — 시행착오를 줄이려면 처음부터 `context_pins=[]`로 `find_node_types`를 먼저 시도할 것.

### 함정⑯ 자기 자신의 블루프린트 멤버(같은 BP 안의 변수/함수)는 `find_node_types`가 반환한 문자열(`함수호출|X`, `Variables|디폴트|GetX`)이 그대로 `create_node`에 통과하지만, 유니코드 이스케이프 오타는 완전히 다른 방식으로 실패한다
스캐폴드 작업 중 `Variables|디폴트|GetActiveUnit`을 만들려고 수동으로 유니코드 이스케이프(`디폰트`)를 입력했는데 "does not exist" 에러가 반복 재현됐다. 원인은 **디폴트(정상)와 디폰트(오타) 두 글자가 자모 하나 차이**(폴=`ud3f4`, 폰=`ud3f0`)로, 육안으로는 렌더링된 한글이 똑같아 보이지 않지만(실제로는 다른 유니코드 코드포인트를 가리켜 콘솔에 다르게 출력됨) 실수로 잘못된 코드포인트를 타이핑한 것이었다. **탐지**: 같은 카테고리 문자열이 반복적으로 "does not exist"로 실패하면서 다른 유사 멤버(`GetTurnQueue`, `SetActiveUnit` 등 같은 `Variables|디폴트|` 접두어)는 성공하는 경우, 접두어 자체의 유니코드 인코딩을 `python -c "print([hex(ord(c)) for c in s])"`로 직접 검증할 것 — 한글 자모 하나 차이는 육안 검토로 거의 못 잡는다.

### 발견 — 다른 BP의 커스텀 이벤트를 CallFunction으로 직접 호출하면, 그 이벤트 내부에 latent 노드(Delay 계열)가 있을 경우 호출자(caller) 자신의 exec 흐름도 그 latent 완료까지 대기한다(같은 그래프 내 함수 호출과 동일하게 "latent 전파")
W2 타임라인 실측(WT-11) 중 1턴 총 길이가 plan 설계 예상(1.75s)보다 실측(2.333s)에서 +0.58s 더 걸리는 현상을 조사한 결과, 근본 원인은 `BP_BattleManager`가 `BP_BattleSpawnPoint`의 `PlayAttack` 커스텀 이벤트를 `CallFunction` 노드로 직접 호출하는데, **`PlayAttack`의 내부 그래프 자체에 `RetriggerableDelay` 노드 4개(공격 애니메이션 타이머, W2 이전부터 존재)가 직렬로 포함**되어 있었다는 점이다. 이 때문에 Manager 쪽의 `PlayAttack.then`(다음 Sequence 노드로 이어지는 exec 출력)은 PlayAttack 호출 즉시 발화하는 것이 아니라, PlayAttack 내부의 모든 RetriggerableDelay 체인이 완료된 뒤에야 발화한다 — 즉 **다른 BP의 이벤트를 CallFunction으로 호출하는 것은, 그 이벤트가 내부에 latent 노드를 가지고 있다면 호출자 관점에서도 latent 호출이 된다**(§7 함정④가 "함수 그래프에서 Delay 사용 불가"였던 것과는 다른 계열의 사실 — 이건 "커스텀 이벤트 호출자가 그 이벤트의 내부 latent를 투명하게 흡수한다"는 실측 확인). **실전 시사점**: 다른 BP의 이벤트를 호출해 그 직후 타이밍을 정밀 설계할 때는, 반드시 그 이벤트의 **내부 그래프도 먼저 조회**(`get_connected_subgraph`)해 latent 노드 유무를 확인할 것 — 겉보기엔 "즉시 반환하는 트리거성 호출"처럼 보여도 내부에 Delay가 있으면 호출자의 전체 타이밍 설계가 그만큼 밀린다.

### 게이트 스캐폴드 설계 시 "레벨이 이미 자동으로 진행 중인 상태"를 가정하지 말고 먼저 로그로 확인할 것
BeginPlay에 `InitBattle()` 호출을 포함한 스캐폴드를 심었는데, 실제로는 **레벨(GameMode 등)이 이미 BeginPlay t=0에 자체적으로 InitBattle을 호출하고 있어서**, 스캐폴드의 중복 호출이 이미 AwaitTarget까지 진행된 상태를 되돌려버리는 부작용(`NotifyUnitClicked: ignored`)이 발생했다. **탐지**: 스캐폴드 실행 후 로그에 같은 State 전환 로그가 **두 번 다른 GameTime**(`t=0`과 `t=1.x`처럼)으로 나타나면 중복 초기화를 의심할 것. **해법**: 스캐폴드를 짜기 전에 먼저 순수 관찰(스캐폴드 없이 StartPIE→GetLogEntries)로 레벨이 자동으로 어디까지 진행되는지부터 확인하는 습관이 왕복을 줄인다.

### `NotifyUnitClicked` 같은 "특정 유닛을 대상으로 하는" 함수를 스캐폴드에서 호출할 때, `TurnQueue`의 정적 인덱스로 팀을 가정하지 말 것
`GetArrayItem(TurnQueue, 4)`가 항상 상대팀일 것이라 가정하고 고정 인덱스로 타겟팅했으나 `NotifyUnitClicked: ignored (same team or self)`가 재현됐다 — TurnQueue 순서는 속도 정렬 등으로 팀이 고정 배치되지 않는다(미규명, 이 프로젝트의 다른 노하우 문서에도 "8기 좌표 예상과 실측이 다르다"는 유사 패턴이 반복됨 — **"배열 순서/좌표 등 구조적 가정은 실측 없이 하드코딩하지 말 것"**이라는 상위 원칙의 또 다른 사례). **해법**: `ForEachLoopWithBreak` + `Branch(GetIsParty(Element) != GetIsParty(ActiveUnit))` 런타임 탐색으로 항상 유효한 상대팀 유닛을 동적으로 찾는 패턴이 정적 인덱스보다 안전하다.

### 스로틀(bThrottleCPUWhenNotForeground) 설정 — 개발 기간 동안 false 유지 권장
W2 타이밍 검증에서 스로틀을 OFF(false)로 설정한 뒤 실측한 GameTime 로그가 안정적이었다. 이후 에이전트 PIE 검증 시에도 동일한 조건(스로틀 OFF)에서 실행해야 재현성이 높다. **프로젝트 정책 확정 필요(2026-07-07 Director)**: 개발 기간 동안 스로틀을 기본값 false로 유지할지, 아니면 ON/OFF 양쪽을 별도로 검증할지. MCP를 통한 `GetSectionPropertyValues`/`SetSectionProperties`로 런타임 변경 가능하나, 한 번 정책이 정해지면 모든 에이전트 검증 세션이 그에 맞춰야 한다.

---

## 15. 걸어나오기연출 W3fix(걸음 왜곡 핫픽스)에서 확정된 노하우 (2026-07-07)

### 함정 ⑱ `MoveComponentTo`는 회전도 함께 latent 보간한다 — `TargetRelativeRotation` 핀을 미배선하면 조용히 (0,0,0)으로 보간되어 비회전 스프라이트를 눕혀버린다
`컴포넌트|MoveComponentTo`는 `TargetRelativeLocation`(위치)뿐 아니라 `TargetRelativeRotation`(회전) 핀도 가지고 있으며, 이 핀을 배선하지 않으면 기본값 `(0,0,0)`으로 **매 호출마다 실제로 그 회전으로 보간**한다 — 에러도 경고도 없다. 스프라이트 쿼드처럼 `relativeRotation.roll=90`이 정규 회전값인 컴포넌트를 이 노드로 이동시키면, 이동할 때마다 roll이 0으로 서서히 눕혀지고(이동 중 비균등 스케일과 결합해 꾸겨짐으로 보임), 이동 완료 후에는 roll=0으로 고착된다(도착 후에도 계속 왜곡). 좌표만 로그로 검증하는 이동 계열 TC는 이 결함을 놓친다(이번 프로젝트 W1 게이트가 좌표만 검증해 사각지대가 됐던 실사례).
**해법**: 이동 노드를 새로 배선할 때는 **반드시 `TargetRelativeRotation`에 그 컴포넌트의 정규 회전을 명시적으로 연결**한다. 리터럴 문자열(`set_pin_value`로 `"0, 0, 90"` 등)은 Rotator 필드 순서(Pitch/Yaw/Roll vs Roll/Pitch/Yaw)가 모호해 오설정 위험이 있으므로 피하고, **`MakeRotator` 노드를 생성해 Pitch/Yaw/Roll 필드를 각각 `set_pin_value`로 명시**한 뒤 `ReturnValue`를 `TargetRelativeRotation`에 연결하는 편이 안전하다(각 필드는 index_id로 구분되며 이 프로젝트 실측 순서는 Roll=0, Pitch=1, Yaw=2 — MakeRotator 노드마다 `get_node_infos`로 실제 index_id를 재확인할 것, 버전에 따라 달라질 수 있음).
**교훈 일반화**: 이동 계열 TC(WalkForward 등)를 설계할 때는 **좌표뿐 아니라 회전값도 검증 항목에 포함**할 것 — 좌표는 정확한데 회전이 틀어지는 결함은 좌표만 보는 로그로는 절대 못 잡는다.

### `GetRelativeRotation`(SceneComponent 네이티브 함수)은 이 MCP `create_node`에서 어떤 문자열 형식으로도 생성 불가로 확정 — `GetWorldRotation`으로 대체 가능(루트 컴포넌트 한정)
디버그 로그용으로 컴포넌트의 `RelativeRotation`을 그래프에서 조회하려고 `find_node_types`(빈 `context_pins`와 채운 `context_pins` 양쪽)로 검색하면 `Class|씬컴포넌트|GetRelativeRotation`, `Variables|트랜스폼|GetRelativeRotation` 등 여러 후보 문자열이 나오지만, **이 중 어느 것을 `create_node`에 넣어도 "does not exist"로 실패**한다(§10/§14의 "표시 문자열 ≠ 생성 문자열" 패턴과 계열은 같으나, 그 문서들이 제시한 해법—기존 노드 역산, `Class|블루프린트명|멤버명` 형식, `b` 접두어 제거 등—이 전부 적용되지 않는 케이스다. `declaring_class`를 `/Script/Engine.SceneComponent`로 명시해도 실패). 근본 원인 미규명(엔진 네이티브 함수의 BlueprintCallable 노출 방식과 이 MCP 도구의 노드 생성 로직 사이 불일치로 추정, 후속 조사 과제로 이월).
**실전 대안**: 대상 컴포넌트가 **그 액터의 루트 컴포넌트**(부모 없음)라면 Relative == World이므로, `find_node_types`로 정상 생성 가능함이 확인된 `트랜스포메이션|GetWorldRotation`(`self` 핀에 컴포넌트 레퍼런스 연결, Pure 함수)으로 완전히 동등한 값을 얻을 수 있다. 비루트 컴포넌트의 RelativeRotation이 꼭 필요하면 `GetRelativeTransform`(컴포넌트 간 상대 트랜스폼, self→self로 자기 자신 기준을 구한 뒤 Rotation을 Break) 등의 우회가 필요할 것으로 보이나 이번 세션에서는 검증하지 않음(이월).

### FormatText 노드의 동적 인자 핀은 `add_node_pin`으로 추가 가능(§17 "커스텀 이벤트는 파라미터 추가 불가"와는 다른 계열) — 단, 순차 호출 권장
§13 함정⑰은 "커스텀 이벤트(AddEvent|Custom)는 `add_node_pin`으로 파라미터를 추가할 수 없다"였으나, **FormatText 노드는 `add_node_pin`으로 인자 핀(0, 1, 2...)을 정상적으로 추가할 수 있다**(공식 문서상 "Switch/Sequence/Make Array 등 동적 핀 지원 노드"에 FormatText도 포함되는 것으로 실측 확인 — 매 호출마다 다음 index_id의 새 입력 핀이 생성됨). §8 함정⑤(`add_event` 병렬 호출 시 이름 충돌)의 예방 원칙을 그대로 적용해 이번에도 2개 핀을 **순차(1개씩)** 호출로 추가했고 문제없이 각각 index_id=1, 2로 정상 생성됨 — 동적 핀 추가 계열 노드 전반에 순차 호출 습관을 유지하는 것이 안전하다.

### 진단용 임시 스캐폴드/로그 삽입-제거 사이클에서 exec 체인 복원 순서 — `break_pins`로 끊기 전에 반드시 원래 연결 대상을 기록해둘 것
이번 사례처럼 기존 exec 체인(`A.then → B`) 중간에 진단 노드를 끼워 넣었다가(`A.then → Diag.execute`, `Diag.then → B`) 검증 후 원상복구할 때는, **먼저 `break_pins(A.then, Diag.execute)`와 `break_pins(Diag.then, B)`로 진단 노드와의 연결을 모두 끊은 뒤, `connect_pins(A.then, B)`로 원래 직결을 재생성**하고, 그 다음에야 진단 노드들을 `delete_node`로 제거하는 순서가 안전하다(진단 노드를 먼저 지우면 `B`의 정확한 refPath를 다시 찾아야 하는 번거로움이 생길 수 있음 — 삽입 시점에 기록해둔 원래 대상 노드의 refPath를 끝까지 보존해두는 습관이 유용하다). 이번 세션에서 이 순서(끊기→재연결→삭제)로 WalkForward/WalkBack 양쪽 모두 정확히 원상복구했고, 재조회로 원래 배선과 100% 일치함을 확인했다.


---

## 16. 카메라액션 C0+C1에서 확정된 노하우 (2026-07-07)

### `유틸리티|SelectObject`의 ReturnValue는 자동 타입 승격이 안 된다
A/B 입력에 Actor(또는 특정 클래스) 레퍼런스를 연결해도 ReturnValue는 **제네릭 UObject로 고정** — 그대로 Actor 파라미터 핀(예: SetViewTargetWithBlend의 NewViewTarget)에 연결하면 타입 불일치. **`CastToActor`(또는 대상 클래스 캐스트) 노드를 사이에 삽입**해서 우회한다. `Utilities|Casting|CastTo*` 계열이 스캐폴드에서도 동일하게 필요했음(재현 2회).

### 스캐폴드 대기시간은 "명목 턴 길이"가 아니라 "실측 턴 길이" 기준으로
W2에서 실측된 대로 1턴 실소요(≈3s+)는 명목 설계(2.1s)보다 길다(PlayAttack 내부 latent가 호출자를 붙잡는 특성). 스캐폴드의 턴 간 Delay를 명목값으로 잡으면 `bInputLocked` 가드에 막혀 **"게임 클럭 정지"(§9 함정⑦)로 오판하기 쉽다** — 로그에 `BLOCKED (bInputLocked=true)`가 찍히는지 먼저 확인하면 타이밍 부족과 클럭 정지를 즉시 구분할 수 있다. 스캐폴드 턴 간격은 실측+여유(4.0s)로.

---

## 17. 카메라액션 v3(동적 어깨너머 컷)에서 확정된 노하우 (2026-07-08)

### 함정 ⑲ 프로모터블 오퍼레이터의 A핀(예: Vector)을 먼저 연결한 뒤 B핀에 `set_pin_value`로 스칼라 리터럴("-1.0" 등)을 세팅하면, 노드가 이미 A핀 타입으로 승격되어 B핀도 같은 타입이 되고 스칼라 문자열이 파싱 실패해 조용히 소실(값 없음→사실상 0)된다 — 에러·경고 없이 로직이 틀린 결과를 낸다
`lat_flip_mul = normalize_lat(Vector) * -1.0`(부호반전 의도의 스칼라곱)을 프로모터블 곱셈 노드로 구성할 때, **A핀(Vector)을 먼저 `connect_pins`로 연결한 뒤 B핀에 `set_pin_value(B, "-1.0")`을 호출**했다. 이 시점 노드는 이미 A핀 타입에 맞춰 `수학|벡터|vector*vector`(Vector×Vector 성분곱)로 승격되어 있었고, B핀도 Vector 타입이 되어 `-1.0`이라는 스칼라 문자열이 Vector로 파싱되지 못해 값이 소실, 사실상 `(0,0,0)`으로 남았다. `set_pin_value` 자체는 `returnValue: null`(성공)을 반환하므로 **호출 결과만으로는 실패를 감지할 수 없다** — 반드시 `get_node_infos`로 B핀의 실제 `value`와 `type_id`를 재조회해야 드러난다(이 사례에서 `type_id`가 `수학|벡터|vector*vector`로 나온 것이 결정적 단서였음).

**증상의 위험성**: 이 버그는 "대칭 케이스 중 한쪽만" 틀린 결과를 냈다(부호반전이 필요 없는 케이스=정상, 필요한 케이스=완전히 틀린 좌표) — 컴파일은 항상 0 에러, 실행도 크래시 없이 조용히 잘못된 값만 낸다. **이런 종류의 결함은 대칭 로직(양 팀·양 부호·양방향)의 양쪽을 모두 실측 대조해야만 발견된다** — 한쪽만 확인하고 "정상"으로 판정하면 놓친다.

**해법**: Vector×Float 스칼라곱 의도라면, (a) A핀 연결 전에 B핀을 먼저 float로 확정짓거나, (b) 더 안전하게 **부호반전은 곱셈이 아니라 뺄셈으로 표현**한다(`flipped = ZeroVector - v`, Vector-Vector 연산 — 이미 이 프로젝트의 다른 곳(`mul_axis_back` 등)에서 안전하게 검증된 Vector-Vector/Vector+Vector 승격 패턴과 동일 계열이라 이 함정 자체를 회피한다). §9(프로모터블 오퍼레이터는 연결 후 재조회로 확인)의 "재조회 습관"을 **핀 값을 세팅하는 모든 시점**(데이터 연결뿐 아니라 `set_pin_value` 리터럴 세팅 직후도)으로 확장 적용할 것.

### `SelectVector`(Utilities Select, pure)의 `bPickA` 의미론은 표준(`true`=A 반환)을 그대로 따른다 — 배선 오류가 아니라 입력값 자체(위 함정⑲)를 먼저 의심할 것
이번 사례에서 `SelectVector`의 `bPickA=NOT(latY>0)` 배선 자체(`A=원본lat`, `B=반전lat`, `bPickA` 연결 방향)는 애초부터 정확했다 — 실패 원인은 `B`(반전lat) 입력값 자체가 함정⑲으로 소실된 것이었다. `SelectVector`/`Select` 계열 노드에서 예상과 다른 값이 나올 때는, 먼저 **A/B 각각의 값을 직접 진단 로그로 찍어(임시 `ToString`+`PrintString` 스캐폴드, §15 "진단용 임시 스캐폴드" 정석 패턴 재사용) Select 자체가 아니라 그 입력값이 틀렸는지부터 격리**할 것 — Select 노드의 조건 배선을 의심하기 전에 입력 두 값의 실측이 더 빠른 판별법이다.

### 리터럴 오브젝트 레퍼런스 CDO에만 `set_properties`를 적용하면 기존 레벨 인스턴스의 신규 변수 기본값이 반영되지 않을 수 있다 — CDO와 인스턴스 양쪽에 개별 세팅 필요
Manager에 float 변수 6종을 신규 추가한 뒤 CDO(`Default__BP_X_C`)에만 `set_properties`로 기본값을 세팅했으나, 이미 레벨에 배치되어 있던 인스턴스(`BP_X_C_0`)를 `get_properties`로 재조회하면 **전부 0(타입 기본값)으로 남아있었다** — 변수를 신규 추가해도 기존 배치 인스턴스가 CDO의 새 기본값을 자동으로 상속하지 않는 것으로 관찰됨(엔진의 "기존 인스턴스는 저장된 프로퍼티 오버라이드 없이 컴파일 시점 기본값을 그대로 캐시" 동작으로 추정, 근본 메커니즘 미규명). **해법**: 신규 변수의 기본값을 실제로 레벨에서 쓰이게 하려면 **CDO뿐 아니라 이미 배치된 레벨 인스턴스에도 개별 `set_properties`를 호출**하고, 양쪽 다 `get_properties`로 재확인할 것 — CDO 세팅만으로 "완료"라고 판단하면 실제 게임플레이에서는 값이 전혀 반영되지 않는 채로 넘어갈 위험이 크다(§12 plan 지시 "CDO에 개별 set_properties + 매회 재조회"가 정확히 이 문제를 예방하려는 지시였음을 이번 사례로 재확인).

---

## 18. 카메라액션 토글버튼 라벨 키 소실 핫픽스에서 확정된 노하우 (2026-07-08)

### 함정 ⑳ `StringTableTools.set_entry`는 기존 StringTable 패키지를 dirty로 표시하지 않는다 — `save_assets`가 명시적 경로를 줘도 무음으로 저장을 스킵한다(원 결함의 근본 원인 확정)
`set_entry`로 기존 StringTable에 새 키를 추가하면 `get_entry`/`list_keys` 재조회로는 정상 반영된 것처럼 보이지만, 그 직후 `AssetTools.is_dirty(경로)`를 호출하면 **`false`**가 나온다. 이 상태에서 `save_assets(asset_paths=["/Game/.../ST_UI"])`(빈 리스트가 아니라 명시적 경로!)를 호출해도 `returnValue: true`(에러 없음)를 반환하지만, **파일 mtime이 갱신되지 않고 디스크 바이너리에 새 키/값 문자열이 전혀 없다**(직접 바이트 검색으로 확인) — 즉 "저장 성공"처럼 보이는 리턴값 뒤에서 실제로는 아무것도 쓰이지 않는다. **대조군**: `StringTableTools.create`로 새로 만든 애셋은 생성 직후 `is_dirty=true`이고, 그 상태에서 `set_entry`+`save_assets`는 정상적으로 디스크에 반영된다 — 버그는 `set_entry` 단독 호출이 dirty를 세팅하지 않는다는 데 있다(`create`는 정상). **실전 절차**: 기존 StringTable에 `set_entry`로 키를 추가/수정한 뒤에는 반드시 `is_dirty`를 재확인하고, `false`로 남아있으면 `save_assets`를 아무리 반복 호출해도 소용없다 — 이 프로젝트의 이전 세션에서 "키 추가는 했는데 재시작 후 사라짐"으로 보고된 사고의 정확한 메커니즘이 이것이다. 강제 dirty 수단(메타데이터 태그 세팅→제거 등)은 이번 세션에서 시도했으나 확실히 검증하지 못했다(이월 과제) — 현재 유일하게 검증된 우회는 **전체 키 목록을 `list_keys`+`get_entry`로 백업한 뒤 `create`로 재생성**하는 것.

### 함정 ㉑ 이미 존재하는 경로에 `StringTableTools.import_file`을 시도해 "already exists" 에러가 나면, 그 실패한 호출이 부작용으로 **기존 애셋 파일을 디스크에서 삭제**할 수 있다 — 매우 위험, 재시도 금지
함정⑳의 dirty-안 걸림 문제를 우회하려고 기존 `/Game/UI/ST_UI` 경로에 CSV `import_file`을 시도했다(같은 폴더·같은 애셋명). 호출은 `"create_asset: ST_UI at /Game/UI already exists"` 에러로 실패했으나, 직후 `find_assets`/`ls Content/UI/`로 확인하니 **기존 `ST_UI.uasset` 파일 자체가 디스크에서 사라져 있었다**(1회 재현, 정확한 내부 메커니즘은 미규명 — 애셋 생성 파이프라인이 이름 충돌 검사 이전에 대상 슬롯을 선점/언링크하는 것으로 추정). **이 프로젝트는 `Content/` 전체가 `.gitignore` 대상이라 git으로 복구 불가능함도 이번에 확정**(백업 수단이 원본 데이터 기억/재구성뿐). **실전 절차**: 기존 애셋과 같은 폴더+이름으로 `import_file`을 시도하기 전에 **반드시 다른 이름(예: 임시 스크래치 애셋)으로 먼저 안전성을 검증**하거나, 애초에 이 경로(재임포트로 우회)를 피하고 함정⑳의 백업+재생성 절차를 곧장 쓸 것. 실패 에러를 봤다고 안전하게 롤백됐다고 가정하지 말고, **에러 발생 즉시 대상 애셋의 존재 여부를 재확인하는 습관**이 필요하다.

### 함정 ㉒ 비균등 스케일+회전 부모(§7 함정②)의 자식 `TextRenderComponent`는 `RelativeLocation`의 국소축 변화량과 화면상 이동량이 비례하지 않고, 특정 구간에서 렌더링이 완전히 사라지는 비단조 회귀가 발생할 수 있다
§7 함정②는 "비균등스케일+회전 부모의 자식에 SetWorldRotation/Scale을 쓰면 전단된다"였는데, 이번 사례는 **`RelativeLocation`(단순 오프셋) 하나만 바꿔도 유사 계열의 예측 불가능성**이 나타남을 추가로 확인했다. `ButtonBg`(scale 2.2,1.2,1 / rotation pitch90,yaw84,roll0)의 자식 `LabelOn`에서 `RelativeLocation.Z`를 30→0→-140으로 단계적으로 낮추자, 화면상 텍스트는 "판 위로 뜸(Z=30)" → "판 상단 안쪽으로 진입(Z=0)" → "완전히 안 보임(Z=-140, 3회 캡처 연속 재현)"으로 변했다 — 로컬 Z 감소량과 화면상 이동량의 비율이 구간마다 달랐고(Z=30→0 구간 대비 Z=0→-140 구간에서 선형 외삽이 완전히 빗나감), 특정 임계값을 넘기면 텍스트가 판 뒤로 넘어가거나 프러스텀을 벗어나는 것으로 추정되는 완전 소실이 발생했다. **해법(이번엔 채택)**: 값을 무리하게 밀어붙이지 말고, **원래 값으로 되돌리고 안전하게 확인된 개선(정렬 Left/Bottom→Center/Center)만 유지**하는 보수적 선택이 3회 실패 규칙과 부합했다. **후속 과제**: 이 계열 컴포넌트의 위치를 정밀 제어하려면 §7 함정②가 제시한 `bAbsoluteLocation/Rotation/Scale=true` 우회(단, 회전은 부모의 유효 월드회전을 직접 계산해 재적용해야 시각적 방향이 유지됨)를 다음 세션에서 시도할 것.

### `CaptureViewport`가 같은 파라미터로 연속 호출해도 결과가 크게 달라지는 사례 추가 확인(§12 함정⑫의 확장) — 특정 근접 각도에서 에디터 그리드 플레인(연보라색)이 실제 씬 대신 캡처되기도 함
카메라 토글 버튼에 근접한 특정 시점(액터 경계 근처)에서 완전히 동일한 `captureTransform`으로 연속 캡처했을 때 (a) 씬이 정상 렌더된 프레임, (b) 지형 대신 연보라색 무한 그리드 플레인이 지평선까지 채워진 프레임, (c) 오브젝트는 보이는데 그 위 텍스트만 사라진 프레임이 **비결정적으로 섞여 나왔다**(창 최소화 여부와 무관, `IsIconic=false` 확인 후에도 재현). §12 함정⑫가 보고한 "최소화 시 스테일 프레임" 문제와는 별개로, **에디터 창이 정상 상태여도 근접/경계 각도에서 캡처 자체가 불안정**할 수 있다는 새로운 사례로 기록한다. **대응**: 이런 캡처가 나오면 씬 자체 문제로 오판하지 말고, 카메라를 원래 신뢰할 수 있었던 거리/각도(더 멀리, 또는 이전에 정상 캡처됐던 정확히 같은 좌표)로 되돌려 재캡처해 재현성을 먼저 확인할 것 — 이번 사례에서도 "정상 캡처됐던 좌표"로 되돌아가자 다시 정상 렌더가 나왔다(다만 100% 안정적이진 않았음, 근본 원인 미규명·이월).

---

## 19. 알파 A0 스파이크 병렬 착수에서 확정된 노하우 (2026-07-08)

### 함정 ㉓ 특정 `asset_type`으로 `BlueprintTools.create`를 호출하면 엔진이 블로킹 Slate 모달을 띄우고, 그 순간 **공유 MCP 브릿지 전체(다른 세션 포함)가 완전히 마비**된다 — Win32/UI Automation 둘 다로 내용을 읽을 수 없어 오너의 육안 확인 없이는 복구 불가
알파 A0 스파이크 3건(UMG·합성 머티리얼·CSV 파이프라인)을 동시에 launch했는데, 셋 다 거의 동시(UTC 07:26~07:28) `BlueprintTools.create(asset_type=UserDefinedStruct 또는 Widget계열)` 호출 직후 `MCP server "unreal-mcp" is not connected`로 전면 마비됐다 — **자신이 호출하지 않은 세션까지 포함해 전부.** 3중 교차진단으로 원인 확정:
1. **프로세스**: `Get-Process`로 확인 — PID 생존, `Responding=True`(OS 메시지펌프는 살아있어 완전 크래시가 아님).
2. **엔진 로그**: `projectTP.log`의 `LogModelContextProtocol` 타임라인 — 마지막 dispatch가 `BlueprintTools.create`이고 그 직후 **모든 백그라운드 틱(5~7분 주기 `LogEOSSDK`조차)이 완전히 멈춤** — 엔진의 정상 프레임 루프 자체가 정지했다는 결정적 신호.
3. **Win32 윈도우 열거**(`EnumWindows`, PID 소유 윈도우 전수): 메인 에디터 창의 **소유(owned) 모달 윈도우** — 제목 "메시지", class `UnrealWindow`, 494×149px — 가 **13분+ 계속 열려 있음**을 직접 확인. `EnumChildWindows`와 `AutomationElement.FindAll` **둘 다 자식 0개** 반환 — Slate가 네이티브 컨트롤/접근성 트리를 노출하지 않아 **다이얼로그 내용을 기계적으로 읽을 방법이 없다.**

**메커니즘 추정(정황 근거, 신뢰도 높음)**: "정상적이지 않은" `asset_type`(구조체 팩토리, 에디터 전용 Widget 클래스 등)으로 `BlueprintTools.create`를 호출하면 엔진 내부에서 블로킹 네이티브 모달을 띄우는 경로를 탄다. 이 모달은 Slate의 중첩 이벤트루프 안에서만 돌아서 OS 레벨엔 "Responding"으로 보이지만, **엔진 틱과 MCP 커맨드 디스패치는 완전히 멎는다.** MCP 브릿지가 단일 커맨드 큐를 여러 클라이언트가 공유하는 구조로 보여, **한 세션이 이 모달을 띄우면 그 세션을 호출하지 않은 다른 모든 세션까지 함께 마비**된다.

**실전 절차**:
1. **`asset_type`에 확신 없는 클래스**(struct 팩토리, WidgetBlueprint류, 에디터 전용 클래스 등)로 `BlueprintTools.create`를 시도할 땐 **한 번에 하나씩, 매 호출 후 응답 정상 여부를 확인하고 다음으로 진행**(병렬 금지 — 트리거 자체가 이 호출일 수 있음).
2. **여러 에이전트가 같은 UE 에디터(unreal-mcp)를 동시에 건드리는 작업**은 한 메시지로 병렬 launch하지 말 것. MCP를 안 쓰는 순수 조사·문서 작업(designer 논의, Pillow 실측 등)은 병렬 무방 — "독립적"의 기준에 **"같은 외부 리소스(unreal-mcp 세션)를 공유하지 않는다"**를 추가할 것.
3. **차단 발생 시 데스크톱 자동화로 임의 클릭 금지** — 다이얼로그 내용을 못 읽는 상태에서 아무 버튼이나 누르면 의도치 않은 동작(예: 데이터 손실 확인창의 "예") 위험. **오너가 에디터 화면을 직접 보고 다이얼로그를 확인·닫아야** 복구된다. 이건 Director가 판단해 오너를 호출할 사안이지, 서브에이전트가 임의로 자동화 클릭을 시도할 영역이 아니다(이번 사례에서 두 에이전트 모두 이 판단을 정확히 지켰다).
4. 복구 후 재개: 각 스파이크가 남긴 "재개 지점"부터 이어가면 이미 확정된 부분은 재조사 불필요.

### 확정 — `BlueprintTools.create`의 `asset_type`별 동작 (2026-07-09, Director 직접 재현 + A0 스파이크 실증)
함정㉓의 "추정"을 실측으로 확정했다. **판별선은 asset_type이 Blueprintable UObject인가 아닌가**다:

| asset_type | 결과 | 근거 |
|---|---|---|
| `/Script/UMG.UserWidget` (Blueprintable) | ✅ **모달 없이 정상 생성** — 진짜 `WidgetBlueprint` 컨테이너 생성됨(`find_assets` 타입필터로 확정, 일반 Blueprint 아님) | A0① 재개 |
| `/Script/CoreUObject.UserDefinedStruct` (비-Blueprintable) | ❌ **블로킹 모달 → 300초 무응답 → MCP 마비** | Director가 직접 1회 호출로 재현, 오너가 팝업 닫아 복구 |

- **실무 규칙**: `create`로 만들 때 asset_type이 **Blueprintable 클래스(액터·UserWidget·컴포넌트 등)면 안전**, **struct·비-Blueprintable이면 모달 위험** → 후자는 오너가 에디터에서 수동 생성해야 한다. (전용 create 도구가 있는 애셋 — `MaterialTools.create_material`·`DataTableTools.create`·`StringTableTools.create` — 은 모달 없이 안전. 문제는 전용 도구가 없어 범용 `BlueprintTools.create`를 써야 하는 경우.)

### 확정 — WidgetBlueprint 내부 위젯트리는 MCP로 조작 불가 (2026-07-09, A0①)
`WBP_Probe`(진짜 WidgetBlueprint) 생성 후, `WidgetTree`/`RootWidget` 프로퍼티를 `ObjectTools`의 `list_properties`/`get_properties`/`set_properties` **전부로 read·write 시도했으나 모두 막힘**(camelCase·PascalCase 무관). 서브오브젝트 경로(`:WidgetTree`)로 오브젝트 실존은 리졸브되나 그 내부(RootWidget·자식 위젯)로는 진입 불가. 전용 Widget/UMG 툴셋도 0개(재확인).
- **결론(알파 UMG 워크플로우 확정)**: **WBP 껍데기 생성·컴파일·저장 = MCP 가능 / 위젯 레이아웃 배치(Button·TextBlock 트리) = 오너 수동 필요 / 데이터 바인딩·이벤트 로직·문자열 연결 = (골격이 있으면) MCP 가능**. 이 하이브리드가 알파 UI 실행 방식이다([[알파_개발계획]] §2.6① 파이프라인의 "전사" 단계에 반영). cpp-engineer의 전용 위젯 브릿지 추가는 베타 후보(MVP는 오너 수동 골격으로 충분).

---

## 20. 전투완성 F3(스탯 로드+HP게이지)에서 확정된 노하우 (2026-07-14)

### 함정 ㉔ 컴포넌트 템플릿(CDO)에 `set_properties`로 세팅한 `bAbsoluteLocation`/`bAbsoluteRotation`/`bAbsoluteScale`은 **레벨에 이미 배치된 인스턴스**에 전파되지 않는다 — 인스턴스마다 개별로 다시 세팅해야 함
`ActorTools.add_component`로 새 컴포넌트(`TextRenderComponent`)를 Blueprint에 추가한 뒤, 그 컴포넌트 템플릿(`BP_X_C:CompName_GEN_VARIABLE`)에 `bAbsoluteLocation/Rotation/Scale=true`를 `set_properties`로 세팅하고 `get_properties`로 즉시 `true` 확인까지 했음에도, **이미 레벨에 배치돼 있던 8개 인스턴스**(`BP_X_C_0` 등)를 PIE로 재조회하면 전부 `false`로 나왔다(신규 스폰 액터가 아니라 기존 배치 액터라 CDO 변경이 소급 적용되지 않는 것으로 추정, 근본 메커니즘 미규명). **증상**: `SetWorldLocation`/`AddWorldOffset`/`SetWorldRotation`을 BeginPlay 그래프 노드로 정확히 호출해도(§7 함정③과 무관한 안전 경로), `bAbsolute*`가 실제로는 `false`라서 결과값이 **부모(꼭짓점 컴포넌트)의 회전·스케일을 거쳐 역변환된 relative 값**으로 저장되고, 부모의 회전·스케일이 8개 인스턴스 전부 동일(위치만 다름)했기 때문에 **8개 인스턴스의 relativeLocation/relativeRotation이 우연히 완전히 동일한 값으로 나와** "위치 계산이 액터별로 반영 안 된다"는 오판을 유발하기 쉽다(실제로는 world 결과 자체는 부모 origin이 상쇄돼 일치하는 게 수학적으로 정상 — 다만 bAbsoluteScale=false라 텍스트가 부모의 비균등 스케일을 그대로 물려받아 렌더링이 일그러지는 게 진짜 문제). **판별법**: PIE 인스턴스에서 `get_properties(component, ["bAbsoluteLocation","bAbsoluteRotation","bAbsoluteScale"])`을 CDO 세팅 직후 반드시 재조회할 것 — CDO에서 `true` 확인했다고 안심하지 말 것. **해법**: `find_actors`로 얻은 **각 레벨 인스턴스**에 대해 개별적으로 `set_properties({"bAbsoluteLocation": true})`(개별 호출, §7 함정⑪ 준수)를 반복 적용하면 정상 반영된다(8개 전부 PIE 재확인 완료).

### 확정 — 방금 추가한 컴포넌트의 Get 노드는 `find_node_types` 검색 인덱스에 즉시 안 잡히지만, `Variables|디폴트|Get<컴포넌트명>` 패턴으로 `create_node`는 곧바로 성공한다
`add_component`+`compile_blueprint` 직후 `find_node_types(filter="Get<새컴포넌트명>")`가 빈 배열을 반환했다(기존 컴포넌트 `Sprite`로 같은 패턴 검색하면 `Variables|디폴트|GetSprite`가 정상 검색됨 — 대조군 확인). 그러나 `create_node`에 **검색 없이** `Variables|디폴트|Get<새컴포넌트명>` 문자열을 직접 넣으면 즉시 성공하고 `get_node_infos`로 타입도 정상 확인된다. **결론**: `find_node_types`의 검색 인덱스는 방금 추가된 신규 멤버에 대해 갱신 지연이 있는 것으로 보이나, `create_node`의 실제 이름 해석(클래스 리플렉션 직접 조회로 추정)은 지연이 없다 — 새 컴포넌트/변수를 추가한 직후엔 기존 컴포넌트로 검증된 명명 패턴(`Variables|디폴트|Get<이름>`/`Variables|디폴트|Set<이름>`)을 **검색 없이 직접 시도**하는 편이 빠르고 안전하다.

### 확정 — `Get Data Table Row`(K2Node_GetDataTableRow)는 `Found` bool이 아니라 **`then`/`RowNotFound` 두 개의 별도 exec 출력 핀**을 가진다 + `Break <구조체>`는 `get_node_type_pins`에서 에러가 나도 `create_node`(`Utilities|Struct|Break<구조체명>` 패턴)는 정상 동작
`find_node_types("데이터테이블행가져오기")`로 찾은 `Utilities|데이터테이블행가져오기`로 노드를 만들면 실행 출력이 `then`(찾음)/`RowNotFound`(못 찾음) 2개라 별도 `Branch` 노드 없이 바로 분기 배선 가능하다. `DataTable` 입력 핀에 `set_pin_value`로 애셋 소프트패스를 리터럴로 주면(액터 레퍼런스가 아닌 콘텐츠 애셋이라 §9 함정⑥ 그림자 액터 문제와 무관, 안전) `ReturnValue` 와일드카드 출력이 즉시 실제 struct 타입(`F Job Stats Row 구조체`)으로 승격된다. 이 승격된 출력 핀을 `context_pins`로 넘겨 `find_node_types("Break")`를 검색하면 `||Break<구조체명>`(더블파이프)이 나오지만 **이 문자열로 `create_node`하면 "does not exist" 에러**가 난다 — 대신 다른 모든 `Break*` 예시(`BreakVector`, `BreakDataTableRowHandle` 등)와 동일한 `Utilities|Struct|Break<구조체명>` 패턴으로 직접 시도하면 성공한다(`get_node_type_pins`로 사전 미리보기하면 같은 이유로 에러 나지만 `create_node`는 무관하게 성공 — 노드가 실제 생성된 뒤 `get_node_infos`로 필드 핀 목록·인덱스를 확인하는 편이 안전).

### 확정 — `CaptureViewport`가 PIE 세션 중에도 에디터 원본(BeginPlay 미실행 상태)을 캡처하는 문제, §7의 "미해결 이월" 재현 확정(해법은 여전히 없음)
PIE 시작 후 `get_properties`로 PIE 인스턴스의 `Text`/위치가 BeginPlay 로직대로 정확히 세팅된 것을 확인한 직후 같은 좌표로 `CaptureViewport`를 호출했으나, 캡처된 이미지엔 `TextRenderComponent`의 **미수정 기본값("Text")**만 보였다(§7 미해결 이월과 동일 패턴, 이번엔 완전 재현 확정). §7이 제안한 우회("PIE 끄고 에디터 레벨 인스턴스에 동일 값을 직접 세팅 후 캡처")도 이번엔 `ObjectTools.set_properties`의 인라인 구조체 비결정성(§7 함정③)이 겹쳐 관련 필드(`relativeLocation`/`relativeRotation`)가 10회 재시도 후에도 첫 번째 필드(X/Pitch)만 반영되고 나머지가 반영되지 않아 그 우회조차 완결하지 못했다. **결론**: 이 조합(PIE 런타임 상태를 요구하는 시각 캡처)은 현재 이 MCP 툴셋으로 신뢰할 수 있는 방법이 없다 — **런타임 로직 정확성 검증은 `get_properties`로 PIE 인스턴스를 직접 재조회하는 것에 전적으로 의존**하고, 픽셀 단위 시각 확인이 꼭 필요하면 오너가 에디터에서 직접 PIE를 실행해 육안 확인하는 것이 유일하게 신뢰 가능한 경로다(§0 "스크린샷 생략, 오너가 엔진에서 확인" 메모리 원칙과 부합).

---

## 21. UmgMcp 서드파티 플러그인 도입 — 오너 UMG 배치 수동노동 해소 + PC 최초 C++ 빌드 확인 (2026-07-14)

> 배경: [[UI_화면_규약]] §B가 "4.위젯 배치 = 오너 수동"(§19 "확정 — WidgetBlueprint 내부 위젯트리는 MCP로 조작 불가" 근거)으로 확정해뒀던 것을, 오너 제안으로 서드파티 UMG MCP 플러그인을 조사·도입해 뒤집은 사건. 도입 과정에서 이 PC의 C++ 빌드 능력 자체가 막혀 있었다는 더 근본적인 문제도 함께 드러나 해결됐다 — 이 문서 통틀어 파급이 가장 큰 사건 중 하나.

### 사전 조사 — 공식 MCP는 UMG 미지원, 서드파티 후보 비교
이 프로젝트가 상시 쓰는 공식 Unreal MCP(`ModelContextProtocol`/`EditorToolset`)는 **기본 툴셋에 UMG/Widget 함수가 0개**이며, 커스텀 툴셋을 C++로 직접 확장하는 구조만 제공한다(§19 결론과 일치). UMG를 다루려면 처음부터 UMG 전용으로 설계된 서드파티 C++ 플러그인이 필요하다. 웹 교차확인으로 후보 비교:

| 후보 | 라이선스 | UMG 지원 | 채택 여부 |
|---|---|---|---|
| **winyunq/UnrealMotionGraphicsMCP (UmgMcp)** | MIT | ✅ UE5.8 전용·UMG 특화 | **채택** |
| UE-MCP | MIT | ✅ 있음 | 미검토(UmgMcp로 충분히 해소돼 추가 검토 불필요) |
| Ivan Murzak | — | ❌ 프리빌드지만 UMG 없음 | 제외 |
| chongdashu | — | ⚠ UMG 지원 불명확 | 제외 |

### 함정 ㉕ 이 PC에 `.NET Framework SDK`가 없어서 **모든** 신규 C++ 플러그인 빌드가 막혀 있었다 — UmgMcp 자체의 결함이 아니라 PC 환경의 선재 결함
UmgMcp를 클론해 `.uproject`에 등록하고 빌드를 트리거하자 `Result: Failed (RulesError)`로 실패했다. 처음엔 UmgMcp 소스 문제로 의심했으나, 로그의 실패 지점은 UmgMcp가 아니라 **엔진 코어 모듈 `SwarmInterface`**였다:
```
Unable to instantiate module 'SwarmInterface': Could not find NetFxSDK install dir;
Install a version of .NET Framework SDK at 4.6.0 or higher.
(referenced via ... UnrealEd.Build.cs)
```
**진단**: `SwarmInterface`는 UmgMcp와 무관한 언리얼 엔진 표준 모듈(분산 셰이더 컴파일용)이고, `UnrealEd`가 이를 참조하므로 **어떤 프로젝트 재빌드든 이 모듈을 거친다.** 즉 **이 PC는 애초에 C++ 소스 빌드 자체가 불가능한 상태**였다 — 지금까지 써온 공식 MCP 플러그인은 전부 **이미 빌드된 바이너리**로 동작했을 뿐, 이 PC에서 실제로 컴파일된 적이 없었다. 새 C++ 플러그인(UmgMcp) 추가가 프로젝트 전체 재빌드를 트리거하면서 이 잠재 결함이 처음 드러난 것 — **UmgMcp가 아니라 어떤 신규 C++ 플러그인이었어도 똑같이 막혔을 것이다.** UmgMcp는 무고.

**해결**: **관리자 권한** PowerShell에서
```
winget install Microsoft.DotNet.Framework.DeveloperPack_4
```
(일반 권한 PowerShell로 시도하면 `exit 1602`로 실패 — 반드시 관리자 권한 필요.) 설치되면 `C:\Program Files (x86)\Windows Kits\NETFXSDK\4.8.1`이 생성되고, 이후 UBT 빌드가 `Result: Succeeded`(59초, `UnrealEditor-UmgMcp.dll` 1.7MB)로 성공.

**파급**: 이 조치로 **이 PC가 처음으로 C++ 소스 빌드 가능 상태가 됐다.** [[projectTP_허브]] 결정 로그의 "MVP = Blueprint-only, C++(cpp-engineer)는 MVP 이후 코어 이관 시 활성화(VS2022 필요)" 조건 중 하나(빌드 환경 자체)가 여기서 해소됨 — **VS2022뿐 아니라 .NET Framework SDK도 필요조건이었다는 게 이번에 밝혀졌다.** cpp-engineer 활성화 시점에 이 항목을 별도로 재확인할 필요는 없다.

### 확정 — UmgMcp 설치 절차 (재현 가능하게 기록)
1. `git clone https://github.com/winyunq/UnrealMotionGraphicsMCP.git` → `D:\unreal\projectTP\Plugins\UmgMcp`.
2. `projectTP.uproject`의 `Plugins` 배열에 `UmgMcp`와 `EditorScriptingUtilities` 등록(자동 활성화).
3. `Resource\.mcp.json`에 서버 추가:
   ```json
   "UmgMcp": {
     "command": "uv",
     "args": ["run", "--directory", "D:\\unreal\\projectTP\\Plugins\\UmgMcp\\Resources\\Python", "UmgMcpServer.py"]
   }
   ```
4. Python 의존성은 별도 설치 불필요 — `uv run`이 최초 실행 시 자동 설치(65개 패키지, `.venv` 생성).
5. UBT로 C++ 빌드(함정㉕의 .NET SDK 선결조건 충족 후).
6. **에디터 재시작 → 그다음 Claude Code(MCP 클라이언트) 재시작.** 순서가 중요하다 — 에디터가 먼저 완전히 떠서 UmgMcp 서버가 자기 포트를 discovery registry에 공개해야, 나중에 뜨는 MCP 클라이언트가 그 포트를 찾아 연결할 수 있다(반대 순서면 연결 실패).

**롤백 절차(빌드 실패 시)**: `.uproject`의 `Plugins` 배열에서 `UmgMcp` 항목 제거 **+** `Plugins\UmgMcp` 폴더 자체를 `Plugins\` 밖으로 이동. **둘 다 해야 한다** — 폴더만 `Plugins\` 안에 남아 있으면 UE가 다음 실행 시 자동 재감지해 다시 빌드를 시도한다.

### 확정 — UmgMcp 사용 패턴 실측 (오너 수동 배치 0으로 확정)
표준 시퀀스: `set_target_umg_asset` → `create_widget`(계층 생성) → `set_widget_properties` → `query_widget_properties`(재조회 검증) → `save_asset`.

파일럿에서 `set_widget_properties({"bIsVariable": true})` 적용 후 `query_widget_properties`로 재조회해 `bIsVariable: true`를 확정했다 — **Is Variable 체크까지 MCP로 됨.** 즉 [[UI_화면_규약]] §B-1의 "4.위젯 배치 = 오너 수동, 애셋당 수 분"이 이제 **오너 노동 0**(육안 확인만)으로 대체 가능함을 실증했다.

**실측 발견 — 빈 WBP는 위젯 트리에 루트조차 없다**: gameplay-engineer가 `BlueprintTools`로 만들어둔 빈 WBP를 `get_widget_tree`로 조회하면 **빈 트리가 반환된다**(루트 위젯 자체가 없음 — §19가 실측한 `WBP_Probe`도 같은 상태였을 것으로 추정). **루트부터 `create_widget`으로 새로 만들어야 한다** — "빈 캔버스에 자식만 배치하면 된다"고 가정하면 첫 호출부터 어긋난다.

**위젯 타입명**: 표준 UMG 클래스명을 문자열 그대로 지정 — `Button`, `TextBlock`, `VerticalBox`, `Image`, `Border`, `Overlay`, `Spacer`, `HorizontalBox`.

### UmgMcp 도구 51종 개요
- **위젯 조작**: `set_target_umg_asset`·`set_target_widget`·`get_widget_tree`·`query_widget_properties`·`create_widget`·`set_widget_properties`·`reorder_widget_tree`·`reparent_widget`·`apply_layout`(HTML/JSON 일괄 적용)·`delete_widget`·`save_asset`·`get_layout_data`.
- **`bluecode_*`**(BP 배선 — apply/connect/compile/read_function/read_variables/apply_variables 등): [[UI_화면_규약]] §B-3이 "미검증"으로 남겨둔 5단계(배선) 자동화 가능성을 열지만, **이번 세션엔 미실증**(다음 UMG 제작 착수 시 최우선 검증 대상).
- **`animation_*`**, **`hlsl_*`**: 이번 세션엔 미사용, 존재만 확인.
- UmgMcp는 공식 MCP(포트 8000, HTTP)와 **별도 discovery registry**(stdio, `uv run`)를 쓰므로 두 서버가 충돌하지 않는다 — `Resource\.mcp.json`에 동시 등록해도 안전.

---

## 22. 전투완성 U단계(HP게이지 UMG 실장)에서 확정된 노하우 (2026-07-15)

> 배경: 3회 실패한 F3b(액터부착 월드공간 TextRenderComponent) 방식을 폐기하고 UMG WidgetComponent(Screen space)로 재구현해 F3(HP 게이지)를 완결한 세션. 상세 구현 기록은 [[U단계_HP게이지_UMG_실장]].

### 함정 ㉖ 레벨에 이미 배치된 액터 인스턴스의 컴포넌트 `RelativeLocation`은 MCP `set_properties`/`reset_properties`로 수정 불가 — CDO 세팅도 Construction Script도 안 먹히고 **BeginPlay만 유일하게 작동**
함정㉔(§20)이 `bAbsoluteLocation/Rotation/Scale` 세팅의 CDO→인스턴스 미전파를 확정했는데, 이번엔 더 근본적인 사례가 추가로 확인됐다: `HpGaugeWidget`(WidgetComponent)의 `RelativeLocation` 값 자체를 `ObjectTools.set_properties`/`reset_properties`로 레벨 인스턴스에 직접 세팅해도 **호출은 `true`를 반환하지만 실제 값은 전혀 바뀌지 않는다**(4회 재시도 전부 동일 결과로 실측 확인). CDO(`BP_BattleSpawnPoint_C:HpGaugeWidget_GEN_VARIABLE`) 자체는 정상적으로 수정되지만, 레벨에 이미 배치된 8개 인스턴스가 **개별 per-instance 오버라이드를 계속 붙들고 있어 CDO 값이 상속되지 않는다.** 한 걸음 더 나아가 Construction Script(`UserConstructionScript`)에 `SetRelativeLocation` 노드를 넣어 실행해도 실패했다 — 액터 재구성(construction) 순서상 **인스턴스 오버라이드가 Construction Script 실행 이후에 다시 한 번 덮어써지는 것으로 추정**된다. **해법**: **`BeginPlay`에서 `SetRelativeLocation`을 호출**하는 것이 유일하게 작동하는 경로다 — BeginPlay는 모든 재적용(construction·오버라이드 복원)이 끝난 뒤 실행되므로 그 무엇도 이 호출 결과를 덮어쓰지 못한다. PIE에서 8기 전원 값이 정상 반영됨을 실측 확인했다(아래 함정㉗ 값 기준).

### 함정 ㉗ WidgetComponent가 비균등 스케일+회전된 스프라이트 부모에 붙어있으면 로컬축이 화면 방향과 어긋나고, 좌우로 마주보게 회전된 두 그룹(아군/적군)엔 팀 공통 단일 오프셋이 성립하지 않는다
`HpGaugeWidget`의 부모가 HD-2D 스프라이트 컨벤션의 `Sprite`(루트, yaw 정렬됨 + 스케일 `(6.48, 2.59, 1)`인 비균등 스케일)라 §7 함정②·§18 함정㉒ 계열의 로컬축 예측불가 문제가 다시 나타났다 — 다만 이번엔 "완전 소실" 대신 **축 자체가 직관과 다르게 매핑**되는 형태였다. 실측 확정: **Z가 "위"가 아니고, Y가 화면 수직축(음수 방향이 위)이다.** 게다가 **아군/적군 스프라이트가 서로 마주보도록 반대로 회전돼 있어 로컬 X축의 부호가 팀마다 반전**된다 — 즉 "머리 위" 오프셋을 팀 공통 단일 벡터 하나로 표현하는 것이 원리적으로 불가능하고, `bIsParty`(또는 `bIsAlly`) 분기가 반드시 필요하다. **최종 확정값**(오너가 PIE에서 F8로 빙의 해제한 뒤 기즈모로 직접 맞춘 값을 Director가 MCP로 실측 채집): **아군 `(-7.716049, -34.722008, 0)` / 적군 `(+7.716049, -27.0, 0)`**(전부 `RelativeLocation`, 함정㉖의 BeginPlay 경로로 주입). 배선은 `수학|벡터|SelectVector` 노드로 `bIsParty` 분기해 두 리터럴 벡터 중 하나를 선택하는 방식. PIE 라이브 값 재조회로 8기 전원 검증 완료(아래 확정 항목의 PIE 월드 경로 조회 방식 사용).

### 확정 — PIE 실행 중에는 `save_assets`가 차단된다(조회는 정상 동작) — 저장은 PIE 종료 후에 할 것
U단계 작업 중 PIE를 띄운 채로 `save_assets`를 호출하면 **"Asset does not exist" 에러**가 반환됐다 — 같은 애셋에 대한 조회(`get_properties` 등)는 PIE 중에도 정상 동작하므로, 애셋이 실제로 없는 게 아니라 **저장 동작만 선택적으로 차단**되는 것으로 보인다(근본 메커니즘 미규명, PIE가 애셋 패키지를 점유해서로 추정). PIE를 종료하면 동일 호출이 즉시 정상 저장된다. **실무 규칙**: PIE 중 값을 바꿔 실측 확인한 뒤, 저장이 필요하면 반드시 PIE를 먼저 끝낼 것.

### 확정 — BeginPlay가 런타임에 바꾼 값을 확인하려면 에디터 월드 경로가 아니라 **PIE 월드 경로**로 조회해야 한다
에디터 월드 경로(예: `/Game/Stages/map_battle_octopath...`)에 대고 `get_properties`를 호출하면 **직렬화된(저장된) 초기값만** 돌아온다 — `BeginPlay`가 런타임에 계산해 바꾼 실제 값은 반영되지 않는다. PIE를 실행한 상태에서 **PIE 월드 경로**(같은 경로에 `UEDPIE_0_` 접두어가 붙은 형태, 예: `/Game/Stages/UEDPIE_0_map_battle_octopath...`)로 다시 조회해야 BeginPlay가 실제로 세팅한 런타임 값을 볼 수 있다. 함정㉖·㉗의 위치 확정 전 과정에서 이 구분을 놓치면 "BeginPlay 로직이 반영 안 됐다"는 오판을 하기 쉽다(사실은 조회 경로가 틀린 것).

### 함정 ㉘ UmgMcp `bluecode_apply`/`bluecode_connect`는 함수 파라미터 참조·위젯 액션 매칭에서 반복 실패한다 — `unreal-mcp` `BlueprintTools`의 저수준 노드 API로 대체할 것
U단계에서 `WBP_UnitFrame.SetHp`/`SetUnitInfo` 배선과 `BP_BattleSpawnPoint`의 Cast 재타깃을 `bluecode_apply`/`bluecode_connect`(§21이 "미실증"으로 남겨둔 배선 자동화)로 시도했으나 **반복적으로 실패**했다 — 함수 파라미터를 참조하려 하면 "No Blueprint action matched"류 에러가 나거나, 파라미터를 심볼릭 참조가 아니라 **리터럴 값으로 오파싱**하는 사례가 나왔다(예: 위젯 `SetText` 액션에 파라미터를 연결하려는 시도가 매칭 실패). **대체 경로**: §7~§20에서 이미 검증된 **`unreal-mcp`(공식 서버) `BlueprintTools`의 저수준 노드 API** — `create_node`/`connect_pins`/`set_pin_value`/`get_node_infos`/`delete_node`/`retarget_node_class` — 를 그대로 사용하면 전부 정상 작동했다. **핵심 요령**: 함수 파라미터는 이름 문자열로 매칭시키려 하지 말고, **`FunctionEntry` 노드가 노출하는 출력 핀에 `connect_pins`로 직접 연결**할 것 — 이 경로가 U단계 배선 전체(SetHp/SetUnitInfo/Cast 재타깃/SelectVector 분기)에서 예외 없이 성공했다.

---

## 23. 전투완성 S0~F4(DT 재임포트+ResolveHit 스캐폴드)에서 확정된 노하우 (2026-07-15)

> 배경: `DT_Skills` 상태이상 데이터 재반영(S0)부터 §8 판정 코어를 `ResolveHit` 함수로 구현하고(F4) 베기 검증 스캐폴드를 정리하던 중 신규 함정 5건이 발견된 세션. F4 자체는 디스크 저장까지 완료됐으나, 스캐폴드 정리 중 그래프 손상 사고(아래 함정㉜)가 나 에디터 재시작 대기 상태로 세션이 종료됐다 — 상세 경위는 [[F4_중단_인수인계]] 참고.

### 함정 ㉙ 이미 존재하는 DataTable은 `import_file` 단독 호출로도 덮어쓰기가 안 된다 — 기존 F2 노하우는 "신규 생성" 케이스 한정이었다
전투완성 plan.md §2-3이 F2 시점에 확정해둔 "`DataTableTools.create()` 병용 금지, `import_file()` 단독 호출이 정답"은 **DT가 아직 없는 신규 생성 케이스에서만 유효한 결론**이었다.

**실측(S0)**: F2에서 이미 만들어둔 `DT_Skills`에 상태이상 데이터(EffectChance 등)를 반영하려고 같은 경로로 `import_file`을 호출하면 **`"DT_Skills at /Game/Data already exists"` 에러**가 즉시 난다. `create()`+`import_file()` 병용 실패(§F2)와 표면 증상은 같지만 트리거가 다르다 — 이번엔 `import_file` 하나만 불러도, **MCP 래퍼 자체에 "대상이 이미 존재하면 거부"하는 명시적 존재-체크 가드가 박혀 있어** 막힌다.

**해결(실증됨)**: `get_referencers`로 해당 DT를 참조하는 애셋이 0건임을 먼저 확인 → `AssetTools.delete(경로)`로 삭제 → `DataTableTools.import_file()` 재호출(이제 신규 생성 경로와 동일해짐). S0 시점 `DT_Skills`는 참조 0건이라 이 절차가 안전했다.

**부작용 주의**: delete-recreate 경로를 타면 **애셋 GUID가 새로 발급된다.** 참조가 있는 DT에 같은 절차를 쓰면 그 하드참조가 끊길 위험이 있다 — 실제로 F4_TC.md가 "같은 절차를 `DT_JobStats`에 적용하면 즉시 파국(`BP_BattleSpawnPoint.BeginPlay`가 하드참조 중이라 끊기면 8기 즉사)"이라고 별도로 못박은 이유가 이것이다. **기존 DT를 갱신해야 할 땐 먼저 `get_referencers`로 위험도를 가늠할 것** — 참조가 있으면 delete-recreate 대신 행 단위 갱신이나 오너 수동 편집을 검토한다.

### 함정 ㉚ `K2Node_GetDataTableRow`(BP 팔레트의 "Get Data Table Row")를 `create_node`로 생성할 수 없는 사례 확인 — §20의 성공 사례와 표면적으로 상충, 그래프 종류 차이가 원인일 가능성(미확정)
**증상(F4)**: `ResolveHit`(§8 판정 함수, **Function Graph**) 안에서 `DT_Skills`를 SkillId로 조회하려고 RowName 기반 typed 단일행 조회 노드를 `create_node`로 만들려 했으나, 시도한 어떤 type_id 문자열도 전부 실패했다(다수 방법 시도 후 확정).

**§20과의 관계(주의해서 읽을 것)**: 이 문서 §20("전투완성 F3에서 확정된 노하우")은 정확히 같은 계열 노드(`Utilities|데이터테이블행가져오기`, exec 출력이 `then`/`RowNotFound` 2개)를 `create_node`로 **성공적으로 생성**했다고 이미 기록하고 있다 — 다만 그건 `DT_JobStats`를 `BeginPlay`(**EventGraph**) 컨텍스트에서 조회하는 용도였다. 이번 실패는 `DT_Skills`를 **Function Graph** 컨텍스트에서 조회하려던 시도다. **그래프 종류(EventGraph vs Function Graph) 차이가 성패를 가른 원인일 가능성이 있으나, 이번 세션에서 §20의 성공 문자열을 Function Graph에서 재시도해 이 가설을 확정 검증하지는 않았다**(후속 조사 과제로 이월). **"이 노드는 MCP로 무조건 생성 불가"로 일반화하지 말 것** — 다음에 필요해지면 먼저 §20의 정확한 성공 문자열부터 그래프 종류를 바꿔가며 재시도해볼 가치가 있다.

**회피(F4에서 채택, 실동작 확인)**: `GetDataTableRowNames`(전체 RowName 배열) + `Utilities|Array|FindItem`(대상 RowName의 인덱스 획득) + `GetDataTableColumnAsString`(컬럼별 문자열 추출) × N회 + `StringToInt`/`StringToFloat`(타입 변환) 조합으로 동등한 조회를 구현했다. 기능은 동일하나 **그래프가 컬럼 수만큼 선형으로 커진다.**

**파급**: F7(스킬 4종 확장)에서도 스킬 데이터 조회가 반복된다 — 착수 전에 이 우회를 그대로 재사용할지, §20 방식 재시도부터 할지 미리 정해둘 것.

### 함정 ㉛ `Format Text`에 리터럴 포맷 문자열을 세팅하면 인자 핀이 자동 생성된다 — 이미 자동생성된 상태에서 `add_node_pin`을 추가로 부르면 orphan(고아) 핀이 생긴다
**증상(F4)**: `ResolveHit`의 전투로그 조립용 `Format Text` 노드에 `set_pin_value`로 `{0}/{1}/{2}...`가 포함된 포맷 문자열을 세팅하면 **UE가 그 즉시 인자 핀을 자동 생성**한다(§15가 이미 확인한 "FormatText는 `add_node_pin`을 지원한다"는 사실 자체는 그대로 유효하다). 이걸 모르고 그 뒤에 **`add_node_pin`을 추가로 호출**하면, 이미 생성된 인덱스 핀과 별개로 **중복된 orphan 핀**이 생긴다.

**결과**: 컴파일은 에러 없이 통과한다(orphan 핀은 조용히 무시됨) — 그런데 **런타임에 로그 라인의 여러 필드가 공백으로 찍힌다**(실제 배선이 orphan 핀 쪽으로 가 있어서). 1차 PIE 실행에서 실측 발견되어 4개소를 수정했다.

**교훈**: `Format Text`에 리터럴 포맷 문자열을 세팅할 계획이면 **문자열만 먼저 세팅하고 `get_node_infos`로 자동생성된 인자 핀을 재조회해 거기에 배선**할 것 — **`add_node_pin`을 별도로 부르지 마라.**

**연관(리터럴 vs 동적 — 혼동 금지)**: [[언리얼5.8_기술카탈로그]] §1-3의 UE 공식 문서 조사에서 대칭 함정이 확인됐다 — **포맷 핀이 다른 노드에 "연결"(동적)돼 있으면 반대로 인자 핀이 자동 생성되지 않고, Details 패널에서 수동 선언해야 한다.** F7의 스킬 설명(`DescKey`가 DataTable에서 런타임에 오는 동적 포맷)이 정확히 이 케이스다. **리터럴 포맷 = 인자 핀 자동 생성(`add_node_pin` 추가 금지) / 동적 포맷(핀 연결) = 인자 핀 수동 선언 필요(Details 패널)** — 두 경우를 반드시 구분할 것.

### 함정 ㉜ ★`delete_node`가 노드를 지우지 않고 그래프 전역의 핀 연결만 파괴하는 부작용 — 이 문서에 기록된 사고 중 가장 파괴적
**증상(F4, 이번 세션 최대 사고)**: 베기 검증 스캐폴드를 정리하던 중 존재를 확인하지 않고 추측한 refPath로 `delete_node`를 호출했다. 그 노드는 삭제되지 않았고, 대신 **그래프 전역에서 exec/데이터 연결이 다발적으로 끊기는 부작용**이 났다 — 재조회로 확인된 것만 **11곳 단선**: `SetbInputLocked→PrintString→ForEachLoop`, `HighlightOff`, `ForEachLoop.Completed→PlayAttack→Sequence` 등, 스캐폴드와 무관한 기존 정상 배선까지 광범위하게 끊어졌다.

**2차 피해**: 끊어진 연결을 `connect_pins`로 재배선하려 했으나 **`Internal compiler error inside CreateExecutionSchedule (site 2)`**로 컴파일 자체가 되지 않았다 — 그래프 구조 자체가 통상적 재배선으로는 복구 불가능한 수준까지 손상됐다.

**대응(올바르게 수행됨)**: 손상을 인지한 즉시 **저장하지 않고 작업을 중단·보고**했다 — 이 판단 덕분에 디스크상의 F4 완료본은 무사했다.

**★예방 규칙(반드시 지킬 것)**:
1. `delete_node` 호출 전 **반드시 `find_nodes`/`get_node_infos`로 그 refPath가 실재하는지 먼저 확인**한다 — 노드 번호(인덱스)를 추측해서 넣지 않는다.
2. 스캐폴드(임시 검증용 노드)는 **생성 직후 그 refPath를 별도로 기록**해두고, 정리할 때는 그 기록만 근거로 삭제한다 — §15가 이미 "삽입 시점에 원래 대상 refPath를 보존"을 권장했는데, 그 습관을 스캐폴드 자신의 refPath에도 적용하지 않았을 때 실제로 벌어지는 최악의 결과가 이번 사고다.
3. 큰 그래프(수십~백여 노드)를 수술하기 전엔 **BP 애셋(.uasset)을 파일 복사로 미리 백업**한다 — `Content/`는 `.gitignore` 대상이라 git으로는 복구되지 않는다(§18 함정㉑에서 이미 확인된 사실과 같은 선상).

**복구법**: 저장 전이라면 **에디터 재시작**으로 디스크 버전이 복원된다(메모리상의 손상만 버려진다). 그러나 `AssetTools`에 애셋을 디스크에서 강제로 재로드하는 API는 **없다** — `load_asset`은 이미 메모리에 있는 캐시를 반환할 뿐 디스크와 재동기화하지 않는다. 즉 **"저장하기 전에 손상을 알아채는 것"이 유일한 방어선**이며, 한 번 저장하면 손상이 디스크로 그대로 번져 복구 수단이 없다.

### 함정 ㉝ MCP 툴은 게임 스레드에서 직렬 실행된다(병렬 호출 불가) — §8 함정⑤가 버그가 아니라 문서화된 설계 제약이었음이 확인됨
공식 Unreal MCP 플러그인 문서(5.8 Experimental)에 **"calls run serially on the game thread (no overlapping tool calls)"**가 명시돼 있다 — MCP 툴 호출은 게임 스레드에서 **직렬로만** 실행되고 겹쳐 부를 수 없다.

**소급 확인**: §8 함정⑤(`add_event`를 병렬 호출하면 `event_name`이 무시되고 기본 이름 `커스텀이벤트`로 생성되는 현상)를 당시엔 원인 미규명의 "버그"로 기록해뒀는데, 이번에 공식 문서와 대조해보니 **버그가 아니라 문서화된 설계 제약**이었음이 확인됐다. §19가 보고한 "특정 `asset_type`으로 `BlueprintTools.create`를 병렬 호출했을 때 공유 MCP 브릿지 전체가 마비된 사고"도, 여러 클라이언트가 같은 직렬 큐를 공유하는 이 구조 위에서 벌어진 일로 재해석할 수 있다.

**규칙**: MCP 툴, 특히 **그래프·애셋을 바꾸는 쓰기 계열 호출은 항상 순차(1개씩) 호출**한다. "독립적인 일은 한 메시지에서 여러 에이전트 병렬 호출"이라는 워크플로우 원칙은 **에이전트 레벨의 병렬성**이지, 그 에이전트들이 **같은 unreal-mcp 세션으로 보내는 개별 툴 호출**에는 적용되지 않는다 — 같은 UE 에디터를 공유하는 여러 에이전트를 한 메시지로 병렬 launch하지 말라는 §19의 규칙이 이 제약의 직접적인 귀결이다.

**출처**: [[언리얼5.8_기술카탈로그]] §1-4.

---

## 24. 전투완성 F4 실플레이 디버깅에서 확정된 노하우 (2026-07-15)

> 배경: §23(`delete_node` 그래프 손상 사고)으로 중단됐던 세션의 후속. 에디터 재시작으로 복구한 뒤 오전 내내 F4(데미지 계산) 실플레이(PIE 실클릭)를 디버깅하며 발견한 함정 5건 — 그중 하나(㉞)는 이 문서 통틀어 가장 은닉성이 높은 버그였다. 상세 경위는 [[F4_중단_인수인계]] "오늘 오전(2026-07-15) 복구·디버깅 경과" 참고.

### 함정 ㉞ — pure 노드 이중 계산 (★오늘 최악의 버그)
**증상**: 데미지 계산에서 `dmg=30`(스캐폴드 단발 호출)은 맞는데, 실제 게임에서 여러 번 때리니 Hp>0인 유닛이 사망 처리됨(예: hp=48인데 죽음).

**원인**: `Max(0, Hp − Dmg)` 계산 노드가 **pure 노드(실행핀 없음)**라서, 이 출력을 읽는 곳마다 **매번 독립적으로 재평가**된다. 세 소비처(①Hp 변수 저장 ②위젯 SetHp ③사망판정 `<=0` 비교)가 각각 Max 체인을 다시 굴리는데, 실행 순서상 ①이 Hp를 이미 갱신한 뒤 ③의 `GetHp`가 **갱신된 새 Hp를 재조회해 Dmg를 또 뺐다**(이중차감). 예: 90−42=48 저장 → 판정 시 48−42=6 → 상황 따라 0 이하로 오판.

**왜 스캐폴드 검증을 통과했나**: 첫 타격(단발)은 이중차감 결과가 우연히 0 초과라 살아남는다. **여러 번 누적 타격해야 드러나는 버그**라 함수 단발 호출로는 절대 안 잡힌다.

**해결**: 사망판정·위젯 SetHp의 입력을 pure Max 재계산이 아니라 **이미 저장된 멤버 변수**(`GetHp`, 실행 순서상 SetHp 이후)로 연결. 핀 2개 재배선.

**일반 교훈**: pure 노드 출력을 "값이 확정된 후 여러 곳에서 읽어야 하는" 계산에 직결하지 마라. **멤버/로컬 변수에 한 번 저장(impure Set)한 뒤 그 변수를 읽어라.** BP의 pure 노드는 "매 읽기마다 재실행"이 기본 동작이다.

### 함정 ㉟ — `delete_node`가 노드 여러 개와 연결 다수를 파괴 (§23 ㉜의 실제 피해 규모)
**증상**: 어젯밤 잘못된 refPath `delete_node` 한 번(§23 함정㉜)이 `EnterExecuting` 그래프에서 **최소 6곳의 exec 연결을 끊고 `PlayAttack` 노드 자체를 삭제**했다. 각 단선이 **서로 다른 조건에서만** 드러나 순차적으로 발견됨:
- `bInputLocked → 하이라이트 ForEachLoop` 단선 → 클릭해도 무반응(항상)
- `Align 루프 → PlayAttack` 단선 + `PlayAttack` 노드 삭제 → 카메라 ON 공격이 카메라컷에서 멈춤
- `bCamActionEnabled Branch`의 else(카메라 OFF) 단선 → **카메라 끄면** 공격이 WalkArrive에서 멈춤
- IsValid 노드 5개의 "Is Not Valid" 출구 미연결(정상 플레이엔 잠복)

**원인**: §23 함정㉜과 동일 — `delete_node`가 노드를 지우지 않고 그래프 전역 핀 연결을 파괴하는 부작용. 그때는 "11곳 단선"까지만 실측했고, 오늘 그중 실제로 플레이에 영향을 준 지점을 조건별로 순차 확인했다.

**해결**: 6곳 재연결 + `PlayAttack` 노드 재생성으로 오늘 오전 복구 완료([[F4_중단_인수인계]] 경과 참고).

**교훈**: 그래프 손상은 "한 곳"이 아니라 **여러 곳에 흩어져 각기 다른 조건에서 발현**한다. 하나 고칠 때마다 "복구 완료"라 하지 말고, **손상 의심 시 전 그래프의 미연결 exec 핀을 먼저 전수 조사**(`get_connected_subgraph`로 도달 가능 노드 덤프 후 `connected_pins:[]` 스캔)하라. Director가 "복구 완료"를 3번 성급히 선언했다가 매번 새 단선이 나온 게 이번 교훈.

### 함정 ㊱ — PIE 실행 중 `compile_blueprint`는 무시된다
**증상**: PIE 켜진 채로 핀을 재배선하고 `compile_blueprint`(성공 반환)+`save_assets`(PIE라 "Asset does not exist" 실패)한 뒤, PIE 끄고 다시 `save`(성공)했다. 그런데 오너 재테스트에서 수정이 **반영 안 됨**.

**원인**: PIE 중 컴파일은 반영되지 않는다(에디터가 PIE 월드를 물고 있음). StopPIE 후 **재컴파일을 다시 하지 않으면** 저장된 .uasset이 컴파일 안 된 그래프 상태로 남는다. §22가 확인한 "PIE 중 `save_assets` 차단"이 저장 쪽 증상이라면, 이건 그 **컴파일 쪽 대응 함정**이다 — 저장 차단은 에러로 드러나기라도 하지만, 컴파일 무시는 에러 없이 조용히 무효화된다는 점이 더 위험하다.

**해결(순서 고정)**: 그래프 수정 → **`StopPIE` 먼저** → `compile_blueprint` → `save_assets` → `is_dirty=false` 확인. PIE 중이면 컴파일·저장 둘 다 신뢰하지 마라.

### 함정 ㊲ — 스캐폴드 함수 호출 ≠ 실제 플레이 경로 (검증 방법론)
**증상**: gameplay-engineer가 "스캐폴드로 ResolveHit 직접 호출 → dmg=30 확인, 완료"라 보고했으나, 실제 게임은 (a)클릭→Executing 경로가 끊겨 있었고(함정㉟) (b)이중차감 버그(함정㉞)가 있었다. 둘 다 스캐폴드 단발 호출로는 안 잡혔다.

**원인**: 스캐폴드는 함수를 **격리 호출**하므로 ①그 함수에 도달하는 exec 경로(클릭→AwaitTarget→Executing→PlayAttack→ResolveHit)를 건너뛰고 ②누적 상태(여러 턴 반복)를 재현하지 않는다.

**교훈/해법**: **화면 변화가 있는 기능의 게이트 검증은 반드시 PIE 실클릭 경로로.** 스캐폴드 결과를 "통과"로 인정하지 마라(설계에도 명시돼 있던 원칙인데 Director가 어겼다). Director는 각 F단계 게이트에서 오너 실클릭 또는 자동 클릭 스캐폴드로 **전체 경로**를 태워야 한다.

### 함정 ㊳(참고, 버그 아님) — 사망 처리는 F5 몫, F4에선 죽어도 턴이 돈다
**증상처럼 보였던 것**: F4 완료 시점엔 사망 **판정**(`bAlive=false` 세팅)만 있고, "죽은 유닛 턴 스킵(TS1)"·"죽은 유닛 타겟 제외"·"DYING 모션"은 **F5에서 구현**한다. 그래서 F4 단계 실플레이에서 hp=0 유닛이 턴을 받아 공격하고 계속 타겟되는 현상이 나타난다.

**판정**: 이건 버그가 아니라 **설계상 예상된 상태**다. 로그의 `effectRoll=-1`(사망으로 상태이상 롤 생략)이 사망 판정 자체는 정상 작동하고 있다는 증거다.

**해법**: F5 착수 시 해소되는 이월 항목이다 — 새 버그로 재조사하지 말 것.

---

## 25. 전투완성 F5-1(사망·승패) 게이트에서 확정된 노하우 (2026-07-15)

> 배경: F5-1(사망·승패 판정) 게이트 검증 중 "데미지가 전투 일정 이상 지나면 안 들어감"이라는 증상을 추적하다 발견한 함정 2건. 두 함정은 서로 독립적으로 존재하지 않고, **겹쳐야만** 매 세션 결정론적으로(정확히 turn=8) 재현됐다. 상세 경위는 [[F5-1_완료]] §4 참고.

### 함정 ㊴ — 검증용 디버그 값(SkillId 리터럴 핀) 원복 절차 누락 → 다음날 라이브 공격이 통째로 다른 스킬로 고정됨
**증상**: F5-1 실플레이 디버깅 중 "데미지가 전투 일정 이상 지나면 안 들어감"이라는 모호한 증상 발견. 걸음·모션은 정상 재생되지만 BattleLog 라인도 HP 변화도 없이, 매 세션 정확히 같은 시점에서 데미지가 멈췄다.

**원인**: 하루 전 F4 베기 검증(§24 배경, TC-F4-03) 때 `ResolveHit` 호출 노드의 `SkillId` 리터럴 핀을 `31000000`(기본공격)→`31001000`(베기)로 바꿔 검증했다([[F4_중단_인수인계]] §4의 정식 절차). 검증 자체는 통과(dmg=42, PASS — [[F4_중단_인수인계]] "베기 검증" 절)했으나, **그 직후 `31000000`으로 원복하는 절차가 다음날 아침 에디터 복구 작업 중 실행 누락**됐다 — 인수인계 문서엔 원복 단계가 절차의 일부로 명시돼 있었지만, 실제 그래프에는 반영되지 않은 채로 세션이 이어졌다. 그 결과 라이브 공격이 (F7 스킬 UI가 아직 없어 Attack 버튼 1개뿐인 상태에서) 베기로 고정돼 전원이 쿨다운 1턴짜리 스킬을 매 턴 사용하는 셈이 됐다.

**해결**: `ResolveHit` 호출 노드의 `SkillId` 핀을 `31001000`→`31000000`로 재원복. 컴파일 0에러, 저장 완료. 계획상 F4~F5 단계의 라이브 공격은 기본공격(쿨다운 0)이 정상이고, 베기 등 쿨다운 있는 스킬은 F7(스킬메뉴)이 쿨다운 감소 로직과 함께 결선해야 안전하다.

**교훈**: 검증용으로 바꾼 디버그 값(리터럴 핀·임시 변수 등)은 **검증 통과 직후 즉시 원복**하고, 원복을 "인수인계 문서에 적어두는 할 일"이 아니라 **그 자리에서 실행까지 끝내는 체크리스트 항목**으로 다뤄야 한다. 문서에 "원복 예정"이라고만 적어두면 다음 세션 담당자가 "이미 됐겠지"라고 오독하거나 실행을 빠뜨려도 문서만 봐서는 눈치채기 어렵다 — 이번 사고가 정확히 그 패턴이었다.

### 함정 ㊵ — 쿨다운 가드는 있는데 감소 로직이 없는 반쪽 구현이 결정론적 지뢰가 됨 (함정㊴와 결합해 라운드2에서 전원 정지)
**증상**: 함정㊴만으로는 "베기가 쿨다운 1턴짜리로 고정됐다"는 사실만 설명된다. 실제 증상은 한 술 더 떠 **라운드1(턴1~8)은 정상 작동하고 라운드2(턴9~)부터 전원 데미지가 0으로 멈추는 결정론적 패턴**이었다 — 매 PIE 세션이 정확히 `turn=8`(8유닛 한 바퀴 직후)에서 똑같이 멈췄다.

**원인**: `ResolveHit`의 §8 판정 스켈레톤 진입 첫 노드(step0)는 `GetSkillCooldown(Attacker, SkillId) > 0`이면 데미지 계산 전 조기 return하는 **쿨다운 가드**다([[plan]] §F4 4-2 step0, [[F4_중단_인수인계]] §3 `ResolveHit` 함수 목록). 이 가드는 F4에서 이미 구현됐지만, 그 가드가 전제하는 **쿨다운 감소(매 턴 −1 스윕)는 F5의 TS3로 예정만 돼 있을 뿐 아직 구현되지 않은 상태**였다([[F5_TC]] BLOCKER-4가 F5 착수 전 바로 이 공백을 지적한 항목). 즉 "가드는 있고 소비(감소)는 없는" 반쪽짜리 기능이 라이브 데이터 위에 얹혀 있었다. 함정㊴로 전원이 베기(쿨다운1)를 매 턴 사용하는 상태였으므로, 라운드1에 8유닛 전원이 쿨다운=1을 세팅하고 그게 영원히 안 풀려 라운드2부터 전원이 가드에 걸려 데미지·로그 없이 걸음만 반복했다.

**진단법(교훈)**: "전투 일정 이상 지나면 안 들어감"이라는 모호한 증상을 BattleLog와 대조해보니 매번 정확히 `turn=8`에서 멈추는 **결정론적 패턴**을 발견 → 유닛 수(8)와 일치 → 라운드 경계를 의심 → BP 그래프를 `find_nodes`/`get_node_infos`로 직접 추적(**PIE 실행 중엔 `read_graph_dsl`이 빈 값을 반환**하므로 이 상황에서는 노드 단위 조회가 유일한 경로)해 `ResolveHit` step0의 쿨다운 가드를 근본원인으로 특정했다.

**해결**: 함정㊴의 SkillId 원복으로 기본공격(쿨다운 0)이 라이브 경로가 되면서 이 가드에 걸리지 않게 됐다 — 쿨다운 감소 로직(TS3) 자체는 여전히 F5의 정식 구현 대상으로 남아 있다([[F5_착수지시서]] B4).

**일반 교훈**: "가드(차단 조건)는 넣었는데 그 가드를 해제하는 소비/감소 로직은 아직 안 넣은" 반쪽 구현은 **결정론적 지뢰**다 — 조건이 맞아떨어지는 순간 100% 재현되고, 게다가 유닛 수·라운드 경계처럼 겉보기엔 무관해 보이는 수치와 맞아떨어져 원인 추적을 어렵게 만든다. 회피책 둘: (a) 가드와 소비 로직을 **한 세트로만** 커밋한다(반쪽만 먼저 넣지 않는다), 또는 (b) 부득이 반쪽만 먼저 넣어야 한다면 **그 가드를 트리거하는 데이터(쿨다운>0인 스킬)를 라이브 경로에서 완전히 격리**한다(이번 사고는 정확히 이 격리가 깨지면서 터졌다).

---

## 26. 전투완성 F5-2(죽은 유닛 처리) 배선에서 확정된 노하우 (2026-07-15)

> 배경: F5-2(턴스킵·DYING·ClickBox·ResetForBattle) 3청크를 BP로 배선하며 발견한 MCP 그래프 편집 함정 2건. 둘 다 "MCP가 보여주는 표기와 실제 편집 대상이 어긋나는" 계열(§L130 엔진 자동네이밍과 같은 선상)이다. 상세 경위는 [[F5-2_완료]] 참고.

### 함정 ㊶ — `EnterTurnEnd` "함수" 그래프는 컴파일 스텁(프록시)일 뿐, 실제 로직은 EventGraph의 CustomEvent에 있다
**증상(F5-2)**: `EnterTurnEnd`의 TE 파이프라인(δ틱·`Branch(bBattleOver)` 등)을 수정하려고 `list_graphs`/`find_nodes`로 `BP_BattleManager:EnterTurnEnd` 그래프를 열었더니 **`FunctionEntry → ExecuteUbergraph` 두 노드뿐**이었다 — 편집하려던 실제 로직(MarkerOff·Delay·CurrentIndex 증가 등)이 그 그래프에 없다.

**원인**: `EnterTurnEnd`는 이름은 "함수"처럼 보이지만 **Delay(latent)를 보유**해야 하므로(Function Graph는 latent 불가 — §7 함정④/⑨) 실제로는 **EventGraph의 CustomEvent로 구현**돼 있다. MCP가 `:EnterTurnEnd`라는 이름으로 노출하는 그래프는 그 CustomEvent를 호출하는 **컴파일 스텁(프록시)** — FunctionEntry에서 곧장 ExecuteUbergraph로 넘기는 껍데기다. 진짜 편집 대상은 EventGraph 안에 있는 동명 CustomEvent 노드와 거기서 뻗어나가는 체인이다.

**회피(실동작 확인)**: `EnterTurnEnd`(및 같은 이유로 CustomEvent로 구현됐을 법한 다른 "함수" — Delay/RetriggerableDelay를 쓰는 것들)를 수정할 때는 **`:함수명` 그래프가 아니라 EventGraph를 열어 동명 CustomEvent를 찾아라.** `:함수명` 그래프에 FunctionEntry→ExecuteUbergraph만 있으면 그건 스텁이라는 신호다. F5-2에서 이 구분을 놓쳐 처음엔 "EnterTurnEnd에 로직이 없다"고 오판할 뻔했다.

### 함정 ㊷ — bool 변수의 Get/Set 노드는 노드 검색 시 "b" 접두어가 탈락한다(`bAlive` → `GetAlive`)
**증상(F5-2)**: 유닛의 `bAlive`(bool) 게터 노드를 `create_node`/`find_node_types`로 만들거나 찾으려고 검색어를 `GetbAlive`(= `get_node_infos`가 표기하는 이름 그대로)로 넣으면 **매칭 실패**한다.

**원인**: 언리얼의 bool 변수는 노드 팔레트/네이밍 계층에서 **헝가리안 "b" 접두어가 벗겨진 형태**로 노출된다 — `bAlive`의 게터는 검색상 **`GetAlive`**, 세터는 **`SetAlive`**로 잡아야 한다. 그런데 정작 `get_node_infos`가 생성된 노드를 **재조회**할 때의 표시 이름은 `GetbAlive`(접두어 유지)라, **생성 시 검색어와 조회 시 표기가 서로 다르다.** 이 불일치가 §L130(`SetScalarParameterValue`의 `declaring_class` 미명시 무음 실패)과 같은 "MCP 표기 ≠ 실제 매칭 키" 계열 함정이다.

**회피**: bool 변수 노드를 `create_node`/`find_node_types`로 다룰 때는 **"b" 접두어를 뗀 이름**(`GetAlive`/`SetAlive`/`GetbBlockActive`→`GetBlockActive` 등)으로 검색하라. 조회 결과가 `Getb…`로 돌아와도 당황하지 말 것 — 같은 노드다. 검색이 안 되면 접두어 유무를 먼저 바꿔보는 것이 1순위 진단이다.

---

## 27. 걸어나오기연출 공중부양 수정(사선무대 접지)에서 확정된 노하우 (2026-07-15)

> 배경: 유닛이 공격 위치로 걸어갈 때 바닥에서 뜨는 버그를 진단·수정하며 확정한 함정 2건. 하나는 접지용 라인트레이스 구현 함정, 다른 하나는 검증 판정 설계의 함정이다. 상세 경위·수치는 [[공중부양_수정]] 참고.

### 함정 ㊸ — 접지용 아래방향 라인트레이스는 유닛 콜리전을 반드시 무시해야 한다(안 그러면 자기/이웃을 "바닥"으로 오인)
**증상/위험(공중부양fix)**: 도착 지점의 바닥 높이를 구하려고 아래 방향으로 라인트레이스를 쏘면, 유닛 자신의 `ClickBox`(Visibility=Block, extent Z±125)나 `Sprite`(BlockAllDynamic)·또는 이웃 유닛의 콜리전이 트레이스 채널을 먼저 막아 **그 콜리전 표면을 "바닥"으로 오인**한다. 그 결과 계산된 발오프셋의 **부호가 반전(−127류)**되어, 접지시키려던 유닛이 오히려 땅에 매몰되는 정반대 결과가 나온다.

**회피(실동작 확인)**:
1. 트레이스에 **`bIgnoreSelf=true`** + **`ActorsToIgnore=전 유닛(TurnQueue)`** 를 반드시 지정 — 자기와 다른 모든 유닛의 콜리전을 배제하고 순수 무대 지오메트리만 맞힌다.
2. 트레이스 범위는 **홈 Z 상대가 아니라 고정 절대값(최저 바닥을 감싸는 브래킷, 예: 상단 2000 / 하단 −1000)** 으로 준다 — 홈 Z 기준 상대 범위로 주면 사선 무대에서 낮은 바닥이 범위 밖으로 빠져 미스가 난다.
3. 미스(트레이스 실패) 시엔 폴백값 + 로그를 남겨 무음 실패를 막는다.

이 프로젝트의 접지 로직(홈에서 `footOffset = homeZ − 홈바닥트레이스Z` 캐시 → 도착지에서 `destGroundZ + footOffset`)은 홈·도착 **두 트레이스 모두** 위 규칙을 지켜야 성립한다.

### 함정 ㊹ — "대입문을 그 대입식으로 재검하는 판정"은 가짜 GREEN(항상 참) — 독립 지상진실로 판정하라
**증상(공중부양fix)**: 수정 검증에서 "도착 Z가 올바른가?"를 `destZ == groundZ + offset`으로 판정하려 했는데, 이 식은 **코드가 방금 그 공식으로 계산해 대입한 값**을 **똑같은 공식으로 다시 확인**하는 것이라 **수정이 깨져 있어도 항상 참**이 된다(트레이스가 엉뚱한 값을 물어와도, groundZ와 destZ가 함께 틀린 채로 등식은 성립). 테스트는 GREEN인데 화면에선 여전히 떠 있는 전형적 위양성.

**회피(실동작 확인)**: 판정 기준을 **BP 내부가 계산한 값이 아니라, 완전히 독립적인 지상진실**로 삼아라. 이번엔 BP의 접지 트레이스와 **별개로** `trace_world`(독립 트레이스)를 직접 쏴서 groundZ를 재취득하고, 둘이 소수점 3자리까지 일치하는지로 판정했다(파티 487.708 / 적 501.066 일치 확인). 추가로 실제 효과(destZ 633.453→591.267, 42cm 하강)와 **오너 육안**(발이 바닥에 닿음)까지 교차 확인.

**일반 교훈**: 검증식에 **피검증 코드가 쓴 것과 같은 변수·같은 공식**이 등장하면 그 판정은 대개 항등식이다. "이 판정은 수정이 틀렸을 때 실제로 FAIL이 날 수 있는가?"를 먼저 자문하라 — FAIL이 원리적으로 불가능하면 그건 테스트가 아니다. 지상진실은 반드시 **독립 경로**(별도 트레이스·별도 측정·육안)에서 와야 한다.

**연관**: [[F5_TC]] BLOCKER 계열이 지적한 "항상참 판정 금지"와 같은 원리 — 데이터 흐름이 순환하는 판정(계산→대입→같은 식으로 재검)은 검증력이 0이다.

---

## 28. 전투완성 야간③(데미지폰트)·F7 스킬아키텍처 조사에서 확정된 노하우 (2026-07-16)

> 배경: 야간③(피격 데미지 플로팅 텍스트, [[야간③_데미지폰트_완료]]) 구현 중 발견한 UMG 애니메이션·데스크톱 자동화·스크린샷 캡처·로그 스캔·그래프 조회 함정 6건과, F7 스킬 아키텍처 F7b 착수 전 조사로 지정된 함정 3건([[F7_스킬아키텍처_확정]] §8-12 "노하우 이관 대기")을 합쳐 총 9건을 확정한 세션. **유니코드 원문자 숫자가 ㊿(50)에서 소진**되어, 마지막 3건(51~53)은 괄호숫자로 표기한다.

### 함정 ㊺ — UMG 애니메이션 `animation_append_time_slice`를 같은 시간대에 재호출하면 덮어쓰기가 아니라 키 중복 생성
**증상**: 이미 키가 있는 시간 지점에 `animation_append_time_slice`를 다시 호출해 값을 바꾸려 했더니, 기존 키가 교체되지 않고 **같은 시간에 키가 중복 생성**됐다.
**해법**: `animation_delete_widget_keys`로 해당 시간대 키를 먼저 지운 뒤 재작성한다 — "append"라는 이름과 달리 이 툴은 덮어쓰기를 지원하지 않는다.

### 함정 ㊻ — UMG 애니메이션 에셋의 보고된 길이가 실제 키 범위와 무관하게 부풀려질 수 있다 — 길이 조정 툴 부재, `Delay` 고정값으로 우회
**증상**: `Anim_Float` 트랙의 실제 키는 0~2.4s 범위(4키×5트랙)뿐인데, 에셋 자체가 보고하는 길이는 **5.0s**였다. UMG 애니메이션 길이를 직접 조정하는 MCP 툴은 없다.
**영향**: `Play Animation`으로 전체 재생하면 2.4s 이후 5.0s까지 **키 없는 유휴 구간**이 그대로 재생되므로, 이 구간의 끝을 뜻하는 `Finished` 이벤트에 위젯 자기소멸을 걸면 의도한 2.4s가 아니라 5.0s 뒤에야 소멸한다.
**해법**: `Finished`에 의존하지 말고 **키의 실제 종점 시각(2.4s)에 맞춘 고정 `Delay`**로 수명을 제어한다(`WBP_DamageNumber` 자기소멸이 이 패턴 채택 — [[야간③_데미지폰트_완료]] 참고).

### 함정 ㊼ — Windows-MCP `Click`/`Move`의 `loc` 좌표 파라미터가 문자열 직렬화되어 pydantic 검증에서 거부된다(3회 재현) — PowerShell user32.dll 직접 호출로 우회
**증상**: Windows-MCP `Click`/`Move`에 좌표(`loc`)를 넘기면 내부적으로 문자열 직렬화된 채 pydantic 스키마 검증에 걸려 거부되는 현상이 **3회 연속 재현**됐다.
**해법**: **PowerShell에서 `user32.dll`을 직접 호출**(`SetCursorPos`+`mouse_event`)해 우회한다. ★**`SetProcessDPIAware()` 호출이 필수** — 빠뜨리면 DPI 가상화로 논리좌표와 물리좌표가 어긋나 엉뚱한 곳을 클릭하는 사고가 **실제로 발생**했다.
**재사용 자산**: `scratchpad\click_at.ps1`.

### 함정 ㊽ — MCP `CaptureEditorImage`의 왕복 지연(8초 이상)은 수명이 짧은 연출을 구조적으로 캐치할 수 없다 — 로컬 .NET 버스트 캡처로 대체
**증상**: `CaptureEditorImage` 툴콜 왕복이 8초 이상 걸린다. 2.4초짜리 데미지 폰트처럼 **수명이 짧은 연출은 이 왕복 시간 안에 이미 사라져 있으므로**, MCP 툴콜만으로는 캐치가 구조적으로 불가능하다.
**해법**: **로컬 .NET `Graphics.CopyFromScreen`으로 클릭+sleep+3연사 캡처를 단일 PowerShell 스크립트 안에서** 처리한다 — MCP 왕복이 스크립트 실행 중간에 끼어들지 않아 왕복 지연이 사실상 0이 된다.
**재사용 자산**: `scratchpad\click_burst_capture.ps1`.

### 함정 ㊾ — 에디터 로그가 한국어 로케일이라 영어 에러 패턴 grep은 위양성 0건을 만든다
**증상**: 런타임 에러를 찾으려고 `"Accessed None"`(영어)으로 로그를 grep하면 **0건**이 나온다 — 실제 에러가 있어도 없는 것처럼 보이는 위양성이다.
**원인**: 이 프로젝트 에디터의 로그 로케일이 한국어라 같은 에러가 한국어 문자열로 찍힌다.
**해법**: **`"None에 액세스"` / `"블루프린트 런타임 오류"`** 패턴으로 grep해야 한다 — 이 프로젝트에서 영어 패턴 grep은 필수적으로 위양성이다.

### 함정 ㊿ — `get_connected_subgraph`를 EventGraph의 CustomEvent 진입점에서 호출하면 공유 Get 노드를 경유해 그래프 전체 연결성분이 혼입된다
**증상**: EventGraph의 CustomEvent 진입점에서 `get_connected_subgraph`를 호출했더니, 그 이벤트 체인과 무관한 노드까지 결과에 섞여 나왔다.
**원인**: EventGraph 안의 여러 이벤트 체인이 **공유 Get 노드(변수 게터 등)를 경유해 서로 연결**돼 있어, 한 진입점에서 도달 가능한 연결성분을 추적하면 사실상 EventGraph 전체가 한 덩어리로 잡힌다. **Function Graph는 무관**(함수마다 독립 그래프라 공유 경유가 없음).
**교훈**: EventGraph에서 얻은 **노드 수 실측치를 액면 그대로 신뢰하지 말 것** — 다른 이벤트 체인의 노드가 섞여 부풀려졌을 수 있다.

### 함정 (51) — PIE 중 `get_actor_transform` 조회값이 실제 렌더 위치와 불일치하는 사례 — 클릭 좌표는 화면 픽셀 직접 판독만 신뢰
**증상**: PIE 실행 중 특정 유닛(B1)의 `get_actor_transform` 조회값이 실제 화면 렌더 위치와 어긋나는 사례가 나왔다(원인 미규명). `WorldPosToScreenCoords`로 환산한 좌표도 같은 이유로 오도할 수 있다.
**해법**: 클릭 좌표가 필요한 자동화에서는 트랜스폼 조회값을 신뢰하지 말고 **`CaptureEditorImage` 직접 픽셀 크롭 판독**만 신뢰한다(스케일 2.014x/2.016x 환산 실측). **파티측(카메라에서 먼 원경) 유닛일수록 원근 왜곡으로 오차가 커진다** — 원경 유닛 좌표는 특히 보수적으로 다룰 것.

### 함정 (52) — `ResolveHit`이 `DT_Skills`의 구식 `Effect*` 컬럼을 직접 read — F7b의 컬럼 제거·`ResolveHit` 수술은 동세션 연속 실행 필수
**배경**: `ResolveHit`은 현재 `GetDataTableColumnAsString`으로 `DT_Skills`의 구식 `Effect*` 컬럼을 직접 조회한다. F7b에서 이 컬럼을 제거하는 작업과 `ResolveHit`을 신규 스키마로 수술하는 작업이 **한 세션 안에 연속으로** 이뤄지지 않으면, 컬럼이 사라진 중간 상태에서 `GetDataTableColumnAsString`이 빈 문자열을 반환 → `StringToFloat("")`가 0으로 캐스팅되어 **전 상태이상이 조용히 무음전멸**한다.
**부재 컬럼명 조회(추정, 미실측)**: 존재하지 않는 컬럼명으로 `GetDataTableColumnAsString`을 호출하면 에러 없이 빈 문자열을 반환하는 것으로 **추정**된다 — F7b 착수 시 스캐폴드로 1회 실측 확인이 필요하다(아직 확정 아님).
**출처**: [[F7_스킬아키텍처_확정]] §8-5·§8-12.

### 함정 (53) — `DataTableTools.set_rows`가 기존 DataTable 데이터 갱신의 표준 — `import_file` 재호출의 delete-recreate·GUID 함정(㉙)을 완전히 회피
**배경**: 함정 ㉙(§23)이 확인했듯, 이미 존재하는 DataTable에 `import_file`을 재호출하면 거부되고, 우회하려고 delete→recreate를 타면 **애셋 GUID가 새로 발급**돼 하드레퍼런스가 끊길 위험이 있었다.
**해법**: `DataTableTools.set_rows`로 **기존 행을 직접 갱신**하면 delete-recreate 자체가 필요 없어 GUID가 유지되고 하드레퍼런스가 끊기지 않는다. 향후 `DT_Skills`/`DT_SkillEffects`/`DT_StatusEffects` 갱신은 전부 이 경로를 표준으로 쓴다.
**출처**: [[F7_스킬아키텍처_확정]] §8-2·§8-12.
