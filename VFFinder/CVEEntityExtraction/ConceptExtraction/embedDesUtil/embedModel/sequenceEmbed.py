from collections import deque


def traverse_sequence(root):
    seq = []
    q = deque([root])
    while q:
        node = q.popleft()
        seq.append(str(node.label))
        for child in node.children:
            q.append(child)
    return seq


def embed_treesequence(description_tree, treesequence_model):
    seq = traverse_sequence(description_tree)
    tokens = [t for t in seq if isinstance(t, str)]
    if hasattr(treesequence_model, "encode"):
        return treesequence_model.encode(" ".join(tokens))
    return [float(len(tokens)), float(len(set(tokens)))]


