"""
compose_party.py — 기본전투무대 S1: 캐릭터 8종(A1~A4, B1~B4) 스프라이트 합성

원본 레이어 소스: D:\\unreal\\Resource\\_RawAssets\\heroes99\\ (읽기 전용, 수정 금지)
출력: D:\\unreal\\Resource\\_RawAssets\\heroes99\\_composed\\party\\T_Party_{ID}.png

레시피 근거: docs/features/기본전투무대/raw/P1_레시피_idle조사.md (a) 8종 레시피 표
합성 순서(back->front): hair_bot -> weapon_bot -> cloth_bot -> skin -> face -> cloth_top -> hair_top -> weapon_top
(참고 스크립트: _RawAssets/heroes99/_composed/compose2.py ≡ docs/scripts/compose_knight.py)

⚠ weapon5만 색상 변형 존재(weapon5_c2_bot/top.png). weapon1~4는 색상 접미사 없는 단색
  (weaponN_bot.png / weaponN_top.png). 레시피 표에 이미 반영된 완전 경로를 그대로 사용하므로
  이 스크립트에서는 별도 분기 로직 없이 표 기반 경로를 그대로 조립한다.
"""
from PIL import Image
import hashlib
import os

RAW_ROOT = r"D:\unreal\Resource\_RawAssets\heroes99"
OUT_DIR = os.path.join(RAW_ROOT, "_composed", "party")

CANVAS_SIZE = (800, 680)
CELL_W, CELL_H = 100, 40  # 8 cols x 17 rows

# 8종 레시피 — P1_레시피_idle조사.md (a) 표를 그대로 반영한 완전 상대경로.
# 합성 순서(back->front): hair_bot, weapon_bot, cloth_bot, skin, face, cloth_top, hair_top, weapon_top
RECIPES = {
    "A1": {  # 남 기사
        "hair_bot": r"hair\m5\m5_bot\m5_c7_bot.png",
        "weapon_bot": r"weapon\weapon1\weapon1_bot\weapon1_bot.png",
        "cloth_bot": r"cloth\cloth15\cloth15_bot\cloth15_c1_bot.png",
        "skin": r"skin\skin_c1.png",
        "face": r"face\face_c1.png",
        "cloth_top": r"cloth\cloth15\cloth15_top\cloth15_c1_top.png",
        "hair_top": r"hair\m5\m5_top\m5_c7_top.png",
        "weapon_top": r"weapon\weapon1\weapon1_top\weapon1_top.png",
    },
    "A2": {  # 여 궁수
        "hair_bot": r"hair\f3\f3_bot\f3_c3_bot.png",
        "weapon_bot": r"weapon\weapon2\weapon2_bot\weapon2_bot.png",
        "cloth_bot": r"cloth\cloth7\cloth7_bot\cloth7_c2_bot.png",
        "skin": r"skin\skin_c2.png",
        "face": r"face\face_c3.png",
        "cloth_top": r"cloth\cloth7\cloth7_top\cloth7_c2_top.png",
        "hair_top": r"hair\f3\f3_top\f3_c3_top.png",
        "weapon_top": r"weapon\weapon2\weapon2_top\weapon2_top.png",
    },
    "A3": {  # 남 창병
        "hair_bot": r"hair\m9\m9_bot\m9_c8_bot.png",
        "weapon_bot": r"weapon\weapon3\weapon3_bot\weapon3_bot.png",
        "cloth_bot": r"cloth\cloth3\cloth3_bot\cloth3_c4_bot.png",
        "skin": r"skin\skin_c3.png",
        "face": r"face\face_c2.png",
        "cloth_top": r"cloth\cloth3\cloth3_top\cloth3_c4_top.png",
        "hair_top": r"hair\m9\m9_top\m9_c8_top.png",
        "weapon_top": r"weapon\weapon3\weapon3_top\weapon3_top.png",
    },
    "A4": {  # 여 법사
        "hair_bot": r"hair\f6\f6_bot\f6_c1_bot.png",
        "weapon_bot": r"weapon\weapon4\weapon4_bot\weapon4_bot.png",
        "cloth_bot": r"cloth\cloth11\cloth11_bot\cloth11_c3_bot.png",
        "skin": r"skin\skin_c1.png",
        "face": r"face\face_c4.png",
        "cloth_top": r"cloth\cloth11\cloth11_top\cloth11_c3_top.png",
        "hair_top": r"hair\f6\f6_top\f6_c1_top.png",
        "weapon_top": r"weapon\weapon4\weapon4_top\weapon4_top.png",
    },
    "B1": {  # 남 전사(적) — weapon5 색상변형 c2 반영
        "hair_bot": r"hair\m2\m2_bot\m2_c2_bot.png",
        "weapon_bot": r"weapon\weapon5\weapon5_bot\weapon5_c2_bot.png",
        "cloth_bot": r"cloth\cloth9\cloth9_bot\cloth9_c5_bot.png",
        "skin": r"skin\skin_c4.png",
        "face": r"face\face_c5.png",
        "cloth_top": r"cloth\cloth9\cloth9_top\cloth9_c5_top.png",
        "hair_top": r"hair\m2\m2_top\m2_c2_top.png",
        "weapon_top": r"weapon\weapon5\weapon5_top\weapon5_c2_top.png",
    },
    "B2": {  # 여 도적(적)
        "hair_bot": r"hair\f8\f8_bot\f8_c6_bot.png",
        "weapon_bot": r"weapon\weapon1\weapon1_bot\weapon1_bot.png",
        "cloth_bot": r"cloth\cloth5\cloth5_bot\cloth5_c6_bot.png",
        "skin": r"skin\skin_c5.png",
        "face": r"face\face_c6.png",
        "cloth_top": r"cloth\cloth5\cloth5_top\cloth5_c6_top.png",
        "hair_top": r"hair\f8\f8_top\f8_c6_top.png",
        "weapon_top": r"weapon\weapon1\weapon1_top\weapon1_top.png",
    },
    "B3": {  # 남 광전사(적)
        "hair_bot": r"hair\m12\m12_bot\m12_c9_bot.png",
        "weapon_bot": r"weapon\weapon2\weapon2_bot\weapon2_bot.png",
        "cloth_bot": r"cloth\cloth13\cloth13_bot\cloth13_c7_bot.png",
        "skin": r"skin\skin_c6.png",
        "face": r"face\face_c7.png",
        "cloth_top": r"cloth\cloth13\cloth13_top\cloth13_c7_top.png",
        "hair_top": r"hair\m12\m12_top\m12_c9_top.png",
        "weapon_top": r"weapon\weapon2\weapon2_top\weapon2_top.png",
    },
    "B4": {  # 여 사제(적)
        "hair_bot": r"hair\f1\f1_bot\f1_c5_bot.png",
        "weapon_bot": r"weapon\weapon3\weapon3_bot\weapon3_bot.png",
        "cloth_bot": r"cloth\cloth17\cloth17_bot\cloth17_c8_bot.png",
        "skin": r"skin\skin_c4.png",
        "face": r"face\face_c1.png",
        "cloth_top": r"cloth\cloth17\cloth17_top\cloth17_c8_top.png",
        "hair_top": r"hair\f1\f1_top\f1_c5_top.png",
        "weapon_top": r"weapon\weapon3\weapon3_top\weapon3_top.png",
    },
}

