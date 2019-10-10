from src.model.syntax_node import SyntaxNode


class SyntaxTree:
    def __init__(self,
                 root: SyntaxNode = None,
                 current_level: int = 1):
        if root is None:
            root = SyntaxNode("root", [])
        self.current_level = current_level
        self.root = root
        self.current_node = root

    def add_node_to_current_level(self, node: SyntaxNode):
        self.current_node.body.append(node)

    def branch_with_new_node(self, node: SyntaxNode):
        self.add_node_to_current_level(node)
        node.parent = self.current_node
        self.current_node = node
        self.current_level += 1

    def return_to_upper_level(self):
        self.current_node = self.current_node.parent
        self.current_level -= 1
