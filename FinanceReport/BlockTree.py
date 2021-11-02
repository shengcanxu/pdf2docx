from pdf2docx.common.Block import Block
from pdf2docx.text.TextBlock import TextBlock


class BlockNode:
    def __init__(self, block:TextBlock, parent = None):
        self._block = block
        self._children = []
        self._parent = parent

    def add_child(self, block:TextBlock):
        node = BlockNode(block, parent=self)
        self._children.append(node)

    @property
    def parent(self):
        return self._parent

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

    def print_tree(self):
        self._print_tree("", self.root)

    def _print_tree(self, prefix, node):
        cur_prefix = prefix + "    "
        for child in node.children:
            print("%s%s" % (cur_prefix, child.text))
            self._print_tree(cur_prefix, child)
