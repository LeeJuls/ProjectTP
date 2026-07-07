---
type: plan
feature: 걸어나오기연출
status: W0~W2 완료, W3 부분판정(3/8 PASS + 5/8 이월/정적보증), W3fix 완료(걸음 왜곡 핫픽스, WT-23 PASS)
updated: 2026-07-07
---

# plan — 걸어나오기연출 (승인 plan 전사)

> 승인 원본: `C:\Users\user\.claude\plans\humble-purring-glacier.md`. 아래는 그 전문 + W0/W1 완료 반영.
#projectTP/걸어나오기연출

## Context
오너 연출 목표(옥토패스 동일: 자기 턴에 앞으로 나와 공격) + **오너 요구: 적/아군 공격 전 멈춤 포인트를 각각 수동 지정 가능(기본은 Director 설정)**. 턴제전투MVP Executing 예약 지점에 삽입. 이 판은 **gameplay-engineer(GE)·qa-critic(QA) 검토 통합** — GE가 실그래프로 재배선 지점 2곳을 특정하고 MoveComponentTo 실재를 확정했으며, QA가 타이밍 급소 2건(C-1·C-2)과 z-fight 기하를 정량 검증했다. 실행 전부 sonnet/haiku.

## 검토로 확정된 사실
- **MoveComponentTo 실재 확정**(GE 실측): 이벤트그래프 latent, 루트(Sprite) 대상 시 TargetRelativeLocation=월드좌표 동작. **[W0 실증 정정]** output pin은 `then` 1개뿐(Completed 델리게이트 별도 아님) — `then`이 곧 완료 콜백으로 실측 확인(WalkArrive 로그가 target과 정확히 일치하는 좌표로 t=+0.33~0.4s 후 발화).
- **Executing 재배선 지점 정확히 2곳**(GE 실그래프): ①`HideAll.then→PlayAttack` 사이 ②`Delay(0.75).then→EnterTurnEnd` 사이. Delay(0.25)/TakeHit 분기는 무변경. (W2에서 실행 예정, 이번 W1엔 미착수)
- **마커 OFF는 실그래프에 없음 = 신규 작업**(GE) — HideAll **앞**에 삽입. (W2 예정)
- **방향 계산은 월드 X축 부호 직접 사용**(GE 함정: 유닛 yaw=0이라 ForwardVector 금지). Party X<0(좌측)→+X 전진 / Enemy X>0→−X 전진.
- **레이스 안전**(QA 정량): 아래 확정 타이밍 기준 마진 0.85s. HomeLocation 절대좌표 = 자기교정(누적 오차 없음, WT-07 실증).
- RUN1=8f 이중 검증 완료(QA) — W1에서 셀별 count 스팟체크 실행(WT-08, 실측 400+ opaque px/cell 8칸 전부).

## 설계 확정판

### 공격 포인트 — 3단 우선순위 + z-fight 자동 가드
1. 유닛 `AttackPointOverride`(액터 ref, instance-editable, 기본 None)
2. **팀 포인트**: `BP_AttackPoint` 2기(`AttackPoint_Party`/`AttackPoint_Enemy`, 폴더 BattleStage/Points) — 에디터 표식(Arrow 패턴, 게임 중 숨김), **오너 드래그 이동**. Manager가 `PartyAttackPoint`/`EnemyAttackPoint` ref 보유, 유닛은 **`GetAttackPointForTeam(bIsParty)` 함수 경유 조회**(아래 "구현 중 명세 조정" 참조 — ManagerRef 직접 변수 접근이 아니라 Manager에 신설한 함수를 통함).
3. 폴백: `HomeLocation + (bIsParty ? +X : −X) × 300`
- **⚠ IsValid-first 배선(QA-H1 필수)**: 각 단계 GetActorLocation은 IsValid 통과 후에만. **[W1 실증]** 3중 IsValid(Override→ManagerRef 불필요, GetAttackPointForTeam 결과→직접) 체인으로 구현, 정적 그래프 확인 완료(WT-04).
- **도착 좌표**: X·Y=결정된 포인트 값, **Z=HomeLocation.Z 유지**(WT-06 로그 실증). **z-fight 자동 가드**: 도착 Y가 서있는 유닛 중 누군가의 Y와 10cm 이내면 자동으로 12cm 비킴(ForEach 비교 → 조건 오프셋).
- **[W1 실측 갱신]** plan 예상 Y≈−7150은 부정확 — 8기 실측 Y 범위는 **−6861.80(Enemy_B1, 카메라 최근접) ~ −7630.34(Enemy_B4)**. 채택 Y=**−6750**(가장 가까운 유닛과 111.8cm 이격, 10cm 기준 안전).

