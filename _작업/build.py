# -*- coding: utf-8 -*-
"""_작업/runs/*.json 을 모아 data/runs.js 로 굽는다.

file:// 로 열어도 동작해야 해서 fetch 대신 전역 변수로 심는다.
"""
import glob
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))

ORDER = ['tc04-auto', 'tc04-sonnet', 'tc04-terra', 'tc01-real', 'tc01-demo',
         'rfp-report', 'badge-check', 'isms-audit', 'brief-real', 'brief-demo',
         'skill-proofread', 'weekly-team']


def key(path):
    name = os.path.splitext(os.path.basename(path))[0]
    return ORDER.index(name) if name in ORDER else 99


def main():
    files = sorted(glob.glob(os.path.join(BASE, 'runs', '*.json')), key=key)
    runs = []
    for f in files:
        with open(f, encoding='utf-8') as fh:
            r = json.load(fh)
        # 공개용이라 이 데모에서 재지 않은 값은 싣지 않는다.
        r.pop('monthTotal', None)
        r.get('bench', {}).pop('msBaseline', None)
        for s in r.get('log', []):
            s.pop('month', None)
        runs.append(r)

    out = os.path.join(ROOT, 'data', 'runs.js')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write('/* 자동 생성 파일. _작업/build.py 로 다시 만든다. */\n')
        fh.write('window.COWORK_RUNS = ')
        json.dump(runs, fh, ensure_ascii=False, indent=1)
        fh.write(';\n')

    print('runs.js  %d개 시나리오  %.1f KB'
          % (len(runs), os.path.getsize(out) / 1024))
    for r in runs:
        print('  %-8s %-40s 로그 %2d단계  산출물 %d'
              % (r['tc'], r['title'][:38], len(r['log']), len(r['artifacts'])))


if __name__ == '__main__':
    main()



