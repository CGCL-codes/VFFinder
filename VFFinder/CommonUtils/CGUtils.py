

import os
import networkx as nx
from APIEntityExtraction.inline import transfer_cg_mtd_name


def get_K_hop_next_neibor(G:nx.DiGraph, node:str, K:int):
    '''
    Get the K-hop neibor of the node
    :param G:
    :param node:
    :param K:
    :return:
    '''
    if K == 0:
        return [node]
    neibor_list = list(G.neighbors(node))
    for i in range(K-1):
        tmp_neibor_list = []
        for neibor in neibor_list:
            tmp_neibor_list += list(G.neighbors(neibor))
        neibor_list = list(set(tmp_neibor_list))
    return neibor_list


def get_K_hop_prev_neibor(G:nx.DiGraph, node:str, K:int):
    '''
    Get the K-hop neibor of the node
    :param G:
    :param node:
    :param K:
    :return:
    '''
    if K == 0:
        return []

    try:
        neibor_list = list(G.predecessors(node))
    except nx.exception.NetworkXError:
        return [node]
    for i in range(K-1):
        tmp_neibor_list = []
        for neibor in neibor_list:
            tmp_neibor_list += list(G.predecessors(neibor))
        neibor_list = list(set(tmp_neibor_list))
    return neibor_list


def get_02K_hop_prev_neibor(G:nx.DiGraph, node:str,  K:int):
    '''
    Get the 0 to K-hop neibor of the node
    :param G:
    :param node:
    :param K:
    :return:
    '''
    if K == 0:
        return [node]

    all_node = [node]
    neibor_list = all_node

    for i in range(K):
        tmp_neibor_list = []

        for neibor in neibor_list:
            try:
                tmp_neibor_list += list(G.predecessors(neibor))
            except nx.exception.NetworkXError:
                continue

        neibor_list = list(set(tmp_neibor_list))
        all_node = list(set(all_node + neibor_list))
    return all_node



def calculate_distance(G:nx.DiGraph, node1:str, node2:str)->int:
    '''
    Calculate the distance between two nodes
    :param node1:
    :param node2:
    :return:
    '''
    try:
        distance = nx.shortest_path_length(G, source=node1, target=node2)
    except nx.NodeNotFound:
        distance = -1
    except nx.NetworkXNoPath:
        distance = -1
    return distance



def construct_CG_network(call_edge_dir:str)->nx.DiGraph:
    '''
    Construct the call graph network
    :param call_edge_dir:
    :return:
    '''
    if not os.path.exists(call_edge_dir):
        raise FileNotFoundError(f"Call edge file {call_edge_dir} not found.")

    with open(call_edge_dir, "r") as f:
        lines = f.readlines()
    edge_list = []
    for line in lines:
        if line[:2] != "M:":
            continue
        caller = line.split(" ")[0].lstrip("M:").rstrip("\n")
        callee = line.split(" ")[1][3:].strip().rstrip("\n")
        if caller.startswith("java.") or callee.startswith("java."):
            continue
        caller = transfer_cg_mtd_name(caller)
        callee = transfer_cg_mtd_name(callee)
        edge_list.append((caller, callee))

    node_list = list(set([i[0] for i in edge_list] + [i[1] for i in edge_list]))
    G = nx.DiGraph()
    G.add_nodes_from(node_list)
    G.add_edges_from(edge_list)
    return G