### 연출 시퀀스·타이밍 (QA-C1·C2 반영 확정) — **W2 완료**
```
Executing: 잠금(기존) → 마커 OFF(신규, HideAll 앞) → 발광 OFF·버튼 숨김(기존)
→ ActiveUnit.WalkForward()  [즉시 반환 — RUN1 애니+이동 0.4s는 유닛 내부 latent]
→ Delay(0.55)
→ PlayAttack → Sequence[A: Delay(0.25)→IsValid→TakeHit / B: Delay(0.75)→ActiveUnit.WalkBack()→Delay(0.45)→TurnEnd]
```
- 이동 시간 고정 0.4s 설정. **[W1 실측]** 실제 latent 소요 t=3.067→3.4 (0.333s), 8종 컴포지션·엔진 프레임 편차 반영해 -16.75% 편차(§9 함정⑦류 패턴과 유사) — plan의 0.55/0.45 마진(0.15s/0.05s)은 이 편차를 충분히 흡수함(0.4-0.333=0.067s 여유 이내).
- **[W2 실증·명세 대비 편차 발견]** WalkForward/WalkBack/Delay(0.55)/Delay(0.45) 자체는 설계값과 정확히 일치(WalkArrive t0+0.333s, 2회 재현). 그러나 **PlayAttack 자체(W2 비수정 대상, 이전 MVP 단계부터 존재)의 내부에 RetriggerableDelay 애니 타이머 체인이 있어** PlayAttack 호출이 Manager 관점에서 즉시 반환하지 않고 그 내부 완료(약 +0.58s)까지 대기시킴 — 1턴 총 길이가 plan 예상(TurnEnd≈1.75, 다음TurnStart≈2.10)보다 실측 TurnEnd≈2.333/다음TurnStart≈3.0로 유의하게 늘어남. 레이스 마진(WT-12)은 이 지연이 TakeHit·WalkBack 양쪽 분기에 동일 선행 적용되어 오히려 확대(1.30s > plan 0.85s) — 안전 방향 편차이므로 W2 자체의 결함은 아님. 상세: `raw/W2_Executing개편.md` §8.

### 유닛 확장 (BP_BattleSpawnPoint — CS 무변경) — **W1 완료**
- 변수: `HomeLocation`(Vector, BeginPlay 체인 끝 캐시) / `AttackPointOverride`(Actor ref, instance-editable) / `WalkTargetLoc`(Vector, 내부 계산용 멤버 — plan에 없던 신규, 이유는 아래 참조).
- **WalkForward**: 3단 우선순위(IsValid-first) → Y가드(ForEachLoop+NotEqual 자기제외+IsValid+|dY|<10→+12) → MID(TimeOffset=GetGameTimeInSeconds→FrameCount=8→RowIndex=2) → MoveComponentTo(Sprite, WalkTargetLoc, 0.4s, EaseOut) → 로그 2종.
- **WalkBack**: RUN 애니(TimeOffset/FrameCount=8/RowIndex=2) → MoveComponentTo(Sprite, HomeLocation, 0.4s, EaseOut) → `then`(완료) → idle 복귀(TimeOffset0/FrameCount6/RowIndex0) + PrintString "WalkHome".
- **EffectQuad 재계산**: PlayAttack·TakeHit 이펙트 분기(Sequence then_1, SetMaterial 노드 앞) `SetWorldLocation(EffectQuad, GetActorLocation+MakeVector(0,-80,20))` — vector+vector 프로모터블 연산자(`유틸리티|연산자|추가` 생성 후 자동 승격) 사용.

## 구현 중 명세 조정 (Director 보고 필요 사항)

