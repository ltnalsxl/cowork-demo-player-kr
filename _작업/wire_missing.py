# -*- coding: utf-8 -*-
"""미리보기가 비어 있던 산출물에 실제 파일과 페이지 이미지를 붙인다.

원본을 assets/artifacts 아래로 복사하고 PDF를 거쳐 PNG로 자른 뒤
_작업/runs/*.json 의 artifacts 항목을 갱신한다.

사용법: python wire_missing.py
"""
import glob
import json
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
ART = os.path.join(ROOT, 'assets', 'artifacts')

CAM = (r'C:\Users\suminlee\OneDrive - Microsoft\문서\Microsoft Scout'
       r'\Cowork GO+ Delivery Asset\사용자교육-3시간\05_촬영용')
WORK = (r'C:\Users\suminlee\OneDrive - Microsoft\문서\Microsoft Scout\_작업')

SRC_HTML = os.path.join(CAM, '공공AI사업_추진체계_유연화_제안요청서_분석보고서.html')
SRC_PPTX = os.path.join(WORK, 'sample-proposal-output.pptx')
SRC_XLSX = os.path.join(CAM, '밀린 메일·Teams 정리 추적표 (2026-08-20~09-03).xlsx')


def rel(p):
    return p.replace(ROOT + os.sep, '').replace(os.sep, '/')


def pdf_to_png(pdf, out_dir, prefix, width=900):
    import fitz
    for old in glob.glob(os.path.join(out_dir, prefix + '_*.png')):
        os.remove(old)
    d = fitz.open(pdf)
    made = []
    for i, page in enumerate(d, 1):
        zoom = width / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        p = os.path.join(out_dir, '%s_%02d.png' % (prefix, i))
        pix.save(p)
        made.append(rel(p))
    d.close()
    return made


def ppt_to_pdf(src, pdf):
    import win32com.client as win32
    app = win32.Dispatch('PowerPoint.Application')
    try:
        pres = app.Presentations.Open(os.path.abspath(src),
                                      ReadOnly=True, WithWindow=False)
        pres.SaveAs(os.path.abspath(pdf), 32)  # ppSaveAsPDF
        pres.Close()
    finally:
        app.Quit()


def xls_to_pdf(src, pdf):
    import win32com.client as win32
    app = win32.Dispatch('Excel.Application')
    app.Visible = False
    app.DisplayAlerts = False
    try:
        wb = app.Workbooks.Open(os.path.abspath(src), ReadOnly=True)
        for ws in wb.Worksheets:
            ws.PageSetup.Zoom = False
            ws.PageSetup.FitToPagesWide = 1
            ws.PageSetup.FitToPagesTall = False
            ws.PageSetup.Orientation = 2  # 가로
        wb.ExportAsFixedFormat(0, os.path.abspath(pdf))
        wb.Close(False)
    finally:
        app.Quit()


def html_to_png(src, out_png, width=1100):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': width, 'height': 900},
                        device_scale_factor=1)
        pg.goto('file:///' + os.path.abspath(src).replace('\\', '/'))
        pg.wait_for_timeout(1200)
        pg.screenshot(path=out_png, full_page=True)
        b.close()
    return rel(out_png)


def load(name):
    with open(os.path.join(BASE, 'runs', name + '.json'), encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(BASE, 'runs', name + '.json'), 'w',
              encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')


def main():
    rfp_dir = os.path.join(ART, 'rfp')
    inbox_dir = os.path.join(ART, 'inbox')
    os.makedirs(rfp_dir, exist_ok=True)
    os.makedirs(inbox_dir, exist_ok=True)

    # 1) 제안요청서 분석 보고서(HTML)
    html_dst = os.path.join(rfp_dir, 'rfp-분석보고서.html')
    shutil.copyfile(SRC_HTML, html_dst)
    html_png = html_to_png(html_dst, os.path.join(rfp_dir, 'rfp_html_01.png'))
    print('html  ', html_png)

    # 2) 제안요약서(PPTX)
    pptx_dst = os.path.join(rfp_dir, 'rfp-제안요약서.pptx')
    shutil.copyfile(SRC_PPTX, pptx_dst)
    tmp = os.path.join(rfp_dir, '_tmp.pdf')
    ppt_to_pdf(pptx_dst, tmp)
    ppt_pages = pdf_to_png(tmp, rfp_dir, 'rfp_ppt')
    os.remove(tmp)
    print('pptx  ', len(ppt_pages), '장')

    # 3) 밀린 메일 정리 추적표(XLSX)
    xlsx_dst = os.path.join(inbox_dir, '밀린메일-정리-추적표.xlsx')
    shutil.copyfile(SRC_XLSX, xlsx_dst)
    tmp = os.path.join(inbox_dir, '_tmp.pdf')
    xls_to_pdf(xlsx_dst, tmp)
    xls_pages = pdf_to_png(tmp, inbox_dir, 'inbox')
    os.remove(tmp)
    print('xlsx  ', len(xls_pages), '쪽')

    # ---- runs json 갱신 ----
    doc_pages = ['assets/artifacts/tc01/doc_%02d.png' % i for i in (1, 2, 3)]

    r = load('weekly-team')
    a = r['artifacts'][0]
    a.pop('labeled', None)
    a['meta'] = '3쪽 · 표 4개 · 사내 표준 서식'
    a['file'] = 'assets/artifacts/tc01/주간업무보고.docx'
    a['thumb'] = doc_pages[0]
    a['pages'] = doc_pages
    save('weekly-team', r)

    r = load('inbox-triage')
    a = r['artifacts'][0]
    a.pop('labeled', None)
    a['meta'] = '시트 2개 · 밀린 항목 7건 · 집계 수식'
    a['file'] = rel(xlsx_dst)
    a['thumb'] = xls_pages[0]
    a['pages'] = xls_pages
    save('inbox-triage', r)

    for name in ('rfp-deck', 'rfp-sonnet'):
        r = load(name)
        h, p = r['artifacts'][0], r['artifacts'][1]
        h['file'] = rel(html_dst)
        h['thumb'] = html_png
        h['pages'] = [html_png]
        p['meta'] = '%d장 · 사내 표준 서식' % len(ppt_pages)
        p['file'] = rel(pptx_dst)
        p['thumb'] = ppt_pages[0]
        p['pages'] = ppt_pages
        save(name, r)

    subprocess.check_call([sys.executable, os.path.join(BASE, 'build.py')])


if __name__ == '__main__':
    main()
