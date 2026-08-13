---
type: gate
project: projectTP
feature: 스킬연출구조
stage: FT1-S2
updated: 2026-08-13
status: PASS
status_note: "director 착수판정 — S2 착수 승인. S1 권고 1건 기각(sid BP 생성 잠정 채택 → 파서 유도 1차 계약 준수, sid 노드 0개), Sequence는 S2가 체인 토폴로지로 선제 배치(함정107 조건 자체 소멸), 슬롯 원천은 S4 첫 스텝 이월(PM 반증 재실측 확인), AU-F0b-01 재정의는 2단 분리(스키마=S5 착수 전 / 항등식=심은 뒤 실측). 화이트리스트 노드 2·연결 2·핀값 1. selftest 기준선 32/32 PASS 실측. ★★실행 완료(2026-08-13) — Part A~C 전량 수행: 게이트 5건(`AU-F0a-01~05`) 전량 PASS(04는 실측 26줄로 '계약 요구' 경로 승격 → [[FT1-S2_04판정]] 별도 판정으로 조건 충족 PASS). BP 무결 확인(노드 182→184, 정확히 +2). 커밋 `f487dc9`(Content BP 수술)·`c89e458`(selftest 4건)·`46b69f7`(본 착수판정). 상세 결과는 [[FT1-0_TC]] §2-B·[[FT1_plan]] §5 S2행에 반영."
---

# FT1-S2 착수판정 — 수술① 0a `SessionBoundary|` 마커 (director)

> 근거 사슬: [[FT1_plan]] §5 S2행·§7 · [[FT1-S1_조회결과_2026-08-13]](§PM 검증 포함) · [[FT1-0_TC]] `AU-F0a-01~05`·§3-A · [[FT1_착수조회_2026-08-12]] · [[전투로그]] §2-1(sid 계약 원문) · `docs/scripts/battle_log/{session,parser,tokens}.py` 실조회 · `projectTP.log` 직접 실측(2026-08-13, director) · [[언리얼_MCP_실전노하우]] 함정⑩·(23)·(99)·(101)·(102)·(103)·(104)·(107)
> ★이 문서가 곧 **S2 발주 지시서**다 — Part A(수술: gameplay-engineer) / Part B(실증: verifier) / Part C(판정·커밋: PM). 라이브 `BP_BattleManager` 첫 수술이므로 절차가 산출물이다.
#projectTP/스킬연출구조

---

## 0. 판정 요약

1. ★**S2 착수 승인** — 단 S1 권고 1건을 **기각**하고 착수한다(아래 2번). 오너 차단 0건(BeginPlay는 클릭 불요 — 함정99 벽 밖).
2. ★★**[가] sid 생성 노드는 0개다. F0p-01 실측(create+즉시delete)을 S2에서 하지 않는다** — [[전투로그]] §2-1이 **파서 유도를 이미 1차 계약으로 채택**했고 `battle_log/session.py::derive_sid`가 구현·자가시험 완료다(director 직접 실행: **selftest 32/32 PASS**, 세션 분할 케이스 포함). S1의 "BP 생성 잠정 채택(`sid=<Now>-<Rand>`)" 권고는 이 계약과 충돌하므로 기각. §1-가.
3. **[나] `AU-F0b-01` 재정의는 2단 분리** — `branch=` 필드 스키마는 **S5 착수 시 심기 전** TC 개정으로 확정(심는 위치가 곧 스키마), 카운트 항등식 숫자는 **심은 뒤 첫 하네스 런 실측으로** 동결. 지금 확정하지 않으며 **S2와 무관**. §1-나.
4. **[다] 슬롯 원천은 S4 첫 스텝 1회 조회로 미룬다** — PM 반증을 director가 재실측으로 확인(`attacker=SpawnPoint_Party_*` 20건 + ★`VFXSetup:SpawnPoint_Party_A2:` 발화 주체가 `[BP_BattleSpawnPoint_C_9]` **자신** — 원천 후보가 액터 자기 이름/표시명으로 사실상 좁혀짐). S2와 묶지 않는다. §1-다.
5. ★★**[②-2] Sequence는 S2가 배치한다 — 단 체인 토폴로지로**: `BeginPlay.then → PrintString(마커) → Sequence(then_0/then_1 빈 예약)`. 마커가 항상 최선두(F0a-04 최선) ∧ 이후 S3·S5는 **빈 핀에만** 붙으므로 함정107의 발생 조건("이미 배선된 출력 핀에 재연결")이 **구조적으로 소멸**한다. §2.

