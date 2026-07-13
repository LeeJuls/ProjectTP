---
type: convention
project: projectTP
updated: 2026-07-12
---

# 🖥 UI·화면 제작 규약 (방향성2 단일 출처)

> projectTP **방향성2(Steam 드래프트 단판 PvP)**의 전체 화면·UI 제작 규약. 흩어진 확정 사항을 통합한 **이 주제의 단일 출처**다.
> 상위: [[projectTP_허브]] · 기반: [[기획_방향성]](§방향성2 씬·화면 구조·flow) · [[A0_UMG스파이크]](파이프라인 실측) · [[언리얼_MCP_실전노하우]] §19.
> 소관: system-ui-designer. 구현: gameplay-engineer. 수치: balance-designer.
#projectTP/UI규약

---

## 0. 이 문서가 대체하는 것 (위상)

| 대상 | 처리 |
|---|---|
| [[알파_개발계획]] **§2.6①** (UI 제작 가이드·클로드 디자인 파이프라인) | **폐기 → 이 문서 §B가 대체.** "3.전사: MCP가 UMG 위젯 구성"은 A0 실측으로 **틀린 것으로 확정**(위젯 배치 MCP 불가). |
| [[알파_개발계획]] **§2.6②** (화면 정의, `SCR_Lobby/SCR_Battle/SCR_Result` 목록) | **폐기 → 이 문서 §A가 대체.** SCR_* 3종은 방향성1 화면명. **단 Unity↔UE 매핑 원칙은 계승**(§A-1). |
| [[알파_개발계획]] §2.6②-b (CSV 기획 데이터 규약) | **[[데이터_서버_규약]] §4로 분리**(2026-07-13) — 데이터 스키마라 이 문서 범위 밖. |
| [[알파_개발계획]] §2.6③ (리소스 관리 규약) | **접두사 표는 [[네이밍_폴더_규약]]으로 이관**(2026-07-12, 단일 출처). 이 문서 §D·`알파_개발계획.md` §2.6③ 모두 그쪽을 가리키는 참조로 축소. 리소스 3계층 흐름 등 접두사 외 내용은 §2.6③에 유지. |

알파_개발계획.md §2.6①② 본문은 이 문서로 위임하는 짧은 참조로 교체됨(구버전 상세 삭제).

> **범위 주의**: 위 표는 **문서(설계) 레벨 위임**을 뜻한다. **물리 폴더**(`Resource/ui/`·`/Game/UI/`)는 **마이그레이션 실행 완료**(2026-07-11 — system-ui-designer·qa-critic 계획 검토 후 Director 실행, git 14줄 변경(D4+A10)+UE `Screens`→`Frontend/Battle/Common` 재조회 검증). `WBP_Probe`(A0① 테스트 애셋)는 이때 함께 삭제, `ST_UI`는 사전 물리 백업 후 무변조 확인.

