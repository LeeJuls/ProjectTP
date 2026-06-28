---
type: guide
project: projectTP
updated: 2026-06-28
---

# 새 PC 환경 구축 가이드

> 기존 PC에서 GitHub에 올린 projectTP를 다른 PC에서 동일하게 세팅하는 절차.

---

## 0. 사전 준비 — 필수 설치 목록

| 항목 | 버전 | 비고 |
|---|---|---|
| **Git** | 최신 | https://git-scm.com |
| **Unreal Engine 5.8** | 5.8.x | Epic Games Launcher로 설치 |
| **Visual C++ Redist** | **14.50+** | UE 5.8 필수 — 아래 참조 |
| **Python** | 3.13 | https://python.org (PATH 추가 체크) |
| **Pillow** | 12.x | `pip install Pillow` |

> ⚠ VC++ 14.50 미만이면 에디터가 실행되지 않음.  
> UE 5.8 설치 후 `UE_5.8\Engine\Extras\Redist\en-us\vc_redist.x64.exe` 실행 → 재부팅.

---

## 1. 폴더 구조 먼저 잡기

```
D:\unreal\          ← 워크스페이스 루트 (이 위치 고정 권장)
├─ UE_5.8\          ← Epic Launcher로 설치 (git 외부)
├─ projectTP\       ← git clone 결과 (아래 2번)
└─ Resource\        ← git clone 결과 (아래 2번)
```

> `D:\unreal\` 경로를 그대로 쓰는 걸 권장. 경로가 다르면 `.uproject`의 Engine 연결이 깨질 수 있음.

---

## 2. 저장소 클론

PowerShell 또는 Git Bash에서:

```bash
git clone https://github.com/LeeJuls/ProjectTP.git D:\unreal
```

완료되면 `D:\unreal\` 아래에 `projectTP\`, `Resource\`, `.gitignore`, `README.md` 등이 생김.

---

## 3. UE 5.8 엔진 폴더 배치

Epic Games Launcher → Unreal Engine 5.8 설치 경로를 `D:\unreal\UE_5.8`로 지정.

> 이미 다른 경로에 설치했다면:  
> `projectTP.uproject`의 `"EngineAssociation"` 값을 수정하거나,  
> `.uproject` 파일을 더블클릭 → 엔진 경로 선택 팝업에서 지정.

---

## 4. VC++ 14.50+ 설치

```
D:\unreal\UE_5.8\Engine\Extras\Redist\en-us\vc_redist.x64.exe
```

실행 후 **재부팅** 필수.

---

## 5. heroes99 에셋 설치 (유료 — 재배포 금지)

1. **itch.io** (https://itch.io) → 구매 계정으로 로그인
2. 라이브러리에서 **heroes99** 찾아 다운로드 (`Heroes99_v1.2.zip` 등)
3. 압축을 풀어 아래 경로에 배치:

```
D:\unreal\Resource\_RawAssets\heroes99\
├─ skin\
├─ face\
├─ hair\
├─ cloth\
├─ weapon\
└─ _composed\        ← 직접 만들거나 compose 스크립트로 생성
```

> ⚠ `_RawAssets\`는 `.gitignore`로 git에서 제외됨. 직접 배치해야 함.

---

## 6. 캐릭터 합성 이미지 생성

`_RawAssets\heroes99\_composed\` 폴더가 없으면 직접 만들고, 스크립트 실행:

```bash
cd D:\unreal\Resource\_RawAssets\heroes99
python D:\unreal\Resource\docs\scripts\compose_knight.py
```

> 스크립트 경로가 다르면 `compose_knight.py` 내 `base = "."` 경로 확인.  
> 결과물: `_composed\hero_knight.png`, `_composed\hero_knight_idle1.png`

---

## 7. Python / Pillow 확인

```bash
python --version        # 3.13.x
python -c "from PIL import Image; print('OK')"
```

Pillow 없으면:
```bash
pip install Pillow
```

---

## 8. 에디터 실행 및 MCP 연결

```
D:\unreal\projectTP\_Launch_MCP.bat  ← 더블클릭
```

- 검은 콘솔 창에 `projectTP is RUNNING` 표시되면 정상
- 에디터 완전히 뜰 때까지 대기 (첫 실행 시 셰이더 컴파일 5~15분)
- **이 콘솔 창 절대 닫지 말 것** (MCP 서버 포트 8000이 이 프로세스에 묶여 있음)

---

## 9. Claude Desktop에서 MCP 연결 확인

1. Claude Desktop 실행
2. `D:\unreal\Resource` 폴더에서 Claude Code 세션 시작
3. MCP 승인 팝업이 뜨면 허용
4. `unreal-mcp` 연결 확인 후 작업 시작

---

## 체크리스트

- [ ] Git 설치 완료
- [ ] `D:\unreal` 클론 완료
- [ ] UE 5.8 `D:\unreal\UE_5.8\` 에 설치 완료
- [ ] VC++ 14.50+ 설치 + 재부팅 완료
- [ ] Python 3.13 + Pillow 설치 완료
- [ ] heroes99 `_RawAssets\heroes99\` 에 배치 완료
- [ ] `compose_knight.py` 실행 → `hero_knight_idle1.png` 생성 확인
- [ ] `_Launch_MCP.bat` 실행 → 에디터 기동 확인
- [ ] Claude Desktop MCP 연결 확인
