
import time
import sys
sys.path.append("//data/alan/VFlocation/")
sys.path.append("//data/alan/VFlocation/CVEEntityExtraction/ConceptExtractionRAG/embedDesUtil")
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.utils import parse_tree, Node, dfs, lca, find_leaves, remove_dot_nodes, cut_flag_node
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.BasicComponent import BasicComponent
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.recognize_basic_component import recognize_basic_component_online
import os
import hashlib
import pickle
import json


def recoginize_basic_component(CVE_ID, description, basic_component_dir:str, vul_simi_model, vul_dict_dir, vul_case_num=2)->BasicComponent:
    sentence_hash = hashlib.md5(description.encode()).hexdigest()
    file_name = CVE_ID + "_" + sentence_hash
    if not os.path.exists(os.path.join(basic_component_dir, file_name)):
        base_componet_dict = recognize_basic_component_online(description, vul_simi_model, vul_dict_dir, vul_case_num)
        basic_component = BasicComponent()
        basic_component.CVE_ID = CVE_ID
        basic_component.description = description
        basic_component.component_dict = base_componet_dict
        with open(os.path.join(basic_component_dir, file_name), 'wb') as f:
            pickle.dump(basic_component, f)
        return basic_component
    else:
        with open(os.path.join(basic_component_dir, file_name), 'rb') as f:
            basic_component = pickle.load(f)

        return basic_component


def replace_basic_component(description, basic_component):
    '''
    replace the basic component in the description
    :param description:
    :param basic_component:
    :return:
    '''
    for key, value in basic_component.component_dict.items():
        if value == "None":
            continue
        if type(value) == list:
            for v in value:
                description = description.replace(v, key)
        else:
            if key == "AGENT":
                description = description.replace(value, key)
            else:
                description = description.replace(value, key)
    return description


def tree_build(CVE_ID, description, nlp_model, basic_componet_dir,  vul_simi_model, vul_dict_dir):
    """
    Build the tree structure of the description
    :param description: str, the description of the CVE
    :return: dict, the tree structure of the description
    """
    basic_component = recoginize_basic_component(CVE_ID, description, basic_componet_dir, vul_simi_model, vul_dict_dir)
    description = replace_basic_component(description, basic_component)
    output = nlp_model.annotate(description, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
    })
    try:
        output = json.loads(output)
    except Exception as e:
        print(description)
        print(e)
        raise Exception("The description is not valid")
    description_tree_str = output['sentences'][0]['parse']
    description_tree = parse_tree(description_tree_str)
    draw_tree(description_tree, "original_tree.png")
    refine_tree(description_tree)
    return description_tree


def merge_basic_component(root, basic_component_value, basic_component_key):
    """

    :param description_tree:
    :param basic_component:
    :return:
    """
    words = basic_component_value.split()
    # 找到代表这些单词的叶子节点
    all_leves = find_leaves(root)
    leaves = [node for node in all_leves if node.label in words]
    # 遍历树，记录每个节点的父节点和深度
    parents = {}
    depths = {}
    dfs(root, None, 0, parents, depths)
    # 找到叶子节点的最近公共祖先
    ancestor = leaves[0]
    for leaf in leaves[1:]:
        ancestor = lca(ancestor, leaf, parents, depths)
    # 用一个新的节点替换这个祖先节点
    parents[ancestor].children = [Node(basic_component_key) if child == ancestor else child for child in parents[ancestor].children]


def refine_tree(description_tree):
    '''
    remove the dot nodes in the tree
    :param description_tree:
    :return:
    '''
    description_tree = remove_dot_nodes(description_tree)
    cut_flag_node(description_tree)
    return description_tree


#
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from stanfordcorenlp import StanfordCoreNLP
from collections import OrderedDict


def add_edges(graph, node):
    graph.add_node(node.id, label=node.label)
    for child in node.children:
        graph.add_edge(node.id, child.id)
        add_edges(graph, child)


def draw_tree(tree, file_name):
    graph = nx.DiGraph()
    graph.graph['node'] = OrderedDict()
    add_edges(graph, tree)
    labels = {node: data['label'] for node, data in graph.nodes(data=True)}
    plt.figure(figsize=(15, 15), dpi=300)
    pos = graphviz_layout(graph, prog='dot')
    nx.draw(graph, pos, labels=labels, with_labels=True, arrows=False)
    #plt.show()
    plt.savefig(file_name)
#
#
if __name__ == "__main__":
    from VFRanking.utils import BERT_PATH
    from sentence_transformers import SentenceTransformer

    vul_dict_dir = "//data/alan/VFlocation/CVEEntityExtraction/ConceptExtractionRAG/embedDesUtil/baseVulDict/vulDict"
    vul_simi_model = SentenceTransformer(BERT_PATH)
    vul_simi_model.to("cpu")


    sentence = "The SecurityTokenService (STS) in Apache CXF before 2.6.12 and 2.7.x before 2.7.9 does not properly validate SAML tokens when caching is enabled, which allows remote attackers to gain access via an invalid SAML token."
    nlp = StanfordCoreNLP(r'//data/alan/stanford-corenlp-4.5.7')
    description_tree = tree_build("CVE-2014-0034", sentence, nlp, "//data/alan/VFlocation/resource/CVETree/BasicComponent", vul_simi_model, vul_dict_dir)

    draw_tree(description_tree, "candidate.png")

    # case1 = 'By measuring the response time for the login request, arbitrary attribute data can be retrieved from LDAP user objects.'
    # description_tree = tree_build('CVE-2021-23899', case1, nlp,
    #                               "//data/alan/VFlocation/resource/CVETree/BasicComponent", vul_simi_model, vul_dict_dir)
    # draw_tree(description_tree, "case1.png")
    #
    # case2 = 'jasypt before 1.9.2 allows a timing attack against the password hash comparison.'
    # description_tree = tree_build('CVE-2014-9970', case2, nlp, "//data/alan/VFlocation/resource/CVETree/BasicComponent", vul_simi_model, vul_dict_dir)
    # draw_tree(description_tree, "case2.png")