> **경계**: 이 문서는 화면 **인벤토리·전환·제작 파이프라인·폴더·문자열·데이터 흐름**을 규정한다. `WBP_BattleHUD`의 **내부 전투 UI**(스킬 메뉴→타겟→확정, ATB, 데미지 부동숫자, 턴 순서)는 **별도 전투 HUD 명세**(system-ui, 예정 — [[알파_개발계획]] §4.5 system-ui #1)에서 다룬다. 밸런스 수치는 balance-designer, 비주얼 룩은 hd2d-art-director 소관.

---

## A. 화면 인벤토리 (방향성2 · 8개 위젯 / 레벨 2개)

> **7 vs 8 표기 차이**: [[기획_방향성]] flow 산문은 7종(Options 미포함, ①~⑨ 서술 흐름 요약). Options는 [[데이터_서버_규약]] §1(다국어 뼈대 — 언어 선택 UI 필요)의 확정 요구가 8번째로 편입한 것 — flow와 이 문서의 불일치가 아니라 두 근거 문서의 병합.

### A-1. 루트/오버레이 판정 기준 (규약)

방향성2는 **레벨 2개(map_frontend·map_battle)** 위에 **8개 WBP**를 얹는다. 레벨 전환은 무겁고 네트워크가 끊기므로 **화면 전환 = 위젯 교체가 원칙**([[기획_방향성]] §씬·화면 구조 계승).

**Unity↔UE 매핑 (§2.6②에서 계승):**

| Unity | UE | projectTP 규약 |
|---|---|---|
| Scene / `LoadScene` | Level(.umap) / `OpenLevel` | **3D 무대가 바뀔 때만**(로비무대↔전투무대) |
| Prefab(월드) | Blueprint 액터 | `BP_` |
| Prefab(UI) | UMG WidgetBlueprint | `WBP_` — 화면당 루트 1장 + 부품 WBP 분리 |
| `DontDestroyOnLoad`·static | **GameInstance** | 세션 데이터 운반(§F) |

**루트 vs 오버레이 판정 (2축):**

- **루트(Root)** = 한 시점에 그 레벨의 "주 화면". `CreateWidget`→`AddToViewport`. **한 레벨은 여러 루트를 순차 호스팅**하되 **동시에 1장만 활성**(루트 스왑 시 이전 루트 `RemoveFromParent`). ← §A-4에서 규약 신설.
- **오버레이(Overlay)** = 현재 루트 **위에 동시에 얹힘**(밑 루트 계속 보임). 취소/닫기 시 자기만 `RemoveFromParent`, 밑 루트 유지.
- **판정선**: 이전 화면을 **덮어 치우면 루트 스왑**, **위에 얹혀 공존하면 오버레이**.

### A-2. 8개 위젯 분류표

| # | WBP | 소속 레벨 | 루트/오버레이 | 역할 | 밑에 깔리는 것 |
|---|---|---|---|---|---|
| 1 | **WBP_Title** | map_frontend | **루트**(진입) | 로고+2D 일러스트+Press Start (로그인 없음) | — (3D 로드 은폐용 전면 아트) |
| 2 | **WBP_Lobby** | map_frontend | **루트** | 길드하우스 로비 루트, Start/옵션 | — |
| 3 | **WBP_Matching** | frontend·battle 공용 | **오버레이** | 매칭 스피너·취소 | Lobby(초기) 또는 전투레벨(재시작) |
| 4 | **WBP_Transition** | 레벨 걸침(공용) | **오버레이**(연출) | FF6풍 와이프 — 레벨 전환·로드 은폐 | 전환 시점의 아무 화면 |
| 5 | **WBP_Options** | map_frontend | **오버레이** | 언어 선택 등(로비에서 열림) | Lobby |
| 6 | **WBP_Draft** | map_battle | **루트** | 뽑기·리롤→픽→밴 (내부 3단계, §A-5) | — |
| 7 | **WBP_BattleHUD** | map_battle | **루트** | 4:4 턴제 전투(내부는 별도 명세) | — |
| 8 | **WBP_Result** | map_battle | **오버레이** | 승패·골드·재시작/로비 분기(부전승 포함) | BattleHUD |

> **§2.6① 오분류 정정**: 구 규약은 `WBP_Options`를 `components/` 하위에 임시 배치("필요시 조정")했다. Options는 재사용 **부품**이 아니라 자기 **spec을 가진 오버레이 화면**이므로 §C에서 `frontend/`로 재배치한다.

### A-3. 화면 전환 다이어그램

```
[엔진 부팅] ─ OpenLevel(map_frontend) ─ (WBP_Title 전면 아트가 3D 길드하우스 로드 은폐)
   │
┌── map_frontend ────────────────────────────────────────────────────────┐
│  ┌ WBP_Title (루트) ┐                                                   │
│  │  Press Start     │── 루트 스왑(Title 제거) ──▶ ┌ WBP_Lobby (루트) ┐  │
│  └──────────────────┘                            │                  │  │
│                            +WBP_Options(오버레이) ◀┤ 옵션 클릭         │  │
│                            (언어 등, 닫으면 복귀)   │                  │  │
│                                                   │ Start 클릭        │  │
│                              +WBP_Matching(오버레이)◀┤ 스피너/취소       │  │
│                                    │ 취소 → 오버레이만 제거(Lobby 유지) │  │
│                                    │ 매칭 확정                         │  │
│                              +WBP_Transition(연출) ─ FF6 와이프         │  │
│                                    │ 와이프가 덮은 채 OpenLevel(map_battle)│
└────────────────────────────────────┼───────────────────────────────────┘
                                      ▼
┌── map_battle ──────────────────────────────────────────────────────────┐
│  ┌ WBP_Draft (루트) ─ 내부 3단계 상태(§A-5) ──────────────────┐          │
│  │  [Roll] 6장 지급·리롤(5s,1회) → [Pick] 5픽(30s) → [Ban] 1밴(30s)        │
│  └────────────────────────────── 밴 완료 → 루트 스왑 ─────────┘          │
│                                      │                                  │
│                             ┌ WBP_BattleHUD (루트) ┐ 4:4 턴제           │
│                             └──────────┬───────────┘                    │
│                                        │ 승패 확정(또는 부전승)          │
│                             +WBP_Result(오버레이) ─ 승패·골드            │
│                                  ├ [재시작] → +Matching(전투레벨 대기)   │
│                                  │     ├ 매칭 성사 → Draft 재진입(무전환) │
│                                  │     └ 재매칭 실패 → [로비로]          │
│                                  └ [로비로] → +Transition → OpenLevel(map_frontend)
└────────────────────────────────────────────────────────────────────────┘
                                        │ (로비로 복귀 = WBP_Lobby 재활용)
                                        ▲───────────────────────────────────
```

### A-4. WBP_Title↔WBP_Lobby: **레벨 내 루트 스택 규약** (예외 해소)

**문제**: Title·Lobby 둘 다 루트급인데 같은 레벨(map_frontend)에 산다 — 구 §2.6②의 "레벨=화면" 암묵 가정과 충돌.
> **§D와는 무관**: §D "화면당 루트 1장"은 그대로 유지된다(Title도 Lobby도 각자 루트 1장). 새로 규약화하는 건 "**한 레벨에 화면이 여러 개 있을 수 있다**"는 것뿐 — 화면 정의 자체는 안 바뀐다.

**판단 → 규약 신설 (1:1 원칙을 스택으로 일반화)**:
- 구 "레벨당 루트 1장"은 알파 3화면용 **단순화였다.** 실제 규약은:
  > **한 레벨은 루트 위젯 스택을 호스팅한다 — 동시 활성은 1장, 나머지는 스왑 대상.**
- **map_frontend 루트 스택**: `WBP_Title`(초기) → (Press Start) → `WBP_Lobby`. **레벨 로드 없음**(같은 map_frontend). Title은 전면 불투명 2D 아트라 뒤의 3D 길드하우스가 스왑 전까지 안 보임 → **길드하우스 로드 시간을 Title이 공짜로 은폐.**
- **map_battle 루트 스택**: `WBP_Draft` → (밴 완료) → `WBP_BattleHUD`.
- **적용 요건**: 루트 스왑은 (a) 이전 루트 `RemoveFromParent` (b) 새 루트 `AddToViewport` (c) 3D 무대 동일. 무대가 바뀌면 그건 스왑이 아니라 `OpenLevel`(레벨 전환)이다.

**대안(기각)**: Title 전용 부트스트랩 레벨 분리 — 부팅 시 레벨 1회 더 로드하는 비용만 추가되고 이점 없음. **같은 레벨 루트 스왑 채택.**

### A-5. WBP_Draft 3단계: **단일 루트 + 내부 상태 + 재사용 부품** (설계 판단)

**판단**: WBP_Draft는 **위젯 하나(단일 루트)**이고, 뽑기·리롤→픽→밴은 **그 안의 내부 상태 전환**이다. 별도 루트 위젯 3개가 아니다.

**근거**: ①세 단계 모두 map_battle·레벨 전환 없음(연속 UX) ②카드 그리드·타이머가 단계 공유(중복 방지) ③드래프트 결과가 하나의 응집된 GameInstance 흐름.

**구성**: `WBP_Draft`(루트) = 공유 프레임(배경·타이머 바 슬롯·카드 그리드 영역) + `WidgetSwitcher`(또는 상태 enum 기반 가시성)로 단계별 컨트롤 교체. 단계별 부품은 **재사용 컴포넌트 조합**(§E): `WBP_TimerBar`·`WBP_CharacterCard`.

**내부 상태 표** (gameplay-engineer용):

| 상태 | 진입 | 타이머 | 표시 카드 | 주 입력 | 이탈 | GameInstance 기록 |
|---|---|---|---|---|---|---|
| **Roll** | Draft 루트 진입(매칭 직후) — **★드래프트 세션 필드 전체 리셋**(아래 참조) | 5초 | 내 6장(**풀랜덤 — B안 오너 확정 2026-07-13**) | 리롤(1회·골드) | 5초 경과 또는 리롤 확정 | `RolledUnitIds`, `RerollUsed`, `Gold` |
| **Pick** | Roll 종료 | 30초 | 내 6장(선택 가능) | 5장 선택 | 5픽 완료 or 30초(자동 랜덤) | `PickedUnitIds`, `OpponentPickedUnitIds`(AI/서버) |
| **Ban** | **양측 Pick 잠금 후** | 30초 | 상대 5장 | 1장 밴 | 1밴 완료 or 30초(자동 랜덤) → **내 밴 제출 후 상대 밴 대기**(§I E9) → 양쪽 확정 시 즉시 전환 | `BannedUnitId`, `OpponentBannedUnitId`(AI/서버), `FinalPartyUnitIds` |

> **동기 지점**: Ban은 상대의 확정 픽 5장이 필요 → Pick과 Ban 사이에 "상대 픽 대기" 구간(§I E2) + Ban 내부에서도 "내 밴 제출 후 상대 밴 대기" 구간(§I E9) 발생 가능. 자동처리(30초 초과=랜덤 가정)의 **규칙 값**은 gameplay/balance 소관, UI는 "자동 처리됨" 표시만 규정.
>
> **★세션 필드 리셋(재시작 루프 필수)**: 결과→재시작(레벨 무전환, §A-3)으로 Draft에 재진입할 때 **`RolledUnitIds`·`RerollUsed`·`PickedUnitIds`·`OpponentPickedUnitIds`·`BannedUnitId`·`OpponentBannedUnitId`·`FinalPartyUnitIds`·`MatchInfo`(신규 상대) 전량 리셋**(Roll 진입 시점, 위 표 참조) — 리셋 없으면 2판째 `RerollUsed=true`가 남아 리롤 영구 비활성. **`Gold`·`CurrentLanguage`(SaveGame)는 리셋 대상 아님**(누적 유지).

---

## B. 제작 파이프라인 (A0 실측 반영 · 5단계)

> **핵심 정정**: 구 §2.6①의 "3.전사: MCP가 UMG 위젯 구성"은 **틀렸다.** A0 실측([[A0_UMG스파이크]] §7-5·[[언리얼_MCP_실전노하우]] §19): WBP **껍데기 생성/컴파일/저장은 MCP 가능**하나, **`WidgetTree`/`RootWidget`이 `ObjectTools` read/write 전부 차단** → **위젯 배치(자식 Button/TextBlock 트리)는 MCP 불가.**

### B-1. 5단계 — 누가 무엇을 하는가

| 단계 | 담당 | 도구/방법 | MCP 실증 | 오너 부담 |
|---|---|---|---|---|
| **1. 디자인** | **Claude** | HD-2D 톤 HTML → DesignSync → claude.ai/design | (MCP 무관) | 브라우저 리뷰·승인만 |
| **2. 스펙화** | **Claude** | 승인본 → `spec.md`(레이아웃 토큰표: 위치·크기·색·폰트·문자열키) | (MCP 무관) | — |
| **3. 골격 생성** | **Claude (MCP)** | `BlueprintTools.create(asset_type=/Script/UMG.UserWidget)` + `compile_blueprint` + `save_assets` | ✅ **확정**(모달 없음·진짜 WidgetBlueprint) | — |
| **4. 위젯 배치** | **오너 (수동)** | UMG Designer에서 `spec.md` 보고 Button/TextBlock/이미지/CanvasPanel 배치·앵커·사이즈 | ❌ **MCP 불가 확정** | **애셋당 수 분** ← 유일한 오너 노동 |
| **5. 배선** | **Claude (MCP)** | 문자열 바인딩(CSV 키)·이벤트 그래프(OnClicked 등)·데이터 바인딩 | ⚠ **부분 미검증**(B-3) | (폴백 시 클릭 소수) |

### B-2. 담당 분리 원칙 (오너가 헷갈리지 않게)

```
Claude:  ①디자인 ②스펙 ③골격생성 ─────────[오너: ④배치]─────────  ⑤배선  Claude
         └────── 자동(반복 노동) ──────┘  └ 수동(창의·수 분) ┘  └ 자동(로직) ┘
```
- **오너의 유일한 노동 = 4번(배치)**, 애셋당 수 분. 나머지 1·2·3·5는 전부 Claude.
- **배치 효율화(권고)**: Claude가 3번에서 **8개 화면+컴포넌트 WBP 껍데기를 일괄 생성** → 오너가 4번을 **한 번에 몰아서** 배치 → Claude가 5번을 일괄 배선. 단계당 컨텍스트 전환 최소화.
- **순서 강제(계승)**: **`spec.md` 없이 배치하지 않는다.** 승인본과 스펙이 어긋나면 스펙 기준.

### B-3. 5단계(배선) MCP 경계 — 확정/미검증 (정직 고지)

A0는 위젯을 심을 방법 자체가 없어 **배선을 실측하지 못했다.** 경계를 분리한다:

| 배선 종류 | MCP 상태 | 폴백 |
|---|---|---|
| **EventGraph 순수 로직** (핸들러 함수, `GetLocalizedString(Key)` 호출, GameInstance 읽기/쓰기 노드) — 위젯 참조 없음 | ⚠ **미검증**(EventGraph 존재는 `list_graphs`로 확인됐으나 로직 노드 삽입 자체는 A0에서 미실증 — 일반 BP에선 이미 다수 실증된 패턴이라 유력하지만 WBP 대상 실증은 아직 없음) | — |
| **오너 배치 위젯 참조·바인딩** (TextBlock.Text 바인딩, Button `OnClicked` 바인딩) | ⚠ **미검증** — `add_component_bound_event`가 위젯 델리게이트에 통하는지 A0에서 테스트 불가(버튼이 없었음), WidgetTree 접근 벽에 걸릴 수 있음 | 오너가 4번에서 (a)위젯 IsVariable 노출(체크 1회) (b)빈 `OnClicked` 바인딩 추가(클릭 1회) → Claude가 핸들러 그래프 채움 |

> **후속 실증(예약)**: 다음 UMG 제작 착수 시, 오너가 첫 Button 배치 후 **`add_component_bound_event` 1회 프로브** — 통하면 배선 전량 MCP, 안 통하면 위 폴백(연결점=오너, 로직=Claude). §J-2에 등록.

---

## C. 폴더 구조 (방향성2) + 마이그레이션

### C-1. `Resource/ui/` (git 추적 = 단일 출처)

**설계 판단**: 화면을 **레벨별로 그룹핑**(frontend/battle) — 실전 탐색이 쉽다("전투 손대면 battle/ 하나만"). **오버레이도 자기 화면 spec을 가지므로** components/가 아니라 **소속 레벨 폴더**에 둔다. **레벨 걸치는 흐름 오버레이(Transition·Matching)**만 `common/`. `components/`는 **원자 재사용 부품** 전용.

```
Resource/ui/
├─ frontend/                     map_frontend 소속 화면군
│  ├─ WBP_Title/    { design_v<N>.html · approved.html · spec.md }
│  ├─ WBP_Lobby/    { … }
│  └─ WBP_Options/  { … }        ← 구 components/WBP_Options 에서 이전(오버레이라 여기가 맞음)
├─ battle/                       map_battle 소속 화면군
│  ├─ WBP_Draft/    { … }        ← 내부 3단계, 하위 부품은 components/
│  ├─ WBP_BattleHUD/{ … }
│  └─ WBP_Result/  { … }
├─ common/                       레벨 걸치는 흐름 오버레이
│  ├─ WBP_Transition/{ … }       레벨 전환 공용 커튼(양방향)
│  └─ WBP_Matching/ { … }        로비 대기 + 전투레벨 재시작 대기 공용
├─ components/                   원자 재사용 부품(레벨 무관) — §E
│  ├─ WBP_CharacterCard/
│  ├─ WBP_TimerBar/
│  ├─ WBP_PopupFrame/
│  └─ …
└─ assets/                       추출 PNG(9-slice·아이콘) — UE 임포트 원본
```
- 각 화면 폴더 = `design_v<N>.html`(버전 보존) + `approved.html`(승인 스냅샷) + `spec.md`(전사 기준).
- **골격은 skeleton-first(정정 2026-07-11)**: 8개 화면 폴더 전부 마이그레이션 시점에 `.gitkeep`으로 이미 선배치(이 프로젝트 기존 관행 — 방향성1 때도 동일 패턴). 화면 디자인 착수 시 `.gitkeep` 삭제하고 `design_v1.html`부터 채운다.

### C-2. `/Game/UI/` (UE Content · 미러)

```
/Game/UI/
├─ Frontend/    WBP_Title · WBP_Lobby · WBP_Options
├─ Battle/      WBP_Draft · WBP_BattleHUD · WBP_Result
├─ Common/      WBP_Transition · WBP_Matching
├─ Components/  WBP_CharacterCard · WBP_TimerBar · WBP_PopupFrame · …  (구 WBP_Probe = A0 테스트 애셋, 마이그레이션 시 삭제 완료 — referencer 0 확인 후)
└─ Textures/    T_UI_*
```
- 명명: `WBP_<이름>` / 텍스처 `T_UI_<이름>`.
- 기존 `/Game/UI/Screens`(빈 폴더) → `Frontend/Battle/Common`으로 대체(폐기).

### C-3. 마이그레이션 — ★실행 완료 (2026-07-11)

system-ui-designer(원저자 검토)·qa-critic(안전성 검토, ST_UI 무백업 리스크 지적) 피드백 반영 후 Director 실행. 절차·근거는 `C:\Users\user\.claude\plans\humble-purring-glacier.md`(세션 plan 파일)에 보존.

| 현재(구) | 조치 | 결과 |
|---|---|---|
| `Resource/ui/screens/{SCR_Lobby,SCR_Battle,SCR_Result}/` | 삭제 | ✅ 완료 |
| `Resource/ui/components/WBP_Options/` | 삭제 → `frontend/WBP_Options/` 재생성 | ✅ 완료 |
| `Resource/ui/components/`, `assets/`(기존분) | 유지 | ✅ 무변경 확인 |
| 신규 8개 화면 폴더(`.gitkeep` skeleton-first) | 생성 | ✅ 완료 |
| §E 컴포넌트 우선순위 "높음" 2종(`WBP_TimerBar`·`WBP_CharacterCard`) | 신규 선배치(Director 결정 — system-ui 권고 채택) | ✅ 완료 |
| `/Game/UI/Screens`(UE, 빈 폴더) | 삭제 → `Frontend`·`Battle`·`Common` 생성(`Textures`는 기존 존재분 재사용) | ✅ 완료 |
| `/Game/UI/Components/WBP_Probe`(A0 테스트 애셋) | referencer 0 확인 후 삭제 | ✅ 완료 |
| `/Game/UI/ST_UI` | **무변조**(사전 물리 백업 후 미대상 확인) | ✅ 무사 |

**검증**: git `Resource/ui/` 범위 `--untracked-files=all` diff = 정확히 14줄(삭제4+추가10, 사전 열거한 기대치와 100% 일치) / UE `list_folders` 재조회 = `Battle·Common·Components·Frontend·Textures` 5개 정확히 일치 / `find_assets` = `ST_UI` 1건만 잔존.
| `/Game/UI/Screens`(UE, 빈 폴더) | 폐기 → `Frontend/Battle/Common` 생성 |

> **실행 금지 주의**: 이 문서는 **설계·지시까지**. 실제 폴더 생성/이름변경은 **qa-critic 검증 후 Director가 별도 게이트에서** 진행(task 규칙).

---

## D. 명명 규칙

전 카테고리 명명·폴더 규약의 **단일 출처는 [[네이밍_폴더_규약]]으로 이관**(2026-07-12) — 접두사 완전판(struct/enum `F_`/`E_` 포함)·명명 순서 원칙·기존 이탈 레지스트리·위젯 트리 요소 명명 전부 그 문서 참조.

화면 제작에 특히 관련된 것만 요약:

| 종류 | 접두사 | 예 | 비고 |
|---|---|---|---|
| 위젯(루트·오버레이·부품 전부) | `WBP_` | `WBP_Title`·`WBP_Draft`·`WBP_CharacterCard` | 역할 구분은 **폴더**가 담당(별도 서브접두사 없음) |
| UI 텍스처 | `T_UI_` | `T_UI_Frame_9slice`·`T_UI_Icon_Gold` | 픽셀퍼펙트 3종 세팅 |

- 루트/오버레이/컴포넌트가 전부 `WBP_`인 이유: 셋 다 물리적으로 WidgetBlueprint. **역할은 위치(frontend/battle/common/components)로 읽는다.** ([[알파_개발계획]] §2.6② "화면당 루트 1장 + 부품 WBP 분리" 계승).

---

## E. 재사용 컴포넌트 목록 (`components/`에 미리 준비 권고)

| 컴포넌트 | 역할 | 사용처 | 우선순위 | 소관 |
|---|---|---|---|---|
| **WBP_TimerBar** | 카운트다운 바 | Draft(Roll 5s·Pick 30s·Ban 30s) | **높음** | 이 문서 |
| **WBP_CharacterCard** | 캐릭터 카드(초상·이름키·포지션·**등급**·스킬3슬롯) — 등급 필드는 등급축 확정(2026-07-13)의 파급([[알파_개발계획]] §4.5 balance#4 해소 게이트: 카드가 role+grade 노출) | Draft(Roll/Pick/Ban 전 단계)·Result(최종4 변형) | **높음** | 이 문서 |
| **WBP_PopupFrame** | 9-slice 팝업 프레임(제목·본문·버튼 슬롯) | Options·Result·Matching 박스·확인 다이얼로그 | 중 | 이 문서 |
| **WBP_GoldCounter** | 골드 표시(아이콘+수치) | Lobby·Draft(리롤 비용)·Result(보상) | 중 | 이 문서 |
| **WBP_Button_Primary/Secondary** | 스타일 버튼 | 전역 | 낮음(공용 스타일로 대체 가능) | 이 문서 |
| WBP_DamageNumber | 부동 데미지/힐 숫자 | BattleHUD | (후보) | **전투 HUD 명세** |
| WBP_UnitFrame | 전투 유닛 HP/상태 프레임 | BattleHUD | (후보) | **전투 HUD 명세** |

> **미리 만들면 이득**: TimerBar·CharacterCard는 Draft 3단계가 공유하므로 **Draft 착수 전 우선 제작**. Draft를 이 둘의 조합으로 세우면 배치 노동(4단계)이 준다.

---

## F. GameInstance 데이터 흐름

[[기획_방향성]]: "GameInstance 운반 = 매칭 정보·드래프트 결과·승패·골드. SaveGame = 누적 골드." 각 화면이 읽고/쓰는 필드:

**GameInstance 필드 스키마** (gameplay-engineer용 — 타입은 제안, 확정은 구현 시):

| 필드 | 타입 | 의미 | 영속 |
|---|---|---|---|
| `MatchInfo` | struct{ OpponentId, SessionId, Seed, IsBot:bool } | 매칭 상대/세션 | 세션 |
| `RolledUnitIds` | int[6] | 지급 6장 | 세션 |
| `RerollUsed` | bool | 리롤 1회 소진 | 세션 |
| `PickedUnitIds` | int[5] | 내 픽 5장 | 세션 |
| `OpponentPickedUnitIds` | int[5] | 상대 픽(밴 대상) — 알파=AI 봇이 즉시 결정, PvP=서버 확정값 미러 | 세션 |
| `BannedUnitId` | int | 내가 상대 5장 중 건 밴 | 세션 |
| `OpponentBannedUnitId` | int | 상대(알파=AI 봇, PvP=서버)가 **내** 5장 중 건 밴 — `FinalPartyUnitIds` 산출에 필수 | 세션 |
| `FinalPartyUnitIds` | int[4] | `PickedUnitIds − {OpponentBannedUnitId}` (5장에서 상대가 건 1장 제외) | 세션 |
| `BattleResult` | enum{ Win, Lose, Walkover } | 승패(부전승 포함) | 세션 |
| `Gold` | int | 누적 골드 | **SaveGame** |
| `CurrentLanguage` | enum/string | 현재 언어([[데이터_서버_규약]] §1) | **SaveGame** |

**화면별 read/write** (오버레이 표시는 밑 루트와 합산):

| 화면 | 읽기(read) | 쓰기(write) |
|---|---|---|
| WBP_Title | CurrentLanguage | — |
| WBP_Lobby | Gold, CurrentLanguage | — |
| WBP_Options | CurrentLanguage | CurrentLanguage (+SaveGame) |
| WBP_Matching | — | MatchInfo(매칭 성사 시) |
| WBP_Transition | — | — (순수 연출) |
| WBP_Draft · Roll | MatchInfo, Gold, RerollUsed | RolledUnitIds, RerollUsed, Gold(리롤 차감) |
| WBP_Draft · Pick | RolledUnitIds | PickedUnitIds, **OpponentPickedUnitIds**(AI/서버 — 내 픽 확정과 동시에 상대 픽도 확정) |
| WBP_Draft · Ban | PickedUnitIds, OpponentPickedUnitIds | BannedUnitId, **OpponentBannedUnitId**(AI/서버 — 내 밴 제출과 동시/직후 상대 밴도 확정), FinalPartyUnitIds(양쪽 밴 확정 후 산출) |
| WBP_BattleHUD | FinalPartyUnitIds, MatchInfo | BattleResult |
| WBP_Result | BattleResult, Gold | Gold(+=보상, +SaveGame) |

> **PvP 서버 권위 주석**: 실 PvP에서 Rolled/Picked/Banned/Result는 **서버가 확정**하고 GameInstance는 그 확정값의 클라 미러다. 클라 UI는 GameInstance를 읽는다(권위·핫픽스 상세 = [[데이터_서버_규약]] §3(§3-B 서버권위·§3-C 원격배송), 재설계 아님). 알파(서버 없음)는 GameInstance가 유일 소스.

---

## G. 문자열 규칙 + 스타터 키 목록

- **규칙(계승·재확인)**: UI 표시 문자열 **하드코딩 금지.** 전부 `strings.csv`(`Key,ko,ja,en`) 키 → 런타임 `GetLocalizedString(Key)` (빈칸 폴백 ko). 언어 변경 시 `OnLanguageChanged` 브로드캐스트로 열린 위젯 재바인딩([[데이터_서버_규약]] §1).
- **키 명명**: `UI_<SCREEN>_<ELEMENT>` UPPER_SNAKE. Draft 하위단계는 `UI_DRAFT_<STAGE>_<ELEMENT>`.

**스타터 키(화면별 — 디자인/스펙 착수 시 strings.csv에 등록):**

| 화면 | 키 |
|---|---|
| Title | `UI_TITLE_PRESS_START`·`UI_TITLE_VERSION` |
| Lobby | `UI_LOBBY_START`·`UI_LOBBY_OPTIONS`·`UI_LOBBY_QUIT`·`UI_LOBBY_GOLD` |
| Matching | `UI_MATCHING_SEARCHING`·`UI_MATCHING_CANCEL`·`UI_MATCHING_FOUND`·`UI_MATCHING_FAILED` |
| Transition | `UI_TRANSITION_LOADING`(선택 — 대개 문자열 없음) |
| Options | `UI_OPTIONS_TITLE`·`UI_OPTIONS_LANGUAGE`·`UI_OPTIONS_CLOSE`·`UI_OPTIONS_LANG_KO`·`UI_OPTIONS_LANG_JA`·`UI_OPTIONS_LANG_EN` |
| Draft/Roll | `UI_DRAFT_ROLL_TITLE`·`UI_DRAFT_REROLL`·`UI_DRAFT_REROLL_COST`·`UI_DRAFT_ROLL_TIMER` |
| Draft/Pick | `UI_DRAFT_PICK_TITLE`·`UI_DRAFT_PICK_CONFIRM`·`UI_DRAFT_PICK_COUNT`("{0}/5") |
| Draft/Ban | `UI_DRAFT_BAN_TITLE`·`UI_DRAFT_BAN_CONFIRM`·`UI_DRAFT_BAN_WAIT`(상대 대기) |
| BattleHUD | (상세 = 전투 HUD 명세) 예시: `UI_BATTLE_TURN`·`UI_BATTLE_SKILL`·`UI_BATTLE_ATTACK`·`UI_BATTLE_TARGET` — ★`UI_BATTLEHUD_`가 아닌 `UI_BATTLE_` 축약(의도적 — 정식 목록은 전투 HUD 명세에서 표준화) |
| Result | `UI_RESULT_WIN`·`UI_RESULT_LOSE`·`UI_RESULT_WALKOVER`(부전승)·`UI_RESULT_GOLD_REWARD`·`UI_RESULT_RESTART`·`UI_RESULT_TO_LOBBY` |

---

## H. 입력·플랫폼 원칙 (터치 친화 재검토)

방향성2 = **Steam(마우스·키보드) 확정.** 구 §2.6①의 "터치 친화(최소 터치 타겟·해상도 앵커링 — 베타 플랫폼 대비)"를 **완화하되 폐기하지 않는다.**

| 처리 | 항목 | 이유 |
|---|---|---|
| **버림** | 터치 우선 상호작용 모델·모바일 밀도 레이아웃·"44px 하드룰" | Steam 1차 = 포인터/키보드 |
| **유지(최소 권고)** | 해상도 앵커링·세이프에어리어 | Steam 다양한 해상도 + 후일 콘솔 포팅 대비 |
| **유지(최소 권고)** | "과도하게 작은 클릭 타겟 금지" 가이드(하드룰 아님) | **Steam Deck 터치스크린**(큰 세그먼트) + 접근성 |
| **추가** | 게임패드 포커스 내비게이션(D-pad/스틱 포커스 이동, A확정) | **Steam Deck Verified**·컨트롤러 기대. 구현 시점은 §J-2(오너) |

> 요지: 랜덤은 "제시"에, 공정/접근성은 "레이아웃"에. Steam Deck이 터치+게임패드를 둘 다 요구하므로 **최소 권고는 남기는 게 안전**하다. 알파 = 마우스 우선, 게임패드 본격 대응 = 시점 미정(§J-2).

---

## I. UI 엣지케이스 (화면 흐름 — 설계·구현 시 반영)

> 방어적 설계: system-ui가 미리 명시(qa-critic이 후속 검증). **화면/입력 흐름 한정**(전투 규칙 엣지케이스는 별도 전투 명세).

| # | 케이스 | UI 처리 요구 |
|---|---|---|
| E1 | **취소·매칭 성사 경합** (취소 누른 프레임에 매칭 확정) | 확정 우선 or 취소 우선을 명시(권고: 서버 확정 우선, 취소 무시+안내). Matching 오버레이가 두 이벤트 순서 방어 |
| E2 | **Pick→Ban 사이 상대 대기** (한쪽이 먼저 5픽 완료) | `UI_DRAFT_BAN_WAIT` 대기 표시. 양측 잠금 전까지 Ban 진입 금지 |
| E3 | **픽/밴 30초 초과 자동처리** | UI는 "자동 처리됨" 명시 표시(규칙값=랜덤 가정은 gameplay/balance) |
| E4 | **리롤 5초 창 vs 픽 진입** | 5초 카운트 종료 = 리롤 확정+Pick 진입 원자적. 창 닫힘 후 리롤 버튼 비활성 |
| E5 | **Transition 도중 로드 실패/연결 끊김** | 와이프가 무한 지속 금지 — 타임아웃 시 로비 복귀+에러(`UI_MATCHING_FAILED` 계열) |
| E6 | **부전승(상대 이탈)** | Result가 `Walkover` 경로 표시(`UI_RESULT_WALKOVER`). 골드 보상 규칙은 balance |
| E7 | **재시작 후 재매칭 실패** | 전투레벨 무한 대기 금지 → 로비 이동(flow 확정) |
| E8 | **양측 동시 픽 정보 누출 방지** | 진행 중 상대 픽 미노출 — Ban 단계에서만 상대 확정 5장 공개 |
| E9 | **밴 제출 후 상대 밴 대기** (내가 먼저 1장 밴 확정, 상대 미확정) | 카드그리드·밴 버튼 잠금 + 대기 인디케이터(`UI_DRAFT_BAN_WAIT` 재사용). 상대 확정(수동 or 30초 자동처리) 즉시 `FinalPartyUnitIds` 산출+루트 스왑(BattleHUD) — E2(Pick→Ban 진입 전 대기)와 별개 구간 |

---

## J. 오너 결정·입력 필요 (3건)

> 임의로 얼버무리지 않고 모음. 나머지(화면 8분류·루트스택·Draft 내부상태·폴더 그룹핑·터치 완화)는 이 문서에서 **결정 완료.**

**J-1. 전투 중 옵션/일시정지 오버레이가 필요한가?**
flow에 전투 중 옵션이 없다. 경쟁 PvP + 30초 타이머라 **일시정지 불가**일 수 있다. 결정에 따라: (a) 불필요 → Options는 `frontend/` 유지 (b) 필요 → Options를 `common/`으로 옮기고 전투용 pause 오버레이 추가. **→ 오너: 전투 중 설정 접근 허용 여부?**

**J-2. Steam Deck/게임패드 지원 시점 (스코프).**
`add_component_bound_event` 프로브(§B-3)와 별개로, 게임패드 포커스 내비 요구 강도가 최소 타겟 크기·포커스 설계를 좌우한다. **→ 오너: 알파부터 게임패드 최소 대응할지, 마우스 전용으로 가고 게임패드는 베타로 미룰지?**

**J-3. 배선(5단계) 미검증 실증 — 오너 에디터 필요.**
다음 UMG 제작 착수 시, 오너가 첫 Button 배치 후 `add_component_bound_event` 통하는지 **1회 프로브** 필요(§B-3). 결정이라기보다 **예약된 오너 액션** — 통하면 배선 전량 MCP, 안 통하면 폴백(연결점=오너 클릭, 로직=Claude). **→ 오너: 첫 실화면 착수 시 이 프로브 1회 동참.**

---

## 관련 문서
[[기획_방향성]] · [[알파_개발계획]] · [[A0_UMG스파이크]] · [[언리얼_MCP_실전노하우]] · [[projectTP_허브]]
