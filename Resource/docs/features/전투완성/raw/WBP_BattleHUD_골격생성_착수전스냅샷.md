---
type: log
---

# WBP_BattleHUD 골격 생성 착수 전 스냅샷 (롤백 지점)

gameplay-engineer가 `Resource/ui/battle/WBP_BattleHUD/spec.md`(WBP_BattleHUD spec) §0/§B 파이프라인 3단계(골격 생성) 착수 전 기록. `WBP_HpGauge`(F3b 임시)를 `WBP_UnitFrame`으로 대체하기 전 상태를 보존한다.

## 1. `WBP_HpGauge` (`/Game/UI/Battle/WBP_HpGauge`) 구조

- Parent Class: `/Script/UMG.UserWidget`(순정, 커스텀 C++ 부모 없음)
- Member 변수: `HpText` 1개만 존재
- 함수: `SetHpText`(커스텀, 구현됨) — 나머지는 UserWidget 기본 오버라이더블 이벤트(미구현)
- 그래프: `SetHpText`(함수), `EventGraph`
- Referencer: `/Game/Blueprints/BP_BattleSpawnPoint` 1건만(단일 소비자)

## 2. `BP_BattleSpawnPoint` WidgetComponent(`HpGaugeWidget`) — CDO 기본값

`get_default_object` → `/Game/Blueprints/BP_BattleSpawnPoint.Default__BP_BattleSpawnPoint_C`, 컴포넌트 `HpGaugeWidget_GEN_VARIABLE`(클래스 `/Script/UMG.WidgetComponent`):

| 프로퍼티 | 값 |
|---|---|
| `space` | `Screen` |
| `widgetClass` | `/Game/UI/Battle/WBP_HpGauge.WBP_HpGauge_C` |
| `drawSize` | (140, 50) |
| `relativeLocation` | (0, 96.5, 0) |
| `pivot` | (0.5, 0.5) |
| `bVisible` | true |
| `geometryMode` | `Plane` |
| `tickMode` | `Enabled` |
| `bDrawAtDesiredSize` | false |

CDO 컴포넌트 전체 목록(참고): `Arrow`·`TurnMarker`·`ClickBox`·`EffectQuad`·`HpGaugeWidget`·`Sprite`.

EventGraph에 `GetHpGaugeWidget`(VariableGet) → `GetUserWidgetObject` → (DynamicCast로 이어짐, 이후 `SetHpText` 호출 추정) 노드 체인 존재 — 런타임에 위젯 컴포넌트의 UserWidget 인스턴스를 얻어 텍스트를 갱신하는 경로. `UserConstructionScript`에는 위젯 관련 노드 없음(= Space/WidgetClass/DrawSize/RelativeLocation은 SCS 컴포넌트 템플릿 기본값이며, 임퍼러티브 코드로 세팅되지 않음).

## 3. ⚠ 발견: 레벨에 배치된 8인스턴스는 CDO 기본값과 불일치

`map_battle_octopath` 레벨의 실제 배치 액터 8개(`BP_BattleSpawnPoint_C_0/2/3/4/5/6/7/9`, 라벨 `SpawnPoint_Party_A1~A4`/`SpawnPoint_Enemy_B1~B4`) 전부 `HpGaugeWidget` 프로퍼티가 **CDO와 다른, WidgetComponent 엔진 네이티브 기본값**을 보임:

| 인스턴스 라벨 | space | widgetClass | drawSize | relativeLocation |
|---|---|---|---|---|
| SpawnPoint_Party_A1 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Party_A2 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Party_A3 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Party_A4 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Enemy_B1 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Enemy_B2 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Enemy_B3 | World | **None** | (500,500) | (0,0,0) |
| SpawnPoint_Enemy_B4 | World | **None** | (500,500) | (0,0,0) |

CDO는 `Screen`/`WBP_HpGauge_C`/(140,50)/(0,96.5,0)인데 8인스턴스 전부 `World`/`None`/(500,500)/(0,0,0) — WidgetComponent가 처음 추가됐을 때의 엔진 네이티브 기본값 그대로다. **이 문서 작성 시점 기준, 레벨에 실제 배치된 액터들은 HP 게이지 위젯이 기능하지 않는 상태로 저장되어 있을 가능성이 있다**(`GetUserWidgetObject`가 `WidgetClass=None`이면 위젯 인스턴스를 만들지 못해 `None`을 반환 → 이후 캐스트/`SetHpText` 체인이 조용히 실패).

