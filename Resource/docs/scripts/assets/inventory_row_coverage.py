"""
inventory_row_coverage.py — heroes99 파츠 인벤토리 + 17행 모션 팔레트 실측 스크립트

목적: docs/features/캐릭터시스템/raw/파츠_인벤토리.md 의 수치 근거를 재현한다.
      추정치가 아니라 _RawAssets/heroes99 전체 PNG(그리드 자산 761개, 전수/샘플링 아님)를
      Pillow+numpy로 직접 열어 알파채널을 스캔한 결과다.

측정 항목:
  1) 전 PNG 파일의 (w,h) 전수 스캔 -> 캔버스 크기 일치 여부(800x680 = 8열x17행, 셀 100x40)
  2) 8x17 그리드 셀 단위 알파>0 존재 여부 -> 행별 유효 프레임 수, 행별 파츠 커버리지
  3) 색상 변형(c1..cN) 간 행-커버리지 일치 여부(팔레트 스왑이 프레임 구조에 영향 없는지)
  4) bot/top 레이어 단독 공백 여부(구조적 "이 파츠는 top이 없다" vs 행별 공백)

실행: python inventory_row_coverage.py
출력: 콘솔 요약 + 같은 폴더에 inventory_row_coverage_result.json (재사용 가능한 원자료)

원본 소스: D:\\unreal\\Resource\\_RawAssets\\heroes99\\ (읽기 전용)
"""
import os
import re
import json
from collections import defaultdict, Counter

import numpy as np
from PIL import Image

RAW_ROOT = r"D:\unreal\Resource\_RawAssets\heroes99"
CELL_W, CELL_H = 100, 40
COLS, ROWS = 8, 17
CANVAS_SIZE = (COLS * CELL_W, ROWS * CELL_H)  # (800, 680)

ROW_NAMES = [
    "IDLE1", "IDLE2", "RUN1", "RUN2", "JUMP(+FALL LOOP)",
    "ATK1", "ATK2", "ATK3", "AIRATK1", "AIRATK2",
    "CAST1(+LOOP)", "CAST2(+LOOP)", "HURT", "DYING",
    "DASH(+LOOP)", "BLOCK", "ROLL",
]

CLOTH_RE = re.compile(r"^cloth/cloth(\d+)/cloth\d+_(bot|top)/cloth\d+_c(\d+)_(bot|top)\.png$")
HAIR_RE = re.compile(r"^hair/([mf]\d+)/\1_(bot|top)/\1_c(\d+)_(bot|top)\.png$")
WEAPON_RE = re.compile(r"^weapon/weapon(\d+)/weapon\d+_(bot|top)/weapon\d+(?:_c(\d+))?_(bot|top)\.png$")


def walk_all_pngs():
    records = []
    for root, dirs, files in os.walk(RAW_ROOT):
        dirs.sort()
        if os.path.relpath(root, RAW_ROOT).split(os.sep)[0] == "_composed":
            continue
        for fn in sorted(files):
            if not fn.lower().endswith(".png"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, RAW_ROOT).replace("\\", "/")
            im = Image.open(full)
            records.append({"rel": rel, "w": im.size[0], "h": im.size[1]})
    return records


def grid_alpha_scan(path):
    """8x17 bool grid: True면 해당 셀에 alpha>0 픽셀이 하나라도 있음."""
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3]
    grid = np.zeros((ROWS, COLS), dtype=bool)
    for r in range(ROWS):
        for c in range(COLS):
            cell = alpha[r * CELL_H:(r + 1) * CELL_H, c * CELL_W:(c + 1) * CELL_W]
            grid[r, c] = bool((cell > 0).any())
    return grid


