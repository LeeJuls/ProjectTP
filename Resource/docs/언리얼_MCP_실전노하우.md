---
type: reference
project: projectTP
updated: 2026-07-07
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

