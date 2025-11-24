class AVLNode:
    def __init__(self, key: str):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1  # Height of the node
        
class AVLTree:

    def __init__(self):
        self.root = None
        self.word_count = 0

    def _height(self, node: AVLNode) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: AVLNode) -> int:
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node: AVLNode):
        node.height = 1 + max(self._height(node.left),
                              self._height(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def _balance(self, node: AVLNode) -> AVLNode:
        balance = self._balance_factor(node)

        # Left heavy
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right heavy
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def insert(self, word: str):
        def _insert(node: AVLNode, word: str) -> AVLNode:
            if not node:
                self.word_count += 1
                return AVLNode(word)

            if word < node.key:
                node.left = _insert(node.left, word)
            elif word > node.key:
                node.right = _insert(node.right, word)
            else:
                return node  # Duplicate, do nothing

            self._update_height(node)
            return self._balance(node)

        self.root = _insert(self.root, word)

    def search(self, prefix: str) -> list[str]:
        suggestions = []
        self._collect_prefix_matches(self.root, prefix, suggestions)
        return sorted(list(set(suggestions)))

    def _collect_prefix_matches(self, node: AVLNode, prefix: str, suggestions: list):
        if not node:
            return
        self._collect_prefix_matches(node.left, prefix, suggestions)

        if node.key.startswith(prefix):
            suggestions.append(node.key)

        self._collect_prefix_matches(node.right, prefix, suggestions)

    def _min_value_node(self, node: AVLNode) -> AVLNode:
        current = node
        while current.left:
            current = current.left
        return current

    def bulk_insert(self, words):
        for word in words:
            self.insert(word)

    def mem_usage(self) -> float:
        def count_nodes(node: AVLNode) -> int:
            if not node:
                return 0
            return 1 + count_nodes(node.left) + count_nodes(node.right)

        node_count = count_nodes(self.root)
        return (node_count * 150) / 1024  # Convert to KB

    def complexity(self) -> dict:
        return {
            'time': 'O(log n)',  # n = number of words
            'space': 'O(n)'  # n = number of words
        }
