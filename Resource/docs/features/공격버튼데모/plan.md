---
type: plan
feature: 공격버튼데모
status: 완료 (오너 라이브 확인 대기)
updated: 2026-07-06
---

# 📋 공격버튼데모 plan (승인판 요약)

> 옥토패스대치 진행 중 오너 요청으로 끼어든 빠른 데모. 원본 승인 plan: 세션 plan 파일(피드백 3건 통합판). 상위: [[../옥토패스대치/plan|옥토패스대치]]
#projectTP/공격버튼데모

## 목표
PIE에서 화면 하단 "Attack" 버튼 클릭 → **A1이 ATTACK1(Row5, 실측 6프레임) frame0부터 1회(0.70s) 재생 후 idle 복귀**. 아군 1기만, 빠른 데모 성격(오너 확정).
> ⚠ 핫픽스(오너 깜빡임 리포트): 팩 가이드의 "ATTACK1=8프레임"은 오표기 — **시트 알파 실측 = ATK1 6f / ATK2 6f / ATK3 4f (8종 공통)**. FrameCount 8→6, 타이머 0.95→0.70s로 수정(투명 셀 렌더 제거).

## 핵심 설계 (검수 실증 완료)
- 텍스처는 이미 17행 전체 시트 — **ATTACK1=Row5, 8f**. 합성 불필요.
- 마스터에 `TimeOffset`(기본 0) 추가: `floor((Time−TimeOffset)×FPS) mod FrameCount` — Time_0 유일 소비처=Multiply_0.A 실증, 삽입 1곳.
- 파라미터 실명: `RowIndex, FrameCount, FPS, TimeOffset, FlipX` — SetScalarParameterValue는 오철자 **무음 무시** 함정.
- UMG Designer MCP 불가 → **월드공간 버튼 액터**(BP_AttackButton: Plane+TextRender+Box클릭). 카메라는 `autoActivateForPlayer=Player0`.
- BP_BattleSpawnPoint는 **CS 무변경**, BeginPlay에서 MID 생성 + `PlayAttack`/`RevertToIdle` 이벤트. 리스타트=**Retriggerable Delay 0.95s**(1안).
- SetScalar 순서 고정: TimeOffset → FrameCount → RowIndex(마지막). 복귀 위상 점프 1회는 **수용 명세**.

## 단계
| 단계 | 내용 | 담당 | 모델 | 상태 |
|---|---|---|---|---|
| D1 | 마스터 TimeOffset(8스텝 절차)+MI 상속·village 렌더 회귀 | art-pipeline | sonnet | 완료 |
| D2 | BP 2종+스트링테이블+레벨 배선+문서 반영 | gameplay-engineer | sonnet | 완료 — ⚠ Label(TextRenderComponent) 에디터 뷰포트 미표시 발견, PIE 실증 필요(D2_구현.md 함정5) |
| D3 | 게이트: PIE 실클릭 실증+에디터/village 회귀 | verifier+Director(클릭) | haiku | **완료 — 10/10 PASS** ([[raw/D3_게이트기록]]. 복귀"결함"은 idle 기준 오판으로 정정, Label은 회전+LOCTABLE로 해결) |

## TC 미니 목록
TimeOffset 기본0 회귀 / 공격 frame0 시작 / SetScalar 순서 / 0.95s 랩 팝 금지 / 재클릭 리스타트 / 복귀 위상 점프=수용 / null 가드 3종 / CS 무변경·배치도구 회귀 / village 무오염 / 스트링테이블 키(`ST_UI` `Battle.Attack`).

## 비범위
데미지·타겟팅·턴 로직 / 나머지 7기 / 애니 시스템 구조화 / 위상 점프 완화 / 공격 FPS 튜닝(오너 체감 후) / 배치 T4·F는 별도 진행.

## 이월·간섭 표기
- 배치가이드에 "UI_AttackButton 건드리지 말 것" 추가(D2⑤).
- 옥토패스대치 T4/F는 버튼 액터·마스터 TimeOffset·카메라 autoActivate 존재를 인지하고 검증(TC-29 범위 갱신).
