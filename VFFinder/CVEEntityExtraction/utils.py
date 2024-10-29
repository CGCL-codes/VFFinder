

from nltk.corpus import wordnet
from BM25Filtering.utils import remove_words
from APIEntityExtraction.utils import split_camel_words
from CommonUtils.textUtils import extract_noun_verb
from CVEEntityExtraction.CVEEntity import CVEEntity
import hashlib
import json
import pickle
import os

CVE_description_file_dir = "../resource/CVE_description"
CVE_entity_storage_dir = "../resource/CVEEntity/CVEEntity"
CVE_CWE_dir = "../resource/CVE_CWE"
CVE_PARTS_DIR = "../resource/CVEParts"
black_list = ["Apache", "Tomcat"]


def remove_duplicate_entity(entity_list:list, ven_pro_ver_list:list)->list:
    """
    Remove duplicate entities from the list
    :param entity_list:
    :return:
    """
    done_id = []
    entity_lower = [entity.lower() for entity in entity_list]
    entity_list = list(set(entity_lower))
    for i in range(len(entity_list)):
        if i in done_id:
            continue
        for j in range(i+1, len(entity_list)):
            if j in done_id:
                continue
            syn1 = wordnet.synsets(entity_list[i])
            syn2 = wordnet.synsets(entity_list[j])
            if syn1 and syn2:
                similarity = syn1[0].path_similarity(syn2[0])
                if similarity is not None and similarity == 1:
                    entity_list[j] = entity_list[i]
                    done_id.append(j)

    ven_pro_ver_list = [entity.lower() for entity in ven_pro_ver_list]
    entity_list = set(entity_list) - set(ven_pro_ver_list)
    entity_list = list(entity_list)
    return entity_list


def remove_dup_entity(entity_list:list)->list:
    done_id = []
    entity_lower = [entity.lower() for entity in entity_list]
    entity_list = list(set(entity_lower))
    for i in range(len(entity_list)):
        if i in done_id:
            continue
        for j in range(i + 1, len(entity_list)):
            if j in done_id:
                continue
            syn1 = wordnet.synsets(entity_list[i])
            syn2 = wordnet.synsets(entity_list[j])
            if syn1 and syn2:
                similarity = syn1[0].path_similarity(syn2[0])
                if similarity is not None and similarity == 1:
                    entity_list[j] = entity_list[i]
                    done_id.append(j)



def process_CVE_parts(CVE_parts:str)->str:
    sentences = CVE_parts.split("\n")
    sentences = [sentence.strip() for sentence in sentences]
    parts_str = " ".join([":".join(i.split(":")[1:]) for i in sentences if i])
    return parts_str


def process_ven_pro_ver(ven_pro_ver:str)->list:
    entity_list = []
    sentences = ven_pro_ver.split("\n")
    sentences = [":".join(i.strip().split(":")[1:]) for i in sentences if i]
    for sentence in sentences:
        entity_list.extend(sentence.split(" "))
    entity_list = [i for i in entity_list if i]
    return entity_list


def refine_entity(entity_list:list):
    after_list1 = []
    after_list2 = []
    for entity in entity_list:
        if "/" in entity:
            after_list1.append(entity.split("/")[-1])
        elif "." in entity:
            after_list1.append(entity.split(".")[-1])
        else:
            after_list1.append(entity)

    for entity in after_list1:
        after_list2.extend(split_camel_words(entity))

    return list(set(after_list2))


def remove_meaningless_entity(description:str, entity:list, extaction_opt_dict:dict):
    return remove_words(description, entity, extaction_opt_dict)


def set_CVE_entity(CVE_entity, CVE_ID, CVE_description, clz_name_list, CVE_parts, ven_pro_ver, entity, CVE_CWE_dict):
    CVE_entity.set_CVE_ID(CVE_ID)
    CVE_entity.set_CVE_description(CVE_description)
    CVE_entity.set_clz_name(clz_name_list)
    CVE_entity.set_atc_rc(CVE_parts)
    CVE_entity.set_ven_pro_ver(ven_pro_ver)
    CVE_entity.set_all_entity(entity)


    if CVE_ID in CVE_CWE_dict:
        CVE_entity.set_CWE_ID(CVE_CWE_dict[CVE_ID])
    else:
        CVE_entity.set_CWE_ID("NVD-CWE-noinfo")
    return CVE_entity


def clean_entity_list(CVE_description:str, ven_pro_ver_list:list, entity_list:list, extaction_opt_dict:dict):
    entity = remove_meaningless_entity(CVE_description, entity_list, extaction_opt_dict)
    entity = refine_entity(entity)
    entity = remove_duplicate_entity(entity, ven_pro_ver_list)
    return entity


def fullfill_AV_IM_RC(AV:list, IM:list, RC:list, answer:str):
    """
    Fullfill the AV, IM, RC
    :param AV:
    :param IM:
    :param RC:
    :param answer:
    :return:
    """
    try:
        answer_dict = json.loads(answer)
    except Exception as e:
        print(answer)
        print(e)
        return AV, IM, RC

    if "Attack Vector" in answer and answer_dict["Attack Vector"] != "None":
        AV.append(answer_dict["Attack Vector"])
    if "Impact" in answer and answer_dict["Impact"] != "None":
        IM.append(answer_dict["Impact"])
    if "Root Cause" in answer and answer_dict["Root Cause"] != "None":
        RC.append(answer_dict["Root Cause"])
    return AV, IM, RC


def split_part_entity(CVE_description:str, CVE_ID, AV:list, IM:list, RC:list, clz_name_list:list, nlp):
    """
    Split the part entity
    :param CVE_description:
    :param AV:
    :param IM:
    :param RC:
    :param nlp:
    :param extract_opt_dict:
    :return:
    """
    # all_logic = AV + IM + RC
    all_logic = AV + RC
    entity_list = []
    for part in all_logic:
        entity_list = entity_list + extract_noun_verb(nlp, [token.text for token in nlp(part)])
    cve_entity = CVEEntity()
    cve_entity.CVE_ID = CVE_ID
    cve_entity.CVE_description = CVE_description
    cve_entity.AV = AV
    cve_entity.IM = IM
    cve_entity.RC = RC
    cve_entity.all_entity = entity_list
    cve_entity.clz_name = clz_name_list
    return cve_entity


def get_basic_component(CVE_ID:str, description:str, basic_component_dir:str):
    """
    Get the basic component
    :param CVE_ID:
    :param description:
    :param basic_component_dir:
    :return:
    """
    hash = hashlib.md5(description.encode()).hexdigest()
    file_name = CVE_ID + "_" + hash
    with open(basic_component_dir + "/" + file_name, "rb") as f:
        basic_component = pickle.load(f)
    VPV = basic_component.component_dict["VPV"]
    VUL = basic_component.component_dict["VUL"]
    AGENT = basic_component.component_dict["AGENT"]
    COMP = basic_component.component_dict["COMP"]

    return VPV, VUL, AGENT, COMP


def save_cve_part_json(CVE_ID, description, AV, RC, IM, cve_part_dir):
    """
    Save the cve part
    :param CVE_ID: str, the CVE ID
    :param cve_part: CVEPart, the cve part
    :param semiGT_dir: str, the semiGT dir
    :return:
    """

    file_name = CVE_ID
    result = {
        "CVE_ID": CVE_ID,
        "Description": description,
        "AV": " ".join(AV),
        "RC": " ".join(RC),
        "IM": " ".join(IM)
    }

    # 将Python对象写入JSON文件
    with open(os.path.join(cve_part_dir, file_name), 'w') as f:
        json.dump(result, f)