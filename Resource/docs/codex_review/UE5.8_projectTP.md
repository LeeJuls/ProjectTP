---
type: review
project: projectTP
status: active
updated: 2026-07-17
---

# UE 5.8 Codex Review — projectTP

> 상위: [[projectTP_허브]] · 계획: [[UE5.8_Codex_학습계획]] · 근거 카탈로그: [[언리얼5.8_기술카탈로그]]
>
> 목적: UE 5.8 공식 문서를 현재 projectTP의 구현·검증 판단으로 번역한다. 기능을 새로 채택하는 문서가 아니라, 채택 전 근거와 게이트를 남기는 기준 노트다.

## 0. 현재 프로젝트 판단

> **[Director 갱신 — 2026-07-17]** 이 문서는 Codex가 2026-07-15에 작성했다. 아래 진행 단계 서술(1문단)만 그 이후 통과한 게이트를 반영해 Director가 현재 상태로 갱신했다 — Codex FULL-004("허브·plan·체크리스트·UE5.8 노트의 현재 단계와 완료 게이트가 서로 다름") 지적 반영. §1 기술 판단표·§2 알파 시스템 매핑·§3 보류·금지 목록은 Codex 원문을 그대로 유지했다(유효하므로 미변경).

projectTP는 Steam용 4:4 HD-2D 턴제 PvP를 목표로 하며, 알파는 **드래프트→4:4 전투(vs AI)→결과** 루프다. A1 전투완성은 **F6·F7a·F8·F9a 전부 게이트를 통과**했고, 이어서 **F7b**(struct 3종·데이터 3층 임포트·인터프리터 골격까지 완료, ResolveHit 수술은 이월)를 거쳐 **파트1(Start 버튼) 게이트 PASS**(커밋 `7743d85`)·**파트2(SPD 턴 순서) 핵심 게이트 PASS**(커밋 `c4f8695`)까지 통과했다. 다음 단계는 **파트3(막기·치유 연출)** 진행 중이다(2026-07-17 01시 기준).

- 알파의 기본 구현은 **Blueprint + CSV DataTable + UMG + UE MCP/UMG MCP**를 유지한다.
- C++은 A2 이후 코어 이관 또는 성능·표현 복잡도가 실증된 경우에만 도입한다.
- 이 문서는 [[언리얼5.8_기술카탈로그]]를 대체하지 않는다. 카탈로그의 문서 조사 결과를 현재 기능 우선순위에 연결한다.
- 이 노트는 구현 명세가 아니라 기술 판단의 색인이다. 수치·CSV 스키마·TC·증거 저장 위치는 각 `features/<기능>/plan.md`와 그 raw 기록이 정본이다.

## 1. 지금 적용할 기술

