
import os.path
import pickle
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.embedDes import embed_des
from CVEEntityExtraction.ConceptExtractionRAG.datasetConstruction.constructGTDataset import convert_GT_obj_file
from stanfordcorenlp import StanfordCoreNLP
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.utils import cos_similarity


def select_case(CVE_ID, description:str, embed_mode, nlp_model, component_dir, dataset_dir:str, k:int, vul_simi_model, vul_dict_dir):
    """
    Select the case of the description
    :param description: str, the description of the CVE
    :return: str, the case of the description
    """
    embed_to_analysis = embed_des(CVE_ID, description, nlp_model, component_dir, embed_mode, vul_simi_model, vul_dict_dir)
    case_list = search_sort_similar_case(embed_to_analysis, dataset_dir, k)
    return case_list


def search_sort_similar_case(embed_to_analysis, dataset_dir:str, k:int):
    """
    Search and sort the similar cases
    :param embed_to_analysis: str, the embedded description of the CVE
    :param dataset_dir: str, the directory of the dataset
    :param k: int, the number of the similar cases
    :return: list, the list of the similar cases
    """
    with open(os.path.join(dataset_dir, "GT_dict.bin"), "rb") as f:
        GT_dict = pickle.load(f)
    cos_sim_list = [(cos_similarity(embed_to_analysis, key), key) for key in GT_dict.keys()]
    cos_sim_list.sort(key=lambda x: x[0], reverse=True)
    top_k = cos_sim_list[:k]
    case_list = [GT_dict[key] for sim, key in top_k]
    return case_list


def check_GT_result(GT_description_reuslt_dict:dict):
    result_num = 0
    count = 0
    for GT, result_case_list in GT_description_reuslt_dict.items():
        GT_index = get_GT_index(GT, result_case_list)
        if GT_index is None:
            print("Error: The GT case is not in the result list"+GT)
            continue
        result_num = result_num + GT_index
        count = count + 1
        if GT_index != 0:
            print(str(GT_index) +" Error: The GT case is not in the first place"+GT)
    print(result_num/count)



def get_GT_index(description, case_list):
    for index, case in enumerate(case_list):
        if case.description == description:
            return index


# if __name__ == "__main__":
#     # GT_exp()