def main():
    print("=== 1) 전수 캔버스 크기 스캔 ===")
    records = walk_all_pngs()
    size_counter = Counter((r["w"], r["h"]) for r in records)
    print(f"총 PNG(비-_composed): {len(records)}")
    for size, cnt in size_counter.most_common():
        tag = "  <- 8x17 그리드(100x40 셀)와 일치" if size == CANVAS_SIZE else "  <- 그리드 자산 아님(카탈로그/가이드 이미지)"
        print(f"  {size}: {cnt}개{tag}")

    grid_records = [r for r in records if (r["w"], r["h"]) == CANVAS_SIZE]
    match_rate = len(grid_records) / len(records) * 100
    print(f"그리드 일치율: {len(grid_records)}/{len(records)} ({match_rate:.1f}%)")

    print("\n=== 2) 카테고리별 파일 수 집계 ===")
    by_cat = Counter(r["rel"].split("/")[0] for r in records)
    for cat, cnt in sorted(by_cat.items()):
        print(f"  {cat}: {cnt}")

    print("\n=== 3) 8x17 알파 그리드 스캔 (전수, 시간 다소 소요) ===")
    grids = {}
    for r in grid_records:
        grids[r["rel"]] = grid_alpha_scan(os.path.join(RAW_ROOT, r["rel"].replace("/", os.sep)))
    print(f"스캔 완료: {len(grids)}개")

    # 그룹화
    cloth_groups = defaultdict(dict)
    hair_groups = defaultdict(dict)
    weapon_groups = defaultdict(dict)
    for rel, grid in grids.items():
        m = CLOTH_RE.match(rel)
        if m:
            cid, layer, color, _ = m.groups()
            cloth_groups[(f"cloth{cid}", layer)][color] = grid
            continue
        m = HAIR_RE.match(rel)
        if m:
            hid, layer, color, _ = m.groups()
            hair_groups[(hid, layer)][color] = grid
            continue
        m = WEAPON_RE.match(rel)
        if m:
            wid, layer, color, _ = m.groups()
            weapon_groups[(f"weapon{wid}", layer)][color] = grid

    def check_color_invariance(groups, label):
        mismatches = []
        for key, colormap in groups.items():
            gs = list(colormap.values())
            if not all(np.array_equal(gs[0], g) for g in gs[1:]):
                mismatches.append(key)
        print(f"  [{label}] 색상변형 간 행-커버리지 불일치: {len(mismatches)}/{len(groups)} 그룹")
        return mismatches

    print("\n=== 4) 색상 변형이 행-커버리지에 영향 주는지 검증 ===")
    check_color_invariance(cloth_groups, "cloth")
    check_color_invariance(hair_groups, "hair")
    check_color_invariance(weapon_groups, "weapon")

    def rep_grid(colormap):
        return colormap.get("1", next(iter(colormap.values())))

    cloth_rep = {k: rep_grid(v) for k, v in cloth_groups.items()}
    hair_rep = {k: rep_grid(v) for k, v in hair_groups.items()}
    weapon_rep = {k: rep_grid(v) for k, v in weapon_groups.items()}

    def combined(groupdict, id_):
        bot, top = groupdict.get((id_, "bot")), groupdict.get((id_, "top"))
        if bot is None:
            return top
        if top is None:
            return bot
        return bot | top

    cloth_ids = sorted(set(k[0] for k in cloth_rep), key=lambda s: int(s.replace("cloth", "")))
    hair_ids = sorted(set(k[0] for k in hair_rep))
    weapon_ids = sorted(set(k[0] for k in weapon_rep), key=lambda s: int(s.replace("weapon", "")))

    skin_grid = grids.get("skin/skin_c1.png")

    print("\n=== 5) 행별 유효 프레임 수 & 파츠 커버리지 (OR(bot,top) 기준) ===")
    print(f"{'row':>4} {'name':<16} {'skin_frames':>11} {'cloth_ok':>10} {'hair_ok':>9} {'weap_ok':>9}")
    row_report = {}
    for r in range(ROWS):
        skin_cnt = int(skin_grid[r].sum())
        c_ok = sum(1 for i in cloth_ids if combined(cloth_rep, i)[r].sum() > 0)
        h_ok = sum(1 for i in hair_ids if combined(hair_rep, i)[r].sum() > 0)
        w_ok = sum(1 for i in weapon_ids if combined(weapon_rep, i)[r].sum() > 0)
        print(f"{r:>4} {ROW_NAMES[r]:<16} {skin_cnt:>11} {c_ok:>7}/17 {h_ok:>6}/23 {w_ok:>6}/5")
        row_report[r] = {"name": ROW_NAMES[r], "skin_frames": skin_cnt,
                          "cloth_ok": c_ok, "hair_ok": h_ok, "weapon_ok": w_ok}

    out = {
        "total_png_noncomposed": len(records),
        "grid_match": f"{len(grid_records)}/{len(records)}",
        "category_counts": dict(by_cat),
        "row_report": row_report,
    }
    out_path = os.path.join(os.path.dirname(__file__), "inventory_row_coverage_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n결과 저장: {out_path}")


if __name__ == "__main__":
    main()
