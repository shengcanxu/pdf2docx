import logging

from pdf2docx.page.Page import Page
from pdf2docx.page.Pages import Pages
from pdf2docx.layout.Blocks import Blocks, Block
from pdf2docx.layout import Section

# logging
from pdf2docx.text.TextBlock import TextBlock

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")


class PdfSkeleton:
    '''
    从已经分析好的pdf Converter类作为输入， 并分析和形成PDF文件的框架结构
    '''

    def __init__(self, pages:Pages):
        self._pages = pages

    def _retrieve_skeleton(self):
        pass


    def get_skeleton_str(self):
        blocks = self._retrieve_blocks()
        for block in blocks:
            if block.is_text_block:
                print(block.raw_text)
            elif block.is_table_block:
                print("<TABLE>")


    def get_font_size(self):
        blocks = self._retrieve_blocks()
        for block in blocks:
            if block.is_text_block:
                for line in block.lines:
                    print("%f  %s" % (line.font_size, line.raw_text))
            elif block.is_table_block:
                print("<TABLE>")


    def get_indent_space(self):
        blocks = self._retrieve_blocks()
        for block in blocks:
            if block.is_text_block:
                for line in block.lines:
                    print("%f  %s" % (line.indent_space, line.raw_text))
            elif block.is_table_block:
                print("<TABLE>")


    def _retrieve_blocks(self):
        """
        Returns:
            Blocks: pdf文件中所有的block， 按照文件顺序
        """
        blocks = Blocks()
        for page in self._pages:
            for section in page.sections:
                for column in section:
                    blocks.extend(column.blocks)
        return blocks