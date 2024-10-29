
import json
import os.path

from LLMRequest.ask_GPT import query_chat_gpt
from CVEEntityExtraction.clzExtraction import extract_clz_entity_rule
from CVEEntityExtraction.CVEEntity import CVEEntity
from CVEEntityExtraction.EntityStore import store_logic
from CVEEntityExtraction.utils import clean_entity_list
from CVEEntityExtraction.utils import CVE_PARTS_DIR
from CommonUtils.textUtils import extract_noun_verb
from CVEEntityExtraction.utils import save_cve_part_json
from CVEEntityExtraction.utils import process_CVE_parts, process_ven_pro_ver, fullfill_AV_IM_RC, set_CVE_entity, split_part_entity, get_basic_component
from stanfordcorenlp import StanfordCoreNLP
import nltk
from CVEEntityExtraction.ConceptExtractionRAG.splitPrompt import construct_split_query
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.utils import regulate_gpt_output, find_bracket_closure


extract_vendor_product_version_prompt_template = '''
Objective:
Extract the vendor, product, and version number mentioned in the given sentence, if you can not find the corresponding answer, leave that field empty.

INPUT: Apache Hive cookie signature verification used a non-constant time comparison which is known to be vulnerable to timing attacks.
OUTPUT: 
vendor: Apache
product: Hive
version number:

INPUT: Apache Shiro before 1.5.2, when using Apache Shiro with Spring dynamic controllers, a specially crafted request may cause an authentication bypass.
OUTPUT: 
vendor: Apache
product: Shiro
version number: 1.5.2

Please learn and strictly follow the examples above, and analyze the following sentence, if you find several answers for one field, separate the answers by a space:
INPUT:{}
OUTPUT:
'''


def extract_vendor_product_version(CVE_description:str):
    question = extract_vendor_product_version_prompt_template.format(CVE_description)
    answer = query_chat_gpt(question)
    return answer



def extract_entity_by_parts(CVE_ID:str, CVE_description:str, CVE_CWE_dict:dict, nlp, extract_opt_dict:dict, embed_mode='treesequence', cve_part_dir="")->CVEEntity:
    CVE_entity = CVEEntity()
    entity = []
    CVE_parts = ""

    if extract_opt_dict["CoT"] == "RCAV_TMP":
        description_sentence_list = nltk.sent_tokenize(CVE_description)
        basic_component_dir = "//data/alan/VFlocation/resource/CVETree/BasicComponent"
        GT_dir = "//data/alan/VFlocation/CVEEntityExtraction/ConceptExtractionRAG/datasetConstruction/" + embed_mode
        vul_dict_dir = "//data/alan/VFlocation/CVEEntityExtraction/ConceptExtractionRAG/embedDesUtil/baseVulDict/vulDict"

        if os.path.exists(os.path.join(cve_part_dir, CVE_ID)):
            with open(os.path.join(cve_part_dir, CVE_ID), "r") as f:
                CVE_parts = json.loads(f.read())
                AV, IM, RC = [CVE_parts["AV"]], [CVE_parts["IM"]], [CVE_parts["RC"]]

        else:
            from VFRanking.utils import BERT_PATH
            from sentence_transformers import SentenceTransformer
            vul_simi_model = SentenceTransformer(BERT_PATH)
            vul_simi_model.to("cpu")
            stanford_nlp = StanfordCoreNLP(r'//data/alan/stanford-corenlp-4.5.7')

            AV,IM,RC = [], [], []
            for sentence in description_sentence_list:
                question = construct_split_query(CVE_ID, sentence, embed_mode, stanford_nlp, basic_component_dir, GT_dir, 2, vul_simi_model, vul_dict_dir)
                answer = query_chat_gpt(question)
                answer = regulate_gpt_output(answer)
                answer = find_bracket_closure(answer)
                AV, IM, RC = fullfill_AV_IM_RC(AV, IM, RC, answer)
            save_cve_part_json(CVE_ID, CVE_description, AV, IM, RC, cve_part_dir)

        VPV_entity_set = set()
        COMP_entity_list = list()
        for sentence in description_sentence_list:
            VPV, _, _, COMP = get_basic_component(CVE_ID, sentence, basic_component_dir)
            if VPV == "None" or VPV == "":
                continue
            for VPV_ele in VPV.split(" "):
                VPV_entity_set.add(VPV_ele)
            for compnent_part in COMP:
                if compnent_part != "None" and compnent_part != "":
                    COMP_entity_list.append(compnent_part)

        clz_name_list = extract_clz_entity_rule(CVE_description, list(VPV_entity_set))
        cve_entity = split_part_entity(CVE_description, CVE_ID, AV, IM, RC, clz_name_list, nlp)
        return cve_entity


    ven_pro_ver = extract_vendor_product_version(CVE_description)
    ven_pro_ver_list = process_ven_pro_ver(ven_pro_ver)
    entity = clean_entity_list(CVE_description, ven_pro_ver_list, entity, extract_opt_dict)
    clz_name_list = extract_clz_entity_rule(CVE_description, ven_pro_ver_list)
    set_CVE_entity(CVE_entity, CVE_ID, CVE_description, clz_name_list, CVE_parts, ven_pro_ver, entity, CVE_CWE_dict)

    return CVE_entity