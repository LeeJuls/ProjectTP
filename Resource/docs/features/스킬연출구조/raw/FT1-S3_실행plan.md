---
type: plan
project: projectTP
feature: 스킬연출구조
stage: FT1-S3
updated: 2026-08-13
status: BLOCKED
status_note: "★홀드(2026-08-13, 오너 지시) — D6까지 완료, D7(부착) 직전 정지. 재개 진입점은 [[FT1_홀드기록_2026-08-13]]. / S3 실행 plan v2 — 오너 승인 완료(2026-08-13). agents 피드백 3건(qa-critic·gameplay-engineer·verifier) 반영해 v1에서 업그레이드. ★착수 전 필수 정정 5건 포함. ★plan을 git 안에 둔다 — .claude/plans/는 이력이 없다(오너 지시)"
---

# FT1 S3 — 자동 시작 토글 (v2, 에이전트 피드백 3건 반영)

## Context

**S3가 무엇인가**: ★**함정99가 죽는 단계**다. 에이전트는 Start 버튼을 클릭할 수 없다. 토글이 생기면 **처음으로 전투를 혼자 시작**할 수 있고, 이후 실증 30건이 여기 걸려 있다.

**왜 v2인가**: 오너 지시로 **agents 피드백 → plan upgrade**를 거쳤다. ★**v1(솔로 plan)에는 착수를 막을 결함이 있었다.**

| 피드백 | 발견 |
|---|---|
| **qa-critic** | 9단계 분할 + TC 35건 + ★**적대 검토 11건**(High 4) |
| **gameplay-engineer** | 노드 17 재검산 통과 + ★**절차 순서 오류** + 선례 조사 |
| **verifier** | ★**게이트가 못 잡는 것 8건** |

★**독립 중복 발견 4건**(= 확실): `Accessed None` 부재 · off-런 `GUARDFAIL` 미커버 · "완전 침묵" 미분류 · off 복원 미재확인.

---

## ★착수 전 필수 정정 5건

### ★F1 — `BattleState` 타입 모순 (qa, High)

★**착수판정 한 문서 안에서 상충한다**: `BattleState`는 **정수**인데 §3-2 N5는 **`Equal(Byte)` 복제**를 지시한다(원출처 `전투BP_현황도` L40 ↔ L52도 같은 모순).

★**실현되면**: D5에서 **자동 형변환 노드가 삽입** → 노드 **202** → ★**`AU-FAS-01`이 올바른 구현인데도 FAIL**한다.

★**PM 판정 — director 재호출 불요.** qa의 **D1(조회 전용)**이 `AU-FSTP-03`으로 이걸 닫는다. ★**단계 분할이 이 문제를 구조적으로 흡수**한다 — 실측 후 N5를 결정하고, 형변환이 필요하면 **화이트리스트를 그때 확정**한다.

### ★F2 — `Delay(0.1)` 존치 근거가 검증되지 않는다 (qa, High)

director는 *"latent 재개가 전 액터 `BeginPlay` 완료 후"*를 존치 근거로 들었는데, ★**`AU-FAS-04`로는 그게 검증되지 않는다(교락).** 04판정 §2가 이미 이 레벨의 순서를 확정했으므로 `INIT < FIRE`는 **Delay 유무와 무관하게 성립**한다.

★**qa의 대체 판정식 채택**: **`frame(FIRE) ≠ frame(마커)`**
로그 프리픽스의 프레임 카운터는 `parse_line_meta`가 **이미 추출**하고, ★**이산 정수라 3fps에서 합법**이며 비용 0이다. (랩어라운드 미확인이라 `>`가 아니라 `≠`)

### ★F3 — `Accessed None` 스윕 부재 (qa·verifier 독립 중복)

가드가 `TurnQueue`·`BattleState`·`bInputLocked`를 새로 참조한다. `AU-FAS-01`의 *"컴파일 에러 0"*은 **정적**이라 런타임 문제를 못 잡는다. 이 프로젝트는 이미 ★**"`Accessed None` 0건"을 기준선**으로 갖고 있다(`로그시스템_점검` §2-4).
→ ★**`AU-FAS-02/03`에 `grep -c "Accessed None"` = 0 추가.** 비용 0.

### ★F4 — 정지선 미커버 3종 (qa·verifier 중복)

| 누락 | 왜 위험한가 |
|---|---|
| ⓐ **off-런 `GUARDFAIL` ≥1** | 정지선#1은 **on-런 한정**, #4는 `TurnStart`만 본다. ★**토글 Branch 극성이 반대로 꼬인 시그니처** |
| ⓑ ★**on-런 `FIRE 0 ∧ GUARDFAIL 0`**(완전 침묵) | ★**"사문(死文) 체인" vs "오버라이드 쓰기 실패"** — **처분이 정반대인 2분기가 미분류**. `set_properties` 인스턴스 bool 쓰기가 **최초 실측**이라 실제로 일어난다 |
| ⓒ 스모크 PIE 오염 | `save_assets` **직전** 정지선으로 미승격 |

