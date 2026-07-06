---
type: plan
feature: 옥토패스대치
status: 진행중
updated: 2026-07-06
---

# 📋 옥토패스대치 세부 plan

> 청사진: [[청사진]] · 프로세스: [[개발_워크플로우]] · 스냅샷: [[P0_상속스냅샷]]
> 승인된 상위 plan(에이전트 피드백 4건 반영)이 이 문서의 원본. 여기는 실행용 구체 명세.
#projectTP/옥토패스대치

## 단계
| 단계 | 내용 | 담당 | 모델 | 상태 |
|---|---|---|---|---|
| P0 | 복제(map_battle_octopath)+상속스냅샷+문서정정 | Director+scene-builder | opus/sonnet | 완료 |
| P1 | 좌표표+카메라 A/B 설계(무이동 수치검증) / flip 명세(아래 §2) | scene-builder / Director | sonnet | 진행중 |
| P2 | 단계별 TC | qa-critic | opus | 대기 |
| S1 | FlipX 마스터 파라미터 + flip MI 4종 신규 | art-pipeline | sonnet | 대기 |
| G1 | flip 게이트(렌더 육안·비대칭·셀경계·**정면레벨 회귀**) | verifier→Director | haiku | 대기 |
| S2 | 사선 배치(유니크Y)+오블리크 카메라 → 오너 A/B 선택 | scene-builder | sonnet | 대기 |
| S3 | 룩: KeySun 정면-상단(C2)·PPV·진영 명암대조 | hd2d | sonnet | 완료(KeySun pitch-60/yaw90, DoF는 오너 A안=off 확정) |
| **S2'** | **오너 직접 배치 도구**(BP_BattleSpawnPoint) — S2 좌표는 "초기 배치"로 유지, 최종 배치는 오너 | gameplay-engineer | sonnet | **도구 완료·G게이트 8/8 PASS → 오너 배치 진행 중** |
| T4 | 오너 배치 후 검증(z-fight·프레임·접지) | verifier | haiku | 대기 |
| F | 풀테스트+오너 방향부합 — ⚠ TC-12 좌표 기대값=오너 최종 배치 실측으로 대체, TC-15/23/29 판정=FaceLeft+컴포넌트 상태 기준(BP 전환 반영). P2 문서의 옛 좌표는 Y스왑 이전 값. ⚠ 공격버튼데모 산출물(UI_AttackButton·마스터 TimeOffset·카메라 autoActivate) 존재 인지 후 TC-29 판정 | qa·verifier·Director | opus·haiku | 대기 |

## 1. 방향 규칙 (확정)
- 적 4기(화면 좌측 = 월드 +X): **원본 MI**(우향 그대로) — `MI_Enemy_B1..B4`
- 아군 4기(화면 우측 = 월드 -X): **flip MI**(좌향) — `MI_Party_A1_flip..A4_flip` **신규**
- ⚠ 기존 `MI_Party_A1..A4` 변조 절대 금지(정면대치 레벨 공유 — C1)

## 2. flip 구현 명세 (S1 — art-pipeline 피드백 확정판)
- 마스터 `M_Sprite_Flipbook_Lit`에 추가:
  - `ScalarParameter FlipX` (기본 **0**) — 기본 0이라 기존 MI/정면레벨 무영향
  - `OneMinus(baseU)` + `Lerp(A=baseU, B=OneMinus, Alpha=FlipX)`
  - **삽입 지점**: `ComponentMask_0`(TexCoord→U) 출력이 물려있던 자리를 Lerp 출력으로 교체 — **col 오프셋(Add_0) 더하기 전**. 다른 지점이면 프레임 재생순서 역전 버그.
  - col/GridX/GridY/RowIndex/FPS 배선 불변. recompile 필수.
- flip MI 4종: `MaterialInstanceTools.create`(부모=마스터) → SpriteTex=각 T_Party_A*, FlipX=1 오버라이드. 경로 `/Game/Materials/`.
- 도구 주의: `get_expression_inputs` 반환 부정확 → 배선은 `connect_expressions` 명시 + 재조회 이중검증.

## 3. 좌표·카메라 (P1 확정 — Director 판정 반영)
> 원설계 [[P1_좌표카메라설계]]에서 **사선 방향을 레퍼런스 정합으로 수정**: 앞열=바깥쪽(외곽), 뒤열=중앙(소실점 쪽). 진영 내 Y 역순 스왑. Z는 S2 배치 시 재트레이스(+129.5).

