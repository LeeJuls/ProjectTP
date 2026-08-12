---
type: plan
project: projectTP
updated: 2026-08-12
status: 오너 승인 완료 — 착수
---

# LOG-A — 로그 파싱 계약 단일화 + 오라클-diff 비교기

## Context

**왜 지금인가**: 오너가 *"문제 해결을 위해 로그 남기는 거 상태를 점검해줘"*라고 지시했고, 점검 결과 **로그 내용은 쓸모 있는데 파싱 계약이 없다**는 것이 드러났다. 그리고 어제 **로그 파싱으로 43% 불확실성을 닫은 실적**(턴 예산 3.0s → 2.100s 확정)이 그 가치를 증명했다.

**무엇이 막혀 있나**:
- `BattleLog|`(pipe) vs `State:`(colon) vs `Align:`(colon, **위치 기반**) — 문법 3종 공존
- 로그 `attacker=SpawnPoint_Party_A3` ↔ 오라클 `A3` — **조인 미구현**
- `attacker_job`/`target_job` — ★**로그에 없고, 조인표 데이터 소스도 없다**
- **오라클-diff 비교기가 미구축** — F7b ⑦ 게이트의 도구인데 존재하지 않는다
- `extract_battle_log.py`가 3주 정지 — MARKER 고정으로 6개 문서가 *"스크립트 수정 대신 별도 grep"*을 반복 선택한 드리프트

**결과물**: S1 봉인(오너 20턴 런)을 **그 자리에서 판정**할 수 있는 비교기. ★이게 없으면 오너가 20턴을 돌리고 며칠 뒤 *"다시 해주세요"*가 될 수 있다.

**선행 판정**: [[로그시스템_개선_plan]](director 4차) — 새 트랙 없이 BT2 확장으로 용해. 순환 없음 확인.

---

## ★설계 결정 1건 (PM 판정 — 반대하시면 말씀 주세요)

**job 조인표를 어디서 얻나** — 전수 조사 결과 **기계 판독 가능 파일이 없다.**

| 후보 | 결과 |
|---|---|
| `positions_초안.csv` | ✗ 탱/딜/서폿 아키타입 마스터 — 슬롯 개념 없음 |
| `job_stats.csv` | △ 키가 캐릭터 Id(`10102000`)라 `A1` 문자열이 없다 |
| `data/` 14개 CSV 전수 | ✗ `SpawnPoint_Party_A1`을 담은 CSV **0개** |
| **`SPD원장_오라클_v1.md` §0 27행** | ★**유일 정본** — 산문 표 |

**→ 판정: (a) 오라클 §0 표를 파싱해 유도한다.**

근거: `AU-B2-03`이 금지한 것이 *"조인표가 하드코딩이면 오라클 §0 재유도 시 **무음 스테일**"*이다. **정본을 직접 읽으면 그 위험이 원천 소멸**한다. 사이드카 CSV 신설(b)은 **정본을 둘로 만들어** 방금 `extract_battle_log.py`에서 대가를 치른 드리프트를 재생산한다. 인자 주입(c)은 호출 시점 실수 위험.

★**기각**: `job_stats.csv`의 Atk/Def로 dmg를 역산해 직업 추론 — **채점 대상(dmg)으로 채점 기준(job)을 만드는 순환**이라 오라클 §0.5 blind 유도 선언에 위배.

**취약점 보완**: 마크다운 표 파싱이 실패하면 **fail-loud**(빈 조인표로 진행 금지).

---

## 작업

### 파일

| 경로 | 무엇 |
|---|---|
| `Resource/docs/scripts/battle_log/__init__.py` 등 (신규 모듈) | ★**ingestion 공용 모듈** — 파싱의 단일 소스 |
| `Resource/docs/scripts/oracle_diff.py` (신규) | 비교기 CLI |
| `Resource/docs/scripts/extract_battle_log.py` (개조) | 모듈의 thin wrapper로 |
| `Resource/docs/전투로그.md` (신규 또는 갱신) | grep 커맨드 세트 통합 + **토큰 계약서** |

### ① ingestion 공용 모듈

