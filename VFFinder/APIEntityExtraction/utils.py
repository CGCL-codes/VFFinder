
import os.path
import pickle
import re
from APIEntityExtraction.APIEntity import APIEntity
from CommonUtils.textUtils import get_groundTruth


def store_API_entity(api_entity_list, store_path, jar_file_name):
    with open(os.path.join(store_path, jar_file_name), "wb") as f:
        pickle.dump(api_entity_list, f)


def split_camel_words(camel_word: str) -> list:
    words = re.findall(r'[A-Z]?[a-z]+', camel_word)
    if words == []:
        words = [camel_word]
    return words


def get_para_type_list(para_signature:str)->list:
    '''
    获取参数类型列表
    :param para_signature:
    :return:
    '''
    if para_signature == "":
        return []
    para_list = para_signature.split(":")
    para_type_list = [i.split("$")[0] for i in para_list]
    return para_type_list


def get_para_name_list(para_signature:str) -> list:
    '''

    :param para_signature:
    :return:
    '''
    if para_signature == "":
        return []
    para_list = para_signature.split(":")
    para_name_list = [i.split("$")[1] for i in para_list]
    return para_name_list


def set_API_entity(api, API_para_name_entity, API_para_type_entity, API_name_entity, API_class_entity, API_code_entity, API_clean_entity):
    apientity = APIEntity()
    apientity.set_name(api.get_name())
    apientity.set_description(api.get_description())
    apientity.set_para_name_list(api.get_para_name_list())
    apientity.set_para_type_list(api.get_para_type_list())
    apientity.set_processed_para_name_list(API_para_name_entity)
    apientity.set_processed_para_type_list(API_para_type_entity)
    apientity.set_src_code(api.get_source())
    apientity.set_name_entity(API_name_entity)
    apientity.set_clz_entity(API_class_entity)
    apientity.set_clz_name(api.get_file_name())
    apientity.set_code_entity(API_code_entity)
    apientity.set_cleaned_entity(API_clean_entity)
    return apientity

def enumerate_opt(opt_dict:dict)->dict:
    '''
    Enumerate the options in the opt_dict
    :param opt_dict:
    :return:
    '''
    dict_list = []
    for key, value in opt_dict.items():
        new_dict = dict(opt_dict)
        new_dict[key] = not value
        dict_list.append(new_dict)
    return dict_list


