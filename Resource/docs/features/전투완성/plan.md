---
type: plan
project: projectTP
feature: 전투완성
stage: F
status: F0 문서화 완료 — F0 TC(qa-critic) 대기, F1~F9 미착수
updated: 2026-07-13
---

# 📋 전투완성(A1) 세부 plan

> 청사진: [[청사진]] · 프로세스: [[개발_워크플로우]] · 승인 원본: `C:\Users\user\.claude\plans\humble-purring-glacier.md`(v3, 전 에이전트 8명 리뷰 반영, git 외부) — 이 문서는 그 F0~F9 스펙을 **실행 가능한 절차**로 전개한 것이다.
> 설계 근거: [[스탯_전투공식_v1]](§8 TakeHit 계약, qa 조건부 GO) · [[모션연결_규칙안]](E1-B 오너 확정, `캐릭터시스템` 폴더 소속)
#projectTP/전투완성

## 스테이지 코드표 (네이밍 규약 §7 의무)

이 기능은 알파벳 **F** 하나만 쓰고 숫자로 하위 단계를 구분한다(다른 기능처럼 여러 문자를 섞지 않음).

| 코드 | 단계 | 성격 | 담당 |
|---|---|---|---|
| *(코드 없음)* | 설계 산출물 — `raw/스탯_전투공식_v1.md`(전투공식·§8 계약, v1)·`raw/qa_스탯공식검토.md`(적대적 검토) + `캐릭터시스템/raw/모션연결_규칙안.md`(E1-B, 다른 기능 폴더 소속·교차참조) | 설계(F0 이전, 규약§7상 기존 문서라 `stage:` 소급 안 함) | balance-designer·qa-critic |
| F0 | 기능폴더+선결 확정 8건(본 문서 포함) | 확정·문서화 | Director+gameplay+qa+balance+art-pipeline |
| F1 | 광폭화 수비상한 재검증(F0과 병렬, F8 게이트) | 검증 | balance-designer |
| F2 | 데이터 부트스트랩(DT_JobStats·DT_Skills·DT_Motions) | 구현 | gameplay-engineer+오너 |
| F3 | 스탯 로드+HP 게이지 | 구현 | gameplay-engineer |
| F4 | TakeHit §8 코어(전체 스켈레톤) | 구현 | gameplay-engineer |
| F5 | 사망·승패(End 상태) | 구현 | gameplay-engineer |
| F6 | 모션 배선(리터럴→데이터 구동, 무변화 회귀) | 구현 | gameplay-engineer |
| F7 | 스킬 확장+쿨다운(슬롯 동적 재바인딩) | 구현 | gameplay-engineer |
| F8 | 광폭화 적용(F1 게이트) | 구현 | gameplay-engineer |
| F9 | 풀 회귀+풀테스트(F9a 기계 / F9b 오너 육안) | 검증 | verifier+오너+전원 |