**재사용**(`extract_battle_log.py`에서):
- `find_log_files()` mtime 정렬 + `--all` 롤오버 처리 (40–46행)
- 출력 헤더 3줄 `# source` / `# extracted` / `# lines` (62–64행)
- `Saved/` 출력 규약(`.gitignore` 대상 — 레포 오염 방지, 의도된 설계)
- `errors="replace"` 관용 읽기 (51행)

**폐기**:
- `MARKER` 단일 문자열 (37행) → **토큰 목록**으로
- `LOGS_DIR`/`OUT_DIR` 하드코딩 (35–36행) → 인자화(비교기는 임의 두 파일을 받아야 한다)

**신규**:
- ★**라인 프리픽스 분리** — `[2026.08.11-22.32.06:160][596]LogBlueprintUserMessages: [BP_BattleManager_C_0] ` 를 스트립. **R-3 음성시험의 대상이 정확히 이것**
- **pipe key=value → dict** 파싱 (`BattleLog|`·`State|`·`StatusLog|`)
- ★`Align:`은 **위치 기반**(`Align:<라벨>:yaw=<값>`)이라 별도 규칙. 필요 없으면 스코프 밖으로 명시
- ★**`died` 위치 가변** — `effect` 3필드 유무에 따라 6번째↔10번째. **위치 파싱 금지, dict 필수**

### ② 오라클 매핑 (`AU-B2-03` 5건)

| # | 변환 |
|---|---|
| 1 | `SpawnPoint_Party_A1` → `A1` (접두어 스트립) |
| 2 | `SpawnPoint_Enemy_B1` → `B1` |
| 3 | `died=true` → `died` 열 = **스트립된 target 값** / 필드 부재 → `""` |
| 4 | `hp` → `target_hp_after` (리네임) |
| 5 | ★`attacker_job`/`target_job` → **오라클 §0 파싱 조인**(위 설계 결정) |

부수: `turn` → `T` 리네임. `dmg`는 **RAW 계약**(치유 음수 `-33`, 오버킬 원시값) — 무변환.

### ③ 비교기 (`AU-B2-01/02` + R-3)

- **AU-B2-01**: 오라클 §7 20행 그대로 입력 → diff 0 ∧ 종료 코드 0
- **AU-B2-02**: 변조 3종 — (a)행 삭제/추가 (b)값 변조(`T13 dmg 36→35`) (c)순서 뒤바꿈(`T8↔T9`) → **3/3 검출 ∧ 첫 불일치 행 번호 출력**
- ★**R-3 음성시험**: *"연출 타이밍만 다른 두 로그 → diff 0"*
  → ★**픽스처가 싸다**: 기존 `battle_*.log` 1개의 **프리픽스만 치환**하면 된다. 별도 런 2회 불필요

### ④ 불변식·고지 (`AU-B2-04/05/06`)

- **04**: `action` 전 행 == `31000000` ∧ `berserk` 부재 또는 1.0 → 위반 시 FAIL
- **05**: 산출물에 ★*"`attacker`·`target` 열은 판정력이 없다"* 명시. 실질 판정 열 = `dmg`·`hp`·`died`·행수
- **06**: 미지 필드(`effect`·`effectRoll`) 무시 ∧ 파싱 예외 0. **단 `berserk`는 04로 검사**

### ⑤ 토큰 계약서 + ★카테고리 체계 + grep 통합

`전투로그.md`에:
- **신규 토큰 문법 확정** — `SessionBoundary|`·`PlayAttack|`·`SkillSelected|`. ★**pipe key=value**(점검 §4-1 권고). `sid` = 세션 내 불변·세션 간 유일
- 흩어진 grep 커맨드 세트 통합(6개 문서가 각자 들고 있던 것)
- ★**"언제 돌리는가"** — 추출기가 3주 정지한 원인이 **실행 습관**이다. **검증 게이트 통과 시점 자동 실행**으로 규약화

---

## ★★로그 카테고리 체계 (오너 결재 — 수명 기준 4종)

> 오너: *"나중에 개발 완료돼서 필요 없는 로그는 안 남기게 할 수도 있어야 하니 **카테고리화를 사전에 계획**해줘"*

