import re

from pdf2docx.common.Block import Block
from pdf2docx.common.share import BlockOrderType
from pdf2docx.layout.Blocks import Blocks
from pdf2docx.text.TextBlock import TextBlock


class BlockNode:
    def __init__(self, block:TextBlock, parent = None):
        self._id = id(self)
        self._block = block
        self._children = []
        self._parent = parent
        self._pre_node = None
        self._next_node = None
        self._title = None

    def add_child(self, block:TextBlock):
        node = BlockNode(block, parent=self)
        self._children.append(node)

    def store(self):
        return {
            'id': self._id,
            'block': self._block.id if self._block is not None else 0,
            'children': [node.store() for node in self._children],
        }

    def restore(self, data: dict, blocks:Blocks):
        self._id = data.get('id', 0)
        block_id = data.get('block', 0)
        self._block = blocks.find_block(block_id)
        for raw_node in data.get('children', []):
            node = BlockNode(block=None, parent=self)
            node.restore(raw_node, blocks)
            self._children.append(node)

    def to_json(self):
        def _get_table_texts(node:BlockNode):
            table_texts = []
            for row in node.block._rows:
                cells_text = [cell.text for cell in row._cells]
                table_texts.append(cells_text)
            return table_texts

        def _get_node_path(node: BlockNode):
            path = ""
            p = node.parent
            while p is not None:
                path = "%s/%s" % (p.text, path)
                p = p.parent
            return path

        if not self._block or (self._block.is_text_block and self._block.order_type != BlockOrderType.UNDEFINED):
            return {
                'type': 'title',
                'text': self.text,
                'path': _get_node_path(self),
                'children': [node.to_json() for node in self._children]
            }
        elif self._block and  self._block.is_table_block:
            return {
                'type': 'table',
                'title': self._get_table_title(),
                'text': _get_table_texts(self),
                'path': _get_node_path(self)
            }
        else:
            return {
                'type': 'str',
                'text': 'inter-title',
                'path': _get_node_path(self),

            }

    # 获得table的标题
    def _get_table_title(self):
        if not self.block.is_table_block: return ""

        title_node = self.pre_node
        while title_node is not None:  # 从兄弟上获得title
            if title_node.block.order_type != BlockOrderType.UNDEFINED:
                break
            title_node = title_node.pre_node
        if title_node is None:
            title_node = self.parent

        return re.sub(BlockTree.index_pattern, "", title_node.block.raw_text)

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def pre_node(self):
        return self._pre_node

    @pre_node.setter
    def pre_node(self, node):
        self._pre_node = node

    @property
    def next_node(self):
        return self._next_node

    @next_node.setter
    def next_node(self, node):
        self._next_node = node

    @property
    def block(self):
        return self._block

    @property
    def children(self):
        return self._children

    @property
    def text(self):
        return self._block.raw_text if self._block else ""


class BlockTree:
    ''' pdf文件的文档框架'''

    _num_exp = "[A-Za-z0-9一二三四五六七八九十]+"
    _reg_exp = "^\s*(([（\(]?%s[）\)])|(%s、)|(第%s节))" % (_num_exp, _num_exp, _num_exp)
    index_pattern = re.compile(_reg_exp)

    def __init__(self):
        self._root = BlockNode(None)

    @property
    def root(self):
        return self._root

    def store(self):
        return {
            'root': self._root.store()
        }

    def to_json(self):
        json_data =  self._root.to_json()
        return json_data["children"]

    def restore(self, data: dict, blocks:Blocks):
        raw_root = data.get('root', {})
        self._root.restore(raw_root, blocks)

    def print_tree(self):
        for deep, node in self._head_first_traverse(0, self.root):
            if node.block.is_text_block and node.block.order_type != BlockOrderType.UNDEFINED:
                print(f"{'  ' * deep}{node.text}")
            elif node.block.is_table_block:
                print(f"{'  ' * deep}<Table {node.block.num_rows} X {node.block.num_cols}> header: {len(node.block.header)} lines. Title:{node._get_table_title()}")

    def _head_first_traverse(self, deep:int, node:BlockNode):
        deep += 1
        for child in node.children:
            yield deep, child
            yield from self._head_first_traverse(deep, child)

    def _children_first_traverse(self, deep:int, node:BlockNode):
        deep += 1
        for child in node.children:
            yield from self._children_first_traverse(deep, child)
            yield deep, child