---

## 1. 전제 판정 3건 (S1이 흔든 것)

### 1-가. sid — ★S1 권고 기각, 현행 계약(파서 유도) 그대로 이행

| 안 | 판정 | 이유 |
|---|---|---|
| S1 권고: BP 생성 잠정 채택(`sid=<Now>-<Rand>`), S2 첫 스텝에서 create+delete 실측 | ❌ **기각** | ①[[전투로그]] §2-1 계약 원문: *"`sid`는 BP가 만들지 않는다(1차 계약). sid = 마커 라인의 엔진 프리픽스 벽시계 원문(**ms 해상도**)"* — `derive_sid(ts)->ts`로 **이미 구현·자가시험 완료**(selftest `PM지시④` 3케이스, director 직접 실행 32/32 PASS) ②BP 생성안은 첫 수술에 노드 4개+(Now·Rand·Append·Format)를 추가하고, `derive_sid` 승격·selftest 개정·계약서 개정까지 유발한다 — **결정론적 ms 해상도 수단을 확률적 초 해상도 수단으로 교체**하는 순손해 ③[[FT1-0_TC]] §3-A가 경고한 `FDateTime` 초 해상도 충돌 축은 파서 유도에서 **아예 존재하지 않는다**(두 PIE가 같은 ms에 시작할 수 없음) |
| ★**채택: 파서 유도(현행 1차 계약) — BP는 상수 1줄만 찍는다** | ✅ | 마커 = `SessionBoundary\|event=BeginPlay` 리터럴 1줄, **sid 관련 노드 0개**. 계약·파서·selftest가 전부 이미 존재하므로 S2의 신규 구현은 BP 쪽 2노드뿐 |

★**"실측 성공 ≠ 게이트 통과" 문제의 처리**: 문제 자체가 소멸한다. `AU-F0p-01`의 유일한 소비자는 "BP측 sid 승격(계약 §2-1 하위호환 경로)"인데 승격할 이유가 현재 0이므로, create+delete 실측은 **소비자 부재로 격하**한다 — 성공해도 어떤 게이트에도 기여하지 않는 실측을 첫 수술 세션에 넣지 않는다. `AU-F0p-01`은 **"택1 완료(파서 유도, 계약이 결정) — 생성 가능성 판정은 잠정(높은 확신, 미실측)인 채 동결"**로 종결한다(Part C에서 PM이 TC 문서에 기록). 승격이 필요해지는 날이 오면 **그 단계의 착수 조회**에서 닫는다.

`AU-F0a-02`(sid 2종)는 파서 유도로 판정한다 — 두 PIE의 마커 라인 프리픽스 ts가 다름을 `assign_sessions` 실행으로 실증(Part B).

### 1-나. `AU-F0b-01` — 지금 숫자를 확정하지 않는다 (2단 분리)

- **PM 검증 ⓑ가 옳다**: exec 종단 4갈래는 핀 원문 기반 **정적 예측**이고, `PlayAttack|` 토큰은 현재 로그에 enter 0/exit 0(director 재실측: `grep -c "PlayAttack|"` → `projectTP.log` 0건, `projectTP_2.log` 0건 — 0b 미심기라 당연). 실측 없는 항등식 확정은 원칙 위반이다.
- **단, 스키마는 실측을 기다릴 수 없다** — 4종단에 `branch=guard_fail|delay_end|move_end|nomove_end`를 심으려면 **심기 전에** 필드가 계약에 있어야 한다(심는 위치가 곧 스키마). 따라서:
  - **(i) S5 착수 시, 심기 전**: `AU-F0b-01` PASS 기준 문장과 `PlayAttack|` 필드 스키마(`branch=` 추가)를 TC 개정으로 확정 — [[FT1_plan]] §10-5의 "S5 착수 전 qa append-only 1회" 권고와 **한 발주로 병합**한다.
  - **(ii) 심은 뒤**: 첫 하네스 자동 런의 실측 카운트로 항등식(예: `enter n == guard_fail n₁ + delay_end n₂` ∧ `n₂ == move_end+nomove_end`)을 동결. `RetriggerableDelay` exit 삼킴(`AU-F0b-03`)도 이때 실측된다.
