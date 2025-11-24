import bisect


class SuffixTreeNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_suffix = False
        # To track which words end here, but for simplicity, we'll store words directly
        self.word_indices = set()


class SuffixTree:
    def __init__(self):
        self.root = SuffixTreeNode()
        self.words = []  # Sorted list for binary search

    def insert(self, word: str):
        if word in self.words:
            return
        bisect.insort(self.words, word)
        # Build suffix tree for the word (for completeness, though not used for prefix search)
        for i in range(len(word)):
            suffix = word[i:]
            node = self.root
            for char in suffix:
                if char not in node.children:
                    node.children[char] = SuffixTreeNode()
                node = node.children[char]
            node.is_end_of_suffix = True

    def search(self, prefix: str) -> list[str]:
        if not hasattr(self, 'words') or not self.words:
            return []
        # Use binary search to find words starting with prefix
        start = bisect.bisect_left(self.words, prefix)
        end = bisect.bisect_right(self.words, prefix + '\uffff')
        return [w for w in self.words[start:end] if w.startswith(prefix)]

    def bulk_insert(self, words):
        unique_words = sorted(set(words))
        self.words = unique_words
        for word in unique_words:
            # Build suffix tree
            for i in range(len(word)):
                suffix = word[i:]
                node = self.root
                for char in suffix:
                    if char not in node.children:
                        node.children[char] = SuffixTreeNode()
                    node = node.children[char]
                node.is_end_of_suffix = True

    def mem_usage(self) -> float:
        def count_nodes(node: SuffixTreeNode) -> int:
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        node_count = count_nodes(self.root)
        return (node_count * 120) / 1024  # Rough estimate in KB

    def complexity(self) -> dict:
        return {
            'time': 'O(n)',  # Linear search for prefix
            'space': 'O(n^2)'  # Worst case for suffix tree
        }
