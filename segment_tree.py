class SegmentTreeNode:
    def __init__(self, start, end, words):
        self.start = start
        self.end = end
        self.left = None
        self.right = None
        self.words = words
        self.min_word = words[0]
        self.max_word = words[-1]


class SegmentTree:
    def __init__(self):
        self.words = []
        self.root = None

    def _build(self, start, end):
        if start > end:
            return None
        if start == end:
            return SegmentTreeNode(start, end, [self.words[start]])
        mid = (start + end) // 2
        left = self._build(start, mid)
        right = self._build(mid + 1, end)
        node = SegmentTreeNode(start, end, self.words[start:end+1])
        node.left = left
        node.right = right
        node.min_word = self.words[start]
        node.max_word = self.words[end]
        return node

    def bulk_insert(self, words):
        if not words:
            return
        self.words = sorted(list(set(words)))  # unique + sorted
        self.root = self._build(0, len(self.words) - 1)

    def insert(self, word):
        if not word:
            return
        if word not in self.words:
            self.words.append(word)
            self.words.sort()
            self.root = self._build(0, len(self.words) - 1)

    def search(self, prefix: str):
        results = []
        self._search_recursive(self.root, prefix, results)
        return sorted(set(results))

    def _search_recursive(self, node, prefix, results):
        if not node:
            return
        if node.max_word < prefix or node.min_word > prefix:
            return

        if all(w.startswith(prefix) for w in node.words):
            results.extend(node.words)
            return

        for w in node.words:
            if w.startswith(prefix):
                results.append(w)

        self._search_recursive(node.left, prefix, results)
        self._search_recursive(node.right, prefix, results)

    def delete(self):
        pass

    def mem_usage(self):
        def count_nodes(node):
            return 0 if not node else 1 + count_nodes(node.left) + count_nodes(node.right)
        return (count_nodes(self.root) * 180) / 1024

    def complexity(self) -> dict:
        return {
            'time': 'O(log n)',
            'space': 'O(n)'
        }
