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
        (matched_blocks, blocks) = self._get_skeleton_blocks()
        tree = self._build_tree(blocks)
        #self._connect_children(tree)
        tree.print_tree()

    # 将树里面的列表节点左右连接起来
    def _connect_children(self, tree:BlockTree):
        node = tree.root
        def _connect(node):
            for index, child in enumerate(node.children):

                _connect(child)
        _connect(node)

    # 根据文本创建pdf文档的树形架构
    def _build_tree(self, blocks):
        def type_in_parent(type:BlockOrderType, pnode:BlockNode):
            if type == BlockOrderType.UNDEFINED: return (False, None)
            while pnode.block is not None:
                if pnode.block.order_type == type:
                    return (True, pnode.parent)
                pnode = pnode.parent
            return (False, None)

        tree = BlockTree()
        parent = tree.root
        cur_order_type = blocks[0].order_type
        for index, block in enumerate(blocks):
            type = block.order_type
            if type == cur_order_type:   # 当前层加入
                parent.add_child(block)
            else:
                (in_parent, parent_node) = type_in_parent(type, parent)   # 加入上一层
                if in_parent:
                    parent = parent_node
                    parent.add_child(block)
                    cur_order_type = type
                else:    # 加入下一层
                    parent = parent.children[-1]
                    parent.add_child(block)
                    cur_order_type = type

        return tree


    def get_skeleton_str(self):
        blocks = self._retrieve_blocks()
        for block in blocks:
            if block.is_text_block:
                match = re.match(pattern, block.raw_text)
                if match:
                    block.order_num = match.group(1)
                    matched_blocks.append(block)
                else:
                    block.order_num = ""
        return (matched_blocks, blocks)

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