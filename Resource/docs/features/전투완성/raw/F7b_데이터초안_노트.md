---
type: design
project: projectTP
feature: 전투완성
agent: balance-designer
updated: 2026-07-16
status: F7b 데이터 prep 초안 노트 — status_effects.csv/skill_effects.csv/skills_v2_draft.csv 3파일 부속. 라이브 파일(skills.csv/job_stats.csv/strings.csv) 무접촉, 제안만.
source: F7_스킬아키텍처_확정.md §3·§6·§8-7(b)·§9 · data/skills.csv · data/job_stats.csv · data/strings.csv
---

# F7b 데이터초안 노트

> [[F7_스킬아키텍처_확정]](SSOT) 기반 CSV 3파일(`data/status_effects.csv` · `data/skill_effects.csv` · `data/skills_v2_draft.csv`) 초안의 부속 노트. 신규 ID 발급 근거·strings.csv 추가안·job_stats.csv 갱신 제안·검증 계산을 기록한다. **본 문서와 3개 CSV 모두 신규 파일이며 기존 라이브 파일(`skills.csv`/`job_stats.csv`/`strings.csv`)은 무접촉이다 — 아래는 전부 "제안"이지 실제 반영이 아니다.**
> 관련: [[F7_스킬아키텍처_확정]] · [[F7_TC]] · [[상태이상_확정]]
#projectTP/전투완성

---

## 1. 신규 SkillId 발급 근거

| 스킬 | SkillId | 근거 |
|---|---|---|
| 버프후공격 | **31002000** | 지시문("전사 계열 신규 ID — job_stats 31xxx 체계에서 미사용 ID 발급") 그대로 적용. `job_stats.csv` 실측 결과 전사 3등급 전원 `SkillIds=31000000;31001000;33001000` — 31xxx 대역 기사용 ID는 31000000(기본공격,공용)·31001000(베기,전사)뿐. 기존 "+1000 증분" 패턴(31000000→31001000)을 따라 다음 미사용 슬롯 **31002000** 발급. |
| 집중일격 | **31003000**(★가정 — 검증 필요) | 지시문이 이 스킬엔 ID 프리픽스를 지정하지 않음(버프후공격만 "전사 계열" 명시). Category=SKILL(물리 기술)·데미지 전용(마법 요소 없음)이라 31xxx(PHYS kind) 대역이 자연스럽다고 판단해 31002000 다음 슬롯 배정. balance-designer 추론이지 SSOT 명시가 아니므로 **Director/system-ui 확인 필요**. 대안: 직업무관 범용기술 전용 대역 신설(향후 job_stats에 종족/역할 컬럼 추가 시 재검토). |

**검증**: 기존 skills.csv 5개 ID(31000000/31001000/32001000/33001000/34001000)와 충돌 없음.

---

## 2. strings.csv 추가 필요 키 목록

### 2-1. 신규 스킬 (skills_v2_draft.csv 신규 2행)

| Key | ko | 비고 |
|---|---|---|
| `Skill.BuffAttack` | 버프후공격 | |
| `Skill.BuffAttack.Desc` | 자신의 공격력을 25퍼센트 증가시킨 뒤 대상에게 공격력의 100퍼센트 물리 피해. 쿨다운 1턴. | `Skill.Slash.Desc` 문형 준용 |
| `Skill.FocusStrike` | 집중일격 | |
| `Skill.FocusStrike.Desc` | 대상에게 공격력의 100퍼센트 물리 피해. 대상 HP가 50퍼센트 이상이면 피해량이 2배로 증가. 쿨다운 2턴. | |

### 2-2. 신규 상태이상 (status_effects.csv 6행 중 BURN/DEF_DOWN/ATK_UP 3종만 신규 — STUN/ATK_DOWN/DMG_REDUCE는 §2-4 기존 키 재사용)

| Key | ko | 비고 |
|---|---|---|
| `Status.Burn` | 화상 | |
| `Status.Burn.Desc` | 매 턴 시작 시 고정 피해 6을 입는다. 3턴간 지속되며 방어력·막기·광폭화의 영향을 받지 않는다. | STUB(알파 미구현) 서술 그대로 반영 |
| `Status.DefDown` | 방어력약화 | 기존 `UI_BATTLE_STATUS_ATK_DOWN`="공격력약화"와 대구 |
| `Status.DefDown.Desc` | 2턴간 받는 피해가 25퍼센트 증가한다. | STUB(알파 미구현) |
| `Status.AtkUp` | 공격력증가 | |
| `Status.AtkUp.Desc` | 이번 턴의 공격력이 25퍼센트 증가한다. 다음 턴에는 적용되지 않는다. | §8-7(b) 캐스트한정 의미 반영 |

