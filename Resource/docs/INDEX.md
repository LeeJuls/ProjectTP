---
type: index
status: PASS
project: projectTP
updated: 2026-08-13
status_note: docs/scripts/vaultfix/generate_index.py로 frontmatter에서 자동생성 — 손으로 편집하지 않는다
---

# INDEX — projectTP 옵시디언 볼트 전체 목록

> ★자동생성 문서. 손으로 편집하지 마라 — 다음 `generate_index.py --apply` 실행에서 덮어써진다.
> 총 217개 문서, `type`별로 묶었다. 표의 "요약"은 frontmatter `status_note`가 있으면 그 첫 문장,
> 없으면 문서 첫 헤딩 다음 문장을 썼다(둘 다 200자 상한 — 표시용 절삭이며 frontmatter 원문은 무수정).
> 둘 다 없으면 빈칸이다(추측해서 채우지 않는다). 전문은 각 문서의 frontmatter/본문에서 확인.

| 항목 | 값 |
|---|---|
| 총 문서 수 | 217 |
| 요약 빈칸 | 0 |
| type 그룹 수 | 10 |

## 계획 (plan) (33)

| 문서 | status | 요약 |
|---|---|---|
| [[codex/UE5.8_Codex_학습계획\|UE5.8_Codex_학습계획]] | WIP | 상위: [[projectTP_허브]] · 기록 대상: [[codex/UE5.8_projectTP]] · 기존 근거: [[언리얼5.8_기술카탈로그]] |
| [[features/_TEMPLATE/plan\|plan]] | DRAFT | 청사진: [[features/_TEMPLATE/청사진\|청사진]] · 프로세스: [[개발_워크플로우]] |
| [[features/_TEMPLATE/청사진\|청사진]] | DRAFT | 목표 |
| [[features/걸어나오기연출/plan\|plan]] | ARCHIVED | W0~W2 완료, W3 부분판정(3/8 PASS + 5/8 이월/정적보증)(※ 분모 8 = 전 9항목 중 WT-22 "미실시" 제외. |
| [[features/걸어나오기연출/청사진\|청사진]] | ARCHIVED | 진행중 — 구현 완료, WF(오너 육안 튜닝)만 잔여(2026-08-11 정정, 근거: [[plan]] 단계 표) — [director 판정] WF 잔여는 아래 원문 + 오너_대기목록 이관 확인 |
| [[features/공격버튼데모/plan\|plan]] | 완료 (오너 라이브 확인 대기) | 옥토패스대치 진행 중 오너 요청으로 끼어든 빠른 데모. |
| [[features/기본전투무대/plan\|plan]] | PASS | 완료 (F풀테스트 잔여) |
| [[features/기본전투무대/청사진\|청사진]] | PASS | 상위: [[projectTP_허브]] · 프로세스: [[개발_워크플로우]] · 세부: [[features/기본전투무대/plan\|plan]] · 로그: [[진행로그]] |
| [[features/스킬연출구조/E_스파이크_plan\|E_스파이크_plan]] | WIP | S0/S1/S2' PASS · S4a-0 완료(스크립트 경로) · S4a 완료(2026-08-12, 스팟검증) — S2 진행 중 · R2 취소(2026-08-12, H18 블록 부재 확정) — [director 판정] S2 진행 중 · S3~S6 재검토 대기 |
| [[features/스킬연출구조/plan\|plan]] | PASS | D5 PASS(2026-08-11) — 설계 트랙 종료. |
| [[features/스킬연출구조/raw/FT1_plan\|FT1_plan]] | DRAFT | director 설계(2026-08-13) — FT1 자동 재생 하네스 plan. |
| [[features/스킬연출구조/청사진\|청사진]] | SUPERSEDED | plan 승인(2026-08-11) — 4슬롯으로 구조 변경됨. |
| [[features/옥토패스대치/plan\|plan]] | ARCHIVED | 진행중 — [director 판정] 기능 동결 — 아래 원문의 '진행중'은 스테일 |
| [[features/옥토패스대치/청사진\|청사진]] | ARCHIVED | 진행중 — [director 판정] 기능 동결 — 아래 원문의 '진행중'은 스테일 |
| [[features/전투레벨트리밍/plan\|plan]] | PASS | Context |
| [[features/전투완성/plan\|plan]] | WIP | F0~F9a 게이트 전부 통과, 잔여 F9b(오너 육안 풀플레이)·S1 SPD 오라클런 검증. |
| [[features/전투완성/raw/F7b_재개계획_초안\|F7b_재개계획_초안]] | BLOCKED | BLOCKED 근거(director 지정): 선행=S1 원장 봉인 — 오너 20턴 런은 [[BT5_S1봉인수단_판별]]의 AWAIT_OWNER가 추적. |
| [[features/전투완성/청사진\|청사진]] | PASS | F0~F9a 게이트 통과(F0 잔여 TC 2026-07-17 재판정 — 03·05 실측 PASS·04 해소·01·02 하류 커버, [[plan]] 참고) — 잔여는 F9b 오너 육안 풀플레이 + 원장 재수집(★신규 SPD 오라클-diff 방식 필수, 관측-봉인 금지 — 구 F9a 원장은 공식 증명으로 유효하나 SPD 이후 라이브 재현 불가) 2건. |
| [[features/카메라액션/청사진\|청사진]] | ARCHIVED | 완료(원안 기준, 2026-07-07) — 본문(고정 카메라 2기 C0/C1)은 v3(2026-07-08)에서 철거되고 동적 OTS 카메라 1기(ActionCam_Dynamic)+토글버튼으로 대체됨. |
| [[features/턴제전투MVP/plan\|plan]] | ARCHIVED | 진행중 |
| [[features/턴제전투MVP/청사진\|청사진]] | ARCHIVED | 진행중 |
| [[plans/ArtMVP_아트선검증_계획\|ArtMVP_아트선검증_계획]] |  | 작성일: 2026-06-28 / 엔진: UE 5.8 / 상태: ~~계획만, 구현 미착수~~ → ✅ **2026-08-11 정정**: S0 검증 **완료·GO 판정**. |
| [[plans/LOG-A_실행계획\|LOG-A_실행계획]] | PASS | 오너 승인 완료 — 착수 |
| [[plans/로그시스템_개선_plan\|로그시스템_개선_plan]] | PASS | 확정 — LOG-A 즉시 착수 / FT1-0은 S1 봉인 후 |
| [[plans/로드맵_버전계획\|로드맵_버전계획]] | PASS | 방향성2 반영 재작성 완료 (2026-07-13) — 다음: 알파 단계별 상세화(A1 전투완성부터). |
| [[plans/문서구조_개선plan\|문서구조_개선plan]] | DRAFT | v4 — 범위를 전투(92) → docs 전역(209)으로 확대. |
| [[plans/알파_개발계획\|알파_개발계획]] | WIP | 방향성2 반영 재작성 (2026-07-13) — 승인 후 단계별 features/ 상세화. |
| [[plans/자율작업배치_2026-07-17\|자율작업배치_2026-07-17]] | PASS | v2 — qa 적대 피드백 반영(H1~H3·M1~M4·L1~L3 전 수용) — **전 트랙 실행 완료**(2026-07-17). |
| [[plans/자율작업배치_2026-07-31\|자율작업배치_2026-07-31]] | PASS | 완료 (2026-07-31 야간) — 오프라인 목업 트랙 종료. |
| [[plans/자율진행_plan_v1\|자율진행_plan_v1]] | DRAFT | 초안 — 에이전트 피드백 + qa TC 라운드 대기 |
| [[plans/자율진행_plan_v2\|자율진행_plan_v2]] | WIP | ★확정 — 피드백 4건 반영 완료. |
| [[방향성1_백업/방향성1_로드맵_버전계획\|방향성1_로드맵_버전계획]] | SUPERSEDED | 백업/구버전(방향성1) — 방향성2로 대체됨. |
| [[방향성1_백업/방향성1_알파_개발계획\|방향성1_알파_개발계획]] | SUPERSEDED | 백업/구버전(방향성1) — 방향성2로 대체됨. |

## 설계 (design) (23)

| 문서 | status | 요약 |
|---|---|---|
| [[design/HD2D_PvP_ATB_설계\|HD2D_PvP_ATB_설계]] |  | 작성일: 2026-06-28 / 엔진: UE 5.8 (`D:\unreal\UE_5.8`) / 상태: **설계 검토 단계, 구현 미착수** |
| [[design/기획_방향성\|기획_방향성]] | PASS | ★방향성 2 공식 확정 (오너 2026-07-11). |
| [[design/백업_결정패키지_2026-07-17\|백업_결정패키지_2026-07-17]] | PASS | 실행 완료 (2026-07-18) — 오너 채택 = Git LFS 별도 저장소. |
| [[design/에이전트팀_설계\|에이전트팀_설계]] |  | UE 5.8 HD-2D 턴제 PvP 배틀을 만드는 **멀티에이전트 팀 청사진**. |
| [[design/전투VFX_방향\|전투VFX_방향]] | PASS | 방향 확정 (Director 판단 + 오너 논의 2026-07-26) — 실행은 아트 단계 |
| [[features/스킬연출구조/raw/D1_4슬롯구조_확정\|D1_4슬롯구조_확정]] | PASS | 3차 개정(D4.5 실측 반영) — D5 대기 |
| [[features/스킬연출구조/raw/D4.5c_연출SFX행확정\|D4.5c_연출SFX행확정]] | PASS | D4.5-c 산출 — D5 대기 |
| [[features/스킬연출구조/raw/D5_값배정\|D5_값배정]] | PASS | D5 산출 — Director 게이트 대기 · ★2026-08-12 정정: §2-2 `FxCastId=0` 의미 반전(외부FX없음, 舊 모션폴백 `63000100` 서술 취소) — D6 폴백 배선 주의 — [director 판정] FxCastId=0 반전 정정 반영 + 내장트레일 파급 재검토 중 — [[BT-DOC1_정본경계설계]] §5-5 |
| [[features/전투완성/raw/BP정리_통합명세_2026-08-11\|BP정리_통합명세_2026-08-11]] | PASS | D6 착수 전 필독 |
| [[features/전투완성/raw/BT-DOC1_정본경계설계\|BT-DOC1_정본경계설계]] | PASS | director 판정 확정(2026-08-13) — 문서구조_개선plan 7단계의 설계 SSOT. |
| [[features/전투완성/raw/BT-DOC2_status매핑규칙\|BT-DOC2_status매핑규칙]] | PASS | director 판정 확정(2026-08-13) — 문서구조_개선plan 3단계의 매핑 SSOT. |
| [[features/전투완성/raw/BT3_MA_상세설계서\|BT3_MA_상세설계서]] | PASS | 설계 완료(구현 0건) — 게이트 AU-B3-01~03 + 신설 3항 반영 / PM 확인 요청 4건 / 미확인 8건 · ★★2026-08-12 재갱신(director 6차 + 오너 승인) — §9-1 신설: 착수 순서 확정(FT1이 S1보다 먼저, MA-1a가 기준선). |
| [[features/전투완성/raw/F7_스킬아키텍처_확정\|F7_스킬아키텍처_확정]] | PASS | ★Director 확정 2026-07-15 — F7 스킬 아키텍처 SSOT(오너 승인, F7a/F7b 분할, gameplay 실측+qa-critic BLOCKER 게이트 반영) — 부트스트랩 주체 변경 2026-07-16(오너 승인, Claude 직접 시도+실패시 오너 폴백) |
| [[features/전투완성/raw/F7b_데이터초안_노트\|F7b_데이터초안_노트]] | DRAFT | F7b 데이터 prep 초안 노트 — status_effects.csv/skill_effects.csv/skills_v2_draft.csv 3파일 부속. |
| [[features/전투완성/raw/SPD원장_오라클_v1\|SPD원장_오라클_v1]] | WIP | v1 초안 — **오너 S1 검증 대기**. |
| [[features/전투완성/raw/광폭화_재검증\|광폭화_재검증]] | PASS | F1 완료 — 30(유닛턴) 확정, F8 게이트 GO. |
| [[features/전투완성/raw/상태이상_카탈로그_밸런스\|상태이상_카탈로그_밸런스]] | SUPERSEDED | 초안 — 오너 신규 요구(스킬 stateEffect+확률 발동)의 수치/밸런스 축. |
| [[features/전투완성/raw/상태이상_타겟범위_설계안\|상태이상_타겟범위_설계안]] | SUPERSEDED | 초안 — 구조/상태머신 축. |
| [[features/전투완성/raw/상태이상_확정\|상태이상_확정]] | PASS | ★Director 확정 2026-07-14 — 상태이상+AoE SSOT. |
| [[features/전투완성/raw/스탯_전투공식_v1\|스탯_전투공식_v1]] | PASS | v1 — qa 검증 완료·A1 착수. |
| [[features/캐릭터시스템/raw/balance1_포지션킷_v0\|balance1_포지션킷_v0]] | PASS | 결재 완료(2026-07-18 · 오너 S3) — Q0 Spd 승격(조건부·시뮬 이월)/Q1 등급 3단 유지+N단계 확장성/Q2 직업 태그 흡수. |
| [[features/캐릭터시스템/raw/balance1_포지션킷_v1\|balance1_포지션킷_v1]] | PASS | 본설계 완료(2026-07-18) — 오너 S3 결재 반영. |
| [[features/캐릭터시스템/raw/모션연결_규칙안\|모션연결_규칙안]] | PASS | ★오너 확정(2026-07-13) — 안 B(느슨결합) 채택 + R1 완화=완드 4색 변형 활용. |

## 게이트 판정 (gate) (20)

| 문서 | status | 요약 |
|---|---|---|
| [[features/스킬연출구조/raw/A1_T1검증_및_트리거벽\|A1_T1검증_및_트리거벽]] | PASS | 부분 통과 — 정적 2건 PASS / 실증 3건 오너 이월 (자동 트리거 불가 확정) |
| [[features/스킬연출구조/raw/AT4-a_결과_2026-08-12\|AT4-a_결과_2026-08-12]] | PASS | ★AT4-a 완료 — BP_FxLabDummy 신설, FxLab Director 내장, PIE 실측 전량 PASS. |
| [[features/스킬연출구조/raw/AT4-b_결과_2026-08-12\|AT4-b_결과_2026-08-12]] | PASS | ★AT4-b 완료 — PlayCameraCut/STGDEFAULT/arcHeight 3건 전량 PIE 실측 PASS. |
| [[features/스킬연출구조/raw/AT4-pre_결과_2026-08-12\|AT4-pre_결과_2026-08-12]] | PASS | ★AT4-pre 완료 — 5건 PASS / FXSHOW 갈래 (b) 배제 / T1 대조쌍 실재 확인 |
| [[features/스킬연출구조/raw/D4.5_판정\|D4.5_판정]] | PASS | D4.5 완료 — D5 착수 승인 |
| [[features/스킬연출구조/raw/D4_게이트판정\|D4_게이트판정]] | PASS | D4 PASS (조건부) — D4.5 착수 승인 |
| [[features/스킬연출구조/raw/D5_게이트판정\|D5_게이트판정]] | AWAIT_OWNER | D5 PASS — D5.5(오너 struct) 대기. |
| [[features/스킬연출구조/raw/E-S0_노드프로브_결과\|E-S0_노드프로브_결과]] | PASS | S0 완료 — 설계 전환(대역 액터) 확정 |
| [[features/스킬연출구조/raw/E-S1_레벨구축_결과\|E-S1_레벨구축_결과]] | PASS | S1 PASS — S2 착수 |
| [[features/스킬연출구조/raw/E0_에이전트피드백_Director판정\|E0_에이전트피드백_Director판정]] | PASS | 판정 완료 — E-S0 착수 |
| [[features/스킬연출구조/raw/FT1-S1_조회결과_2026-08-13\|FT1-S1_조회결과_2026-08-13]] | PASS | S1 조회 프로브 완료 — 조회 전용(F0p-04 예외 1건만 연결+즉시원복). |
| [[features/스킬연출구조/raw/T1_잔상절단_결과\|T1_잔상절단_결과]] | WIP | 구현 완료 — verifier 실증 대기 / 오너 육안 비차단 대기. |
| [[features/스킬연출구조/raw/내장트레일_director판정\|내장트레일_director판정]] | PASS | director 판정 완료 — T0 착수 가능 / T1은 오너 게이트 |
| [[features/스킬연출구조/raw/내장트레일_채택_오너판정\|내장트레일_채택_오너판정]] | PASS | 오너 판정 완료 — 내장 트레일 채택, legacy Smear 제거 방향 |
| [[features/전투완성/raw/AU-A1-09_T1전후_실측대조\|AU-A1-09_T1전후_실측대조]] | PASS | ★AU-A1-09 PASS — T1 Δ=0.000 실측 확정 / 부산물로 천단위쉼표 함정 발견·차단 |
| [[features/전투완성/raw/BP정리_Director판정_2026-08-11\|BP정리_Director판정_2026-08-11]] | PASS | 판정 완료 — D6 착수 전 필독 |
| [[features/전투완성/raw/BT-PLAN검증_2026-08-13\|BT-PLAN검증_2026-08-13]] | PASS | director 전체 plan 재검증(오너 지시 2026-08-13) — ①골격 A1~A8 유효(구조 변경 0) ②진척 어긋남 8건(스테일3·오진1·누락3·교착1) — 핵심: 'FT8 TC 없음'은 오진, 실체는 FT 번호 4단계 오프셋 ③1순위 = FT1 착수(선행: FT 번호 정합) ④신규 위험: A2-B/S 약칭 재충돌·CSV 린트 실물 0 |
| [[features/전투완성/raw/BT5_S1봉인수단_판별\|BT5_S1봉인수단_판별]] | AWAIT_OWNER | ★(c) 확정 — 오너 20턴 런 필요. |
| [[features/전투완성/raw/턴길이_실측확정_2026-08-12\|턴길이_실측확정_2026-08-12]] | PASS | ★확정 — H18 블록 부재 / T1 턴길이 Δ=0 / SlotBudgetSec 기준선 2.100s |
| [[features/전투완성/raw/턴예산_balance판정_2026-08-12\|턴예산_balance판정_2026-08-12]] | PASS | balance 판정 — 제3안. |

## 테스트/TC (test) (7)

| 문서 | status | 요약 |
|---|---|---|
| [[features/걸어나오기연출/TC\|TC]] | ARCHIVED | W1 8/8 통과, W2 4/4 판정 완료(3 통과+1 부분통과/명세편차 발견), W3 부분 판정(3/8 PASS + 5/8 이월/정적보증)(※ 분모 8 = 전 9항목 중 WT-22 "미실시" 제외. |
| [[features/공격버튼데모/raw/D3_게이트기록\|D3_게이트기록]] |  | 실행: verifier(haiku, Phase A/B) + Director(Windows 실클릭). |
| [[features/스킬연출구조/raw/D3_TC_확정\|D3_TC_확정]] | PASS | TC 확정 — D4 게이트 대기 |
| [[features/스킬연출구조/raw/E_TC\|E_TC]] | WIP | TC 확정 — E-S0 진행 중 |
| [[features/스킬연출구조/raw/FT1-0_TC\|FT1-0_TC]] | WIP | 신설 — TC 20건 설계 완료 / 적대 검토 15건(Critical 1 · High 6) / ★실행 불가 판정 2건(sid 생성수단 · 0b·0c 오너세션 미할당) |
| [[features/스킬연출구조/raw/자율진행_TC\|자율진행_TC]] | DRAFT | TC 초판 — plan v1(초안) 대상. |
| [[features/턴제전투MVP/TC\|TC]] | ARCHIVED | E3 자가검증 완료 (verifier 실증 대기) — [director 판정] E3 실증 미완인 채 동결 |

## 리뷰/QA (review) (16)

| 문서 | status | 요약 |
|---|---|---|
| [[codex/Codex_전체_읽기전용_리뷰_2026-07-16\|Codex_전체_읽기전용_리뷰_2026-07-16]] | PASS | complete_with_concurrent_commit_and_blueprint_graph_limitation |
| [[codex/review_2026-07-16_F7b_bootstrap_source_control\|review_2026-07-16_F7b_bootstrap_source_control]] | DRAFT | provisional |
| [[codex/UE5.8_projectTP\|UE5.8_projectTP]] | WIP | 상위: [[projectTP_허브]] · 계획: [[UE5.8_Codex_학습계획]] · 근거 카탈로그: [[언리얼5.8_기술카탈로그]] |
| [[features/HD2D배경/raw/목업_유효범위_판정\|목업_유효범위_판정]] | PASS | 판정 완료 (qa-critic, 2026-07-31) — 목업 관련 모든 문서·보고에 §경고문구 필수 첨부 |
| [[features/전투완성/raw/F4_TC\|F4_TC]] | PASS | TC 확정 — 개발 착수 전 BLOCKER 5건 Director 판정 필요 — [director 판정] 'BLOCKER 5건 판정 필요'는 스테일 — 판정 완료·F4 통과 |
| [[features/전투완성/raw/F5_TC\|F5_TC]] | PASS | TC 확정 — 개발 착수 전 BLOCKER 5건 Director 판정 필요 — [director 판정] 동(BLOCKER 판정 완료) |
| [[features/전투완성/raw/F7_TC\|F7_TC]] | PASS | TC 확정 — Director BLOCKER 5건 게이트 판정 반영. |
| [[features/전투완성/raw/qa_스탯공식검토\|qa_스탯공식검토]] | PASS | v1 적대적 검토 완료 — 게이트 통과(조건부 GO). |
| [[features/전투완성/raw/U단계_TC\|U단계_TC]] | PASS | TC 확정 대기 — [director 판정] '확정 대기'는 스테일 |
| [[features/전투완성/raw/상태이상_설계_qa검증\|상태이상_설계_qa검증]] | PASS | 검증 — 상태이상·AoE 병합안 적대적 논리검증. |
| [[features/전투완성/raw/야간큐_TC\|야간큐_TC]] | PASS | 4건 전부 게이트 완료 — 상태 컬럼 갱신 완료(각 완료 문서 판정대로). |
| [[features/전투완성/raw/파트1_Start_TC\|파트1_Start_TC]] | PASS | 게이트 PASS 2026-07-16 23시경 — ~~TC 46건 verifier 실행 완료~~ → ❌ **2026-08-11 정정**(frontmatter 자기모순 — 바로 다음 문장이 R01 이월을 밝힘): **46건 중 T1 실증+오너육안 5건(P1-V01~05)+GRAPH 일부 핀검증(Director 직접검증)으로 게이트 PASS**, P1-R01(… |
| [[features/전투완성/raw/파트2_SPD_TC\|파트2_SPD_TC]] | PASS | 핵심 게이트 PASS 2026-07-17 00시경 — 41건(GRAPH 17·PIE 11·회귀 9·데이터 4) 중 **10건 Director 직접 실행·전부 PASS**: GRAPH 5/5(P2-G01·G02·G03·G04·G07, 본 문서 §7이 지목한 "서브에이전트 보고 불인정" 5곳 전부)+보너스 2건(P2-G05·G09) + ★★★최강게이트 P2-… |
| [[features/전투완성/raw/파트3_연출_TC\|파트3_연출_TC]] | PASS | 핵심 게이트 PASS 2026-07-17 01시경 — 38건(GRAPH 18·PIE 11·회귀 9) 중 **6건 Director 직접 실행·전부 PASS**: GRAPH 6/6(P3-G01·G02·G03·G04·G05·G06, 본 문서가 지목한 ★★★/★★ 최우선 6곳 전부). |
| [[features/전투완성/raw/파트4_라벨힐_TC\|파트4_라벨힐_TC]] | PASS | 게이트 PASS(Director, 2026-07-17) — 오너 육안 4항목 PASS + Director 핀검증(작업1 라벨 GRAPH 8건) PASS + P4C-15(런타임조인 8기) PASS + 컴파일0·디스크저장 실증. |
| [[records/로그시스템_점검_2026-08-12\|로그시스템_점검_2026-08-12]] | PASS | 점검 완료 — 구현 없음(발주 대기). |

## 기록·로그 (record) (86)

| 문서 | status | 요약 |
|---|---|---|
| [[codex/Codex_Unreal_MCP_연결\|Codex_Unreal_MCP_연결]] | PASS | configured_and_endpoint_verified |
| [[features/HD2D배경/raw/2D배경_기각_교훈_2026-08-10\|2D배경_기각_교훈_2026-08-10]] | ARCHIVED | 종결 — 오너 기각(2026-08-10). |
| [[features/HD2D배경/raw/목업_결과_요약_2026-07-31\|목업_결과_요약_2026-07-31]] | ARCHIVED | 오프라인 목업 트랙 종료 — 답할 수 있는 것은 다 답했고, 나머지는 엔진 몫 |
| [[features/UI파이프라인/raw/A0_UMG스파이크\|A0_UMG스파이크]] |  | 알파의 메뉴 UI(대기실 등) 전량을 UMG WidgetBlueprint로 만들 계획(`알파_개발계획.md` §2.6①)인데, 이 프로젝트는 UMG를 한 번도 안 써봤고 MCP 툴셋 목록에 Widget/UMG 전용 툴셋이 안 보인다는 Director 리컨을 실증하는 A0 스파이크. |
| [[features/걸어나오기연출/raw/W1_구현\|W1_구현]] |  | projectTP/걸어나오기연출 |
| [[features/걸어나오기연출/raw/W2_Executing개편\|W2_Executing개편]] |  | projectTP/걸어나오기연출 |
| [[features/걸어나오기연출/raw/W3fix_회전보간\|W3fix_회전보간]] |  | projectTP/걸어나오기연출 |
| [[features/걸어나오기연출/raw/공중부양_수정\|공중부양_수정]] | PASS | 완료 — 오너 육안 확인까지 통과(발이 바닥에 닿음). |
| [[features/공격버튼데모/raw/D1_TimeOffset\|D1_TimeOffset]] | PASS | 0. |
| [[features/기본전투무대/raw/P1_레시피_idle조사\|P1_레시피_idle조사]] | PASS | 조사 전용 산출물. |
| [[features/기본전투무대/raw/P1_무대_배치조사\|P1_무대_배치조사]] | PASS | 조사 전용 산출물. |
| [[features/기본전투무대/raw/P2_TC설계\|P2_TC설계]] | PASS | 적대적 QA 관점. |
| [[features/기본전투무대/raw/S1_합성결과\|S1_합성결과]] | PASS | 사용 스크립트: [[compose_party.py]] · 레시피 소스: [[P1_레시피_idle조사]] · 상위: [[features/기본전투무대/plan\|plan]] |
| [[features/기본전투무대/raw/S2_임포트머티리얼\|S2_임포트머티리얼]] | PASS | 상위: [[features/기본전투무대/plan\|plan]] · 선행: [[S1_합성결과]] |
| [[features/기본전투무대/raw/S3_글리치수정\|S3_글리치수정]] | ARCHIVED | 기각 (TSR 오진 — 근본원인은 S5에서 별도 규명, 공면 z-fight) |
| [[features/기본전투무대/raw/S3_무대배치\|S3_무대배치]] | PASS | 완료(경고 있음) |
| [[features/기본전투무대/raw/S4_애니검증\|S4_애니검증]] |  | 목적 |
| [[features/기본전투무대/raw/S5_룩패스\|S5_룩패스]] | PASS | 완료 (룩 패스만 — 글리치는 이후 S5 Fable 조사로 근본원인 규명·해결, 진행로그 참고) |
| [[features/기본전투무대/진행로그\|진행로그]] | PASS | 완료 (F풀테스트 잔여) |
| [[features/스킬연출구조/raw/AT4-b-2_결과_2026-08-12\|AT4-b-2_결과_2026-08-12]] | PASS | ★작업1 완료 — FXSHOW 0건의 진짜 원인 확정(경로 실행 아님, DT_Vfx.texPath 포맷 결함). |
| [[features/스킬연출구조/raw/AT트랙_세션기록_2026-08-12\|AT트랙_세션기록_2026-08-12]] | PASS | ★하루치 전체 기록 — AT4-pre~AT4-b-2 완료, FXSHOW 0건 원인 확정, 오독 3건·PM 오판 3건·인증만료 사고 1건 정리 |
| [[features/스킬연출구조/raw/B4_찌르기형_후보실측\|B4_찌르기형_후보실측]] | PASS | 완료 — plan 피드백 2건 + 후보 실측 1건 추천 |
| [[features/스킬연출구조/raw/D4.5a_VFX재고_실측\|D4.5a_VFX재고_실측]] | PASS | 실측 완료 — D4.5 행 배정 대기 |
| [[features/스킬연출구조/raw/D4.5b_VFX행배정\|D4.5b_VFX행배정]] | PASS | D4.5-b 산출 — D5 대기 |
| [[features/스킬연출구조/raw/DT_Vfx_texPath보정_2026-08-12\|DT_Vfx_texPath보정_2026-08-12]] | PASS | ★완료 — 5행 서픽스 보정 + FXSHOW 5/5 실측 PASS. |
| [[features/스킬연출구조/raw/E-S2_FxLabQuad_결과\|E-S2_FxLabQuad_결과]] | PASS | 부분 통과 — 구현·fail-loud PASS / 타이밍 5건 미실증(원인=환경, 규명 완료) |
| [[features/스킬연출구조/raw/E-S2_틱스로틀_진단\|E-S2_틱스로틀_진단]] | PASS | 원인 확정 — bThrottleCPUWhenNotForeground 기본값(true) 미적용 상태 |
| [[features/스킬연출구조/raw/E-S4a-0_struct자동화_조사결과\|E-S4a-0_struct자동화_조사결과]] | PASS | 판정 B(조건부 가능) — 스크립트 경로 채택, 결함 2건 수정 선행 |
| [[features/스킬연출구조/raw/E-S4a_오너_실행절차\|E-S4a_오너_실행절차]] | PASS | ★완료(2026-08-12, Content 저장소 커밋 `9c3934d`) — 단 검증은 스팟(전수 아님). |
| [[features/옥토패스대치/raw/P0_상속스냅샷\|P0_상속스냅샷]] |  | 상위: [[../청사진\|옥토패스대치 청사진]] |
| [[features/옥토패스대치/raw/P1_좌표카메라설계\|P1_좌표카메라설계]] |  | 상위: [[../청사진\|옥토패스대치 청사진]] · 전 단계: [[P0_상속스냅샷\|P0 상속스냅샷]] |
| [[features/옥토패스대치/raw/P2_TC설계\|P2_TC설계]] |  | 상위: [[../청사진\|옥토패스대치 청사진]] · plan: [[../plan]] · 프로세스: [[../../../guides/개발_워크플로우]] |
| [[features/옥토패스대치/raw/S1_flip구현\|S1_flip구현]] |  | 상위: [[../plan\|옥토패스대치 plan]] §1·§2 명세 그대로 구현. |
| [[features/옥토패스대치/raw/S2_사선배치\|S2_사선배치]] |  | 상위: [[../청사진\|옥토패스대치 청사진]] · 전 단계: [[P1_좌표카메라설계\|P1 좌표·카메라 설계]] |
| [[features/옥토패스대치/raw/S2p_초기배치백업\|S2p_초기배치백업]] |  | T1(BP 구현) + T2(8기 교체) 완료 시점 기록. |
| [[features/옥토패스대치/raw/S3_룩패스\|S3_룩패스]] |  | 상위: [[../청사진\|옥토패스대치 청사진]] · 전 단계: [[S2_사선배치\|S2 사선 배치]] |
| [[features/옥토패스대치/raw/T1T2_BP구현\|T1T2_BP구현]] |  | gameplay-engineer 구현 로그. |
| [[features/옥토패스대치/raw/나무제거_백업\|나무제거_백업]] | PASS | 기록 |
| [[features/옥토패스대치/raw/배치_1\|배치_1]] | PASS | 승인 |
| [[features/전투완성/raw/F3_HP게이지_수정전스냅샷\|F3_HP게이지_수정전스냅샷]] |  | Director가 오너 라이브 확인에서 "HP 게이지 안 보임"을 직접 MCP로 진단(2026-07-14). |
| [[features/전투완성/raw/F3_사전스냅샷\|F3_사전스냅샷]] |  | `JobId` 변수 신설 + 컴파일 + 8기 값 세팅 착수 직전 시점 기록(TC-F3-03 드리프트=0 대조용 롤백 지점). |
| [[features/전투완성/raw/F4_중단_인수인계\|F4_중단_인수인계]] | ARCHIVED | ~~F4 개발 완료(디스크 저장됨) / 에디터 메모리 손상 → 재시작 필요 / 베기 검증 1건 미완~~ → ❌ **2026-08-11 정정**(frontmatter가 인수인계 시점에서 멈춰 본문의 후속 완료 기록과 불일치): **F4 완료(베기검증 포함, dmg=42/46 PASS) — F5-1 정정까지 반영**(§4 원복 누락→쿨다운 가드 정지 버그 해… |
| [[features/전투완성/raw/F5-1_완료\|F5-1_완료]] | PASS | 게이트 통과 — 사망·승패 판정 정상 동작 확인(PIE 실증+오너 육안). |
| [[features/전투완성/raw/F5-2_TC\|F5-2_TC]] | PASS | TC 확정 — ~~착수 대기(F5-1 게이트 통과가 선행, 완료됨). |
| [[features/전투완성/raw/F5-2_완료\|F5-2_완료]] | PASS | 게이트 통과 — 죽은 유닛 처리(턴스킵·DYING·ClickBox·ResetForBattle) + 스킵 즉시화. |
| [[features/전투완성/raw/F5_착수지시서\|F5_착수지시서]] | ARCHIVED | 착수 대기 (에디터 재시작 + F4 베기검증 통과가 선행 조건) — [director 판정] '착수 대기'는 스테일 — F5 완료 |
| [[features/전투완성/raw/F7b_struct부트스트랩_완료\|F7b_struct부트스트랩_완료]] | PASS | 완료 2026-07-16(오너 승인 설치) |
| [[features/전투완성/raw/F7b_인터프리터_진행상황_인계\|F7b_인터프리터_진행상황_인계]] | WIP | 진행중(골격 완료, 애플리케이터 수술 대기) |
| [[features/전투완성/raw/FT1_착수조회_2026-08-12\|FT1_착수조회_2026-08-12]] | PASS | 조회 완료 — 수정 0건. |
| [[features/전투완성/raw/U단계_HP게이지_UMG_실장\|U단계_HP게이지_UMG_실장]] | PASS | 완료 — F3(HP 게이지) 완결. |
| [[features/전투완성/raw/WBP_BattleHUD_골격생성_착수전스냅샷\|WBP_BattleHUD_골격생성_착수전스냅샷]] |  | gameplay-engineer가 `Resource/ui/battle/WBP_BattleHUD/spec.md`(WBP_BattleHUD spec) §0/§B 파이프라인 3단계(골격 생성) 착수 전 기록. |
| [[features/전투완성/raw/야간F6_모션데이터구동_완료\|야간F6_모션데이터구동_완료]] | PASS | 게이트 PASS 2026-07-16 야간 |
| [[features/전투완성/raw/야간F7a_스킬메뉴_완료\|야간F7a_스킬메뉴_완료]] | PASS | 게이트 PASS 2026-07-16 야간 |
| [[features/전투완성/raw/야간F8_광폭화_완료\|야간F8_광폭화_완료]] | PASS | 게이트 PASS 2026-07-16 야간 |
| [[features/전투완성/raw/야간F9a_풀회귀_완료\|야간F9a_풀회귀_완료]] | PASS | 게이트 PASS 2026-07-16 |
| [[features/전투완성/raw/야간③_데미지폰트_완료\|야간③_데미지폰트_완료]] | PASS | 게이트 PASS 2026-07-16 야간 |
| [[features/전투완성/raw/야간③b_데미지폰트_위치수정_완료\|야간③b_데미지폰트_위치수정_완료]] | PASS | 게이트 PASS 2026-07-16 |
| [[features/전투완성/raw/야간④_End버튼_완료\|야간④_End버튼_완료]] | PASS | 게이트 PASS 2026-07-16 야간 |
| [[features/전투완성/raw/야간⑤_로그보강_완료\|야간⑤_로그보강_완료]] | PASS | 게이트 PASS 2026-07-16 야간 |
| [[features/전투완성/raw/야간작업_총결산_2026-07-16\|야간작업_총결산_2026-07-16]] | PASS | 야간 세션 7단계 게이트 전부 완료(③~F9a). |
| [[features/전투완성/raw/전진로직_실체_확정\|전진로직_실체_확정]] | PASS | 조회 완료 — 수정 0건. |
| [[features/전투완성/raw/턴표시_완료\|턴표시_완료]] | PASS | 게이트 PASS 2026-07-18(PIE 블로커 해소 후 재개·완료) |
| [[features/전투완성/raw/파트1_Start_진행\|파트1_Start_진행]] | PASS | 게이트 PASS 2026-07-16 23시경(파트1 완료) — Director 직접검증(GRAPH 핀 원문)·자산·PIE·오너 육안 5항목·T1 실증 전부 PASS. |
| [[features/전투완성/raw/파트2_SPD_완료\|파트2_SPD_완료]] | PASS | 핵심 게이트 PASS 2026-07-17 00시경 — Director 직접검증 GRAPH 5/5(P2-G01·G02·G03·G04·G07) + 보너스 2건(P2-G05·G09) PASS. |
| [[features/전투완성/raw/파트3_연출_완료\|파트3_연출_완료]] | PASS | 핵심 게이트 PASS 2026-07-17 01시경 — qa-critic 착수 전 검출(계획서 5건 중 3건이 명세대로면 미작동 확정, 신규발견 N0~N13 14건)+Director 결정 3건(Target 조달=게이팅 전용 DT 조회 신설·카메라=OR조건 보존·치유잔상=motions.csv 데이터 수정) 채택 후 구현. |
| [[features/전투완성/raw/파트4_라벨힐_완료\|파트4_라벨힐_완료]] | PASS | 게이트 PASS(Director, 2026-07-17) — 오너 육안 4항목 전부 PASS(①메뉴 라벨 형태+턴마다 갱신 ②치유 제자리 casting+`+33`초록 ③만피 치유 `+0`초록 ④회귀 3종: 막기제자리/공격걸어나감/빨간데미지) + Director 직접 핀검증 PASS(작업1 라벨 FormatText 체인 8건: 인자 핀 실생성·인자0/1 소스… |
| [[features/카메라액션/raw/C1_구현\|C1_구현]] |  | projectTP/카메라액션 |
| [[features/카메라액션/raw/V1_철거\|V1_철거]] |  | projectTP/카메라액션 |
| [[features/카메라액션/raw/V2_구축\|V2_구축]] |  | projectTP/카메라액션 |
| [[features/카메라액션/raw/V3_게이트\|V3_게이트]] |  | projectTP/카메라액션 |
| [[features/카메라액션/raw/VF_빌보딩\|VF_빌보딩]] |  | projectTP/카메라액션 |
| [[features/카메라액션/raw/VF_토글버튼\|VF_토글버튼]] |  | projectTP/카메라액션 |
| [[features/캐릭터시스템/raw/A0_CSV파이프라인스파이크\|A0_CSV파이프라인스파이크]] |  | `Resource/data/strings.csv`(git 추적)를 UE DataTable로 임포트하고 런타임 조회가 가능한지 확인하는 A0 스파이크. |
| [[features/캐릭터시스템/raw/A0_합성머티리얼스파이크\|A0_합성머티리얼스파이크]] |  | heroes99 파츠(skin/face/hair/cloth/weapon) 5레이어를 런타임에 겹쳐 그리는 합성 머티리얼(`M_Sprite_PartComposite`)이 되는지 실증하는 A0① 스파이크. |
| [[features/캐릭터시스템/raw/파츠_인벤토리\|파츠_인벤토리]] |  | UE 작업 없음. |
| [[features/캐릭터시스템/raw/파츠모션_실태조사\|파츠모션_실태조사]] |  | 목적: 전투 구현(A1) 착수 전 "캐릭터 리소스 조합 · 스킬 모션 조합의 연결 규칙"을 결정하는 데 필요한 사실관계만 정리한다. |
| [[features/턴제전투MVP/raw/E0_프로브\|E0_프로브]] |  | 상위: [[../plan\|턴제전투MVP plan]] · [[../청사진\|청사진]] |
| [[features/턴제전투MVP/raw/E1_유닛확장\|E1_유닛확장]] |  | 상위: [[../plan\|턴제전투MVP plan]] · [[../청사진\|청사진]] |
| [[features/턴제전투MVP/raw/E2_상태머신\|E2_상태머신]] |  | 상위: [[../plan\|턴제전투MVP plan]] · [[../청사진\|청사진]] · 선행: [[E1_유닛확장]] |
| [[features/턴제전투MVP/raw/E3_게이트\|E3_게이트]] |  | 상위: [[../plan\|턴제전투MVP plan]] · [[../청사진\|청사진]] · 선행: [[E2_상태머신]] |
| [[features/턴제전투MVP/raw/F_라이브결함\|F_라이브결함]] |  | 상위: [[../plan\|턴제전투MVP plan]] · [[../청사진\|청사진]] · 선행: [[E3_게이트]] |
| [[features/턴제전투MVP/raw/전투로그\|전투로그]] |  | 상위: [[../plan\|턴제전투MVP plan]] · [[../청사진\|청사진]] |
| [[records/야간작업_2026-08-12\|야간작업_2026-08-12]] | AWAIT_OWNER | 완료 — 오너 확인 대기 |
| [[records/야간작업_2026-08-13\|야간작업_2026-08-13]] | PASS | 문서구조 개선 1~6·9·10단계 완료. |
| [[records/작업로그_HD2D아트검증_플레이북\|작업로그_HD2D아트검증_플레이북]] |  | 목적: 이번 S0(아트 선검증) 전 과정을 **재현 가능하게** 기록. |
| [[records/포트폴리오_projectTP\|포트폴리오_projectTP]] |  | 사용법: `---`가 슬라이드 구분선입니다. |

## 인덱스/허브 (index) (4)

| 문서 | status | 요약 |
|---|---|---|
| [[features/스킬연출구조/_기능허브\|_기능허브]] | PASS | 설계 완료 — 구현 대기 (★E단계 전제 재검토 중 — 아래 경고 참조) · ★AT4 전 구간(pre·a·b·b-2) 완료, AT5 대기(FT1 선행), AT6-a/b/c 보류(HOLD) |
| [[INDEX\|INDEX]] | PASS | docs/scripts/vaultfix/generate_index.py로 frontmatter에서 자동생성 — 손으로 편집하지 않는다 |
| [[projectTP_허브\|projectTP_허브]] |  | UE 5.8 HD-2D 정면 대치 배틀 프로젝트의 **문서 진입점(MOC)**. |
| [[오너_대기목록\|오너_대기목록]] | WIP | active — ★0군(일괄 확인 세션) 신설 · ★★2026-08-12 재갱신(director 6차 + 오너 승인) — 0군 #4(S1 20턴 런)의 성격이 "FT트랙 전체 차단 요인" → "사후 확인(비차단)"으로 강등, 0군 전체가 비차단임을 명시 — [director 판정] 상시 롤링 문서 |

## 참고자료 (reference) (18)

| 문서 | status | 요약 |
|---|---|---|
| [[codex/MVP_개발_핵심_운영가이드\|MVP_개발_핵심_운영가이드]] | WIP | 관련 전체 리뷰: [[Codex_전체_읽기전용_리뷰_2026-07-16]] |
| [[features/HD2D배경/raw/룩_지침_2D타일셋\|룩_지침_2D타일셋]] | ARCHIVED | 종결 — ❌ 2026-08-11 정정: 2026-08-10 오너 기각(전투 배경 3D 유지)으로 적용 대상 소멸. |
| [[features/HD2D배경/raw/오너_2D배경_튜닝가이드\|오너_2D배경_튜닝가이드]] | ARCHIVED | ~~배치 완료 — 라이팅/PP/색조 미적용, 오너 육안 확인 대기~~ → ❌ **2026-08-11 정정**: 오너 육안 확인 완료 — 기각(전투 배경은 3D 유지). |
| [[features/스킬연출구조/raw/D5.5_오너_struct세션_절차서\|D5.5_오너_struct세션_절차서]] | AWAIT_OWNER | 오너 실행 대기 — 진입 조건 1/2 충족 |
| [[features/옥토패스대치/배치가이드\|배치가이드]] | ARCHIVED | 활성 |
| [[features/전투완성/raw/전투BP_현황도_2026-08-11\|전투BP_현황도_2026-08-11]] | PASS | 라이브 실측 스냅샷 |
| [[reference/_RawAssets_전수카탈로그\|_RawAssets_전수카탈로그]] | WIP | `D:\unreal\Resource\_RawAssets\` 5개 폴더(heroes99·vfx·tilesets·ui-packs·_mockups) 전수 조사. |
| [[reference/HD2D_기법_지식베이스\|HD2D_기법_지식베이스]] |  | `hd2d-art-director` 에이전트의 상시 참조 문서. |
| [[reference/heroes99_스프라이트시트툴_조사\|heroes99_스프라이트시트툴_조사]] | WIP | 오너 단서: *"이 툴을 참고하면 좀 더 다양한 기능도 알 수 있을 거야."* (`https://yhkk.itch.io/heroes99-spritesheet-tool`) |
| [[reference/heroes99_에셋_전수탐색\|heroes99_에셋_전수탐색]] | WIP | 오너 질문에 대한 답을 찾기 위한 `_RawAssets` 전수 탐색. |
| [[reference/데이터규약_예시\|데이터규약_예시]] | SUPERSEDED | ~~예시 시드 — A0에서 공식 데이터 규약 문서로 승격 예정~~ → ❌ **2026-08-11 정정**: 승격 이미 완료 — [[데이터_서버_규약]] §4가 공식 규약 SSOT이고, 이 문서는 그 규약을 실데이터로 시연하는 상시 예시 컴패니언으로 역할 고정됨(더 이상 "승격 대기" 상태 아님) |
| [[reference/셋업가이드_새PC환경구축\|셋업가이드_새PC환경구축]] |  | 기존 PC에서 GitHub에 올린 projectTP를 다른 PC에서 동일하게 세팅하는 절차. |
| [[reference/셋업가이드_에디터MCP연결\|셋업가이드_에디터MCP연결]] |  | 목적: projectTP 에디터를 띄우고 Unreal MCP 서버를 기동해 **Claude가 에디터를 직접 조종**할 수 있게 한다. |
| [[reference/언리얼5.8_기술카탈로그\|언리얼5.8_기술카탈로그]] |  | UE 5.8 공식 문서를 폭넓게 읽고 **projectTP 스택에 실제로 닿는 것만** 골라 3분류한 참고 자료. |
| [[reference/언리얼_MCP_실전노하우\|언리얼_MCP_실전노하우]] |  | UE 5.8을 unreal-mcp로 조작하며 실제로 겪은 함정·해법·방법론. |
| [[reference/에셋_후보_카탈로그\|에셋_후보_카탈로그]] | PASS | 조사 기록 — 채택 아님. |
| [[reference/전투로그\|전투로그]] | PASS | LOG-A 완료 — 토큰 계약서 확정(문법·카테고리). |
| [[reference/카메라연출_원칙\|카메라연출_원칙]] |  | 카메라액션(공격 액션 컷) 설계 과정에서 확정된 기하 원칙. |

## 규약/프로세스 (process) (6)

| 문서 | status | 요약 |
|---|---|---|
| [[guides/UI_화면_규약\|UI_화면_규약]] |  | projectTP **방향성2(Steam 드래프트 단판 PvP)**의 전체 화면·UI 제작 규약. |
| [[guides/개발_워크플로우\|개발_워크플로우]] |  | projectTP 개발의 **정본 프로세스**. |
| [[guides/네이밍_폴더_규약\|네이밍_폴더_규약]] |  | projectTP 전 카테고리(**UE Content 애셋 · 레벨/맵 · CSV/데이터 · UI 디자인 파일 · 스크립트 · 문서 · Blueprint 내부 · 위젯 트리 · 액터/씬 인스턴스 · CSS 토큰**)의 **명명·폴더 규약 단일 출처**다. |
| [[guides/데이터_서버_규약\|데이터_서버_규약]] |  | projectTP의 **버전 무관 데이터·서버 아키텍처 규약**의 단일 출처 — CSV 데이터 전략·포맷 판단·데이터 드리븐 효과·서버 권위 범위·라이브옵스 원격 배송·CSV 컬럼 스키마. |
| [[guides/문서화_규칙\|문서화_규칙]] |  | 모든 작업 산출물·중간 기록을 이 볼트에 남기는 규칙. |
| [[guides/저장소_구조_규약\|저장소_구조_규약]] | PASS | 확정 — 저장소 배치의 단일 출처(SSOT). |

## (미분류) (4)

| 문서 | status | 요약 |
|---|---|---|
| [[features/공격버튼데모/raw/D2_구현\|D2_구현]] | 완료 — D3 게이트 통과 후 오너 리포트로 핫픽스(FrameCount 8→6, RetriggerableDelay 0.95→0.70s) 추가 반영, 컴파일/저장 확인, 오너 재확인 대기 | gameplay-engineer 구현 로그. |
| [[features/카메라액션/plan\|plan]] |  | 승인 원본: `C:\Users\user\.claude\plans\humble-purring-glacier.md`. |
| [[features/턴제전투MVP/raw/VFX_임시통합_방침\|VFX_임시통합_방침]] | 활성 (구조 재설계 전까지) | 오너 원문: "vfx는 나중에 구조를 다시 잡아야 하니까 여기선 **눈 구별 가는 정도만** 해도 됨." |
| [[scripts/README\|README]] |  | 여기서 무엇을 찾을 수 있는가** (AI는 이 4줄만 읽어도 판단 가능해야 한다): |

