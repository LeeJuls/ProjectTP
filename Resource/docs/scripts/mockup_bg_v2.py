"""
mockup_bg_v2.py — HD-2D 전투 배경 목업 v2 (구도 재설계 + 룩 레시피)

Director 판정(v1 리뷰): "성벽이 화면 60% 점유, 깊이층 없음, 지면 평면, 벽-지면 접합 딱딱,
나무가 벽에 붙음, 흙길이 세로줄무늬" — 전부 v1은 "구도" 문제였고 룩 패스로 못 고친다.
v2는 변수를 분리해서 두 장을 낸다:
  - bg_mockup_v2_nolook.png : 구도만 재설계 (레이어 배치·스케일·접지그림자·지면압축). 톤 无.
  - bg_mockup_v2.png        : 위 레이어에 룩_지침_2D타일셋.md §⑤ 레시피 적용.

레이어 정의 (§⑤ 원안의 "midground=지면+벽"에서, Director의 새 프레임예산에 맞춰
벽/탑을 background(원경)로 재배치 — 벽을 원경으로 보내는 것 자체가 diagnosis #1 해법):
  sky(그라데이션, 톤 미적용) -> background(원경: 성벽·탑·작은 나무, ×0.40/×0.60, blur8)
  -> midground(지면: 압축원근+접지그림자+노이즈, ×0.55/×0.75/×1.05) -> characters(무변경)
  -> foreground(전경 모서리 나무, ×0.70/×0.85, blur3)

원본: D:\\unreal\\Resource\\_RawAssets\\_mockups\\parts\\ (mockup_extract_parts.py 산출물, v1과 공용)
출력: D:\\unreal\\Resource\\_RawAssets\\_mockups\\bg_mockup_v2_nolook.png
      D:\\unreal\\Resource\\_RawAssets\\_mockups\\bg_mockup_v2.png
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import numpy as np
import os

PARTS_DIR = r"D:\unreal\Resource\_RawAssets\_mockups\parts"
OUT_DIR = r"D:\unreal\Resource\_RawAssets\_mockups"

NATIVE_W, NATIVE_H = 960, 540  # 16:9
DISPLAY_FACTOR = 2             # 최종 1920x1080

# 프레임 예산 (Director 지시표)
SKY_Y1 = round(NATIVE_H * 0.20)          # 0-108   하늘 20%
FAR_Y1 = round(NATIVE_H * 0.35)          # 108-189 원경(성벽·탑) 15%p 띠
GROUND_Y0 = FAR_Y1                        # 189
GROUND_Y1 = NATIVE_H                      # 189-540 중경(전투무대) ~65%

CHAR_SCALE_FRONT = 2.0
CHAR_SCALE_BACK = 1.5


def load(name):
    return Image.open(os.path.join(PARTS_DIR, name)).convert("RGBA")


def new_layer():
    return Image.new("RGBA", (NATIVE_W, NATIVE_H), (0, 0, 0, 0))


# ---------- sky ----------
def render_sky():
    top = np.array([152, 190, 232], dtype=np.float32)
    bot = np.array([222, 231, 233], dtype=np.float32)
    h = FAR_Y1 + 4  # 원경 밴드 끝까지 채워 갭 방지
    t = np.linspace(0, 1, h).reshape(h, 1, 1)
    grad = top.reshape(1, 1, 3) + (bot - top).reshape(1, 1, 3) * t
    grad = np.repeat(grad, NATIVE_W, axis=1).astype(np.uint8)
    img = Image.fromarray(grad, "RGB").convert("RGBA")
    canvas = new_layer()
    canvas.alpha_composite(img, (0, 0))
    return canvas


# ---------- background (원경: 성벽/탑/작은 나무) ----------
def render_background():
    layer = new_layer()
    wall = load("tile_wall_stone_144.png")
    merlon = load("tile_wall_merlon_48.png")
    tower = load("prop_tower_stone.png")
    far_tree = load("prop_tree_pine.png")

    wall_scale = 0.38
    ww, wh = round(wall.width * wall_scale), round(wall.height * wall_scale)
    wall_s = wall.resize((ww, wh), Image.NEAREST)
    wall_bottom = GROUND_Y0  # 원경 벽이 지면 시작선(수평선)에 닿음
    wall_top = wall_bottom - wh
    x = 0
    while x < NATIVE_W:
        w = min(ww, NATIVE_W - x)
        layer.alpha_composite(wall_s.crop((0, 0, w, wh)), (x, wall_top))
        x += ww

    merlon_scale = 0.35
    mw, mh = round(merlon.width * merlon_scale), round(merlon.height * merlon_scale)
    merlon_s = merlon.resize((mw, mh), Image.NEAREST)
    x = 0
    while x < NATIVE_W:
        w = min(mw, NATIVE_W - x)
        layer.alpha_composite(merlon_s.crop((0, 0, w, mh)), (x, wall_top - mh))
        x += mw

    tw, th = tower.size
    t_scale = 0.22
    tsw, tsh = round(tw * t_scale), round(th * t_scale)
    tower_s = tower.resize((tsw, tsh), Image.NEAREST)
    tower_bottom = wall_top + round(wh * 0.3)  # 벽 뒤에 밑동이 살짝 가려지도록 겹침
    for cx in (130, NATIVE_W - 130):
        layer.alpha_composite(tower_s, (cx - tsw // 2, tower_bottom - tsh))

    ftw, fth = far_tree.size
    f_scale = 0.20
    fsw, fsh = round(ftw * f_scale), round(fth * f_scale)
    far_tree_s = far_tree.resize((fsw, fsh), Image.NEAREST)
    layer.alpha_composite(far_tree_s, (340 - fsw // 2, wall_bottom - fsh))
    layer.alpha_composite(far_tree_s, (NATIVE_W - 300 - fsw // 2, wall_bottom - fsh))

    return layer


# ---------- midground (지면: 압축 원근 + 접지그림자 + 흙길) ----------
def render_midground():
    layer = new_layer()
    grass = load("tile_ground_grass_48.png")
    dirt = load("tile_ground_dirt_48.png")

    band_h = GROUND_Y1 - GROUND_Y0
    # 압축 원근: 먼(벽쪽) 줄은 얇게 크롭, 가까운(카메라쪽) 줄은 48px 원본 그대로.
    # 리사이즈(블러 유발) 대신 "타일 상단을 얇게 잘라 쌓기"로 압축 — 도트 뭉개짐 없음.
    row_heights = [10, 14, 20, 28, 38]
    while sum(row_heights) < band_h:
        row_heights.append(48)
    # 마지막 줄 클립
    over = sum(row_heights) - band_h
    if over > 0:
        row_heights[-1] -= over

    n_rows = len(row_heights)
    dirt_rows = {n_rows - 2, n_rows - 1}  # 맨 앞 두 줄 = 전열 캐릭터 발밑을 가로로 지나가는 흙길

    y_cursor = GROUND_Y0
    row_bounds = []  # (y0,y1) per row for later use (character feet 정렬용)
    for i, rh in enumerate(row_heights):
        depth_t = i / max(1, n_rows - 1)  # 0=제일 먼 줄, 1=제일 가까운 줄
        dark = 0.72 + 0.28 * depth_t  # 뒤(먼 줄)일수록 어둡게 -> 원근 깊이 단서(구도 단계에서 처리)
        src = dirt if i in dirt_rows else grass
        tile_slice = src.crop((0, 0, src.width, rh))
        # 어둡게: RGB만 곱연산, 알파 유지
        arr = np.array(tile_slice).astype(np.float32)
        arr[..., :3] *= dark
        if i == 0:
            arr[..., 3] *= 0.80  # 지평선 접점 살짝 반투명 -> 원경 블러(DoF)가 은은히 비쳐 경계 하드컷 완화
        elif i == 1:
            arr[..., 3] *= 0.92
        tile_dark = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
        x = 0
        while x < NATIVE_W:
            w = min(tile_dark.width, NATIVE_W - x)
            layer.alpha_composite(tile_dark.crop((0, 0, w, rh)), (x, y_cursor))
            x += tile_dark.width
        row_bounds.append((y_cursor, y_cursor + rh))
        y_cursor += rh

    # 벽-지면 접지 그림자(AO): 지면 맨 윗쪽에 부드러운 어두운 그라데이션 오버레이
    ao_h = 22
    ao = np.zeros((ao_h, NATIVE_W, 4), dtype=np.uint8)
    for yy in range(ao_h):
        a = int(120 * (1 - yy / ao_h))
        ao[yy, :, :3] = 10
        ao[yy, :, 3] = a
    ao_img = Image.fromarray(ao, "RGBA")
    layer.alpha_composite(ao_img, (0, GROUND_Y0))

    return layer, row_bounds


# ---------- foreground (전경 모서리 나무, 크게·잘리게) ----------
def render_foreground():
    layer = new_layer()
    tree_l = load("prop_tree_wide.png")
    tree_r = load("prop_tree_bush.png")

    lscale = 1.5
    lw, lh = round(tree_l.width * lscale), round(tree_l.height * lscale)
    tl = tree_l.resize((lw, lh), Image.NEAREST)
    layer.alpha_composite(tl, (-round(lw * 0.30), NATIVE_H - lh + 12))

    rscale = 1.35
    rw, rh = round(tree_r.width * rscale), round(tree_r.height * rscale)
    tr = tree_r.resize((rw, rh), Image.NEAREST).transpose(Image.FLIP_LEFT_RIGHT)
    layer.alpha_composite(tr, (NATIVE_W - rw + round(rw * 0.30), NATIVE_H - rh + 18))

    return layer


# ---------- characters ----------
def paste_shadow(layer, cx, feet_y, w):
    h = max(4, w // 3)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.ellipse([0, 0, w - 1, h - 1], fill=(8, 8, 8, 110))
    layer.alpha_composite(shadow, (cx - w // 2, feet_y - h // 2))


def render_characters(row_bounds):
    layer = new_layer()
    back_y = row_bounds[len(row_bounds) - 5][0] + 6   # 압축존 끝난 직후 = 후열 라인
    front_y = row_bounds[-1][1] - 6                     # 맨 앞줄 = 전열 라인

    team_a = [
        ("char_A1.png", 190, front_y, CHAR_SCALE_FRONT, False),
        ("char_A3.png", 320, front_y - 8, CHAR_SCALE_FRONT, False),
        ("char_A2.png", 140, back_y, CHAR_SCALE_BACK, False),
        ("char_A4.png", 300, back_y + 10, CHAR_SCALE_BACK, False),
    ]
    team_b = [
        ("char_B1.png", NATIVE_W - 190, front_y, CHAR_SCALE_FRONT, True),
        ("char_B3.png", NATIVE_W - 320, front_y - 8, CHAR_SCALE_FRONT, True),
        ("char_B2.png", NATIVE_W - 140, back_y, CHAR_SCALE_BACK, True),
        ("char_B4.png", NATIVE_W - 300, back_y + 10, CHAR_SCALE_BACK, True),
    ]

    def draw_one(name, cx, feet_y, scale, flip):
        char = load(name)
        if flip:
            char = char.transpose(Image.FLIP_LEFT_RIGHT)
        cw, ch = char.size
        sw, sh = max(1, round(cw * scale)), max(1, round(ch * scale))
        scaled = char.resize((sw, sh), Image.NEAREST)
        paste_shadow(layer, cx, feet_y, int(sw * 0.85))
        layer.alpha_composite(scaled, (cx - sw // 2, feet_y - sh))

    for name, cx, feet_y, scale, flip in team_a[2:] + team_b[2:]:  # 후열 먼저
        draw_one(name, cx, feet_y, scale, flip)
    for name, cx, feet_y, scale, flip in team_a[:2] + team_b[:2]:  # 전열 나중
        draw_one(name, cx, feet_y, scale, flip)

    return layer


# ---------- 톤/이펙트 헬퍼 (룩 레시피, look 버전에서만 사용) ----------
def tone(img_rgba, brightness=1.0, saturation=1.0, contrast=1.0):
    r, g, b, a = img_rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def add_noise_overlay(img_rgba, alpha=0.12, blur_radius=50):
    r, g, b, a = img_rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    noise = np.random.randint(0, 255, (NATIVE_H, NATIVE_W, 3), dtype=np.uint8)
    noise_img = Image.fromarray(noise, "RGB").filter(ImageFilter.GaussianBlur(blur_radius))
    blended = Image.blend(rgb, noise_img, alpha)
    r2, g2, b2 = blended.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def apply_vignette(img_rgb, intensity=0.40):
    arr = np.array(img_rgb).astype(np.float32)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    max_d = np.sqrt(cx ** 2 + cy ** 2)
    dist_norm = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max_d
    factor = 1 - intensity * (dist_norm ** 2)
    arr *= factor[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def apply_bloom(img_rgb, opacity=0.18, blur_radius=18, luma_threshold=235):
    # ⚠ percentile 기준은 "화면의 밝은 영역(하늘 등)"을 통째로 블룸 소스로 잡아
    #   경계에 밝은 헤일로 선이 생기는 버그가 났다(실측). 실제 하이라이트(거의 흰색)만
    #   골라야 하므로 절대 휘도 임계값으로 교체.
    arr = np.array(img_rgb).astype(np.float32)
    luma = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    mask = (luma >= luma_threshold)[..., None]
    bright = (arr * mask).astype(np.uint8)
    bright_img = Image.fromarray(bright, "RGB").filter(ImageFilter.GaussianBlur(blur_radius))
    b = np.array(bright_img).astype(np.float32)
    base = arr
    screen = 255 - (255 - base) * (255 - b) / 255
    out = base * (1 - opacity) + screen * opacity
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    sky = render_sky()
    background = render_background()
    midground, row_bounds = render_midground()
    foreground = render_foreground()
    characters = render_characters(row_bounds)

    # ---- ① nolook: 구도만, 톤 처리 없이 그대로 합성 ----
    canvas = new_layer()
    for layer in (sky, background, midground, characters, foreground):
        canvas.alpha_composite(layer)
    nolook_rgb = canvas.convert("RGB")
    nolook_big = nolook_rgb.resize((NATIVE_W * DISPLAY_FACTOR, NATIVE_H * DISPLAY_FACTOR), Image.NEAREST)
    p1 = os.path.join(OUT_DIR, "bg_mockup_v2_nolook.png")
    nolook_big.save(p1)
    print(f"SAVED: {p1} size={nolook_big.size}")

    # ---- ② look: §⑤ 레시피 적용 ----
    bg_t = tone(background, 0.40, 0.60, 1.0)
    bg_t = bg_t.filter(ImageFilter.GaussianBlur(8))
    mid_t = tone(midground, 0.55, 0.75, 1.05)
    mid_t = add_noise_overlay(mid_t, alpha=0.12, blur_radius=50)
    fg_t = tone(foreground, 0.70, 0.85, 1.0)
    fg_t = fg_t.filter(ImageFilter.GaussianBlur(3))
    chars_t = characters  # 무변경

    canvas2 = new_layer()
    for layer in (sky, bg_t, mid_t, chars_t, fg_t):
        canvas2.alpha_composite(layer)

    # 지평선(벽-지면) 접합부 국소 블러: 블러된 원경 <-> 선명한 지면이 칼같이 붙는
    # 마하밴드(경계 과대비 착시) 완화. 이 좁은 띠만 살짝 더 섞어 하드컷 인상을 지운다.
    seam_pad = 16
    seam_box = (0, GROUND_Y0 - seam_pad, NATIVE_W, GROUND_Y0 + seam_pad)
    seam_crop = canvas2.crop(seam_box).filter(ImageFilter.GaussianBlur(4))
    canvas2.paste(seam_crop, seam_box)

    look_rgb = canvas2.convert("RGB")
    look_rgb = apply_vignette(look_rgb, intensity=0.40)
    look_rgb = apply_bloom(look_rgb, opacity=0.18, blur_radius=18, luma_threshold=235)
    look_rgb = ImageEnhance.Contrast(look_rgb).enhance(1.02)  # §⑤ step6 약한 전역 보정만
    look_big = look_rgb.resize((NATIVE_W * DISPLAY_FACTOR, NATIVE_H * DISPLAY_FACTOR), Image.NEAREST)
    p2 = os.path.join(OUT_DIR, "bg_mockup_v2.png")
    look_big.save(p2)
    print(f"SAVED: {p2} size={look_big.size}")


if __name__ == "__main__":
    main()
