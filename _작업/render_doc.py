# -*- coding: utf-8 -*-
"""Word 산출물을 PDF로 굽고 페이지별 PNG 미리보기를 만든다.

Word COM으로 PDF를 만들고 PyMuPDF로 자른다. 뷰어가 쓰는 폭에 맞춰
가로 800px 언저리로 렌더링한다.

사용법: python render_doc.py <docx 경로> <출력 폴더> [접두어]
"""
import os
import sys
import glob


def to_pdf(src, pdf):
    import win32com.client as win32
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    try:
        doc = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
        doc.SaveAs(os.path.abspath(pdf), FileFormat=17)  # wdFormatPDF
        doc.Close(False)
    finally:
        word.Quit()


def to_png(pdf, out_dir, prefix):
    import fitz
    d = fitz.open(pdf)
    made = []
    for i, page in enumerate(d, 1):
        # 가로 800px 언저리가 되도록 배율을 잡는다.
        zoom = 800 / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        p = os.path.join(out_dir, '%s_%02d.png' % (prefix, i))
        pix.save(p)
        made.append(p)
    d.close()
    return made


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, out_dir = sys.argv[1], sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else 'doc'
    os.makedirs(out_dir, exist_ok=True)

    for old in glob.glob(os.path.join(out_dir, prefix + '_*.png')):
        os.remove(old)

    pdf = os.path.join(out_dir, '_tmp.pdf')
    to_pdf(src, pdf)
    made = to_png(pdf, out_dir, prefix)
    os.remove(pdf)

    for p in made:
        print('%s  %.0f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))


if __name__ == '__main__':
    main()
