---
type: guide
project: projectTP
updated: 2026-06-28
---

# 🔌 셋업 가이드 — 에디터 실행 & MCP 연결

> 목적: projectTP 에디터를 띄우고 Unreal MCP 서버를 기동해 **Claude가 에디터를 직접 조종**할 수 있게 한다.
> 허브: [[projectTP_허브]]

생성된 파일 (Claude가 만듦):
- `D:\unreal\projectTP\projectTP.uproject` — 플러그인(Paper2D / ModelContextProtocol / ToolsetRegistry) 활성
- `D:\unreal\projectTP\_Launch_MCP.bat` — 에디터 실행 + MCP 서버 자동 기동(port 8000)
- `D:\unreal\Resource\.mcp.json` — Claude Code 연결 설정

---

## 오너가 할 일 (순서대로)

### 1단계. 에디터 실행
- `D:\unreal\projectTP\_Launch_MCP.bat` **더블클릭**.
- ⚠ `.uproject`를 직접 더블클릭하지 말 것 — 엔진이 등록 안 돼 있어 엔진 선택 창이 뜸. 반드시 **.bat**로 실행.
- ⚠ 첫 실행은 셰이더/DDC 컴파일로 **수 분** 걸림(정상). 창이 멈춘 듯 보여도 대기.
- (SmartScreen 경고 시: "추가 정보 → 실행")

### 2단계. MCP 서버 기동 확인
에디터가 열린 뒤, 서버가 떴는지 확인:
- **방법 A (자동)**: `.bat`의 `-ExecCmds`가 이미 `StartServer 8000`을 실행함. → 보통 자동으로 떠 있음.
- **방법 B (수동/확인)**: 에디터에서 백틱(`` ` ``) 눌러 콘솔 열고:
  ```
  ModelContextProtocol.StartServer 8000
  ```
- **방법 C (영구 자동시작)**: `Edit > Editor Preferences > General > Model Context Protocol` → **Auto Start Server** 켜두면 다음부터 자동.
- 확인: 같은 Preferences 화면 또는 Output Log에 서버 동작/포트(8000) 표시.

### 3단계. Claude Code 재시작
- 현재 세션은 새 `.mcp.json`을 실시간으로 못 읽음.
- Claude Code를 **종료 후 재실행** (작업 폴더 `D:\unreal\Resource` 유지).
- 재시작 시 새 MCP 서버 **`unreal-mcp` 승인 프롬프트**가 뜨면 **허용**.

### 4단계. Claude에게 알리기
- 위 완료 후 "에디터 떴고 MCP 켰어" 라고 알려주세요.
- 제가 MCP 도구를 호출해 **연결 확인**하고, 그때부터 임포트·머티리얼·라이팅·무대 셋업을 직접 진행합니다.

---

## 문제 시 체크리스트

| 증상 | 확인 |
|---|---|
| 엔진 선택 창이 뜸 | `.uproject` 직접 실행한 것 — `.bat`로 실행 |
| 에디터가 안 열림/모듈 오류 | BP 전용이라 컴파일 불필요. 플러그인명 오타? (`ModelContextProtocol`/`ToolsetRegistry`) |
| 재시작 후에도 unreal-mcp 안 보임 | `.mcp.json` 위치가 Claude Code 실행 폴더와 같은지(`D:\unreal\Resource`) |
| Claude가 도구 호출 시 연결 실패 | 에디터 떠 있는지 + 서버 8000 기동됐는지 + 포트 점유 충돌 |

---

## 연결 성공 후 다음 (Claude가 진행)
[[ArtMVP_아트선검증_계획]]의 S0~S7 — 더미 스프라이트로 HD-2D 파이프라인 선검증 → heroes99 스왑.
