
import os
from tqdm import tqdm
from CommonUtils.textUtils import transfer_entity_mtd_name, transfer_cg_mtd_name
import javalang
from APIEntityExtraction.utils import full_fill_inline_element
from APIEntityExtraction.cleanEntity import clean_entity


class Graph:
    def __init__(self, nodes, adjacency_matrix):
        self.nodes = nodes
        self.adjacency_matrix = adjacency_matrix

    def get_upstream(self, node):
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found in the graph.")
        index = self.nodes.index(node)
        upstream_nodes = [self.nodes[i] for i in range(len(self.nodes)) if self.adjacency_matrix[i][index] == 1]
        return upstream_nodes

    def get_downstream(self, node):
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found in the graph.")
        index = self.nodes.index(node)
        downstream_nodes = [self.nodes[i] for i in range(len(self.nodes)) if self.adjacency_matrix[index][i] == 1]
        return downstream_nodes


def inline_API_elemenet(CVE_ID, API_entity_list:list, jar_CG_dir:str, nlp):
    '''
    Inline the API element
    :param API_entity_list:
    :param jar_name:
    :return:
    '''
    if not os.path.exists(jar_CG_dir):
        raise FileNotFoundError(f"Call graph file {jar_CG_dir} not found.")
    G = construct_adjMatrix(jar_CG_dir)
    extend_API_entity_by_caller_para(API_entity_list, G, nlp)
    extend_API_entity_until_no_change(API_entity_list, G)
    return API_entity_list


def extract_function_para(caller_api_entity, tgt_api_entity):
    # tokens = list(javalang.tokenizer.tokenize(caller_api_entity.get_src_code()))
    tree = javalang.parser.Parser(caller_api_entity.get_src_code())


    class FunctionCallVisitor(javalang.tree.NodeVisitor):
        def __init__(self, function_name):
            self.function_name = function_name
            self.arguments = []

        def visit_MethodInvocation(self, node):
            if node.member == self.function_name:
                self.arguments.append(
                    [arg.member if isinstance(arg, javalang.tree.MemberReference) else arg.value for arg in
                     node.arguments])

    visitor = FunctionCallVisitor(tgt_api_entity.name)
    visitor.visit(tree)
    return visitor.arguments


def extend_API_entity_by_caller_para(API_entity_list, call_graph, nlp):
    '''

    :param API_entity_list:
    :param call_graph:
    :return:
    '''
    for API_entity in API_entity_list:
        api_entity_mtd_sig = transfer_entity_mtd_name(API_entity.get_name())

        try:
            caller_api_entity_list = call_graph.get_upstream(api_entity_mtd_sig)
        except ValueError:
            caller_api_entity_list = []

        caller_para_set = set()
        for caller_api_entity_name in caller_api_entity_list:
            caller_api_entity = find_API_entity_by_name(API_entity_list, caller_api_entity_name)
            if caller_api_entity:
                caller_api_paraname = extract_function_para(caller_api_entity, API_entity)
                for i in caller_api_paraname:
                    caller_para_set.add(i)
        clean_para = clean_entity(nlp, list(caller_para_set))
        API_entity.clean_entity.extend(clean_para)


def extend_API_entity_until_no_change(API_entity_list, call_graph):
    '''
    Extend the API entity until no change
    :return:
    '''
    todo_list = [api_entity for api_entity in API_entity_list if check_inline_condition(api_entity)]
    for api_entity in todo_list:
        origin_api_entity = api_entity.get_cleaned_entity()
        api_entity_mtd_sig = transfer_entity_mtd_name(api_entity.get_name())

        new_api_entity = set(origin_api_entity)
        try:
            callee_api_entity_list = call_graph.get_downstream(api_entity_mtd_sig)
        except ValueError:
            callee_api_entity_list = []

        for callee_api_entity_name in callee_api_entity_list:
            callee_api_entity = find_API_entity_by_name(API_entity_list, callee_api_entity_name)
            if callee_api_entity:
                new_api_entity = new_api_entity.union(callee_api_entity.get_cleaned_entity())

        if set(origin_api_entity) != new_api_entity:
            try:
                caller_api_entity_list = call_graph.get_upstream(api_entity_mtd_sig)
            except ValueError:
                caller_api_entity_list = []

            for caller_api_entity_name in caller_api_entity_list:
                caller_api_entity = find_API_entity_by_name(API_entity_list, caller_api_entity_name)
                if caller_api_entity:
                    todo_list.append(caller_api_entity)

        api_entity.set_cleaned_entity(list(new_api_entity))

    return API_entity_list


def do_java_cg(binary_jar_path:str, output_path:str, tmp_dir:str, lib_path:str):
    '''
    Generate the call graph of the jar file
    :param binary_jar_path:
    :param output_path:
    :return:
    '''
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    all_jar_file = os.listdir(binary_jar_path)
    for jar in tqdm(all_jar_file):
        if os.path.exists(os.path.join(output_path, jar)):
            continue
        cmd = "cp " + os.path.join(binary_jar_path, jar) + " " + tmp_dir
        os.system(cmd)
        cmd = "/lib/jvm/java-8-openjdk-amd64/bin/java -classpath /lib/jvm/java-8-openjdk-amd64/jre/lib/ext:" + tmp_dir + " -jar " + lib_path + " " + os.path.join(binary_jar_path, jar)
        output = os.popen(cmd).read()
        if not output or output == "":
            continue
        with open(os.path.join(output_path, jar), "w") as f:
            f.write(output)
        rm_cmd = "rm " + tmp_dir + "/" + jar
        os.system(rm_cmd)


def construct_adjMatrix(call_graph_dir:str):
    '''
    Construct the adjacency matrix of the call graph
    :param jar_name:
    :param call_graph_path:
    :return:
    '''
    with open(call_graph_dir, "r") as f:
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
    adjacency_matrix = [[0] * len(node_list) for _ in range(len(node_list))]

    for edge in edge_list:
        caller_index = node_list.index(edge[0])
        callee_index = node_list.index(edge[1])
        adjacency_matrix[caller_index][callee_index] = 1

    return Graph(node_list, adjacency_matrix)


def find_API_entity_by_name(API_entity_list, mtd_sig):
    '''
    Find the API entity by the method signature
    :param API_entity_list:
    :param mtd_sig:
    :return:
    '''
    for api_entity in API_entity_list:
        normalize_name = transfer_entity_mtd_name(api_entity.get_name())
        if normalize_name == mtd_sig:
            return api_entity
    return None


def check_inline_condition(api_entity):
    '''
    Check the whether the API entity can be inlined(code line < 5)
    :param api_entity:
    :return:
    '''
    code = api_entity.get_src_code()
    if len(code.split("\n")) < 5:
        return True
    else:
        return False

