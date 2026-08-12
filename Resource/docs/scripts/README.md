# docs/scripts/ — 자동화 스크립트 카탈로그

**여기서 무엇을 찾을 수 있는가** (AI는 이 4줄만 읽어도 판단 가능해야 한다):
- **루트의 로그 4종**(`battle_log/` 패키지 + `extract_battle_log.py`/`oracle_diff.py`/`battle_log_selftest.py`) = ★현행. 전투 로그를 파싱해 오라클(정답지) CSV와 비교하는 파이프라인. **의도적으로 하위폴더로 옮기지 않았다** — 이유는 아래 "왜 루트인가" 참고.
- **`compose/`** = heroes99 캐릭터 스프라이트 Pillow 합성. 지금은 대기 중이지만 **A2(캐릭터 1000명 합성) 단계에서 재가동 예정** — 참조 0건이어도 죽은 스크립트가 아니다.
- **`mockup/`** = HD2D 전투배경 목업(오프라인 Pillow 합성). 목적 달성 후 종료, 결과물(PNG)만 참고용으로 남아있다.
- **`assets/`** = 파츠 데이터 생성/실측/캡처 디코드 등 개별 목적 도구 모음. 파일별로 생사가 다르므로 아래 표의 상태 컬럼을 반드시 확인할 것.
- **`vaultfix/`** = 옵시디언 볼트 frontmatter 정규화 도구(문서구조_개선plan 3단계). `status`/`type` 값을 BT-DOC2 SSOT 규칙대로 enum화한다. 재실행 멱등 — 이미 enum이면 건드리지 않는다.

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
| `vaultfix/normalize_status_type.py` | vaultfix | 현행(2026-08-13 1회 실행 완료, 재실행 가능) | 2026-08-13 | `python docs/scripts/vaultfix/normalize_status_type.py [--apply] [--json-report <path>] [--text-report <path>]` — 기본은 dry-run. BT-DOC2(`features/전투완성/raw/BT-DOC2_status매핑규칙.md`) §3~§8 규칙을 그대로 실행해 frontmatter `status`(7종 enum)·`type`(9종 enum)을 정규화한다. 멱등(이미 enum인 값은 스킵) | 0(문서에 실행경로 아직 미기재) |
| `vaultfix/convert_section_refs.py` | vaultfix | 현행(2026-08-13 1회 적용 완료, 재실행 가능) | 2026-08-13 | `python docs/scripts/vaultfix/convert_section_refs.py [--apply] [--text-report <path>]` — 기본은 dry-run. 문서구조_개선plan v4 4단계: 다른 파일을 가리키는 `<약칭/파일명> §N` 텍스트 참조를 `[[파일]] §N` 위키링크로 변환(197건 적용, 2건 자기참조 스킵, 36건 판단 보류 — `features/전투완성/raw/vaultfix_stage4_적용결과_2026-08-13.txt` 참고). 접두사 매핑은 파일명 규칙에서 기계적으로 생성하고 최소 1개 ASCII 숫자를 요구해 오탐을 막는다. 멱등(이미 `[[..]]`인 참조는 마스킹되어 재매칭 안 됨) | 0(문서에 실행경로 아직 미기재) |
| `vaultfix/generate_index.py` | vaultfix | 현행(2026-08-13 신설) | 2026-08-13 | `python docs/scripts/vaultfix/generate_index.py [--apply]` — 기본은 dry-run(통계만 출력). 문서구조_개선plan v4 5단계: `docs/INDEX.md`를 frontmatter(`type`·`status`·`status_note`)에서 자동생성한다. 손으로 편집 금지 — 재실행 시 덮어써진다. 멱등(같은 날 재실행 시 바이트 단위 동일) | 0(문서에 실행경로 아직 미기재) |
| `vaultfix/shrink_screenshots.py` | vaultfix | 종료(WebP 전환 전 1차 축소에 사용 — 이력. 57장 전부 `png_to_webp.py`로 대체 전환 완료돼 대상 PNG가 더 이상 없음) | 2026-08-13 | `python docs/scripts/vaultfix/shrink_screenshots.py [--apply] [--max-long-edge <px>]` — 기본은 dry-run. `docs/features/*/raw/*.png` 게이트 증거 스크린샷을 긴 변 1600px로 LANCZOS 리사이즈 + PNG 무손실 재압축(팔레트 양자화는 하늘 그라데이션 밴딩이 확인되어 제외). 57장 162.49MB → 86.17MB(53.0%, 76.31MB 절감) — 이 1600px 축소본이 이후 `png_to_webp.py`가 참고한 "긴 변 1600px" 값의 근거가 됐다. `docs/renders/`(git 추적 중)는 glob 범위 밖이라 무관 | 0(문서에 실행경로 아직 미기재) |
| `vaultfix/png_to_webp.py` | vaultfix | 현행(2026-08-13 1회 적용 완료, 재실행 가능) | 2026-08-13 | `python docs/scripts/vaultfix/png_to_webp.py [--apply] [--source-dir <경로>] [--max-long-edge <px>] [--quality <0-100>] [--method <0-6>]` — 기본은 dry-run. 오너 승인("PNG 86MB에서 더 줄이자 — WebP 전환")으로 `docs/features/*/raw/*.png` 57장을 **원본(2169px) 백업에서 직접**(1600px 축소본을 재리샘플하지 않고) 긴 변 1600px LANCZOS 리사이즈 + WebP 손실 인코딩(quality=90, method=6)으로 전환하고 원본 PNG를 삭제한다. 57장 86.17MB(1600px PNG 기준) → 13.73MB(15.9%, 72.45MB 절감) / 원본 162.49MB 대비 91.5% 절감. 알파는 실제로 쓰이는 파일만 유지(실측 1장 — PM 지시서의 "4개" 추정과 다름, `--apply` 로그에 보고). 대상 PNG가 이미 없으면(=이미 전환됨) 원본 백업 없이도 멱등 종료. `docs/renders/`는 glob 범위 밖이라 무관 | 0(문서에 실행경로 아직 미기재) |

## 이번 재편(2026-08-13) 메모

- 이동 10개 `.py` + `compose_basic.py`/`compose_knight.py`/`compose_party.py`/`compose_a0_spike_layers.py`/`compose_test_combo.py`(5) + `mockup_*.py`(6) + `gen_parts_csv.py`/`inventory_row_coverage.py`/`decode_capture.py`(3) + `inventory_row_coverage_result.json`(1) = **15개 항목**(14개 `.py` + 1개 `.json`)을 `git mv`로 이동, 이력 보존.
- 이동 전 15개 파일 전수 열람 결과, **`inventory_row_coverage.py`만 `os.path.dirname(__file__)` 기반 상대경로**를 썼다(결과 json 저장 경로). 스크립트와 json을 같은 `assets/` 폴더로 함께 옮겼으므로 **코드 수정 불필요**. 나머지는 절대경로(`RAW_ROOT`/`PARTS_DIR`/`OUT_DIR` 등) 또는 CWD 기준 상대경로(`compose_basic.py`/`compose_knight.py`의 `base = "."`)라 이동에 영향받지 않는다.
- 파일 삭제 0. 문서 경로 참조는 실행 경로(코드블록·백틱 경로)만 갱신했고, `[[compose_party.py]]` 같은 Obsidian 위키링크는 파일명 기준으로 해석되므로 그대로 둬도 깨지지 않는다.
