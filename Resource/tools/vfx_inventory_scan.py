"""
vfx_inventory_scan.py — 픽셀 VFX 팩(_RawAssets/vfx/Free) 180장 전수 메타 추출

목적: D4.5-a. `vfx.csv` 컬럼 후보(TexPath/GridX/GridY/ColorRow/FrameCount/FPS)를
      실제로 채울 수 있는 값인지 추측 없이 Pillow+numpy 실측으로 확인한다.

측정 항목 (파일당):
  - W, H 실측 크기
  - CellPx: 64가 W,H를 나누어떨어지는지 검증(가정 아님)
  - GridX, GridY: W/CellPx, H/CellPx
  - FrameCount: 열 단위로 "그 열의 전체 높이 중 alpha>0 픽셀이 하나라도 있는가" 판정.
    앞에서부터 연속으로 내용이 있는 열 수(첫 빈 열 이후는 후미로 간주)와
    전체 내용열 수를 모두 기록해 "중간에 구멍" 이상치를 잡는다.
  - ColorRowCount: 행 단위로 같은 방식(alpha>0 존재)으로 판정한 내용행 수
  - AchromaticRows: 내용은 있으나(alpha>0) 채도(HSV Saturation) > 0.15인 픽셀이 0개인 행
    (= 무채색/그레이스케일 색상 변형. "빈 행"과는 다른 개념 — 반드시 구분)
  - RowHues: 행별 median Hue(도, chromatic 픽셀만). 무채색 행은 -1.
  - Note: 이상치 메모(64 나누어떨어지지 않음/열-구멍/빈 행 등)

실행: "C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" vfx_inventory_scan.py
출력: D:\\unreal\\Resource\\data\\drafts\\vfx_inventory_raw.csv
      + 콘솔에 요약(GridX 분포, achromatic row 인덱스 분포, FrameCount!=GridX 카운트)

원본 소스: D:\\unreal\\Resource\\_RawAssets\\vfx\\Free\\ (읽기 전용, 유료 에셋 — 이 스크립트 밖으로 원본 유출 금지)
"""
import os
import csv
from collections import Counter

import numpy as np
from PIL import Image

RAW_ROOT = r"D:\unreal\Resource\_RawAssets\vfx"
SCAN_SUBDIR = "Free"
CELL_ASSUMED = 64
SAT_THRESHOLD = 0.15  # 이 값 초과라야 "유채색" 픽셀로 카운트

OUT_CSV = r"D:\unreal\Resource\data\drafts\vfx_inventory_raw.csv"