**수명이 곧 카테고리다** — *"언제 끌 것인가"*가 분류 기준이므로, 개발 완료 시 **재분류 없이 바로** 끌 수 있다.

| 카테고리 | 수명 | 기본값 | 무엇 | 세션당 |
|---|---|---|---|---|
| **LEDGER** | ★**영구** | **ON** | `BattleLog\|` · `StatusLog\|` · **`SessionBoundary\|`**(신규) | ~38 |
| **FLOW** | 알파~베타 | **ON** | `State:` · `State\|` · `Registered:` · `UnitClicked:` · `ExecWalkPhase:` · **`PlayAttack\|`**·**`SkillSelected\|`**(신규) | ~260 |
| **STAGE** | 개발 중 | **ON** | `Align:` 320 · `VFXSetup:` 160 · `Walk*` · `Cam*` · `TakeHit*` · `FXLAB:*` | ~700 (**전체 70%**) |
| **DIAG** | 일회성 | ★**OFF** | 임시 진단(`FXLAB:DIAG` 등) | 소수 |

**판정 근거**:
- ★**`SessionBoundary`는 LEDGER다** — 원장을 파싱하려면 세션을 갈라야 하므로 **원장과 수명이 같다.** FLOW로 두면 FLOW를 끄는 순간 원장이 파싱 불능이 된다
- ★**DIAG 기본 OFF** — 임시 진단이 켜진 채 남아 로그를 오염시키는 걸 구조적으로 막는다. 실제로 `FXLAB:DIAG`가 그렇게 남아 있다
- **LEDGER는 토글을 주되 끄지 않는다** — 밸런스 회귀·오라클 대조의 근거다. 문서에 *"끄면 S1·MA-1 검증이 불가능해진다"* 경고 명기

### ★구현 — `PrintString.bPrintToLog` 핀에 bool 연결

오너 결재: **에디터 체크박스**(Instance Editable bool 4개, 레벨에서 조절).

```
BP_BattleManager / BP_BattleSpawnPoint 각각:
  bLogLedger : bool = true    (Instance Editable, Category="Log")
  bLogFlow   : bool = true
  bLogStage  : bool = true
  bLogDiag   : bool = false
        ↓
  PrintString(Text, bPrintToScreen=false, bPrintToLog=◄ 여기에 연결)
```

★**이 방식이 이긴 이유 — exec 체인을 안 건드린다**:

| 방식 | 신규 애셋 | 노드 추가 | exec 체인 |
|---|---|---|---|
| ★**`bPrintToLog` 핀 연결** | **0** | **0** | ★**무접촉** |
| 커스텀 `TPLog()` 함수 | 함수 라이브러리 1 | 호출부마다 교체 | 교체 = 절단·재연결 |
| enum 기반 스위치 | **UEnum 애셋** | 〃 | 〃 |

★**enum은 애초에 불가에 가깝다** — `BlueprintTools.create`로 비-Blueprintable(UEnum)을 만들면 **블로킹 모달로 MCP가 마비**된다(함정㉓ 실증). 오너 수동 생성이 필요해진다.

### ★★부수 이득 — carve-out이 축소된다

`PrintString`이 **이미 있는** 호출부는 **핀 1개 연결**로 끝나므로 **exec 절단이 0**이다.
→ plan v2 §5 제약 1(*"기존 exec 절단 0"*)의 **carve-out이 기존 15종 이관에는 불필요**해진다.

**splice가 필요한 것은 신규 3종뿐**(`SessionBoundary`·`PlayAttack`·`SkillSelected` — 노드를 새로 넣어야 하므로). carve-out 범위를 **그 3곳으로 한정**한다.

### 이관 범위 — 오너 결재: **신규부터 점진**

| 시점 | 무엇 |
|---|---|
| **이번(LOG-A)** | ★**체계 확정 + 문서화만.** 코드 0 |
| **FT1-0** | 신규 3종을 **처음부터 카테고리 체계로** 심는다(bool 4개 신설 포함) |
| **이후** | 기존 15종은 **그 BP를 어차피 건드리는 단계**(D6 등)에서 핀 연결로 같이 이관 |

★**라이브 수술 횟수가 안 늘어난다**는 것이 이 순서의 핵심이다.

---

