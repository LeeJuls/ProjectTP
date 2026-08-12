#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
png_to_webp.py — 게이트 증거 스크린샷 PNG → WebP 전환 (오너 승인 2026-08-13: "PNG 86MB에서 더 줄이자 — WebP 전환")

대상: `docs/features/*/raw/*.png` (57장, 이번 실행 시점 디스크는 1600px 1차 축소본 PNG, 합계 약 86MB)
      ★`docs/renders/*.png`(2장, git 추적 중)는 이 스크립트가 절대 건드리지 않는다
      — glob이 `docs/features/**/raw/*.png`로 고정되어 구조적으로 범위 밖이다.

★핵심: 디스크에 있는 1600px 축소본이 아니라 **원본(2169px) 백업**에서 직접 변환한다.
축소본에서 또 리사이즈하면 2단계 리샘플링이라 화질이 불필요하게 깎이기 때문이다.
원본 백업 위치는 --source-dir로 지정한다(기본값은 이번 작업 세션의 스크래치패드 경로 —
세션이 끝나면 사라질 수 있으므로, 재실행 시 원본이 필요한 상황이면 --source-dir를 새로
지정하라. 이미 전환이 끝난 상태(멱등)라면 원본 없이도 그냥 skip한다).

무엇을 하는가:
  1. `docs/features/**/raw/*.png` 중 아직 안 남은(=아직 .webp로 전환 안 된) PNG를 찾는다.
  2. 같은 상대경로를 --source-dir(원본 백업) 아래에서 찾아 원본을 연다.
  3. 알파 채널이 "실제로" 쓰이는 파일만 RGBA 유지(전 픽셀이 불투명이면 RGB로 변환).
     ★실측(2026-08-13, PIL로 alpha.getextrema() 전수 조사): 57장 중 완전 불투명이
     아닌 파일은 `공격버튼데모/raw/D3_click_t045.png` **1장뿐**이었다(그마저 2px만 비-255,
     마우스 클릭 마커의 안티앨리어싱으로 추정). PM 지시서의 "알파 실사용 4개 파일" 추정과는
     다르다 — 실측값을 우선했다(PM 보고 완료, 2026-08-13 실행 로그 참고).
  4. 긴 변이 MAX_LONG_EDGE(기본 1600px)를 넘으면 LANCZOS로 리사이즈.
     ★1200px는 스프라이트가 뭉개지고 1600px는 원본에 근접함이 직전 작업(shrink_screenshots.py)에서
     육안 확인됨 — 이 값을 그대로 유지한다.
  5. WebP로 인코딩(손실, quality=90, method=6).
  6. `docs/features/<feature>/raw/<파일>.webp`로 저장하고, 원본 `.png`를 삭제한다(--apply일 때만).
     PNG는 git 미추적이므로 삭제해도 이력이 안 남는다(정상 — PM 확인됨).

멱등성: 대상 `.webp`가 이미 있고 원본 `.png`가 이미 없으면(=이미 전환됨) 그 파일은 자동으로
        "찾을 대상"에서 빠진다(glob이 .png만 찾으므로). 전체가 이미 전환된 상태면 --source-dir가
        없어도(또는 사라져 있어도) 에러 없이 "대상 없음"으로 종료한다.

사용법:
  python png_to_webp.py                              # dry-run: 콘솔에 파일별 전후 크기만 출력, 쓰기 없음
  python png_to_webp.py --apply                       # 실제로 webp 생성 + png 삭제
  python png_to_webp.py --source-dir <경로>             # 원본(리사이즈 전) PNG 백업 폴더 지정
  python png_to_webp.py --apply --quality 92 --max-long-edge 1600   # 설정 조정