- **S2 지시서에는 포함하지 않는다** — S2 산출물·게이트 어디에도 `PlayAttack|`이 없다.

### 1-다. 슬롯 원천 — PM 반증 타당(재실측 확인), S4 첫 스텝 이월

director 직접 실측(2026-08-13, `D:\unreal\projectTP\Saved\Logs`):

```
projectTP.log:   attacker=SpawnPoint_Party_*  20건 / projectTP_2.log: 6건
[2026.08.11-12.14.03:246][394]LogBlueprintUserMessages: [BP_BattleSpawnPoint_C_9] VFXSetup:SpawnPoint_Party_A2:SmearMID=True
```

- **PM 반증 확정**: 슬롯 문자열(`SpawnPoint_<Team>_<Slot>`)은 라이브 로그에 실재하며 이미 로그가 쓴다.
- ★**반증을 넘어서는 단서 1건**: `VFXSetup:SpawnPoint_Party_A2:` 라인의 발화 주체가 **`BP_BattleSpawnPoint_C_9` 자신**이다 — SpawnPoint가 자기 슬롯 문자열을 BeginPlay 시점에 스스로 만든다. 변수·Tags 부재(S1 실측)와 결합하면 원천은 **액터 이름/표시명(`GetDisplayName(self)` 류) 사실상 확정** — 남은 것은 그 생성 노드 1홉 역추적뿐이다.
- **판정**: S4 착수를 차단하지 않는다. **S4 첫 스텝(수술 전 조회 1회)**에서 `VFXSetup:` 또는 `BattleLog|attacker=` 문자열 생성 노드를 역추적해 확정한다. **S2와 묶지 않는다** — 첫 라이브 수술의 범위는 최소가 원칙이고, 이 조회는 S4 세션에서 수술 전 조회로 비용 동일하다.

---

## 2. [②-2 판정] Sequence — S2가 배치한다, 체인 토폴로지로

**채택 토폴로지** (이후 FT1 전 단계의 부착 구조를 이 판정으로 확정):

```
BeginPlay(K2Node_Event_0).then
  → [신규] PrintString(마커).execute ── .then
      → [신규] Sequence.execute
          .then_0 → (빈 채로 둠 — S3 자동시작 1b 예약)
          .then_1 → (빈 채로 둠 — S5 SCF 1c 예약)
```

| 축 | 근거 |
|---|---|
| 왜 S2가 놓는가 | plan 원안대로 S2가 마커를 `BeginPlay.then`에 직결하면, S3의 `Sequence` 선제 배치가 **이미 배선된 핀을 갈아끼우는 작업**이 된다(함정107을 의도적으로 쓰는 꼴 + additive 규율 위반). 부착 토폴로지는 **첫 점유자가 확정**해야 이후 단계가 전부 "빈 핀에 붙이기"로 균질해진다 |
| 왜 마커가 Sequence **앞**인가 | `AU-F0a-04`(순서 게이트) — 마커는 Manager BeginPlay 체인에서 **무조건 최선두**여야 한다. 체인 토폴로지는 이를 구조로 보장한다(then_0 배정 방식과 달리 이후 핀 추가·재배치와 무관) |
| 함정107 | 발생 조건("이미 배선된 출력 exec 핀에 재연결") 자체가 소멸 — S3은 `then_0`(빈 핀), S5는 `then_1`(빈 핀)에만 붙는다. 단 각 단계 배선 후 `get_node_infos` 재조회 의무는 유지(함정107 규칙 3) |
| 기각 (a): S2는 마커만, S3이 `마커.then`에 Sequence 부착 | 동작은 한다(마커.then이 빈 핀이므로). 그러나 부착 토폴로지 결정이 S3으로 밀리고, plan §5 S3행("Sequence 선제 배치")과 실제 구조가 어긋난 채 남는다. 노드 1개 아끼자고 결정을 한 번 더 하게 하는 구조 — 기각 |
| 기각 (b): `Sequence` 3핀(then_0=마커/then_1=1b/then_2=1c) | 세 번째 핀은 `add_node_pin` 필요 — FormatText에서의 실적은 있으나 **ExecutionSequence 대상 실적은 미실측**. 첫 수술에 미실측 의존을 넣지 않는다 — 기각 |

