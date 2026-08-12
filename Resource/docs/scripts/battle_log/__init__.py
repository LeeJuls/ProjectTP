"""battle_log — 전투 로그 ingestion 공용 모듈 (파싱의 단일 소스).

LOG-A_실행계획.md(오너 승인)의 ①ingestion 공용 모듈 산출물.

이 패키지 밖(oracle_diff.py·extract_battle_log.py 등)에서는 토큰 프리픽스 리터럴을
직접 문자열로 다루지 않는다. 전부 `battle_log.tokens` 레지스트리 + `battle_log.parser`
함수를 통해서만 접근한다(★게이트: 원장 토큰의 프리픽스 리터럴이 전체 스크립트 트리에서
`tokens.py`의 레지스트리 엔트리 단 1곳에만 존재해야 한다).

서브모듈:
    tokens   — 18종 토큰 레지스트리(프리픽스·카테고리·문법) — 카테고리 배정의 단일 소스.
               `render_category_markdown()`이 전투로그.md §3 표의 생성기(SSOT는 이 파일).
    parser   — 라인 프리픽스 스트립 + pipe key=value 파싱 (died 위치 가변 → dict 필수).
               `parse_line_meta()`가 ts·frame·rest를 동시에 추출 — sid 유도 순서 제약의 기반.
    session  — `SessionBoundary|` 소비 — sid 유도(`derive_sid`) + 세션 경계 분할
               (`assign_sessions`) + 세션 키 `(sid, init_ordinal)` 계산(`assign_session_keys`).
    oracle   — 오라클 문서(§0 직업 배정 표, §7 CSV 블록) 파싱 + 로그→오라클 스키마 매핑.
    io_utils — 로그 파일 탐색·읽기·추출 산출물 저장 (extract_battle_log.py 원본 로직 이관).
"""