### 2-3. 탭 라벨 4종 (Category 탭 UI, §11-2)

| Key | ko |
|---|---|
| `UI_BATTLE_TAB_ATTACK` | 공격 |
| `UI_BATTLE_TAB_SKILL` | 스킬 |
| `UI_BATTLE_TAB_MAGIC` | 마법 |
| `UI_BATTLE_TAB_DEFEND` | 방어 |

기존 `UI_BATTLE_*` 프리픽스(`UI_BATTLE_TURN` 등) 그대로 계승. `Battle.End`류 ST_UI 키는 별도 담당(④) 몫이라 본 목록에서 제외.

### 2-4. 기존 키 재사용(신규 발급 불요 — 참고용)

| StatusId | NameKey | DescKey |
|---|---|---|
| STUN | `UI_BATTLE_STATUS_STUN`(기존) | 공란(툴팁 미보유, 알파 범위 밖) |
| ATK_DOWN | `UI_BATTLE_STATUS_ATK_DOWN`(기존) | 공란(상동) |
| DMG_REDUCE | `Skill.Block`/`Skill.Block.Desc`(기존 — "기존 막기 재분류"이므로 스킬명 그대로 재사용) | |

IconKey는 6행 전부 공란 처리 — 아이콘 에셋/네이밍 파이프라인이 아직 없음(art-pipeline 영역, balance 권한 밖). 스키마 컬럼은 유지하되 값 발급은 보류.

---

## 3. job_stats.csv SkillIds 갱신안 (제안만 — 라이브 파일 무접촉)

현재(실측):
```
전사(3등급 전원): SkillIds=31000000;31001000;33001000  (기본공격;베기;막기)
마법사(3등급 전원): SkillIds=31000000;32001000;34001000  (기본공격;파이어볼;치유)
```

**제안**: 버프후공격(31002000)은 **전사**에 배정(지시문의 "전사 계열" 명시 + 물리/근접 콤보 컨셉이 전사 아이덴티티에 부합). 집중일격(31003000)은 소유 직업 미확정 — 잠정 전사 후보이나 낮은 확신(§1 참고). 마법사 SkillIds는 변경 제안 없음(신규 2스킬 모두 물리계열이라 부적합 판단).

```
전사(제안, 미반영): SkillIds=31000000;31001000;33001000;31002000  (+버프후공격)
```

**★슬롯 정책 충돌 — 즉시 반영 보류 권장**: `WBP_SkillMenu`는 F7a 기준 **정적 Row 3개**(§11-2 실측)다. 전사 SkillIds에 4번째 ID를 추가하면 F7a의 플랫 3-Row 리스트가 4번째 스킬을 표시하지 못하거나 정적 위젯 가정이 깨질 위험이 있다. **F7b의 Category 탭**(§11-2, "야간 가능" 목록에 포함됨)이 정확히 이 3-슬롯 제약을 해소하는 설계이므로, **job_stats.csv 실 갱신은 Category 탭 UI 게이트 통과 후로 미루는 것을 권장**한다. 그 전에 신규 2스킬을 검증하려면 job_stats.csv를 건드리지 않고 스캐폴드/TC에서 `ApplySkillEffects(Caster, 31002000, ...)` 식으로 SkillId를 직접 주입하는 경로가 더 안전하다(F7_TC의 SCF 판정도구와 정합).

대안(비권장): F7a 상태에서 급히 노출해야 한다면 전사 기존 3슬롯 중 하나(예: 막기)를 임시 교체 — 단 막기는 F7-R04(block 부호 회귀 TC)가 의존하는 슬롯이므로 **교체 비권장**.

---

## 4. 검증 체크 (정답지 불변 확인)

기준: 전사2성 Atk=40·Def=10 / 마법사2성 Atk=42 (job_stats.csv 10102000·10202000 실측치). 공식 `floor(Atk × Value × CondMult) − Def`.

| 스킬 | 계산 | 결과 | 비교 |
|---|---|---|---|
| 기본공격 | floor(40×1.0) − 10 | **30** | 지시문 지정값 30과 일치 |
| 베기 | floor(40×1.3) − 10 = floor(52) − 10 | **42** | 지시문 지정값 42와 일치 |
| 파이어볼(캐스터=마법사, Atk=42) | floor(42×1.7) − 10 = floor(71.4) − 10 | **61** | 지시문 지정값 61과 일치. (검산: 전사 Atk=40 대입 시 floor(68)−10=58로 불일치 → 캐스터가 마법사임을 역으로 확인) |
| 집중일격(HP≥50%) | floor(40×1.0×2.0) − 10 = floor(80) − 10 | **70** | 지시문 지정값 70과 일치 |
| 집중일격(HP<50%, 추가 self-check) | floor(40×1.0×1.0) − 10 | 30 | 지시문 미지정 — 기본공격과 동일(조건 미충족 시 기본공격급으로 회귀, 의도된 트레이드오프) |
| 버프후공격(추가 self-check) | floor(40×(1+0.25)×1.0) − 10 = floor(50) − 10 | 40 | 지시문 미지정 — Timing프루브 손계산 정답지 후보로 제시 |