⚠ **plan 정정 기록 필요(Part C)**: [[FT1_plan]] §5 S3행의 "`Sequence` 선제 배치"는 **S2로 이동**된다(취소선+사유). S3은 "S2가 예약한 `then_0`에 1b 체인 부착"으로 바뀐다.

---

## 3. Part A — 수술 지시서 (gameplay-engineer, Sonnet)

### 3-1. 범위와 금지

- **대상**: `BP_BattleManager.EventGraph` 단 1그래프. 목적: `SessionBoundary|` 마커 + 예약 Sequence 심기(순수 additive).
- **금지**: 기존 노드·핀·연결의 수정·절단 0건 / 변수·함수·그래프 신설 0건 / 다른 BP·레벨·DataTable 접촉 0건 / **`save_assets` 빈 리스트 금지**(함정102 — 항상 명시 경로) / 레벨 인스턴스 오버라이드 0건(`.umap` dirty 금지) / sid 관련 노드 생성 금지(§1-가).
- **세션 배타**: 이 세션 동안 타 발주 MCP 사용 금지(함정23) — PM이 발주 시 보장.
- 권장 사전조건: 에디터 fresh 기동 상태(S1 프로브의 인메모리 dirty 잔존 회피 — 차단 아님, 내용 무해 실증됨) ∧ 수술 전 `git -C D:/unreal/projectTP/Content -c core.quotepath=false status --porcelain` **공백 확인**.

### 3-2. 화이트리스트 (사전 고정 — 이것 외 diff 0이 게이트다)

| # | 신규 노드 | 생성 문자열 | 개수 |
|---|---|---|---|
| N1 | `PrintString` | `개발\|PrintString`(실적: [[T1T2_BP구현]]·[[전진로직_실체_확정]] line43) — 단 ★생성 전 `find_node_types` 선탐색으로 재확인 의무(함정⑩) | 1 |
| N2 | `Sequence`(ExecutionSequence) | 추정 `유틸리티\|플로컨트롤\|Sequence`(같은 카테고리의 `RetriggerableDelay`가 S1에서 실측됨) — ★**미실측이므로 `find_node_types` 선탐색 필수**, 0건이면 카테고리 전체 나열로 스캔(함정104 공통 대응) | 1 |

| # | 신규 연결 | 출발 | 도착 |
|---|---|---|---|
| C1 | exec | `EventGraph.K2Node_Event_0`(BeginPlay).`then` — **연결 전 미배선 재확인**(2회 실측됐으나 함정107 규칙 1) | N1.`execute` |
| C2 | exec | N1.`then` | N2.`execute` |

| # | 핀 값 설정 | 값 |
|---|---|---|
| P1 | N1.`InString` | `SessionBoundary\|event=BeginPlay` (계약 §2-1 원문 그대로 — 필드 추가·변형 금지) |

**그 외 전부 기본값 유지**(diff 최소화). N2의 `then_0`/`then_1`은 **빈 채로 남긴다**(S3/S5 예약). ⚠노드 자동 번호(`K2Node_CallFunction_N`)는 예측·하드코딩 금지 — 항상 생성 호출의 반환 refPath를 사용(함정103, 카운터 비롤백).

### 3-3. 절차 (순서 고정)

1. **수술 전 덤프(베이스라인)**: `find_nodes(EventGraph)` 노드 총수 기록 + `K2Node_Event_0` 핀 원문 `get_node_infos` 덤프(보고서에 원문 인용).
2. `find_node_types`로 N1·N2 생성 문자열 확정(0건이면 상위 카테고리 나열 스캔 — 함정104).
3. `create_node` ×2 → 반환 refPath 기록.
4. `set_pin_value`(P1) → `get_pin_value` 재조회로 값 반영 확인.
5. `connect_pins`(C1, C2) → ★**`get_node_infos` 재조회로 3노드(BeginPlay·N1·N2) 핀 원문 전부 재덤프** — C1·C2 실재 ∧ 그 외 연결 변화 0 확인(함정107 규칙 3).
6. `compile_blueprint(BP_BattleManager)` → 에러 0 확인.
7. **스모크 PIE 1회**(레벨 = `map_battle_octopath` 확인 후): 로그에 마커 1줄 발화 유무만 확인. ★이것은 게이트 판정이 아니다 — 판정 카운트는 Part B(verifier)가 새 런으로 잰다(구현자 자가검증 금지 규율).
8. `save_assets(["/Game/Blueprints/BP_BattleManager"])` — ★명시 경로, 빈 리스트 금지.
9. `git -C D:/unreal/projectTP/Content -c core.quotepath=false status --porcelain` → **`BP_BattleManager.uasset` 1파일만 M ∧ `.umap` 부재** 확인(원문 인용).

