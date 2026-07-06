---
type: reference
project: projectTP
updated: 2026-07-06
---

# 🛠️ 언리얼 MCP 실전 노하우

> UE 5.8을 unreal-mcp로 조작하며 실제로 겪은 함정·해법·방법론. **UE MCP 작업 전 필독.**
> art-pipeline / scene-builder / hd2d-art-director / gameplay-engineer / verifier / cpp-engineer 공용.
> 관련: [[HD2D_기법_지식베이스]] · [[개발_워크플로우]]
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
