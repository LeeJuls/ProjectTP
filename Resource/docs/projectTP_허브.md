---
type: moc
project: projectTP
updated: 2026-06-28
---

# 🏠 projectTP 문서 허브

> UE 5.8 HD-2D 정면 대치 배틀 프로젝트의 **문서 진입점(MOC)**.
> 이 볼트(`Resource\docs`)는 언리얼 작업 관련 클로드 문서의 단일 출처다. 새 문서는 여기서 링크로 갈래를 친다.

---

## 📌 현재 상태 (한눈에)

- **✅ S0 아트 선검증 성공!** heroes99 32px 도트 → UE5.8 HD-2D 렌더 확인.

![[HD2D_validation_hero.png]]

- MCP 연결 안정 (`unreal-mcp`, 127.0.0.1:8000). 에디터 켜둔 상태 유지 필요.

### ▶ 검증 결과 요약
- 도트 스프라이트가 3D 어두운 무대에 라이팅·**캐스트 섀도우**와 함께 또렷이 렌더됨. 픽셀퍼펙트(Nearest) 작동. 옥토패스식 디오라마 룩 확보.
- **결론: 이 에셋으로 HD-2D 진행 가능(GO).**

### ▶ 만들어진 것 (재현/이어가기용)
- 합성 캐릭터: `_RawAssets/heroes99/_composed/hero_knight.png` (skin_c1 + cloth15_c1 + hair m5_c7 + weapon1 + face_c1). 스크립트 `_composed/compose2.py`.
- 그리드 규격: **8칸 × 17행, 셀 100×40px** (idle1 = 좌상단 셀).
- UE 에셋: `/Game/Sprites/T_Hero_Knight_Idle1`·`T_Hero_Knight_Sheet`(Nearest/NoMip/UI압축), `/Game/Materials/M_Sprite_Lit`(Masked+양면+Lit), `M_Ground`(다크), `/Game/Meshes/SM_SpriteQuad`·`SM_Ground`.
- 씬: 기본 오픈월드 템플릿의 하늘/라이트 제거 후, **z=10000 고공에 격리된 디오라마**(StageGround/HeroSprite/KeySun/FillSky/StageFog/PPV). PPV: 노출고정 + Bloom0.45 + Vignette0.45 + 채도/대비.

### ▶ 다음 후보 (오너 선택 대기)
- (a) idle **애니메이션**(플립북 6프레임) → 살아있는 느낌
- (b) **AI 적** 배치 → 정면 대치 구도
- (c) 제대로 된 **무대/배경**(소품·라이팅 고도화)
- (d) **다른 캐릭터/복장** 테스트
- (e) 충분 → [[HD2D_PvP_ATB_설계]] 전투 시스템으로

---

## 📚 문서 목록

| 문서 | 내용 | 단계 |
|---|---|---|
| [[작업로그_HD2D아트검증_플레이북]] | **★ 재현 플레이북** — 전 과정·설정·함정·재구축 권장 | 로그 |
| [[ArtMVP_아트선검증_계획]] | 아트 선검증 계획 (S0 완료) | MVP 0 ✅ |
| [[셋업가이드_에디터MCP연결]] | 에디터 실행 & MCP 연결 절차 | 셋업 ✅ |
| [[셋업가이드_새PC환경구축]] | **새 PC 세팅** — 클론·에셋·엔진·MCP 전체 절차 | 셋업 |
| [[HD2D_PvP_ATB_설계]] | 전체 그림 — 실시간 ATB PvP, 서버 권위 네트워킹 | 본설계 |

> 의존 관계: [[ArtMVP_아트선검증_계획]] 통과(Go) → [[HD2D_PvP_ATB_설계]]의 무거운 작업(PvP·네트워킹) 착수.

---

## 🗂 폴더 구조 (확정)

```
D:\unreal\                     ← 워크스페이스 루트
├─ UE_5.8\                     ← 엔진 (불가침)
├─ Resource\                   ← 리소스 + 문서
│  ├─ docs\                    ← 이 볼트 (Obsidian)
│  └─ _RawAssets\heroes99\     ← 구매 zip 풀 곳
└─ projectTP\                  ← UE 프로젝트
   ├─ Config\
   └─ Content\{Sprites,Flipbooks,Materials,Stages,UI}\
```

---

## 🔧 환경 메모

- 엔진: `D:\unreal\UE_5.8` (Paper2D ✅ / GameplayAbilities ✅ / Unreal MCP·Toolset Registry 내장)
- MCP: UE 5.8 공식 Experimental. HTTP `http://127.0.0.1:8000/mcp` (loopback, 무인증). 에디터 안에서 기동.
- 에셋: heroes99 (au-pixel) — $18.75, 상업·수정 가능, 32px 도트 정면. 무료 데모 없음.
- 병행: 오너가 별도 Unity 프로젝트 작업 중 — 충돌 없음(별 엔진/포트). RAM만 주의.

---

## ✅ 결정 로그

- 장르 = A형(정면 대치 턴제). 필드 없음 → heroes99 방향 스프라이트 부재 문제 해소.
- 최종형 = 실시간 ATB **PvP**(사람 vs 사람). 단, **아트 선검증(vs AI, 클라 only)을 먼저**.
- 서버 권위·네트워킹은 후순위(사람이 풀 수 있는 영역으로 판단).
- 프로젝트명 = `projectTP` (※ 임시명 여부 미확정 — 확정 시 폴더/.uproject 동시 변경 필요).
- 문서 관리 = Obsidian 볼트 `Resource\docs`. 엔진 폴더엔 문서 금지.

---

## 📝 컨벤션

- 새 문서는 이 허브에 위키링크로 등록한다(`[[문서명]]`).
- 문서 frontmatter에 `updated:` 날짜 갱신.
- 미결정 사항은 각 문서 하단 "미결정/확정 필요" 섹션에 모은다.
- 코드/에디터 작업이 진척되면 진행 로그를 별도 노트로 떼어 여기 링크.
