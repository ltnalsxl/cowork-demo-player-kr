# -*- coding: utf-8 -*-
"""check_readme.py가 사다리 불일치를 실제로 잡는지 확인한다.

값을 일부러 틀리게 바꿔 검사가 실패하는지 보고, 곧바로 되돌린다.
검사기가 통과만 하고 아무것도 못 잡는 상태를 막는다.
"""
import io
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, 'ladder.py')


def run_check():
    r = subprocess.run([sys.executable, '-X', 'utf8',
                        os.path.join(BASE, 'check_readme.py')],
                       capture_output=True, text=True, encoding='utf-8', cwd=BASE)
    return r.returncode, (r.stdout or '').strip()


def main():
    orig = io.open(P, encoding='utf-8').read()
    if "'avg': 107," not in orig:
        print('기준 값을 찾지 못했습니다.')
        sys.exit(1)

    code, out = run_check()
    if code != 0:
        print('바꾸기 전부터 실패합니다:\n' + out)
        sys.exit(1)

    try:
        io.open(P, 'w', encoding='utf-8').write(orig.replace("'avg': 107,", "'avg': 999,", 1))
        code, out = run_check()
    finally:
        io.open(P, 'w', encoding='utf-8').write(orig)

    if code == 0:
        print('검사기가 불일치를 못 잡습니다.')
        sys.exit(1)
    print('검사기가 불일치를 잡습니다.')
    for line in out.splitlines():
        print('  ' + line)

    code, out = run_check()
    print('되돌린 뒤: ' + out)
    sys.exit(0 if code == 0 else 1)


if __name__ == '__main__':
    main()
