class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        if not node.is_end_of_word:
            node.is_end_of_word = True
            self.word_count += 1

    def search(self, prefix: str) -> list[str]:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        suggestions = []
        self._collect_words(node, prefix, suggestions)
        return sorted(list(set(suggestions)))

    def _collect_words(self, node: TrieNode, current_prefix: str, suggestions: list):
        if node.is_end_of_word:
            suggestions.append(current_prefix)

        for char, child in node.children.items():
            self._collect_words(child, current_prefix + char, suggestions)

    def bulk_insert(self, words):
        for word in words:
            self.insert(word)

    def mem_usage(self) -> float:
        def count_nodes(node: TrieNode) -> int:
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        node_count = count_nodes(self.root)
        return (node_count * 100) / 1024  # Convert to KB

    def complexity(self) -> dict:
        return {
            'time': 'O(L)',
            'space': 'O(N*L)'
        }
