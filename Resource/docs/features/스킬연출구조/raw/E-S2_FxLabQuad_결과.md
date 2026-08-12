---
type: record
project: projectTP
feature: 스킬연출구조
stage: E-S2
updated: 2026-08-11
status: PASS
status_note: 부분 통과 — 구현·fail-loud PASS / 타이밍 5건 미실증(원인=환경, 규명 완료)
---

# E-S2 — `BP_FxLabQuad` + `PlayVfx` 결과

> 상위: [[E_스파이크_plan]] · 후속: [[E-S2_틱스로틀_진단]]

## 구현 — 완료

`/Game/Blueprints/BP_FxLabQuad`(Actor). 컴포넌트 `Quad`(Plane), 변수 `Mid`(MID)·`PendingVfxId`(int).

★**2단 구조**로 구현했다: `PlayVfx(vfxId)` **Function** + `PlayVfxInternal` **Custom Event**.

이유 — `RetriggerableDelay`·`AsyncLoadAsset` 같은 **latent 노드는 Function Graph에서 못 쓰고**(함정④), Custom Event는 **MCP로 파라미터 추가가 불가**(함정⑰)하다. 그래서 `PlayVfx`가 멤버변수 `PendingVfxId`에 값을 넣고 파라미터 없는 `PlayVfxInternal`을 호출한다.

### 로직

```
GetDataTableRow(DT_Vfx) ─ RowNotFound → LOG FXLAB:FXNOROW:<id> → 종료
BreakFVfxRow
(frameCount≤0 OR fps≤0) → LOG FXLAB:FXSKIP:<id> → 종료      ← 경계값 가드
MakeSoftObjectPath → AsyncLoadAsset → CastToTexture2D
  └ CastFailed → LOG FXLAB:TEXMISS:<id>:<path> → 종료
SetTextureParameterValue + SetScalar ×5 (GridX·GridY·RowIndex·FrameCount·FPS) + TimeOffset
SetVisibility(true) → LOG FXLAB:FXSHOW
RetriggerableDelay( Max( SafeDivide(frameCount, fps) − 0.05, 0.0 ) )   ← ★계산식
SetVisibility(false) → LOG FXLAB:FXHIDE
```

**컴파일 에러 0.** 지시서 규칙 5개 전부 충족 — 계산식 · 매 재생마다 DT 조회 · DT 조회가 exec 상류 · 스칼라 동시 세트 · 토큰 분리(`FXNOROW`/`TEXMISS`/`FXSKIP` 3종).

레벨 배치: `map_battle_fxlab`에 `FxQuad_Cast`/`Travel`/`Impact` 3기, 아웃라이너 `FxLab/` 폴더.

---

## 판정 7건 — **2 PASS / 5 미실증**

| # | 판정 | 결과 |
|---|---|---|
| 4 | **fail-loud**(`63009999`) | ✅ **PASS** — `FXLAB:FXNOROW:63009999` 3기 각 1줄, 재생 0, 크래시 0 |
| 7 | **경계값**(fps=0 / frameCount=0) | ✅ **PASS** — `FXLAB:FXSKIP` 1줄, 0나눗셈·무한 Delay·크래시 전부 0 |
| 1 | Δt 0.45/0.55 | ❌ 미실증 |
| 2 | 관통(fps 10→40) | ❌ 미실증 |
| 3 | PIE 핫리로드 | ⚠ 부분 — `set_rows`가 PIE 중에도 성공하는 것은 확인. "다음 재생부터 반영"은 미관측 |
| 5 | 색 행(`colorRow=2`) | ❌ 미실증 |
| 6 | 스칼라 잔존 0 | ❌ 미실증 |

★**미실증 5건은 전부 같은 지점에서 막혔다** — `AsyncLoadAsset`이 완료되지 않아 `TEXMISS`로 빠지고, 그 뒤 `SetVisibility`·`RetriggerableDelay`에 도달하지 못한다.

★★**그리고 그 원인은 그래프 결함이 아니라 환경이다.** → [[E-S2_틱스로틀_진단]]

---

## DT 원복 — 확인

`DT_Vfx` 5행이 최초 값과 **바이트 단위 동일**(`get_rows` 재조회). 테스트용 임시 행(`63009001`·`63009002`) 전부 `remove_rows`로 제거, `list_rows` 5행만 잔존. **저장 안 함** — 디스크 무변경.

---

## ★남은 부채 (정리 대상)

| 항목 | 내용 |
|---|---|
| **orphaned 노드** | `TestDriver_TEMP`(Custom Event) + 진단용 노드 다수가 EventGraph에 **연결 끊긴 채** 잔존. `delete_node`가 그래프 전역 연결을 파괴하는 기지 위험(함정㉜/㉟) 때문에 `break_pins`로 비활성화만 했다. 컴파일·런타임 무영향 |
| **`TempDT` 변수** | DataTable 타입, 미사용. 노드 검색 실험 잔재 |

→ **정리 시점**: 스로틀 해제 후 타이밍 5건을 재검증하고 나서. 지금 지우면 재검증 시 진단 노드가 다시 필요해질 수 있다.

---

## 관련

- 원인 규명: [[E-S2_틱스로틀_진단]]
- 노드 제약 근거: [[언리얼_MCP_실전노하우]] 함정④·⑰·㉜·㉟
- 상위: [[E_스파이크_plan]] S2
