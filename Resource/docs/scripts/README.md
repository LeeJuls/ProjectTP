# docs/scripts/ — 자동화 스크립트 카탈로그

**여기서 무엇을 찾을 수 있는가** (AI는 이 4줄만 읽어도 판단 가능해야 한다):
- **루트의 로그 4종**(`battle_log/` 패키지 + `extract_battle_log.py`/`oracle_diff.py`/`battle_log_selftest.py`) = ★현행. 전투 로그를 파싱해 오라클(정답지) CSV와 비교하는 파이프라인. **의도적으로 하위폴더로 옮기지 않았다** — 이유는 아래 "왜 루트인가" 참고.
- **`compose/`** = heroes99 캐릭터 스프라이트 Pillow 합성. 지금은 대기 중이지만 **A2(캐릭터 1000명 합성) 단계에서 재가동 예정** — 참조 0건이어도 죽은 스크립트가 아니다.
- **`mockup/`** = HD2D 전투배경 목업(오프라인 Pillow 합성). 목적 달성 후 종료, 결과물(PNG)만 참고용으로 남아있다.
- **`assets/`** = 파츠 데이터 생성/실측/캡처 디코드 등 개별 목적 도구 모음. 파일별로 생사가 다르므로 아래 표의 상태 컬럼을 반드시 확인할 것.

## 왜 로그 4개는 루트에 남았는가

이번 재편(2026-08-13)에서 `battle_log/` + `extract_battle_log.py` + `oracle_diff.py` + `battle_log_selftest.py`는 **하위 도메인 폴더로 옮기지 않았다.** 정리가 덜 된 게 아니라 의도적 결정이다. 근거 2가지:

1. `battle_log_selftest.py`가 `sys.path.insert(0, SCRIPTS_DIR)` 뒤 `import oracle_diff`로 **형제 모듈을 이 디렉터리 기준 상대 import**한다(스크립트 201행 부근). 옮기면 3개 파일 전부의 import/경로 계산을 고쳐야 한다.
2. `extract_battle_log.py`의 실행 경로가 **19개 문서**에 박혀 있다 — 이동 비용이 이 폴더에서 가장 크다.

다음에 이 폴더를 보는 사람(AI 포함)은 이 4개를 "정리가 덜 됐다"고 오판해 옮기지 말 것.

## 상태 어휘

| 상태 | 의미 |
|---|---|
| `현행` | 지금도 실행되거나 다른 워크플로우에서 계속 호출되는 파이프라인 |
| `대기(A2 재가동)` | 지금은 안 돌지만 A2 단계(캐릭터 1000명 합성/생성)에서 재사용이 이미 계획되어 있음 |
| `종료` | 목적(조사·스파이크·목업)을 달성하고 결과물만 남긴 상태. 재실행 가능하지만 계획된 재가동 시점 없음 |

## 표