### 3-4. 롤백 (수술 실패·게이트 FAIL 시)

- **즉시 무력화**: `break_pins`(C1) 1건 절단 → 스캐폴드 전체가 고아 섬이 된다(순수 additive·데이터 의존 0이므로 부작용 0). — plan §7-1의 "발화 지점 exec 1개 절단"으로 **충분함을 확인**(단 아래 완전 원복까지가 롤백 완료다).
- **완전 원복**: `delete_node` ×2 → `compile` → BeginPlay 핀 원문 재덤프가 §3-3-1 베이스라인과 **완전 일치**함을 인용 → `save_assets`(명시 경로).
- **저장·커밋 후 원복**: 에이전트 `git restore` 권한 없음(함정102 해법 3) — 직접 시도 금지, PM/오너에 위임. 세이브포인트(Part C)가 최종 안전망.

### 3-5. 보고 필수 항목

① 수술 전/후 핀 원문(3노드) 전문 ② 노드 총수 전/후(정확히 +2) ③ 사용한 생성 문자열 원문 2건 ④ 컴파일 결과 ⑤ 스모크 PIE의 마커 라인 원문 1줄 + `max tick rate` 값 ⑥ git status 원문 ⑦ `save_assets` 호출 원문(경로 포함).

---

## 4. Part B — 실증 지시서 (verifier, Sonnet, 수술 세션 종료 후 별도 발주)

전제: 레벨 = `map_battle_octopath`. 판정 로그 = `D:\unreal\projectTP\Saved\Logs\projectTP.log`. 구간 정의 = 연속한 엔진 `up for play` 라인 사이. ★자기 세션의 PIE 런만 판정 대상(구간의 `up for play` 벽시계로 식별 — 함정101).

| 게이트 | 무엇을 확인하면 통과인가 |
|---|---|
| **AU-F0a-01** | 새 PIE 1회 기동 → 그 구간 안 `SessionBoundary\|event=BeginPlay` 라인 수 == **정확히 1** ∧ 보고에 `max tick rate` 명기(값 자체는 판정 대상 아님) |
| **AU-F0a-02** | PIE 2회 연속(같은 로그 파일) → `battle_log.session.assign_sessions`를 그 로그에 실제 실행해 **sid 2종**(두 마커의 프리픽스 ts 상이)을 파서 출력으로 인용 ∧ 두 PIE의 벽시계 간격 기록(파서 유도는 ms 해상도라 간격 무관 — 그 사실 자체를 기록) |
| **AU-F0a-03** | Part A 보고의 수술 전/후 핀 원문 diff == §3-2 화이트리스트(노드 2·연결 2·핀값 1) **정확히 그것뿐** ∧ 노드 총수 +2 ∧ 핀 원문이 보고서에 그대로 인용돼 있음(서술만이면 FAIL) |
| **AU-F0a-04** ★유일한 결과 불확정 게이트 | 같은 구간에서 마커 **이전** `LogBlueprintUserMessages` 줄 수를 센다. **판정 트리**: ⓐ 0줄 → PASS ⓑ ≥1줄 → FAIL 아님, 선행 라인의 **토큰 내역**(어떤 토큰 몇 줄)을 보고하고, 계약 요구 충족을 인용으로 확인 — pre-marker 구간의 명시 라벨링(`sid=None`)은 `session.py::assign_sessions`에 **이미 구현**돼 있고 selftest `PM지시④`가 커버한다 ⓒ ★선행 라인에 `Registered:`·`State\|`(특히 `event=INIT`)가 포함되면 **직권 PASS 금지, 즉시 정지·PM 보고** — 세션 N≥2의 선행 라인이 세션 N-1의 sid로 오귀속되는 **bleed**는 현행 계약이 커버하지 않는 갭이며(마커가 로그 중간에서 늦게 뜨는 경우), S4의 MA-1a 세션 절단 전제를 훼손한다. 후보 해법(엔진 `up for play` 라인을 보조 None-경계로 승격하는 `session.py` 소폭 개정)은 계약 변경이므로 director 판정 사안이다 |
| **AU-F0a-05** | (오프라인, MCP 불요) ⓐ selftest 전량 PASS 유지(기준선 **32/32**, 2026-08-13 director 실측) ⓑ ★실측 마커 라인 **원문 1건**을 selftest 픽스처로 추가(실측 포맷 vs 합성 포맷 괴리 방어) 후 재실행 전량 PASS |

