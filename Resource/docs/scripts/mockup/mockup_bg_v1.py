"""
mockup_bg_v1.py — HD-2D 전투 배경 목업 v1 (bg_mockup_v1.png)

density_compare.png 판정 결과(캐릭터 2.0x가 가장 균형 잡힌 비율)를 적용해
4v4 전투 무대 시안을 합성한다. 순수 오프라인 Pillow 합성 — 언리얼 미사용.

레이어(뒤->앞): 하늘(그라데이션, 에셋 아님) -> 성탑(0.5x, 벽 뒤에 절반 가림)
  -> 흉벽 톱니(merlon) -> 석벽 밴드(144px) -> 지면(잔디+중앙 흙길)
  -> 나무(좌/우 전경 프레이밍) -> 캐릭터 8기(4v4, 전열/후열 Y어긋남)

⚠ 캐릭터는 idle 프레임(정면 고정) 1종만 추출되어 있어 좌/우 방향 스프라이트가 없다.
  적팀(우측)은 좌우반전으로 "마주보는" 느낌만 흉내냈다 — 정식 방향 스프라이트는
  heroes99 시트의 다른 row(좌/우 방향 프레임)를 슬라이스해야 하며 이번 범위 밖.

입력 부품: D:\\unreal\\Resource\\_RawAssets\\_mockups\\parts\\ (mockup_extract_parts.py 산출물)
출력:      D:\\unreal\\Resource\\_RawAssets\\_mockups\\bg_mockup_v1.png
"""
from PIL import Image, ImageDraw
import os

PARTS_DIR = r"D:\unreal\Resource\_RawAssets\_mockups\parts"
OUT_PATH = r"D:\unreal\Resource\_RawAssets\_mockups\bg_mockup_v1.png"

TILE = 48
W_TILES, H_TILES = 16, 9
NATIVE_W, NATIVE_H = TILE * W_TILES, TILE * H_TILES  # 768x432 (16:9)
DISPLAY_FACTOR = 3  # 최종 가시성용 공통 업스케일

CHAR_SCALE_FRONT = 2.0   # density_compare 판정: 2.0x가 타일 대비 가장 균형
CHAR_SCALE_BACK = 1.7    # 후열은 살짝 작게 -> 원근감

SKY_Y0, SKY_Y1 = 0, 96          # 2 tiles
MERLON_Y0, MERLON_Y1 = 96, 144  # 1 tile
WALL_Y0, WALL_Y1 = 144, 288     # 3 tiles == tile_wall_stone_144 높이와 정확히 일치
GROUND_Y0, GROUND_Y1 = 288, 432  # 3 tiles


def load(name):
    return Image.open(os.path.join(PARTS_DIR, name)).convert("RGBA")