원인은 미확인(추정: SCS 템플릿 값이 액터 배치 이후 변경됐고, 배치 인스턴스의 per-instance 프로퍼티 델타가 재동기화되지 않았을 가능성 — 확정하려면 별도 디버깅 필요, 이 작업 스코프 밖). **이 발견은 이번 골격 생성 작업과 직접 관련 없어 수정하지 않고 그대로 둔다** — Director/후속 gameplay-engineer 확인 필요 항목으로 보고.

## 롤백 절차

문제 발생 시:
1. `WBP_HpGauge` 애셋을 삭제하지 않았다면(§4 처리 방식 참고) 원상태 그대로 유지.
2. `BP_BattleSpawnPoint`의 `HpGaugeWidget` 컴포넌트 CDO 프로퍼티를 위 §2 표 값으로 복원(`ObjectTools.set_properties`).
3. 레벨 8인스턴스는 원래도 위 §3 표 상태(비정상)였으므로 "복원"이 아니라 "그대로 둠"이 곧 롤백.

## 4. ⚠ 착수 중 발견: EventGraph의 `Cast To WBP_HpGauge` 커플링 — WidgetComponent 갱신 시도 후 원복

작업 지시(§3: "BP_BattleSpawnPoint의 WidgetComponent를 UnitFrame으로 갱신")에 따라 `HpGaugeWidget_GEN_VARIABLE.widgetClass`를 `WBP_HpGauge_C → WBP_UnitFrame_C`로 변경 후 컴파일까지 성공(에러 0)했으나, 저장 후 `WBP_HpGauge`의 referencer가 여전히 `BP_BattleSpawnPoint` 1건으로 남아있어 조사한 결과:

- `EventGraph`에 `K2Node_DynamicCast_2`(`type_id: Utilities|Casting|CastToWBP_HpGauge`) 노드가 별도로 `WBP_HpGauge` 타입을 하드 참조 중. 체인: `GetHpGaugeWidget(컴포넌트) → GetUserWidgetObject → Cast To WBP_HpGauge → (추정) SetHpText 호출`.
- WidgetComponent의 `widgetClass` 프로퍼티(런타임에 실제 생성되는 위젯 클래스)와 이 Cast 노드(타입 체크)는 **서로 독립적인 별개 참조**다. `widgetClass`만 `WBP_UnitFrame_C`로 바꾸면 컴파일은 통과하지만(타입 에러 아님), **런타임에 Cast가 항상 실패**하는 조용한 회귀가 생긴다(`WBP_UnitFrame` 인스턴스를 `WBP_HpGauge`로 캐스팅 시도 → 항상 실패 → 이후 `SetHpText` 분기 미실행).
- `WBP_UnitFrame.SetHp` 함수는 이번 골격 단계에서 시그니처만 생성(빈 바디) — 설령 Cast 타입까지 맞춰 고쳐도 지금 당장은 아무 동작도 하지 않음(오너가 §3-3 트리를 배치해야 `Bar_Hp`/`Txt_HpValue`가 생겨 SetHp 바디를 채울 수 있음).

**결정**: `widgetClass` 변경을 **원복**(`WBP_HpGauge_C`로 되돌림, 컴파일+저장 재확인). `WBP_HpGauge`는 삭제하지 않고 그대로 유지. EventGraph의 Cast 타깃 교체 + `SetHpText`→`SetHp` 호출부 재배선은 **§B 5단계(배선)로 이월** — 오너가 `WBP_UnitFrame`에 `Bar_Hp`/`Txt_HpValue`를 배치한 뒤, Cast 타깃 교체와 `SetHp` 바디 구현을 한 번에 원자적으로 처리하는 것이 안전(지금 절반만 바꾸면 "왜 Cast가 항상 실패하는지" 불명확한 상태로 남아 디버깅 함정이 됨).

**Director 보고 사항**: 작업 지시 "WidgetComponent를 UnitFrame으로 갱신"은 문자 그대로는 실행했으나(컴파일 에러 0 확인됨), EventGraph 커플링 때문에 **의도한 효과(HP 표시가 UnitFrame으로 전환)는 나지 않고 오히려 기존 F3b 표시를 조용히 깨뜨리는 부작용**이 있어 원복했다. 명세와 다르게 구현한 부분 — 근본 원인 없이 수정 금지 원칙에 따름.