def rgb_to_hue_deg(r, g, b):
    """r,g,b: 0..1 numpy 배열. 반환: 0..360 Hue(도)."""
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    delta = maxc - minc
    mask = delta > 1e-6
    d = np.where(mask, delta, 1.0)
    rc = (maxc - r) / d
    gc = (maxc - g) / d
    bc = (maxc - b) / d
    h = np.zeros_like(r)
    is_r = (maxc == r) & mask
    is_g = (~is_r) & (maxc == g) & mask
    is_b = (~is_r) & (~is_g) & mask
    h = np.where(is_r, bc - gc, h)
    h = np.where(is_g, 2.0 + rc - bc, h)
    h = np.where(is_b, 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0
    return h * 360.0


def analyze_file(full_path, rel_path):
    im = Image.open(full_path).convert("RGBA")
    W, H = im.size
    arr = np.array(im).astype(np.float32)
    alpha = arr[:, :, 3]

    notes = []

    # --- CellPx 검증 (64 가정, 실측으로 확인) ---
    cell = CELL_ASSUMED
    if W % cell != 0 or H % cell != 0:
        notes.append(f"64로 안 나누어떨어짐(W%64={W%cell},H%64={H%cell})")
        # 그래도 정수 그리드로 취급하기 위해 floor
    gx = W // cell
    gy = H // cell

    # --- 열(column) 단위 내용 판정: FrameCount ---
    col_has_content = np.zeros(gx, dtype=bool)
    for c in range(gx):
        band = alpha[:, c * cell:(c + 1) * cell]
        col_has_content[c] = bool((band > 0).any())
    frame_count_total = int(col_has_content.sum())
    # 앞에서부터 연속된 내용 열 수(후미 공백만 있는 정상 케이스면 total과 동일)
    leading = 0
    for c in range(gx):
        if col_has_content[c]:
            leading += 1
        else:
            break
    if frame_count_total != leading:
        notes.append(f"열 구멍 존재(연속선두={leading}, 전체내용열={frame_count_total})")

    # --- 행(row) 단위 판정 ---
    color_row_count = 0
    achromatic_rows = []
    empty_rows = []
    row_hues = []
    for r in range(gy):
        band_alpha = alpha[r * cell:(r + 1) * cell, :]
        mask = band_alpha > 0
        if not mask.any():
            empty_rows.append(r)
            row_hues.append(-1.0)
            continue
        color_row_count += 1
        rgb = arr[r * cell:(r + 1) * cell, :, :3]
        rr = rgb[:, :, 0][mask] / 255.0
        gg = rgb[:, :, 1][mask] / 255.0
        bb = rgb[:, :, 2][mask] / 255.0
        maxc = np.maximum(np.maximum(rr, gg), bb)
        minc = np.minimum(np.minimum(rr, gg), bb)
        sat = np.where(maxc > 0, (maxc - minc) / np.maximum(maxc, 1e-6), 0)
        chromatic = sat > SAT_THRESHOLD
        if not chromatic.any():
            achromatic_rows.append(r)
            row_hues.append(-1.0)
            continue
        hue = rgb_to_hue_deg(rr[chromatic], gg[chromatic], bb[chromatic])
        row_hues.append(float(np.median(hue)))

    if empty_rows:
        notes.append(f"완전 빈 행 존재(alpha 전무): {empty_rows}")

    if frame_count_total != gx:
        notes.append(f"FrameCount({frame_count_total}) != GridX({gx})")

    return {
        "File": rel_path,
        "W": W,
        "H": H,
        "CellPx": cell,
        "GridX": gx,
        "GridY": gy,
        "FrameCount": frame_count_total,
        "ColorRowCount": color_row_count,
        "AchromaticRows": ";".join(str(x) for x in achromatic_rows),
        "RowHues": ";".join(f"{h:.1f}" for h in row_hues),
        "Note": " / ".join(notes),
    }


def main():
    scan_root = os.path.join(RAW_ROOT, SCAN_SUBDIR)
    records = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.lower().endswith(".png"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, RAW_ROOT).replace("\\", "/")
            records.append(analyze_file(full, rel))

    print(f"총 스캔: {len(records)}개 (기대값 180)")

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    fieldnames = ["File", "W", "H", "CellPx", "GridX", "GridY", "FrameCount",
                  "ColorRowCount", "AchromaticRows", "RowHues", "Note"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    print(f"CSV 저장: {OUT_CSV}")

    # --- 콘솔 요약 ---
    print("\n=== GridX 분포 ===")
    gx_counter = Counter(r["GridX"] for r in records)
    for gx, cnt in sorted(gx_counter.items()):
        print(f"  GridX={gx}: {cnt}개")

    print("\n=== GridY 분포 (전부 9여야 정상) ===")
    gy_counter = Counter(r["GridY"] for r in records)
    for gy, cnt in sorted(gy_counter.items()):
        print(f"  GridY={gy}: {cnt}개")

    print("\n=== FrameCount != GridX 인 파일 ===")
    mismatch = [r for r in records if r["FrameCount"] != r["GridX"]]
    print(f"  {len(mismatch)}개")
    for r in mismatch[:20]:
        print(f"    {r['File']}: GridX={r['GridX']} FrameCount={r['FrameCount']}")

    print("\n=== AchromaticRows 인덱스 분포 (행 인덱스가 파일마다 일관되는지) ===")
    idx_counter = Counter()
    for r in records:
        if r["AchromaticRows"]:
            for tok in r["AchromaticRows"].split(";"):
                idx_counter[int(tok)] += 1
    for idx, cnt in sorted(idx_counter.items()):
        print(f"  row{idx}: {cnt}개 파일에서 무채색")
    no_achromatic = sum(1 for r in records if not r["AchromaticRows"])
    print(f"  무채색 행이 0개인 파일: {no_achromatic}개")
    multi_achromatic = [r for r in records if r["AchromaticRows"].count(";") >= 1]
    print(f"  무채색 행이 2개 이상인 파일: {len(multi_achromatic)}개")

    print("\n=== 완전 빈 행(전 열 alpha=0)이 있는 파일 ===")
    empty_row_files = [r for r in records if "완전 빈 행" in r["Note"]]
    print(f"  {len(empty_row_files)}개")
    for r in empty_row_files[:10]:
        print(f"    {r['File']}: {r['Note']}")

    print("\n=== ColorRowCount 분포 (전부 9여야 '9색 고정' 가정 성립) ===")
    crc_counter = Counter(r["ColorRowCount"] for r in records)
    for crc, cnt in sorted(crc_counter.items()):
        print(f"  ColorRowCount={crc}: {cnt}개")

    print("\n=== 64로 안 나누어떨어지는 파일 ===")
    bad64 = [r for r in records if "64로 안" in r["Note"]]
    print(f"  {len(bad64)}개")
    for r in bad64[:10]:
        print(f"    {r['File']}: {r['W']}x{r['H']}")


if __name__ == "__main__":
    main()
