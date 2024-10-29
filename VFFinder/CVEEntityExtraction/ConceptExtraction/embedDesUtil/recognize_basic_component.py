
import os
import time
import sys
sys.path.append("../../../")
import nltk
import hashlib
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.utils import parse_tree, Node, dfs, lca, check_gpt_basic_answer, filter_VPV_COM, regulate_gpt_output
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.basicConcRecPrompt import VPV_recognition_prompt_template, VUL_recognition_prompt_template, AGENT_recognition_prompt_template, COMP_recognition_prompt_template
from LLMRequest.ask_GPT import query_chat_gpt
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.BasicComponent import BasicComponent
import pickle
from CommonUtils.vecUtils import cos_simialrity
from tqdm import tqdm


vul_dict_dir = "//data/alan/VFlocation/CVEEntityExtraction/ConceptExtractionRAG/embedDesUtil/baseVulDict/vulDict"

def recognize_basic_component_online(description, vul_simi_model, vul_dict_dir, vul_case_num)->dict:
    '''

    :param description:
    :return:
    '''
    basic_component = {
        'VPV': '',
        'VUL': '',
        'AGENT': '',
        'COMP': ''

    }
    extract_VPV_phase_question = VPV_recognition_prompt_template.format(description)
    VPV_phase = query_chat_gpt(extract_VPV_phase_question)
    VPV_phase = regulate_gpt_output(VPV_phase)
    VPV_phase = check_gpt_basic_answer(VPV_phase, description, 'VPV')
    basic_component['VPV'] = VPV_phase

    VUL_phase = extract_vul_component(description, vul_simi_model, vul_dict_dir, vul_case_num)
    VUL_phase = regulate_gpt_output(VUL_phase)
    VUL_phase = check_gpt_basic_answer(VUL_phase, description, 'VUL')
    basic_component['VUL'] = VUL_phase

    AGENT = extract_agent_component(description)
    AGENT = check_gpt_basic_answer(AGENT, description, 'AGENT')
    basic_component['AGENT'] = AGENT

    if VPV_phase == "None":
        basic_component['COMP'] = []
        return basic_component

    extract_COMP_question = COMP_recognition_prompt_template.format(VPV_phase, description)
    COMP = query_chat_gpt(extract_COMP_question)
    COMP = regulate_gpt_output(COMP)
    COMP = check_gpt_basic_answer(COMP, description, 'COMP')
    COMP = filter_VPV_COM(COMP, VPV_phase)
    basic_component['COMP'] = COMP

    return basic_component


def extract_agent_component(description:str)->str:
    '''
    extract the agent component from the description
    :param description:
    :return:
    '''
    has_agent = "None"
    description_word = nltk.word_tokenize(description)

    if "attacker" in description_word:
        if description_word.index("attacker") - 1 >= 0 and description_word[description_word.index("attacker") - 1] == "remote":
            has_agent = "remote attacker"
        else:
            has_agent = "attacker"
    if "attackers" in description_word:
        if description_word.index("attackers") - 1 >= 0 and description_word[description_word.index("attackers") - 1] == "remote":
            has_agent = "remote attackers"
        else:
            has_agent = "attackers"
    return has_agent


def extract_vul_component(description:str, simi_model, vul_dict_dir, case_num:int)->str:
    '''
    extract the vul component from the description
    :param description:
    :return:
    '''
    with open(vul_dict_dir, "rb") as f:
        vul_dict = pickle.load(f)

    sentence_vec = simi_model.encode(description)
    cos_sim = [(cos_simialrity(vul, sentence_vec), vul) for vul in vul_dict.keys()]
    cos_sim.sort(key=lambda x: x[0], reverse=True)
    cos_sim = cos_sim[:case_num]
    question = format_VUL_question(description, [vul_dict[item[1]] for item in cos_sim], VUL_recognition_prompt_template)
    VUL = query_chat_gpt(question)
    return VUL


def format_VUL_question(description, case_list, template):
    '''
    format the VUL question
    :param description:
    :param case_list:
    :param template:
    :return:
    '''
    vul_type = [case[0] for case in case_list]
    vul_case = [case[1] for case in case_list]

    vul_type_str = ",".join(vul_type)

    case_str = '''INPUT:{}
OUTPUT:{}
    '''.format(vul_case[0], vul_type[0])

    question = template.format(vul_type_str, case_str, description)
    return question


if __name__ == "__main__":
    with open("../../../resource/CVE_description", "r") as f:
        all_description = f.readlines()

    from VFRanking.utils import BERT_PATH
    from sentence_transformers import SentenceTransformer

    vul_simi_model = SentenceTransformer(BERT_PATH)
    vul_simi_model.to("cpu")
    for line in tqdm(all_description):
        CVE_ID = line.split(":")[0]
        description = ":".join(line.split(":")[1:])
        sentences = nltk.sent_tokenize(description)
        for sentence in sentences:
            sentence_hash = hashlib.md5(sentence.encode()).hexdigest()
            file_name = CVE_ID + "_" + str(sentence_hash)
            if os.path.exists("../../../resource/CVETree/BasicComponent/" + file_name):
                continue
            basic_component = BasicComponent()
            basic_component.CVE_ID = CVE_ID
            basic_component.description = sentence
            time.sleep(3)
            basic_component.component_dict = recognize_basic_component_online(sentence, vul_simi_model, vul_dict_dir, 2)

            with open("../../../resource/CVETree/BasicComponent/" + file_name, "wb") as f:
                pickle.dump(basic_component, f)


# from VFRanking.utils import BERT_PATH
# from sentence_transformers import SentenceTransformer
#
# vul_simi_model = SentenceTransformer(BERT_PATH)
# vul_simi_model.to("cpu")
# sentence = "The URLValidator class in Apache Struts 2 2.3.20 through 2.3.28.1 and 2.5.x before 2.5.1 allows remote attackers to cause a denial of service via a null value for a URL field"
# recognize_basic_component_online(sentence, vul_simi_model, vul_dict_dir, 2)
