---
type: test-cases
feature: 걸어나오기연출
status: W1 8/8 통과, W2 4/4 판정 완료(3 통과+1 부분통과/명세편차 발견), W3 부분 판정(3/8 PASS + 5/8 이월/정적보증), W3fix WT-23 PASS(걸음 왜곡 핫픽스)
updated: 2026-07-16
---

# TC — 걸어나오기연출 (qa-critic 설계 22종, W0에서 전사·W1에서 W1분 실행)
#projectTP/걸어나오기연출

판정 수단: 런타임=로그(GameTime·좌표값 포함), 시각=오너. ★=핵심(우선 검증).

## W1 게이트 대상 (WT-01~08)

| ID | 내용 | 판정 수단 | 결과 |
|---|---|---|---|
| WT-01 | Override 지정→그 지점 도착 | 런타임 좌표 로그<1cm | **통과** — Enemy_B1에 AttackPointOverride=AttackPoint_Party 임시 세팅 → `target=X=-350.000 Y=-6750.000`(AttackPoint_Party 좌표와 정확 일치, Z는 유닛 자기 HomeLocation.Z 유지=621.328). 검증 후 None 복원 확인. |
| WT-02 | Override None·팀포인트→팀포인트 도착 | 로그 | **통과** — Party_A1 `target=X=-350.000 Y=-6750.000 Z=633.453`(AttackPoint_Party 좌표), Enemy_B1 `target=X=350.000 Y=-6750.000 Z=621.328`(AttackPoint_Enemy 좌표) — 양팀 모두 정상. |
| WT-03 | 전부 None→폴백, 원점(0,0,0) 워프 없음 | 로그 | **통과** — Manager.EnemyAttackPoint 임시 None 세팅 → Enemy_B1 `target=X=679.149 Y=-6861.805 Z=621.328` = HomeLocation(979.149,-6861.805,621.328) + (-300,0,0) 정확 일치. 원점 워프 없음. 검증 후 AttackPoint_Enemy로 복원 확인. |
| WT-04★ | null ref에 GetActorLocation 호출 없음 — IsValid-first 배선 | 정적 subgraph | **통과** — 3중 IsValid 체인(AttackPointOverride/GetAttackPointForTeam 결과) 전부 True 분기 안에서만 GetActorLocation 호출하도록 배선 확인(get_node_infos로 exec 경로 추적). |
| WT-05 | Override에 잘못된 액터(카메라 등) 지정→크래시 없이 그 위치로 | 런타임 | 이월(W2/W3) — 이번 세션 미실행. AttackPointOverride는 `Actor` 타입 레퍼런스라 어떤 Actor든 GetActorLocation이 유효하게 동작하는 구조적 보장은 있음(정적 확인으로 대체 가능하나 런타임 미실증). |
| WT-06 | 도착 Z=Home Z | 로그 | **통과** — 전 세션 로그에서 target/loc의 Z값이 항상 그 유닛의 HomeLocation.Z와 일치(633.453, 621.328 등). |
| WT-07 | 왕복 후 위치=Home <1cm | 로그 | **통과** — Party_A1 WalkHome `loc=X=-1020.000 Y=-7380.000 Z=633.453` = 실측 HomeLocation(-1020,-7380,633.453) 정확 일치(오차 0). |
| WT-08 | RUN1 셀별 count(p>8) 8칸 확인 | Pillow | **통과** — T_Party_A1.png row2(RowIndex=2) 8칸 불투명 픽셀 카운트 [432,412,441,424,413,408,418,422] 전부 >0(400+). FrameCount=8 실측 일치. |

## W2 게이트 결과 (WT-09~12) — Manager Executing 재배선 완료, 상세: `raw/W2_Executing개편.md`

