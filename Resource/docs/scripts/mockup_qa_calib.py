"""
mockup_qa_calib.py — QA-1/QA-2 캘리브레이션 대조 (목업_유효범위_판정.md 후속 TC)

목적: 룩_지침_2D타일셋.md §⑤ 레시피가 "언리얼 결과를 예측할 능력이 있는가"를 수치로 검증한다.
qa-critic 판정(C1/C2)의 핵심 주장 — "Pillow는 sRGB 8비트에 곱하고 UE는 리니어에 곱해
같은 0.55가 감마만으로 2.1배, 라이팅 포함 5~9배 차이" — 를 실제 기준 렌더와 대조해 재현한다.

절차:
  1) 기준 실측: docs/renders/HD2D_validation_wide.png 에서 지면 sRGB 평균 + 캐릭터 sRGB 평균(참고) 측정.
     지면 측정은 캐릭터/암반(rock) 실루엣을 피한 순수 지면 밴드에서.
  2) QA-1: 동일 입력(다크 지면 BaseColor 0.03 균일 + heroes99 캐릭터, 배경 검정)을 만들고
     §⑤ midground 레시피(Brightness×0.55→Saturation×0.75→Contrast×1.05 + 노이즈오버레이)를
     "그대로" 태운 뒤, 프레임 전역 효과(비네트0.40, 절제블룸, 전역Contrast×1.02)까지 적용.
     결과 지면 sRGB 평균을 기준 실측과 비교(±10%).
  3) QA-2 (QA-1 실패 시): 브라이트니스 곱연산을 sRGB 인코딩 공간이 아니라 리니어 공간에서 수행하도록
     교체한 버전을 다시 측정 — 일치도가 개선되는지 확인.

⚠ DoF 미적용(오너 확정 off, 옥토패스대치 plan.md L23). 이 스크립트는 벽/하늘/나무 등 §⑤의
   background/foreground 레이어를 포함하지 않는다 — 과제 지시대로 "다크 지면 + heroes99 캐릭터"만.

출력: D:\\unreal\\Resource\\_RawAssets\\_mockups\\calib_compare.png
      (기준 실측 크롭 | QA-1 오프라인 재현 | QA-2 리니어공간 재현, 각각 수치 라벨)
      + 측정값 표를 stdout에 출력.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np
import os

RENDER_PATH = r"D:\unreal\Resource\docs\renders\HD2D_validation_wide.png"
PARTS_DIR = r"D:\unreal\Resource\_RawAssets\_mockups\parts"
OUT_DIR = r"D:\unreal\Resource\_RawAssets\_mockups"
OUT_PATH = os.path.join(OUT_DIR, "calib_compare.png")

NATIVE_W, NATIVE_H = 960, 540
GROUND_START_FRAC = 465 / 983  # 기준 렌더 실측 수평선 비율(캐릭터/지면 경계)
DISPLAY_FACTOR = 2

# §⑤ midground 레시피 수치 (룩_지침_2D타일셋.md §⑤-1 표)
MID_BRIGHTNESS = 0.55
MID_SATURATION = 0.75
MID_CONTRAST = 1.05
NOISE_ALPHA = 0.12
NOISE_BLUR = 50
VIGNETTE_INTENSITY = 0.40
BLOOM_OPACITY = 0.18
BLOOM_BLUR = 18
BLOOM_LUMA_THRESHOLD = 235
GLOBAL_CONTRAST = 1.02

M_GROUND_BASECOLOR_LINEAR = 0.03  # 작업로그_HD2D아트검증_플레이북 — M_Ground 다크 Constant3Vector


# ---------------- sRGB <-> Linear (numpy, float 0..1) ----------------
def srgb_to_linear(u8):
    x = u8.astype(np.float64) / 255.0
    lo = x <= 0.04045
    lin = np.where(lo, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
    return lin


def linear_to_srgb_u8(lin):
    lin = np.clip(lin, 0.0, 1.0)
    lo = lin <= 0.0031308
    s = np.where(lo, lin * 12.92, 1.055 * (lin ** (1 / 2.4)) - 0.055)
    return np.clip(s * 255.0, 0, 255).astype(np.uint8)


def scalar_linear_to_srgb_u8(v):
    return int(linear_to_srgb_u8(np.array([v]))[0])


# ---------------- 1) 기준 실측 ----------------
def measure_reference():
    img = Image.open(RENDER_PATH).convert("RGB")
    arr = np.array(img).astype(np.float64)
    h, w, _ = arr.shape

    # 지면: 캐릭터(대략 x 0.46~0.80)와 암반(y_frac<0.49)을 피한 순수 지면 밴드
    y0, y1 = int(0.49 * h), int(0.56 * h)
    x_left = arr[y0:y1, 0:int(0.40 * w)]
    x_right = arr[y0:y1, int(0.85 * w):w]
    ground_px = np.concatenate([x_left.reshape(-1, 3), x_right.reshape(-1, 3)], axis=0)
    ground_srgb_mean = ground_px.mean(axis=0)
    ground_lin = srgb_to_linear(ground_px.astype(np.uint8))
    ground_lin_mean = ground_lin.mean(axis=0)
    br_linear = ground_lin_mean[2] / ground_lin_mean[0]

    # 캐릭터: bbox 휴리스틱(참고용, 배경 검정/지면 일부 혼입 가능 — 캐비아트)
    cx0, cx1 = int(0.46 * w), int(0.80 * w)
    cy0, cy1 = int(0.10 * h), int(0.73 * h)
    cbox = arr[cy0:cy1, cx0:cx1].reshape(-1, 3)
    non_black = cbox[cbox.sum(axis=1) > 25]  # 순수 검정 배경 픽셀 제외
    char_srgb_mean = non_black.mean(axis=0)

    return {
        "ground_srgb": ground_srgb_mean,
        "ground_br_linear": br_linear,
        "char_srgb": char_srgb_mean,
        "img": img,
        "crop_box": (int(0.30 * w), int(0.0 * h), int(0.95 * w), int(0.98 * h)),
    }


# ---------------- §⑤ 레시피 헬퍼 (mockup_bg_v2.py 동일 구현 재사용) ----------------
def load_char(name):
    return Image.open(os.path.join(PARTS_DIR, name)).convert("RGBA")


def tone_srgb(img_rgba, brightness=1.0, saturation=1.0, contrast=1.0):
    r, g, b, a = img_rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def brightness_linear(img_rgba, factor):
    """QA-2: sRGB 인코딩 곱연산이 아니라 리니어 공간에서 곱연산."""
    r, g, b, a = img_rgba.split()
    rgb = np.array(Image.merge("RGB", (r, g, b)))
    lin = srgb_to_linear(rgb)
    lin *= factor
    out = linear_to_srgb_u8(lin)
    rgb2 = Image.fromarray(out, "RGB")
    r2, g2, b2 = rgb2.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def add_noise_overlay(img_rgba, alpha=NOISE_ALPHA, blur_radius=NOISE_BLUR):
    r, g, b, a = img_rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    w, h = rgb.size
    noise = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
    noise_img = Image.fromarray(noise, "RGB").filter(ImageFilter.GaussianBlur(blur_radius))
    blended = Image.blend(rgb, noise_img, alpha)
    r2, g2, b2 = blended.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def apply_vignette(img_rgb, intensity=VIGNETTE_INTENSITY):
    arr = np.array(img_rgb).astype(np.float32)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    max_d = np.sqrt(cx ** 2 + cy ** 2)
    dist_norm = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max_d
    factor = 1 - intensity * (dist_norm ** 2)
    arr *= factor[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def apply_bloom(img_rgb, opacity=BLOOM_OPACITY, blur_radius=BLOOM_BLUR, luma_threshold=BLOOM_LUMA_THRESHOLD):
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


# ---------------- 2) QA-1 / QA-2 오프라인 재현 ----------------
def build_scene(mid_brightness_mode="srgb"):
    """다크 지면(BaseColor 0.03, 배경 검정) + heroes99 캐릭터(무변경) 를 §⑤ 그대로 태운다.
    mid_brightness_mode: 'srgb' = Pillow 기본(ImageEnhance, QA-1) / 'linear' = 리니어 곱연산(QA-2)
    """
    canvas = Image.new("RGBA", (NATIVE_W, NATIVE_H), (0, 0, 0, 255))  # 배경 검정(기준 렌더의 빈 스테이지와 동일)

    ground_y0 = round(NATIVE_H * GROUND_START_FRAC)
    base_srgb = scalar_linear_to_srgb_u8(M_GROUND_BASECOLOR_LINEAR)  # 0.03 lin -> ~48 sRGB
    ground = Image.new("RGBA", (NATIVE_W, NATIVE_H - ground_y0), (base_srgb, base_srgb, base_srgb, 255))

    # §⑤ midground 레시피 그대로
    if mid_brightness_mode == "srgb":
        ground_t = tone_srgb(ground, MID_BRIGHTNESS, MID_SATURATION, MID_CONTRAST)
    else:
        r, g, b, a = ground.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Color(rgb).enhance(MID_SATURATION)
        rgb = ImageEnhance.Contrast(rgb).enhance(MID_CONTRAST)
        r2, g2, b2 = rgb.split()
        ground_mid = Image.merge("RGBA", (r2, g2, b2, a))
        ground_t = brightness_linear(ground_mid, MID_BRIGHTNESS)
    ground_t = add_noise_overlay(ground_t)

    canvas.alpha_composite(ground_t, (0, ground_y0))

    # 캐릭터: heroes99, 무변경(1.0/1.0/1.0), 기준 렌더와 비슷한 중앙 배치
    char = load_char("char_A1.png")
    scale = 6.0  # 기준 렌더 프레이밍(캐릭터가 화면의 상당 부분 차지)에 근사
    cw, ch = char.size
    sw, sh = round(cw * scale), round(ch * scale)
    char_s = char.resize((sw, sh), Image.NEAREST)
    cx = NATIVE_W // 2
    feet_y = ground_y0 + round((NATIVE_H - ground_y0) * 0.42)
    canvas.alpha_composite(char_s, (cx - sw // 2, feet_y - sh))
    char_box = (cx - sw // 2, feet_y - sh, cx + sw // 2, feet_y)

    # 전역 효과 (§⑤ step 4: 비네트 -> 절제블룸 -> 전역Contrast, DoF 미적용)
    rgb = canvas.convert("RGB")
    rgb = apply_vignette(rgb, VIGNETTE_INTENSITY)
    rgb = apply_bloom(rgb, BLOOM_OPACITY, BLOOM_BLUR, BLOOM_LUMA_THRESHOLD)
    rgb = ImageEnhance.Contrast(rgb).enhance(GLOBAL_CONTRAST)

    return rgb, ground_y0, char_box


def measure_scene(rgb, ground_y0, char_box):
    arr = np.array(rgb).astype(np.float64)
    h, w, _ = arr.shape
    cx0, cy0, cx1, cy1 = char_box

    # 지면: 캐릭터 좌우, 기준 렌더와 동일한 상대 y밴드(수평선 바로 아래 7%p)
    y0 = ground_y0 + round(0.02 * (h - ground_y0))
    y1 = ground_y0 + round(0.09 * (h - ground_y0))
    left = arr[y0:y1, 0:max(1, cx0 - 4)]
    right = arr[y0:y1, min(w - 1, cx1 + 4):w]
    ground_px = np.concatenate([left.reshape(-1, 3), right.reshape(-1, 3)], axis=0)
    ground_srgb_mean = ground_px.mean(axis=0)
    ground_lin = srgb_to_linear(ground_px.astype(np.uint8))
    ground_lin_mean = ground_lin.mean(axis=0)
    br_linear = ground_lin_mean[2] / ground_lin_mean[0] if ground_lin_mean[0] > 1e-9 else float("nan")

    char_crop = arr[max(0, cy0):cy1, max(0, cx0):cx1].reshape(-1, 3)
    non_black = char_crop[char_crop.sum(axis=1) > 25]
    char_srgb_mean = non_black.mean(axis=0) if len(non_black) else np.array([0, 0, 0])

    return ground_srgb_mean, br_linear, char_srgb_mean


def pct_dev(offline, real):
    return (offline - real) / real * 100.0


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ref = measure_reference()

    # QA-1
    qa1_rgb, gy0, cbox = build_scene(mid_brightness_mode="srgb")
    qa1_ground, qa1_br, qa1_char = measure_scene(qa1_rgb, gy0, cbox)

    # QA-2
    qa2_rgb, gy0_2, cbox_2 = build_scene(mid_brightness_mode="linear")
    qa2_ground, qa2_br, qa2_char = measure_scene(qa2_rgb, gy0_2, cbox_2)

    dev1 = pct_dev(qa1_ground, ref["ground_srgb"])
    dev2 = pct_dev(qa2_ground, ref["ground_srgb"])
    pass1 = np.all(np.abs(dev1) <= 10.0)
    pass2 = np.all(np.abs(dev2) <= 10.0)

    print("=" * 78)
    print("QA-1/QA-2 캘리브레이션 측정값 표")
    print("=" * 78)
    print(f"{'':22s} {'R':>8s} {'G':>8s} {'B':>8s} {'B/R(lin)':>10s}")
    print(f"{'기준 실측(엔진)':22s} {ref['ground_srgb'][0]:8.2f} {ref['ground_srgb'][1]:8.2f} {ref['ground_srgb'][2]:8.2f} {ref['ground_br_linear']:10.3f}")
    print(f"{'QA-1(sRGB곱, 지면)':22s} {qa1_ground[0]:8.2f} {qa1_ground[1]:8.2f} {qa1_ground[2]:8.2f} {qa1_br:10.3f}")
    print(f"{'  편차%':22s} {dev1[0]:7.1f}% {dev1[1]:7.1f}% {dev1[2]:7.1f}%")
    print(f"{'QA-2(리니어곱, 지면)':22s} {qa2_ground[0]:8.2f} {qa2_ground[1]:8.2f} {qa2_ground[2]:8.2f} {qa2_br:10.3f}")
    print(f"{'  편차%':22s} {dev2[0]:7.1f}% {dev2[1]:7.1f}% {dev2[2]:7.1f}%")
    print("-" * 78)
    print(f"{'기준 실측(캐릭터,참고)':22s} {ref['char_srgb'][0]:8.2f} {ref['char_srgb'][1]:8.2f} {ref['char_srgb'][2]:8.2f}")
    print(f"{'QA-1(캐릭터,무변경)':22s} {qa1_char[0]:8.2f} {qa1_char[1]:8.2f} {qa1_char[2]:8.2f}")
    print("-" * 78)
    print(f"QA-1 판정: {'PASS' if pass1 else 'FAIL'} (지면 RGB 모두 ±10% 이내={pass1})")
    print(f"QA-2 판정: {'PASS' if pass2 else 'FAIL'} (지면 RGB 모두 ±10% 이내={pass2})")
    print("=" * 78)

    # ---- 비교 이미지 저장 ----
    ref_crop = ref["img"].crop(ref["crop_box"])
    ref_crop = ref_crop.resize((NATIVE_W, round(NATIVE_W * ref_crop.height / ref_crop.width)), Image.LANCZOS)

    def upscale(im):
        return im.resize((NATIVE_W * DISPLAY_FACTOR, NATIVE_H * DISPLAY_FACTOR), Image.NEAREST)

    qa1_big = upscale(qa1_rgb)
    qa2_big = upscale(qa2_rgb)
    ref_big = ref_crop.resize((NATIVE_W * DISPLAY_FACTOR, round(ref_crop.height * NATIVE_W * DISPLAY_FACTOR / NATIVE_W)), Image.LANCZOS)

    panel_h = max(ref_big.height, qa1_big.height, qa2_big.height) + 90
    panel_w = NATIVE_W * DISPLAY_FACTOR
    canvas = Image.new("RGB", (panel_w * 3 + 40, panel_h), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("C:\\Windows\\Fonts\\malgunbd.ttf", 24)
        font_s = ImageFont.truetype("C:\\Windows\\Fonts\\malgun.ttf", 19)
    except Exception:
        font = ImageFont.load_default()
        font_s = font

    def paste_panel(im, x, title, lines):
        canvas.paste(im, (x, 60))
        draw.text((x, 10), title, fill=(255, 255, 80), font=font)
        yy = 60 + im.height + 6
        for ln in lines:
            draw.text((x, yy), ln, fill=(230, 230, 230), font=font_s)
            yy += 22

    paste_panel(ref_big, 10, "기준 실측 (엔진 렌더 크롭)",
                [f"지면 sRGB = {ref['ground_srgb'][0]:.1f}/{ref['ground_srgb'][1]:.1f}/{ref['ground_srgb'][2]:.1f}  B/R(lin)={ref['ground_br_linear']:.2f}"])
    paste_panel(qa1_big, panel_w + 20, "QA-1: sRGB공간 곱 (레시피 그대로)",
                [f"지면 sRGB = {qa1_ground[0]:.1f}/{qa1_ground[1]:.1f}/{qa1_ground[2]:.1f}  B/R(lin)={qa1_br:.2f}",
                 f"편차 = {dev1[0]:.0f}% / {dev1[1]:.0f}% / {dev1[2]:.0f}%  -> {'PASS' if pass1 else 'FAIL'}"])
    paste_panel(qa2_big, panel_w * 2 + 30, "QA-2: 리니어공간 곱",
                [f"지면 sRGB = {qa2_ground[0]:.1f}/{qa2_ground[1]:.1f}/{qa2_ground[2]:.1f}  B/R(lin)={qa2_br:.2f}",
                 f"편차 = {dev2[0]:.0f}% / {dev2[1]:.0f}% / {dev2[2]:.0f}%  -> {'PASS' if pass2 else 'FAIL'}"])

    canvas.save(OUT_PATH)
    print(f"SAVED: {OUT_PATH} size={canvas.size}")


if __name__ == "__main__":
    main()
