"""
mockup_density_compare.py — 픽셀 밀도 비교 시안 (density_compare.png)

목적: heroes99 캐릭터(도트 굵음, idle 프레임 alpha-bbox 실측 ~23x27px)와
      Winlu 타일셋(48px 그리드, 도트 잚)을 같은 화면에 놓았을 때 "어느 배율이
      맞는가"를 눈으로 판정하기 위한 비교표. 타일은 항상 네이티브 48px 그대로
      두고, 캐릭터만 nearest-neighbor로 1.0x / 1.5x / 2.0x 스케일해 나란히 배치한다.

입력 부품(선행 스크립트 mockup_extract_parts.py 산출물):
  D:\\unreal\\Resource\\_RawAssets\\_mockups\\parts\\tile_ground_grass_48.png
  D:\\unreal\\Resource\\_RawAssets\\_mockups\\parts\\char_A1.png (기사, 23x27px)

출력:
  D:\\unreal\\Resource\\_RawAssets\\_mockups\\density_compare.png
"""
from PIL import Image, ImageDraw, ImageFont
import os

PARTS_DIR = r"D:\unreal\Resource\_RawAssets\_mockups\parts"
OUT_PATH = r"D:\unreal\Resource\_RawAssets\_mockups\density_compare.png"

TILE = 48
COLS, ROWS = 4, 3           # native ground grid per panel
DISPLAY_FACTOR = 5          # 최종 가시성용 공통 업스케일 (타일/캐릭터 동일 적용 -> 상대비율 불변)
SCALES = [1.0, 1.5, 2.0]

FONT_PATH = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD_PATH = r"C:\Windows\Fonts\arialbd.ttf"


def build_panel(grass: Image.Image, char: Image.Image, scale: float) -> Image.Image:
    native_w, native_h = TILE * COLS, TILE * ROWS
    canvas = Image.new("RGBA", (native_w, native_h), (0, 0, 0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            canvas.paste(grass, (col * TILE, row * TILE))

    cw, ch = char.size
    sw, sh = max(1, round(cw * scale)), max(1, round(ch * scale))
    char_scaled = char.resize((sw, sh), Image.NEAREST)

    feet_y = TILE * (ROWS - 1)  # 뒤 1줄 남기고 앞 2줄 경계에 발 위치
    fx = native_w // 2 - sw // 2
    fy = feet_y - sh
    canvas.alpha_composite(char_scaled, (fx, fy))

    # 공통 업스케일 (타일:캐릭터 상대 비율 불변 — 가시성만 확보)
    big = canvas.resize((native_w * DISPLAY_FACTOR, native_h * DISPLAY_FACTOR), Image.NEAREST)

    # 48px 타일 경계 그리드 오버레이
    draw = ImageDraw.Draw(big)
    for col in range(COLS + 1):
        x = col * TILE * DISPLAY_FACTOR
        draw.line([(x, 0), (x, big.height)], fill=(0, 0, 0, 70), width=1)
    for row in range(ROWS + 1):
        y = row * TILE * DISPLAY_FACTOR
        draw.line([(0, y), (big.width, y)], fill=(0, 0, 0, 70), width=1)

    return big, sw, sh


def main():
    grass = Image.open(os.path.join(PARTS_DIR, "tile_ground_grass_48.png")).convert("RGBA")
    char = Image.open(os.path.join(PARTS_DIR, "char_A1.png")).convert("RGBA")
    cw, ch = char.size
    print(f"reference char (A1 knight) native px: {cw}x{ch}")

    font_title = ImageFont.truetype(FONT_BOLD_PATH, 30)
    font_label = ImageFont.truetype(FONT_BOLD_PATH, 26)
    font_small = ImageFont.truetype(FONT_PATH, 20)

    panels = []
    for scale in SCALES:
        big, sw, sh = build_panel(grass, char, scale)
        panels.append((scale, big, sw, sh))

    margin = 40
    gap = 30
    label_h = 90
    title_h = 70
    panel_w, panel_h = panels[0][1].size

    total_w = margin * 2 + panel_w * len(panels) + gap * (len(panels) - 1)
    total_h = margin + title_h + panel_h + label_h + margin

    out = Image.new("RGBA", (total_w, total_h), (235, 235, 230, 255))
    draw = ImageDraw.Draw(out)

    title = "Density Compare — tile 48px (native, fixed) x character 1.0 / 1.5 / 2.0x (nearest-neighbor)"
    draw.text((margin, margin // 2), title, fill=(20, 20, 20, 255), font=font_title)

    x = margin
    y = margin + title_h
    for scale, big, sw, sh in panels:
        out.alpha_composite(big, (x, y))
        label1 = f"{scale:.1f}x"
        label2 = f"char {sw}x{sh}px (native {cw}x{ch})"
        draw.text((x, y + panel_h + 8), label1, fill=(10, 10, 10, 255), font=font_label)
        draw.text((x, y + panel_h + 44), label2, fill=(60, 60, 60, 255), font=font_small)
        x += panel_w + gap

    footer = "grid line = 48px tile boundary | ground: A2 grass tile (native) | character: hero_knight(A1) idle frame1, alpha-bbox"
    draw.text((margin, total_h - margin // 2 - 4), footer, fill=(80, 80, 80, 255), font=font_small)

    out = out.convert("RGB")
    out.save(OUT_PATH)
    print(f"SAVED: {OUT_PATH} size={out.size}")


if __name__ == "__main__":
    main()
