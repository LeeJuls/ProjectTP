---
type: tc
feature: 턴제전투MVP
status: E3 자가검증 완료 (verifier 실증 대기)
updated: 2026-07-07
---

# ✅ 턴제전투MVP TC (qa-critic 산출, 35종)

> plan: [[plan]] · 청사진: [[청사진]]
> 표기: `[TC-ID/우선순위] 조건 → 기대결과 | 판정수단`. **판정수단 열이 생명**(QA-H6) — 런타임 상태는 PrintString+GetLogEntries 또는 오너 육안만. get_properties는 정적 프로퍼티에만 유효.
#projectTP/턴제전투MVP

## 공통 전제
- [전제-1] 에디터+MCP 연결
- [전제-2] 런타임 상태값은 get_properties 불가(에디터 스냅샷만) → PrintString+GetLogEntries 또는 오너 육안
- [전제-3] 스크린샷 생략(오너 라이브 확인 대체)
- [전제-4] 결정적 트리거=임시 스캐폴드 심고 제거
- [전제-5] village 회귀는 각 게이트 맨 마지막

## E1 (유닛 확장 — TC-01~10)
| TC | 우선순위 | 조건 → 기대결과 | 판정수단 |
|---|---|---|---|
| TC-01 | High | 스캐폴드로 TakeHit 단발 → HURT 진입 후 0.45s 뒤 idle(0/6/0) 복귀 | PrintString+오너 육안 |
| TC-02 | High | TakeHit Duration=0.45 단일값 | get_node_infos(정적) |
| TC-03 | Crit | 지연 TakeHit 발화 직전 IsValid 가드 존재 | get_connected_subgraph(정적) |
| TC-04 | Crit | 같은 유닛 PlayAttack 직후 0.1s TakeHit 강제 → clobber 없이 마지막 것 우선·크래시 없음 | PrintString 타임스탬프+육안 |
| TC-05 | Med | 마커 ON/OFF 토글, Party 청록·Enemy 주황 | 오너 육안 |
| TC-06 | Med | EmissiveBoost ON/OFF 정적 발광 | 육안+get_properties(소스 스칼라, 정적) |
| TC-07 | High | ClickBox 클릭 로그 발화, 아군/자신 클릭 무피드백(bIsParty 분기 로그) | PrintString |
| TC-08 | Low | TakeHit 이상 RowIndex 방어 | get_node_infos |
| TC-09 | Crit | village 회귀: 유닛 BP 확장이 정면대치 불변(dirty=false) | 육안+is_dirty |
| TC-10 | High | 배치도구 회귀: FaceLeft 토글 양방향 후 원값 복원 dirty=false | get_properties(정적)+is_dirty |

## E2 (Manager 상태머신+큐+버튼 재배선 — TC-11~19)
| TC | 우선순위 | 조건 → 기대결과 | 판정수단 |
|---|---|---|---|
| TC-11 | High | Init: 큐 [A1,B1,A2,B2,A3,B3,A4,B4] 순서 로그+전 효과 리셋 | PrintString |
| TC-12 | High | 유닛 self-register 8/8 완료 후 Init 진행(BeginPlay 순서 비의존) | PrintString |
| TC-13 | High | 1턴 정상 흐름 각 상태진입+타임스탬프(임팩트 t≈0.25, TurnEnd t≈0.75, 텀 0.35) | PrintString+육안 |
| TC-14 | Crit | 최속 유저 8턴 연속 — 어느 유닛도 revert/attack 겹침 없음·크래시 없음 | PrintString 타임스탬프+육안 |
| TC-15 | High | 마커 항상 ≤1개(2개 상태 절대 없음) | 육안+PrintString 카운트 |
| TC-16 | High | TurnEnd에서 마커 OFF가 i 증가보다 먼저(노드 순서) | get_connected_subgraph(정적)+육안 |
| TC-17 | Crit | modulo=compact 후 실길이(상수 8 금지), null 1기 강제 시 정상 순환 | PrintString |
| TC-18 | High | null 슬롯 skip, 무한루프/크래시 없음 | PrintString |
| TC-19 | High | 공격→피격 싱크(t=0.25), 타겟이 상대팀 | 육안+PrintString |

## E3 (폴리시·엣지+풀 회귀 — TC-20~35)
| TC | 우선순위 | 조건 → 기대결과 | 판정수단 | 상태 |
|---|---|---|---|---|
| TC-20 | Crit | 타겟 초고속 연타 2회 → Executing 1회만·이중발화 없음 | PrintString 카운트+육안 | **PASS**(gameplay-engineer 자가검증) |
| TC-21 | Crit | 클릭핸들러 bInputLocked=true가 상태전이보다 먼저(노드 순서) | get_connected_subgraph(정적) | **PASS** |
| TC-22 | Med | 버튼 연타=AwaitCommand↔AwaitTarget 왕복만 | PrintString+육안 | **PASS**(4연타로 검증) |
| TC-23 | High | Executing 중 전 클릭 무시 | PrintString+육안 | **PASS** |
| TC-24 | Med | 취소 경로 발광 전체 OFF 잔류 없음 | 육안+정적 교차 | **PASS**(정적) |
| TC-25 | Med | 숨김 버튼 콜리전 동반 OFF 이행 | PrintString(숨김상태 OnClicked 발화 여부) | **PASS**(정적) |
| TC-26 | High | 1바퀴+ 순환 후 AwaitCommand 도달·잠금 영구 ON 없음 | PrintString | **PASS**(TC-14 8턴 완주로 간접 검증) |
| TC-27 | High | 8턴 완주+취소 5회 후 잔여 발광·마커 0 | 육안+PrintString | 이월(F단계 오너 육안 권장) |
| TC-28 | High | 모드 구분 2중 신호(라벨+발광) 오인 없음 | 오너 육안 | 이월(F단계) |
| TC-29 | Med·이월 | 10분+ 순환 float 안정성 | 오너 육안 관찰 | 이월(F단계) |
| TC-30 | Low | Battle.Attack+Battle.Cancel 키 존재, 하드코딩 없음 | 정적 조회 | **PASS** |
| TC-31 | High | PIE 재시작 Init 능동 리셋, 잔류 없음 | 육안+PrintString | **PASS**(4회 재시작 확인) |
| TC-32 | High | 공격버튼데모 기능이 Manager 통합 후 동작 or 명시적 대체 | 육안+PrintString | **PASS**(정적) |
| TC-33 | Crit | village 최종 회귀 완전 불변 | 육안+is_dirty | **PASS** |
| TC-34 | High | 배치_1 회귀: 8기 좌표·FaceLeft 불일치 없음 | get_actor_transform+get_properties(정적) | **PASS** |
| TC-35 | Low | 버튼·유닛 ClickBox 화면 비중첩/채널 분리 | 육안+정적 | 이월(F단계 육안 권장) |

## 진행 상태 표기 규칙
각 게이트(E1/E2/E3) 실행 시 verifier가 TC별 PASS/FAIL/이월을 [[진행로그]]에 append하고, 이 표의 상태는 게이트 통과 후 일괄 갱신한다.
