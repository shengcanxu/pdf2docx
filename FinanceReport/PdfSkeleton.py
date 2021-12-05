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
        self._skeleton_list = None

    @property
    def tree(self):
        if self._tree is None:
            self._tree = self.build_skeleton()
        return self._tree

    @property
    def skeleton_list(self):
        if self._skeleton_list is None:
            self._skeleton_list = self.get_skeleton_list()
        return self._skeleton_list

    def build_skeleton(self):
        (skeleton_blocks, blocks) = self._get_skeleton_blocks()
        tree = self._build_tree(blocks, skeleton_blocks)
        self._connect_children(tree)

        self._tree = tree
        return tree

    # 获得PDF文档的章节目录以list形式展现， 去掉不重要的文字内容，表格保留
    def get_skeleton_list(self):
        (skeleton_blocks, blocks) = self._get_skeleton_blocks()
        self._skeleton_list = [block for block in blocks if block.is_table_block or block.order_type != BlockOrderType.UNDEFINED]
        return self._skeleton_list

    def print_skeleton_list(self):
        for block in self._skeleton_list:
            if block.is_text_block and block.order_type != BlockOrderType.UNDEFINED:
                print(block.raw_text)
            elif block.is_table_block:
                # print(f"<Table {block.num_rows} X {block.num_cols}> header: {len(block.header)} lines. Title:{node._get_table_title()}")
                print(f"<Table {block.num_rows} X {block.num_cols}> header: {len(block.header)} lines. Title:to_be_determined")

    def skeleton_list_to_json(self):
        def _get_table_texts(block):
            table_texts = []
            for row in block._rows:
                cells_text = [cell.text for cell in row._cells]
                table_texts.append(cells_text)
            return table_texts

        json_list = []
        for block in self._skeleton_list:
            if block.is_table_block:
                json_list.append({
                    'type': 'table',
                    'title': 'to_be_determined',
                    'text': _get_table_texts(block)
                })
            else:
                json_list.append({
                    'type': 'title',
                    'text': block.raw_text,
                })
        return json_list


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
                # 只有大于文章的主要内容的字号, 或者字号相等但是是bold, 或者字号想等但是字体是黑体（SimHei）
                if match and (block.font_size > article_font_size or (block.font_size == article_font_size and (block.font == 'SimHei' or block.is_bold_text))):
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
        # return self.tree.store()

        # 放弃restore tree结构， 改成restore list结构， 因为list结构已经足够了
        return [block.id for block in self.skeleton_list]

    def restore(self, data: dict):
        # self._tree = BlockTree()
        # blocks = self._pdf_blocks()
        # self._tree.restore(data, blocks)
        # self._connect_children(self.tree)

        # 放弃restore tree结构， 改成restore list结构， 因为list结构已经足够了
        blocks = self._pdf_blocks()
        self._skeleton_list = [blocks.find_block(block_id) for block_id in data]
