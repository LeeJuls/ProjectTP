---
type: design
project: projectTP
feature: 전투완성
status: PASS
status_note: director 판정 확정(2026-08-13) — 문서구조_개선plan 3단계의 매핑 SSOT. §4 규칙을 158건 전수에 실행 검증 완료(자동 108/수동 50)
updated: 2026-08-13
tags:
  - projectTP/문서
---

# BT-DOC2 — `status` 134종 → enum 매핑 규칙 (director 판정)

> **결론 3줄**: ① 6종이 아니라 **7종** — `AWAIT_OWNER`를 추가한다(오너 게이트가 상시 존재하는 팀에서 BLOCKED와 섞으면 두 질의가 다 오염된다). ② **BLOCKED는 자동 배정 금지** — 자동 후보 2건을 실측했더니 **전부 스테일**이었다(차단 상태는 나중에 풀렸을 확률이 가장 높은 상태다). ③ 애매하면 **자동 단계에선 수동으로 넘기고, 수동에서도 확신 없으면 WIP** — 원문은 전건 `status_note`에 보존되므로 enum 오판은 "1회 열람 비용"이지 정보 손실이 아니다.
> §4 규칙은 실제 158건에 실행해 검증했다: **자동 108 / 수동 50**. 수동 50건의 사전판정은 §6 — sonnet은 판단 없이 적용만 한다.
> 관련: [[문서구조_개선plan]] · [[BT-DOC1_정본경계설계]]

---

## §1 enum 7종 정의

| enum | 의미 | grep 용도 |
|---|---|---|
| `PASS` | 완결·유효 — 내용을 신뢰하고 인용해도 된다 | 확정 사실 소스 |
| `WIP` | 미완 또는 트랙 진행 중 — 다음 액션이 **에이전트** | "이어받을 일" |
| `DRAFT` | 초안 — 합의·게이트 전. 인용 금지 | 리뷰 대상 |
| `BLOCKED` | 선행 조건으로 정지 — 에이전트가 지금 못 연다. `status_note`에 차단자 필수 | "막힌 것"(순수) |
| `AWAIT_OWNER` | 다음 액션이 **오너**(육안·결재·수동 편집·런) | 오너 세션 준비 |
| `SUPERSEDED` | 후속 문서로 대체 — `superseded_by:` 필수 | 낡은 것 배제 |
| `ARCHIVED` | 역할 종료·동결 — 후속 없음(기각·완료 기능·소멸) | 탐색 제외 |

- **AWAIT_OWNER 추가 근거**: 실측상 "오너 대기"가 상시 8건+ 존재(F9b·D5.5·S1 런·육안 확인…). BLOCKED에 합치면 "에이전트가 풀 막힘" 질의가 오염되고, WIP에 합치면 "오너 세션에 모아갈 것" 질의가 사라진다. 세 상태는 **다음 액션의 주체가 다르다**. 부수 효과: `AWAIT_OWNER` 전건 ↔ [[오너_대기목록]] 정합을 스크립트로 대조할 수 있게 된다(§7 검증 3).
- **의미 규약(type별)**: `plan`·`index` 문서의 status = **그 작업 트랙의 진행 상태** / 그 외(design·record·test·gate 등) = **문서 내용의 유효성**. 게이트 기록이 "PASS"인 것은 게이트가 통과했다는 뜻이지 후속 작업이 없다는 뜻이 아니다 — 후속은 status_note와 status 층 소관.

## §2 오판 비용의 방향 (판정 근거)

| 오판 | 비용 | 실측 근거 |
|---|---|---|
| 거짓 `PASS` | **최대** — 검증 스킵을 유발(이 팀 최대 금기) | E-S2 자가검증 사고 계열 |
| 거짓 `BLOCKED` | 작업이 조용히 영구 정지 — 아무도 재시도 안 함 | ★자동 BLOCKED 후보 2건(`F5_착수지시서`·`상태이상_설계_qa검증`) **전수가 스테일** — 차단은 이미 풀려 있었다 |
| 거짓 `WIP` | 에이전트 1회 열람 후 note로 진실 복구 — 자기 교정적 | status_note가 원문 보존 |

