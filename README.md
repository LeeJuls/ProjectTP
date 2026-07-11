# projectTP — HD-2D 정면 대치 배틀 (UE 5.8)

실시간 ATB **PvP** 정면 대치 턴제 배틀 게임. 캐릭터는 au-pixel **heroes99**(32px 도트)를 HD-2D로 렌더.

## 현재 상태
- ✅ **아트 선검증(S0) 완료** — heroes99 도트가 UE5.8 HD-2D로 잘 나옴을 확인. 결과: `Resource/docs/renders/`
- ⏭ 다음: idle 애니메이션 / AI 적 / 무대 고도화 / 전투 시스템(미정)

## 폴더 구조
```
unreal/
├─ UE_5.8/        ← 엔진 (git 제외, 31GB)
├─ projectTP/     ← UE 프로젝트 (.uproject, Config, _Launch_MCP.bat)
│                   ※ Content/Saved/Intermediate 등 생성물은 git 제외
└─ Resource/
   ├─ .mcp.json   ← Claude Code ↔ Unreal MCP 연결 설정
   ├─ _RawAssets/ ← heroes99 원본 (★유료, git 제외 — 재배포 금지)
   └─ docs/       ← Obsidian 볼트: 설계 문서·플레이북·렌더·스크립트
```

## 문서 (Obsidian 볼트 `Resource/docs`)
- `projectTP_허브.md` — 문서 진입점(MOC)
- `작업로그_HD2D아트검증_플레이북.md` — ★ 재현 플레이북 (전 과정·설정·함정)
- `HD2D_PvP_ATB_설계.md` — 전체 설계 (PvP·네트워킹)
- `ArtMVP_아트선검증_계획.md` / `셋업가이드_에디터MCP연결.md`

## 실행
1. VC++ 14.50+ 필요 (`UE_5.8/Engine/Extras/Redist/en-us/vc_redist.x64.exe`)
2. `projectTP/_Launch_MCP.bat` 실행 → 에디터 + Unreal MCP 서버(:8000)

## ⚠ 라이선스
`heroes99`는 유료 에셋(상업 사용·수정 허용 / **재판매·재배포·NFT·AI학습 금지**). 원본 팩(`Resource/_RawAssets/`, `*.zip`)은 git에서 제외됨.