| 라벨 | X | Y | 비고 |
|---|---|---|---|
| Party_A1 | -600 | **-6990** | 아군 최앞(바깥) |
| Party_A2 | -450 | -6908 | |
| Party_A3 | -300 | -6794 | |
| Party_A4 | -150 | **-6705** | 아군 최뒤(중앙) |
| Enemy_B4 | 600 | **-7010** | 적 최앞(바깥) |
| Enemy_B3 | 450 | -6892 | |
| Enemy_B2 | 300 | -6806 | |
| Enemy_B1 | 150 | **-6695** | 적 최뒤(중앙) |

- 유니크Y 8개(인접차 ≥10cm) ✓ · X스텝 150 ✓ · 뒤열 축소율 21.5~29.4%(A안 기준) ✓
- **카메라 A안(채택)**: Location(-90,-7850,750) / Rotation(pitch-6, **yaw84**, roll0) — 6° 오프축(12°는 DoD 동시만족 불가, 15회+ 실측). FOV 미세조정은 S3.
- **B안(참고)**: (-700,-8000,750)/(pitch-5.5,yaw65) — 25°는 이 스트립 치수상 구조적 불성립(축소5.3% 또는 간격10%). S2에서 참고 캡처만 떠서 오너에게 실물 비교 제공.
- **fence_158 제거 승인**(S2에서 실행, Y스왑 후 8기 전체 간섭 재확인 포함).

## 4. 상속 베이스라인 (P0 스냅샷 — 이상 발생 시 신규/상속 구분 기준)
- 카메라 (0,-7850,750)/(-6,90,0) · 볼류메트릭 포그 off · PPV 오버라이드 18종(노출고정·블룸0.45 등) · **랜턴 CastShadows=true(BP 컨스트럭션 스크립트가 로드 시 재적용 추정 — S5의 off는 비지속. S3 룩은 이 값을 전제로 설계)** · 스트립 내 fence 7개 잔존.

## 단계별 TC (P2 완료 — 상세·도구시퀀스는 [[P2_TC설계]])
> ⚠ 실행 전제 3건: ① village 회귀 TC는 **각 게이트 맨 마지막**(레벨 스위칭=뷰포트 리셋, 끝나면 octopath 재로드) ② 카메라 TC는 SetCameraTransform(A안) 선행 or captureTransform 명시 ③ 수치 TC는 CaptureViewport **labeledActors 메타데이터로 디코드 없이** 판정, 육안 TC만 분할 캡처.

### G1 — flip 게이트 ✅ PASS (verifier 11/11)
- Crit [TC-02/05/07/08/11] flip MI FlipX=1·마스터 기본0·원본 무오염·좌향 렌더·**village 회귀 무오염** | 전부 PASS
- High [TC-01/03/06/09/10] MI존재·텍스처1:1·Lerp삽입점·애니 중 flip유지·seam없음 | 전부 PASS
- Med [TC-04] 재생 파라미터 무변조 | PASS / [TC-M3] 비대칭 어색함 | **오너 리뷰 대기**(증적 raw/tc08~09)
- 이월: [TC-15 마주봄] → S2.

### S2 — 사선 배치 게이트 (개발완료 · **오너 A안(6°) 확정** · 잔여 독립검증은 S3 게이트에 통합)
- Crit [TC-15] 마주봄 | PASS 예비(Director 육안: A안 캡처에서 적 우향·아군 좌향 확인)
- Crit [TC-23] village 불변 | PASS 예비(scene-builder is_dirty=false — S3 게이트서 verifier 재확인)
- High [TC-12/13/16/19] 좌표·유니크Y·프레임 안(0.173~0.868)·앞열=바깥 | PASS(scene-builder 계측)
- High [TC-17] 미겹침 / Med [TC-14/18/22] 접지·뒤열≤30%·z-fight | S3 게이트서 verifier 확정
- Med [TC-21] fence158 제거 PASS. ⚠ **fence_47이 A3·A4·B1과 AABB 교차**(육안 실루엣 겹침은 없음) → S3 게이트 재확인 항목.
- 캡처: [[raw/S2_A안.png]](채택) · [[raw/S2_B안참고.png]](기각 — 진영 비대칭·겹침)

### S3 — 룩 게이트
- High [TC-24] KeySun 정면-상단(측면광 금지) / [TC-25] PPV 상속 유지 | 대기
- Med [TC-26/27] 워시아웃 없음·랜턴 그림자 베이스라인 / [TC-M-대조] 진영 명암대조(**오너육안**) | 대기

### F — 통합
- Crit [TC-29] 정면레벨 최종 무오염(TC-11+23 재실행) | 대기
- High [TC-28] 마주봄+원근사선+애니 동시성립 | 대기
- [TC-M-방향부합] **오너 최종: 옥토패스 느낌** | 대기

## 진행 체크리스트
- [x] P0
- [ ] P1 → plan §3 확정
- [ ] P2 TC
- [ ] S1 → G1 게이트
- [ ] S2 → 오너 앵글 선택
- [ ] S3 → F
