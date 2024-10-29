
from CommonUtils.textUtils import split_into_sentences
import re

class_name_pattern = r'\b[A-Z][a-zA-Z0-9_]*\b'


def normal_pick_clz_name(word:str)->list:
    '''

    :param word:
    :return:
    '''

    clz_name = re.findall(class_name_pattern, word)
    if clz_name:
        return clz_name

    # if word.endswith(".java"):
    #     clz_name = word[:-5]
    #     return [clz_name]
    return []


def pick_clz_name(word:str)->list:
    '''

    :param word:
    :return:
    '''
    if "/" in word:
        clz_name = word.split("/")[-1]
        if clz_name.endswith(".java"):
            clz_name = clz_name[:-5]
            return [clz_name]
        else:
            return normal_pick_clz_name(clz_name)
    else:
        return normal_pick_clz_name(word)


def pick_first_word(word:str)->list:
    '''

    :param word:
    :return:
    '''
    if "/" in word:
        clz_name = word.split("/")[-1]
        if clz_name.endswith(".java"):
            clz_name = clz_name[:-5]
            return [clz_name]
        else:
            return normal_pick_clz_name(clz_name)
    elif word.endswith(".java"):
        return [word[:-5]]
    else:
        return []


def extract_clz_entity_rule(CVE_description:str, ven_pro_ver_list:list):
    '''

    :param clz:
    :return:
    '''

    clz_cddt_list = []
    for sentence in split_into_sentences(CVE_description):
        words = sentence.split(" ")
        if len(words) == 0:
            continue
        clz_cddt_list += pick_first_word(words[0])
        for word in words[1:]:
            clz_cddt_list += pick_clz_name(word)

    ven_pro_ver_list = [entity.lower() for entity in ven_pro_ver_list]
    new_clz_cddt_list = []
    for clz_cddt in clz_cddt_list:
        if clz_cddt.lower() in ven_pro_ver_list:
            continue
        else:
            new_clz_cddt_list.append(clz_cddt)
    return new_clz_cddt_list