★**ⓑ의 진단 순서를 명문화**: 먼저 `get_properties`로 override가 **true로 읽히는지** 확인 → 그다음에야 BP 배선을 의심한다.

### ★F5 — `AU-FAS-01`이 문언 그대로면 자가검증이다 (verifier, 최우선)

원문: *"**Part A 보고의** 전/후 핀 원문 diff"*. ★**verifier가 실제 BP를 한 번도 안 보고 PASS를 줄 수 있다.**
★★**그리고 S2의 `AU-F0a-03`도 문자 그대로 같은 문구였다** — Part A/B 분리의 명분이 **게이트 문구 수준에서는 한 번도 고쳐지지 않았다.**

★**정정**: verifier는 Part A의 경로를 **주소로만** 쓰고 ★**자기 세션에서 직접 재호출**한다 — `find_nodes`(총수 재확인) · `get_node_infos`(핀 원문 재확보) · `list_variables`/`get_properties`(변수 속성). ★**`tokens.py`와 selftest도 직접 재확인·재실행**한다(오프라인이라 비용 0).
⚠ `184`(수술 전 베이스라인)만 예외 — 재현 불가능하므로 S2 게이트 기록과 대조한다.

---

## 실행 순서 — 9단계 (qa 설계)

★**경계 원칙 3가지**: ①중간 상태는 항상 **"컴파일되고 실행되지 않는" 고아 섬** ②★**arm last** — 부착 연결(`Sequence.then_0 → N1`)을 **맨 마지막(D7)**으로 민다 ③비가역성을 늦게 배치.

| 단계 | 무엇 | 검증 |
|---|---|---|
| **D1** | ★**조회 전용** — `BattleState` 타입·`TurnQueue` 타입·생성 문자열 선탐색 | 정적. ★**F1을 여기서 닫는다** |
| **D2** | 변수 `bAutoStartBattle` 신설 | 정적 (★선례 있음 — `E0_프로브`에서 같은 BP에 `bInputLocked` 성공) |
| **D3** | ★**고위험 노드 2건**(N17 → N1) | 정적 |
| **D4** | 잔여 15 + 핀값 7 | 정적 |
| **D5** | 데이터 연결 7 | 정적 |
| **D6** | exec 연결 9 (★**부착 제외**) | 정적 |
| **D7** | ★**무장 + 스모크** | ★**PIE 1회 — 여기뿐** |
| **D8** | 저장·봉인 | 정적 |
| **D9** | 오프라인(토큰 등록·selftest) | 오프라인 |

★**PIE는 D7 1회뿐**이다 — director 원안 대비 **PIE 증가 0**. 추가 비용은 컴파일 6회 + 재조회 6배치뿐이다.

### ★gameplay-engineer의 절차 정정 (D4/D5 순서)

함정104: 연산자 노드는 ★**와일드카드 A/B 핀 — 연결 후 자동 승격**. 그런데 원 절차는 **핀값 → 연결**이다.
→ ★**`N8(Greater)`은 연결 먼저, 리터럴 나중**. D1 선탐색에서 N8이 와일드카드인지 판정하고 순서를 분기한다.

### ★생성 문자열 — `Delay`가 진짜 위험

S1 실측 `RetriggerableDelay` = `유틸리티|플로컨트롤|RetriggerableDelay`(카테고리 **한글** + 이름 **영문**)
함정109 `Sequence` = `Utilities|FlowControl|시퀀스`(카테고리 **영문** + 이름 **한글**)
→ ★**같은 카테고리 형제끼리 혼합 방향이 정반대**다. ★**`RetriggerableDelay` 패턴을 `Delay`의 힌트로도 쓰지 마라.** 두 세그먼트를 독립적으로 확정한다.

---

## 게이트 체계 — 2층

| 층 | 무엇 | 주체 | 성격 |
|---|---|---|---|
| **단계 TC** `AU-FSTP-01~35` | 9단계 각각 | **engineer 자가확인** | ★**게이트가 아니라 정지선** |
| **최종 게이트** `AU-FAS-01~06` | 완성된 201노드 1회 | ★**verifier(별도 세션)** | ★**게이트** |

★**단계 TC는 최종 게이트를 대체하지 않는다.** ID 충돌은 전수 grep으로 확인됐다(`AU-FASp`·`AU-FSA`는 규약 위반으로 기각).

---

## ★오너 확인 포인트 (verifier 구체화)

★**왜 오너인가**: 에이전트 PIE는 **tick 3** 고정이다. ★**3fps에선 `Delay(0.1)`이 "정확히 1틱"으로 뭉개져 관측 폭이 좁다.** 60fps에선 같은 0.1초가 여러 틱에 걸친다.

### 포인트 ① — D7 스모크 후, BP 그래프 육안

- [ ] `BeginPlay → PrintString(마커) → Sequence` 체인이 보이는가
- [ ] `Sequence.then_0` → `Delay` → **가드 4단** → `NotifyAttackButtonClicked` 흐름이 이어지는가
- [ ] ★**`then_1`이 빈 채인가** (S5 예약 — 뭔가 붙어 있으면 잘못됨)
- [ ] 컴파일 에러 **0**
- [ ] 내 변수에 `bAutoStartBattle`, ★**Instance Editable(눈 아이콘) 켜짐**
- [ ] ⚠ ★**아무것도 저장하지 말 것**

