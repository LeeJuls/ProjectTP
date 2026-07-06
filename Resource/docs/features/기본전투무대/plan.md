---
type: plan
feature: 기본전투무대
status: 진행중
updated: 2026-07-05
---

# 📋 기본전투무대 세부 plan

> 청사진: [[청사진]] · 프로세스: [[개발_워크플로우]] · 로그: [[진행로그]]
> 조사 원본: [[P1_레시피_idle조사]] · [[P1_무대_배치조사]]
#projectTP/기본전투무대

## 단계 분해
| 단계 | 내용 | 담당 | 모델 | 상태 |
|---|---|---|---|---|
| S1 | 캐릭터 8종 합성(compose_party.py) | art-pipeline | sonnet | 완료 |
| S2 | UE 임포트 + 플립북 머티리얼 | art-pipeline | sonnet | 완료 |
| S3 | 무대 복제 + 4v4 배치 + 카메라 | scene-builder | sonnet | 대기 |
| S4 | idle 모션(SubUV) 활성화 | art-pipeline | sonnet | 대기 |
| S5 | 룩 패스(라이팅/PP) | hd2d-art-director | sonnet | 대기 |

---

## 1. 레시피 8종 (실측 확인 완료)
전체 레이어 경로는 [[P1_레시피_idle조사]]에 표로. 요약:

| ID | 컨셉 | cloth | hair | weapon |
|---|---|---|---|---|
| A1 | 남 기사 | cloth15 c1 | m5 c7 | weapon1 |
| A2 | 여 궁수 | cloth7 c2 | f3 c3 | weapon2 |
| A3 | 남 창병 | cloth3 c4 | m9 c8 | weapon3 |
| A4 | 여 법사 | cloth11 c3 | f6 c1 | weapon4 |
| B1 | 남 전사 | cloth9 c5 | m2 c2 | **weapon5 c2** |
| B2 | 여 도적 | cloth5 c6 | f8 c6 | weapon1 |
| B3 | 남 광전사 | cloth13 c7 | m12 c9 | weapon2 |
| B4 | 여 사제 | cloth17 c8 | f1 c5 | weapon3 |

- 팀 구분: A=한색/저채도, B=고채도. 남/여 헤어 교차.
- ⚠ **weapon5만 색상변형 존재**(`weapon5_c2_*`), weapon1~4는 단색. S1 스크립트에서 경로 분기 주의.
- 합성 순서(back→front): `hair_bot → weapon_bot → cloth_bot → skin → face → cloth_top → hair_top → weapon_top` (alpha_composite 누적).

## 2. 시트 스펙
- 원본 시트 800×680, **8열×17행, 셀 100×40px**.
- **idle = Row 0(0-based), 6프레임(열 0~5)**. 근거: 팩 `frameguide_v2.png` "IDLE 1" + `hero_knight.png` 실측 일치. 대체: Row 1(IDLE 2).
- 8종 전부 동일 레이아웃 → 머티리얼 RowIndex/FrameCount 공용.

## 3. 임포트 세팅 (텍스처 8종)
- Filter=**Nearest**, MipGen=**NoMipmaps**, Compression=**TC_EditorIcon** (도트 보존).
- 명명·경로: `/Game/Sprites/T_Party_A1..A4`, `T_Party_B1..B4` (합성 전체 시트 800×680 임포트).

## 4. 머티리얼 명세
- **마스터 `M_Sprite_Flipbook_Lit`** (신규, `M_Sprite_Lit` 계승): Blend=Masked, TwoSided=true, Shading=Lit. RGB→BaseColor, A→OpacityMask.
- **SubUV 로직**: `frame = floor(Time × FPS) % FrameCount`; `U = (baseU + (frame % GridX)) / GridX`; `V = (baseV + RowIndex) / GridY`. (idle은 frame이 0~5, RowIndex=0)
- **파라미터**: Texture, GridX=8, GridY=17, RowIndex=0, FrameCount=6, FPS=8(시작값).
- **MI 8개**: `MI_Party_A1..A4`, `MI_Enemy_B1..B4` — Texture만 각각 다르고 나머지 공용.
- 그림자: 프레임별 OpacityMask로 캐스트 섀도우 동작(S0 검증).

## 5. 무대 · 배치
- **무대**: `map_village_day` → **복제** `/Game/Stages/map_battle_village` (원본 무오염). 스팟 = "게이트 남쪽 마당"(좌우 대칭 가로등이 정면 무대 근거).
- **지면 Z=486**(실측 480~505). 국지 기복 ±20~30cm → **배치 시 snap_to_ground=true 필수**(특히 A2/A4).
- **배치**(정면 대치, Y=-6600, 팀내 간격 150, 중앙 갭 300, 안전폭 X∈[-750,+750]):

| 라벨 | X | Y | Z |
|---|---|---|---|
| Party_A1~A4 | -600, -450, -300, -150 | -6600 | 486 |
| Enemy_B1~B4 | 150, 300, 450, 600 | -6600 | 486 |