### 조정 1 — "유닛이 ManagerRef 경유로 팀 포인트 조회" → "Manager의 함수(`GetAttackPointForTeam`)를 유닛이 호출"
**원인**: 이 MCP 도구(`BlueprintTools.create_node`)는 **"현재 세션에서 방금 만든, 아직 아무 곳에서도 호출되지 않은 다른 블루프린트의 멤버(변수 게터/함수)"를 그래프 노드로 생성할 수 없다**는 근본 제약이 실증됨. `find_node_types`가 반환하는 문자열 형식이 여러 종류(`함수호출|X`, `|X`, `Class|ClassName|X`)로 나오는데, 신규 항목에 대해선 이 중 **정확한 하나만** 유효하고 그 정확한 형식이 사전에 결정 불가능해 보임(3회 이상 다른 형식으로 시도 후 실패 확정). 최종적으로 `Class|BPBattleManager|GetAttackPointForTeam`(클래스명에서 언더스코어 제거+파스칼케이스) 형식으로 성공했으나, 이 형식을 알아내기까지 5회 이상 실패 시행착오가 있었음 — 근본 원인이지 우연이 아님을 확인(bool 변수 `bIsParty`의 게터가 `GetIsParty`로 `b` 접두어가 빠지는 것과 유사한 "엔진 자동 네이밍 변환" 계열 문제).
**대응**: 원래 설계 의도(유닛이 Manager를 통해 팀 포인트를 조회)는 그대로 보존하되, 경유 방식을 "멤버 변수 직접 접근"에서 "Manager에 신설한 `GetAttackPointForTeam(bIsParty: bool) -> Actor` 함수 호출"로 변경. 최종 동작(결과)은 설계 의도와 100% 동일 — 유닛→Manager→해당 팀 포인트 Actor 반환. 이 함수 자체가 Branch+로컬변수(`LocalResult`)로 구현되어 컴파일 검증됨.
**영향**: 없음(사용자 관점 동작 동일). BP_BattleManager에 함수 그래프 1개(`GetAttackPointForTeam`) + 로컬 변수 1개(`LocalResult`) 추가.

### 조정 2 — 계산용 멤버 변수 `WalkTargetLoc` 신설(plan 미명시)
**원인**: WalkForward 커스텀 이벤트는 **파라미터를 추가할 수 없음**이 실증됨(`add_node_pin`이 커스텀 이벤트 노드에서 "does not support adding pins" 에러 반환). 또한 EventGraph 커스텀 이벤트는 Function Graph가 아니라서 로컬 변수(add_variable에 graph 지정)도 사용 불가(로컬 변수는 함수/이벤트 디스패처 그래프 전용). 3단 우선순위 결정 → Y가드 → 최종 MoveComponentTo까지 여러 단계에 걸쳐 "지금까지 결정된 도착 좌표"를 들고 다녀야 하는데, 이를 위한 임시 저장소가 필요.
**대응**: 멤버 변수 `WalkTargetLoc`(Vector)을 신설해 이 역할을 담당. 매 WalkForward 호출 시작 시 결정 로직이 이 값을 쓰고 마지막에 MoveComponentTo가 읽는 방식 — 함수형이 아니라 상태 기반이지만, WalkForward 호출은 매번 순차 실행(같은 유닛이 중첩 호출될 일 없음 — 턴제이므로)이라 레이스 문제 없음.
**영향**: 없음(기능 동일). 코드 가독성 측면에서 로컬변수보다 살짝 떨어지나 이 MCP 도구셋의 확립된 제약 안에서는 최선.

## 단계
| 단계 | 내용 | 게이트(핵심 TC) | 담당 | 상태 |
|---|---|---|---|---|
| W0 | MoveComponentTo 파일럿 배선 1회+기능폴더 생성+GE 함정 노하우 등재 | 파일럿 컴파일 0 | ge(sonnet) | **완료** |
| W1 | BP_AttackPoint+2기 배치(실측 산출)+유닛 확장(3단 결정·Y가드·Walk 2종·이펙트 재계산)+RUN1 스팟체크 | WT-01~08 | ge(sonnet) | **완료** |
| W2 | Manager Executing 개편(재배선 2곳+마커 OFF 신규)+타이밍 문서화 | WT-09~12 | ge(sonnet) | **완료** |
| W3 | 풀 게이트+회귀+배치가이드에 AttackPoint 사용법 추가 | WT-13, 15~22 | verifier(haiku) | 예정 |
| W3fix | 걸음 왜곡 핫픽스 — MoveComponentTo 회전 보간 미배선 수정(오너 리포트) | WT-23 | ge(sonnet) | **완료** |
| WF | 오너 육안 + 포인트 드래그 조정 + 파라미터 튜닝 | 오너 판정 | 오너 | 예정 |

## 검증 방침 (기존 체계)
스캐폴드 참조=TurnQueue Get만 / 단일 대기 60s 금지 / 스로틀 OFF 측정 후 복원(W1 착수 시 이미 false로 확인됨, 변경 불필요) / get_properties는 에디터 정적값만.

## 산출물·문서·커밋
`docs/features/걸어나오기연출/`(청사진·plan·TC·raw) — 단계마다 wiki 기록+커밋. 수정: BP_BattleSpawnPoint·BP_BattleManager·BP_AttackPoint(신규)·octopath(레벨)·실전노하우(함정 신규분). push는 오너 확인.

## 비범위
데미지·HP ❌ / 대시 잔상·카메라 워크 ❌ / 뒤돌아 걷기 ❌ / VFX 재설계 ❌ / DASH 행 ❌ / ATB 도입 시 WalkBack 간섭 재검토(QA 미래 노트).