★파일명(확장자 제외)은 절대 바꾸지 않는다 — 옵시디언 `![[파일명.webp]]` 임베드가 이름에 의존한다.
★git add / git mv / commit은 하지 않는다 — PM이 일괄 커밋한다.
★docs/renders/ 접촉 금지, _RawAssets 접촉 금지.
"""
import os
import io
import sys
import glob
import argparse

from PIL import Image

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))  # docs/scripts/vaultfix -> Resource/
FEATURES_ROOT = os.path.join(REPO_ROOT, 'docs', 'features')
TARGET_GLOB = os.path.join(FEATURES_ROOT, '**', 'raw', '*.png')

# 이번 작업(2026-08-13) 세션의 스크래치패드 백업 경로. 세션이 끝나면 사라질 수 있다 —
# 재실행 시 원본이 더 이상 없으면 --source-dir로 새 위치를 지정하라.
DEFAULT_SOURCE_DIR = (
    r"C:\Users\user\AppData\Local\Temp\claude\D--unreal-Resource"
    r"\7246227d-0e35-430a-a874-e287b4339af8\scratchpad\png_original_backup"
)

DEFAULT_MAX_LONG_EDGE = 1600
DEFAULT_QUALITY = 90
DEFAULT_METHOD = 6


def find_targets():
    """아직 .webp로 전환 안 된 PNG 목록."""
    return sorted(glob.glob(TARGET_GLOB, recursive=True))


def resolve_source(png_path, source_dir):
    """docs/features/<feature>/raw/<파일>.png -> source_dir/docs/features/<feature>/raw/<파일>.png"""
    rel = os.path.relpath(png_path, REPO_ROOT)  # docs/features/<feature>/raw/<파일>.png
    return os.path.join(source_dir, rel)


def has_real_alpha(im):
    """알파 채널이 실제로(전 픽셀 불투명이 아니게) 쓰이는지 판정."""
    if im.mode == 'RGBA':
        a = im.getchannel('A')
        return a.getextrema() != (255, 255)
    if im.mode == 'P' and 'transparency' in im.info:
        a = im.convert('RGBA').getchannel('A')
        return a.getextrema() != (255, 255)
    return False


def build_webp(src_path, max_long_edge):
    im = Image.open(src_path)
    im.load()

    keep_alpha = has_real_alpha(im)
    work = im.convert('RGBA') if keep_alpha else im.convert('RGB')

    w, h = work.size
    if max(w, h) > max_long_edge:
        scale = max_long_edge / max(w, h)
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        work = work.resize((nw, nh), Image.LANCZOS)

    return work, keep_alpha


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='실제로 webp를 생성하고 png를 삭제한다 (기본은 dry-run)')
    ap.add_argument('--source-dir', default=DEFAULT_SOURCE_DIR, help='원본(리사이즈 전) PNG 백업 폴더')
    ap.add_argument('--max-long-edge', type=int, default=DEFAULT_MAX_LONG_EDGE,
                     help=f'긴 변 리사이즈 임계값 px (기본 {DEFAULT_MAX_LONG_EDGE})')
    ap.add_argument('--quality', type=int, default=DEFAULT_QUALITY, help=f'WebP 손실 품질 (기본 {DEFAULT_QUALITY})')
    ap.add_argument('--method', type=int, default=DEFAULT_METHOD, help=f'WebP 압축 노력 0-6 (기본 {DEFAULT_METHOD})')
    args = ap.parse_args()

    targets = find_targets()
    if not targets:
        print('대상 PNG 없음 — 이미 전부 WebP로 전환되었거나(멱등) 대상이 원래 없음.')
        return 0

    total_png = 0
    total_webp = 0
    n_converted = 0
    n_error = 0
    n_alpha = 0

    print(f'{"파일":60s} {"PNG":>10s} {"WebP":>10s} {"절감":>8s}  상태')
    print('-' * 100)

    for png_path in targets:
        rel = os.path.relpath(png_path, REPO_ROOT)
        webp_path = os.path.splitext(png_path)[0] + '.webp'
        src_path = resolve_source(png_path, args.source_dir)

        if not os.path.isfile(src_path):
            n_error += 1
            print(f'{rel:60s} ERROR: 원본 백업 없음 ({src_path})')
            continue

        try:
            png_size = os.path.getsize(png_path)
            work, keep_alpha = build_webp(src_path, args.max_long_edge)
            if keep_alpha:
                n_alpha += 1

            buf = io.BytesIO()
            work.save(buf, format='WEBP', quality=args.quality, method=args.method, lossless=False)
            webp_bytes = buf.getvalue()
            webp_size = len(webp_bytes)

            status = 'alpha유지' if keep_alpha else 'RGB'
            if args.apply:
                with open(webp_path, 'wb') as f:
                    f.write(webp_bytes)
                os.remove(png_path)
                status += ' [적용됨: webp 생성 + png 삭제]'
            else:
                status += ' [dry-run]'

            pct = (1 - webp_size / png_size) * 100 if png_size else 0
            total_png += png_size
            total_webp += webp_size
            n_converted += 1
            print(f'{rel:60s} {png_size/1024:9.1f}K {webp_size/1024:9.1f}K {pct:7.1f}%  {status}')
        except Exception as e:
            n_error += 1
            print(f'{rel:60s} ERROR: {e}')

    print('-' * 100)
    print(f'대상 {len(targets)}장 | 변환 {n_converted}장(알파유지 {n_alpha}장) | 오류 {n_error}장')
    if total_png:
        print(f'합계: {total_png/1024/1024:.2f} MB -> {total_webp/1024/1024:.2f} MB '
              f'({total_webp/total_png*100:.1f}%, {(total_png-total_webp)/1024/1024:.2f} MB 절감)')
    if not args.apply:
        print('\n(dry-run 모드 — 실제로 적용하려면 --apply 를 붙여 재실행하라)')

    return 1 if n_error else 0


if __name__ == '__main__':
    sys.exit(main())
