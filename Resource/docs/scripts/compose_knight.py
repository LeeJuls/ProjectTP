from PIL import Image
import os
base = "."
# back-to-front
layers = [
    "hair/m5/m5_bot/m5_c7_bot.png",
    "weapon/weapon1/weapon1_bot/weapon1_bot.png",
    "cloth/cloth15/cloth15_bot/cloth15_c1_bot.png",
    "skin/skin_c1.png",
    "face/face_c1.png",
    "cloth/cloth15/cloth15_top/cloth15_c1_top.png",
    "hair/m5/m5_top/m5_c7_top.png",
    "weapon/weapon1/weapon1_top/weapon1_top.png",
]
canvas = None
for rel in layers:
    p = os.path.join(base, rel)
    if not os.path.exists(p):
        print("MISSING:", p); continue
    img = Image.open(p).convert("RGBA")
    if canvas is None:
        canvas = Image.new("RGBA", img.size, (0,0,0,0))
    canvas = Image.alpha_composite(canvas, img)
    print("ok:", rel)
out = "_composed/hero_knight.png"
canvas.save(out)
print("SAVED full:", out, canvas.size)
# crop idle frame 1 : grid 8x17, cell 100x40, frame1 = (0,0)
cell_w, cell_h = 100, 40
f1 = canvas.crop((0,0,cell_w,cell_h))
f1.save("_composed/hero_knight_idle1.png")
print("SAVED idle1 cell:", f1.size)
# also a tight-cropped single (bbox of frame1) for preview
bbox = f1.getbbox()
print("idle1 content bbox:", bbox)
