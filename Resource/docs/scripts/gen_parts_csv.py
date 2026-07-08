"""
gen_parts_csv.py — heroes99 파츠 카탈로그를 파일시스템 스캔으로 data/parts.csv에 생성한다.

데이터 규약(정본): docs/데이터규약_예시.md §parts.csv
파츠 실측 근거   : docs/features/캐릭터시스템/raw/파츠_인벤토리.md

ID 규칙(도메인2=파츠): [2][C 카테고리][SS 스타일][CC 색상][NN 예비] 8자리
  C  : 1=Skin 2=Face 3=Hair 4=Cloth 5=Weapon
  SS : skin/face=00(단일), hair 01~23(m1~14->01~14, f1~9->15~23), cloth 01~17, weapon 01~05
  CC : skin 01~06, face 01~07, hair 01~10, cloth 01~08, weapon(1~4=00 색상없음, 5=01~04)
  NN : 예비 00

행 모델: parts.csv 정본 예시와 동일하게 "1 style x color 콤보 = 1행"이며, 한 행이
AssetPathBot/AssetPathTop 두 컬럼에 bot/top 파일을 함께 담는다(레이어별로 행을 쪼개지 않음
— ID 세그먼트에 레이어 축이 없어 쪼개면 같은 콤보의 bot/top이 Id가 중복되기 때문).

콤보(행) 수: skin 6 + face 7 + hair 230(23x10) + cloth 136(17x8) + weapon 8(4+4) = 387행.
파츠_인벤토리.md의 "총 PNG 761"(skin6/face7/hair460/cloth272/weapon16)은 bot·top 개별
'파일' 수 지표라 행 수(콤보)와는 단위가 다르다. 아래 __main__ 끝의 검증에서 두 지표가
서로 정합함을 재확인한다(761 = 참조 673 + cloth top-blank 미참조 88).

cloth top-blank 목록(11종)은 파츠_인벤토리.md §2-2 알파채널 전수 스캔 결과를 그대로 사용
(본 스크립트는 과제 지시에 따라 픽셀 재검사를 하지 않고 파일명 규칙 + 기존 실측만 사용).

실행: python gen_parts_csv.py
출력: D:\\unreal\\Resource\\data\\parts.csv (UTF-8, LF, 387행 + 헤더)
"""
import csv
import os
import re

RAW_ROOT = r"D:\unreal\Resource\_RawAssets\heroes99"
OUT_PATH = r"D:\unreal\Resource\data\parts.csv"

GENDER_MALE = "90200100"
GENDER_FEMALE = "90200200"

# 파츠_인벤토리.md §2-2: _top 레이어가 전체 알파=0(완전 공백)으로 실측된 cloth 스타일.
# 파일 자체는 존재하지만(그리드 272개에 포함) 참조 가치가 없어 AssetPathTop을 비운다(과제 지시).
CLOTH_TOP_BLANK = {1, 2, 3, 4, 5, 6, 9, 10, 11, 16, 17}

CATEGORY_DIGIT = {"Skin": "1", "Face": "2", "Hair": "3", "Cloth": "4", "Weapon": "5"}

WEAPON_ID_TXT = {
    1: "part_weapon_w1",
    2: "part_weapon_w2",
    3: "part_weapon_w3",
    4: "part_weapon_spear",
}

FIELDNAMES = ["Id", "#id_txt", "Category", "StyleNo", "ColorNo", "GenderTag", "JobTags",
              "AssetPathBot", "AssetPathTop"]

rows = []
_seen_ids = set()


def make_id(category, style, color):
    return f"2{CATEGORY_DIGIT[category]}{style:02d}{color:02d}00"


def list_pngs(folder):
    return sorted(fn for fn in os.listdir(folder) if fn.lower().endswith(".png"))


def color_num(fn):
    """'skin_c3.png'->3, 'f7_c10_bot.png'->10, 'weapon5_c4_bot.png'->4"""
    m = re.search(r"_c(\d+)(?:_bot|_top)?\.png$", fn)
    return int(m.group(1))


def add_row(category, style, color, gender_tag, id_txt, bot_path, top_path):
    id_ = make_id(category, style, color)
    assert id_ not in _seen_ids, f"Id 중복: {id_} ({id_txt})"
    _seen_ids.add(id_)

    for p in (bot_path, top_path):
        if p:
            full = os.path.join(RAW_ROOT, p.replace("/", os.sep))
            assert os.path.isfile(full), f"파일 없음: {full}"

    rows.append({
        "Id": id_, "#id_txt": id_txt, "Category": category,
        "StyleNo": style, "ColorNo": color, "GenderTag": gender_tag, "JobTags": "",
        "AssetPathBot": bot_path or "", "AssetPathTop": top_path or "",
    })


def gen_skin():
    for fn in list_pngs(os.path.join(RAW_ROOT, "skin")):
        c = color_num(fn)
        add_row("Skin", 0, c, "", f"part_skin_c{c}", f"skin/{fn}", "")


