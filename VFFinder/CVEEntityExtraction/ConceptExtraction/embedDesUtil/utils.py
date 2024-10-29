


import json
import string
import warnings
import networkx as nx
import re
from nltk import Tree
from scipy.spatial import distance


class Node:
    id_counter = 0  # 类变量，用于生成唯一的 ID
    def __init__(self, label):
        self.id = Node.id_counter  # 将当前的 id_counter 值赋给新节点的 id
        Node.id_counter += 1  #
        self.label = label
        self.children = []


def parse_tree(tree_str):
    # 使用NLTK的Tree类将括号化的字符串转换为树
    nltk_tree = Tree.fromstring(tree_str)
    # 将NLTK的Tree转换为我们自定义的树
    return convert_tree(nltk_tree)


def convert_tree(nltk_tree):
    # 创建一个新的节点
    node = Node(nltk_tree.label())
    # 对于NLTK树中的每个子树，递归地转换为我们自定义的树
    for subtree in nltk_tree:
        if type(subtree) is Tree:
            node.children.append(convert_tree(subtree))
        else:
            node.children.append(Node(subtree))
    return node


def convert_tree_to_networkx_with_sorted_child(root):
    G = nx.DiGraph()
    stack = [(root, None)]  # (node, parent) pairs
    while stack:
        node, parent = stack.pop()
        G.add_node(node.id, label=node.label)  # 添加节点到图中
        if parent is not None:
            G.add_edge(parent.id, node.id)  # 添加边到图中
        for i in range(len(node.children) - 1, -1, -1):
            child = node.children[i]
            stack.append((child, node))

            # 如果不是第一个子节点，那么添加一条从上一个子节点到当前子节点的边
            if i > 0:
                G.add_edge(node.children[i - 1].id, child.id)
    return G


def find_leaves(node):
    # 如果一个节点没有子节点，那么它就是叶子节点
    if not node.children:
        return [node]

    # 如果一个节点有子节点，那么我们需要在它的所有子节点中寻找叶子节点
    leaves = []
    for child in node.children:
        leaves.extend(find_leaves(child))
    return leaves


def dfs(node, parent, depth, parents, depths):
    # 记录当前节点的父节点和深度
    parents[node] = parent
    depths[node] = depth
    # 遍历当前节点的每个子节点
    for child in node.children:
        dfs(child, node, depth + 1, parents, depths)

def lca(node1, node2, parents, depths):
    # 找到两个节点的最近公共祖先
    while node1 != node2:
        if depths[node1] > depths[node2]:
            node1 = parents[node1]
        else:
            node2 = parents[node2]
    return node1


def remove_dot_nodes(root):
    # If the root node's label is ".", return None
    if root.label in string.punctuation:
        return None

    # Recursively process children
    new_children = []
    for child in root.children:
        new_child = remove_dot_nodes(child)
        if new_child is not None:
            new_children.append(new_child)

    # Update children list
    root.children = new_children

    return root


def cut_flag_node(root, parent=None):
    # 遍历子节点
    for child in root.children[:]:  # 使用[:]复制列表以避免在迭代过程中修改列表
        cut_flag_node(child, root)

    # 检查当前节点是否需要被剪切
    if root.label in ["VUL", "VPV", "COMPONENT", "ATTACKER", "VICTIM"] and parent and len(parent.children) == 1:
        replace_node(parent, root)
        return True

    return False


def replace_node(node1, node2):
    '''

    :param node1:
    :param node2:
    :return:
    '''
    node1.label = node2.label
    node1.children = node2.children

def regulate_gpt_output(output:str):
    '''

    :param output:
    :return:
    '''
    output = output.strip()
    if output.startswith("OUTPUT:"):
        output = output[7:]
    output = output.strip()

    if output.startswith("INPUT:"):
        output = output[output.index("OUTPUT:"):]
        output = output[7:]
    output = output.strip()

    if output.startswith("`"):
        output = output.strip("`")

    return output


def check_gpt_basic_answer(answer, descritpion, type):
    '''

    :param answer:
    :param descritpion:
    :return:
    '''
    if type == "VPV" or type == "AGENT":
        if answer.strip() in descritpion or answer == "None":
            return answer
        else:
            warnings.warn("The " + type + " answer " + answer + " is not in the description " + descritpion)
            return "None"

    elif type == "VUL":
        if len(answer.split()) > 5:
            return "None"
        if answer.strip() in descritpion or answer == "None":
            return answer
        else:
            warnings.warn("The " + type + " answer " + answer + " is not in the description " + descritpion)
            return "None"

    elif type == "COMP":
        if ";" in answer:
            new_comp = []
            for item in answer.split(";"):
                if item.strip() not in descritpion:
                    warnings.warn("The " + type + " answer " + answer + " is not in the description" + descritpion)
                    continue
                else:
                    new_comp.append(item.strip())
            return ";".join(new_comp)
        else:
            if answer.strip() not in descritpion and answer != "None":
                warnings.warn("The COMP answer is not in the description!")
                return "None"
            else:
                return answer


def find_bracket_closure(s):
    # 使用非贪婪匹配来找到第一个闭包
    start = s.find('{')
    end = s.rfind('}')
    if start != -1 and end != -1 and start < end:
        return s[start:end + 1]  # 返回包含两头的花括号的子串
    else:
        return None  # 如果没有找到有效的闭包，返回None


def filter_VPV_COM(COMP, VPV):
    '''

    :param description:
    :return:
    '''
    if ";" in COMP:
       COMP = COMP.split(";")
    else:
        COMP = [COMP]
    filtered_comp = []
    for com in COMP:
        if com not in VPV:
            filtered_comp.append(com)
    return filtered_comp


def cos_similarity(vec1, vec2):
    cosine_distance = distance.cosine(vec1, vec2)

    # 计算余弦相似度
    cosine_similarity = 1 - cosine_distance
    return cosine_similarity