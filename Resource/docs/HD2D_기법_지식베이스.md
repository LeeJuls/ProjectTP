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
- **Bloom**: 0.45 (과다 주의 — 1.3은 워시아웃이었음)
- **Vignette**: 0.45
- **Saturation**: 1.15, **Contrast**: 1.08
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