- **스케일**(Director 결정): 셀 비율 **2.5:1(X:Z) 유지**가 원칙. 시작값 X≈6.48·Z≈2.59(성인 체구 가정) — **절대 크기는 S3 스크린샷 보고 오너 확정**. (미적/가시성 사안, balance 소관 아님)
- **쿼드 회전**(⚠ S2 발견): `SM_SpriteQuad`는 XY평면(두께0)에 누워있음 → **roll=90 필수**(정면 기립). rotation=(0,0,0)이면 카메라 정면에서 얇은 선. yaw는 카메라 정면 응시 유지.
- 메시: `SM_SpriteQuad` 재사용. **⚠ 머티리얼은 컴포넌트 `overrideMaterials`로만 적용** — `StaticMeshTools.set_material`은 메시 에셋을 영구변경하므로 금지(S2 원복 이력). 아웃라이너: `BattleStage/Party`, `BattleStage/Enemy`, `BattleStage/Camera`.

## 6. 카메라 (안1, 실증 완료)
> ⚠ 정정(2026-07-06): S5 글리치 수사 중 전장을 Y=-7000으로 이동하며 **최종 카메라 = (0, -7850, 750)**이 됨(레벨에 저장된 현행값). 아래 -7550은 S3 당시 초기값.
- location (0, -7550, 750), rotation (pitch=-6, yaw=90, roll=0).
- 검증: 배치 라인 양 끝 화면 0.191/0.809 대칭, 중앙 0.500. 즉시 사용 가능.
- FOV 미세조정(HD-2D 좁은 원근)은 S5에서 CameraActor FieldOfView로.

## 7. 단계별 완료 정의(DoD) — TC 근거
- **S1**: `_composed/party/` 에 8종 합성 시트 PNG 8장, idle 6프레임 육안 확인, 레이어 순서 정합.
- **S2**: 텍스처 8종 Nearest/NoMip/TC_EditorIcon 실측, `M_Sprite_Flipbook_Lit`+MI 8개 존재, 쿼드에 정지 1프레임(frame 0) 도트 뭉개짐 없이 표시.
- **S3**: `map_battle_village`에 8기 배치(좌표/스케일/yaw/폴더 준수), PIE 아닌 에디터 뷰에서 8기 전원+좌우 대치+캐스트 섀도우 스크린샷.
- **S4**: PIE에서 8기 idle 6프레임 애니 재생(도트 무손상, 프레임 끊김/역방향 없음).
- **S5**: PPV(노출고정 등 [[HD2D_기법_지식베이스]] 실측값)+라이팅, 워시아웃 없음, before/after 스크린샷 → **오너 미적 승인**.

---

## 단계별 TC (qa-critic 작성 — P2)
> 표기: `[단계][ID] 조건 → 기대결과 | 상태`. 상세 "깨지는 시나리오"는 [[P2_TC설계]].
> ⚠ **S2↔S4 지연발현**: [S2][05] FrameCount 오설정은 S2(frame0)에선 안 잡히고 [S4][02]에서만 발현 → S2 통과해도 S4 재검 필수.

### S1 — 합성 ✅ PASS (verifier 독립검증 8/8)
- Crit [S1][01] `_composed/party/` → 정확히 8장, A1~4·B1~4 명명 | PASS
- Crit [S1][02] 각 시트 → 800×680 | PASS
- Crit [S1][03] Row0 col0~5 bbox 6개 non-None, col6·7=None | PASS
- High [S1][04] B1 무기 → `weapon5_c2` 반영(단색본과 상이) | PASS (A1 alpha 3050px vs B1 2878px)
- High [S1][05] 레이어 순서 → hair_top>cloth_top, weapon_top 최상단, skin>cloth_bot | PASS (코드+육안)
- High [S1][06] 8종 상호구분(중복 시트 없음) | PASS (SHA256 8/8 유니크)
- Med [S1][07] RGBA·여백 A=0·반투명 잔여 없음 | PASS
- Med [S1][08] 원본 `_RawAssets` 무오염 | PASS

### S2 — 임포트·머티리얼 ✅ PASS (verifier 독립검증 10/10, FrameCount=6 확정)
- Crit [S2][01] `T_Party_A1..B4` 8종 존재 | PASS
- Crit [S2][02] Nearest/NoMipmaps/TC_EditorIcon 전부 | PASS
- Crit [S2][03] 소스 800×680 유지(POT 패딩 없음) | PASS
- Crit [S2][04] `M_Sprite_Flipbook_Lit` → Masked/TwoSided/Lit, RGB→BaseColor, A→OpacityMask | PASS
- Crit [S2][05] SubUV 파라미터 → GridX8/GridY17/RowIndex0/**FrameCount6**/FPS8 | PASS
- Crit [S2][06] MI 8개 `MI_Party_A1..4`/`MI_Enemy_B1..4`, 부모=마스터 | PASS
- High [S2][07] MI↔Texture 1:1(오프바이원 없음) | PASS
- High [S2][08] frame0 도트 무손상(번짐 없음) | PASS
- High [S2][09] Masked 경계(반투명/사각배경 없음) | PASS
- Med [S2][10] frame0 종횡비(눌림/늘어남 없음) | PASS(육안, 절대스케일은 S3서 확정)