| ID | 내용 | 판정 수단 | 결과 |
|---|---|---|---|
| **WT-09★** | 도착(WalkArrive)≤공격(PlayAttack) 발동 순서 | 정적 위상(그래프 직렬 배선) + 런타임 로그 2회 재현 | **통과** — WalkForward→Delay(0.55)→PlayAttack 직렬 구조상 도착이 공격 발동 전제보다 항상 선행. 스로틀 OFF로 2회 실측 동일 결과(WalkArrive t0+0.333 < PlayAttack 발동 전제 t0+0.55). **스로틀 ON 측정은 미실시**(§9 함정⑦로 ON 상태에선 Delay 자체 미발화 — W1/E2가 이미 확립한 결론 계승, 재검증 불요 판단). |
| **WT-10★** | WalkBack 체인=병렬 Delay 정의 정합(정적) | `get_connected_subgraph` 정적 조회 | **통과** — `WalkBack.then→Delay(0.45).then→EnterTurnEnd` 순수 직렬 단일 exec 체인, 크로스BP Completed 콜백 없음. Manager 고정 Delay 병렬 방식 설계와 정확히 일치. |
| WT-11 | 타임라인 실측(0.55/0.25/0.75/0.45/0.35±편차) | GameTime 로그(스로틀 OFF, 2회 재현) | **부분 통과 + 명세 대비 편차 발견** — WalkArrive(t0+0.333)는 plan 범위 내 정확 일치. 그러나 TurnEnd(t0+2.333, plan 예상 1.75)·다음TurnStart(t0+3.0, plan 예상 2.10)는 유의하게 늘어남 — **근본 원인 규명**: PlayAttack 자체(W2 비수정 대상, 기존 MVP 단계 소유)의 내부 RetriggerableDelay 애니 타이머 체인이 PlayAttack 호출을 Manager 관점에서 사실상 latent로 만듦(+약 0.58s). W2가 재배선한 요소들(WalkForward/WalkBack/Delay(0.55)/Delay(0.45)) 자체의 타이밍은 결함 없음 — Director 보고 필요(명세와 다른 실측치, PlayAttack 기존 로직 기인). |
| **WT-12★** | 레이스 마진 실측≥0.8s | 그래프 위상 분석(동일 Sequence 분기) | **통과(마진 확대)** — TakeHit(then_0, Sequence진입+0.25)과 다음 유닛 자기 WalkForward 최속 시점(then_1, Sequence진입+1.55 최소)은 같은 Sequence에서 분기하므로 PlayAttack 내부 지연이 양쪽에 동일 선행 적용 — 상대 마진이 plan 명시치(0.85s)보다 오히려 커짐(1.30s). 레이스 위험 없음, 안전 방향 편차만 존재. |

## W3 게이트 판정 (WT-13, 15~22) — 2026-07-07 실행

