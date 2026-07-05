---
type: reference
project: projectTP
updated: 2026-07-05
---

# 🎨 HD-2D 기법 지식베이스

> `hd2d-art-director` 에이전트의 상시 참조 문서. HD-2D 룩의 핵심 요소·UE 파라미터·우리 실측 세팅·함정.
> 관련: [[작업로그_HD2D아트검증_플레이북]] · [[에이전트팀_설계]]

---

## HD-2D란

**2D 스프라이트(픽셀아트) + 3D 배경 + 현대적 라이팅/포스트프로세스**의 결합. 옥토패스 트래블러·트라이앵글 스트래티지(Square Enix)가 대표. 도트의 향수 + 3D의 깊이·빛을 동시에.

핵심: 스프라이트를 단순 오버레이가 아니라 **3D 무대 위 라이팅 받는 오브젝트**로 취급한다. 그래서 그림자·깊이·분위기가 생긴다.

---

## 핵심 시각 요소 (5축)

1. **픽셀퍼펙트 스프라이트** — 도트가 뭉개지지 않게. Nearest 필터, NoMipmaps.
2. **Lit 통합** — 스프라이트가 3D 라이팅·캐스트 섀도우를 받음. Unlit 오버레이와의 결정적 차이.
3. **틸트시프트 DoF** — 화면 상/하단을 흐리게 → **미니어처(디오라마)** 느낌. HD-2D의 시그니처.
4. **블룸 + 컬러그레이딩** — 빛 번짐 + 채도·대비·톤으로 분위기. 과하면 워시아웃.
5. **약한 원근 카메라** — 완전 정사영이 아니라 살짝 원근을 준 앵글. 깊이감.

---

## UE 구현 파라미터 (실측 — 아트검증 S0에서 확보)

### 텍스처 (픽셀퍼펙트)
- Filter: **Nearest**
- Mip Gen: **NoMipmaps**
- Compression: **TC_EditorIcon** (도트 보존)

### 스프라이트 머티리얼
- Blend: **Masked**, **TwoSided = true**
- RGB → **BaseColor**, Alpha → **OpacityMask**
- Shading: **Lit** (그림자·라이팅 받게)
- `TextureSampleParameter2D`로 파라미터화 → 캐릭터별 MaterialInstance 교체

### 라이팅
- **KeySun**: Directional Light (주광, 각도로 그림자 방향)
- **FillSky**: Sky/앰비언트 (그림자 안 죽게 채움)

### 포스트프로세스 볼륨 (PPV)
- **AutoExposure 고정**: min = max = 1.0 (노출 흔들림 제거 — 중요)
- **Bloom**: 0.45 (과다 주의 — 1.3은 워시아웃이었음. `map_battle_village`에서도 기본값 4.0은 과다했음)
- **Vignette**: 0.45
- **Saturation**: 1.15, **Contrast**: 1.08 — **단, 맵 자체 색보정이 이미 채도 높은 팔레트(예: 목재/오렌지 위주 village 맵)면 과포화됨. 그 경우 Saturation 1.0/Contrast 1.03 정도로 완화**(S5 실측, `map_battle_village`에서 A/B 비교 후 B안 채택)
- (틸트시프트 DoF는 무대 규모에 맞춰 조정)

---

## ⚠ 함정 (실측 기록)

