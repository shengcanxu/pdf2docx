from FinanceReport.PdfSkeleton import PdfSkeleton
from pdf2docx import Converter
import json

# pdf_file = 'test2.pdf'
# json_file = 'test2.json'
pdf_file = 'unresolved.pdf'
json_file = 'unresolved.json'
docx_file = 'sample.docx'


def parse_pdf_to_json():
    cv = Converter(pdf_file)
    settings = cv.default_settings
    cv = cv.load_pages()
    totalPageNum = len(cv.pages)

    cv = cv.parse_document(**settings)
    cv = cv.parse_pages(**settings)

    data = cv.store()
    strData = json.dumps(data)
    with open(json_file,"w") as f:
        f.write(strData)

    cv.close()


def parse_page_on_index(index:int, num:int):
    cv = Converter(pdf_file)
    settings = cv.default_settings

    cv = cv.load_pages(start=index, end=index+num)
    cv = cv.parse_document(**settings)
    cv = cv.parse_pages(**settings)

    data = cv.store()
    strData = json.dumps(data)
    with open(json_file,"w") as f:
        f.write(strData)


def restore_from_json():
    cv = Converter(pdf_file)
    settings = cv.default_settings
    with open(json_file, "r") as f:
        strData = f.read()
        data = json.loads(strData)
        cv.restore(data)
    return cv


# parse_pdf_to_json()
# parse_page_on_index(72, 3)

cv = restore_from_json()

cv._combineTables()
# cv.block_tree.print_tree()
# cv.skeleton.print_tables()

aa=2
# skeleton = PdfSkeleton(cv.pages)
# skeleton.build_skeleton()
# skeleton.get_indent_space()
# skeleton.get_font_size()




# 需要在更多的pdf文件上测试 _remove_header_footer