---
type: gate
project: projectTP
feature: 스킬연출구조
stage: FT1-S3
updated: 2026-08-13
status: PASS
status_note: "director 착수판정 — S3(수술② 1b 자동 시작 토글) 착수 승인. 판정 5건: [가]호출 대상 = StartBattle 직호출 기각 → NotifyAttackButtonClicked 채택(수동 경로와 다운스트림 동일) [나]가드 = 토글(무음)→state==0→qlen>0→lock==false 캐스케이드, qlen이 하중 조건 [다]Delay(0.1) 존치 — 목적 재정의(초기화 대기→BeginPlay 패스 탈출 1틱 양보) [라]토글 = 인스턴스 오버라이드 유일 수단, Part B save_assets 0회 규율로 .umap 오염 기계 차단 [마]S3 대응 TC 부재 실측 → 본 문서가 AU-FAS-01~06 신설(충돌 0 grep 확인). 화이트리스트: 변수 1·노드 17·연결 17·핀값 7(184→201). ★실행 대기 — Part A(수술)/B(실증)/C(판정·커밋) 미수행, 게이트 결과는 실행 후 본 문서 status_note에 추기"
---

# FT1-S3 착수판정 — 수술② 1b 자동 시작 토글 (director)

> 근거 사슬: [[FT1_plan]] §5 S3행(S2 정정 반영분)·§6·§7 · [[FT1-S2_04판정]] §6-1(가드 필수화 — 본 판정의 출발점) · [[FT1-S2_착수판정]] §2(체인 토폴로지)·§3(절차 선례) · [[FT1-S1_조회결과_2026-08-13]] §2(BeginPlay 종단)·§3(Sequence+latent 실측 의미론)·§7(변수 29종) · [[전투BP_현황도_2026-08-11]] §2(상태머신 0~6)·§3(Start 경로) · [[FT1-0_TC]](S3 대응 TC 부재 확인) · [[자율진행_TC]] §4-1(AU-F1-01a/b = S4 영역 확인) · `docs/scripts/battle_log/tokens.py` 실조회 · `projectTP.log`/`projectTP_2.log`/백업 로그 직접 실측(2026-08-13, director) · [[언리얼_MCP_실전노하우]] 함정(99)·(100)·(102)·(103)·(104)·(106)·(107)·(109)
> ★이 문서가 곧 **S3 발주 지시서**다 — Part A(수술: gameplay-engineer) / Part B(실증: verifier) / Part C(판정·커밋: PM). S2 착수판정의 Part 구조·절차 규율을 계승한다.
#projectTP/스킬연출구조

---

## 0. 판정 요약

1. ★**S3 착수 승인.** 오너 차단 0건. **함정99가 이 단계에서 죽는다** — 이후 S4·S5 실증 전부가 이 토글 위에서 돈다.
2. ★★**[가] 호출 대상 = `NotifyAttackButtonClicked`. `StartBattle` 직호출 기각**(§2-가). `BP_AttackButton`은 `ManagerRef.NotifyAttackButtonClicked()` 순수 relay임이 실측돼 있으므로([[전투BP_현황도_2026-08-11]] §1), 이 함수를 부르면 **수동 클릭과 다운스트림이 동일**해진다. 내부 가드(BattleState 비교 + `bInputLocked`)가 한 번 더 방어하는 것도 이득.
3. ★★**[나] 가드 4단 캐스케이드 확정**(§2-나): `bAutoStartBattle`(토글, **False=무음 종단**) → `BattleState==0` → `TurnQueue.Length>0`(★하중 조건 — InitBattle 완주의 유일한 증명) → `bInputLocked==false`. 뒤 3단의 False는 각각 **리터럴 fail-loud**(`MA:AUTOSTART:GUARDFAIL:*` 3종). ★`bAutoStartBattle`은 **현재 부재 — S3이 신설**한다(S1 변수 29종 실측에 없음. 원설계가 기존 변수처럼 읽히는 것을 정정).
4. **[다] `Delay(0.1)` 존치 — 단 목적 재정의**(§2-다). 원목적("초기화 대기")은 S2 실측으로 소멸했으나, latent 재개가 **전 액터 BeginPlay 완료 후**라는 성질이 가드 실행 시점을 액터 순서와 무관하게 만든다 — 엔진 비보장 순서에 대한 보험. 비용 = 3fps에서 ~1틱(≈333ms) 1회, 전 게이트가 카운트·순서 기반이라 무해(함정100).
5. **[라] 토글은 레벨 인스턴스 오버라이드 유일 수단**(§2-라). CDO 인메모리 토글 기각 — 이 세션의 저장 대상이 바로 그 uasset이라 사고 시 폭발 반경이 더 크다. 오염 차단은 규범이 아니라 **기계 절차**로: Part B `save_assets` 호출 0회 + 원복 재조회 인용 + git porcelain `.umap` 부재 인용(§4-5).
6. **[마] S3 대응 TC는 어디에도 없다 — 실측 확인**(§1-마). [[FT1-0_TC]]는 0a/0b/0c/0x/0p뿐이고 [[자율진행_TC]] §4-1 `AU-F1-01a/b`는 MA 본체(S4) 게이트다. 본 문서가 **`AU-FAS-01~06`을 신설**한다(`AU-FAS` 충돌 0, docs 전수 grep). TC 문서 등재는 Part C, qa append-only 검토는 S5 앞 예고분([[FT1_plan]] §10-5)에 병합 권고.

---

## 1. 전제 실측 (판정의 근거 — 전부 이 세션에서 직접 확인)

### 1-마 포함, 축별 실측 결과

