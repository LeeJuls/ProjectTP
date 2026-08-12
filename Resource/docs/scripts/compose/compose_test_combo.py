"""
compose_test_combo.py — 캐릭터시스템 raw 조사: 파츠 랜덤 조합 실증용 테스트 합성

목적: heroes99 파츠(스킨/의상/머리/무기/얼굴)를 자유 조합해도 캔버스가 어긋나지 않는지
      실제 합성물로 증명한다. UE 임포트 없음 — 오너 육안 확인용 PNG만 생성.

원본 레이어 소스: D:\\unreal\\Resource\\_RawAssets\\heroes99\\ (읽기 전용, 수정 금지)
출력: D:\\unreal\\Resource\\_RawAssets\\heroes99\\_composed\\test_combo\\

합성 순서(back->front): hair_bot -> weapon_bot -> cloth_bot -> skin -> face -> cloth_top -> hair_top -> weapon_top
(참고: _RawAssets/heroes99/_composed/compose2.py ≡ docs/scripts/compose_knight.py)

조합3(cross_gender)은 검증된 기존 레시피(hero_knight = skin_c1+cloth15_c1+weapon1+face_c1,
docs/features/기본전투무대/raw 및 projectTP_허브 기록)에서 hair만 남성(m5_c7) -> 여성(f5_c1)
태그로 교체한 최소-diff 실험. 몸(skin)은 남녀 구분이 없는 단일 형상이므로, 이 조합에서
어긋남이 관측되면 "머리 성별 태그가 실제로는 몸 형태와 무관하다"는 가설이 깨진다는 뜻.
"""
from PIL import Image
import os

RAW_ROOT = r"D:\unreal\Resource\_RawAssets\heroes99"
OUT_DIR = os.path.join(RAW_ROOT, "_composed", "test_combo")

CANVAS_SIZE = (800, 680)
CELL_W, CELL_H = 100, 40  # 8 cols x 17 rows

LAYER_ORDER = [
    "hair_bot", "weapon_bot", "cloth_bot", "skin", "face",
    "cloth_top", "hair_top", "weapon_top",
]

RECIPES = {
    # 조합1 — cloth8(top 레이어 실사용 계열) + 여성 헤어 f7 + weapon3(dagger)
    "test1": {
        "hair_bot": r"hair\f7\f7_bot\f7_c6_bot.png",
        "weapon_bot": r"weapon\weapon3\weapon3_bot\weapon3_bot.png",
        "cloth_bot": r"cloth\cloth8\cloth8_bot\cloth8_c4_bot.png",
        "skin": r"skin\skin_c3.png",
        "face": r"face\face_c2.png",
        "cloth_top": r"cloth\cloth8\cloth8_top\cloth8_c4_top.png",
        "hair_top": r"hair\f7\f7_top\f7_c6_top.png",
        "weapon_top": r"weapon\weapon3\weapon3_top\weapon3_top.png",
    },
    # 조합2 — cloth2(top 레이어 항상-공백 계열, 11/17 케이스 대표) + 남성 헤어 m11 + weapon5 색상변형(c3)
    "test2": {
        "hair_bot": r"hair\m11\m11_bot\m11_c9_bot.png",
        "weapon_bot": r"weapon\weapon5\weapon5_bot\weapon5_c3_bot.png",
        "cloth_bot": r"cloth\cloth2\cloth2_bot\cloth2_c7_bot.png",
        "skin": r"skin\skin_c5.png",
        "face": r"face\face_c6.png",
        "cloth_top": r"cloth\cloth2\cloth2_top\cloth2_c7_top.png",
        "hair_top": r"hair\m11\m11_top\m11_c9_top.png",
        "weapon_top": r"weapon\weapon5\weapon5_top\weapon5_c3_top.png",
    },
    # 조합3 — 교차 성별 테스트: hero_knight 레시피(skin_c1+cloth15_c1+weapon1+face_c1)에서
    # hair만 m5_c7(남) -> f5_c1(여)로 교체. 몸/의상/무기는 기존 검증본과 100% 동일(최소-diff).
    "test3_cross_gender": {
        "hair_bot": r"hair\f5\f5_bot\f5_c1_bot.png",
        "weapon_bot": r"weapon\weapon1\weapon1_bot\weapon1_bot.png",
        "cloth_bot": r"cloth\cloth15\cloth15_bot\cloth15_c1_bot.png",
        "skin": r"skin\skin_c1.png",
        "face": r"face\face_c1.png",
        "cloth_top": r"cloth\cloth15\cloth15_top\cloth15_c1_top.png",
        "hair_top": r"hair\f5\f5_top\f5_c1_top.png",
        "weapon_top": r"weapon\weapon1\weapon1_top\weapon1_top.png",
    },
}