def gen_face():
    for fn in list_pngs(os.path.join(RAW_ROOT, "face")):
        c = color_num(fn)
        add_row("Face", 0, c, "", f"part_face_c{c}", f"face/{fn}", "")


def gen_hair():
    hair_dir = os.path.join(RAW_ROOT, "hair")
    all_dirs = [d for d in os.listdir(hair_dir) if os.path.isdir(os.path.join(hair_dir, d))]
    m_names = sorted((d for d in all_dirs if d.startswith("m")), key=lambda s: int(s[1:]))
    f_names = sorted((d for d in all_dirs if d.startswith("f")), key=lambda s: int(s[1:]))
    assert len(m_names) == 14 and len(f_names) == 9, (m_names, f_names)

    style_map = {}
    for i, name in enumerate(m_names, start=1):
        style_map[name] = i
    for i, name in enumerate(f_names, start=15):
        style_map[name] = i

    for name in m_names + f_names:
        style = style_map[name]
        gender_tag = GENDER_MALE if name.startswith("m") else GENDER_FEMALE
        bot_dir = os.path.join(hair_dir, name, f"{name}_bot")
        colors = sorted(color_num(fn) for fn in list_pngs(bot_dir))
        for c in colors:
            bot_path = f"hair/{name}/{name}_bot/{name}_c{c}_bot.png"
            top_path = f"hair/{name}/{name}_top/{name}_c{c}_top.png"
            add_row("Hair", style, c, gender_tag, f"part_hair_{name}_c{c}", bot_path, top_path)


def gen_cloth():
    cloth_dir = os.path.join(RAW_ROOT, "cloth")
    names = sorted(
        (d for d in os.listdir(cloth_dir) if os.path.isdir(os.path.join(cloth_dir, d))),
        key=lambda s: int(s.replace("cloth", "")),
    )
    assert len(names) == 17, names

    for name in names:
        n = int(name.replace("cloth", ""))
        bot_dir = os.path.join(cloth_dir, name, f"{name}_bot")
        colors = sorted(color_num(fn) for fn in list_pngs(bot_dir))
        for c in colors:
            bot_path = f"cloth/{name}/{name}_bot/{name}_c{c}_bot.png"
            top_path = None if n in CLOTH_TOP_BLANK else f"cloth/{name}/{name}_top/{name}_c{c}_top.png"
            add_row("Cloth", n, c, "", f"part_cloth_s{n}_c{c}", bot_path, top_path)


def gen_weapon():
    for n in range(1, 5):
        bot_path = f"weapon/weapon{n}/weapon{n}_bot/weapon{n}_bot.png"
        top_path = f"weapon/weapon{n}/weapon{n}_top/weapon{n}_top.png"
        add_row("Weapon", n, 0, "", WEAPON_ID_TXT[n], bot_path, top_path)

    w5_bot_dir = os.path.join(RAW_ROOT, "weapon", "weapon5", "weapon5_bot")
    colors = sorted(color_num(fn) for fn in list_pngs(w5_bot_dir))
    for c in colors:
        bot_path = f"weapon/weapon5/weapon5_bot/weapon5_c{c}_bot.png"
        top_path = f"weapon/weapon5/weapon5_top/weapon5_c{c}_top.png"
        add_row("Weapon", 5, c, "", f"part_weapon_wand_c{c}", bot_path, top_path)


def validate_and_report():
    by_cat = {}
    for r in rows:
        by_cat[r["Category"]] = by_cat.get(r["Category"], 0) + 1
    print("행 수(콤보 기준):", len(rows), by_cat)

    assert by_cat == {"Skin": 6, "Face": 7, "Hair": 230, "Cloth": 136, "Weapon": 8}, by_cat
    assert len(rows) == 387

    ids = [r["Id"] for r in rows]
    assert len(ids) == len(set(ids)), "Id 중복 발견"
    for r in rows:
        assert len(r["Id"]) == 8 and r["Id"].startswith("2"), f"세그먼트 규칙 위반: {r}"
        assert r["JobTags"] == "", f"JobTags 임의 배정 발견: {r}"

    bot_ref = sum(1 for r in rows if r["AssetPathBot"])
    top_ref = sum(1 for r in rows if r["AssetPathTop"])
    ref_total = bot_ref + top_ref
    excluded = len(CLOTH_TOP_BLANK) * 8  # cloth top-blank 11종 x 색상8
    print(f"참조 파일: bot={bot_ref} top={top_ref} 합계={ref_total}")
    print(f"의도적 미참조(cloth top-blank): {excluded}개")
    print(f"참조+미참조 합계: {ref_total + excluded} (파츠_인벤토리 총 PNG 761과 일치해야 함)")
    assert ref_total + excluded == 761


def main():
    gen_skin()
    gen_face()
    gen_hair()
    gen_cloth()
    gen_weapon()
    validate_and_report()

    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"저장 완료: {OUT_PATH} ({len(rows)}행)")


if __name__ == "__main__":
    main()