| # | 무엇 | 실측 결과 | 출처 |
|---|---|---|---|
| 1 | 가드 변수 실재 | `BattleState`(**정수 0~6**, enum 아님)·`bInputLocked`·`TurnQueue` 실재. ★**`bAutoStartBattle` 부재** — S3 신설 대상 | S1 `list_variables` 29종 + 현황도 §2 |
| 2 | Start 경로 | 상태0(Init)에서 클릭 → `NotifyAttackButtonClicked` → `StartBattle` → `SortTurnQueueBySpd` → TurnStart(1) → AwaitCommand(2). `BP_AttackButton`은 순수 relay | 현황도 §1·§2 표·§3-0 |
| 3 | State 토큰 어휘 | `State\|event=INIT\|mode=FRESH`(pipe) · `State:Init:` · `State:TurnStart:t=` · `State:AwaitCommand:t=` · `State:AwaitTarget` · `State:Executing` · `State:TurnEnd` — 전부 라이브 로그 원문 확인. TurnStart→AwaitCommand는 **같은 프레임**(동기 체인) | 3개 로그 grep 실측(2026-08-13) |
| 4 | `bInputLocked` 부팅 시 상태 | `BLOCKED` 리터럴 발화 **3개 로그 전부 0건** — 수동 Start가 매 세션 통과해 왔으므로 부팅 시 lock=false 방증(직접 실측은 아님 — 가드가 fail-loud로 커버) | 로그 grep + S1 §5(리터럴 미발화 19종) |
| 5 | S2 잔여 상태 | `BeginPlay → PrintString(마커) → ExecutionSequence_0`, `then_0`/`then_1` 빈 예약. EventGraph 노드수 **184** | [[FT1-S2_착수판정]] §2·상태노트 |
| 6 | `Sequence`+latent 의미론 | `then_0`이 latent에 걸리면 그 자리서 정지하고 `then_1`은 같은 프레임 즉시 실행 — **이 프로젝트 실측**(PlayAttack의 ExecutionSequence_0) | S1 §3-ⓒ |
| 7 | S3 대응 TC | **0건.** FT1-0_TC=0a/0b/0c/0x/0p 한정, 자율진행_TC FT1절=MA(S4). qa-critic도 "자동 시작 훅은 별도 단계·별도 게이트"로 예고만 해둠(FT1-0_TC §3-B High) | 두 TC 문서 전수 확인 |
| 8 | 게이트 ID 충돌 | `AU-FAS` — docs 전수 grep **0건**. ★`AU-F1b-*`는 기각 — 기존 `AU-F1-01b`와 동형 문자열(FT1-0_TC §0이 방금 막은 충돌 패턴 재발) | grep 실측 |
| 9 | 토큰 네임스페이스 | `MA:AUTOSTART` 로그 발화 이력 0건(깨끗). [[FT1_plan]] §6이 이 이름을 tokens.py 등록 대상으로 **이미 예약** | 로그 grep + plan §6 |

### 1-A. `INIT`이 먼저 찍힌 뒤 `StartBattle`이 호출되는 순서 — 원설계 게이트와의 정합 (지시서 질문 ④-1)

원설계 게이트 "`INIT→TurnStart→AwaitCommand` 도달"은 **그대로 성립한다.** INIT은 BeginPlay 시점 `InitBattle()`이 찍고(S2 실측), 자동 시작은 그 뒤 상태0에서 `StartBattle`을 태우므로 State 시퀀스는 수동 경로와 동일하다(현황도 §2 상태0 행). 달라진 것은 **INIT과 마커의 상호 순서가 엔진 비보장**이라는 점뿐 — 그래서 게이트의 순서 검사는 `INIT < FIRE < TurnStart < AwaitCommand`로 걸고(§4 AU-FAS-04), **INIT < 마커는 요구하지 않는다**(순서가 뒤집힌 레벨에서도 Delay+가드 덕에 성립하는 시퀀스만 게이트로 삼는다). 원설계에 없던 강화 2건: ⓐ "StartBattle 발화 1회"는 **성공 경로에 로그가 없어 실측 불능**이었다 → `MA:AUTOSTART:FIRE` 마커를 신설해 카운트 가능하게 만든다 ⓑ "AwaitCommand 도달"을 "**도달 후 정지**"까지 검사한다(초과 진행 토큰 0건 — §4 AU-FAS-03).

---

## 2. 설계 판정 4건 (기각안 포함)

### 2-가. 호출 대상 — `NotifyAttackButtonClicked` 채택

| 안 | 판정 | 이유 |
|---|---|---|
| `StartBattle` 직호출 | ❌ 기각 | ①상태 디스패치를 우회 — BattleState가 어긋나 있어도 발화한다(가드가 있어도 이중 방어 상실) ②수동 경로와 갈라진다 — [[자율진행_TC]] `AU-F1-01b`(경로 동치, 오너 1턴 대조)의 대조 폭이 커진다 |
| ★**`NotifyAttackButtonClicked` 호출** | ✅ 채택 | 버튼 액터가 순수 relay이므로 **이 함수 호출 = 수동 클릭의 다운스트림 전체**. 내부 가드(상태 비교+lock)가 한 번 더 방어. 함정99의 벽은 `OnClicked` 델리게이트(발화 불능)이지 이 함수가 아니다 — 같은 BP 그래프에서의 호출은 평범한 함수 호출 |

⚠ **S4 예고 1건**: 이 함수는 상태2(AwaitCommand)에서 `PendingSkillId=31000000` 리터럴 세팅 역할을 겸한다(4역할, 현황도 §3-3). S3은 상태0 가드로 Start 역할만 타지만, **S4 MA 훅 설계는 이 겸용을 다시 만난다** — S4 착수판정에서 처리.

### 2-나. 가드 — 4단 캐스케이드, AND 결합 기각

