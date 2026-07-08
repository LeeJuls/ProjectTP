"""
compose_a0_spike_layers.py -- A0 합성 머티리얼 스파이크용 5레이어 텍스처 준비

목적: M_Sprite_PartComposite 머티리얼은 5개 텍스처 파라미터(SkinTex/FaceTex/HairTex/
      ClothTex/WeaponTex)만 받는다. 그런데 heroes99 원본은 hair/cloth/weapon 3개
      카테고리가 각각 bot+top 서브레이어로 나뉘어 있다(skin/face는 원래 단일 레이어).
      이 스크립트는 hair/cloth/weapon의 bot+top을 카테고리 내부에서만 먼저 Pillow로
      알파 합성해 "카테고리당 1장" 텍스처로 평탄화한다 (내부 순서 bot -> top 유지).
      skin/face는 원본을 그대로 복사한다.

      결과 5장을 UE에 개별 텍스처로 임포트해 머티리얼의 5개 파라미터에 바인딩한다.
      머티리얼 레벨의 블렌드 순서는 A0 스파이크 지시서가 정한 단순화 순서
      (skin -> face -> hair -> cloth -> weapon, 뒤가 앞을 덮음)를 따른다.

      주의(알려진 단순화): 실제 프로덕션 8레이어 순서(hair_bot -> weapon_bot ->
      cloth_bot -> skin -> face -> cloth_top -> hair_top -> weapon_top)와 다르다.
      hair/cloth/weapon을 각각 "완성된 한 장"으로 합쳐 skin/face 뒤에 넣기 때문에,
      hair_bot이 face보다 위(앞)에 오는 등 카테고리 간 교차 인터리빙은 재현하지 않는다.
      이 스파이크는 "N장 텍스처를 머티리얼 그래프에서 알파오버로 합성 + SubUV 동기화"
      기술 자체의 성립 여부를 보는 것이 목적이라 5레이어로 단순화했다 (지시서 명시 사항).

원본 소스: D:\\unreal\\Resource\\_RawAssets\\heroes99\\ (읽기 전용, 유료 에셋)
출력: D:\\unreal\\Resource\\_RawAssets\\heroes99\\_composed\\A0_spike\\
"""
from PIL import Image
import os

RAW_ROOT = r"D:\unreal\Resource\_RawAssets\heroes99"
OUT_DIR = os.path.join(RAW_ROOT, "_composed", "A0_spike")

CANVAS_SIZE = (800, 680)
CELL_W, CELL_H = 100, 40  # 8 cols x 17 rows

# test1 레시피 (파츠_인벤토리.md §2-4 test1과 동일):
# skin_c3 + face_c2 + hair f7_c6 + cloth8_c4(top 실사용 계열) + weapon3
TEST1 = {
    "SkinTex": {"single": r"skin\skin_c3.png"},
    "FaceTex": {"single": r"face\face_c2.png"},
    "HairTex": {
        "bot": r"hair\f7\f7_bot\f7_c6_bot.png",
        "top": r"hair\f7\f7_top\f7_c6_top.png",
    },
    "ClothTex": {
        "bot": r"cloth\cloth8\cloth8_bot\cloth8_c4_bot.png",
        "top": r"cloth\cloth8\cloth8_top\cloth8_c4_top.png",
    },
    "WeaponTex": {
        "bot": r"weapon\weapon3\weapon3_bot\weapon3_bot.png",
        "top": r"weapon\weapon3\weapon3_top\weapon3_top.png",
    },
}

OUT_NAMES = {
    "SkinTex": "T_A0_SkinTex_c3.png",
    "FaceTex": "T_A0_FaceTex_c2.png",
    "HairTex": "T_A0_HairTex_f7c6.png",
    "ClothTex": "T_A0_ClothTex_c8c4.png",
    "WeaponTex": "T_A0_WeaponTex_w3.png",
}


def load(rel: str) -> Image.Image:
    path = os.path.join(RAW_ROOT, rel)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    img = Image.open(path).convert("RGBA")
    if img.size != CANVAS_SIZE:
        print(f"  WARNING size mismatch {rel}: {img.size} != {CANVAS_SIZE}")
    return img


def flatten_layer(spec: dict) -> Image.Image:
    if "single" in spec:
        return load(spec["single"])
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    # bot 먼저(뒤), top 나중(앞) -- 카테고리 내부 순서만 보존
    for key in ("bot", "top"):
        rel = spec.get(key)
        if not rel:
            continue
        canvas = Image.alpha_composite(canvas, load(rel))
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for param_name, spec in TEST1.items():
        img = flatten_layer(spec)
        out_path = os.path.join(OUT_DIR, OUT_NAMES[param_name])
        img.save(out_path)
        print(f"{param_name}: SAVED {out_path} size={img.size}")

    # idle(row0, 6프레임) 미리보기 -- 5장을 실제 머티리얼과 동일 순서로 합쳐 눈으로 사전 확인
    order = ["SkinTex", "FaceTex", "HairTex", "ClothTex", "WeaponTex"]
    preview_canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    for param_name in order:
        layer_img = flatten_layer(TEST1[param_name])
        preview_canvas = Image.alpha_composite(preview_canvas, layer_img)
    idle = preview_canvas.crop((0, 0, CELL_W * 6, CELL_H))
    idle_big = idle.resize((idle.width * 8, idle.height * 8), Image.NEAREST)
    idle_big_path = os.path.join(OUT_DIR, "test1_5layer_idle_preview_8x.png")
    idle_big.save(idle_big_path)
    print(f"PREVIEW (5-layer skin->face->hair->cloth->weapon order): SAVED {idle_big_path}")


if __name__ == "__main__":
    main()