→ 정책: ① PASS는 선두 절 종결 토큰일 때만 자동 ② **BLOCKED 자동 배정 금지**(전건 수동, 실측상 총 2~3건뿐이라 비용 0) ③ 애매하면 자동→수동 라우팅, 수동에서도 애매하면 **WIP로 하향**.

## §3 처리 파이프라인 (sonnet 실행 순서)

```
원문 status 값
 → [0] 원문 전문을 status_note로 복사 (값이 enum 정확일치 6종*이면 생략 가능)
 → [1] M규칙 (수동 라우팅 트리거) → 걸리면 §6 사전판정표 적용
 → [2] A규칙 (자동, 순서 고정·첫 일치 승리)
 → [3] 정오표 override (§5 — 자동 결과를 덮는 확증 스테일 교정)
 → [4] 검증 3종 (§7) → 커밋
```
*enum 정확일치: `완료`→PASS, `초안`→DRAFT, `진행중`→WIP, `active`→WIP, `DRAFT`→DRAFT 등 §4 트리비얼 매핑도 note 생략 가능. **그 외 전건 note 보존 의무.**

## §4 기계 매핑표 (검증 완료 — 스크립트가 그대로 읽는다)

정규식은 Python `re` 기준. `leading` = 값을 `—`·`·`·`,`·`/`·`(` 중 첫 구분자에서 자른 선두 절. `FROZEN` = 정지 폴더(`옥토패스대치`·`기본전투무대`·`턴제전투MVP`·`카메라액션`·`걸어나오기연출`·`방향성1_백업`).

```json
{
  "enums": ["PASS", "WIP", "DRAFT", "BLOCKED", "AWAIT_OWNER", "SUPERSEDED", "ARCHIVED"],
  "manual_triggers": [
    {"id": "M1", "cond": "len(value) > 300", "이유": "산문 대작 — 자기모순 고위험"},
    {"id": "M2", "cond": "'~~' in value or '❌' in value", "이유": "취소선/자기정정 포함 — 사고 클래스 그 자체"},
    {"id": "M3", "regex": "정정", "이유": "정정 이력 포함"},
    {"id": "M4", "cond": "FROZEN 폴더인데 결과가 WIP/BLOCKED/AWAIT_OWNER", "이유": "정지 기능이 진행 중일 수 없다 — 스테일 확정적"},
    {"id": "M5", "regex": "BLOCKER|차단|막힘|착수 대기|진입 조건|선행 조건|선행 필요", "이유": "BLOCKED 후보는 전건 수동(§2)"},
    {"id": "M9", "cond": "A규칙 무일치", "이유": "기계가 추측하지 않는다"}
  ],
  "auto_rules_ordered": [
    {"id": "A1", "target": "SUPERSEDED", "regex": "대체됨|superseded|백업/구버전", "flags": "I"},
    {"id": "A2", "target": "ARCHIVED", "regex_leading": "^(종결|종료|기각)", "regex_any": "오너 기각|트랙 종료 —"},
    {"id": "A3", "target": "WIP", "regex": "(verifier|실증|검증)\\s*대기", "비고": "에이전트측 검증 대기 — AWAIT_OWNER보다 먼저 평가"},
    {"id": "A4", "target": "AWAIT_OWNER", "regex": "오너[^.·—/~]{0,25}?(대기|필요)", "비고": "근접 매치만 — '오너 결정으로 X 이월'(이미 소화된 결정) 오탐을 차단한다. 실측으로 잡은 오탐: 파트1_Start_진행"},
    {"id": "A6", "target": "PASS", "regex_leading": "(PASS|통과|완료|확정|산출|승인|채택|해소|봉인|판정|개정|기록|스냅샷)[\\s\\d\\-:.년월일시경야간()~]*$|^(판정|결재)\\b|^(complete|configured)", "guard": "값에 '진행 ?중|착수 예정' 있으면 → WIP(A6b)", "비고": "날짜·시각 접미사('게이트 PASS 2026-07-16 야간') 허용"},
    {"id": "A7", "target": "WIP", "regex_leading": "^(진행 ?중|active|활성|골격 완료|부분 통과|부분 판정|신설)", "flags": "I"},
    {"id": "A8", "target": "DRAFT", "regex_leading": "^(초안|초판|DRAFT|잠정|provisional)", "flags": "I"}
  ]
}
```

