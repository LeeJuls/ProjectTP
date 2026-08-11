---
type: raw
project: projectTP
feature: 스킬연출구조
stage: E-S2
updated: 2026-08-11
status: 원인 확정 — bThrottleCPUWhenNotForeground 기본값(true) 미적용 상태
---

# E-S2 틱 스로틀 진단 — Director 직접 조사

> 계기: S2 에이전트가 *"이 MCP 환경에서 World Tick 자체가 진행되지 않는다"*고 보고. 사실이면 **타이밍 기반 BP 전체를 MCP로 검증할 수 없다**는 뜻이라 파급이 커 Director가 직접 엔진 로그를 조사했다.

## 에이전트 보고 (원문 요지)

> *"`warmupSeconds`를 20초까지 늘려도, PlayMode를 바꿔도 `RetriggerableDelay`가 한 번도 완료되지 않았고 **`Tick` 이벤트조차 단 한 번도 발화하지 않았다**. → 이 MCP `StartPIE` 세션에서 **World Tick 자체가 진행되지 않는다**(frame 0의 BeginPlay 동기 실행만). 타이밍 기반 BP 로직 전체가 구조적으로 검증 불가."*

에이전트는 5회 시도 후 **3회 실패 규칙에 따라 중단하고 보고**했다 — 절차상 옳은 판단이다.

---

## ★결론 — 진단이 틀렸다. 틱은 돈다

### 반증 1 — 프레임 카운터가 진행한다

엔진 로그 대괄호 두 번째 값이 **프레임 번호**다.

```
[07.24.55:157][768] FXLAB:DIAG:LoadAsset.then fired
[07.26.03:484][973] FXLAB:TEXMISS:...
```

**768 → 973.** 68초 동안 **205프레임**이 진행했다. 프레임 0에 멈춰 있지 않다.

### 반증 2 — 같은 로그에 정상 속도 세션이 있다

```
14회  up for play (max tick rate 3)
 2회  up for play (max tick rate 60)     ← ★
```

같은 날 같은 레벨 같은 도구인데 **07:28:08과 07:31:55 두 세션은 60fps로 돌았다.** 구조적 불가능이 아니라 **조건 의존**이다.

---

## ★진짜 원인 — `max tick rate 3`

```
LogWorld: Bringing World .../map_battle_fxlab up for play (max tick rate 3)
```

**초당 3틱.** `205프레임 / 68초 ≈ 3.0` — 로그의 프레임 진행률과 정확히 일치한다.

이건 UE의 **`bThrottleCPUWhenNotForeground`**(에디터 Preferences의 *"Use Less CPU when in Background"*)가 켜져 있을 때 나타나는 전형적 값이다. 에디터 창이 포그라운드가 아니면 3fps로 제한된다.

### 왜 3fps에서 `AsyncLoadAsset`이 완료되지 않는가

게임 시간(델타타임)은 3fps에서도 정상적으로 누적되므로 `Delay(0.45)`는 원리적으로 2틱이면 끝난다. 그러나 **비동기 에셋 로딩은 틱당 시간 예산(time slice)에 묶여** 있어, 틱이 초당 3회뿐이면 스트리밍이 사실상 진행되지 않는다. → `Completed`가 오지 않고, 에이전트가 `then` 핀으로 우회하자 그 시점엔 `Object`가 아직 `None`이라 `TEXMISS`로 빠졌다.

★**그래서 "그래프 결함"으로 보이는 증상이 나왔다.** 실제 그래프는 정상이다.

---

## ★★가장 아픈 발견 — 3주 전에 적어두고 적용하지 않았다

[[언리얼_MCP_실전노하우]]에 **이미 두 곳**에 적혀 있다:

- 함정⑦ — *"`bThrottleCPUWhenNotForeground=true`(기본값)이면 MCP가 에디터와 통신하는 동안 PIE 게임 틱이 사실상 정지할 수 있다"*
- §19 — *"스로틀 설정 — 개발 기간 동안 **false 유지 권장**"*

**그런데 실측 결과 설정 항목 자체가 어디에도 없다.**

```bash
grep -rn "ThrottleCPU" projectTP/Saved/ projectTP/Config/
# → 0건
```

`Config/*.ini`에도 `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`에도 없다. **항목이 없으면 엔진 기본값 `true`가 적용된다.**

→ **"권장"이 문서에만 남고 실제로 적용된 적이 없다.** 3주 뒤 다른 기능의 진단을 오염시켰고, 에이전트가 *"구조적으로 검증 불가"*라는 훨씬 무거운 결론에 도달하게 만들었다.

★이건 [[E-S4a-0_struct자동화_조사결과]]에서 겪은 것과 **같은 계열**이다 — *"문서에 답이 있었는데 연결되지 않았다."* 다만 이번은 더 나쁘다: 그쪽은 **읽었으면 찾을 수 있었고**, 이쪽은 **읽어도 "이미 false겠지"라고 믿게 만드는 문장**이 적혀 있었다.

---

## 해법

에디터 Python 콘솔에서 한 줄:

```python
s = unreal.get_default_object(unreal.EditorPerformanceSettings); s.set_editor_property('throttle_cpu_when_not_foreground', False); s.save_config()
```

또는 GUI: **Edit → Editor Preferences → General → Performance → "Use Less CPU when in Background" 체크 해제**.

★**`save_config()`가 핵심** — 이걸 빼면 이번 세션만 적용되고 재시작하면 원상복귀한다. 지금 상태가 정확히 "설정이 저장된 적 없음"이다.

**적용 후 확인 방법**: PIE를 켜고 로그에서 `up for play (max tick rate 60)`이 나오는지 본다. `3`이면 아직 안 걸린 것이다.

---

## 파급 — 이번 건에 그치지 않는다

| 영향 | 내용 |
|---|---|
| **S2 판정 5건** | 스로틀 해제 후 재검증하면 통과 가능성이 높다. 그래프 결함이 아니다 |
| **과거 "PIE 검증 PASS" 기록 전반** | 3fps에서 관측한 타이밍은 **신뢰도가 낮다.** 특히 Delay·Async가 걸린 검증. 다만 BeginPlay 동기 체인 검증(대부분의 로직 검증)은 영향 없다 |
| **함정⑦의 지위** | *"정지할 수 있다"*(불확실)에서 **"기본값이 켜져 있고 실제로 3fps로 제한된다"**(확정)로 승격 |
| **앞으로의 latent 검증** | 스로틀 해제가 **선행 조건**이다. 안 하면 같은 오진이 반복된다 |

---

## ★교훈 — "틱 정지"와 "틱 스로틀"을 구별하는 법

증상이 거의 같다(latent 노드가 안 끝난다). 구별은 **로그 프레임 카운터** 하나면 된다:

| 관측 | 해석 |
|---|---|
| 프레임 번호가 **고정** | 진짜 정지 — 모달 블로킹(함정㉓) 계열 의심 |
| 프레임 번호가 **느리게 증가** | 스로틀 — 설정 문제 |
| `up for play (max tick rate N)` | ★**N을 직접 읽어라.** 이 한 줄이 전부다 |

에이전트는 `Event Tick`에 로그를 걸어 확인하려 했는데, **3fps에서는 20초 대기해도 로그 버퍼 조회 타이밍에 따라 0줄로 보일 수 있다.** 반면 `max tick rate`는 PIE 시작 시 **항상 한 줄로 찍힌다.** 이쪽이 결정적이다.
