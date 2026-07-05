---
type: log
feature: 기본전투무대
phase: P1
agent: art-pipeline
status: 완료
updated: 2026-07-05
---

# P1 — 8종 레시피 · 합성순서 · idle 실측 조사

> 조사 전용 산출물. 실제 합성/임포트는 수행하지 않음. 상위: [[진행로그]] · [[plan]]
#projectTP/기본전투무대

---

## (a) 8종 레시피 표

원본 루트: `D:\unreal\Resource\_RawAssets\heroes99\`. 아래 경로는 모두 루트 기준 상대경로이며, 개별 파일 존재를 실측 확인함(전부 OK).

팀 구분 컨셉: **A팀(아군, 청/한색 계열 cloth 색상 인덱스 위주)** vs **B팀(적, 적/난색 계열 cloth 색상 인덱스 위주)**. 남/여 헤어 세트를 교차 배치해 실루엣 다양성 확보. 각 캐릭터 skin/face 조합도 겹치지 않게 분산.

| ID | 컨셉 | skin | face | hair_bot | hair_top | cloth_bot | cloth_top | weapon_bot | weapon_top |
|---|---|---|---|---|---|---|---|---|---|
| A1 | 남 기사(기존 검증본) | skin/skin_c1.png | face/face_c1.png | hair/m5/m5_bot/m5_c7_bot.png | hair/m5/m5_top/m5_c7_top.png | cloth/cloth15/cloth15_bot/cloth15_c1_bot.png | cloth/cloth15/cloth15_top/cloth15_c1_top.png | weapon/weapon1/weapon1_bot/weapon1_bot.png | weapon/weapon1/weapon1_top/weapon1_top.png |
| A2 | 여 궁수 | skin/skin_c2.png | face/face_c3.png | hair/f3/f3_bot/f3_c3_bot.png | hair/f3/f3_top/f3_c3_top.png | cloth/cloth7/cloth7_bot/cloth7_c2_bot.png | cloth/cloth7/cloth7_top/cloth7_c2_top.png | weapon/weapon2/weapon2_bot/weapon2_bot.png | weapon/weapon2/weapon2_top/weapon2_top.png |
| A3 | 남 창병 | skin/skin_c3.png | face/face_c2.png | hair/m9/m9_bot/m9_c8_bot.png | hair/m9/m9_top/m9_c8_top.png | cloth/cloth3/cloth3_bot/cloth3_c4_bot.png | cloth/cloth3/cloth3_top/cloth3_c4_top.png | weapon/weapon3/weapon3_bot/weapon3_bot.png | weapon/weapon3/weapon3_top/weapon3_top.png |
| A4 | 여 법사 | skin/skin_c1.png | face/face_c4.png | hair/f6/f6_bot/f6_c1_bot.png | hair/f6/f6_top/f6_c1_top.png | cloth/cloth11/cloth11_bot/cloth11_c3_bot.png | cloth/cloth11/cloth11_top/cloth11_c3_top.png | weapon/weapon4/weapon4_bot/weapon4_bot.png | weapon/weapon4/weapon4_top/weapon4_top.png |
| B1 | 남 전사(적) | skin/skin_c4.png | face/face_c5.png | hair/m2/m2_bot/m2_c2_bot.png | hair/m2/m2_top/m2_c2_top.png | cloth/cloth9/cloth9_bot/cloth9_c5_bot.png | cloth/cloth9/cloth9_top/cloth9_c5_top.png | weapon/weapon5/weapon5_bot/weapon5_c2_bot.png | weapon/weapon5/weapon5_top/weapon5_c2_top.png |
| B2 | 여 도적(적) | skin/skin_c5.png | face/face_c6.png | hair/f8/f8_bot/f8_c6_bot.png | hair/f8/f8_top/f8_c6_top.png | cloth/cloth5/cloth5_bot/cloth5_c6_bot.png | cloth/cloth5/cloth5_top/cloth5_c6_top.png | weapon/weapon1/weapon1_bot/weapon1_bot.png | weapon/weapon1/weapon1_top/weapon1_top.png |
| B3 | 남 광전사(적) | skin/skin_c6.png | face/face_c7.png | hair/m12/m12_bot/m12_c9_bot.png | hair/m12/m12_top/m12_c9_top.png | cloth/cloth13/cloth13_bot/cloth13_c7_bot.png | cloth/cloth13/cloth13_top/cloth13_c7_top.png | weapon/weapon2/weapon2_bot/weapon2_bot.png | weapon/weapon2/weapon2_top/weapon2_top.png |
| B4 | 여 사제(적) | skin/skin_c4.png | face/face_c1.png | hair/f1/f1_bot/f1_c5_bot.png | hair/f1/f1_top/f1_c5_top.png | cloth/cloth17/cloth17_bot/cloth17_c8_bot.png | cloth/cloth17/cloth17_top/cloth17_c8_top.png | weapon/weapon3/weapon3_bot/weapon3_bot.png | weapon/weapon3/weapon3_top/weapon3_top.png |

**주의사항(실측 확인됨)**:
- weapon1~4는 색상 변형 없음(파일명에 `_c{n}_` 없음, 예: `weapon1_bot.png`). weapon5만 예외적으로 `_c1~c4_` 색상 변형 존재. B1 무기 경로는 이 예외를 반영(`weapon5_c2_bot.png`).
- cloth 세트는 전 세트 공통 8색(`_c1~c8_`), hair 세트는 전 세트 공통 10색(`_c1~c10_`), skin은 6색, face는 7색.
- 없는 레이어("—")는 이번 8종에는 없음 — heroes99 구조상 hair/cloth/weapon 모두 bot/top 쌍이 항상 존재.

## (b) 합성 순서 확정

`_RawAssets/heroes99/_composed/compose2.py` (≡ `docs/scripts/compose_knight.py`, 동일 내용) 기준, back→front 알파 합성 순서:

1. `hair_bot`
2. `weapon_bot`
3. `cloth_bot`
4. `skin`
5. `face`
6. `cloth_top`
7. `hair_top`
8. `weapon_top`

`PIL.Image.alpha_composite`를 순서대로 누적 적용(`Image.new("RGBA", size, (0,0,0,0))`에서 시작). CLAUDE.md에 명시된 순서와 100% 일치. 캔버스 크기는 첫 레이어 크기를 그대로 사용(=800×680, 8×17 그리드, 셀 100×40).

## (c) idle 애니메이션 실측

**결론: idle은 row 0(0-based), 6프레임(전역 프레임 1~6, 열 0~5). 7·8열은 빈 셀.**
(참고: row 1은 IDLE 2 변형으로 별도 6프레임. 기본전투무대 MVP는 row 0 IDLE 1만 사용 권장)

### 근거 1 — `frameguide_v2.png` (결정적 근거)
heroes99 배포 팩에 포함된 공식 프레임 가이드 이미지(`_RawAssets/heroes99/frameguide_v2.png`)에 각 행의 애니메이션 이름과 전역 프레임 번호가 색상 밴드로 명시되어 있음:
- Row 0: **IDLE 1**, 프레임 1~6 (7·8열 공백)
- Row 1: IDLE 2, 프레임 7~12 (7·8열 공백)
- Row 2: RUN 1, 프레임 13~20 (8프레임, 전열 사용)
- Row 3: RUN 2, 프레임 21~28
- Row 4: JUMP + FALL LOOP, 프레임 29~36
- Row 5~16: ATTACK 1~3 / AIR ATK 1~2 / CASTING 1~2(+CAST LOOP) / HURT / DYING / DASH(+DASH LOOP) / BLOCK / ROLL 순

### 근거 2 — 실제 합성 시트 대조 검증
`_RawAssets/heroes99/_composed/hero_knight.png`(compose2.py 산출물, m5+weapon1+cloth15+skin_c1+face_c1 레시피)를 Pillow로 8×17 그리드 분할 후 셀별 `getbbox()`로 내용 유무 확인:

```
row 0: XXXXXX..   (6프레임, IDLE 1과 일치)
row 1: XXXXXX..   (6프레임, IDLE 2와 일치)
row 2: XXXXXXXX   (8프레임, RUN 1과 일치)
row 3: XXXXXXXX   (8프레임, RUN 2와 일치)
row 4: XXXXXXXX   (8프레임, JUMP+FALL LOOP와 일치)
```

frameguide_v2.png의 행별 프레임 수·공백 패턴과 완전히 일치 → 근거 1·2가 상호 검증됨. 불확실성 없음.

### 대안(참고, 미채택)
IDLE 2(row 1)도 동일 6프레임 구조라 대체 가능. 추후 유휴 상태 변주(대기 오래 지속 시 다른 idle)가 필요해지면 row 1을 2차 idle로 활용 가능.

---

## 다음 단계 제안
- scene-builder P1 조사(무대 배치)와 종합해 [[plan]]에 캐릭터 시트 슬라이스 규격(셀 100×40, idle row 0 col 0~5) + UE 임포트 세팅(Nearest/NoMipmaps/TC_EditorIcon) 명시.
- 실제 합성/슬라이스/임포트는 P1 승인 후 별도 구현 단계에서 수행(본 조사는 실행 없음).