# 합성 순서(back->front). "—"(없음) 레이어는 딕셔너리에서 키 자체를 생략하면 스킵됨.
LAYER_ORDER = [
    "hair_bot",
    "weapon_bot",
    "cloth_bot",
    "skin",
    "face",
    "cloth_top",
    "hair_top",
    "weapon_top",
]


def compose_one(char_id: str, recipe: dict) -> Image.Image:
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    for layer_key in LAYER_ORDER:
        rel = recipe.get(layer_key)
        if not rel:
            print(f"  [{char_id}] SKIP (no layer): {layer_key}")
            continue
        path = os.path.join(RAW_ROOT, rel)
        if not os.path.exists(path):
            print(f"  [{char_id}] MISSING: {path}")
            continue
        img = Image.open(path).convert("RGBA")
        if img.size != CANVAS_SIZE:
            print(f"  [{char_id}] WARNING size mismatch {layer_key}: {img.size} != {CANVAS_SIZE}")
        canvas = Image.alpha_composite(canvas, img)
        print(f"  [{char_id}] ok: {layer_key} <- {rel}")
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = {}
    for char_id, recipe in RECIPES.items():
        print(f"=== composing {char_id} ===")
        sheet = compose_one(char_id, recipe)
        out_path = os.path.join(OUT_DIR, f"T_Party_{char_id}.png")
        sheet.save(out_path)
        results[char_id] = out_path
        print(f"  SAVED: {out_path} size={sheet.size}")

    print("\n=== self-check ===")
    hashes = {}
    for char_id, out_path in results.items():
        img = Image.open(out_path).convert("RGBA")
        w, h = img.size
        size_ok = (w, h) == CANVAS_SIZE

        # Row0 (y=0..39) 6 cells (x=0..599) must have content, col6/7 (x=600..799) must be empty
        row0_bboxes = []
        for col in range(8):
            cell = img.crop((col * CELL_W, 0, (col + 1) * CELL_W, CELL_H))
            row0_bboxes.append(cell.getbbox())
        cols0_5_ok = all(b is not None for b in row0_bboxes[0:6])
        cols6_7_empty = all(b is None for b in row0_bboxes[6:8])

        h_ = hashlib.sha256(img.tobytes()).hexdigest()
        hashes[char_id] = h_

        print(
            f"{char_id}: size={w}x{h} size_ok={size_ok} "
            f"row0_col0-5_content={cols0_5_ok} row0_col6-7_empty={cols6_7_empty} "
            f"hash={h_[:12]}"
        )

    dup = len(hashes) != len(set(hashes.values()))
    print(f"\nduplicate sheets among 8: {dup}")
    if dup:
        seen = {}
        for cid, h_ in hashes.items():
            seen.setdefault(h_, []).append(cid)
        for h_, ids in seen.items():
            if len(ids) > 1:
                print(f"  DUPLICATE GROUP: {ids}")


if __name__ == "__main__":
    main()