**158건 실행 결과(2026-08-13 실측)**: PASS 79 · WIP 11 · DRAFT 7 · AWAIT_OWNER 7 · ARCHIVED 3 · SUPERSEDED 1 = **자동 108** / **수동 50**(§6). 참조 구현 스크립트는 3단계 착수 시 `docs/scripts/`에 넣는다(운용규약 §8).

## §5 정오표 — 자동 결과를 덮는 확증 스테일 (필수 적용)

frontmatter가 거짓말한 실사례 3건(F4_중단_인수인계·F5-2_TC·야간작업_총결산)이 있는 저장소다. 자동 규칙은 frontmatter만 보므로, **본문·하류 문서로 확증된 스테일은 override로 교정**한다:

| 문서 | 자동 결과 | ★확정값 | 근거 |
|---|---|---|---|
| `전투완성/raw/상태이상_타겟범위_설계안` | AWAIT_OWNER | **SUPERSEDED** → `[[상태이상_확정]]` | 병합 완료 2026-07-14 ([[상태이상_확정]] 모두) |
| `전투완성/raw/상태이상_카탈로그_밸런스` | DRAFT | **SUPERSEDED** → `[[상태이상_확정]]` | 동 |
| `스킬연출구조/청사진` | PASS | **SUPERSEDED** → `[[features/스킬연출구조/plan\|plan]]` | 3슬롯 스테일 — 허브 표1이 명시 |
| `걸어나오기연출/plan` | PASS | **ARCHIVED** | 기능 동결(plan v4 §대상). WF 잔여는 note로 |
| `공격버튼데모/plan` · `raw/D2_구현` | AWAIT_OWNER | **PM 확인** | 7월 완료 기능 — [[오너_대기목록]]에 없으면 확인 소실로 ARCHIVED |

## §6 수동 50건 — director 사전판정 (sonnet은 적용만)

확신도 표기 없는 항목 = 확정. `?` = PM 확인 후 적용.

**루트(7)**: 기획_방향성→**PASS** · 데이터규약_예시→**SUPERSEDED**(→데이터_서버_규약, 정정문이 명시) · 로드맵_버전계획→**PASS** · 알파_개발계획→**WIP**(A1 진행 중인 살아있는 계획) · 오너_대기목록→**WIP**(상시 롤링) · 자율작업배치_2026-07-17→**PASS**(전 트랙 완료) · 자율진행_plan_v2→**WIP**(AT/FT 트랙 진행 중)

**HD2D배경(2)**: 룩_지침_2D타일셋→**ARCHIVED** · 오너_2D배경_튜닝가이드→**ARCHIVED**(둘 다 오너 기각·보존)

**걸어나오기연출(2)**: TC→**ARCHIVED**(동결, W3 이월분 note) · 청사진→**ARCHIVED**(WF 잔여는 note+대기목록 이관 확인)

**옥토패스대치(3)**: plan·배치가이드·청사진→**ARCHIVED**(기능 동결 — "진행중"은 스테일)

**턴제전투MVP(4)**: plan·청사진→**ARCHIVED** · TC→**ARCHIVED**(note: E3 실증 미완인 채 동결) · VFX_임시통합_방침→**ARCHIVED?**(vfx.csv 체계가 사실상 대체 — 방침 잔존 여부 PM 확인)

**스킬연출구조(2)**: E_스파이크_plan→**WIP**(S2 진행 중·S3~S6 재검토 대기) · D5_값배정→**PASS**(note 의무: FxCastId=0 반전 정정 반영 + ★내장트레일 파급 재검토 중 — [[BT-DOC1_정본경계설계]] §5-5)

