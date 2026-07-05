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

> 실행 에이전트(sonnet)가 "설정을 하나씩 꺼보는" 배제법으로 16종을 시도하고도 실패한 버그를, 아래 방법으로 잡았다. **표면(셰이딩/설정)이 아니라 구조(지오메트리/데이터)를 의심할 때의 정석.**

1. **이분법으로 층을 가른다**: 원본 데이터 vs 엔진 렌더 / 정지 vs 애니 / 단독 vs 다수. 한 번의 비교로 절반의 가설을 죽인다. (예: 원본 PNG가 깨끗 → 데이터 무죄 → 렌더 문제 확정)
2. **결정적 판별 테스트 = 변수 격리**:
   - **MI 스왑 테스트**: 두 오브젝트의 머티리얼을 맞바꾼다. 문제가 **자리(트랜스폼)에 붙으면** 머티리얼 무죄, 지오메트리/배치 유죄.
   - **단독 배치 테스트**: 이웃을 제거한다. 혼자서 멀쩡하면 **상호작용(겹침·z-fight)** 이 원인.
3. **픽셀 법의학**: 스크린샷을 Pillow로 열어 줄무늬 행의 **RGB를 실측**한다. 줄 색이 무엇인지가 원인을 지목한다 — 배경색=투과, 제3의 팔레트색=z-fight(다른 프레임/오브젝트가 비침), 회색밴딩=압축.
4. **"만든 사람의 가설을 반증하라"**: 실행자가 세운 가설(여기선 "모션블러/velocity")을 **그 가설이 틀렸음을 증명하는 실험**(정지화면 재현)으로 먼저 죽인다. 가설을 지지하는 실험만 하면 영원히 못 잡는다.
5. **증상의 조건을 전부 만족하는 단일 원인**을 찾을 때까지: "위치·높이에 민감 + 어두운 캐릭터 심함 + 모든 렌더설정에 면역 + 단독 재현 불가" → 이 4개를 동시에 설명하는 건 공면 z-fight뿐이었다.

---

## 5. 이 프로젝트의 검증된 실측값 (복붙용)

- 카메라(4v4 정면): location (0, -7850, 750), rotation (pitch -6, yaw 90, roll 0)
- 스프라이트 쿼드: SM_SpriteQuad, rotation (0, 0, 90), scale (6.48, 2.59, 1.0) — 셀 100×40 비율 2.5:1
- 배치: X 간격 150, 중앙갭 300, **Y는 3cm씩 스태거**, snap_to_ground 후 z=지면+129.5