### 포인트 ② — ★on-런 60fps (핵심)

액터 선택 → 디테일에서 `bAutoStartBattle` 체크 → PIE:

- [ ] ★**클릭 없이 전투가 시작되는가** — S3의 전부
- [ ] ★**`AwaitCommand`에서 멈추는가** — MA 훅이 없으므로 **멈추는 게 정상**. 진행하면 ★**정지선 3**
- [ ] ★**멈춘 뒤 직접 스킬/공격을 선택해 정상 진행되는가** — ★**사람만 판정 가능**(에이전트는 그 지점 이후를 조작 못 한다)
- [ ] ★**`FIRE`가 `INIT` 뒤, `TurnStart` 앞인가** — 60fps에서 `Delay` 가정을 **다른 시간 해상도로** 재확인
- [ ] ⚠ PIE 종료 후 ★**체크박스를 반드시 끄고**, ★**레벨 저장 금지**

### 포인트 ③ — 원복·오염 확인

- [ ] `bAutoStartBattle`이 ★**false**인가
- [ ] ★**제목표시줄에 레벨 `*`(미저장)가 있으면 저장하지 말고 알려주세요**
- [ ] `set_properties` 실패로 **폴백(디테일 패널 직접 클릭)**을 썼다면 — 원복했는지 특히 확인

⚠ 착수 전 ★**에디터를 껐다 켜 주세요** — `BP_BattleManager`가 인메모리 dirty입니다(S1 프로브 흔적, 디스크는 깨끗).

---

## 정지선 (원 7건 + 보강 3건)

| # | 조건 | 보고처 |
|---|---|---|
| 1 | on-런 `GUARDFAIL` ≥1 | PM → director. ★**BP 디버깅 금지**, 로그만 |
| 2 | `FIRE` ≥2 | PM → director |
| 3 | FIRE 1인데 `AwaitCommand` 미도달 / 초과 진행 | PM → director. ★**라이브 전투 로직은 경계 밖** |
| ★4 | **off-런 `TurnStart` ≥1** | ★**즉시 오너** |
| ★5 | git에 `.umap` M | PM → 오너. ★**커밋 절대 금지** |
| 6 | 컴파일 에러 / 화이트리스트 외 변화 | PM |
| 7 | `add_variable` 실패 / 생성 문자열 0건 | PM → director |
| ★**8**(신설) | **off-런 `GUARDFAIL` ≥1** | PM → director (극성 반전 의심) |
| ★**9**(신설) | ★**on-런 완전 침묵**(FIRE 0 ∧ GUARDFAIL 0) | ★**먼저 `get_properties`로 override 확인** → 그 후 배선 의심 |
| ★**10**(신설) | 스모크 PIE에서 `Accessed None` ≥1 | PM (★`save_assets` **직전** 차단) |

---

## 검증 (PM이 직접)

```bash
git -C "D:/unreal/projectTP/Content" -c core.quotepath=false status --porcelain
```
```bash
cd "D:/unreal/Resource" && python docs/scripts/battle_log_selftest.py
```
```bash
cd "D:/unreal/Resource" && node docs/scripts/vaultlint/vaultlint.ts docs
```

- ★**Content에 `.uasset` 1개만 M, `.umap` 부재**
- ★**selftest 39/39 + 신규 전량 PASS**
- ★**vaultlint 0 errors** — 커밋 전 린터는 `CLAUDE.md` 규약
- ★**커밋 직전 `git -c core.quotepath=false diff --cached --name-only`에 `.umap` 부재**
- ★**로그는 PIE Stop 이후에 읽는다**(flush 미완료로 말미가 누락된다 — verifier 지적)
- ★**각 PIE 런 직후 `up for play` 라인 번호를 즉시 기록**해 구간을 고정(함정101 변종)

## 실행 계획

1. ★**qa 산출물을 파일로 확정** — `docs/features/스킬연출구조/raw/FT1-S3_TC.md`(본문은 이미 완성돼 있다)
2. ★**착수 전 정정 5건을 착수판정 문서에 반영**(F1~F5)
3. **D1~D9 발주**(gameplay-engineer) → ★**오너 포인트 ①②** → **Part B 발주**(verifier, 별도 세션) → 포인트 ③
4. Part C(PM): 세이브포인트 · 커밋 분리 · 문서 갱신 · push는 오너 확인

★**plan을 wiki에도 남긴다**(오너 지시) — `.claude/plans/`는 git 밖이라 이력이 없다.

## 이 계획이 끝나면

**S4(MA 훅 + 시나리오)** — FT1 핵심 게이트 **MA-1a**(자동 20턴 ↔ 오라클 전 행 diff 0).
★S4 첫 스텝 이월: `ResolveSlotToActor` 슬롯 원천 1회 조회.
