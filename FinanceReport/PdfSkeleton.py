import logging

from FinanceReport.BlockTree import BlockTree, BlockNode
from pdf2docx.common.Collection import Collection
from pdf2docx.common.share import BlockOrderType
from pdf2docx.page.Pages import Pages
from pdf2docx.layout.Blocks import Blocks
import re

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


    def _get_skeleton_blocks(self):
        num_exp = "[A-Za-z0-9一二三四五六七八九十]+"
        reg_exp = "^\s*(([（\(]?%s[）\)])|(%s、)|(第%s节)).*$" % (num_exp, num_exp, num_exp)
        pattern = re.compile(reg_exp)

        blocks = self._pdf_blocks()
        #统计不同字号的文字数量， 最大文字数量的字号以下的文字大概率不是框架标题
        statistics = {} # type: dict [float, Blocks]
        for block in blocks:
            if block.is_text_block:
                font_size = block.font_size
                if font_size in statistics:
                    statistics[font_size] += len(block.raw_text)
                else:
                    statistics[font_size] = len(block.raw_text)

        sorted_stat = sorted(statistics.items(), key=lambda v:v[1], reverse=True)
        article_font_size = sorted_stat[0][0]

        matched_blocks = Collection()
        for block in blocks:
            if block.is_text_block:
                match = re.match(pattern, block.raw_text)
                if match and block.font_size > article_font_size:  #只有大于文章的主要内容的字号才作为标题
                    block.order_num = match.group(1)
                    matched_blocks.append(block)
                else:
                    block.order_num = ""
        return (matched_blocks, blocks)

    def _pdf_blocks(self):
        """ Returns: Blocks: pdf文件中所有的block， 按照文件顺序 """
        blocks = Blocks()
        for page in self._pages:
            blocks.extend(page.blocks)
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

    def print_tables(self):
        for deep, node in self.tree._head_first_traverse(0, self.tree.root):
            if node.block.is_text_block and node.block.order_type != BlockOrderType.UNDEFINED:
                print("%s%s" % ("  " * deep, node.text))
            elif node.block.is_table_block:
                title_node = node.pre_node
                while title_node is not None: #从兄弟上获得title
                    if title_node.block.order_type != BlockOrderType.UNDEFINED:
                        break
                    title_node = title_node.pre_node
                if title_node is None:
                    title_node = node.parent

                print("%s%s" % ("  " * deep, title_node.block.raw_text))
                print("%s<Table %d X %d>" % ("  " * deep, node.block.num_rows, node.block.num_cols))