보고 필수: 게이트별 판정 + 인용 원문 + `max tick rate` + F0a-04 카운트·토큰 내역.

---

## 5. Part C — PM 게이트 판정·커밋·문서 (verifier PASS 후)

1. **게이트 판정**: §4 표 5건 전부 PASS → S2 통과. F0a-04가 트리 ⓒ로 빠지면 **director 재호출**(계약 보강 판정).
2. **세이브포인트**: `BP_BattleManager.uasset` 사본을 `_savepoints\`에 + SHA256 manifest(**`.umap` 포함** — dirty 감시, [[FT1-0_TC]] §3-B Medium 처분 계승).
3. **커밋**(수술별 분리 원칙): Content 저장소 — uasset 1파일, `[C] feat(FT1-S2): SessionBoundary 마커+예약 Sequence 스캐폴드(0a)` / Resource 저장소 — S2 결과 기록 + selftest 픽스처. ★커밋 전 `git -c core.quotepath=false diff --cached --stat` 확인 의무(같은 날 2회 사고 재발 방지).
4. **push**: Content 저장소 push는 세이브포인트 규칙상 필요 — **오너 확인 후** 실행(단독 push 금지).
5. **문서 갱신(작업 완료 = 문서 갱신)**: ⓐ S2 결과 기록 신설(`FT1-S2_수술결과_<날짜>.md`) ⓑ [[FT1_plan]] frontmatter+§5 S2행 완료 처리 + ★**S3행 정정**(Sequence 배치가 S2로 이동 — 취소선+사유, S3은 "예약 `then_0`에 1b 부착") ⓒ [[FT1-0_TC]]에 `AU-F0p-01` 종결 기록(§1-가 문구: 택1 완료·생성 판정 동결) ⓓ 기능허브 갱신.

---

## 6. 이월·동결 목록 (사유 없는 이월 금지)

| 항목 | 처분 | 사유 | 닫히는 곳 |
|---|---|---|---|
| `AU-F0p-01` create+delete 실측 | **동결** | 소비자 부재(파서 유도가 1차 계약) — §1-가 | BP측 sid 승격이 실제로 필요해지는 단계의 착수 조회 |
| `AU-F0b-01` 재정의 | 2단 이월 | 정적 예측 미실증(PM 검증 ⓑ) + 스키마는 심기 전 필수 | S5 착수 시 TC 개정(qa append-only 병합) → 심은 뒤 실측 동결 |
| `ResolveSlotToActor` 원천 확정 | S4 이월 | 라이브 실재 확인(§1-다), 1홉 역추적만 잔여 | S4 첫 스텝(수술 전 조회) |
| 마커 필드 확장(`ledger=`/`flow=` 등 4 bool 동봉, `AU-F0x-05`) | 이월 | 4 bool 자체가 미신설(LOG-A 본진행 범위) | LOG-A 카테고리 bool 수술 시 별도 화이트리스트 |

## 7. 미확인으로 남긴 것

| # | 무엇 | 닫는 방법 |
|---|---|---|
| 1 | `Sequence` 생성 문자열(추정 `유틸리티\|플로컨트롤\|Sequence`, 미실측) | Part A §3-3-2 선탐색(절차에 내장) |
| 2 | Manager BeginPlay가 SpawnPoint 8기보다 먼저 도는가(F0a-04의 결과를 가르는 유일 변수 — 실측상 `Registered:1`이 `up for play` +10ms에 발화하므로 순서는 심어봐야만 안다) | Part B AU-F0a-04 판정 트리(절차에 내장) |
| 3 | pre-marker bleed(마커가 구간 중간에 늦게 뜰 때 세션 오귀속) 계약 보강 필요 여부 | F0a-04 실측이 ⓒ로 빠질 때만 — director 판정 |

## 관련

[[FT1_plan]] · [[FT1-S1_조회결과_2026-08-13]] · [[FT1-0_TC]] · [[FT1_착수조회_2026-08-12]] · [[전투로그]] · [[언리얼_MCP_실전노하우]]
