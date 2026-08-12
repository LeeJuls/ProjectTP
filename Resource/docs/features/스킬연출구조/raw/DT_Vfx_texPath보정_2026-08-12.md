---
type: record
project: projectTP
feature: 스킬연출구조
stage: DT_Vfx.texPath보정
updated: 2026-08-12
status: PASS
status_note: ★완료 — 5행 서픽스 보정 + FXSHOW 5/5 실측 PASS. ③ 조사 결과 DT_Sfx.soundPath에 동일 패턴(현재 휴면) 발견
---

# `DT_Vfx.texPath` 서픽스 보정 — 결과 (MCP 세션, 2026-08-12)

> 선행: [[AT4-b-2_결과_2026-08-12]] §작업1(근본원인 확정) · [[../../전투완성/raw/BT3_MA_상세설계서|BT3_MA_상세설계서]]

## 결론 4줄

1. ★**`DT_Vfx` 5행 전부 `texPath`에 `.AssetName` 서픽스 보정 완료**(값 본체는 무변경, 형식만 정정). 보정 전 5행 실재 애셋(`Texture2D`) 확인 후 적용.
2. ★★**검증 PASS — 5행 전부 `FXSHOW` ≥1 실측**. `BP_FxLabQuad`의 기존 `TestDriver_TEMP` 스캐폴드(100/200/300 커버)에 더해, "제거된 행" 음성 테스트용 두 노드(`63009001`/`63009002`)의 `vfxId` 핀 값을 **일시적으로** `63000400`/`63000500`으로 바꿔 5행 전체를 한 번의 PIE 실행에서 커버했고, 실행 직후 원값으로 완전히 되돌렸다(git diff 0).
3. `FXNOROW:63009999` 등 기존 fail-loud 음성 테스트는 이번 실행에서도 정상 발화 — 회귀 없음.
4. ★**③ 조사 결과**: 다른 8개 DataTable 스키마를 전수 점검, `DT_Sfx.soundPath`가 `DT_Vfx.texPath`와 **동일한 패턴**(소프트 오브젝트 경로를 raw string 컬럼에 저장)임을 확인. 단 현재 3행 전부 `"NONE"` sentinel이라 **아직 실제로 터지지 않은 휴면 상태** — 값이 채워지는 순간 같은 결함이 재현될 위험이 있음(고치지 않고 보고만).

---

## ① `DT_Vfx` 5행 서픽스 보정

### 보정 전 원본 값(전문, 롤백 기준선)

| row | texPath(원본) | colorRow | gridX | gridY | frameCount | fps |
|---|---|---|---|---|---|---|
| 63000100 | `/Game/VFX/T_FX_Smear` | 0 | 5 | 1 | 5 | 10 |
| 63000200 | `/Game/VFX/T_FX_Hit` | 0 | 7 | 1 | 6 | 10 |
| 63000300 | `/Game/VFX/T_FX_CastAtk` | 0 | 13 | 9 | 13 | 20 |
| 63000400 | `/Game/VFX/T_FX_CastSupport` | 0 | 16 | 9 | 16 | 20 |
| 63000500 | `/Game/VFX/T_FX_ProjectileArcane` | 0 | 15 | 9 | 15 | 20 |

(memo 컬럼은 각 행마다 길어서 표 생략 — `get_rows` 원문은 이 세션 로그에 보존. 값 자체는 무변경이므로 롤백은 texPath만 되돌리면 충분함.)

### 실재 확인(보정 전, `AssetTools.exists` + `get_asset_class`)

5행 전부 `exists=true`, `get_asset_class=Texture2D` 확인 — 경로 본체는 전부 정확함, 결함은 서픽스 누락뿐.

### 보정 후 값

| row | texPath(보정 후) |
|---|---|
| 63000100 | `/Game/VFX/T_FX_Smear.T_FX_Smear` |
| 63000200 | `/Game/VFX/T_FX_Hit.T_FX_Hit` |
| 63000300 | `/Game/VFX/T_FX_CastAtk.T_FX_CastAtk` |
| 63000400 | `/Game/VFX/T_FX_CastSupport.T_FX_CastSupport` |
| 63000500 | `/Game/VFX/T_FX_ProjectileArcane.T_FX_ProjectileArcane` |

`set_rows`로 `texPath`만 갱신(다른 컬럼 무변경), `get_rows` 재조회로 반영 확인, `save_assets(["/Game/Data/DT_Vfx"])`로 저장.

---

## ② 검증 — `FXSHOW` 5/5

### 트리거 방식

