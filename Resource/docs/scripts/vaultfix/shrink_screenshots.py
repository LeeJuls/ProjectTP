#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
shrink_screenshots.py — 게이트 증거 스크린샷 PNG 축소 (오너 지시 2026-08-13: "고용량일 필요가 없지 않아?")

대상: `docs/features/*/raw/*.png` (57장, 원본 합계 약 163.8MB, 대부분 2169x1273)
      ★`docs/renders/*.png`는 이미 git 추적 중이므로 이 스크립트는 절대 건드리지 않는다
      (glob이 `docs/features/**/raw/*.png`로 고정되어 있어 구조적으로 범위 밖이다).

무엇을 하는가:
  1. 긴 변이 MAX_LONG_EDGE(기본 1600px)를 넘으면 LANCZOS로 긴 변 기준 리사이즈.
     넘지 않으면 리사이즈하지 않는다(멱등성의 근거 1).
  2. RGBA인데 알파 채널이 완전 불투명(전 픽셀 255)이면 RGB로 변환 — 캐릭터 스프라이트 컷아웃처럼
     실제 투명도가 있는 파일은 그대로 RGBA 유지.
  3. PNG로 재인코딩(optimize=True, compress_level=9) — 색상 팔레트 양자화는 하지 않는다.
     이유(표본 실험, 2026-08-13): 256색 팔레트 양자화는 하늘 그라데이션에 밴딩을 만들어
     ★"라이팅·색감 차이 A/B 비교"라는 증거 가치를 직접 훼손한다(줌인 비교로 확인).
     리사이즈+무손실 재압축만으로도 원본 합계 대비 약 47%(약 86MB)까지 줄어 육안 손실이 없다.
  4. 재인코딩 결과가 원본 파일 크기보다 **작을 때만** 덮어쓴다. 크거나 같으면 원본을 그대로 둔다
     (멱등성의 근거 2 — 이미 축소된 파일이나, 리사이즈해도 이득이 없는 작은 크롭 파일을 보호한다).

사용법:
  python shrink_screenshots.py                # dry-run: 콘솔에 파일별 전후 크기만 출력, 쓰기 없음
  python shrink_screenshots.py --apply         # 실제로 덮어쓴다
  python shrink_screenshots.py --apply --max-long-edge 1400   # 임계값 조정

멱등성: 이미 축소된 파일(긴 변 <= MAX_LONG_EDGE이고 이미 최적 압축)은 재인코딩 결과가 원본보다
        작아지지 않으므로 두 번째 실행에서 변경 0건이다.

★파일명은 절대 바꾸지 않는다(같은 이름으로 덮어쓴다) — 옵시디언 `![[파일명]]` 임베드가 이름에 의존한다.
★git add / git mv / commit은 하지 않는다 — PM이 일괄 커밋한다.
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
TARGET_GLOB = os.path.join(REPO_ROOT, 'docs', 'features', '**', 'raw', '*.png')

DEFAULT_MAX_LONG_EDGE = 1600


def find_targets():
    return sorted(glob.glob(TARGET_GLOB, recursive=True))


def build_candidate(path, max_long_edge):
    """원본을 읽어 축소 후보 PNG 바이트를 만든다. 파일은 건드리지 않는다."""
    im = Image.open(path)
    im.load()
    work = im

    if work.mode == 'RGBA':
        alpha = work.getchannel('A')
        if alpha.getextrema() == (255, 255):
            work = work.convert('RGB')
    elif work.mode == 'P':
        # 팔레트 모드는 그대로 두되, 알파 없는 경우 RGB로 통일해 재압축 일관성을 확보
        work = work.convert('RGBA') if 'transparency' in im.info else work.convert('RGB')
        if work.mode == 'RGBA':
            alpha = work.getchannel('A')
            if alpha.getextrema() == (255, 255):
                work = work.convert('RGB')

    w, h = work.size
    resized = False
    if max(w, h) > max_long_edge:
        scale = max_long_edge / max(w, h)
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        work = work.resize((nw, nh), Image.LANCZOS)
        resized = True

    buf = io.BytesIO()
    work.save(buf, format='PNG', optimize=True, compress_level=9)
    return buf.getvalue(), work.size, resized


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='실제로 파일을 덮어쓴다 (기본은 dry-run)')
    ap.add_argument('--max-long-edge', type=int, default=DEFAULT_MAX_LONG_EDGE,
                     help=f'긴 변 리사이즈 임계값 px (기본 {DEFAULT_MAX_LONG_EDGE})')
    args = ap.parse_args()

    targets = find_targets()
    if not targets:
        print(f'대상 없음: {TARGET_GLOB}')
        return 0

    total_orig = 0
    total_new = 0
    n_shrunk = 0
    n_skipped = 0
    n_error = 0

    print(f'{"파일":60s} {"원본":>10s} {"축소후":>10s} {"변화":>8s}  상태')
    print('-' * 100)

    for path in targets:
        rel = os.path.relpath(path, REPO_ROOT)
        try:
            orig_size = os.path.getsize(path)
            candidate, new_dims, resized = build_candidate(path, args.max_long_edge)
            new_size = len(candidate)

            if new_size < orig_size:
                pct = (1 - new_size / orig_size) * 100
                status = f'{"resize" if resized else "recompress"} -{pct:.0f}%'
                if args.apply:
                    with open(path, 'wb') as f:
                        f.write(candidate)
                    status += ' [적용됨]'
                else:
                    status += ' [dry-run]'
                n_shrunk += 1
                total_orig += orig_size
                total_new += new_size
            else:
                status = 'skip(이득없음, 원본유지)'
                n_skipped += 1
                total_orig += orig_size
                total_new += orig_size
                new_size = orig_size

            print(f'{rel:60s} {orig_size/1024:9.1f}K {new_size/1024:9.1f}K {new_size-orig_size:+8d}B  {status}')
        except Exception as e:
            n_error += 1
            print(f'{rel:60s} ERROR: {e}')

    print('-' * 100)
    print(f'대상 {len(targets)}장 | 축소 {n_shrunk}장 | 스킵 {n_skipped}장 | 오류 {n_error}장')
    if total_orig:
        print(f'합계: {total_orig/1024/1024:.2f} MB -> {total_new/1024/1024:.2f} MB '
              f'({total_new/total_orig*100:.1f}%, {(total_orig-total_new)/1024/1024:.2f} MB 절감)')
    if not args.apply:
        print('\n(dry-run 모드 — 실제로 적용하려면 --apply 를 붙여 재실행하라)')

    return 1 if n_error else 0


if __name__ == '__main__':
    sys.exit(main())
