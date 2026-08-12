---
type: gate
project: projectTP
feature: 스킬연출구조
updated: 2026-08-11
status: PASS
status_note: S0 완료 — 설계 전환(대역 액터) 확정
---

# E-S0 — 노드 가용성 프로브 결과 + Director 전환 판정

> 상위: [[E_스파이크_plan]] · TC: [[E_TC]] · 판정 배경: [[E0_에이전트피드백_Director판정]]

## 결과

| 군 | 대상 | 결과 |
|---|---|---|
| **A군** | `SetScalarParameterValue` · `CreateDynamicMaterialInstance` · `GetDataTableRow`×3 · `SetViewTargetWithBlend` · `SetGlobalTimeDilation` · `RetriggerableDelay` · `SpawnActor` · `MoveComponentTo` | **8/8 PASS** |
| B2 | `SetTextureParameterValue` | ✅ `declaring_class=MaterialInstanceDynamic` 명시로 **MPC 오버로드 무음 오생성 회피 확인** |
| B3 | `LoadAsset`(soft path) | ✅ `Utilities\|에셋비동기로드`. 미임포트 경로도 컴파일 0(소프트 경로는 컴파일 타임 존재 검증 없음) |
| B6 | `InputKey` 이벤트 | ✅ ★**예상보다 좋다** — 아래 §노하우2 |
| **B1** | **외부 raw 변수 Get**(`SpriteMID`·`HomeLocation`) | ❌ **FAIL** |
| **B4** | **`AlignSpriteToCamYaw` 외부 호출** | ❌ **FAIL** |
| **B5** | **`PlayHurtReaction` 외부 호출** | ❌ **FAIL** |

## ★공통 원인 — 원인이 3개가 아니라 1개다

> **신규(관계 없는) 블루프린트에서 외부 클래스의 변수·함수·이벤트를 새로 참조하는 노드 생성이 전부 막힌다.**
> `find_node_types` **검색은 성공하는데 `create_node`가 "does not exist"로 거부**한다.

[[언리얼_MCP_실전노하우]] §11이 **성공 실증**으로 기록한 `PlayAttack`은 **이미 `BP_BattleSpawnPoint` 참조가 확립된 `BP_BattleManager` 내부**에서 이뤄진 것이었다. 이번엔 완전히 새 BP(프로브)에서 시도했고 **재현되지 않았다.**

추가 확인: `retarget_node_class`로 self-scope 커스텀이벤트의 클래스 참조를 `BP_BattleSpawnPoint_C`로 전환하는 우회도 실패(`node type is unsupported or does not reference old_class`).

## ★Director 판정 — 유닛을 **참조하지 않는다.** 대역 액터로 전환

**`BP_FxLabDummy`**(캐릭터 대역) 신설. 스프라이트 쿼드·위치·모션 재생을 **스파이크가 소유**한다.

| 이득 | 내용 |
|---|---|
| **B1·B4·B5 실패가 무해해진다** | 남의 변수를 읽거나 남의 함수를 부를 일이 사라진다. 빌보드 스냅·플린치를 **자기 컴포넌트로 직접** 구현 |
| **"라이브 무접촉"이 더 강해진다** | 편집은 물론 **참조조차 하지 않는다** |
| **밀도 비교는 그대로 유효** | 같은 heroes99 텍스처 + 같은 스케일(**6.48 uu/텍셀**)을 대역에 적용하면 된다 — 이 실험의 **1순위 목적이 보존**된다 |

### 기각한 대안

**`BP_BattleManager` 안에 Director를 구현**(§11 성공 조건과 일치) → **라이브 BP 편집이라 제약1 정면 위반**이고, F7b가 같은 BP를 수술 대기 중이다. **스파이크 하나 때문에 감수할 위험이 아니다.**

### 대가 — S6 유효범위 고지에 **"대역 전제"를 추가**한다

라이브 유닛의 실제 거동과 차이가 남는다: `FaceLeft` 스위칭 · `PlayHurtReaction` 내부 타이밍 · `PlayAttack` **~0.58초 블로킹**.

## 부수 확인

`BP_BattleManager`가 세션 중 `is_dirty=true`로 나타났으나(조회만 했음에도) **`git status`상 `.uasset` 무변경 확인** — `save_assets` 미호출이라 디스크 반영 없음. 원인 미상(순수 조회의 in-memory 부작용으로 추정), 추가 조사는 스코프 밖.

## 프로브 정리

`AssetTools.delete("/Game/Blueprints/BP_FxLabProbe")` → `true` / `exists()` → **`false` 확정**.
