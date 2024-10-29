

from APIEntityExtraction.utils import split_camel_words


def extract_para_name_entity(api):
    '''
    Extract the entity from the API
    :param api:
    :return:
    '''
    para_name_list = api.get_para_name_list()
    processed_para_name_entity = []
    for para_name in para_name_list:
        processed_para_name_entity.extend(split_camel_words(para_name))
    return list(set(processed_para_name_entity))


def extract_para_type_entity(api):
    para_type_list = api.get_para_type_list()
    processed_para_type_entity = []
    for para_name in para_type_list:
        processed_para_type_entity.extend(split_camel_words(para_name))
    return list(set(processed_para_type_entity))
