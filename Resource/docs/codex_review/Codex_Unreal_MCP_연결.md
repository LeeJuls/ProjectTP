---
type: codex_mcp_connection_mirror
project: projectTP
canonical: D:\unreal\review_agent\unreal_mcp_connection.md
status: configured_and_endpoint_verified
codex_client_activation: pending_restart_verification
read_only_enforcement: operational_not_server_enforced
created: 2026-07-16
---

# Codex Unreal MCP 연결

- Codex에 `unreal-mcp` 등록 완료: `http://127.0.0.1:8000/mcp`
- Unreal Editor가 `127.0.0.1:8000`에서 서버를 실행 중인 것을 확인했다.
- MCP 초기화 HTTP 200 및 세션 발급 확인.
- 도구 3종 확인: `list_toolsets`, `describe_toolset`, `call_tool`.
- 모든 MCP 호출 기본 승인 모드: `prompt`.
- 프로젝트 소스·Blueprint 변경 없음.
- 적용 시점: Codex 재시작 또는 새 작업 시작 후.
- Codex 클라이언트 노출 확인: 재시작 후 검증 대기.

## 리뷰 안전 규칙

Codex는 조회·설명·내보내기만 사용한다. 생성·삭제·리네임·핀 연결·값 변경·컴파일·저장·임포트·PIE 제어는 오너가 새로 명시 승인하기 전 금지한다. 단, 이것은 서버가 강제하는 allowlist가 아니라 운영 계약이다. `call_tool`은 내부 쓰기 도구에도 기술적으로 접근할 수 있으므로 항상 승인 대상으로 유지하고, 승인 전에 내부 도구명과 인자가 조회 전용인지 확인한다.
