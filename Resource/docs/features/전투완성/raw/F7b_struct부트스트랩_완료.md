---
type: raw
project: projectTP
feature: 전투완성
stage: F7b-struct부트스트랩
status: 완료 2026-07-16(오너 승인 설치)
updated: 2026-07-16
---

# F7b struct 부트스트랩 완료 — TAPython 설치 + struct 3종 신설

> 대상: [[F7_스킬아키텍처_확정]] §7-2·§8-13 · [[야간작업_총결산_2026-07-16]] §3-① · [[F7b_데이터초안_노트]] · [[언리얼_MCP_실전노하우]] §33
> 직전 문서(`F7b_TAPython_부트스트랩_보류.md`, 이 문서가 전면 대체하며 원본은 삭제됨)가 "다운로드·설치는 Claude 실행범위 밖" 사유로 보류했던 건. 이후 오너가 채팅에서 TAPython 설치를 직접 승인해 상황이 바뀌었고, 설치·struct 생성까지 성공적으로 완료됐다.
#projectTP/전투완성

---

## 1. 배경

F7b 3층 정규화(`DT_Skills`의 구식 `Effect*` 컬럼 제거 + 신규 `F_StatusEffectRow`/`F_SkillEffectRow` 도입)를 위해서는 새 `UserDefinedStruct` 2종 신설과 `F_SkillsRow`에 필드 8개 추가가 필요했다. 이 struct 신설 작업은 (a) 오너 수동 GUI 생성 또는 (b) TAPython 설치 후 스크립트 자동생성 — 두 안 중 선택 대기 상태였다([[야간작업_총결산_2026-07-16]] §3-①).

오너가 채팅에서 TAPython 설치를 직접 승인했다 — **무료 · UE5.8용 · v1.3.3(정식판, prerelease 아님) · AGPL-3.0(에디터 전용 사용이라 배포 조항 리스크 없음)**을 확인한 뒤의 승인이다.

## 2. 설치

- **소스**: GitHub `cgerchenhp/UE_TAPython_Plugin_Release` `v1.3.3-ue5.8.0` zip.
- **배치**: 압축 해제 후 `D:\unreal\projectTP\Plugins\TAPython\`(내부에 `TAPython.uplugin` 존재 확인).
- **`projectTP.uproject`**: `Plugins` 배열에 추가.
  ```json
  { "Name": "PythonScriptPlugin", "Enabled": true },
  { "Name": "TAPython", "Enabled": true }
  ```
- **`.gitignore`**: 플러그인 폴더 + TA 런타임 산출 폴더 제외.
  ```
  /projectTP/Plugins/TAPython/
  /projectTP/TA/
  ```
- **`Content/Python/init_unreal.py`**: 에디터 startup에 자동 실행되는 부트스트랩 스크립트. `Content/`가 통째로 gitignore 대상이라 이 파일은 git 미추적 — 재현법은 이 문서로 대신한다.

## 3. 결과 (로그·MCP 검증)

- `F_StatusEffectRow` **11필드**, `F_SkillEffectRow` **16필드** 신설.
- `F_SkillsRow` **15→23**(기존 15필드 전부 보존 + 신규 8필드 추가, 기존 필드 유실 없음).
- MCP `list_properties`로 3종 struct의 전 필드 **타입 전수 확인** — string/number/integer 명세가 작업지시서와 일치.
- `DT_Skills`에 대해 `get_rows(31000000)`로 **하위호환 실증** — 기존 값 전부 온전, 신규 컬럼은 기본값으로 채워짐(기존 데이터 파손 없음).
- `BP_BattleManager` **컴파일 0에러** — 이전 세션의 에디터 강제종료([[언리얼_MCP_실전노하우]] §33 (77) 참고) 이후에도 애셋 무결성 확인.

## 4. 커밋

**701741e** `[C] chore(F7b): TAPython 플러그인 활성화 — struct 부트스트랩 인프라 (uproject 플러그인 등록 + gitignore)` — `projectTP.uproject`·`.gitignore` 변경분.

**재현 절차**:
1. 위 zip을 받아 `projectTP/Plugins/TAPython/`에 압축 해제.
2. `projectTP.uproject`에 `PythonScriptPlugin`·`TAPython` 활성화 추가.
3. `.gitignore`에 플러그인·TA 런타임 폴더 제외 추가.
4. `Content/Python/init_unreal.py` 배치 후 에디터 시작 — startup에 자동 실행되어 struct 3종을 생성한다.

## 5. 스캐폴드 — init_unreal.py 후속 처리

`init_unreal.py`는 재실행되어도 `F_StatusEffectRow` 존재 시 전체를 스킵하는 **멱등 가드**가 있어 무해하지만, 매 에디터 startup마다 불필요하게 재실행되는 것을 막기 위해 **성공 확인 후 파일명 변경(rename)을 권장**한다(예: `init_unreal.py.done`). 아직 미실행 — 다음 세션에서 처리해도 무방.

`Content/Python/`은 gitignore 대상이라 git에는 포함되지 않는다. 재현이 필요하면 위 §4 절차와 이 문서를 참고한다(스크립트 자체는 스캐폴드 성격이라 커밋 대상에서 의도적으로 제외).

---

## 관련
[[F7_스킬아키텍처_확정]] §7-2·§8-13 · [[야간작업_총결산_2026-07-16]] §3-① · [[F7b_데이터초안_노트]] · [[언리얼_MCP_실전노하우]] §33
