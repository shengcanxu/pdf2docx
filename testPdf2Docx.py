from FinanceReport.PdfSkeleton import PdfSkeleton
from pdf2docx import Converter
from datetime import datetime, timedelta
import json

# pdf_file = 'test3.pdf'
pdf_file = 'unresolved.pdf'
json_file = 'unresolved.json'
docx_file = 'sample.docx'


def parsPDFtoJson():
    cv = Converter(pdf_file)
    settings = cv.default_settings
    cv = cv.load_pages()
    totalPageNum = len(cv.pages)

    for pageNum in range(0, totalPageNum):
    # for pageNum in [68]:
        print("starting on page: %d" % pageNum)
        cv = cv.load_pages(start=pageNum, end=pageNum+1)
        cv = cv.parse_document(**settings)
        cv = cv.parse_pages(**settings)

    cv = cv.parse_document(**settings)
    cv = cv.parse_pages(**settings)

    data = cv.store()
    strData = json.dumps(data)
    with open(json_file,"w") as f:
        f.write(strData)

    cv.close()


def restoreFromJson():
    cv = Converter(pdf_file)
    settings = cv.default_settings
    with open(json_file, "r") as f:
        strData = f.read()
        data = json.loads(strData)
        cv.restore(data)
    return cv


# 114 , 80

# parsPDFtoJson()
cv = restoreFromJson()
print(cv.pages.__len__())
skeleton = PdfSkeleton(cv.pages)
# skeleton.get_skeleton_str()
# skeleton.get_indent_space()
skeleton.get_font_size()