## ★TC 문서 오류 정정 (구현 전 필수)

`자율진행_TC.md` **152행**이 *"라이브 로그 실포맷"*이라며 든 예시가 **실측과 3곳 다르다**:

| 축 | 152행 | 실측 |
|---|---|---|
| `action` | **`SLASH`**(문자열) | ★**`31000000`**(숫자 skillId) |
| `dmg` | 45 | 실측 집합 {30,32,34,36,42,61,65,0,-33} — **45 없음** |
| `died` 위치 | `hp` 뒤 | effect 있으면 **10번째** |

★**같은 문서 160행(AU-B2-04)은 숫자를 요구한다** — 자기모순이다. **152행만 스테일.**

→ 구현 전에 152행을 정정하지 않으면 **파서가 `action`을 문자열로 가정**한다.

**부수**: `action` 형식이 3세대 변천(`ATTACK1` → 숫자). **7/7 이전 로그는 AU-B2-04 자동 FAIL** → BT5 (a)안 검문에 이 축 추가 필요(이미 (c) 확정이라 실무 영향은 없으나 기록).

---

## 검증

### 게이트 (전부 `M` 주체 — MCP 불요, 지금 실행 가능)

| # | 항목 |
|---|---|
| 1 | `AU-B2-01` ~ `AU-B2-06` **전 PASS** |
| 2 | balance R-3 음성시험 **diff 0** |
| 3 | ★**리포에 `BattleLog|` 파싱 구현이 정확히 1곳** (`grep -rn "BattleLog|" docs/scripts/`) |
| 4 | 토큰 계약서에 신규 **3종** 문법 실재 |
| 5 | `extract_battle_log.py`가 wrapper로 동작 — 기존 출력 포맷 **바이트 동일** |
| 6 | ★**카테고리 표에 현행 15종 + 신규 3종이 빠짐없이 배정**됨(누락 0) |
| 7 | ★**ingestion 모듈이 카테고리별 필터를 지원** — `--category LEDGER` 등. STAGE를 끈 로그도 파싱 가능해야 한다 |

### 실행 방법

```bash
python Resource/docs/scripts/oracle_diff.py --oracle <오라클CSV> --log <battle_*.log>
```

★**라이브 대조는 아직 못 한다** — 실측 확인: 현존 로그 중 **오라클 §7과 대조 가능한 런이 하나도 없다**(`projectTP.log`에 `turn=1`이 7번 = 7개 세션이 섞여 있고 분리 수단이 없다). `AU-F1-01a`·`AU-F5-03`은 **S1 런 산출 후**에 열린다.

**이번 게이트는 자가시험 전용**이고, 그게 BT2의 원래 정의다.

---

## 범위 밖 (이월)

| 항목 | 사유 |
|---|---|
| `PlayAttack`·`SessionBoundary` **실제 심기** | 라이브 BP 수술 → **FT1-0**(S1 봉인 후). 이번엔 **문법만 확정** |
| 스킬 선택 로그(오너 질문 ①) | 〃 → **FT1-0c** |
| `ResolveHit` 내부 로그 | 소비 도구 선행 필요. F7b ④ 검증 시점 재평가 |
| 로그 문법 **소급** 통일 | ★**안 함** — 15종 전부 통일은 과잉. 신규부터 pipe로 |
| `Align:` 320회 | ★**노이즈 아님** — 빌보딩 결함 검증(CT-VF-01~04)의 정식 신호. 파서 스코프에서만 제외 |

---

## 후속 (이 계획 승인 후)

1. **qa-critic append-only 1회** — FT1-0 게이트 TC화 + 토큰 계약서 검토. ★전원 라운드는 **과잉**(director 규모 판정)
2. **plan v2 문서 갱신** — BT2 행 확장 / FT1에 FT1-0 편입 / ★**의존 그래프에 `BT2 → 세션 1b 판정` 엣지 추가** / §5 제약 1 carve-out(취소선+사유) / §6 1b에 로그 사본 절차
3. **오너 고지 2건** — carve-out 문구, 1b 절차 1줄
4. 조회 세션에 2항목 편승 — `BeginPlay`·`PlayAttack` 그래프 형상(FT1-0 설계 입력)