# 대조군(참고용, 저장은 안 함) — 조합3의 원본(남성 헤어) 버전. 스크립트 내에서 bbox 비교용으로만 사용.
CONTROL_FOR_CROSS_GENDER = {
    "hair_bot": r"hair\m5\m5_bot\m5_c7_bot.png",
    "weapon_bot": r"weapon\weapon1\weapon1_bot\weapon1_bot.png",
    "cloth_bot": r"cloth\cloth15\cloth15_bot\cloth15_c1_bot.png",
    "skin": r"skin\skin_c1.png",
    "face": r"face\face_c1.png",
    "cloth_top": r"cloth\cloth15\cloth15_top\cloth15_c1_top.png",
    "hair_top": r"hair\m5\m5_top\m5_c7_top.png",
    "weapon_top": r"weapon\weapon1\weapon1_top\weapon1_top.png",
}


def compose_one(name: str, recipe: dict) -> Image.Image:
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    for layer_key in LAYER_ORDER:
        rel = recipe.get(layer_key)
        if not rel:
            continue
        path = os.path.join(RAW_ROOT, rel)
        if not os.path.exists(path):
            print(f"  [{name}] MISSING: {path}")
            continue
        img = Image.open(path).convert("RGBA")
        if img.size != CANVAS_SIZE:
            print(f"  [{name}] WARNING size mismatch {layer_key}: {img.size} != {CANVAS_SIZE}")
        canvas = Image.alpha_composite(canvas, img)
    return canvas


def hair_only_bbox(recipe: dict, row: int):
    """hair_bot|hair_top 레이어만 합성해 특정 row 전체(가로 8프레임)의 bbox를 구한다.
    교차 성별 조합의 머리카락이 캔버스를 벗어나거나 비정상적으로 넓은 영역을 차지하는지 점검."""
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    for key in ("hair_bot", "hair_top"):
        rel = recipe.get(key)
        if not rel:
            continue
        img = Image.open(os.path.join(RAW_ROOT, rel)).convert("RGBA")
        canvas = Image.alpha_composite(canvas, img)
    strip = canvas.crop((0, row * CELL_H, CANVAS_SIZE[0], (row + 1) * CELL_H))
    return strip.getbbox()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, recipe in RECIPES.items():
        print(f"=== composing {name} ===")
        sheet = compose_one(name, recipe)
        out_path = os.path.join(OUT_DIR, f"{name}.png")
        sheet.save(out_path)
        w, h = sheet.size
        print(f"  SAVED: {out_path} size={w}x{h} size_ok={(w, h) == CANVAS_SIZE}")

        # idle(row0) preview, 8x scale, for quick eyeballing
        idle = sheet.crop((0, 0, CELL_W * 6, CELL_H))  # 6 valid idle frames
        idle_big = idle.resize((idle.width * 8, idle.height * 8), Image.NEAREST)
        idle_big.save(os.path.join(OUT_DIR, f"{name}_idle_preview_8x.png"))

        # run1(row2, 8 frames) preview strip, 6x scale -- 머리 흔들림이 가장 잘 드러나는 로우
        run = sheet.crop((0, 2 * CELL_H, CELL_W * 8, 3 * CELL_H))
        run_big = run.resize((run.width * 6, run.height * 6), Image.NEAREST)
        run_big.save(os.path.join(OUT_DIR, f"{name}_run1_preview_6x.png"))

    # --- 조합3 전용: 교차 성별 머리 bbox 정량 비교 (m5 남성 헤어 대조군 vs f5 여성 헤어) ---
    print("\n=== cross-gender hair bbox sanity check (row별 hair-only bbox) ===")
    rows_to_check = {0: "IDLE1", 2: "RUN1", 5: "ATK1", 16: "ROLL"}
    female_recipe = RECIPES["test3_cross_gender"]
    for row, rname in rows_to_check.items():
        bbox_f = hair_only_bbox(female_recipe, row)
        bbox_m = hair_only_bbox(CONTROL_FOR_CROSS_GENDER, row)
        in_canvas_f = bbox_f is None or (0 <= bbox_f[0] and 0 <= bbox_f[1] and bbox_f[2] <= CANVAS_SIZE[0] and bbox_f[3] <= CELL_H)
        print(f"row{row} {rname}: f5(female-tag) bbox={bbox_f} within_row_bounds={in_canvas_f} | m5(male-tag, control) bbox={bbox_m}")


if __name__ == "__main__":
    main()
