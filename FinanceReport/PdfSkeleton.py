import logging

from FinanceReport.BlockTree import BlockTree, BlockNode
from pdf2docx.common.Collection import Collection
from pdf2docx.common.share import BlockOrderType
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

    def build_skeleton(self):
        blocks = self._get_skeleton_blocks()

        def type_in_parent(type:BlockOrderType, node:BlockNode):
            while node is not None:
                if node.block and node.block.order_type == type:
                    return (True, node.parent)
                node = node.parent
            return (False, None)

        tree = BlockTree()
        node = tree.root
        cur_order_type = blocks[0].order_type
        for index, block in enumerate(blocks):
            print("%s %s" % (block.order_type, block.raw_text))
            type = block.order_type
            if type == cur_order_type:   # 当前层加入
                node.add_child(block)
            else:
                (in_parent, parent_node) = type_in_parent(type, node)   # 加入上一层
                if in_parent:
                    node = parent_node
                    node.add_child(block)
                    cur_order_type = block.order_type
                else:    # 加入下一层
                    node = node.children[-1]
                    node.add_child(block)
                    cur_order_type = type

        tree.print_tree()




    def get_skeleton_str(self):
        blocks = self._retrieve_blocks()
        for block in blocks:
            if block.is_text_block:
                print(block.raw_text)
            elif block.is_table_block:
                print("<TABLE>")


    # def get_font_size(self):
    #     blocks = self._pdf_blocks()
    #     for block in blocks:
    #         if block.is_text_block:
    #             print("%f  %s" % (block.font_size, block.raw_text))
    #         elif block.is_table_block:
    #             print("<TABLE>")


    # def get_indent_space(self):
    #     blocks = self._pdf_blocks()
    #     for block in blocks:
    #         if block.is_text_block:
    #             print("%f  %s" % (block.indent_space, block.raw_text))
    #         elif block.is_table_block:
    #             print("<TABLE>")


    def _pdf_blocks(self):
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