지시문이 명시한 4개 값(기본 30·베기 42·파볼 61·집중일격≥50% 70) 모두 CSV 데이터로 재현 확인. 집중일격<50%·버프후공격 값은 지시문 미지정이나 self-check로 추가 검증했다. `skill_effects.csv`의 ScaleMode=ATK·Value는 legacy PowerRate(1.0/1.3/1.7)를 그대로 승계했으므로 이 불변은 값 자체가 안 바뀌어 트리비얼하게 성립한다 — 실제 회귀위험은 **공식(소비측)** 쪽에 있다(부호규약 반쪽전환 등, SSOT §8-11에 이미 플래그됨. 본 데이터 prep 범위 밖).

---

## 5. SSOT 내부 정합성 메모 (발견 사항 — Director 인지 필요)

### 5-1. ATK_UP DefaultDuration: §3-5(=2)와 §8-7(b)(=1) 상충 → §8-7(b) 채택

SSOT §3-5 MVP 상태 카탈로그는 ATK_UP `DefaultDuration=2`로 표기하나, §8-7(b)(qa-critic BLOCKER 게이트 최종 정정)는 "ATK_UP 수명 = 캐스트 한정, `Duration=1`"이라고 명시하며 "§6 Director 확정 ⑥의 '당턴 종료 즉시만료 방지' 문구는 캐스트 한정 버프에는 해당 사항 없음으로 정정"이라 밝힌다. §1의 "§8과 §2~§7이 상충하는 서술은 §8이 우선한다" 원칙에 따라 **본 CSV는 `DefaultDuration=1`을 채택**했다(status_effects.csv ATK_UP 행). 이 상충은 SSOT 원문에 남은 미정리 잔재로 보이며, 향후 SSOT 갱신 시 §3-5 표기를 1로 정정할 것을 제안한다.

### 5-2. skills_v2_draft.csv에 ExecPattern 컬럼 미포함

SSOT §3-1은 `DT_Skills` 목표 스키마에 `ExecPattern`(연출 패턴) 컬럼을 명시하나, 본 작업 지시문이 제시한 skills_v2_draft.csv 신규 컬럼 목록에는 ExecPattern이 빠져있다. 지시문을 그대로 따라 8컬럼(Category·HitCount·PrimaryTargetGroup·CastFX·ProjectileFX·ImpactFX·CastSFX·ImpactSFX)만 추가했다 — ExecPattern은 이번 초안에 없다. system-ui-designer/Director가 이 컬럼을 F7b 범위에 포함할지, 별도 후속 작업으로 미룰지 확인 필요.

### 5-3. CooldownTurns(신규 2스킬) — balance 가정치, 미검증

SSOT/지시문 어디에도 신규 2스킬의 CooldownTurns 수치 지정이 없어 balance-designer가 자체 산출했다:

- **버프후공격 = 1턴**: 이번 캐스트에만 국한된 효과라 총 산출은 ATK×1.25(단발, §4 계산 40) — 베기(ATK×1.3+기절25%, 42+CC)보다 약함. 동일 쿨다운(1턴)이면 베기가 상시 우위이므로 **버프후공격은 베기가 쿨다운 중일 때의 대체 필러**로 자리잡는다(기본공격을 완전대체할 위험은 있으나, 베기가 이미 그 역할을 하고 있어 신규 문제는 아님 — 기존 패턴 계승).
- **집중일격 = 2턴**: 조건 충족 시 피해 70(파이어볼 61보다 높음)으로 파이어볼과 동급 쿨다운이 타당. 조건 미충족(HP<50%) 시 30(기본공격급)으로 하락 — **자연 카운터 내장**(상대가 HP를 50% 밑으로 먼저 깎아두면 이 스킬의 가치가 스스로 감쇠하는 "선제 강타형"이라 마무리 용도로는 약함). 파이어볼(디버프 부가효과 보유) 대비 부가효과가 없는 대신 순수피해 상한이 높아 **상호 카운터 관계 성립**(어느 한쪽도 지배전략 아님).

두 값 모두 **검증 필요 플래그** — 플레이테스트/Director 확인 전까지 잠정치.

---

## 6. 관련

[[F7_스킬아키텍처_확정]] · [[F7_TC]] · [[상태이상_확정]] · `data/status_effects.csv` · `data/skill_effects.csv` · `data/skills_v2_draft.csv`
