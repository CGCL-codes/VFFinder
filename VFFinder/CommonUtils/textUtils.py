

import nltk
from nltk.corpus import wordnet
from CommonUtils.codeUtils import get_para_type_list, form_para_str


def extract_noun_verb_wordnet(w_list:list)->list:
    """
    Extract the noun and verb from the text
    :param text:
    :return:
    """
    new_list = set()
    for word in w_list:
        tagged_word = nltk.pos_tag([word])[0]
        if tagged_word[1] == 'NN' or tagged_word[1] == 'VB' or tagged_word[1] == 'JJ':
            new_list.add(word)

    return list(new_list)


def extract_noun_verb(nlp,w_list:list)->list:
    """
    Extract the noun and verb from the text
    :param text:
    :return:
    """
    new_list = []
    for word in w_list:
        doc = nlp(word)
        for token in doc:
            if token.pos_ == "NOUN" or token.pos_ == "VERB" or token.pos_ == "PROPN" or token.pos_ == "ADJ":
                new_list.append(word)
    return new_list


def split_into_sentences(text):
    # 使用nltk的sent_tokenize函数进行句子分割
    sentences = nltk.sent_tokenize(text)
    return sentences

def transfer_cg_mtd_name(mtd_sig:str):
    '''
    Transfer the method name in call graph to the standard method name
    :param mtd_name:
    :return:
    '''
    mtd_full_class = mtd_sig.split(":")[0]
    mtd_class = mtd_full_class.split(".")[-1]
    mtd_name = mtd_sig.split(":")[1].split("(")[0]
    mtd_para_list = mtd_sig.split(":")[1].split("(")[1].split(")")[0].split(",")
    mtd_para_list = [para.split(".")[-1] for para in mtd_para_list]
    mtd_new_sig =  mtd_name + "@" + ":".join(mtd_para_list) + "@" + mtd_class
    return mtd_new_sig


def transfer_entity_mtd_name(mtd_sig:str):
    '''
    Transfer the method name in API entity to the standard method name
    :param mtd_sig:
    :return:
    '''

    entity_mtd_name = mtd_sig.split("@")[1]
    entity_para_list = [i.split("$")[0] for i in mtd_sig.split("@")[2].split(":")]
    entity_class = mtd_sig.split("@")[3]
    mtd_new_sig = entity_mtd_name + "@" + ":".join(entity_para_list) + "@" + entity_class
    return mtd_new_sig


def transfer_API_cg_name(api)->str:
    '''

    :param api:
    :return:
    '''
    class_name = api.get_file_name().split("/")[-1].split(".")[0].split("$")[0]
    method_name = api.get_name()
    para_list = api.get_para_type_list()
    new_api_name = method_name + "@" + ":".join(para_list) + "@" + class_name
    return new_api_name


def get_groundTruth(GT_dir:str):
    '''

    :param GT_dir:
    :return:
    '''
    with open(GT_dir, "r") as f:
        GT_dict = {}
        for line in f.readlines():
            para_type_list = get_para_type_list(":".join(line.split(":")[1:]))
            GT_dict[line.split(":")[0]] = line.split("/")[-1].split(".")[0].strip() + "@" + line.split(":")[-1].split("(")[0] + "@" + form_para_str(para_type_list)

    return GT_dict

