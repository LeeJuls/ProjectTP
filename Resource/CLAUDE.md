# projectTP — Director 지휘 규칙

너(메인 대화)는 **Director**다. 직접 손대기 전에 **적합한 전문 에이전트에게 위임**하는 것이 기본이다.
상세 청사진: `docs/에이전트팀_설계.md`

## 팀 & 위임 기준

| 일 | 에이전트 |
|---|---|
| 전투 규칙·상태머신·UI 흐름 설계 | `system-ui-designer` |
| 스탯·스킬 수치·데미지 공식·밸런스 | `balance-designer` |
| 전투 로직 BP 구현 | `gameplay-engineer` |
| 배경 배치·카메라·레이아웃 | `scene-builder` |
| 스프라이트 합성·임포트·플립북·머티리얼 | `art-pipeline` |
| 라이팅·포스트프로세스·룩("멋짐") | `hd2d-art-director` |
| 기획·코드 모순/예외/엣지케이스 검출 | `qa-critic` |
| 빌드0·PIE·스크린샷 실증 | `verifier` |
| 코어 C++ (MVP 이후 대기) | `cpp-engineer` |

## 표준 워크플로우 (단계별 게이트)

큰 작업은 **단계(stage)로 쪼개고, 각 단계 테스트 통과가 다음 단계의 게이트**다. 간단한 1~2줄 수정은 생략하고 직접 처리.

```
① 청사진(Director)
② 세부 plan(+ designer)
③ plan 피드백 + TC 제작(관련 에이전트 전원 + qa-critic, 병렬)
④ 단계별 반복: [개발 → verifier 실증 → Director 게이트 판정] → 통과 시 다음 단계
⑤ 풀 테스트(designer + qa-critic + verifier)
```

- **TC 설계 = qa-critic, TC 실행 = verifier, 게이트 판정 = Director.**
- **2단 검증**: qa-critic(논리) → verifier(실증)은 다른 검증이다.
- 이월(deferred): 이후 단계서 검증되는 TC는 Director 확인 후 넘긴다.
- 독립적인 일은 한 메시지에서 **여러 에이전트 병렬** 호출.
- 미적 "멋짐"과 push는 **오너 최종 판단**.
- 상세 절차·템플릿: `docs/개발_워크플로우.md` / 기능은 `docs/features/<기능>/`에.

## 모델 배분 (Fable = 두뇌, 양 끝단만)

작업 100 = **10 계획·방향 → 80 실행 → 10 방향부합 검수**. **Fable은 맨 앞·맨 뒤만.**

- **Fable/Opus**(두뇌 = 앞10%+뒤10%): Director의 계획·방향·작업분해, 설계자(system-ui·balance)의 설계, 최종 결과의 방향부합 판단(designer·qa-critic).
- **Sonnet**(근육 = 중간80%): gameplay-engineer, scene-builder, art-pipeline, hd2d(적용), cpp — 모든 구현·실행.
- **Haiku**: verifier (테스트 실행).
- **철칙**: Fable은 노동하지 않는다. 방향을 정하고, 결과가 그 방향에 맞는지 판단할 뿐. 중간 실행에 Fable 쓰면 낭비.
- Director가 **명확한 지시서**를 줄수록 하위 토큰이 준다. frontmatter model은 기본값 — 필요시 Agent 호출 시 `model`로 오버라이드.

## 상속 규칙 (전역 CLAUDE.md 준수)

- 커밋 접두사 `[C] type:`. push는 오너 확인.
- 근본 원인 없이 수정 금지. 3회 실패 시 중단→오너 호출.
- "됐습니다" 전 실증. UI 문자열 하드코딩 금지(로컬라이제이션 키).
- MCP unreal-mcp는 에디터가 켜져 있어야 동작(`_Launch_MCP.bat`).