| 우선 | 기술·사용처 | 적용 규칙 | 검증 게이트 | 공식 근거 |
|---|---|---|---|---|
| P0 | UMG HP 게이지·전투 HUD | 바인딩 방식과 위젯 직접 `Set` 호출을 혼용하지 않는다. 월드 HP 표시는 Widget Component를 우선 검토한다. | 피해 후 HP 텍스트·게이지가 함께 정확히 갱신되고, F9b에서 잔존 하이라이트/위젯이 없다. | [UMG Property Binding](https://dev.epicgames.com/documentation/en-us/unreal-engine/property-binding-for-umg-in-unreal-engine) · [Widget Components](https://dev.epicgames.com/documentation/en-us/unreal-engine/widget-components-in-unreal-engine) |
| P0 | CSV → DataTable 전투 데이터 | `Name`/Import Key와 struct 필드를 명시적으로 관리한다. reimport 후 row 포인터·참조를 함수 범위 밖에 캐시하지 않는다. | F4~F7 CSV 규칙 TC 전부 통과, reimport 뒤 스킬·모션·문자열 조회가 동일하다. | [Data Driven Gameplay Elements](https://dev.epicgames.com/documentation/en-us/unreal-engine/data-driven-gameplay-elements-in-unreal-engine) |
| P0 | 결정론 전투·로그 | 피해·상태이상·광폭화는 단일 계산 경로와 전투 로그를 정답지로 사용한다. UI는 결과를 표시할 뿐 판정을 소유하지 않는다. | 구현 로직을 호출하지 않는 독립 계산 오라클로 F9a HP 원장을 대조하고, 스킬·사망·광폭화 로그 완성도와 기존 파서 호환을 확인한다. | [[features/전투완성/plan]] · [[스탯_전투공식_v1]] |
| P0 | UE MCP·UMG MCP 작업 | 에디터 조작 호출은 게임 스레드 직렬 처리 전제로 한 단계씩 실행·검증한다. BP/UMG 생성 뒤에는 MCP 정적 조회와 PIE 실측을 모두 남긴다. | 각 feature 단계 TC의 정적 그래프 조회 + PIE/캡처 + 오너 확인을 모두 통과한다. | [[언리얼_MCP_실전노하우]] · [Unreal MCP 개요](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-mcp) |
| P1 | HD-2D 스프라이트·카메라 | 현재의 Lit 스태틱메시 쿼드·머티리얼 UV 애니메이션 경로를 유지한다. Paper2D/Flipbook으로 되돌리지 않는다. | F9b에서 FREEZE_LAST·Z-fighting·틸트시프트 프레이밍을 육안 확인한다. | [[HD2D_기법_지식베이스]] · [[카메라연출_원칙]] |
| P1 | Editor 자동화 | 대량 에셋·CSV 검증·임포트가 반복될 때만 Editor Scripting Utilities + Python/Editor Utility를 사용한다. Python은 런타임 기능에 쓰지 않는다. | 자동화 전후 에셋 수·이름·DataTable 행 무결성을 비교하고, 스크립트 결과를 feature raw에 남긴다. | [Scripting and Automating the Unreal Editor](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-and-automating-the-unreal-editor) · [Python Editor Scripting](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python) |

### P0 규칙: UMG 바인딩

UE 문서는 위젯 프로퍼티에 바인딩을 걸고 직접 `Set`을 호출하면 바인딩이 깨진다고 명시한다. 따라서 `WBP_BattleHUD`·`WBP_UnitFrame`의 각 표시 항목은 **바인딩 소유** 또는 **명시적 Set 소유** 중 하나를 설계 단계에서 선택하고, 둘을 섞지 않는다. 이는 기존 `SetText` 무반영 문제를 추적할 때 우선 점검할 항목이다.

### P0 규칙: 데이터 주도 전투

`characters.csv`·`skills.csv`·`motions.csv`·`strings.csv`는 전투 로직의 입력이고, Blueprint는 유효한 행을 조회해 판정만 한다. `FDataTableRowHandle`/행 조회 결과를 재임포트 경계 밖에서 보관하지 않는다. 키 변경, struct 변경, CSV 열 변경은 같은 단계의 TC로 같이 검증한다.

## 2. 알파 시스템 매핑

| 알파 시스템 | UE 5.8 책임 | 현재 결론 | 다음 검증 시점 |
|---|---|---|---|
| S1 캐릭터 코어 | CSV DataTable, struct, Data Validation | 데이터 우선. 등급 보정은 데이터 컬럼으로 확보하고 로직은 고정한다. | A2 착수 전 1000조합 생성·중복·포지션·극단승률 검증 |
| S2 렌더 조합 | 머티리얼, Static Mesh, DataTable 모션 행 | 현행 5레이어·UV 애니메이션 유지. | 캐릭터 풀 확대 전 배치·드로우콜·룩 회귀 |
| S3 드래프트 | UMG, GameInstance, SaveGame | 화면은 위젯, 레벨은 3D 무대 변경 때만. 드래프트 결과는 GameInstance, 누적 골드는 SaveGame. | 드래프트 feature 청사진 단계 |
| S4 전투 엔진 | Blueprint 상태 머신, DataTable, 전투 로그 | A1 범위에서 BP 유지. 판정과 로그를 단일 소스로 둔다. | F6~F9 남은 게이트 |
| S5 광폭화·밸런스 | 데이터/전투식/검증 스캐폴드 | 30유닛턴 후 가산 +5%, 힐에는 미적용. | F8·F9a 원장 대조 |
| S6 AI·봇 | 기존 전투 상태 머신 위의 결정 선택 | PvP 매칭 폴백용이므로 먼저 AI가 동일 전투 계약을 사용해야 한다. | 알파 vs AI 완주 게이트 |
| S7 화면 흐름 | UMG, GameInstance, OpenLevel | 2개 레벨 + 8화면 규약 유지. | Title→Lobby→Draft→Battle→Result 통합 TC |
| S8 저장·로컬화 | SaveGame, CSV 문자열 규약 | 골드만 영속. 현행 CSV/DataTable 로컬화 경로를 유지한다. | 드래프트 리롤·결과 저장 TC |
| S9 테스트·배포 | 로그 파서, Data Validation, Cooking | 알파는 로그·PIE로 먼저 검증. 패키징 직전에 Incremental Cooking을 재검토한다. | Steam 빌드 착수 전 |

## 3. 보류·금지 목록

| 항목 | 결정 | 이유/재검토 트리거 |
|---|---|---|
| Lumen·Nanite·MegaLights | 채택하지 않음 | 8유닛 정적 디오라마와 저폴리 배경에 해결할 병목이 없다. 룩과 최소 사양을 실제로 바꿀 요구가 생길 때만 재검토. |
| Paper2D Flipbook | 채택하지 않음 | 현재의 DataTable 구동 머티리얼 UV 애니메이션과 3D Lit 통합을 대체하지 못한다. |
| Mass Entity·Network Prediction·Iris | 알파 범위 밖 | 2인·8유닛·턴제에 과잉이다. 베타 PvP에서 프로파일과 네트워크 요구가 나타날 때 재평가. |
| GAS | 보류 | 상태이상 원자 시스템의 규모·C++ 전환 필요성이 실증된 A2 전이 시점에만 비교한다. |
| CommonUI + Enhanced Input | 보류 | 게임패드 UI 착수 전에 5.8 실제 패키징 가능성을 별도 스파이크로 확인한다. |
| Python 런타임 사용 | 금지 | UE Python은 에디터 자동화용이다. 패키지 게임·서버 로직에 넣지 않는다. |

상세 공식 근거와 문서 간 모순은 [[언리얼5.8_기술카탈로그#4. 미확인 / 문서 모순 (8건) — 정직 고지]]를 단일 출처로 삼는다. 특히 CommonUI, Data Validation BP 커맨드릿, GAS BP-only, EOS 저장소는 확인 전 확정 기술로 기록하지 않는다.

## 4. Codex 작업 규칙

1. 기능 시작 전, 이 문서의 해당 행과 [[언리얼5.8_기술카탈로그]]를 확인한다.
2. 새 엔진 기능은 **공식 문서 링크 → 채택 이유 → feature plan TC** 세 항목이 갖춰질 때만 채택한다.
3. Blueprint 변경은 한 논리 단위씩 적용하고, 정적 그래프 확인과 PIE 결과를 같은 게이트에 남긴다.
4. 데이터 스키마/CSV 변경은 import·reimport·런타임 조회·로그 검증을 한 단계에서 끝낸다.
5. 전투 결과 검증은 런타임 계산 함수를 재사용하지 않는 독립 오라클과 로그 대조로 수행한다.
6. 문서가 미확인 또는 모순이면 추정으로 구현하지 않고 스파이크 TC를 만든다.

## 5. 갱신 트리거

- A2 캐릭터 코어 시작: 1000조합 생성, Data Validation, 데이터 스키마 리뷰 추가.
- 드래프트 화면 시작: UMG·GameInstance·SaveGame 항목을 상세 TC로 분리.
- 게임패드 UI 시작: Enhanced Input/CommonUI를 5.8 실물 패키징으로 재검증.
- 베타 네트워킹 시작: Steam/EOS·RPC·리슨서버 계약을 별도 review로 분리.
- Steam 패키징 시작: Incremental Cooking·Shipping 프로파일·성능 계측을 재검토.

## 6. 이번 리뷰의 판정

- S1 공식 근거 정합성: **PASS** — 현행 P0/P1 기술과 공식 문서·기존 카탈로그를 연결했다.
- S2 알파 시스템 매핑: **PASS** — 9개 시스템에 엔진 책임과 다음 검증 시점을 지정했다.
- S3 독립 리뷰 기록: **PASS** — `codex_review` 폴더에 작성했고, 기존 워크플로우 문서는 변경하지 않았다.
- S4 지속 갱신: **진행 중** — 기능 착수와 엔진 도입 결정 때마다 이 노트를 갱신한다.