`BP_FxLabQuad`의 기존 `TestDriver_TEMP` 체인(AT4-b-2가 남긴 8연발, `PlayVfx(63000100)→...→PlayVfx(63000300)→...`)은 100/200/300만 커버한다. 400/500을 추가로 커버하기 위해, 체인 안에 있던 "제거된 행 음성 테스트" 노드 2개(`K2Node_CallFunction_55`: 원래 `vfxId=63009001`, `K2Node_CallFunction_57`: 원래 `vfxId=63009002`)의 `vfxId` 핀 값만 **일시적으로** `63000400`/`63000500`으로 바꿔 재사용했다(새 노드 생성 없음 — 변경 표면 최소화).

트리거 배선: `BeginPlay` 초기화 체인의 진짜 종단(`SetCollisionEnabled(NoCollision).then`, AT4-b-2가 이미 확인한 미배선 지점) → `K2Node_CallFunction_65`(기존에 남아있던, execute/self 미배선 상태의 "Call TestDriver_TEMP" 노드)의 `execute` 핀에 연결. `connect_pins`(execute만) 후 `compile_blueprint`.

### 실행 로그(`max tick rate 3`, PIE 08:32:01 세션, `FXLAB:` 패턴 필터)

```
FXSHOW:63000100:t=0.666667      (63000100, 1회차)
FXHIDE:63000200:t=1.333334      (※ 이전 hide 딜레이 잔영 — 함정 계열, 무시)
FXSHOW:63000200:t=1.666667      ★
FXHIDE:63000200:t=2.333334
FXNOROW:63009999                (fail-loud, 회귀 없음 확인)
FXSHOW:63000400:t=3.000001      ★★ (63009001 자리, 임시 vfxId=63000400)
FXSHOW:63000500:t=3.333334      ★★ (63009002 자리, 임시 vfxId=63000500)
FXSHOW:63000100:t=3.666668      (2회차)
FXHIDE:63000100:t=4.000001
FXSHOW:63000300:t=4.666668      ★
FXHIDE:63000300:t=5.333335
FXSHOW:63000100:t=5.666668      (3회차)
FXHIDE:63000100:t=6.333335
```

### 판정

| row | FXSHOW | 비고 |
|---|---|---|
| 63000100 | ✅ (×3) | t=0.667/3.667/5.667 |
| 63000200 | ✅ | t=1.667 |
| 63000300 | ✅ | t=4.667 |
| 63000400 | ✅ | t=3.000(임시 vfxId 재배정으로 검증) |
| 63000500 | ✅ | t=3.333(임시 vfxId 재배정으로 검증) |

★**5/5 PASS**. `TEXMISS`는 이번 실행에서 0건(이전 실행 로그에 남아있던 `TEXMISS` 항목은 전부 이 세션 이전, 보정 전 실행의 잔여 로그).

### 원복

1. PIE 종료 후 `break_pins`로 `SetCollisionEnabled.then → CallFunction_65.execute` 연결 해제
2. `K2Node_CallFunction_55.vfxId`를 `63009001`로, `K2Node_CallFunction_57.vfxId`를 `63009002`로 복원
3. `get_node_infos`로 4개 노드 전부 원상태 확인(연결·값 모두 원본과 일치)
4. `compile_blueprint` → `save_assets(["/Game/Blueprints/BP_FxLabQuad"])`
5. `git -C D:\unreal\projectTP\Content status --porcelain` → **공백(diff 0)** — 이전 세션(AT4-b-2)보다 더 깨끗하게 원복됨(그때는 재컴파일로 인한 바이너리 diff 1건이 있었음)

---

## ③ 같은 결함이 다른 곳에도 있는가 — 조사 결과(수정 없음, 목록만)

전체 DataTable 9종의 `get_schema` 전수 확인:

| DataTable | 소프트 경로 후보 컬럼 | 판정 |
|---|---|---|
| `DT_JobStats` | 없음(`skillIds`는 ID 목록 문자열, 경로 아님) | 해당 없음 |
| `DT_Motions` | 없음 | 해당 없음 |
| `DT_Skills` | `castFX`/`projectileFX`/`impactFX`/`castSFX`/`impactSFX`(전부 `string`) | ★현재 **전 7행 공백(`""`)** — 실사용은 병렬 정수 컬럼(`fxCastId`/`fxProjectileId`/`fxImpactId`/`sfxCastId`/`sfxImpactId`, DT_Vfx/DT_Sfx row ID 참조)이 담당. 문자열 컬럼은 죽은 슬롯으로 추정, 값이 없어 서픽스 결함 자체가 성립하지 않음 |
| `DT_SkillEffects` | 없음 | 해당 없음 |
| `DT_StatusEffects` | `iconKey`(`string`) | 전 6행 공백. `nameKey`/`descKey`와 동일 계열의 로컬라이제이션/UI 키로 추정(경로 아님 가능성), 공백이라 판별 불가 |
| `DT_Vfx` | `texPath` | ★**이번에 보정 완료** |
| `DT_Stagings` | 없음 | 해당 없음 |
| `DT_Sfx` | `soundPath`(`string`) | ★★**`DT_Vfx.texPath`와 완전히 동일한 패턴** — 소프트 오브젝트 경로를 raw string으로 저장하는 설계. 단 현재 3행 전부 `"NONE"`(명시적 미배정 sentinel, memo에 "알파 정상"이라 기록됨) — **아직 실제 경로 값이 입력된 적이 없어 결함이 휴면 상태**. 값이 채워지는 순간(오디오 임포트 단계) `.AssetName` 서픽스 없이 손입력되면 `DT_Vfx`와 동일하게 100% 재발할 것으로 예상 |
| `DT_Strings` | 없음(순수 로컬라이제이션 ko/ja/en) | 해당 없음 |