| 파일 | 도메인 | 상태 | 마지막 실사용 | 실행법 | 참조 문서 수 |
|---|---|---|---|---|---|
| `battle_log/*.py`(6모듈: `__init__`·`io_utils`·`oracle`·`parser`·`session`·`tokens`) | battle_log | 현행 | 2026-08-12 | 직접 실행 안 함 — 아래 3개 실행기의 내부 모듈 | 19 |
| `extract_battle_log.py` | battle_log | 현행 | 2026-08-12 | `python docs/scripts/extract_battle_log.py` | 19 |
| `oracle_diff.py` | battle_log | 현행 | 2026-08-12 | `python docs/scripts/oracle_diff.py --oracle <오라클CSV> --log <battle_*.log>` | 2 |
| `battle_log_selftest.py` | battle_log | 현행 | 2026-08-12 | `python docs/scripts/battle_log_selftest.py` (32/32 PASS 유지가 게이트) | 1 |
| `compose/compose_basic.py` | compose | 대기(A2 재가동) | 2026-06-28 | `cd _RawAssets\heroes99` 후 `python D:\unreal\Resource\docs\scripts\compose\compose_basic.py` — **CWD 의존**(`base = "."`, `__file__` 아님) | 0 |
| `compose/compose_knight.py` | compose | 대기(A2 재가동) | 2026-06-28 | 상동 — **CWD 의존**(`base = "."`) | 2 |
| `compose/compose_party.py` | compose | 대기(A2 재가동) | 2026-07-05 | `python docs/scripts/compose/compose_party.py` — 내부 경로 전부 절대경로(`RAW_ROOT`), CWD 무관 | 8 |
| `compose/compose_a0_spike_layers.py` | compose | 대기(A2 재가동) | 2026-07-08 | `python docs/scripts/compose/compose_a0_spike_layers.py` — 절대경로, CWD 무관 | 1 |
| `compose/compose_test_combo.py` | compose | 대기(A2 재가동) | 2026-07-08 | `python docs/scripts/compose/compose_test_combo.py` — 절대경로, CWD 무관 | 2 |
| `mockup/mockup_bg_v1.py` | mockup | 종료 | 2026-07-31 | `python docs/scripts/mockup/mockup_bg_v1.py` | 1 |
| `mockup/mockup_bg_v2.py` | mockup | 종료 | 2026-07-31 | `python docs/scripts/mockup/mockup_bg_v2.py` | 0 |
| `mockup/mockup_qa_calib.py` | mockup | 종료 | 2026-07-31 | `python docs/scripts/mockup/mockup_qa_calib.py` | 0 |
| `mockup/mockup_qa_spacing.py` | mockup | 종료 | 2026-07-31 | `python docs/scripts/mockup/mockup_qa_spacing.py` | 0 |
| `mockup/mockup_density_compare.py` | mockup | 종료 | 2026-07-31 | `python docs/scripts/mockup/mockup_density_compare.py` | 0 |
| `mockup/mockup_extract_parts.py` | mockup | 종료 | 2026-07-31 | `python docs/scripts/mockup/mockup_extract_parts.py` (위 5개 목업 스크립트의 부품 원본 추출기) | 1 |
| `assets/gen_parts_csv.py` | assets | 대기(A2 재가동) | 2026-07-08 | `python docs/scripts/assets/gen_parts_csv.py` → `data/parts.csv` 생성. `알파_개발계획.md` A2-S3(1000풀 생성기)가 이 스크립트의 387콤보 패턴을 재사용 예정 | 1 |
| `assets/inventory_row_coverage.py` | assets | 종료 | 2026-07-08 | `python docs/scripts/assets/inventory_row_coverage.py` — 결과는 같은 폴더 `inventory_row_coverage_result.json`에 저장(경로는 `__file__` 기준이라 두 파일을 같은 폴더에 유지해야 함) | 2 |
| `assets/inventory_row_coverage_result.json` | assets | 종료 | 2026-07-08 | 실행 파일 아님 — 위 스크립트의 산출물(원자료, 재사용 가능) | 2(스크립트와 공유) |
| `assets/decode_capture.py` | assets | 현행 | 2026-07-06 | `python docs/scripts/assets/decode_capture.py <tool-results.txt> <out.png>` — MCP `CaptureViewport` base64 결과를 PNG로 디코드하는 범용 유틸(특정 기능에 종속되지 않고 필요할 때마다 계속 호출됨) | 6 |

## 이번 재편(2026-08-13) 메모

- 이동 10개 `.py` + `compose_basic.py`/`compose_knight.py`/`compose_party.py`/`compose_a0_spike_layers.py`/`compose_test_combo.py`(5) + `mockup_*.py`(6) + `gen_parts_csv.py`/`inventory_row_coverage.py`/`decode_capture.py`(3) + `inventory_row_coverage_result.json`(1) = **15개 항목**(14개 `.py` + 1개 `.json`)을 `git mv`로 이동, 이력 보존.
- 이동 전 15개 파일 전수 열람 결과, **`inventory_row_coverage.py`만 `os.path.dirname(__file__)` 기반 상대경로**를 썼다(결과 json 저장 경로). 스크립트와 json을 같은 `assets/` 폴더로 함께 옮겼으므로 **코드 수정 불필요**. 나머지는 절대경로(`RAW_ROOT`/`PARTS_DIR`/`OUT_DIR` 등) 또는 CWD 기준 상대경로(`compose_basic.py`/`compose_knight.py`의 `base = "."`)라 이동에 영향받지 않는다.
- 파일 삭제 0. 문서 경로 참조는 실행 경로(코드블록·백틱 경로)만 갱신했고, `[[compose_party.py]]` 같은 Obsidian 위키링크는 파일명 기준으로 해석되므로 그대로 둬도 깨지지 않는다.
