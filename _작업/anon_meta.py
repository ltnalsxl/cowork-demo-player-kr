# -*- coding: utf-8 -*-
"""저장소에 올릴 산출물의 메타데이터를 익명화한다.

본문은 이미 손봤고, docProps에 남은 작성자·최종수정자·회사·테넌트 주소를 지운다.
Office 파일은 zip이라 해당 XML만 바꿔 다시 묶는다.
"""
import glob
import os
import re
import shutil
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.abspath(os.path.join(BASE, '..', 'assets', 'artifacts'))

AUTHOR = 'Copilot User'
COMPANY = ''

# 태그를 통째로 갈아 끼운다. 값 안에 테넌트 주소가 들어 있는 경우가 있다.
TAGS = {
    'dc:creator': AUTHOR,
    'cp:lastModifiedBy': AUTHOR,
    'lastModifiedBy': AUTHOR,
    'dc:title': '',
    'Company': COMPANY,
    'Manager': '',
}


def scrub_xml(text):
    for tag, val in TAGS.items():
        text = re.sub(r'<' + tag + r'>.*?</' + tag + r'>',
                      '<' + tag + '>' + val + '</' + tag + '>', text, flags=re.S)
        text = re.sub(r'<' + tag + r'\s*/>', '<' + tag + '>' + val + '</' + tag + '>', text)
    return text


def scrub(path):
    tmp = path + '.tmp'
    changed = False
    with zipfile.ZipFile(path) as zin:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith('docProps/') and item.filename.endswith('.xml'):
                    txt = data.decode('utf-8', 'ignore')
                    new = scrub_xml(txt)
                    if new != txt:
                        changed = True
                        data = new.encode('utf-8')
                zout.writestr(item, data)
    if changed:
        shutil.move(tmp, path)
    else:
        os.remove(tmp)
    return changed


def main():
    files = []
    for ext in ('docx', 'pptx', 'xlsx'):
        files += glob.glob(os.path.join(ART, '**', '*.' + ext), recursive=True)
    n = 0
    for f in sorted(files):
        if '_원본' in f:
            continue
        if scrub(f):
            n += 1
            print('  손봄  ' + os.path.relpath(f, ART))
    print('메타데이터 익명화 %d개' % n)


if __name__ == '__main__':
    main()
