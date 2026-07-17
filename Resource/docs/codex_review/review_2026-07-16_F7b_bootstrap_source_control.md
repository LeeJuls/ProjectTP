---
type: codex_review_mirror
project: projectTP
target: F7b bootstrap and Blueprint source-control boundary
canonical: D:\unreal\review_agent\review_2026-07-16_F7b_bootstrap_source_control.md
mode: read_only
status: provisional
reviewed_head: fa3527ab83298f180df755c50b3d526540d613be
model_match_scope: blueprint_functional_pass_fail
created: 2026-07-16
---

# F7b bootstrap and Blueprint source-control review

> 이 문서는 Obsidian 기록용 요약본이다. 상세 finding과 근거의 정본은 `D:\unreal\review_agent\review_2026-07-16_F7b_bootstrap_source_control.md`다.

## Review result

- P0: 0
- P1: 2
- P2: 2
- P3: 1
- 소스 수정: 없음
- 최종 승인: 보류. 실제 모델 설정과 Blueprint 그래프 diff를 확인할 수 없어 이번 결과는 텍스트 코드·Git·설정·로그 기준의 provisional review다.
- 모델 조건: 모델 일치는 Blueprint 기능의 최종 pass/fail에만 필요하다. 아래 P1/P2/P3와 차단 범위는 로컬 증거로 확정된다.
- 차단 범위: 기능 개발 전체가 아니라, 현재 Git 커밋·태그를 Blueprint 구현 백업·정확한 롤백·diff 리뷰 기준으로 신뢰하는 것을 차단한다.

## Findings

1. **CR-20260716-001 / P1 — Blueprint 구현이 Git 커밋에 없음**: `D:\unreal\.gitignore:29`가 `/projectTP/Content/` 전체를 제외한다. `cc1d91d`, `0ca6b71` 완료 커밋에는 실제 Blueprint·DataTable 에셋이 포함되지 않아 diff 리뷰·정확한 롤백·새 PC 재현이 불가능하다.
2. **CR-20260716-002 / P1 — 구조체 부트스트랩 코드가 미추적**: `Content/Python/init_unreal.py`가 구조체 생성의 유일한 실행 코드인데 저장소 밖에 있다. 완료 문서의 재현 절차도 이 파일이 이미 존재한다고 전제한다.
3. **CR-20260716-003 / P2 — 부분 완료를 전체 완료로 오인**: `init_unreal.py:143`, `:364`는 `F_StatusEffectRow` 하나만 존재해도 나머지 구조체 생성과 확장을 전부 건너뛴다.
4. **CR-20260716-004 / P2 — 잘못된 필드 rename 가능성**: `init_unreal.py:246-262`는 변수 목록의 마지막 항목을 방금 추가한 필드로 가정한다. 반환 순서가 달라지면 다른 필드 이름을 바꿀 수 있다.
5. **CR-20260716-005 / P3 — 코드 머리말 상태가 실제와 반대**: 스크립트는 아직 미실행·플러그인 비활성이라고 설명하지만, 현재 두 플러그인은 활성이고 부트스트랩은 완료됐다. `projectTP.log:2068`에서 startup script 실행도 확인됐다.

## Owner decision required

유료 외부 에셋은 제외한 채 first-party Blueprint·DataTable·UI·맵을 어떤 저장소로 관리할지 결정해야 한다. Git LFS·Perforce 등은 저장 용량, 잠금, 비용, 최초 반입 절차를 비교해 선택하고, 그 전에는 `Content/` 전체를 무작정 추적하지 않는다.

## Next review gate

F7b의 `ApplyEffectEntry` 실배선과 `EnterExecuting → ApplySkillEffects` 전환 직후 다음 리뷰를 수행한다. 필요한 증거는 Blueprint 그래프/핀 보고서, 컴파일 결과, 5스킬 E2E 결과, 23턴 원장 회귀 로그다.
