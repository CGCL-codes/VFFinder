

from APIFunctionality.API import API
import javalang
import traceback


def extract_API_code_variable_name(source_code:str)->list:
    try:
        tree = javalang.parse.parse(source_code)
    except Exception:
        source_code = "public class Main {\n" + source_code + "\n}"
        try:
            tree = javalang.parse.parse(source_code)
        except Exception:
            # traceback.print_exc()
            return []

    variables = set()

    for path, node in tree:
        if isinstance(node, javalang.tree.VariableDeclarator):
            variables.add(node.name)
        elif isinstance(node, javalang.tree.LocalVariableDeclaration):
            for declarator in node.declarators:
                variables.add(declarator.name)
        elif isinstance(node, javalang.tree.VariableDeclaration):
            for declarator in node.declarators:
                variables.add(declarator.name)
        elif isinstance(node, javalang.tree.MethodInvocation):
            if node.qualifier:
                variables.add(node.qualifier)
            for arg in node.arguments:
                if isinstance(arg, javalang.tree.MemberReference):
                    variables.add(arg.member)
        elif isinstance(node, javalang.tree.MemberReference):
            variables.add(node.member)
    return list(variables)


def extract_API_code_entity(api:API):
    source_code = api.get_source()
    if source_code != "":
        variable_list = extract_API_code_variable_name(source_code)
    else:
        misc_content = api.get_misc_content()
        variable_list = extract_API_code_variable_name(misc_content)
    return variable_list