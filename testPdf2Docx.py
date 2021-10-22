from pdf2docx import Converter
from datetime import datetime, timedelta

# pdf_file = 'test3.pdf'
pdf_file = 'unresolved.pdf'
docx_file = 'sample.docx'

# convert pdf to docx
cv = Converter(pdf_file)
# cv.convert(docx_file, pages=[19])      # all pages by default

settings = cv.default_settings
cv = cv.load_pages()
totalPageNum = len(cv.pages)

# for pageNum in range(0, totalPageNum):
for pageNum in [114]:
    print("starting on page: %d" % pageNum)
    cv = cv.load_pages(start=pageNum, end=pageNum+1)
    cv = cv.parse_document(**settings)
    cv = cv.parse_pages(**settings)

# cv.make_docx(docx_file)

cv.close()

