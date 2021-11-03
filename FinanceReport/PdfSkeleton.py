import logging

from FinanceReport.BlockTree import BlockTree, BlockNode
from pdf2docx.common.Collection import Collection
from pdf2docx.common.share import BlockOrderType
from pdf2docx.page.Pages import Pages
from pdf2docx.layout.Blocks import Blocks, Block
from pdf2docx.layout import Section

# logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")


class PdfSkeleton:
    '''
    从已经分析好的pdf Converter类作为输入， 并分析和形成PDF文件的框架结构
    '''

    def __init__(self, pages:Pages):
        self._pages = pages
        self._tree = None

    @property
    def tree(self):
        if self._tree is None:
            self._tree = self.build_skeleton()
        return self._tree

    def build_skeleton(self):
        (skeleton_blocks, blocks) = self._get_skeleton_blocks()
        tree = self._build_tree(blocks, skeleton_blocks)
        self._connect_children(tree)

        self._tree = tree
        return tree

        # tables = self._pdf_tables()
        # for table in tables:
        #     print(table.text)
        #     print(" ")

    # 将树里面的列表节点左右连接起来
    def _connect_children(self, tree:BlockNode):
        def _connect(node:BlockNode):
            nodes = node.children
            length = len(nodes)
            if length == 1: return

            for index, child in enumerate(nodes):
                if index == 0:
                    child.next_node = nodes[index+1]
                elif index == length-1:
                    child.pre_node = nodes[index-1]
                else:
                    child.next_node = nodes[index + 1]
                    child.pre_node = nodes[index - 1]
                _connect(child)
        _connect(tree.root)

    # 根据文本创建pdf文档的树形架构
    def _build_tree(self, blocks, skeleton_blocks):
        def type_in_parent(type:BlockOrderType, pnode:BlockNode):
            if type == BlockOrderType.UNDEFINED: return (False, None)
            while pnode.block is not None:
                if pnode.block.order_type == type:
                    return (True, pnode.parent)
                pnode = pnode.parent
            return (False, None)

        tree = BlockTree()
        parent = tree.root
        cur_order_type = skeleton_blocks[0].order_type
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
                    if len(parent.children) == 0: continue
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
        """ Returns: Blocks: pdf文件中所有的block， 按照文件顺序 """
        blocks = Blocks()
        for page in self._pages:
            for section in page.sections:
                for column in section:
                    blocks.extend(column.blocks.sort_in_reading_order())
        return blocks

    def _pdf_tables(self):
        """ Returns: tables: pdf文件中所有的tables， 按照文件顺序 """
        blocks = self._pdf_blocks()
        return list(filter(lambda b: b.is_table_block, blocks))

    def store(self):
        return self.tree.store()

    def restore(self, data: dict):
        self._tree = BlockTree()
        blocks = self._pdf_blocks()
        self._tree.restore(data, blocks)
        self._connect_children(self.tree)