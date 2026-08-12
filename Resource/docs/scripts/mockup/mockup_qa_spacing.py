"""
mockup_qa_spacing.py — QA-4 캐릭터 간격을 엔진 실제값으로 (목업_유효범위_판정.md 후속 TC)

qa-critic C6 실측: 목업 캐릭터 간격 363cm vs 엔진 확정 X스텝 150cm = 2.4배 과대.
엔진 좌표 근거: features/옥토패스대치/raw/P1_좌표카메라설계.md 1-2 최종 좌표표
  Party(아군) X ∈ {-600,-450,-300,-150} / Enemy(적) X ∈ {150,300,450,600}, X스텝 150cm.
  각 진영 4기가 "전열/후열 2쌍"이 아니라 X축 위 1열(V자 사선, 중앙에 가까울수록 카메라에 가깝다).

이 스크립트는 mockup_bg_v2.py와 배경/지면/전경/톤 레시피를 동일하게 유지하고
"캐릭터 배치 로직"만 교체한다(변수 분리 — ①의 "텅 빈 벌판" 인상이 간격 과대 착시인지 확인).

환산: 캐릭터 6.48cm/텍셀, CHAR_SCALE_FRONT=2.0 적용 시 캔버스 3.24cm/px(native).
  X스텝 150cm = 150/3.24 = 46.3 native px.
  뒤열축소율: 아군 21.5%, 적 29.4%(P1 문서 실측) — scale(t) = 2.0*(1-shrink*t), t=0(전열/최안쪽)~1(후열/최바깥쪽).

출력: D:\\unreal\\Resource\\_RawAssets\\_mockups\\bg_mockup_qa4_spacing.png (look 버전, v2와 동일 레시피)
      + 인접 캐릭터 실루엣(알파>0) X범위 겹침률을 v2 배치와 비교해 stdout에 출력.
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import numpy as np
import os

PARTS_DIR = r"D:\unreal\Resource\_RawAssets\_mockups\parts"
OUT_DIR = r"D:\unreal\Resource\_RawAssets\_mockups"

NATIVE_W, NATIVE_H = 960, 540
DISPLAY_FACTOR = 2

SKY_Y1 = round(NATIVE_H * 0.20)
FAR_Y1 = round(NATIVE_H * 0.35)
GROUND_Y0 = FAR_Y1
GROUND_Y1 = NATIVE_H

CHAR_SCALE_FRONT = 2.0
CM_PER_PX = 3.24                 # 캔버스 native px당 cm (캐릭터 6.48cm/텍셀 / 2.0x)
X_STEP_CM = 150.0                # 엔진 확정 X스텝
X_STEP_PX = X_STEP_CM / CM_PER_PX  # 46.3 native px
PARTY_BACK_SHRINK = 0.215        # P1 문서: 아군 뒤열축소율
ENEMY_BACK_SHRINK = 0.294        # P1 문서: 적 뒤열축소율

# v2(기존)의 캐릭터 X 간격 재현 — 겹침률 대조용(재측정, 하드코딩 금지 원칙에 따라 v2 좌표 그대로 사용)
V2_TEAM_A_FRONT = [190, 320]     # char_A1, char_A3 (front row, v2 script)
V2_TEAM_A_BACK = [140, 300]      # char_A2, char_A4


def load(name):
    return Image.open(os.path.join(PARTS_DIR, name)).convert("RGBA")


def new_layer():
    return Image.new("RGBA", (NATIVE_W, NATIVE_H), (0, 0, 0, 0))


# ---------- sky/background/midground/foreground : mockup_bg_v2.py와 동일 ----------
def render_sky():
    top = np.array([152, 190, 232], dtype=np.float32)
    bot = np.array([222, 231, 233], dtype=np.float32)
    h = FAR_Y1 + 4
    t = np.linspace(0, 1, h).reshape(h, 1, 1)
    grad = top.reshape(1, 1, 3) + (bot - top).reshape(1, 1, 3) * t
    grad = np.repeat(grad, NATIVE_W, axis=1).astype(np.uint8)
    img = Image.fromarray(grad, "RGB").convert("RGBA")
    canvas = new_layer()
    canvas.alpha_composite(img, (0, 0))
    return canvas


def render_background():
    layer = new_layer()
    wall = load("tile_wall_stone_144.png")
    merlon = load("tile_wall_merlon_48.png")
    tower = load("prop_tower_stone.png")
    far_tree = load("prop_tree_pine.png")

    wall_scale = 0.38
    ww, wh = round(wall.width * wall_scale), round(wall.height * wall_scale)
    wall_s = wall.resize((ww, wh), Image.NEAREST)
    wall_bottom = GROUND_Y0
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
    tower_bottom = wall_top + round(wh * 0.3)
    for cx in (130, NATIVE_W - 130):
        layer.alpha_composite(tower_s, (cx - tsw // 2, tower_bottom - tsh))

    ftw, fth = far_tree.size
    f_scale = 0.20
    fsw, fsh = round(ftw * f_scale), round(fth * f_scale)
    far_tree_s = far_tree.resize((fsw, fsh), Image.NEAREST)
    layer.alpha_composite(far_tree_s, (340 - fsw // 2, wall_bottom - fsh))
    layer.alpha_composite(far_tree_s, (NATIVE_W - 300 - fsw // 2, wall_bottom - fsh))
    return layer


def render_midground():
    layer = new_layer()
    grass = load("tile_ground_grass_48.png")
    dirt = load("tile_ground_dirt_48.png")

    band_h = GROUND_Y1 - GROUND_Y0
    row_heights = [10, 14, 20, 28, 38]
    while sum(row_heights) < band_h:
        row_heights.append(48)
    over = sum(row_heights) - band_h
    if over > 0:
        row_heights[-1] -= over

    n_rows = len(row_heights)
    dirt_rows = {n_rows - 2, n_rows - 1}

    y_cursor = GROUND_Y0
    row_bounds = []
    for i, rh in enumerate(row_heights):
        depth_t = i / max(1, n_rows - 1)
        dark = 0.72 + 0.28 * depth_t
        src = dirt if i in dirt_rows else grass
        tile_slice = src.crop((0, 0, src.width, rh))
        arr = np.array(tile_slice).astype(np.float32)
        arr[..., :3] *= dark
        if i == 0:
            arr[..., 3] *= 0.80
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

    ao_h = 22
    ao = np.zeros((ao_h, NATIVE_W, 4), dtype=np.uint8)
    for yy in range(ao_h):
        a = int(120 * (1 - yy / ao_h))
        ao[yy, :, :3] = 10
        ao[yy, :, 3] = a
    ao_img = Image.fromarray(ao, "RGBA")
    layer.alpha_composite(ao_img, (0, GROUND_Y0))
    return layer, row_bounds


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


# ---------- characters : QA-4 정정 배치 (엔진 실제 X스텝 150cm, V자 1열 4기) ----------
def paste_shadow(layer, cx, feet_y, w):
    h = max(4, w // 3)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.ellipse([0, 0, w - 1, h - 1], fill=(8, 8, 8, 110))
    layer.alpha_composite(shadow, (cx - w // 2, feet_y - h // 2))


def alpha_bbox_width(char_img):
    a = np.array(char_img.split()[-1])
    cols = np.where(a.max(axis=0) > 0)[0]
    return (cols.max() - cols.min() + 1) if len(cols) else char_img.width


def render_characters_qa4(row_bounds):
    """엔진 좌표표 그대로: Party X{-150,-300,-450,-600} / Enemy X{150,300,450,600}, t=0(안쪽/전열)~1(바깥쪽/후열)"""
    layer = new_layer()
    center = NATIVE_W // 2
    front_y = row_bounds[-1][1] - 6
    back_y = row_bounds[len(row_bounds) - 5][0] + 6

    party_x_cm = [-150, -300, -450, -600]
    enemy_x_cm = [150, 300, 450, 600]
    party_files = ["char_A4.png", "char_A3.png", "char_A2.png", "char_A1.png"]  # 안쪽->바깥쪽 순서에 임의 매핑(형태 다양화 목적)
    enemy_files = ["char_B1.png", "char_B2.png", "char_B3.png", "char_B4.png"]

    members = []  # (name, cx, feet_y, scale, flip, t, team)
    for i, (xcm, name) in enumerate(zip(party_x_cm, party_files)):
        t = i / 3.0
        cx = round(center + xcm / CM_PER_PX)
        feet_y = round(front_y + (back_y - front_y) * t)
        scale = CHAR_SCALE_FRONT * (1 - PARTY_BACK_SHRINK * t)
        members.append((name, cx, feet_y, scale, False, t, "A"))
    for i, (xcm, name) in enumerate(zip(enemy_x_cm, enemy_files)):
        t = i / 3.0
        cx = round(center + xcm / CM_PER_PX)
        feet_y = round(front_y + (back_y - front_y) * t)
        scale = CHAR_SCALE_FRONT * (1 - ENEMY_BACK_SHRINK * t)
        members.append((name, cx, feet_y, scale, True, t, "B"))

    def draw_one(name, cx, feet_y, scale, flip):
        char = load(name)
        if flip:
            char = char.transpose(Image.FLIP_LEFT_RIGHT)
        cw, ch = char.size
        sw, sh = max(1, round(cw * scale)), max(1, round(ch * scale))
        scaled = char.resize((sw, sh), Image.NEAREST)
        paste_shadow(layer, cx, feet_y, int(sw * 0.85))
        layer.alpha_composite(scaled, (cx - sw // 2, feet_y - sh))
        return sw

    # 뒤(t 큰 순)부터 그려야 앞(t=0, 카메라 최근접)이 자연스럽게 겹쳐 덮는다
    members_sorted = sorted(members, key=lambda m: -m[5])
    widths = {}
    for name, cx, feet_y, scale, flip, t, team in members_sorted:
        sw = draw_one(name, cx, feet_y, scale, flip)
        widths[(team, round(t, 3))] = (cx, sw)

    return layer, members, widths


def report_overlap(widths, members):
    print("-" * 70)
    print("QA-4 인접 캐릭터 실루엣(alpha bbox) X범위 겹침 — 정정 배치(150cm 스텝)")
    print("-" * 70)
    for team in ("A", "B"):
        team_members = sorted([m for m in members if m[6] == team], key=lambda m: m[5])
        for i in range(len(team_members) - 1):
            t0 = round(team_members[i][5], 3)
            t1 = round(team_members[i + 1][5], 3)
            cx0, w0 = widths[(team, t0)]
            cx1, w1 = widths[(team, t1)]
            l0, r0 = cx0 - w0 / 2, cx0 + w0 / 2
            l1, r1 = cx1 - w1 / 2, cx1 + w1 / 2
            overlap_px = max(0.0, min(r0, r1) - max(l0, l1))
            narrower = min(w0, w1)
            pct = overlap_px / narrower * 100 if narrower else 0
            print(f"  team{team} {team_members[i][0]:14s}<->{team_members[i+1][0]:14s}  "
                  f"cx {cx0:.0f},{cx1:.0f}  width {w0:.0f}px,{w1:.0f}px  overlap={overlap_px:.1f}px ({pct:.0f}% of narrower)")
    print("-" * 70)


def report_v2_baseline():
    """비교 기준: v2 기존 배치(front row 2인) 간격의 겹침률 — 재측정."""
    a1 = load("char_A1.png")
    a3 = load("char_A3.png")
    w1 = alpha_bbox_width(a1) * CHAR_SCALE_FRONT
    w3 = alpha_bbox_width(a3) * CHAR_SCALE_FRONT
    cx0, cx1 = V2_TEAM_A_FRONT
    l0, r0 = cx0 - w1 / 2, cx0 + w1 / 2
    l1, r1 = cx1 - w3 / 2, cx1 + w3 / 2
    overlap_px = max(0.0, min(r0, r1) - max(l0, l1))
    gap_px = max(0.0, max(l0, l1) - min(r0, r1))
    narrower = min(w1, w3)
    step_cm = abs(cx1 - cx0) * CM_PER_PX
    print("=" * 70)
    print(f"v2(기존) 배치 재확인: char_A1<->char_A3 cx간격={abs(cx1-cx0)}px = {step_cm:.0f}cm "
          f"(엔진확정 150cm 대비 {step_cm/150:.2f}배)")
    if overlap_px > 0:
        print(f"  겹침 {overlap_px:.1f}px ({overlap_px/narrower*100:.0f}% of narrower)")
    else:
        print(f"  간격(겹침 없음) {gap_px:.1f}px")
    print("=" * 70)


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
    report_v2_baseline()

    sky = render_sky()
    background = render_background()
    midground, row_bounds = render_midground()
    foreground = render_foreground()
    characters, members, widths = render_characters_qa4(row_bounds)
    report_overlap(widths, members)

    # ⚠ DoF 미적용(오너 확정 off, 옥토패스대치 plan.md L23) — v2 레시피의 배경/전경 GaussianBlur
    # ("DoF 근사")와 그로 인한 seam 블렌드를 QA-4에서는 의도적으로 제거했다. 이 스크립트의 목적은
    # "간격" 단일 변수 격리이므로 DoF 유무까지 v2와 동일하게 맞추면 이번 세션 제약을 어기게 된다.
    # -> QA-4 이미지는 배경/전경이 v2보다 선명하다(간격 비교와는 무관한 차이, 보고서에 명기).
    bg_t = tone(background, 0.40, 0.60, 1.0)
    mid_t = tone(midground, 0.55, 0.75, 1.05)
    mid_t = add_noise_overlay(mid_t, alpha=0.12, blur_radius=50)
    fg_t = tone(foreground, 0.70, 0.85, 1.0)

    canvas2 = new_layer()
    for layer in (sky, bg_t, mid_t, characters, fg_t):
        canvas2.alpha_composite(layer)

    look_rgb = canvas2.convert("RGB")
    look_rgb = apply_vignette(look_rgb, intensity=0.40)
    look_rgb = apply_bloom(look_rgb, opacity=0.18, blur_radius=18, luma_threshold=235)
    look_rgb = ImageEnhance.Contrast(look_rgb).enhance(1.02)
    look_big = look_rgb.resize((NATIVE_W * DISPLAY_FACTOR, NATIVE_H * DISPLAY_FACTOR), Image.NEAREST)
    p2 = os.path.join(OUT_DIR, "bg_mockup_qa4_spacing.png")
    look_big.save(p2)
    print(f"SAVED: {p2} size={look_big.size}")


if __name__ == "__main__":
    main()