### S3 — 무대·배치·카메라 ✅ PASS (Director 실증: 스크린샷 2장 육안 + scene-builder 실측)
> 수정: 회전 버그(yaw90 측면화) → `(0,0,90)`, 스케일 `(6.48,2.59,1.0)`, A2 둔덕 회피로 8기 Y=-6700. **크기 6.48배 오너 확정.**
- Crit [S3][01] 복제 존재 + 원본 무오염 | PASS
- Crit [S3][02] 8기 존재(Party4+Enemy4, MI 매핑) | PASS
- Crit [S3][03] 좌표 X -600..-150 / 150..600, Y=-6700 | PASS
- Crit [S3][04] snap_to_ground → A2·A4 부양/매몰 없음 | PASS (둔덕 회피 후퇴)
- Crit [S3][05] 카메라 8기 전원 화면 안 | PASS (전원 y 0.46~0.69)
- High [S3][06] roll=90 + yaw 정면 응시 | PASS
- High [S3][07] 캐스트 섀도우 8개 | PASS
- High [S3][08] 스케일 비율(눌림/늘어남 없음) | PASS (회전 버그 수정 후)
- High [S3][09] 좌우 미겹침·대칭 | PASS (겹침 없음, 대칭 원근차 근사)
- Med [S3][10] 아웃라이너 Party/Enemy/Camera | PASS
- Med [S3][11] 구조물 간섭 없음 | PASS
- Med [S3][12] 워시아웃 사전 점검(라이팅 전) | PASS 예비 (S5 재확인)
- ⚠ 신규 이월 [S3][G] 캐릭터 스미어 글리치(SubUV UV이동 × 모션블러/velocity, AA 무관 판명) → **S5 해결**

### S4 — idle SubUV ✅ PASS (art-pipeline 3회 캡처 + Director 스택 실증)
- Crit [S4][01] 8기 프레임 순환 재생 | PASS (실루엣 각도 변화)
- Crit [S4][02] 6프레임만·**col6·7 빈 프레임 미표시** | PASS (3회 캡처 깜빡임 없음=FrameCount6 실효)
- Crit [S4][03] 순방향·wrap 매끄러움(역방향/스킵 없음) | PASS (이상 없음)
- High [S4][04] 애니 중 도트 무손상(크로스페이드 없음) | 이월 → S5 (글리치 해결 후 판단)
- High [S4][05] col 0~5로만 한정(수식 검증) | PASS (깜빡임 없음으로 간접)
- High [S4][06] 8기 독립 재생(스터터 없음) | PASS (좌/우 패턴 상이)
- Med [S4][07] FPS8 속도 적정 | PASS (유지)
- Med [S4][08] RowIndex Row0 고정 | PASS

### S5 — 룩 패스 + 글리치 해결 ✅ PASS (Director/Fable 직접 실증 + 오너 육안 승인)
> **글리치 근본원인 확정·완치**: 공면 쿼드 z-fight → Y 3cm 스태거. 오너: "완벽함". Lit 복원 후에도 무재발.
- Crit [S5][01] 워시아웃 없음 | PASS (Lit 최종 스크린샷)
- Crit [S5][02] AutoExposure Min=Max=1.0 고정 | PASS (hd2d 적용)
- High [S5][03] Bloom 0.45 | PASS (hd2d 적용, 4.0→0.45)
- High [S5][04] 캐스트 섀도우 유지 | PASS (Lit 복원 후 발밑 그림자 확인)
- High [S5][05] before/after 스크린샷 | PASS (raw/ 다수: S5_look_*, S5_글리치해결_최종, S5_Lit최종)
- Med [S5][06] Sat/Contrast/Vignette | PASS (오너 B안: 1.0/1.03/0.45 — 맵 팔레트 과포화 회피)
- Med [S5][07] 원본맵 무오염 | PASS (map_village_day 무변경 — 복제본만 편집)
- Med [S5][08] 8기 균일 조명 | PASS
- 신규 [S5][G] 공면 z-fight 해결·무재발 | **PASS** (Unlit·Lit 양쪽 실증, 오너 육안)

## 이월(deferred) TC
| TC | 검증 예정 단계 | Director 승인 |
|---|---|---|
| [S2][05] FrameCount 실효(빈프레임) | S4[02] 발현 검증 완료(깜빡임 없음) | 해소 ✅ |
| [S3][09] 절대스케일 겹침 확정 | 오너 6.48배 확정 → 겹침 없음 | 해소 ✅ |
| [S3][G] 캐릭터 스미어 글리치 | **S5 해결: 공면 z-fight → 3cm 스태거** (모션블러 가설은 오진이었음) | 해소 ✅ |
| [S4][04] 애니 중 도트 무손상 | 글리치 해소로 F(풀테스트)에서 최종 확인 | F로 이월 |

## 진행 체크리스트
- [x] S1 개발 → 게이트
- [x] S2 개발 → 게이트
- [ ] S3 개발 → 게이트
- [ ] S4 개발 → 게이트
- [ ] S5 개발 → 게이트
- [ ] 풀 테스트(designer+qa+verifier) + 방향부합(Fable+오너)
