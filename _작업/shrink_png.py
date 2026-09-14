# -*- coding: utf-8 -*-
"""미리보기 PNG의 색 수를 줄여 저장소를 가볍게 한다.

표와 글자가 대부분인 스크린샷이라 256색 팔레트로 바꿔도 눈에 띄는 차이가
없다. 차트가 든 장은 색이 뭉칠 수 있어 줄어든 폭이 작으면 원본을 둔다.

사용법: python shrink_png.py <폴더> [최소절감률]
"""
import os
import sys

from PIL import Image


def main():
    d = sys.argv[1]
    floor = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    before = after = 0
    kept = 0
    for n in sorted(os.listdir(d)):
        if not n.lower().endswith('.png'):
            continue
        p = os.path.join(d, n)
        b = os.path.getsize(p)
        im = Image.open(p).convert('RGB')
        q = im.quantize(colors=256, method=Image.MEDIANCUT)
        tmp = p + '.tmp'
        q.save(tmp, format='PNG', optimize=True)
        a = os.path.getsize(tmp)
        before += b
        if a < b * (1 - floor):
            os.replace(tmp, p)
            after += a
            print('  %-12s %5.0fKB → %5.0fKB  (-%.0f%%)'
                  % (n, b / 1024.0, a / 1024.0, (1 - a / b) * 100))
        else:
            os.remove(tmp)
            after += b
            kept += 1
    print('합계 %.2fMB → %.2fMB  (원본 유지 %d장)'
          % (before / 1048576.0, after / 1048576.0, kept))


if __name__ == '__main__':
    main()