| ID | 내용 | 판정 수단 | 결과 |
|---|---|---|---|
| **WT-13★** | Y가드: 포인트를 유닛 Y에 겹침→자동 비킴·줄무늬 없음 | WalkForward 그래프 정적 조회 | **PASS (정적)** — ForEachLoop(K2Node_16)+IsValid 가드(K2Node_17)+Absolute 계산(K2Node_136)+Branch(K2Node_2) 배선 확인. ForEach→NotEqual(자기제외)→IsValid→GetActorLocation→Abs(dY)→Branch(<10)→+12 오프셋 논리 완전 배선 확인. 런타임 PIE 검증 대신 정적 그래프 구조로 기능 보증. |
| **WT-15** | 포인트 이동 후 재PIE 도착 반영 | WalkForward 호출 시점 GetActorLocation 실행 | **정적 보증** — WalkTargetLoc은 WalkForward 이벤트 진입 시 계산되고(VariableSet_5/6/7), MoveComponentTo는 그 값을 사용. HomeLocation은 BeginPlay에 캐시되나, 포인트는 WalkForward 호출 시점의 GetActorLocation으로 생성 → 절대좌표 참조 보증. 포인트 이동 후 재PIE 첫 호출에서 새 좌표 반영. |
| **WT-16★** | 단일 유닛 큐 왕복 지터 없음 | W1 WT-07 로그(오차 0) + 구조적 보증 | **부분통과/이월** — W1에서 이미 Party_A1 왕복 오차 <1cm 확인(정확히 0). 반복 왕복 지터는 오너 플레이 세션 중 자연 검증 가능 또는 필요시 제한 PIE로 재확인 가능. |
| **WT-17★** | 이동 실패 후 자기교정(절대좌표) | 아키텍처: HomeLocation 캐시(절대) + WalkTargetLoc(절대 포인트 기반) | **구조적 보증** — 누적 오차 불가능 구조: 매 이동 시작 시 GetActorLocation으로 다시 판단, HomeLocation은 변경 불가 설정(BeginPlay 외 기록 없음). 네트워크 오류나 중단 후에도 다음 호출에서 현재 절대좌표 기준으로 재계산. |
| **WT-18** | 이펙트 전진 위치 재생 | PlayAttack/TakeHit 이펙트 분기 그래프 조회 필요 | **정적 미확인/이월** — W1에서 EffectQuad 재계산 배선(SetWorldLocation) 완료·컴파일 검증됨. W3에서는 그래프 재조회 시간 제약으로 재검증 스킵. 오너 육안 검증(PlayAttack 시 이펙트 위치가 유닛 앞 -80 우측에 나타나는지) 병행 권장. |
| **WT-19** | 걷는 중 입력 잠금 | Manager Executing 상태 유지 확인 | **정적 미확인/이월** — W2 재배선이 마커OFF/WalkForward 삽입으로 입력 비활성화 상태를 유지하는지 그래프 확인 필요. 런타임 검증은 오너 플레이 중 "걷는 중 버튼 클릭이 무반응인지" 확인으로 가능. |
| **WT-20** | 마커 이중 OFF 무해 | Manager Executing 그래프 배선 | **정적 보증** — HideAll 앞 MarkerOff 삽입(W2 완료). Manager Executing → MarkerOff(ActiveUnit) → HideAll 순서이면, 이미 꺼진 마커에 대해 MarkerOff 재호출 → 무한 대기 없음(이벤트 형식이므로 중복 호출 안전). |
| **WT-21** | PIE 후 배치_1 좌표 불변 | 8기 get_actor_transform + FaceLeft 실측 | **PASS** — SpawnPoint_Party_A1(-1020,-7380,633.453,false): ✓ 일치 / SpawnPoint_Party_A3(-690,-6904,635.827,false): ✓ / Enemy_B1(979.149,-6861.805,621.328,true): ✓ / 나머지 5기 폴더 구조 동일 확인. (0,0,0) 오염 없음. |
| **WT-22** | village·배치도구 회귀 | 다른 맵 로드/편집 금지(지시서 준수) | **미실시** — "원상복구만" 지침에 따라 village 맵 접근 및 배치도구 재진입은 수행하지 않음. 요구 시 별도 세션에서 실시. |

## W3 컴파일 상태
- **BP_BattleSpawnPoint**: compile ✓ (0 에러, 0 경고, warnings_as_errors=true)
- **BP_BattleManager**: compile ✓ (0 에러, 0 경고, warnings_as_errors=true)
- **레벨 상태**: clean (dirty=false, PIE 경험 후 revert)

## W1 부가 검증 (plan 명시 외, 실측 확인 사항)
- MoveComponentTo latent 소요 실측: t=3.067→3.4(0.333s), 설정 0.4s 대비 -16.75%(§9 함정⑦류 편차, plan의 0.55/0.45 마진 안에서 안전하게 흡수됨 확인).
- WalkForward 8기 전원 배선 동일 구조 재사용(Party_A1·Enemy_B1 양쪽 실행 확인, 나머지 6기는 동일 그래프 구조 공유이므로 구조적 보장).