**전투완성(28)**:
- plan→**WIP**(F9b·S1 오라클 런·F7b 잔여) · 청사진→**PASS**(문서 확정 — 진행은 plan·status층 소관)
- 게이트·실측 기록 → 전건 **PASS**: AU-A1-09 · BP정리_통합명세 · BT3_MA(note: PM 확인 4건) · F5-1_완료 · FT1_착수조회 · qa_스탯공식검토 · 스탯_전투공식_v1 · 야간작업_총결산(정정으로 양건 해소 명시) · 파트2_SPD_완료 · 파트3_연출_완료 · 파트4_라벨힐_완료 · F7_스킬아키텍처_확정 · 상태이상_설계_qa검증(BLOCKER 2건은 [[상태이상_확정]]에서 해소)
- TC 문서 → 전건 **PASS**(TC 확정·게이트 소화 완료. 이월 잔여는 note): F4_TC(★"BLOCKER 5건 판정 필요"는 스테일 — 판정 완료·F4 통과) · F5_TC(동) · F5-2_TC · F7_TC · U단계_TC(★"확정 대기"는 스테일) · 파트1_Start_TC · 파트2_SPD_TC · 파트3_연출_TC · 파트4_라벨힐_TC
- F4_중단_인수인계→**ARCHIVED**(정정 각주로 역할 종료) · F5_착수지시서→**ARCHIVED**(★"착수 대기"는 스테일 — F5 완료)
- F7b_데이터초안_노트→**DRAFT**(라이브 미반영 초안, 유효) · F7b_재개계획_초안→**BLOCKED**(note 의무: 선행=S1 원장 봉인 — 오너 20턴 런은 [[BT5_S1봉인수단_판별]]의 AWAIT_OWNER가 추적. 대기 사유 1건은 문서 1개만 담당)

**방향성1_백업(2)**: 로드맵·알파 → **SUPERSEDED**(원문이 "대체됨" 명시 — 자동 A1이 M3(정정)에 선점된 케이스)

## §7 검증 3종 (3단계 게이트)

1. **재실행 멱등**: 매핑 스크립트 2회 실행 결과 동일 + `Grep "^status: (PASS|WIP|DRAFT|BLOCKED|AWAIT_OWNER|SUPERSEDED|ARCHIVED)$"` = 158/158.
2. **부속 필드 정합**: SUPERSEDED 전건에 `superseded_by:` 존재 · BLOCKED 전건 note에 차단자 존재.
3. **AWAIT_OWNER ↔ [[오너_대기목록]] 전건 대조** — 목록에 없는 AWAIT_OWNER는 PM 보고(스테일 의심. §5 공격버튼데모가 선례).

## §8 `type` 32종 → 9종 (8이 아니라 9 — `gate` 유지)

`gate`(판정 기록)는 이 팀의 판단 이력 자산이라 `record`에 섞으면 "게이트 판정 전체 조회"가 죽는다. enum은 개수보다 안정성 — 슬롯 1개 추가 비용은 0.

```json
{
  "plan":      ["plan", "blueprint", "roadmap", "ops_plan"],
  "design":    ["design", "spec", "decision"],
  "gate":      ["gate"],
  "test":      ["test", "tc", "test-cases", "verification"],
  "review":    ["qa", "review", "codex_review_mirror"],
  "record":    ["raw", "log", "report", "retro", "snapshot", "backup", "investigation", "portfolio", "codex_mcp_connection_mirror"],
  "index":     ["index", "moc", "hub"],
  "reference": ["reference", "guide", "owner_guide"],
  "process":   ["process", "convention"]
}
```
32종 전수 소진 확인(4+3+1+4+3+9+3+3+2=32). 원 type은 정보 손실 없음 — 파일명·status_note가 세부를 이미 든다.

## §9 미확인

- §6 사전판정 중 `?` 2건(VFX_임시통합_방침 · 공격버튼데모 2건)은 PM 확인 후 적용.
- `status:` 없는 51건(209−158)의 신규 부여 규칙은 이 문서 범위 밖 — 3단계 실행 시 type 기본값표(예: record→PASS, plan→WIP)로 sonnet이 제안하고 PM이 스팟 검수.
- 다중행 YAML(`status: |`) 존재 여부 미확인 — 참조 구현이 단일행 가정. 스크립트화 시 파서에 방어 추가.
