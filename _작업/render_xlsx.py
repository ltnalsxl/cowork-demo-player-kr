# -*- coding: utf-8 -*-
"""엑셀 산출물을 PDF로 굽고 페이지별 PNG 미리보기를 만든다.

Excel COM은 쓰지 않는다. OneDrive에 있는 통합 문서를 COM으로 열면
공동 편집 세션이 잡혀 파일이 잠기기 때문이다. LibreOffice headless로
PDF를 만들고 PyMuPDF로 자른다.

사용법: python render_xlsx.py <xlsx 경로> <출력 폴더> <접두어> [최대장수]
"""
import os
import shutil
import subprocess
import sys
import tempfile

SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'
WIDTH = 900


def fit_copy(src, workdir):
    """폭에 맞춰 인쇄되도록 임시 사본의 페이지 설정만 바꾼다.

    LibreOffice는 엑셀의 기본 인쇄 설정을 그대로 따르는데, 시트가 넓으면
    오른쪽이 잘린 채 PDF가 나온다. 원본은 Cowork가 만든 그대로 두어야
    하므로 사본에만 손댄다.
    """
    import openpyxl
    dst = os.path.join(workdir, 'fit_' + os.path.basename(src))
    wb = openpyxl.load_workbook(src)
    for ws in wb.worksheets:
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.page_setup.orientation = 'landscape'
        ws.page_margins.left = ws.page_margins.right = 0.3
        ws.page_margins.top = ws.page_margins.bottom = 0.3
    wb.save(dst)
    wb.close()
    return dst


def to_pdf(src, workdir):
    subprocess.run(
        [SOFFICE, '--headless', '--norestore',
         '--convert-to', 'pdf:calc_pdf_Export',
         '--outdir', workdir, os.path.abspath(src)],
        check=True, capture_output=True, timeout=300)
    name = os.path.splitext(os.path.basename(src))[0] + '.pdf'
    return os.path.join(workdir, name)


def main():
    src, out, pre = sys.argv[1], sys.argv[2], sys.argv[3]
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    os.makedirs(out, exist_ok=True)

    work = tempfile.mkdtemp(prefix='xlsxrender_')
    try:
        pdf = to_pdf(fit_copy(src, work), work)
        import fitz
        doc = fitz.open(pdf)
        n = min(len(doc), cap)
        for i in range(n):
            page = doc[i]
            zoom = WIDTH / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            dst = os.path.join(out, '%s_%02d.png' % (pre, i + 1))
            pix.save(dst)
            print('  %s  %dx%d  %.0fKB'
                  % (os.path.basename(dst), pix.width, pix.height,
                     os.path.getsize(dst) / 1024.0))
        print('%s: PDF %d쪽 중 %d장 렌더' % (os.path.basename(src), len(doc), n))
        doc.close()
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
