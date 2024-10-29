
from CVEEntityExtraction.ConceptExtractionRAG.selectCase.selectCase import select_case
import json
split_template = '''
I want you to act like an expert in vulnerability report analysis, I will give you a description. Your task is to extract the attack vector and root cause from it. Attack vector is the method of triggering the vulnerability. If you can not find the corresponding answer, just answer None
Here are some examples you can follow:
{}

INPUT:{}
OUTPUT:

'''


def construct_split_query(CVE_ID:str, description:str, embed_mode, nlp, basic_component_dir, GT_dir, example_case_num,  vul_simi_model, vul_dict_dir):
    """
    Construct the split query
    :param query: str, the query
    :return: str, the split query
    """
    example_case = select_case(CVE_ID, description, embed_mode, nlp, basic_component_dir, GT_dir, example_case_num,  vul_simi_model, vul_dict_dir)
    case_fill_list = []
    for case in example_case:
        case_input = case.description
        case_output = {
            "Root Cause": case.RC,
            "Attack Vector": case.AV,
        }
        case_fill_list.append((case_input, case_output))
    example_case_str = ''
    for case_input, case_output in case_fill_list:
        example_case_str += "INPUT:" + case_input + "\n"
        example_case_str += "OUTPUT:" + json.dumps(case_output) + "\n\n"

    query = split_template.format(example_case_str, description)
    return query