| 증상 | 원인 | 해결 |
|---|---|---|
| 스프라이트 하얗게 날아감(워시아웃) | 오픈월드 템플릿의 SkyAtmosphere+VolumetricCloud+밝은 라이트 | 템플릿 하늘/라이트 제거, 무대 격리(예: 고공 z=10000) |
| 화면 전체 번짐 | Bloom 과다(1.3) | Bloom 0.45로 |
| 노출이 들쭉날쭉 | AutoExposure 자동 | min=max=1.0 고정 |
| 도트 뭉개짐 | 밉맵/선형필터/압축 | Nearest+NoMip+TC_EditorIcon |
| CaptureViewport 에러 | 파라미터 누락 | captureTransform/annotations/bShowUI **3개 모두** 명시 |
| ★★★ **여러 스프라이트 배치 시 가로 줄무늬/찢김**(위치·높이에 민감, 어두운 캐릭터 심함, 단일 배치에선 재현 불가, **머티리얼·AA·모션블러·포그·라이팅·VRS 등 모든 렌더 설정에 면역** — hd2d 16종 배제실험 전부 무효였던 그 증상) | **공면(coplanar) 쿼드 간 Z-파이팅 (S5 확정·해결).** 파티를 한 줄(동일 깊이 평면)에 배치하면 폭 648cm 쿼드가 이웃과 77%(498cm) 겹침 — 몸통 불투명 픽셀끼리도 겹쳐(간격 150 < 몸폭 ~250) 동일 깊이 픽셀이 행 단위로 깊이판정 요동. **단일 쿼드 테스트(S0·S2)에선 절대 재현 안 되고 다수 배치(S3)에서만 발생**해 원인이 은폐됨 | **깊이축으로 2~3cm 계단 배치**(예: Y=-7000, -7003, …) — 육안 식별 불가, 공면성 파괴로 즉시 완치. **HD-2D 일렬 배치의 근본 함정 — 전투 스폰 로직에 스태거를 기본 내장할 것.** 진단 팁: **MI 스왑 테스트**(문제가 자리에 붙나/머티리얼에 붙나)와 **단독 배치 테스트**(이웃 제거)가 가장 싸고 결정적인 판별 |
| 화면 전체 도트 미세 빗질(comb) — 위 z-fight와 **중첩 발생**했던 원인 #1 | **에디터 자동 스크린퍼센티지**(`ScreenPercentageMode=BasedOnDisplayResolution`)가 내부 저해상도 렌더→업스케일. PIE도 상속(`OverridePIEScreenPercentage=1`) | EditorPerformanceSettings **Manual + 100%** 고정 (`realtimeScreenPercentageMode=Manual, bOverrideManualScreenPercentage=true, manualScreenPercentage=100`) |
| (예방) 픽셀아트 VRS 셰이딩률 저하 | HW VRS(8x8/16x16타일)+Nanite Software VRS(2x2)가 저대비 영역 셰이딩을 뭉갤 수 있음 | `DefaultEngine.ini [SystemSettings]`: `r.VRS.Enable=0`, `r.VRS.EnableSoftware=0`, `r.Nanite.SoftwareVRS=0` (재시작 필요). 이번 주범은 아니었으나 픽셀아트 보호로 유지 |

### ⚠ 도구 제약: CaptureViewport 결과가 큰 경우 base64→PNG 디코딩 불가
`hd2d-art-director` 서브에이전트 세션에는 Bash/코드실행 도구가 제공되지 않아, `CaptureViewport` 결과(base64 PNG, 통상 400만자 이상)가 tool-results txt 파일로 저장돼도 이를 디코딩해 PNG로 볼 방법이 없었다(Read/Grep은 텍스트 처리만 가능, `ProgrammaticToolset`의 sandboxed python은 `base64`/파일 I/O 모듈 미지원). 이 글리치 작업(S3)에서 실제로 겪음 — **스크린샷 확보가 필요한 hd2d-art-director 작업은 Bash 도구가 있는 세션(art-pipeline 등)에서 대신 캡처하거나, Director가 이 에이전트에 Bash 권한을 부여해야 함**. → **S5에서 Bash 권한 부여받아 해결**: `python decode_capture.py <tool-results.txt> <out.png>` 후 Read로 확인 가능(스크립트: `docs/scripts/decode_capture.py`).

### PostProcessVolume 세팅은 `settings`(JSON 통짜) 프로퍼티로 다룬다
`ObjectTools.get_properties(instance=PPV, properties=["settings"])`로 전체 조회, `set_properties`로 부분 갱신 시 `{"settings": {"bOverride_X": true, "x": value}}` 형태로 전달(오버라이드 플래그를 반드시 함께 켜야 값이 적용됨). PPV 액터의 `bUnbound`(전역 여부)·`bEnabled`·`blendWeight`는 최상위 프로퍼티로 별도 조회.

---

## 작업 원칙 (art-director용)

- **파라미터는 한 번에 하나씩** 바꾸고 스크린샷 비교. 동시 변경 시 원인 분리 불가.
- 실측 세팅을 출발점으로, 무대·캐릭터에 맞게 미세조정.
- **미적 최종 판단은 오너.** art-director는 before/after 스크린샷으로 A/B 제안만.
- 새로 검증된 유의미한 세팅은 이 문서에 추가(지식 축적).

---

## 참고 (스타일 레퍼런스, 복제 금지)

- 옥토패스 트래블러 / 트라이앵글 스트래티지 — 라이팅·틸트시프트·컬러그레이딩 방향성 참조용.
- 기법·원리·파라미터는 자유 활용. 게임 에셋·튜토리얼 텍스트/이미지 **통째 복제 금지**.
- 새 기법 조사가 필요하면 WebSearch로 최신 UE HD-2D 튜토리얼 참조(필요시에만 — 토큰 절약).