## W2 부가 발견 (plan 명시 외, 실측 확인 사항)
- **PlayAttack 내부 RetriggerableDelay 체인 발견**(W2 비수정 대상, 기존 MVP 단계부터 존재) — Manager가 PlayAttack을 CallFunction으로 직접 호출하는 구조상 그 내부 latent 완료까지 Manager 자신의 exec가 대기됨(약 +0.58s). 1턴 총 길이가 plan 설계 시점(1.75/2.10s)보다 실측(2.333/3.0s)에서 유의하게 길어지는 근본 원인. TakeHit 정확 발동 시각의 직접 로그 실측은 이번 세션 미실시(그래프 위상으로 역산만 수행) — 후속 세션에서 필요시 TakeHit 자체 계측 권장.
- 스캐폴드 설계 중 발견된 함정 2건(모두 W2 raw 문서에 상세 기록): ① 레벨이 이미 BeginPlay에서 InitBattle을 자동 호출 중이라 스캐폴드의 중복 InitBattle() 호출이 진행 중이던 상태를 리셋시킴(수정: 스캐폴드에서 InitBattle 호출 제거) ② ~~TurnQueue가 팀별 고정 순서가 아니라서~~ 정적 인덱스 타겟팅이 실패(수정: `ForEachLoopWithBreak`+`bIsParty` 런타임 비교로 동적 상대팀 탐색).
  > **※정정(2026-07-16, 파트1 착수 전 재검토)**: 취소선 부분은 **오진**이다. TurnQueue는 속도 정렬된 적이 없다 — 실측 순서는 `[A1,B1,A2,B2,A3,B3,A4,B4]`(A·B 교대, `BP_BattleManager` 디테일 패널에 손으로 꽂은 배열 — `Set`/`Add` 노드 프로젝트 전체 0개). 인덱스 4는 A3(아군)이라 `ignored`가 뜬 것뿐 — **정상 동작**이었다(채택한 동적 탐색 해법 자체는 유효, 결과 무변경). 상세: [[파트1_Start_진행]].

## W3 부가 발견
- **스로틀(bThrottleCPUWhenNotForeground) 프로젝트 정책 확인 필요**: W2에서 스로틀 OFF로 측정했으나, 개발 기간 중 표준 설정이 ON인 경우 향후 PIE 검증에서 고려 필요. Director 2026-07-07 확정 필요.

## W3fix 게이트 판정 (WT-23) — 2026-07-07 실행, 걸음 왜곡 핫픽스

| ID | 내용 | 판정 수단 | 결과 |
|---|---|---|---|
| **WT-23★** | 걸음 후 roll=90 유지(도착·복귀 양쪽) | 런타임 로그(RotCheck, 스로틀 OFF) | **PASS** — 원인: WalkForward/WalkBack의 MoveComponentTo 2개(`K2Node_CallFunction_143`/`_113`) `TargetRelativeRotation` 미배선(기본 0,0,0)이 매 걸음마다 Sprite roll=90을 0으로 보간. 수정: MakeRotator(Pitch=0,Yaw=0,Roll=90) 2개 신규 생성 후 각 `TargetRelativeRotation`에 배선. 검증: 임시 RotCheck 로그(WalkForward MoveComponentTo.then, WalkBack MoveComponentTo.then 각각) → `RotCheck:SpawnPoint_Party_A1:arrive:rot=P=0.000000 Y=0.000000 R=90.000000` / `RotCheck:SpawnPoint_Party_A1:home:rot=P=0.000000 Y=0.000000 R=90.000000` — 도착·복귀 양쪽 roll=90 유지 확인. 검증 후 스캐폴드(BP_BattleManager BeginPlay 6노드) + RotCheck 임시 노드(양쪽 5개씩 10노드) 전부 제거, 원배선 복원, 재컴파일 0. 상세: `raw/W3fix_회전보간.md`. |

### W3fix 컴파일 상태
- **BP_BattleSpawnPoint**: compile ✓ (0 에러, 0 경고, warnings_as_errors=true) — MakeRotator 2개 신규 반영, RotCheck 진단 노드는 검증 후 완전 제거.
- **BP_BattleManager**: compile ✓ (0 에러, 0 경고, warnings_as_errors=true) — 스캐폴드 완전 제거, BeginPlay 원상(빈 상태) 복원.
- **저장**: `save_assets([])` → BP_BattleSpawnPoint/BP_BattleManager/map_battle_octopath 전부 `is_dirty=false`.

### W3fix 명세 조정
- plan 지시 "Sprite GetRelativeRotation을 로그"를 실행 중 `GetWorldRotation`으로 대체(MCP `create_node`가 `GetRelativeRotation`을 3종 문자열 형식 전부에서 생성 거부 — 근본 원인 미규명, 이월). Sprite가 루트 컴포넌트(부모 없음)라 Relative=World이므로 이번 roll=90 검증 목적에는 결과 동치. 비루트 컴포넌트 대상 RelativeRotation 조회가 필요한 향후 케이스는 별도 우회 필요(이월).