## 전제 조건 (실행 시작 시 오너 액션 — [[청사진]] 재확인 표기만, 원문은 그쪽)
1. UE 에디터+MCP 기동.
2. 오너 확인 3종: ① struct 3종 수동 생성(컬럼 스펙 = 본 문서 F2절) ② motions 대분류=6 승인(**완료 반영** — 본 세션에서 `data/motions.csv`를 도메인6 Id로 작성함, `_tables.csv` 등록 자체는 별도 실행 대기) ③ (F1이 수치 조정 제안할 경우만) 광폭화 재확인.
3. HP 표시·스킬 입력 = 임시 월드공간(WBP_BattleHUD는 system-ui #1, 임시물 규율: thin·`_A1Temp` 태그·스코프 펜스).
4. 스킬 5종 = v1 구성 그대로.

### 오너 라이브 확인 체크포인트 (오너 지시 2026-07-13 — 게이트 절차 확장)
화면 변화가 생기는 단계는 **[개발 → verifier 실증 → 오너 라이브 확인(PIE) → Director 게이트]**로 확장(기존 [개발→verifier→Director]에 오너 라이브 확인 삽입). verifier 통과 후 Director가 "무엇을 클릭하고 무엇을 관찰하면 되는지" 안내 문구를 준비해 오너에게 제시 → 오너 확인 → Director가 다음 단계 진행을 게이트한다. 상세 표는 [[청사진]] 참고, 아래는 단계별 체크리스트에 반영.

| 단계 | 오너가 보게 되는 것 | 확인 |
|---|---|---|
| F3 | 유닛 8기 머리 위 HP 게이지 첫 등장 | ★필수 |
| F4 | 공격하면 HP가 실제로 깎임 | ★필수 |
| F5 | 사망(쓰러져 고정)·승패 — 한 판이 끝남 | ★필수 |
| F7 | 스킬 4종 사용감(슬롯 선택·타겟팅·모션) | ★필수 |
| F9b | 풀플레이(광폭화 포함)+관찰 포인트 | ★필수 |
| F6 | 회귀 단계 — "달라진 게 없어야 정상" | 선택 |
| F8 | 광폭화 단독 확인 생략, F9b에 묶음 | F9b 포함 |

---

## 단계별 구현 절차

### F0 — 기능폴더+선결 확정 8건
산출물: `청사진.md`(완료)+`plan.md`(본 문서)+qa TC(대기). 8건 확정 내용(v3 리뷰로 이미 방향 확정, 아래는 그 실행판):

① **H1~H3 재확인**: [[스탯_전투공식_v1]] §7-6/§8을 재대조 — H1(막기=지속형, 시전자 다음 자기턴까지)·H2(턴큐 splice 금지, bAlive 플래그+길이불변)·H3(쿨다운은 §8 step9에서 세팅, 감소는 자기 턴 시작) 3/3 이미 v1 본문에 반영 확인됨(재확인 완료, 추가 조치 불요).

② **타겟팅 분기표(확정)**:
| Target 값 | AwaitTarget 동작 |
|---|---|
| `ENEMY1` | 기존 그대로(상대팀 생존자만 하이라이트, 상대팀 클릭 유효) |
| `ALLY1` | 아군(자신의 bIsParty와 동일) 중 **bAlive==true, 자신 포함** 하이라이트(balance 확정 — qa L1 해소) |
| `SELF` | AwaitTarget **스킵** — 스킬 버튼 클릭 즉시 SelectedTarget=자기자신 세팅 후 Executing 직행. 취소창 없음(문서화 완료, 재입력 취소는 지원 안 함) |

③ **8스폰→6템플릿 배정표(확정)**: 양측 미러 구성, **전사2성×2 + 마법사2성×2**(각 팀). `스탯_전투공식_v1.md` §5 손계산표(전2성/마2성 기준값)가 그대로 정답지가 되도록 고정. 스프라이트 외형(`compose_party.py` 산출)과 JobId 배정은 무관계(외형 리소스 재사용, 통계만 신규 필드로 부여).
| 슬롯 | JobId 템플릿 |
|---|---|
| A1, A2 | 전사 2성(`10102000`) |
| A3, A4 | 마법사 2성(`10202000`) |
| B1, B2 | 전사 2성(`10102000`) |
| B3, B4 | 마법사 2성(`10202000`) |

(★Director 확정 2026-07-13: **balance §8-1 배정(A1/A2=전사, A3/A4=마법사)으로 통일** — qa 충돌#1 해소. F9a 원장(광폭화_재검증 §3-1, B1†T5…B4†T23)이 이 배정으로 계산돼 있어 이쪽이 권위. 구 표기(A1/A3=전사)는 폐기.)

④ **`_tables.csv`에 motions 등록(대분류6)**: **오너 승인 완료(2026-07-13 "난 준비 되었어") — 등록 실행됨.** 등재 행은 balance §8-3 문안(`90001100,entity_motions` — 레지스트리 Id는 도메인9 메타 스킴)이 권위(qa 참고#5 해소, 아래 구 제안 Id `60000000`은 폐기):
```
90001100,entity_motions,motions,개체,1,연출,,모션행 참조(프레임수·루프·공격계열). skills.MotionRow→RowIndex
```
(Id 자체는 `_tables.csv`가 쓰는 도메인9 메타 스킴이 아니라 신규 motions 도메인6 스킴 예시 — 실제 등록 시 balance-designer가 `_tables.csv`의 기존 Id 발급 규칙과 맞춰 정정.)

⑤ **§5-5 막기 잔재 문구 정정**: [[스탯_전투공식_v1]] §5-5 "막기 터틀 = 자기만 보호(적1)" 문구가 H1 확정(막기=지속형, 적1 한정 아님) 이전 표현 잔재 — "자기 자신에게 지속형 피해감소, 다음 자기 턴 시작까지 유지"로 정정 필요(balance-designer 소관, 본 문서는 지적만).

⑥ **DYING/BLOCK 정지 메커니즘(신규 치명, art-pipeline 소관)**: 셰이더 프레임 수식이 `floor((Time−TimeOffset)×8) % FrameCount`(모듈러 순환)라 RowIndex/FrameCount 세팅만으로는 "마지막 프레임 고정"이 불가능(시체가 DYING 5프레임을 계속 순환 재생 = 꿈틀거림). **채택안(b)**: 마스터 머티리얼(`M_Sprite_Flipbook_Lit` 계열)에 `bFreeze`(또는 `FreezeFrame`) 파라미터 신설 — true면 UV 계산이 `Time`을 쓰지 않고 고정 프레임(마지막 유효 프레임 = FrameCount−1)을 샘플링. F5(DYING)·F7(BLOCK 지속)가 공통 소비. 기존 8개 MI(idle/run/attack 재생용)는 기본값 `bFreeze=false`로 무회귀. **폴백(c)**: art-pipeline 일정상 불가 시 알파 한정으로 "DYING/BLOCK도 그냥 순환 루프 허용"(품질 타협, Director 재확인 필요).

⑦ **DT_Motions `EndBehavior` 컬럼**: 완료 — `data/motions.csv`(F2 참고)에 반영. `IsLoop`(기존 이진값)은 남겨두고(스키마 축소 없음, "8+1"확장) `EndBehavior`(LOOP/REVERT_IDLE/FREEZE_LAST) 3치 컬럼을 추가로 얹었다. 매핑 원칙: **idle/run류(IsLoop=TRUE 4행)→LOOP, DYING·BLOCK→FREEZE_LAST, 그 외 전부(공격계열 7행+JUMP·HURT·DASH·ROLL)→REVERT_IDLE**. ⚠ JUMP/HURT/DASH/ROLL은 v3 지시문(idle/run=LOOP·공격류=REVERT_IDLE·DYING·BLOCK=FREEZE_LAST)에 명시적 언급이 없어 본 문서가 REVERT_IDLE 기본값으로 판단 — 현재 미사용(HURT 제외) 행이라 실질 영향 없음, 이견 있으면 F2 실행 전 정정 요청.

⑧ **F4 스캐폴드 인터페이스 정의** — 아래 "F4" 절 최상단에 상세 기술(TakeHit 함수 시그니처+로그 스키마). 요지: `TakeHit(Attacker, Target, SkillId)` 3파라미터 함수 + 로그 라인 `BattleLog|turn=<N>|attacker=<Name>|target=<Name>|action=<SkillId>|dmg=<N>|hp=<M>`.


#### TC — F0 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F0][TC-F0-01] | H1~H3 재확인 → v1 §8 L224(막기 지속형)·§7-2 L189(splice 금지·큐길이 불변)·§8 step9 L220+§7-6 L194(쿨 세팅/자기턴 감소) 3/3 문면 존재 | 문서 대조 | 대기 |
| [F0][TC-F0-02] | 타겟팅 분기표 → ENEMY1/ALLY1/SELF 3분기 동작 각각 정의(ALLY1=자신포함 bAlive 생존자, SELF=AwaitTarget 스킵·즉시커밋·취소창 없음) | 문서 대조 | 대기 |
| [F0][TC-F0-03] | 배정표 실재 → job_stats.csv에 10102000(Hp90/Atk40/Def10)·10202000(Hp80/Atk42/Def6) 존재 + 배정표가 측당 전사2+마법사2 미러 | CSV 조회 | 대기 |
| [F0][TC-F0-04]★ | 배정표 슬롯순서 단일화 → plan §F0③(A1/A3=전사)과 balance §8-1(A1/A2=전사) **불일치 해소** — F9a 원장(§3-1)이 쓰는 balance §8-1로 통일 확정 | 문서 대조 | 대기 |
| [F0][TC-F0-05] | motions.csv EndBehavior → 17행에 LOOP/REVERT_IDLE/FREEZE_LAST 3값 실재, Row5=REVERT_IDLE·Row13(dying)/Row15(block)=FREEZE_LAST 매핑 | CSV 조회 | 대기 |
| [F0][TC-F0-06] | 로그 스키마+부호 → 6필드(turn/attacker/target/action=<SkillId>/dmg/hp) 정의 완전 + dmg 부호규약(피해 양수/회복 음수/막기 0) 1줄 확정 | 문서 대조 | **PASS**(Director 확정 2026-07-13: 제안대로 채택 — 피해 양수/회복 음수/막기 0) |



---

### F1 — 광폭화 수비상한 재검증 (balance-designer, F0과 병렬)
산출물: **엔벨로프 표**(공격하한 ~11-15 / even-trade ~22 / 공격+최대수비 ~29-33 / 순수완전수동 ∞) + 임계 단위 락(전투로그 `turn`이 유닛턴임을 코드 실측 확인 — 현재 `TurnCounter`는 [[전투로그]] 구현상 **유닛턴 카운트**로 확정 이미 되어 있음, `EnterTurnStart`의 Is Valid 분기에서만 +1) + 종결보장 증명(~턴40 단조감소) + 순수-수동 홀 명시(A1 핫시트는 무해, 베타 PvP 턴상한 플래그 예약) + F8 공식 스펙 확정 + F0③ 배정표 최종화. 산출물 경로: `raw/광폭화_재검증.md`. **F8 게이트**(F1 통과 전 F8 착수 금지).


#### TC — F1 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F1][TC-F1-01] | 死코드 방지 → 수비게임 전멸 ≥35 유닛턴 > 30, berserk 도달가능 논증(§3-2·§4) 존재 | 문서 대조 | 대기 |
| [F1][TC-F1-02] | 과민발동 방지 → 공격 even-trade 전멸=23 유닛턴 < 30(§3-1 전턴 원장), 정상게임 미발동·저구간 램프 무해 | 문서 대조 | 대기 |
| [F1][TC-F1-03] | 임계 단위=유닛턴 → TurnCounter가 EnterTurnStart IsValid 경로만 +1(사망스킵 미증가) 실증근거(§2), 라운드(=240유닛턴) 아님 명시 | 문서 대조 | 대기 |
| [F1][TC-F1-04] | 종결 보장 → turn≥37~40에서 m>1.31로 집중대상 HP 단조감소(§5), A1 핫시트 무승부룰 불요(qa L8 흡수) | 문서 대조 | 대기 |
| [F1][TC-F1-05] | F8 공식 스펙 → BerserkMult=1+0.05×max(0,turn−30)·step4 국소·Atk 불변 + 기대값표(31=32/40=50/50=70, 힐 33 고정) 존재(§7) | 문서 대조 | 대기 |
| [F1][TC-F1-06] | 순수수동 홀 → berserk 미포섭(공격 0=피해 0=∞) 명시 + 베타 절대턴상한 무승부룰 플래그 예약(§6·§9) | 문서 대조 | 대기 |



---

### F2 — 데이터 부트스트랩

#### 2-1. motions.csv (완료 — 본 세션 산출물)
`D:\unreal\Resource\data\motions.csv` 신규 작성 완료(17행, 9컬럼). [[모션연결_규칙안]] §6-1 초안을 기반으로 **EndBehavior 컬럼 추가**(F0⑦)+**대분류 6으로 Id 갱신**(50xxxxxx→60xxxxxx, F0④). 컬럼: `Id,#id_txt,RowIndex,NameKey,FrameCount,IsLoop,IsAttackFamily,EndBehavior,Memo`.

#### 2-2. 오너 수동 struct 3종 생성 — 컬럼 스펙 (F2 실행 전 오너 액션)
UE 에디터 Content Browser에서 `UserDefinedStruct` 3개 수동 생성(모달 마비 회피 — 실전노하우 §19 확정 사실). 제안 폴더: `/Game/Data/Structs`(미확정, 오너 편의 폴더 무방). **CSV 헤더와 struct 필드명은 대소문자까지 정확히 일치해야 함**(네이밍규약§4-B) — `#id_txt`는 `#` 문자를 필드명에 쓸 수 없으므로 아래 제안명 `IdTxt`로 타이핑하고, **이 매핑이 실제로 import 시 값이 채워지는지는 F2 파일럿에서 최초 검증**(미검증 리스크, 아래 §2-3 참고).

**`F_JobStatsRow`** (job_stats.csv 대응):
| CSV 헤더 | struct 필드명 | 타입 | 비고 |
|---|---|---|---|
| Id | `Id` | Integer | |
| #id_txt | `IdTxt` | String | ⚠ 매핑 미검증 |
| JobId | `JobId` | Integer | FK→jobs.csv(이월, 알파 미로드) |
| GradeId | `GradeId` | Integer | FK→grades.csv(이월) |
| Hp | `Hp` | Integer | |
| Atk | `Atk` | Integer | |
| Def | `Def` | Integer | |
| Spd | `Spd` | Integer | 예약(알파 미사용) |
| CritRate | `CritRate` | Float | 예약(전행 0) |
| SkillIds | `SkillIds` | String | `;`구분 원문 그대로(런타임 `ParseIntoArray(";")`) |
| Memo | `Memo` | String | 미사용 |

**`F_SkillsRow`** (skills.csv 대응):
| CSV 헤더 | struct 필드명 | 타입 | 비고 |
|---|---|---|---|
| Id | `Id` | Integer | |
| #id_txt | `IdTxt` | String | ⚠ 매핑 미검증 |
| NameKey | `NameKey` | String | dot-key 원문(strings.csv는 이월, F7에서 필요) |
| DescKey | `DescKey` | String | dot-key 원문(미사용, 이월) |
| Kind | `Kind` | String | UPPER_SNAKE 토큰(`PHYS`/`MAG`/`DEF`/`HEAL`) — enum 아님, BP 문자열 Equal로 분기 |
| MotionRow | `MotionRow` | Integer | FK→DT_Motions.RowIndex |
| Target | `Target` | String | `ENEMY1`/`SELF`/`ALLY1` 토큰 |
| PowerRate | `PowerRate` | Float | |
| Cost | `Cost` | Integer | 예약(항상 0) |
| CooldownTurns | `CooldownTurns` | Integer | |
| EffectType | `EffectType` | String | `NONE`/`DMG_REDUCE`/`HEAL` 토큰 |
| EffectValue | `EffectValue` | Float | |
| EffectDurationTurns | `EffectDurationTurns` | Integer | |
| Memo | `Memo` | String | 미사용 |

**`F_MotionsRow`** (motions.csv 대응):
| CSV 헤더 | struct 필드명 | 타입 | 비고 |
|---|---|---|---|
| Id | `Id` | Integer | |
| #id_txt | `IdTxt` | String | ⚠ 매핑 미검증 |
| RowIndex | `RowIndex` | Integer | 실질 키(0~16) |
| NameKey | `NameKey` | String | |
| FrameCount | `FrameCount` | Integer | 배선 필수값(F6) |
| IsLoop | `IsLoop` | Boolean | ⚠ 네이밍규약§4-C 실증 대기 — **이 프로젝트 최초의 CSV bool 컬럼 임포트** |
| IsAttackFamily | `IsAttackFamily` | Boolean | ⚠ 상동 |
| EndBehavior | `EndBehavior` | String | `LOOP`/`REVERT_IDLE`/`FREEZE_LAST` 토큰 |
| Memo | `Memo` | String | |

#### 2-3. MCP 실행 절차 (에디터 켜진 후, 파일럿 우선)
이 프로젝트에서 `DataTableTools.create`+`import_file` end-to-end 성공 전례가 **아직 없음**(A0③ CSV 스파이크가 MCP 연결 끊김으로 struct 생성 직전 중단됨) + bool 컬럼 임포트도 최초. 따라서 **DT_Motions 하나만 먼저 파일럿**:
1. `F_MotionsRow` struct 생성 확인(오너).
2. `DataTableTools.create(folder_path="/Game/Data", asset_name="DT_Motions", schema=F_MotionsRow)`.
3. `DataTableTools.import_file(source_file="D:\unreal\Resource\data\motions.csv", ...)`.
4. 검증: `list_rows` 행수=17 확인. `get_rows`로 스팟값 — **Row5(ATK1): FrameCount=6, EndBehavior=REVERT_IDLE** / **Row13(DYING): FrameCount=5, EndBehavior=FREEZE_LAST** 명시 대조. **`IdTxt` 필드가 실제로 값이 들어왔는지**(빈 문자열이면 `#`→필드명 매핑 실패로 판정) + `IsLoop`/`IsAttackFamily`가 BP에 노출되는 실제 이름 확인(네이밍규약§4-C 실증 완결).
5. 파일럿 성공 확인 후 `DT_JobStats`(`F_JobStatsRow`+job_stats.csv)·`DT_Skills`(`F_SkillsRow`+skills.csv) 동일 절차로 확장.
6. `jobs.csv`/`grades.csv` DT는 **명시적으로 이월**(알파에서 안 씀). **`strings.csv`는 이월 취소 — DT_Strings를 F2 확장 목록에 포함**(Director 확정 2026-07-13, qa 충돌#2 해소): F7 슬롯 라벨이 strings 조회를 요구(전역 규칙 "UI 문자열 하드코딩 금지")하므로 F2에서 `F_StringsRow` struct(오너 4번째)+DT_Strings 임포트까지 처리. A0③의 원래 목표이기도 했음.
7. 3개 DT 전부 `AssetTools.save_assets` 후 **`is_dirty` 재확인**(리턴값 불신 규율 — 함정⑳ StringTable 사례처럼 DataTable도 동일 버그가 있는지 미확인이므로 반드시 재조회).


#### TC — F2 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F2][TC-F2-01] | DT_Motions 파일럿 → list_rows 행수=17 | MCP list_rows | 대기 |
| [F2][TC-F2-02] | Row5(atk1) 스팟 → FrameCount=6, EndBehavior=REVERT_IDLE | MCP get_rows | 대기 |
| [F2][TC-F2-03] | Row13(dying)·Row15(block) 스팟 → FrameCount=5, EndBehavior=FREEZE_LAST | MCP get_rows | 대기 |
| [F2][TC-F2-04]★ | IdTxt 매핑 → IdTxt 필드 값이 비어있지 않음(#id_txt→IdTxt 임포트 성공). 빈값이면 FAIL → 대안 컬럼명 재시도 | MCP get_rows | 대기 |
| [F2][TC-F2-05] | bool 노출명 → IsLoop/IsAttackFamily BP 노출 실제명 확인(프로젝트 최초 CSV bool 임포트, 네이밍규약§4-C 실증) | MCP 속성 조회 | 대기 |
| [F2][TC-F2-06] | DT_JobStats → 행수=6 + 10102000=Hp90/Atk40/Def10 · 10202000=Hp80/Atk42/Def6 스팟 | MCP list_rows+get_rows | 대기 |
| [F2][TC-F2-07] | DT_Skills → 행수=5 + 31001000(베기)=PR1.3/CD1/PHYS/ENEMY1 · 33001000(막기)=SELF/DMG_REDUCE/0.5 · 34001000(치유)=HEAL/ALLY1/0.8 스팟 | MCP get_rows | 대기 |
| [F2][TC-F2-08] | 이월 확인 → DT_Jobs/DT_Grades 미생성(알파 이월). **DT_Strings는 생성 확인**(이월 취소 — Director 2026-07-13) | MCP 애셋 조회 | 대기 |
| [F2][TC-F2-09] | 저장 무결성 → 3 DT save_assets 후 is_dirty=false 재조회(리턴값 불신, StringTable 함정⑳ 계열) | MCP is_dirty 재조회 | 대기 |



---

### F3 — 스탯 로드+HP 게이지
1. `BP_BattleSpawnPoint`에 템플릿 선택 필드 신설: `JobId`(Integer, instance-editable, 단일 스칼라 — 구조체 다중필드 `set_properties` 부분반영 함정(§7 함정③) 회피) + F0③ 배정표대로 8기 값 세팅.
2. `BeginPlay`(또는 register 체인)에 `GetDataTableRow(DT_JobStats, JobId)` 조회 → `Hp`/`MaxHp`/`Atk`/`Def` 멤버 변수 세팅.
3. 임시 월드공간 HP 게이지 컴포넌트 신설(**BeginPlay 체인에서 즉시 NoCollision** — 함정⑧ 재발 방지, 기존 Sprite/TurnMarker 클릭 방패 사고를 미리 회피) — 표시는 `Hp/MaxHp` 텍스트 또는 막대(디자인은 art-pipeline 관여 없이 MVP 스칼라 처리, WBP_BattleHUD 대체 예정이므로 과공정 금지).
4. **착수 전 액터 스냅샷 raw 1회**(`S2p_초기배치백업.md` 스타일) — 필드 추가+컴파일 전후 8기 Location/FaceLeft/Sprite 드리프트 0 확인용 롤백 지점.
5. 배치가이드.md에 신규 필드 "손대지 마세요" 1줄 추가.


#### TC — F3 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F3][TC-F3-01] | 스탯 로드 → A측 스폰 로드값=DT값(전사=90/40/10·마법사=80/42/6), B측 대칭. 슬롯순서는 TC-F0-04 확정안 기준 | 로그 대조 | 대기 |
| [F3][TC-F3-02] | 등급 로드 범용성 → DT_JobStats 1성/3성 행 스탯 정확(72/32/8·113/50/13). A1 미사용이라 로드로직 스팟만 | 로그/MCP | 이월(F3 스팟만, 등급 실전 검증은 베타) |
| [F3][TC-F3-03] | 8기 드리프트 0 → JobId 필드추가+컴파일 전후 8기 Location·FaceLeft·Sprite diff=0(S2p 백업 대조) | 트랜스폼 diff | 대기 |
| [F3][TC-F3-04] | 가시성 캡처 → DefaultCamera 실측 트랜스폼 + ActionCam 근접컷 상태 **둘 다**에서 8기 HP게이지 시인 | 캡처 2종 | 대기 |
| [F3][TC-F3-05] | 게이지 Z위치 → HP게이지 시작 Z가 UI_AttackButton 기준(≈420대)이라 CamToggle 초기에도 가림 없음 | 트랜스폼/캡처 | 대기 |
| [F3][TC-F3-06] | 클릭 무간섭 → HP게이지 컴포넌트 BeginPlay 즉시 NoCollision(함정⑧), 기존 Sprite/TurnMarker 클릭 방패 안 됨 | 정적+런타임 | 대기 |
| [F3][오너] | HP 게이지 8기 머리 위 첫 등장 육안 | 오너 라이브(PIE) | 대기 |


> **오너 라이브 확인 ★필수**: HP 게이지 첫 등장. Director 안내 문구 준비 필요(아래 체크리스트).

---

### F4 — TakeHit §8 코어 (전체 스켈레톤)

#### 4-1. 스캐폴드/함수 인터페이스 (F0⑧ 정식 반영)
기존 `TakeHit`은 파라미터 없는 EventGraph Custom Event(HURT 애니만 재생). F4에서 **정식 함수로 재정의**:

- **시그니처**: `TakeHit(Attacker: BP_BattleSpawnPoint ref, Target: BP_BattleSpawnPoint ref, SkillId: Integer)`.
- **그래프 종류 주의**: §8 판정 자체(0~9단계)는 전부 동기 연산(분기·수식·HP세팅)이라 **Function Graph**로 가능(파라미터 `add_object_function_param`/`add_function_param` 사용, 함정④ latent 제약과 무관). 단, 마지막에 애니메이션 재생(HURT/DYING 재생 — 기존 패턴은 `RetriggerableDelay`를 쓰는 EventGraph Custom Event)이 필요한데, **Custom Event는 파라미터를 나중에 못 늘림(함정⑰)**. → **`WalkForward` 선례를 그대로 적용**: TakeHit 로직 마지막에 멤버 변수(예: `PendingHitTarget`, `PendingHitDied`)를 세팅한 뒤, 기존 애니 재생용 Custom Event(예: 기존 `TakeHit` 커스텀 이벤트를 `PlayHurtReaction`류로 개명하거나 그대로 유지)를 파라미터 없이 호출 — 이벤트 내부는 그 멤버 변수를 읽어 HURT 또는 DYING(F5)을 재생.
- 스캐폴드 호출 규약(F0⑧과 동일, F4/F6/F7이 재사용): `Attacker`/`Target`은 항상 `GetTurnQueue()`→Array Get(사본)으로 획득(리터럴 오브젝트 레퍼런스 금지 — 함정⑥ PIE 그림자 액터). `SkillId`는 리터럴 정수(예: 베기=`31001000`).

#### 4-2. §8 판정 스켈레톤 (Branch 구조 — HEAL·DMG_REDUCE 분기 포함, 후속 그래프 수술 회피)
```
TakeHit(Attacker, Target, SkillId):
 0. Branch: GetSkillCooldown(Attacker, SkillId) > 0
      True  → (조기 return — 방어적 가드, 정상 경로는 F7 버튼 enabled가 이미 필터링)
      False → 계속
 1. GetDataTableRow(DT_Skills, SkillId) → 로컬변수 Kind/MotionRow/Target(스킬의)/PowerRate/
            EffectType/EffectValue/EffectDurationTurns/CooldownTurns 확보 (found=false면 로그+return)
 2. Branch: Kind == "HEAL"
      True  → HealAmt = floor(Attacker.Atk × PowerRate)
               Target.Hp = Min(Target.MaxHp, Target.Hp + HealAmt)
               LogDmg = -HealAmt  → goto 9
      False → 계속
 3. Branch: EffectType == "DMG_REDUCE"
      True  → Target(=Attacker, SELF캐스트)에 버프 부여: bBlockActive=true, BlockValue=EffectValue,
               BlockSetTurn=현재유닛턴(해제 판정용) + F0⑥ Freeze 파라미터 세팅(자세 유지)
               LogDmg = 0 → goto 9
      False → 계속
 4. Base = floor(Attacker.Atk × PowerRate)
 5. Dmg  = Base − Target.Def
 6. Branch: Target.bBlockActive == true → Dmg = Dmg × (1 − Target.BlockValue)
 7. Dmg  = Max(1, floor(Dmg))
 8. Target.Hp = Max(0, Target.Hp − Dmg);  LogDmg = Dmg
    Branch: Target.Hp <= 0
      True  → Target.bAlive=false → PendingHitDied=true (F5가 이 분기에 DYING+생존카운트+
               bBattleOver 세팅을 이어붙임 — F4 시점엔 bAlive 세팅까지만, 승패체크는 F5 담당)
      False → PendingHitDied=false (기존 HURT 재생 경로)
 9. SetSkillCooldown(Attacker, SkillId, CooldownTurns)
    PendingHitTarget=Target → 기존 애니 재생 Custom Event 호출(파라미터 없이, 멤버변수 경유)
    BattleLog 로그 방출(§4-3) → Return
```
HEAL/DMG_REDUCE 분기는 F4 시점엔 **아직 시전할 스킬 자체가 없어(파이어볼·막기·치유는 F7)** 실전 트리거 불가 — 그래프는 존재하되 도달 불가 상태로 F7까지 대기(스켈레톤 선구축 원칙, 리뷰에서 확정).

#### 4-3. 전투로그 스키마 (F0⑧ 확정)
```
BattleLog|turn=<TurnCounter>|attacker=<GetDisplayName(Attacker)>|target=<GetDisplayName(Target)>|action=<SkillId>|dmg=<LogDmg>|hp=<Target.Hp>
```
- `turn`: 기존 `TurnCounter` 변수 재사용(신규 변수 없음, [[전투로그]] 기 구현).
- `attacker`/`target`: 기존과 동일 포맷(`GetDisplayName()`) — 파서 호환 유지.
- `action`: **숫자 SkillId를 문자열화**(`#id_txt` 슬러그 아님) — 기존 `ATTACK1` 하드코딩 완전 치환.
- `dmg`: **부호 규약(Director 확정 2026-07-13)**: 피해=양수, 회복(HEAL)=음수(예: 치유 33 → `dmg=-33`), 막기(피해 0, 버프만)=`dmg=0`.
- `hp`: 적용 후 Target.Hp(0~MaxHp 클램프 최종값).
- 기존 `extract_battle_log.py`는 라인을 그대로 통과시키는 방식이라 필드 확장에 스크립트 수정 불요(F9a "기존 파서 호환" 자동 충족).

#### 4-4. 검증 경로 — "베기"는 F7 전까지 스캐폴드 전용
현재 UI엔 버튼이 "Attack" 1개뿐(스킬 선택은 F7). **F4의 베기 검증은 F0⑧ 스캐폴드로 `TakeHit(Attacker, Target, SkillId=31001000)`을 직접 호출하는 함수 레벨 검증**이며, 실제 플레이 중 베기를 선택할 수 있는 건 F7부터다(qa-critic/verifier가 "베기 버튼"을 찾지 않도록 명시).


#### TC — F4 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F4][TC-F4-01] | 전사 basic → 전사=30 / 마법사=34 (v1 §5-1·F1 §1 정답지) | 로그 파싱 | 대기 |
| [F4][TC-F4-02] | 마법사 basic → 전사=32 / 마법사=36 | 로그 파싱 | 대기 |
| [F4][TC-F4-03] | 베기 → 전사=42 / 마법사=46. 스캐폴드로 TakeHit(…,SkillId=31001000) 직접호출(인게임 베기선택은 F7) | 로그 파싱(스캐폴드) | 대기 |
| [F4][TC-F4-04] | 파이어볼 61/65 · 치유 +33 · 막기 0 셀 → F4 스켈레톤 도달불가(스킬은 F7) | 로그 파싱 | 이월(F7) |
| [F4][TC-F4-05] | min1 보정 → 합성 mock 고Def(Def≥Base) 입력 시 dmg=1. 라이브 로스터는 도달불가라 mock 전용 | 로그 파싱(mock) | 대기 |
| [F4][TC-F4-06] | 로그 스키마 → 6필드 정확 + action이 숫자 SkillId(ATTACK1 하드코딩 완전 치환) | 로그 파싱 | 대기 |
| [F4][TC-F4-07] | HP 적용 → hp 필드 = max(0, MaxHp−dmg) 정확, 피해 dmg 양수 | 로그 파싱 | 대기 |
| [F4][TC-F4-08] | 쿨다운 가드 → 스캐폴드로 쿨>0 세팅 후 TakeHit 재호출 시 조기 return(피해 미적용) | 로그 파싱(스캐폴드) | 대기 |
| [F4][오너] | 공격 시 HP가 실제로 깎임 — 첫 진짜 전투감 육안 | 오너 라이브(PIE) | 대기 |


> **오너 라이브 확인 ★필수**: 공격하면 HP가 실제로 깎임(첫 진짜 전투감). Director 안내 문구 준비 필요.

---

### F5 — 사망·승패 (End 상태)

#### 5-1. bAlive·턴 스킵
`EnterTurnStart`에서 `ActiveUnit`이 `bAlive==false`면 카메라·걸음·PlayAttack 전부 건너뛰고 즉시 EnterTurnEnd로(마커도 안 켬) — **턴큐는 splice하지 않음**(H2, 길이 불변 유지).

#### 5-2. End 전이 = EnterTurnEnd 단일 관문 (레이스 원천 차단)
Executing은 걸음 후 `PlayAttack`을 호출하고, 그 뒤 Sequence 2분기(A: Delay0.25→TakeHit / B: Delay0.75→WalkBack→Delay0.45→**EnterTurnEnd**)가 **병렬**로 돈다(권위 서술 = 걸어나오기연출 plan L39 — qa 검증요망#4 정정: PlayAttack이 Sequence 분기보다 먼저다). TakeHit(A분기)이 마지막 생존자를 죽여도 B분기는 그걸 모르고 계속 진행해 `EnterTurnEnd()`를 그대로 호출하므로, **TakeHit이 직접 상태를 End로 바꾸면 B분기의 뒤이은 EnterTurnEnd 호출이 그걸 TurnStart로 되돌리는 레이스**가 생긴다(리뷰에서 확정한 핵심 리스크).

**해법**: TakeHit(F4가 만든 §8 스켈레톤의 8번 death 분기)은 **플래그만** 세팅한다 — 실제 상태 전이는 **기존 `EnterTurnEnd`의 "① 마커OFF → ② i=(i+1)%길이" 다음, "TurnStart 진입" 이전**에 신규 Branch 하나로만 일어난다:

```
EnterTurnEnd() [기존 함수, 확장]:
  ① MarkerOff(ActiveUnit)
     (카메라 기배선: SetViewTargetWithBlend(DefaultCamera, 0.3s) — 무변경, 그대로 실행됨)
  ② SetCurrentIndex((CurrentIndex + 1) % 큐길이)
  ③ [신규] Branch(Condition = GetbBattleOver)
       True  → EnterEnd()          ← 신규, 이 지점에서만 호출
       False → Delay(0.35) → EnterTurnStart()   ← 기존 그대로
```

`bBattleOver`(Manager 신규 bool)는 F4의 8번 death 분기 안에서 F5가 이어붙이는 로직으로 세팅: `Target.bAlive=false` 직후 → 상대팀(Target과 반대 bIsParty) 생존수 카운트(`ForEachLoop(TurnQueue)` + `bAlive==true` 필터) → 0이면 `SetbBattleOver(true)` + `SetWinningTeam(Attacker.bIsParty)`.

이 구조면 (a) B분기가 계속 실행돼 `EnterTurnEnd`에 도달해도 **바로 그 지점에서** End로 갈지 TurnStart로 갈지 결정하므로 레이스가 없고, (b) 카메라 복귀(`DefaultCamera`)가 `EnterTurnEnd`의 기존 진입 액션에 이미 포함돼 있어 **End로 가는 경로도 자동으로 카메라가 복귀**한다(추가 배선 불요).

#### 5-3. DYING 재생 — 기존 "재생 후 idle 복귀" 패턴의 예외
기존 `PlayAttack`/`TakeHit`은 전부 "애니 재생 → 일정 시간 뒤 자동 RowIndex=0(IDLE) 복귀" 패턴이다. **사망 유닛은 이 패턴을 타면 안 됨**(죽은 유닛이 다시 일어서 보이는 회귀) — 死 분기에서는 DYING(Row13) 재생 후 **복귀시키지 않고 F0⑥의 Freeze 파라미터(`bFreeze=true`)를 세팅해 마지막 프레임에 고정**한다. TC(F0⑥ 채택안 기준): 킬링블로우 후 수십 초 방치해도 동일 프레임 유지(꿈틀거림 없음).

#### 5-4. `EnterEnd()` 스펙 (system-ui, v3 반영)
- `bInputLocked=true` **고정**(CamToggle 버튼 클릭도 포함해 전면 잠금 — 기존 `NotifyCamToggleClicked`의 `bInputLocked` 가드가 이미 있으므로 자동 차단되는지 확인만 하면 됨, 신규 배선 최소).
- `BattleFinished` 이벤트 디스패처 방출, payload = 전멸한 파티의 `bIsParty`(A6에서 부전승·Win/Lose 매핑 확장 대비).
- **비파괴**: teardown 금지. `InitBattle()` 재호출로 재시작 가능한 상태 유지(A6 무전환 재시작 접점).
- `TurnMarker` 전원 OFF(`ForEachLoop(TurnQueue)`).

#### 5-5. 타겟팅 제외
`EnterAwaitTarget`의 하이라이트 대상 필터에 `bAlive==true` 조건 추가(사망자는 하이라이트도 클릭도 안 됨 — `ClickBox` 콜리전이 잔존하지 않는지 별도 확인 필요, 사망 시 `ClickBox`도 `NoCollision`으로 전환 권장).


#### TC — F5 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F5][TC-F5-01]★ | End 레이스 차단 → 킬링블로우(B분기 진행 중)에도 최종상태=End 유지, EnterTurnEnd가 TurnStart로 안 되돌림(bBattleOver Branch), **2회 재현** | 로그(상태전이) | 대기 |
| [F5][TC-F5-02] | 사망유닛 턴스킵 → 사망유닛 자기턴 도래 시 Executing 미진입·마커 미점등·**ActionCam 미부착**, 즉시 EnterTurnEnd | 로그+캡처 | 대기 |
| [F5][TC-F5-03] | 큐 길이 불변 → 사망 전후 GetTurnQueue 길이=8 유지(splice 금지, H2) | 로그(큐 length) | 대기 |
| [F5][TC-F5-04] | index<현재 유닛 사망 → 다음 유닛 스킵/중복 없음. [A1,B1,A2,B2]서 B1 처치 후 순회 정합(qa TC-Q01) | 로그 | 대기 |
| [F5][TC-F5-05] | 마지막 유닛 사망 프레임 → 승패확정 + %큐길이 나눗셈 크래시 없음(qa TC-Q02) | 로그 | 대기 |
| [F5][TC-F5-06] | 시체 정지 → DYING(Row13) 재생 후 **수십 초 방치** 동일 프레임(꿈틀거림 없음, F0⑥ FREEZE_LAST). 시간차 캡처 2장 픽셀 동일 | 캡처 2장 대조 | 대기 |
| [F5][TC-F5-07] | 사망자 타겟 불가 → EnterAwaitTarget 하이라이트 후보서 제외 + ClickBox NoCollision(클릭 무효) | 정적+런타임 | 대기 |
| [F5][TC-F5-08] | 마커 전원 OFF → EnterEnd 시 TurnMarker 8기 전부 OFF | 로그/캡처 | 대기 |
| [F5][TC-F5-09] | 킬링블로우 VFX → 마지막 타격에도 Hit VFX 정상 발생(End 전이가 VFX 삼키지 않음) | 캡처/로그 | 대기 |
| [F5][TC-F5-10] | 양측 대칭 종료 → Party 전멸·Enemy 전멸 **양 방향** 모두 End+WinningTeam 정확 | 로그 | 대기 |
| [F5][TC-F5-11] | 비파괴 종료 → EnterEnd 후 teardown 없음, InitBattle 재호출로 재시작 가능(A6 접점) | 로그/런타임 | 대기 |
| [F5][TC-F5-12] | 하이라이트 잔존 없음 → 하이라이트된 적이 그 타격에 사망 시 하이라이트도 함께 해제 | 캡처 | 대기 |
| [F5][오너] | 사망(쓰러져 고정)·승패 — 한 판이 끝남 육안 | 오너 라이브(PIE) | 대기 |


> **오너 라이브 확인 ★필수**: 사망(쓰러져 고정)·승패 — 한 판이 끝남. Director 안내 문구 준비 필요.

---

### F6 — 모션 배선 (리터럴 → 데이터 구동, 무변화 회귀 단계)

#### 6-1. PlayAttack 교체 대상 핀 목록
```
SetScalar(TimeOffset = GetGameTimeInSeconds)   무변경
SetScalar(FrameCount = 6.0)                    ❌ 리터럴 제거 → DT_Motions[RowIndex].FrameCount 조회값
SetScalar(RowIndex   = 5.0)                    ❌ 리터럴 제거 → DT_Skills[SkillId].MotionRow 조회값
RetriggerableDelay(0.70초)                     ❌ 리터럴 제거 → (FrameCount/8) − 0.05 계산값
SetScalar(TimeOffset = 0)                      무변경(idle 복귀 값 고정)
SetScalar(FrameCount = 6.0)                    무변경(IDLE1은 항상 FrameCount6 고정, 데이터 구동 불필요)
SetScalar(RowIndex   = 0.0)                    무변경(항상 IDLE 복귀)
```
- **유지시간 재계산 검증**: ATK1(FrameCount6) → 6/8−0.05=**0.70**(기존값과 완전 동일, 무회귀 확인 포인트). CASTING1/CASTING2/BLOCK(FrameCount5) → 5/8−0.05=**0.575**(기존 0.70 고정 대비 리와인드 팝 75ms 제거).
- **DT 조회 실패 폴백**: `GetDataTableRow` 반환 `found=false`면 RowIndex=5·FrameCount=6(기존 ATK1 리터럴)로 폴백 + 로그 1줄. `FrameCount≥1` 가드(0 나눗셈/역주행 방지).
- **PlayAttack 시그니처**: 현재 파라미터 없는 Custom Event. `SkillId`를 받아야 하므로 F4와 동일 이유로 파라미터 확장 제약(함정⑰)에 걸림 → **`WalkForward`의 `WalkTargetLoc` 선례**를 따라 멤버 변수 `PendingSkillId`를 호출 전에 세팅 후 `PlayAttack` 내부에서 읽는 패턴 채택.
- **무접촉 확인**: `Walk(Row2)`/`idle(Row0)` 관련 `SetScalar` 호출은 `WalkForward`/`WalkBack`(다른 함수, [[걸어나오기연출]] 소관)에 있어 이 교체 작업과 물리적으로 분리 — 회귀 없음.

#### 6-2. 회귀 확인 범위 (카메라·걸음 기배선)
이 지점은 과거 실측으로 2회 배치 오류가 났던 자리([[카메라액션]] V3/VF 리와인드 — OTS 컷 블록이 WalkForward보다 먼저 있었던 버그, 게이트 위치 재배치). F6은 `PlayAttack` **내부 값만** 바꾸고 호출 위치는 그대로라 구조적 회귀 위험은 낮지만, 아래 축을 반드시 재확인:
- `CamCut` 로그가 `WalkArrive` 이후에 발생(순서 불변, 실측 델타 +0.168s 기준).
- `Align`(컷 요/lean 정렬)이 `PlayAttack` 직전에 실행(불변).
- 카메라 토글 OFF 상태에서도 `CamCut` 자체는 발생하되 `Align` 컷 블록만 스킵(불변, VF_토글버튼 사양).
- `WalkBack`(Delay 0.75) 레이스 마진 유지(FrameCount5 스킬로 PlayAttack 내부 지속시간이 0.575로 짧아져도 외부 Executing의 Delay(0.25)/(0.75) 분배 자체는 무변경이므로 안전 — PlayAttack의 자체 유지시간이 외부 Delay보다 항상 짧거나 같음, 4개 관련 행 모두 ≤0.70s 확인됨).


#### TC — F6 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F6][TC-F6-01] | ATK1 무회귀 → 공격/베기(Row5·FC6) 유지시간=(6/8)−0.05=0.70s 기존과 완전 동일 | 로그(타이밍) | 대기 |
| [F6][TC-F6-02] | 데이터 구동 → RowIndex=DT_Skills.MotionRow · FrameCount=DT_Motions.FrameCount 조회값 반영(리터럴 5/6 제거) | 로그/정적 | 대기 |
| [F6][TC-F6-03] | DT 조회 실패 폴백 → mock 미존재 SkillId 시 RowIndex=5·FC6 폴백 + 로그 1줄, 크래시 없음 | 로그(mock) | 대기 |
| [F6][TC-F6-04] | FrameCount≥1 가드 → FC=0 입력 시 0나눗셈/역주행 없음(하한 클램프) | 로그/정적 | 대기 |
| [F6][TC-F6-05] | 걸음·idle 무접촉 → WalkForward(Row2)·WalkBack·idle(Row0) 그래프 F6 전후 동일(다른 함수, 물리 분리) | 정적 그래프 조회 | 대기 |
| [F6][TC-F6-06] | 카메라 컷 순서 불변 → CamCut 로그가 WalkArrive 이후(델타≈+0.168s), Align이 PlayAttack 직전, 토글OFF시 Align만 스킵 | 로그(순서) | 대기 |
| [F6][TC-F6-07] | WalkBack 레이스 마진 → FC5 스킬(유지 0.575)에서도 외부 Delay(0.25/0.75) 분배 불변, 마진 ≥0.8s(WT-12류) | 로그 | 대기 |
| [F6][TC-F6-08] | 리와인드 팝 제거 → CAST1/CAST2/BLOCK(FC5) 재생종료 시 frame0 재노출 없음. F6은 스캐폴드 선검증, 실제 재생은 F7 | 캡처(스캐폴드) | 이월(F7 실전 재검증) |


> **오너 라이브 확인**: 선택(회귀 단계 — "달라진 게 없어야 정상"이므로 오너가 원할 때만).

---

### F7 — 스킬 확장+쿨다운

#### 7-1. 아키텍처 제약 (system-ui★, 필수 준수)
타겟킨드 해석·유효타겟풀 계산·하이라이트·스킵 판단은 전부 **`BP_BattleManager` 소유**. 버튼(임시 월드공간)은 `NotifySkillSelected(SkillId)` 호출만 하고 그 외 로직을 갖지 않는다 — 추후 `WBP_BattleHUD`가 이 버튼을 드롭인 교체할 때 Manager 쪽 로직은 무변경.

#### 7-2. 스킬 슬롯 동적 재바인딩 흐름
`EnterAwaitCommand`(기존 "단일 진입 함수, 항상 잠금 해제") 진입 시:
```
1. ActiveUnit.SkillIds(String, ";" 구분) → ParseIntoArray(";") → SkillIdArray (전 직업 정확히 3개 — F0③ 배정표 기준)
2. ForEachLoop(슬롯 i = 0..2):
     SkillId = SkillIdArray[i]
     GetDataTableRow(DT_Skills, SkillId) → NameKey/CooldownTurns/Target 등
     SlotButton[i].SkillId = SkillId  (클릭 시 NotifySkillSelected(SkillId)로 전달)
     SlotButton[i].Label = strings.csv 조회 텍스트(NameKey 경유 — 하드코딩 금지, SSOT=csv)
     bEnabled = (GetSkillCooldown(ActiveUnit, SkillId) == 0) AND (유효타겟 ≥ 1)
        · ENEMY1: 상대팀 bAlive 생존자 존재 여부
        · ALLY1 : 아군(자신 포함) bAlive 생존자 존재 여부
        · SELF  : 항상 true
     SlotButton[i]의 ClickBox 콜리전 = bEnabled ? QueryOnly : NoCollision (+ 시각적 반투명 처리)
```
버튼 콜리전은 **ClickBox만** 유효(배경/라벨은 기존 컨벤션대로 NoCollision).

#### 7-3. NotifySkillSelected(SkillId) 분기 (Manager 소유)
```
GetDataTableRow(DT_Skills, SkillId).Target 분기:
  "ENEMY1" → 기존 AwaitTarget 로직 그대로(상대팀 하이라이트, 유효 타겟 클릭 시 Executing)
  "ALLY1"  → AwaitTarget 변형: 아군(bIsParty==ActiveUnit.bIsParty) 중 bAlive==true(자신 포함, F0② 확정) 하이라이트
  "SELF"   → AwaitTarget 스킵 — SelectedTarget=ActiveUnit 즉시 세팅 → EnterExecuting 직행(SELF 즉시커밋, 취소창 없음)
```
Executing 안무(걸음→PlayAttack→TakeHit/WalkBack)는 SELF/ALLY1 스킬도 **기존 ENEMY1과 동일한 균일 step-forward**를 그대로 수용(A1 범위 — 대상별 안무 분기는 HUD 시대에 고려, 이번엔 만들지 않음).

#### 7-4. 스킬별 세부
- **파이어볼**(MotionRow=10, CASTING1): F4 스켈레톤의 4~8단계(데미지 경로) 그대로 통과, PowerRate 1.7.
- **막기**(MotionRow=15, BLOCK, 지속형): F4 스켈레톤의 3단계(DMG_REDUCE) 분기 최초 실전 도달 — 버프 부여+F0⑥ Freeze 파라미터로 자세 유지(자기 다음 턴 시작까지, §8 해제 시점).
- **치유**(MotionRow=11, CASTING2): F4 스켈레톤의 2단계(HEAL) 분기 최초 실전 도달 — 치유량 = **시전자** Atk×0.8(§8-2 명시, L2 해소), 대상=생존 아군+자신(§F0②).
- **쿨다운 진행**: `EnterTurnStart`(자기 턴 시작)에서 `ActiveUnit`이 보유한 전 스킬의 쿨다운 −1(하한0) — H3/§7-6 반영.


#### TC — F7 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F7][TC-F7-01] | 파이어볼 → 전사=61 / 마법사=65 (v1 §5-1, F4 이월분) | 로그 파싱 | 대기 |
| [F7][TC-F7-02] | 파볼 vs 막기 → **30** (base 71−10=61, ×0.5=30.5, floor=30 — H5 정정치, 28 아님) | 로그 파싱 | 대기 |
| [F7][TC-F7-03] | 치유 → +33 (시전자 Atk42×0.8=33.6 floor=33, L2=시전자Atk 확인). 대상 Hp += 33 | 로그 파싱 | 대기 |
| [F7][TC-F7-04] | 치유 오버힐 → 풀피/근접 대상 치유 시 min(MaxHp,·) 클램프, 초과분 버림(qa TC-H01) | 로그 파싱 | 대기 |
| [F7][TC-F7-05] | 치유 죽은아군 제외 → ALLY1 후보서 bAlive=false 제외, 사망 아군 타겟 불가(qa TC-H02·L9) | 런타임/캡처 | 대기 |
| [F7][TC-F7-06] | 치유 자신 포함 → ALLY1 후보에 시전자 자신 포함(F0② L1 해소), 단독생존 마법사 자힐 가능 | 런타임 | 대기 |
| [F7][TC-F7-07] | 막기 지속형 → 막기 후 시전자 다음 자기턴 시작 전 **모든 피격 ×0.5**(qa TC-B01: 2회 피격 둘 다 반감), 자기턴 시작 시 해제 | 로그 파싱 | 대기 |
| [F7][TC-F7-08] | 막기 포즈 유지 → BLOCK(Row15) FREEZE_LAST로 지속 구간 자세 고정(리와인드/idle복귀 없음) | 캡처 | 대기 |
| [F7][TC-F7-09] | 막기 피해 0 → 막기 시전 시 dmg=0(DMG_REDUCE 분기 goto9, 버프만·공격 안 함) | 로그 파싱 | 대기 |
| [F7][TC-F7-10] | 쿨다운 진행 → 사용 후 CooldownTurns 세팅, 자기턴 시작마다 −1(하한0), 쿨0 전 재사용 불가(qa TC-C01) | 로그 파싱 | 대기 |
| [F7][TC-F7-11] | 쿨다운 슬롯 비활성 → 쿨>0 슬롯 ClickBox NoCollision + 시각 반투명, 클릭 무효 | 정적+캡처 | 대기 |
| [F7][TC-F7-12] | 슬롯 재바인딩 → 전사턴↔마법사턴 전환 시 3슬롯 라벨·활성상태 정확 갱신(SkillIds ParseIntoArray) | 캡처/로그 | 대기 |
| [F7][TC-F7-13] | SELF 즉시커밋 → 막기 버튼 클릭 시 AwaitTarget 스킵, SelectedTarget=자신 즉시, 취소창 없음 | 로그 | 대기 |
| [F7][TC-F7-14] | ALLY1 타겟 경로 → 치유 선택 시 아군만 하이라이트, 적 클릭 무효(ENEMY1과 다른 경로) | 런타임/캡처 | 대기 |
| [F7][TC-F7-15]★ | 버튼 라벨 SSOT → 슬롯 라벨=DT_Strings 조회 텍스트(하드코딩 아님) — **선결 해소됨**(DT_Strings가 F2로 편입, Director 2026-07-13) | 캡처 | 대기 |
| [F7][오너] | 스킬 4종 사용감(슬롯 선택·타겟팅·파이어볼/막기/치유 모션) 육안 | 오너 라이브(PIE) | 대기 |


> **오너 라이브 확인 ★필수**: 스킬 4종 사용감(슬롯 선택·타겟팅·파이어볼/막기/치유 모션). Director 안내 문구 준비 필요.

---

### F8 — 광폭화 (F1 게이트)
공식(balance 스펙, F1 산출물 승인 후 확정치로 대입): `BerserkMult = 1 + 0.05 × (turn − 30)`(turn≤30이면 1.0, **가산**이지 복리 아님). 적용 지점 = **F4 §8 step4에만 국소** — `Base = floor(Attacker.Atk × PowerRate × BerserkMult)`(단일 floor). **Atk 스탯 자체는 불변**(치유가 Atk를 그대로 읽으므로 자동으로 광폭화 배율을 타지 않게 하는 가드 — HEAL 분기(§8 step2)는 BerserkMult 미적용 유지). **전역 유닛턴 카운터**(`TurnCounter` 재사용) 기준, 양측 동일 배율 적용(PvP 대칭 필수, 리뷰 확정). 로그에 배율 적용 여부 기록(`|berserk=<mult>` 필드 추가 검토, F0⑧ 스키마에 후속 확장).


#### TC — F8 (qa-critic 확정 · 판정방법 컬럼 필수)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F8][TC-F8-01] | 30턴 전 무효과 → turn≤30 전사 basic=30 (BerserkMult=1.0) | 로그 파싱 | 대기 |
| [F8][TC-F8-02] | turn31 +5% → 전사 basic=32, 파이어볼=64 | 로그 파싱 | 대기 |
| [F8][TC-F8-03] | turn40 → 전사 basic=50, 파이어볼=97 | 로그 파싱 | 대기 |
| [F8][TC-F8-04] | turn50 → 전사 basic=70, 파이어볼=132 | 로그 파싱 | 대기 |
| [F8][TC-F8-05]★ | 힐 미스케일 → turn31/40/50 모두 치유=**33 고정**(Atk 스탯 불변·step4 국소 증명, balance TC-Z03) | 로그 파싱 | 대기 |
| [F8][TC-F8-06] | 양측 대칭 → 양 팀 동일 turn 동일 배율(전역 TurnCounter, PvP 대칭, TC-Z04) | 로그 파싱 | 대기 |
| [F8][TC-F8-07] | 종결 보장 → 최대수비 스크립트 turn≥40 집중대상 HP 단조감소(TC-Z05) | 로그 파싱 | 대기 |
| [F8][TC-F8-08] | 막기 미스케일 → DMG_REDUCE 버프값(0.5) berserk 무영향(step3 미접촉) | 로그 파싱 | 대기 |


> **오너 라이브 확인**: 단독 확인 생략, F9b에 묶음(30턴+ 시나리오라 개별 확인 번거로움).

---

### F9 — 풀 회귀+풀테스트

#### F9a (verifier 기계 검증)
자동 커맨드 스캐폴드(고정 타겟 순서 시나리오 — §5-3 1:1 듀얼 또는 §5-4 미러 집중공격)로 한 판 자동 완주 → **턴별 HP 원장 로그 대조**([[스탯_전투공식_v1]] §5 결정론 정답지) + 로그 완성도(스킬5종·사망·광폭화 전부 기록됨) + 기존 `extract_battle_log.py` 호환 확인 + 걸음·카메라·VFX 로그 회귀. 스캐폴드는 검증 후 전량 제거.

#### F9b (오너 육안)
핫시트 실플레이 완주(광폭화 유발까지, 30턴+ 시나리오 필요 시 스캐폴드로 턴 가속). 관찰 포인트: 시체 누적 구도(F5 FREEZE_LAST 다수 발생 시 자연스러운지) · 틸트시프트 프레이밍 · Z파이팅 줄무늬 무발생. **사전 고지**: Result 연출 없이 정지는 의도된 A6 이관(범위 재논쟁 방지).


#### TC — F9a (verifier 기계 · 판정=로그 원장 대조)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F9a][TC-F9a-01]★ | even-trade 원장 → 미러 전원 기본공격 자동완주, 턴별 HP·사망시점=balance §3-1 정답지(B1†T5·A1†T6·B2†T11·A2†T12·B3†T17·A3†T18·B4†T23, 총 **23 유닛턴** A4승) | 로그 원장 대조 | 대기 |
| [F9a][TC-F9a-02] | 로그 완성도 → 스킬5종·사망·(유발 시)광폭화 전부 로그 기록 | 로그 파싱 | 대기 |
| [F9a][TC-F9a-03] | 파서 호환 → extract_battle_log.py가 확장 스키마 라인 통과(스크립트 수정 불요) | 스크립트 실행 | 대기 |
| [F9a][TC-F9a-04] | 연출 회귀 → 걸음(WalkArrive/WalkHome)·카메라(CamCut)·VFX 로그 기존과 동일 | 로그 회귀 | 대기 |

#### TC — F9b (오너 육안)

| ID | 조건 → 기대결과 | 판정방법 | 상태 |
|---|---|---|---|
| [F9b][TC-F9b-01] | 풀플레이 완주 → 핫시트로 스킬5종 써가며 승패까지, 광폭화 유발(스캐폴드 턴가속) 관찰 | 오너 육안 | 대기 |
| [F9b][TC-F9b-02] | 시체 누적 구도 → FREEZE_LAST 다수 발생 시 자연스러운지(꿈틀·기립 없음) | 오너 육안 | 대기 |
| [F9b][TC-F9b-03] | 프레이밍·Z파이팅 → 틸트시프트 프레이밍 유지, 시체 겹침 Z파이팅 줄무늬 무발생 | 오너 육안 | 대기 |
| [F9b][TC-F9b-04] | 하이라이트/잔존 → 타겟팅 하이라이트·버튼 잔존 없음, End 후 화면 클린 | 오너 육안 | 대기 |


> **오너 라이브 확인 ★필수**(F9b 자체가 곧 오너 라이브 확인 단계). Director 안내 문구 준비 필요(관찰 포인트 3종 + 광폭화 유발 방법 안내).

---

## 이월(deferred) TC
| TC | 검증 예정 단계 | Director 승인 |
|---|---|---|
| [F4][TC-F4-04] 파볼61/65·치유+33·막기0 셀 (F4 스켈레톤 도달불가) | F7 | 대기 |
| [F6][TC-F6-08] CAST/BLOCK 리와인드 팝 실전 재생 (F6은 스캐폴드 선검증만) | F7 | 대기 |
| [F3][TC-F3-02] 1성/3성 등급 템플릿 스탯 (A1 미사용, 로드로직 스팟만) | F3 스팟 / 등급 실전=베타 | 대기 |
| 순수-수동 절대턴상한 무승부룰 (berserk 미포섭 홀, A1 핫시트 무해) | 베타(PvP/AI) | 대기 |
| [F7][TC-F7-15] DT_Strings 선결 (F2가 strings DT 이월 → F7 라벨과 충돌) | F7 착수 전 확정 | **해소**(DT_Strings F2 편입 — Director 2026-07-13) |

---

## 진행 체크리스트

- [x] F0 문서화(청사진.md+plan.md, 본 문서) — 선결 확정 8건 방향 반영 완료
- [ ] F0 TC 작성(qa-critic)
- [ ] F0 게이트 통과 (Director 판정)
- [ ] F1 개발(balance, F0과 병렬)
- [ ] F1 게이트 통과 (Director 판정 — F8 게이트 겸함)
- [ ] F2 개발(motions.csv 완료 / struct 3종 오너 생성 / DT 파일럿 / DT 확장)
- [ ] F2 게이트: verifier 실증
- [ ] F2 게이트 통과 (Director 판정)
- [ ] F3 개발
- [ ] F3 게이트: verifier 실증
- [ ] F3 게이트: ★오너 라이브 확인(PIE) — HP 게이지 첫 등장
  - [ ] 오너 안내 문구 준비(Director) — 무엇을 클릭·무엇을 관찰
- [ ] F3 게이트 통과 (Director 판정)
- [ ] F4 개발
- [ ] F4 게이트: verifier 실증
- [ ] F4 게이트: ★오너 라이브 확인(PIE) — 공격하면 HP가 실제로 깎임
  - [ ] 오너 안내 문구 준비(Director)
- [ ] F4 게이트 통과 (Director 판정)
- [ ] F5 개발
- [ ] F5 게이트: verifier 실증
- [ ] F5 게이트: ★오너 라이브 확인(PIE) — 사망(쓰러져 고정)·승패, 한 판이 끝남
  - [ ] 오너 안내 문구 준비(Director)
- [ ] F5 게이트 통과 (Director 판정)
- [ ] F6 개발
- [ ] F6 게이트: verifier 실증
- [ ] F6 게이트: 오너 라이브 확인(선택 — 회귀 단계, 원할 때만)
- [ ] F6 게이트 통과 (Director 판정)
- [ ] F7 개발
- [ ] F7 게이트: verifier 실증
- [ ] F7 게이트: ★오너 라이브 확인(PIE) — 스킬 4종 사용감
  - [ ] 오너 안내 문구 준비(Director)
- [ ] F7 게이트 통과 (Director 판정)
- [ ] F8 개발(F1 게이트 통과 후 착수)
- [ ] F8 게이트: verifier 실증 (오너 라이브 확인은 F9b에 묶음, 별도 없음)
- [ ] F8 게이트 통과 (Director 판정)
- [ ] F9a 개발+실증(verifier 기계 원장 대조)
- [ ] F9b: ★오너 라이브 확인(PIE) — 풀플레이+광폭화+관찰 포인트
  - [ ] 오너 안내 문구 준비(Director) — 관찰 포인트 3종+광폭화 유발 방법
- [ ] F9 게이트 통과 (Director 최종 판정, A1 DoD 충족 확인)

---

## 검증 방침
- TC 확정은 F0(qa-critic) — 위 각 단계 "TC 삽입 지점"은 방향 예시일 뿐 확정 TC 아님. **판정방법(로그/캡처/오너육안) 컬럼 필수**(verifier 요구, v3 반영).
- 수치 검증 기준 = [[스탯_전투공식_v1]] §5 손계산표(결정론, 재현 100%).
- 화면 변화가 있는 단계(F3·F4·F5·F7·F9b)는 verifier 실증 이후 **오너 라이브 확인(PIE)**을 Director 게이트 앞에 추가 편성(위 체크리스트 반영). F6은 선택, F8은 F9b에 흡수.
- A1 DoD: 핫시트로 스킬 5종 써가며 한 판 승패까지 완주 + 전투로그 전 과정 기록 + 기존 연출(걸음·카메라) 무손상 + F9a 원장 대조 통과 + F9b 오너 확인.

## 산출물·문서·커밋
- 본 세션 산출물: `docs/features/전투완성/plan.md`(본 문서) · `data/motions.csv`(17행, 9컬럼, 도메인6).
- `_tables.csv`는 **미변경**(F0④ 등록은 오너 승인 후 별도 실행).
- 기능폴더 `docs/features/전투완성/`(청사진·plan·raw) 계속 사용. 커밋 `[C] docs(전투완성): F0 plan.md+motions.csv 초안` 형태로 1건(push는 오너 확인). 신규 MCP 노하우 발견 시 `언리얼_MCP_실전노하우.md`에 추가(예: F2 파일럿에서 `#id_txt`→`IdTxt` 매핑 실증 결과, DataTable `set_entry`류 dirty 버그 유무).

## 알려진 제약·TODO (본 문서 작성 시점)
1. **`#id_txt` → `IdTxt` 필드 매핑 미검증** — F2 파일럿에서 최초 확인 필요(값이 빈 문자열로 들어오면 대안 컬럼명 재시도 필요, F2 §2-3 참고).
2. **JUMP/HURT/DASH/ROLL의 EndBehavior=REVERT_IDLE은 본 문서의 기본값 판단**(v3 지시문에 명시적 언급 없음) — 현재 미사용 행(HURT 제외)이라 실질 영향 없으나 이견 있으면 F2 실행 전 정정.
3. **`_tables.csv` motions 등록은 미실행** — 오너 승인 후 balance-designer 또는 gameplay-engineer가 실제 Id 발급 규칙과 대조해 등록.
4. **F4 로그 `dmg` 부호 규약(피해=양수/회복=음수)은 본 문서 제안** — F0 또는 F4 착수 전 1줄 확정 필요.
5. F1(광폭화 재검증) 결과에 따라 F8 공식의 정확한 계수(현재 +5%/턴 가정)가 조정될 수 있음 — F1 게이트 통과 시 본 문서 F8 절 갱신 필요.
