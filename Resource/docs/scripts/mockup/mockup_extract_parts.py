"""
mockup_extract_parts.py — HD-2D 전투 배경 목업용 소재 추출

목적: Winlu 타일셋(A2/A4/Fantasy_Outside_B/Objects) + heroes99 파티 스프라이트에서
      목업 배경(bg_mockup_v1.png)과 밀도 비교(density_compare.png)에 쓸 "부품"을
      오려내 재사용 가능한 PNG로 저장한다.

⚠ 오토타일 주의: A1~A4 시트는 RPG Maker 오토타일 인코딩이라 격자로 잘라 그냥 이어
   붙이면 깨진다. 여기서는 자동 이어붙임 알고리즘을 구현하지 않고, 블록 안에서
   "전체가 한 재질로 채워진" 48px(또는 144px) 서브영역을 좌표로 직접 지정해 오려낸다.
   좌표는 numpy로 저분산(균일) 타일을 스캔해 찾은 값 + 육안 확인을 거쳤다.

원본(읽기 전용, 유료 에셋 — 절대 수정/유출 금지):
  D:\\unreal\\Resource\\_RawAssets\\tilesets\\Fantasy Exterior - Other Engines\\
  D:\\unreal\\Resource\\_RawAssets\\heroes99\\_composed\\party\\

출력:
  D:\\unreal\\Resource\\_RawAssets\\_mockups\\parts\\
"""
from PIL import Image
import os

TILESET_ROOT = r"D:\unreal\Resource\_RawAssets\tilesets\Fantasy Exterior - Other Engines"
PARTY_DIR = r"D:\unreal\Resource\_RawAssets\heroes99\_composed\party"
OUT_DIR = r"D:\unreal\Resource\_RawAssets\_mockups\parts"


def save(img: Image.Image, name: str):
    path = os.path.join(OUT_DIR, name)
    img.save(path)
    print(f"  SAVED: {name}  size={img.size}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- A2 Terrain: 균일 서브영역 48x48 (오토타일 블록 통짜 크롭, 이어붙임 로직 없음) ---
    a2 = Image.open(os.path.join(TILESET_ROOT, "A2 - Terrain And Misc.png")).convert("RGBA")
    save(a2.crop((96, 0, 144, 48)), "tile_ground_grass_48.png")   # 초록 잔디, std~6.3 (저분산 확인)
    save(a2.crop((96, 480, 144, 528)), "tile_ground_dirt_48.png")  # 갈색 흙길

    # --- A4 Walls: 셀 그리드 = 6col x 8row, 셀 144x144, 48px 투명 거터로 구분 ---
    a4 = Image.open(os.path.join(TILESET_ROOT, "A4 - Walls.png")).convert("RGBA")
    CELL, STEP = 144, 192
    r, c = 2, 2  # 무늬 없는 회색 석벽 (육안 확인: a4_picks.png wallC)
    x0, y0 = c * STEP, r * STEP
    save(a4.crop((x0, y0, x0 + CELL, y0 + CELL)), "tile_wall_stone_144.png")

    # --- Fantasy_Outside_B: 불규칙 배치 시트, 좌표 직접 지정 ---
    b = Image.open(os.path.join(TILESET_ROOT, "Fantasy_Outside_B.png")).convert("RGBA")
    save(b.crop((384, 0, 432, 48)), "tile_wall_merlon_48.png")  # 흉벽 톱니, 48px 단위 반복 확인됨
    tower = b.crop((624, 0, 720, 352))
    tower = tower.crop(tower.getbbox())
    save(tower, "prop_tower_stone.png")

    # --- Objects/!$Big_Trees.png: 나무 3종 (그림자 베이크 포함, 좌표는 열별 알파갭 스캔으로 확정) ---
    trees = Image.open(os.path.join(TILESET_ROOT, "Objects", "!$Big_Trees.png")).convert("RGBA")
    tree_defs = {
        "prop_tree_wide.png": (401, 328, 576, 568),   # 성목(줄기+그림자), 정면 중앙용
        "prop_tree_pine.png": (209, 288, 384, 502),   # 침엽수(그림자 없음), 배경 실루엣용
        "prop_tree_bush.png": (11, 41, 192, 284),     # 관목+바위(그림자 포함), 전경 소품용
    }
    for name, (x0, y0, x1, y1) in tree_defs.items():
        c_ = trees.crop((x0, y0, x1, y1))
        c_ = c_.crop(c_.getbbox())
        save(c_, name)

    # --- heroes99 파티: 4v4 로스터, 셀(0,0)=idle 프레임1을 알파 bbox로 타이트 크롭 ---
    CELL_W, CELL_H = 100, 40
    for pid in ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4"]:
        p = os.path.join(PARTY_DIR, f"T_Party_{pid}.png")
        sheet = Image.open(p).convert("RGBA")
        cell = sheet.crop((0, 0, CELL_W, CELL_H))
        bbox = cell.getbbox()
        tight = cell.crop(bbox)
        save(tight, f"char_{pid}.png")
        print(f"    {pid}: cell_bbox={bbox} char_px={tight.size}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
