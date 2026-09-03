# -*- coding: utf-8 -*-
"""README와 실제 데이터가 어긋나지 않는지 본다.

시나리오를 더하거나 이름을 바꾸면 README를 고치는 걸 잊기 쉽다.
id, 크레딧, 검증 항목 수를 대조해 어긋난 곳만 찍는다.
"""
import io
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))


def load_runs():
    src = io.open(os.path.join(ROOT, 'data', 'runs.js'), encoding='utf-8').read()
    return json.loads(src.split('= ', 1)[1].rsplit(';', 1)[0])


def main():
    md = io.open(os.path.join(ROOT, 'README.md'), encoding='utf-8').read()
    runs = load_runs()
    ids = {r['id'] for r in runs}
    bad = []

    # 1) README가 인용한 id가 실제로 있는지
    #    스킬 이름과 빼 둔 회차는 미리 제외한다.
    skills = {'company-template', 'frontend-design', 'korean-proofread'}
    held = set()
    hold_dir = os.path.join(BASE, '_보류')
    if os.path.isdir(hold_dir):
        held = {f[:-5] for f in os.listdir(hold_dir) if f.endswith('.json')}
    cited = set(re.findall(r'`([a-z][a-z0-9]+(?:-[a-z0-9]+)+)`', md))
    cited = {c for c in cited if not c.endswith(('.py', '.js', '.md'))} - skills - held
    ghost = sorted(cited - ids)
    if ghost:
        bad.append('README에만 있는 id: ' + ', '.join(ghost))

    # 2) 시나리오 표에 빠진 회차가 있는지
    missing = sorted(i for i in ids if '`%s`' % i not in md)
    if missing:
        bad.append('README에 없는 회차: ' + ', '.join(missing))

    # 3) 표에 적은 크레딧이 실측값과 같은지
    for r in runs:
        if not r.get('credit') or r.get('variants'):
            continue
        row = re.search(r'^\| `%s` \|(.+)$' % re.escape(r['id']), md, re.M)
        if not row:
            continue
        want = '{:,}'.format(r['credit'])
        if want not in row.group(1):
            bad.append('%s 표의 크레딧이 다름 (실측 %s)' % (r['id'], want))

    # 4) 검증 항목 수가 맞는지
    n = subprocess.run([os.environ.get('COMSPEC', 'cmd'), '/c',
                        'node', os.path.join(BASE, 'check.js')],
                       capture_output=True, text=True, encoding='utf-8')
    m = re.search(r'(\d+)/(\d+) 통과', n.stdout or '')
    if m:
        said = re.search(r'현재 (\d+)개 항목', md)
        if said and said.group(1) != m.group(2):
            bad.append('검증 항목 수가 다름 (README %s, 실제 %s)'
                       % (said.group(1), m.group(2)))

    # 5) 사다리 값이 회차의 실측 크레딧과 같은지
    #    한쪽만 고치면 화면에 서로 다른 숫자가 뜬다.
    try:
        import ladder
        pair = {
            '아침 브리핑': 'daily-brief',
            '주간보고 · 사내 표준 서식': 'weekly-team',
            '밀린 메일 정리': 'inbox-triage',
            '출입기록 점검 · 스킬 만들기': 'badge-check',
            'ISMS-P 심사 대응': 'isms-audit',
        }
        by_id = {r['id']: r for r in runs}
        for m in ladder.LADDER:
            rid = pair.get(m['name'])
            if not rid:
                bad.append('사다리에 짝지을 회차가 없음: ' + m['name'])
            elif by_id[rid]['credit'] != m['avg']:
                bad.append('%s 사다리 %d, 실측 %s'
                           % (m['name'], m['avg'], by_id[rid]['credit']))
            elif ('| %s | %s |' % (m['name'], '{:,}'.format(m['avg']))) not in md:
                bad.append('README 사다리 표에 없거나 값이 다름: ' + m['name'])
    except ImportError:
        pass

    # 6) 시나리오 수 표현
    said_n = re.search(r'뒤의 (\S+)은 실습용', md)
    if said_n:
        practice = len([r for r in runs if r['folder'] == '실습'])
        words = {2: '둘', 3: '셋', 4: '넷', 5: '다섯', 6: '여섯',
                 7: '일곱', 8: '여덟', 9: '아홉', 10: '열'}
        if said_n.group(1) != words.get(practice, ''):
            bad.append('실습 회차 수 표현이 다름 (README %s, 실제 %d개)'
                       % (said_n.group(1), practice))

    if bad:
        print('어긋난 곳 %d건' % len(bad))
        for b in bad:
            print('  ' + b)
        sys.exit(1)
    print('README와 데이터가 맞습니다. 시나리오 %d개.' % len(runs))


if __name__ == '__main__':
    main()