### 결론

- ★**`DT_Sfx.soundPath`가 유일한 실질적 위험 컬럼**이다 — 값 입력 시점(오디오 임포트/D6 단계 추정)에 이번과 동일한 사전 점검(서픽스 확인)이 필요.
- `DT_Skills`의 FX/SFX 문자열 컬럼 5종은 죽은 슬롯으로 보이나 balance-designer가 의도한 용도가 있는지 확인 필요(정리 대상인지 판단은 PM/balance 소관).
- 이번 세션에서는 위 항목 전부 **조사만 하고 수정하지 않았다**(지시 준수).

---

## 산출물 / 규율 준수

| 항목 | 내용 |
|---|---|
| `DT_Vfx` | `/Game/Data/DT_Vfx` — 5행 `texPath` 서픽스 보정, 저장 완료. Content 저장소 커밋 `79d3cac` |
| `BP_FxLabQuad` | `/Game/Blueprints/BP_FxLabQuad` — 검증용 임시 배선(연결 1건 + 핀 값 2건) 후 완전 원복, git diff 0(커밋 없음, 변경 없어 커밋 대상 아님) |
| `BP_BattleManager`/`BP_BattleSpawnPoint` | 무접촉(이번 세션에서 조회조차 안 함) |
| `max tick rate` | **3**(이번 PIE 세션 로그 `LogWorld: ... (max tick rate 3)` 직접 확인, 함정95/100과 일치) |
| push | 안 함 |

## 게이트별 PASS/FAIL

| # | 게이트 | 판정 | 근거 |
|---|---|---|---|
| ① 서픽스 보정 | **PASS** | 5행 전부 보정 전 실재 확인(`exists`+`get_asset_class=Texture2D`) 후 서픽스만 추가, 값 본체 무변경 |
| ② `FXSHOW` 5/5 | ★**PASS** | 5행 전부 `FXSHOW` 실측(HIDE 단독 판정 배제, 지시대로 SHOW만 근거로 판정) |
| ② 회귀 없음 | **PASS** | `FXNOROW:63009999` 정상 발화 유지 |
| 규율 — 라이브 전투 BP 무접촉 | **PASS** | `BP_BattleManager` 등 조회조차 안 함 |
| 규율 — 값 출처 존중 | **PASS** | 경로 본체 변경 없음, 서픽스(형식)만 정정. 본체 변경이 필요한 행 없음(5행 전부 실재 확인) |
| 규율 — `save_assets` 경로 명시 | **PASS** | 매 호출 경로 배열 명시(함정102 재발 없음) |
| ③ 범위 확대 금지 | **PASS** | 조사만 수행, 다른 DT 수정 0건 |

## ★PM 확인 요청

| # | 항목 | 사유 | 처리 |
|---|---|---|---|
| 1 | `DT_Sfx.soundPath`가 `DT_Vfx.texPath`와 동일한 결함 패턴을 가짐(현재 휴면) | 값이 아직 전부 `"NONE"`이라 지금은 안 터지지만, 오디오 데이터가 채워지는 시점에 동일 버그가 재발할 것으로 예상됨 | D6/오디오 임포트 단계 착수 시 **미리 서픽스 규칙을 공유**하거나, 입력 검증 로직(BP 쪽에 "서픽스 없으면 자동 보정" 가드)을 추가할지 PM/balance-designer 판단 필요 |
| 2 | `DT_Skills`의 `castFX`/`projectileFX`/`impactFX`/`castSFX`/`impactSFX` 5개 문자열 컬럼이 전 행 공백, 실사용은 병렬 정수 ID 컬럼이 담당 | 죽은 슬롯으로 보이나 의도 확인 안 됨 | 정리(컬럼 제거) 여부는 balance-designer/PM 판단, 이번 세션에서 손대지 않음 |

## 관련

[[AT4-b-2_결과_2026-08-12]] · [[../../전투완성/raw/BT3_MA_상세설계서|BT3_MA_상세설계서]] · [[../../../reference/언리얼_MCP_실전노하우|MCP 실전노하우]] 함정95·100·102