def paste_shadow(canvas, cx, feet_y, w):
    shadow = Image.new("RGBA", (w, w // 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.ellipse([0, 0, w - 1, w // 3 - 1], fill=(10, 10, 10, 90))
    canvas.alpha_composite(shadow, (cx - w // 2, feet_y - w // 6))


def paste_char(canvas, sprite_path, cx, feet_y, scale, flip=False):
    char = load(sprite_path)
    if flip:
        char = char.transpose(Image.FLIP_LEFT_RIGHT)
    cw, ch = char.size
    sw, sh = max(1, round(cw * scale)), max(1, round(ch * scale))
    scaled = char.resize((sw, sh), Image.NEAREST)
    paste_shadow(canvas, cx, feet_y, int(sw * 0.9))
    canvas.alpha_composite(scaled, (cx - sw // 2, feet_y - sh))


def sky_gradient(height):
    # 흉벽(merlon) 톱니 사이 틈으로 비쳐 보여야 하므로 WALL_Y0까지 꽉 채워 그린다
    # (틈 뒤가 검정으로 뚫려 보이는 버그 방지).
    img = Image.new("RGB", (NATIVE_W, height), (0, 0, 0))
    top = (152, 190, 232)
    bot = (216, 227, 232)
    for y in range(height):
        t = y / max(1, height - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(NATIVE_W):
            img.putpixel((x, y), col)
    return img.convert("RGBA")


def main():
    grass = load("tile_ground_grass_48.png")
    dirt = load("tile_ground_dirt_48.png")
    wall = load("tile_wall_stone_144.png")
    merlon = load("tile_wall_merlon_48.png")
    tower = load("prop_tower_stone.png")
    tree_wide = load("prop_tree_wide.png")
    tree_bush = load("prop_tree_bush.png")

    canvas = Image.new("RGBA", (NATIVE_W, NATIVE_H), (0, 0, 0, 0))

    # 1) 하늘 (흉벽 톱니 틈으로 비쳐야 하므로 WALL_Y0 높이까지 채움)
    canvas.alpha_composite(sky_gradient(WALL_Y0), (0, SKY_Y0))

    # 2) 성탑 (0.5x, 벽 뒤에 밑동이 가려지도록 배치)
    tw, th = tower.size
    tscale = 0.5
    tsw, tsh = round(tw * tscale), round(th * tscale)
    tower_s = tower.resize((tsw, tsh), Image.NEAREST)
    tower_bottom_y = WALL_Y0 + 40
    for tx_center in (60, NATIVE_W - 60):
        canvas.alpha_composite(tower_s, (tx_center - tsw // 2, tower_bottom_y - tsh))

    # 3) 흉벽 톱니 (48px 유닛, MERLON 행 전체 타일링)
    for col in range(W_TILES):
        canvas.alpha_composite(merlon, (col * TILE, MERLON_Y0))

    # 4) 석벽 밴드 (144px 폭 유닛 반복, 끝단은 클립)
    x = 0
    while x < NATIVE_W:
        w = min(wall.width, NATIVE_W - x)
        canvas.alpha_composite(wall.crop((0, 0, w, wall.height)), (x, WALL_Y0))
        x += wall.width

    # 5) 지면 (잔디 기본 + 중앙 흙길 패치)
    dirt_cols = range(7, 9)  # 중앙 2열
    for row in range(GROUND_Y0 // TILE, GROUND_Y1 // TILE):
        for col in range(W_TILES):
            tile_img = dirt if col in dirt_cols else grass
            canvas.alpha_composite(tile_img, (col * TILE, row * TILE))

    # 6) 나무 (좌/우 전경 프레이밍, 벽-지면 경계 부근에 밑동)
    lw, lh = tree_wide.size
    lscale = 0.7
    lsw, lsh = round(lw * lscale), round(lh * lscale)
    tree_l = tree_wide.resize((lsw, lsh), Image.NEAREST)
    canvas.alpha_composite(tree_l, (10, GROUND_Y0 + 20 - lsh))

    bw, bh = tree_bush.size
    bscale = 0.65
    bsw, bsh = round(bw * bscale), round(bh * bscale)
    tree_r = tree_bush.resize((bsw, bsh), Image.NEAREST).transpose(Image.FLIP_LEFT_RIGHT)
    canvas.alpha_composite(tree_r, (NATIVE_W - bsw - 8, GROUND_Y0 + 25 - bsh))

    # 7) 캐릭터 4v4 (전열/후열 Y 어긋남, 우측 팀은 좌우반전으로 대치 느낌)
    # 전열(front): feet_y 낮게(가깝게, scale 2.0) / 후열(back): feet_y 높게(멀게, scale 1.7)
    team_a = [
        ("char_A1.png", 120, 420, CHAR_SCALE_FRONT, False),  # 기사(전열)
        ("char_A3.png", 232, 408, CHAR_SCALE_FRONT, False),  # 창병(전열)
        ("char_A2.png", 68, 335, CHAR_SCALE_BACK, False),    # 궁수(후열)
        ("char_A4.png", 188, 345, CHAR_SCALE_BACK, False),   # 법사(후열)
    ]
    team_b = [
        ("char_B1.png", NATIVE_W - 120, 420, CHAR_SCALE_FRONT, True),  # 전사(전열)
        ("char_B3.png", NATIVE_W - 232, 408, CHAR_SCALE_FRONT, True),  # 광전사(전열)
        ("char_B2.png", NATIVE_W - 68, 335, CHAR_SCALE_BACK, True),    # 도적(후열)
        ("char_B4.png", NATIVE_W - 188, 345, CHAR_SCALE_BACK, True),   # 사제(후열)
    ]
    # 뒤에서 앞으로 그려야 전열이 후열을 가리지 않고 자연스럽게 겹침
    for name, cx, feet_y, scale, flip in team_a[2:] + team_b[2:]:  # 후열 먼저
        paste_char(canvas, name, cx, feet_y, scale, flip)
    for name, cx, feet_y, scale, flip in team_a[:2] + team_b[:2]:  # 전열 나중
        paste_char(canvas, name, cx, feet_y, scale, flip)

    # 최종 공통 업스케일 (배경:캐릭터 상대비율 불변, 가시성 확보)
    big = canvas.resize((NATIVE_W * DISPLAY_FACTOR, NATIVE_H * DISPLAY_FACTOR), Image.NEAREST)
    big = big.convert("RGB")
    big.save(OUT_PATH)
    print(f"SAVED: {OUT_PATH} size={big.size} (native {NATIVE_W}x{NATIVE_H} x{DISPLAY_FACTOR})")


if __name__ == "__main__":
    main()
