from PIL import Image
import os

base = "."
# back-to-front layer order
layers = [
    "hair/m1/m1_bot/m1_c1_bot.png",
    "cloth/cloth1/cloth1_bot/cloth1_c1_bot.png",
    "skin/skin_c1.png",
    "face/face_c1.png",
    "cloth/cloth1/cloth1_top/cloth1_c1_top.png",
    "hair/m1/m1_top/m1_c1_top.png",
]

canvas = None
for rel in layers:
    p = os.path.join(base, rel)
    if not os.path.exists(p):
        print("MISSING:", p); continue
    img = Image.open(p).convert("RGBA")
    if canvas is None:
        canvas = Image.new("RGBA", img.size, (0,0,0,0))
        print("canvas size:", img.size)
    if img.size != canvas.size:
        print("SIZE MISMATCH:", rel, img.size); continue
    canvas = Image.alpha_composite(canvas, img)
    print("composed:", rel)

out = "_composed/hero_m1_cloth1_c1.png"
canvas.save(out)
print("SAVED:", out, canvas.size)
