# -*- coding: utf-8 -*-
"""실습파일의 스킬 세 벌을 읽어 '사용자 지정' 화면 데이터를 만든다.

배포하는 zip 안의 SKILL.md를 그대로 읽으므로 스킬을 고치면 다시 돌리기만
하면 된다. 지시문 본문은 화면에 그대로 싣고, 첨부 파일은 이름과 크기만
싣는다. 사람 이름은 데모용으로 바꾼다.

사용법: python build_skills.py
"""
import io
import json
import os
import re
import subprocess
import sys
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
SRC = r'C:\Users\suminlee\OneDrive - Microsoft\실습파일.zip'

# 실제 화면의 '내 기술' 순서를 따른다.
ORDER = ['skill-korean-proofread', 'skill-company-template', 'skill-cowork-router']

# 스킬마다 화면에 붙는 부가 정보. SKILL.md에는 없는 값이다.
META = {
    'skill-korean-proofread': {
        'id': 'korean-proofread',
        'icon': 'doc',
        'path': '문서 > Coworker > skills > korean-proofread',
        'added': '8월 27일',
    },
    'skill-company-template': {
        'id': 'company-template',
        'icon': 'deck',
        'path': '문서 > Coworker > skills > company-template',
        'added': '9월 2일',
    },
    'skill-cowork-router': {
        'id': 'cowork-router',
        'icon': 'doc',
        'path': '문서 > Coworker > skills > cowork-router',
        'added': '9월 7일',
    },
}

# Cowork에 처음부터 들어 있는 기술. 끌 수 없다.
BUILTIN = [
    {'id': 'pdf', 'name': 'PDF', 'icon': 'pdf',
     'desc': 'Read, create, and manipulate PDF documents'},
    {'id': 'word', 'name': 'Word', 'icon': 'word',
     'desc': 'Read, create, and edit Word documents'},
    {'id': 'excel', 'name': 'Excel', 'icon': 'excel',
     'desc': 'Read, create, and manipulate Excel spreadsheets'},
    {'id': 'ppt', 'name': 'PowerPoint', 'icon': 'deck',
     'desc': 'Read, create, and edit PowerPoint presentations'},
]

# 플러그인 탭. 실제 화면의 설치 목록을 그대로 세운다.
PLUGINS = [
    {'name': '패브릭 IQ', 'on': False},
    {'name': 'Dynamics 365 Sales', 'on': False},
    {'name': 'Dynamics 365 ERP', 'on': False},
    {'name': 'Dynamics 365 Customer Service', 'on': False},
]


def frontmatter(text):
    """zip 안의 SKILL.md는 줄바꿈이 CRLF인 것이 섞여 있다. 먼저 고른다."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return '', text
    return m.group(1), text[m.end():]


def field(fm, key):
    """YAML 한 줄 값과 블록 값(|) 둘 다 받는다."""
    m = re.search(r'^%s:\s*\|\s*\n((?:[ \t]+.*\n?)+)' % key, fm, re.M)
    if m:
        lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
        return ' '.join(lines)
    m = re.search(r'^%s:\s*(.+)$' % key, fm, re.M)
    if not m:
        return ''
    return m.group(1).strip().strip('"').strip("'")


def kb(n):
    return '%.2fKB' % (n / 1024.0) if n < 1024 * 1024 else '%.1fMB' % (n / 1048576.0)


def main():
    inner = {}
    with zipfile.ZipFile(SRC) as z:
        for n in z.namelist():
            b = os.path.basename(n)
            if b.startswith('skill-') and b.endswith('.zip'):
                inner[b[:-4]] = z.read(n)

    items = []
    for key in ORDER:
        meta = META[key]
        with zipfile.ZipFile(io.BytesIO(inner[key])) as z:
            body_src = z.read('SKILL.md').decode('utf-8')
            files = [{'name': i.filename, 'size': kb(i.file_size)}
                     for i in z.infolist() if not i.is_dir()]
        fm, body = frontmatter(body_src)

        # 데모용으로 사람 이름을 바꾼다.
        body = body.replace('Sumin Lee', 'Copilot User').replace('Sumin', 'Copilot User')

        items.append({
            'id': meta['id'],
            'name': field(fm, 'name') or meta['id'],
            'icon': meta['icon'],
            'desc': field(fm, 'description'),
            'body': body.strip(),
            'files': files,
            'path': meta['path'],
            'added': meta['added'],
            'owner': '내가 만든 항목',
        })

    data = {
        'tab': '기술',
        'skills': items,
        'builtin': BUILTIN,
        'plugins': PLUGINS,
    }

    out = os.path.join(ROOT, 'data', 'skills.js')
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write('/* 자동 생성 파일. _작업/build_skills.py 로 다시 만든다. */\n')
        fh.write('window.COWORK_SKILLS = ')
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write(';\n')

    print('skills.js %d개 기술  %.1f KB'
          % (len(items), os.path.getsize(out) / 1024))
    for s in items:
        print('  %-18s 본문 %5d자  첨부 %d개  %s'
              % (s['name'], len(s['body']), len(s['files']), s['added']))


if __name__ == '__main__':
    main()
