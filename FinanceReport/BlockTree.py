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
        return self._block.raw_text


class BlockTree:
    ''' pdf文件的文档框架'''

    def __init__(self):
        self._root = BlockNode(None)

    @property
    def root(self):
        return self._root

    def store(self):
        return {
            'root': self._root.store()
        }

    def restore(self, data: dict, blocks:Blocks):
        raw_root = data.get('root', {})
        self._root.restore(raw_root, blocks)

    def print_tree(self):
        self._print_tree("", self.root)

    def _print_tree(self, prefix, node):
        cur_prefix = prefix + "    "
        for child in node.children:
            if child.block.is_text_block and child.block.order_type != BlockOrderType.UNDEFINED:
                print("%s%s" % (cur_prefix, child.text))
            elif child.block.is_table_block:
                print("%s<Table>" % cur_prefix)
            self._print_tree(cur_prefix, child)