```
then_0 → Delay(0.1) → [Branch 토글: bAutoStartBattle]
   False → (무음 종단 — 라이브 기본 경로, 로그 0줄)
   True  → [Branch: BattleState == 0]
      False → PrintString "MA:AUTOSTART:GUARDFAIL:state"
      True  → [Branch: Length(TurnQueue) > 0]
         False → PrintString "MA:AUTOSTART:GUARDFAIL:queue"
         True  → [Branch: bInputLocked]
            True  → PrintString "MA:AUTOSTART:GUARDFAIL:lock"
            False → PrintString "MA:AUTOSTART:FIRE" → NotifyAttackButtonClicked()
```

- ★**토글 False는 무음이다.** 원설계처럼 fail-loud를 토글 자체에 걸면 **모든 라이브 부팅마다 오염 라인 1줄**이 남는다 — off는 실패가 아니라 기본값. fail-loud는 "토글을 켰는데 전제가 어긋난" 경우에만.
- ★**`TurnQueue.Length>0`이 하중 조건이다.** `BattleState==0`은 InitBattle **이전**(변수 기본값이 0일 개연 — 미실측, §7-미확인#1)과 **이후**를 구분 못 할 수 있다. 큐를 채우는 것은 InitBattle의 compact뿐이므로(현황도 §2 + `Init ERROR: TurnQueue length is 0` 가드 실재 — S1 §5) **qlen>0 ⇔ 초기화 완주**. 04판정 §6-1의 "`BattleState`/`TurnQueue` 확인" 요구를 이 논리로 구체화한다.
- 각 단이 서로 다른 실패 축을 잡는다: state≠0 = 이미 진행/재진입 · qlen==0 = 초기화 미완(순서 역전) · lock = 입력 잠금 이상.
- **AND 3개+Branch 1개 결합 기각**: 어느 조건이 깨졌는지 로그로 구분하려면 결국 분기·변환 노드가 더 든다. 캐스케이드는 **조건별 리터럴 fail-loud를 변환 노드 0개로** 얻는다.
- ★**값 미동봉의 정직 고지**(함정106 규칙 3과의 긴장): GUARDFAIL 리터럴은 실패 사유만 남기고 값(state 실제값 등)은 안 남긴다. 채택 사유 = 값 동봉은 FormatText+ToText 변환+add_pin이 필요해 첫 배선 수술의 미실측 의존이 3종 늘어난다. 잔여 갭은 주변 로그가 메운다 — state는 직전 `State|`/`State:` 라인, queue는 `Registered:` 카운트로 판독 가능. **lock만 주변 로그에 값이 없다** — GUARDFAIL:lock 발화는 그 자체로 정지선(§6-1)이라 director 진단으로 넘어간다.
- **가드가 통과했는데도 순서가 어긋난 경우**(지시서 질문 ①-3): 가드는 사전 차단이고, **사후 검증은 게이트가 한다** — AU-FAS-04의 라인 순서 검사(`INIT < FIRE < TurnStart < AwaitCommand`)가 "가드 통과 = 초기화 완주 후 발화"라는 주장 자체를 로그 순서로 재검증한다. 가드 오작동(qlen>0인데 INIT 미기록 같은 모순)은 여기서 걸린다.

### 2-다. `Delay(0.1)` — 존치, 목적 재정의 (지시서 질문 ②)

| 안 | 판정 | 이유 |
|---|---|---|
| 제거(BeginPlay 동기 실행) | ❌ 기각 | 오늘 레벨에선 동작한다(S2 실측: Manager BeginPlay 시점 초기화 완주). 그러나 그 순서는 **엔진 비보장** — 역전된 레벨/미래 변경에서 가드가 fail-loud로 죽고 **하네스 전체(S4·S5)가 그 레벨에서 정지**한다. 보험료(1틱)에 비해 손실이 크다 |
| `Delay(0.0)` 교체 | ❌ 기각 | 효과 동일 추정이나 **미실측 엣지**(0초 즉시 통과 최적화 가능성)를 라이브 첫 배선에 넣지 않는다 — S2 기각(b)(add_pin 미실측 회피)와 같은 원칙 |
| ★**`Delay(0.1)` 존치** | ✅ | latent 재개는 **전 액터 BeginPlay 디스패치 완료 후 틱**이므로, Manager/SpawnPoint 어느 순서든 가드 실행 시점엔 동기 초기화(8기 등록→InitBattle)가 끝나 있다 — **가드를 순서 무관으로 만드는 부품**. 원목적("초기화 대기 100ms")은 소멸, 신목적("BeginPlay 패스 탈출 1틱 양보")으로 재정의. 3fps에서 재개가 ~333ms로 늘어나나(함정100) 게이트에 타이밍 값이 없어 무해 |

⚠ 이 "latent 재개 = 전 BeginPlay 후"는 UE 표준 동작이나 **이 프로젝트 직접 실측은 없다**(§7-미확인#2) — on-런 게이트의 `INIT < FIRE` 순서 검사가 실측을 겸하고, 어긋나면 GUARDFAIL:queue → 정지선으로 떨어진다. 단정이 아니라 게이트가 검증하는 구조다.

### 2-라. 토글 수단 — 인스턴스 오버라이드, CDO 인메모리 기각 (지시서 질문 ③)

| 안 | 판정 | 이유 |
|---|---|---|
| CDO 인메모리 토글(기본값 true로 켜고 저장 안 함) | ❌ 기각 | ①**이 세션의 저장 대상이 바로 그 uasset**이다(수술 산출물) — 토글 on 상태에서 저장 1회가 끼면 오염이 커밋 후보에 직행하고, 그 경우 **이 BP를 쓰는 전 레벨이 자동 시작**(오버라이드보다 폭발 반경 큼) ②CDO 인메모리 변경의 기존 인스턴스 전파는 **미실측** — 전파 실패 시 on-런 FIRE 0으로 오진 유발 |
| ★**레벨 인스턴스 오버라이드**(`BP_BattleManager_C_0`) | ✅ 채택 | plan §7-위험6 원안. 디스크의 CDO 기본값은 **항상 false**로 봉인되고, on은 인메모리 오버라이드로만 존재. `.umap`을 **아무도 저장하지 않으면**(아래 기계 절차) 디스크 도달 경로가 없다. AU-F0x-02/04(DIAG 재점화)와 같은 메커니즘이라 절차 자산이 재사용된다 |

**오염 차단 — 기계 절차 스택**(규범 아님, 각각 검증 지점이 있다):

| # | 절차 | 검증 |
|---|---|---|
| 1 | 디스크 기본값 false — Part A가 저장하는 유일본 | Part A §3-3-9에서 CDO 재조회 인용 |
| 2 | 오버라이드는 Part B에서만, PIE 전 set → PIE 후 원복 | set/원복 각각 `get_properties` 재조회 원문 인용 |
| 3 | ★**Part B는 `save_assets` 호출 0회**(저장할 것이 없다 — 오버라이드는 인메모리로 족함) | 보고서에 "save_assets 0회" 명기. 명시 경로 저장만 허용하는 함정102 규율의 강화판 |
| 4 | 세션 말 git porcelain — `.umap` 부재 | 원문 인용(AU-FAS-05). ⚠quotepath 함정: 확인 명령에 `-c core.quotepath=false` 의무 |
| 5 | Part C 커밋 직전 `git -c core.quotepath=false diff --cached --name-only` — `.umap` 부재 재확인 | 커밋 게이트(같은 날 2회 사고 재발 방지 규율 그대로) |
| 6 | 세이브포인트 manifest에 `.umap` SHA256 포함 — 이후 변화 감시 | S2 Part C 선례 계승 |
| 7 | 오너 고지: 에디터에서 **레벨 저장 금지**(인메모리 dirty는 에디터 재시작으로 소멸 — S1 §PM검증ⓒ 선례 문구 재사용) | 오너_대기목록 비차단 항목 |

잔여 위험의 정직 고지: 에디터 수동 "모두 저장"은 막을 수 없다 — #4·#5·#6이 그 경우를 **커밋 전에 검출**하는 최후 그물이다.

---

## 3. Part A — 수술 지시서 (gameplay-engineer, Sonnet, MCP)

### 3-1. 범위와 금지

- **대상**: `BP_BattleManager` — 변수 1개 신설 + `EventGraph`의 예약 `then_0`에 1b 체인 부착. **순수 additive, 기존 노드·핀·연결의 수정·절단 0건.**
- **금지**: `then_1`(S5 예약) 접촉 금지 / 다른 BP·레벨·DataTable 접촉 0건 / **레벨 인스턴스 오버라이드 금지**(토글 조작은 Part B 몫 — 수술 세션은 인스턴스 무접촉) / `save_assets` 빈 리스트 금지(함정102) / `PendingSkillId` 등 기존 변수 값 접촉 금지.
- **세션 배타**: 이 세션 동안 타 발주 MCP 금지(함정23) — PM 보장.
- 사전조건: 수술 전 `git -C D:/unreal/projectTP/Content -c core.quotepath=false status --porcelain` **공백 확인**(원문 인용).

### 3-2. 화이트리스트 (사전 고정 — 이것 외 diff 0이 게이트다)

**변수 1건**:

| # | 이름 | 타입 | 속성 |
|---|---|---|---|
| V1 | `bAutoStartBattle` | Boolean | **Instance Editable = true** · CDO 기본값 **false**(신설 bool 기본값 — 별도 세팅 불요, §3-3-9에서 재조회로 확인) · 카테고리 권장 "MA"(게이트 비대상) |

**노드 17건** (생성 문자열은 ★전부 `find_node_types` 선탐색으로 확정 — 함정104·109. 0건이면 즉시 무필터 전체 나열. 확정 원문을 보고서에 기재):

| # | 노드 | 탐색 힌트 | 용도 |
|---|---|---|---|
| N1 | `Delay` | `유틸리티\|플로컨트롤\|` 추정이나 ★함정109(형제 노드도 로캘 상이 — `Sequence`가 `Utilities\|FlowControl\|시퀀스`였음) — 선탐색 필수 | 1틱 양보. `Duration=0.1` |
| N2 | VariableGet `bAutoStartBattle` | `Variables\|디폴트\|GetbAutoStartBattle` 계열(함정104 표) | 토글 읽기 |
| N3 | Branch(IfThenElse) | 기존 그래프 다수 — 기존 노드 type_id 조회로 확정 가능 | 토글 게이트(False=무음) |
| N4 | VariableGet `BattleState` | 〃 | |
| N5 | 동등 비교(`==`, B=0) | ★`NotifySkillSelected` 진입 가드가 같은 변수로 같은 비교를 한다(현황도 §2 — `Equal(Byte) B=2`) — **그 노드의 type_id를 조회해 동일 타입으로 생성**(제일 안전) | `BattleState==0` |
| N6 | VariableGet `TurnQueue` | 〃 | |
| N7 | Array `Length` | ★`InitBattle`에 실재("length is 0 after compact" 가드) — 기존 노드 type_id 조회 | 큐 길이 |
| N8 | 초과 비교(`>`, B=0) | `유틸리티\|연산자\|` 계열(함정104 — 명칭은 선탐색) | `qlen>0` |
| N9 | Branch | 〃 N3 | state 가드 |
| N10 | Branch | 〃 | queue 가드 |
| N11 | VariableGet `bInputLocked` | 〃 N2 | |
| N12 | Branch | 〃 | lock 가드(True=fail) |
| N13 | PrintString | `개발\|PrintString`(S2 실측 원문) | `InString="MA:AUTOSTART:GUARDFAIL:state"` |
| N14 | PrintString | 〃 | `InString="MA:AUTOSTART:GUARDFAIL:queue"` |
| N15 | PrintString | 〃 | `InString="MA:AUTOSTART:GUARDFAIL:lock"` |
| N16 | PrintString | 〃 | `InString="MA:AUTOSTART:FIRE"` |
| N17 | CallFunction `NotifyAttackButtonClicked`(self) | self 멤버함수 — `find_node_types("NotifyAttackButtonClicked")` 선탐색(자기 BP 함수 생성은 AT4-a self-call 실적 있음) | 발화 |

**연결 17건** — exec 10: `ExecutionSequence_0.then_0→N1` / `N1.Completed→N3` / `N3.True→N9` / `N9.True→N10` / `N10.True→N12` / `N12.False→N16` / `N16.then→N17` / `N9.False→N13` / `N10.False→N14` / `N12.True→N15`. 데이터 7: `N2→N3.Condition` / `N4→N5.A` / `N5→N9.Condition` / `N6→N7.Array` / `N7→N8.A` / `N8→N10.Condition` / `N11→N12.Condition`.

**핀값 7건**: `N1.Duration=0.1` / `N5.B=0` / `N8.B=0` / N13~N16의 `InString` 리터럴 4건(위 표 원문 그대로 — 변형 금지). **그 외 전부 기본값 유지.** PrintString의 bPrintToLog 등은 기본값 그대로(S2 P1 선례).

노드 자동 번호 예측·하드코딩 금지 — 항상 생성 반환 refPath 사용(함정103).

### 3-3. 절차 (순서 고정)

1. **수술 전 베이스라인**: `find_nodes(EventGraph)` 노드 총수(**184 기대** — 다르면 정지·PM 보고) + `ExecutionSequence_0`·마커 PrintString·`K2Node_Event_0` 핀 원문 덤프(보고서 인용).
2. `list_variables`로 `bAutoStartBattle` **부재** 재확인 → `add_variable`(Boolean) → `set_variable_instance_editable(true)` → `list_variables` 재조회로 실재·속성 확인. ★`add_variable` 실패 시 즉시 정지·PM 보고(§6-7).
3. `find_node_types` 선탐색으로 N1~N17 생성 문자열 전부 확정(0건 → 무필터 나열 — 함정109).
4. `create_node` ×17 → refPath 기록.
5. `set_pin_value` ×7 → 각각 `get_pin_value` 재조회.
6. `connect_pins` ×17 → ★**`get_node_infos` 재조회**: `ExecutionSequence_0`(then_0 연결·**then_1 여전히 빈 채**)·신규 17노드·마커·BeginPlay — 화이트리스트 외 연결 변화 0 확인(함정107 규칙 3).
7. `compile_blueprint(BP_BattleManager)` → 에러 0(경고는 개수만 기록, 판정 비사용).
8. **스모크 PIE 1회**(오버라이드 없음 = off 상태): 로그에 마커 1줄 ∧ `MA:AUTOSTART` 0줄 확인만 — ★판정 아님, 판정은 Part B가 새 런으로(구현자 자가검증 금지).
9. `save_assets(["/Game/Blueprints/BP_BattleManager"])` — 명시 경로. → `get_default_object`+`get_properties`로 `bAutoStartBattle` **CDO=false** 재조회 인용.
10. `git -C D:/unreal/projectTP/Content -c core.quotepath=false status --porcelain` → **`BP_BattleManager.uasset` 1파일만 M ∧ `.umap` 부재** 원문 인용.

### 3-4. 오프라인 병행분 (같은 발주, MCP 불요 구간)

- `tokens.py`에 LogRow **2건 추가**(순번은 파일의 현행 마지막+1·+2 — 하드코딩 금지, 편집 시점 확인): ⓐ `MA:AUTOSTART:FIRE` — prefix `("MA:AUTOSTART:FIRE",)`, category **FLOW**, syntax PLAIN ⓑ `MA:AUTOSTART:GUARDFAIL:<which>` — prefix `("MA:AUTOSTART:GUARDFAIL",)`, category **ERROR**(fail-loud 정식 신호 — 15b 선례), syntax COLON_POS. note에 문법 예외 사유 명기: *"colon인 이유 — 고정 리터럴 4종(가변 필드 0)이라 pipe 이점이 없고, BP측 FormatText/변환 노드 0개 유지가 실동기(순번19·20 예외 논리와 동형). 하네스 진단 계열이지 라이브 원장이 아님"*.
- `battle_log_selftest.py` 신규 케이스 2건(기존 **39 무수정**): ⓐ GUARDFAIL 합성 1건 — ERROR 분류 매칭 확인 ⓑ FIRE 자리표시 1건(실측 원문 픽스처 승격은 Part B 후 — AU-FAS-06).
- 실행: `python docs/scripts/battle_log_selftest.py` → 41+/41+ PASS 확인.

### 3-5. 롤백

- **즉시 무력화**: `break_pins`(then_0→N1) 1건 절단 — 체인 전체 고아화, `then_0`이 다시 빈 예약으로 복귀(S2 §3-4와 동형. 변수는 기본 false·미참조라 라이브 무영향).
- **완전 원복**: `delete_node` ×17 + 변수 삭제 → compile → 베이스라인 대비 완전 일치 인용 → 명시 경로 저장. ★**변수 삭제 툴은 미확인**(§7-미확인#3) — 부재 시 변수만 잔존시키고 PM 보고(무해: 기본 false·미참조, 단 "베이스라인 완전 일치"는 미달이므로 보고 의무).
- 저장·커밋 후 원복은 PM/오너 위임(함정102 해법 3 — `git restore` 권한 없음).

### 3-6. 보고 필수

① 전/후 핀 원문(ExecutionSequence_0·신규 17·마커·BeginPlay) ② 노드 총수 184→201 ③ 생성 문자열 원문 17종 ④ 변수 재조회 원문(Instance Editable·CDO false) ⑤ 컴파일 결과 ⑥ 스모크 로그 2줄(마커 유·MA 무) + `max tick rate` ⑦ git porcelain 원문 ⑧ `save_assets` 호출 원문 ⑨ selftest 카운트.

---

## 4. Part B — 실증 지시서 (verifier, Sonnet, MCP — 수술 세션 종료 후 별도 발주)

전제: 레벨 `map_battle_octopath`. 판정 로그 `D:\unreal\projectTP\Saved\Logs\projectTP.log`. 구간 = 엔진 `up for play` 경계(자기 런만 판정 — 함정101). ★**이 세션은 `save_assets` 호출 0회가 규율이다**(§2-라 절차 3). 판정은 전부 카운트·순서·논리값 — 타이밍 값 사용 금지(함정100), `max tick rate` 명기만.

| 게이트 | 무엇을 확인하면 통과인가 |
|---|---|
| **AU-FAS-01** 정적 무회귀 | Part A 보고의 전/후 핀 원문 diff == §3-2 화이트리스트(변수1·노드17·연결17·핀값7) **정확히 그것뿐** ∧ 노드 총수 **184→201** ∧ `then_1` 빈 채 유지 ∧ 컴파일 에러 0 ∧ 변수 Instance Editable=true·CDO=false 인용 실재. 서술만이면 FAIL(원문 인용 의무 — AU-F0a-03 선례) |
| **AU-FAS-02** off 무회귀(행동) | **오버라이드 없이** PIE 1회 → 자기 구간에서: `MA:AUTOSTART` 계열 **0건** ∧ `State:TurnStart` **0건** ∧ `State:AwaitCommand` **0건** ∧ `SessionBoundary\|` **정확 1건**(S2 회귀 유지) ∧ `State\|event=INIT\|mode=FRESH` 1건 |
| **AU-FAS-03** on 발화·도달·정지 | 인스턴스 오버라이드 on(절차 아래) → **PIE 2회** → 각 구간에서: `MA:AUTOSTART:FIRE` **정확 1건** ∧ `GUARDFAIL` 0건 ∧ `State:TurnStart` **정확 1건** ∧ `State:AwaitCommand` **정확 1건** ∧ ★초과 진행 0(`State:AwaitTarget`·`State:Executing`·`State:TurnEnd`·`BattleLog\|` 각 **0건** — MA 훅 부재 상태의 AwaitCommand 정지가 정상, 완주 요구 아님) |
| **AU-FAS-04** 순서 | on-런 각 구간의 **라인 순서**: `State\|event=INIT\|mode=FRESH` < `MA:AUTOSTART:FIRE` < 첫 `State:TurnStart` < 첫 `State:AwaitCommand`. ★INIT과 마커의 상호 순서는 **판정하지 않는다**(엔진 비보장 — §1-A). 라인 번호를 인용 |
| **AU-FAS-05** 원복·오염 0 | 원복 후 `get_properties` **false** 인용 ∧ `git -C D:/unreal/projectTP/Content -c core.quotepath=false status --porcelain` 원문 — `BP_BattleManager.uasset` 1파일만 M ∧ **`.umap` 부재** ∧ 보고서에 "save_assets 호출 0회" 명기 |
| **AU-FAS-06** 파서 통합 | `assign_session_keys`를 실로그에 실행 → on-런 구간에서 FIRE 라인의 키 == **(그 구간 마커의 sid, 1)** 인용 ∧ 실측 FIRE 라인 원문 1건을 selftest 픽스처로 승격(S2 AU-F0a-05ⓑ 방식) 후 재실행 **기존 전량+신규 PASS** |

**오버라이드 절차**(AU-FAS-03 전후): ①on: `ObjectTools.set_properties(BP_BattleManager_C_0, bAutoStartBattle=true)` → `get_properties` 재조회 true 인용 ②런 2회 ③off: set_properties(false) → 재조회 false 인용. ★set_properties의 인스턴스 bool 쓰기는 **이 프로젝트 최초 실측**(§7-미확인#4) — 실패 시 폴백 순서: 1차 CDO 인메모리 토글(단 **이후 어떤 저장도 금지**, 원복·재조회 의무 — §2-라 기각 사유였던 저장 사고 축을 규율로 봉쇄한 한정 사용) / 2차 오너 1클릭(디테일 패널, 비차단 이월). 폴백 사용 시 보고서에 경로 명기.

---

## 5. Part C — PM (verifier PASS 후)

1. **게이트 판정**: §4 표 6건 전부 PASS → S3 통과. 어느 하나라도 §6 정지선에 해당하면 director 재호출.
2. **세이브포인트**: uasset 사본 + SHA256 manifest(**`.umap` 포함** — 감시용).
3. **커밋 분리**: Content — uasset 1파일 `[C] feat(FT1-S3): 자동 시작 토글 bAutoStartBattle+가드 체인(1b)` / Resource — tokens.py+selftest+본 문서 갱신. ★커밋 직전 `git -c core.quotepath=false diff --cached --name-only`에 **`.umap` 부재 확인**(§2-라 절차 5).
4. **push**: Content push는 오너 확인 후(단독 금지).
5. **문서 갱신**: ⓐ 본 문서 status_note에 실행 결과 추기 ⓑ [[FT1_plan]] §5 S3행 완료 처리(frontmatter+본문 동시) ⓒ [[FT1-0_TC]] 또는 후속 TC 문서에 `AU-FAS-01~06` 등재(본 문서를 정본 링크로 — qa append-only 검토는 S5 앞 예고분과 병합 권고, plan §10-5) ⓓ [[전투로그]] §3 표 재생성(`render_category_markdown()` — tokens.py 갱신 규약) ⓔ 기능허브·오너_대기목록(레벨 저장 금지 고지 + push 승인 요청) 갱신.

---

## 6. ★정지선 — 이 결과가 나오면 자율 판단 금지, 즉시 정지·보고

| # | 조건 | 왜 정지인가 | 보고처 |
|---|---|---|---|
| 1 | on-런에서 `GUARDFAIL` ≥1 (FIRE 0 포함) | 순서/상태 전제 붕괴 실측 — S4 전제까지 연동되는 재판정 사안. **BP 디버깅 착수 금지**, 로그 원문만 수집 | PM → director |
| 2 | `FIRE` ≥2 (한 구간) | BeginPlay 단일 진입 구조 가정 붕괴(재진입/이중 발화) | PM → director |
| 3 | FIRE 1인데 AwaitCommand 미도달, 또는 초과 진행(`BattleLog\|` ≥1 등) | 상태머신 이상 — **라이브 전투 로직은 additive 경계 밖**, 접촉 금지 | PM → director |
| 4 | ★off-런에서 `State:TurnStart` ≥1 | 토글 off인데 전투 시작 = 최악 신호(오염 실체화) | **즉시 오너 호출** |
| 5 | git에 `.umap` M 등장(어느 시점이든) | 오염 디스크 도달 — **커밋 절대 금지**, 경로 역추적 필요 | PM → 오너 |
| 6 | 컴파일 에러, 또는 함정107 재조회에서 화이트리스트 외 연결 변화 | 수술 실패 — §3-5 원복 후 정지 | PM |
| 7 | `add_variable` 실패 / 무필터 나열로도 N1·N17 생성 문자열 0건 | 수단 부재 — 대체 설계는 director 몫(우회 시도 금지, 함정99 해법 원칙) | PM → director |

---

## 7. 유효범위 고지·이월·미확인

**S3으로 판정된다**: 함정99 해소(에이전트 단독 전투 개시) · 자동 시작의 1회성·상태 도달·AwaitCommand 정지 · off 무회귀(정적+행동) · S2 마커·세그먼트 파싱과의 통합 · 토글 오염 0(디스크 기준).

**판정되지 않는다(명시)**: AwaitCommand 이후 전 구간(스킬·타겟 주입 — S4) · 수동 클릭 경로 런타임 회귀(MA-3, 오너 이월 유지) · **RESTART 경로 자동화**(BeginPlay 1회 구조상 1 PIE 1전투 — S4 MA-1a는 FRESH 1전투만 쓰므로 비차단, 필요해지는 날 별도 설계) · 타이밍 값 일체(3fps) · 토글의 UI 노출(없음 — 디버그 전용이 의도).

**미확인 목록**:

| # | 무엇 | 처리 |
|---|---|---|
| 1 | `BattleState` 변수의 CDO 기본값(0인지) | 가드가 이것에 의존하지 않게 설계함(qlen이 하중 조건 — §2-나). Part A §3-3-9의 CDO 조회에 1줄 편승 가능(선택, 게이트 비대상) |
| 2 | latent 재개 = "전 액터 BeginPlay 후" 성질의 이 프로젝트 직접 실측 | AU-FAS-04(INIT<FIRE)가 실측을 겸한다. 어긋나면 정지선 1 |
| 3 | MCP 변수 **삭제** 툴 존재 여부 | 완전 원복 시에만 필요 — 부재 시 변수 잔존+PM 보고(§3-5, 무해 확인 포함) |
| 4 | `ObjectTools.set_properties`의 레벨 인스턴스 bool **쓰기**(읽기는 S1 실측) | Part B가 첫 실측 — 실패 시 폴백 2단(§4 오버라이드 절차) |
| 5 | `NotifyAttackButtonClicked`의 상태0 경로가 Start 버튼 UI 숨김 등 수동과 동일한 부수효과를 내는지 세부 | 수동 경로와 같은 함수이므로 정의상 동일 — 차이가 있다면 MA-1b(오너 1턴 대조, 기존 이월)가 잡는다. ★S3 채택(§2-가)으로 MA-1b의 대조 폭이 "호출자 차이"로 좁혀진 이득을 기록 |

## ★8. PM 착수 전 정정 5건 (2026-08-13 append — 위 본문은 무수정)

> ★**이 절이 위 본문에 우선한다.** 오너 지시로 **agents 피드백 → plan upgrade**를 거쳤고(qa-critic·gameplay-engineer·verifier), 착수를 막을 결함 5건이 나왔다. 위 §1~§7은 **판정 이력으로 보존**한다.
> 단계 분할과 단계별 TC는 → [[FT1-S3_TC]]

★**독립 중복 발견 4건**(서로 다른 에이전트가 같은 구멍을 짚었다 = 확실): `Accessed None` 부재 · off-런 `GUARDFAIL` 미커버 · "완전 침묵" 미분류 · off 복원 미재확인.

### ★F1 — `BattleState` 타입 모순 (qa, High)

★**이 문서 안에서 상충한다**: `BattleState`는 **정수**인데 §3-2 N5는 **`Equal(Byte)` 복제**를 지시한다(원출처 [[전투BP_현황도_2026-08-11]] L40 ↔ L52도 같은 모순).
★**실현되면** D5에서 **자동 형변환 노드가 삽입** → 노드 **202** → ★**`AU-FAS-01`이 올바른 구현인데도 FAIL**한다.

★**PM 판정 — director 재호출 불요.** [[FT1-S3_TC]]의 **D1(조회 전용)**이 `AU-FSTP-03`으로 닫는다. ★**단계 분할이 이 문제를 구조적으로 흡수**한다 — 실측 후 N5를 결정하고, 형변환이 필요하면 **화이트리스트를 그때 확정**한다.

### ★F2 — `Delay(0.1)` 존치 근거가 검증되지 않는다 (qa, High)

§2-다의 존치 근거(*"latent 재개가 전 액터 `BeginPlay` 완료 후"*)는 ★**`AU-FAS-04`로 검증되지 않는다(교락).** [[FT1-S2_04판정]] §2가 이미 이 레벨의 순서를 확정했으므로 `INIT < FIRE`는 **Delay 유무와 무관하게 성립**한다.

★**대체 판정식 채택**: **`frame(FIRE) ≠ frame(마커)`**
로그 프리픽스의 프레임 카운터는 `parse_line_meta`가 **이미 추출**하고, ★**이산 정수라 3fps에서 합법**이며 비용 0이다. (랩어라운드 미확인이라 `>`가 아니라 `≠`)

### ★F3 — `Accessed None` 스윕 부재 (qa·verifier 독립 중복, High)

가드가 `TurnQueue`·`BattleState`·`bInputLocked`를 새로 참조한다. `AU-FAS-01`의 *"컴파일 에러 0"*은 **정적**이라 런타임 문제를 못 잡는다. 이 프로젝트는 이미 ★**"`Accessed None` 0건"을 기준선**으로 갖고 있다([[로그시스템_점검_2026-08-12]] §2-4).
→ ★**`AU-FAS-02`·`AU-FAS-03`의 PASS 조건에 `Accessed None` 0건을 추가**한다. 비용 0.

### ★F4 — 정지선 미커버 3종 (qa·verifier 중복, High)

§6 정지선 7건에 다음을 추가한다:

| # | 조건 | 처분 |
|---|---|---|
| ★**8** | **off-런 `GUARDFAIL` ≥1** | PM → director. #1은 **on-런 한정**, #4는 `TurnStart`만 본다 — ★**토글 Branch 극성 반전 시그니처**가 미커버였다 |
| ★**9** | ★**on-런 `FIRE 0 ∧ GUARDFAIL 0`**(완전 침묵) | ★**진단 순서 고정**: 먼저 `get_properties`로 override가 **true로 읽히는지** 확인 → 그 후에야 배선을 의심한다. ★*"사문 체인"*과 *"오버라이드 쓰기 실패"*는 **처분이 정반대**인데 미분류였다. §7-미확인#4(인스턴스 bool 쓰기 최초 실측)와 직결 |
| ★**10** | 스모크 PIE에서 `Accessed None` ≥1 | PM. ★`save_assets` **직전** 차단 |

### ★F5 — `AU-FAS-01`이 문언 그대로면 자가검증이다 (verifier, 최우선)

§4 원문이 *"**Part A 보고의** 전/후 핀 원문 diff"*다. ★**verifier가 실제 BP를 한 번도 보지 않고 PASS를 줄 수 있다.**
★★**그리고 [[FT1-S2_착수판정]]의 `AU-F0a-03`도 문자 그대로 같은 문구였다** — Part A/B 분리의 명분이 **게이트 문구 수준에서는 한 번도 고쳐지지 않았다.**

★**정정**: verifier는 Part A의 경로를 **주소로만** 쓰고 ★**자기 세션에서 직접 재호출**한다 — `find_nodes`(총수) · `get_node_infos`(핀 원문) · `list_variables`/`get_properties`(변수 속성). ★**`tokens.py` 실재와 selftest도 직접 재확인·재실행**한다(오프라인이라 비용 0).
⚠ `184`(수술 전 베이스라인)만 예외 — 재현 불가하므로 [[FT1-S2_착수판정]] 기록과 대조한다.

### 부수 정정 2건 (gameplay-engineer)

- ★**§3-3 절차 5·6 순서** — 함정104상 연산자 노드는 **와일드카드 A/B 핀, 연결 후 자동 승격**이다. `N8(Greater)`은 ★**연결 먼저, 리터럴 나중**. D1 선탐색에서 와일드카드 여부를 판정해 순서를 분기한다.
- ★**§7-미확인#3이 오류다** — `remove_variable`은 이 프로젝트에서 **성공 선례 4건**이 있다([[E3_게이트]]의 `ScaffoldTurnCounter` — 같은 BP 대상 외 3건). 완전 원복이 *"변수만 잔존"*으로 격하될 이유가 없다.
- ★**§7-미확인#4(정지선 7)는 과잉이었다** — `add_variable` bool + Instance Editable은 ★**같은 BP에 선례**가 있다(`E0_프로브` `bInputLocked`, 2026-07-07). 실패 시 정지는 유지하되 **확률이 낮음을 알고 착수**한다.
- ★**`TurnQueue` 타입은 확정돼 있다** — `E0_프로브`가 `BP_BattleSpawnPoint` 오브젝트 레퍼런스 **배열**로 생성했고 [[AT4-b-2_결과_2026-08-12]]가 `ForEachLoop`로 재확인했다(배열 전용 매크로). 근거사슬에 인용이 빠져 있었다.

### 절차 보강 2건 (verifier)

- ★**로그는 PIE Stop 이후에 읽는다** — flush 미완료로 말미가 누락된다. ⚠ **3fps와 "순서 뒤집힘"은 인과관계가 없다**(tick rate는 줄 간 실시간 간격에만 영향) — 진짜 위험은 순서 역전이 아니라 **말미 누락**이다.
- ★**각 PIE 런 직후 `up for play` 라인 번호를 즉시 기록**해 세그먼트 경계를 고정한다. PIE가 최대 3세그먼트인데 **같은 로그 파일에 쌓인다는 보장이 없다**(함정101 변종). 게이트마다 **읽은 로그 파일명을 원문에 명기**한다.

---

## 관련

[[FT1_plan]] · [[FT1-S3_TC]] · [[FT1-S2_착수판정]] · [[FT1-S2_04판정]] · [[FT1-S1_조회결과_2026-08-13]] · [[FT1-0_TC]] · [[자율진행_TC]] · [[전투BP_현황도_2026-08-11]] · [[전투로그]] · [[언리얼_MCP_실전노하우]]
