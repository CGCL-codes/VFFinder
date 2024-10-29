

from APIFunctionality.API import API
from APIEntityExtraction.APIEntity import APIEntity
from APIEntityExtraction.APIElementProcess.extractAPIClzEntity import extract_API_class_entity
from APIEntityExtraction.APIElementProcess.extractAPICodeEntity import extract_API_code_entity
from APIEntityExtraction.APIElementProcess.extractAPINameEntity import extract_API_name_entity
from APIEntityExtraction.APIElementProcess.extractAPIParaEntity import extract_para_name_entity, extract_para_type_entity
from APIEntityExtraction.APIElementProcess.extractAPIString import extract_API_string_entity
from APIEntityExtraction.utils import set_API_entity
from APIEntityExtraction.cleanEntity import clean_entity


def extract_API_entity(nlp, api:API, opt_dict:dict)->APIEntity:
    '''
    Extract the entity from the API
    :param api:
    :return:
    '''

    API_name_entity = extract_or_return_empty_entity(api, opt_dict['APIName'], extract_API_name_entity)
    API_class_entity = extract_or_return_empty_entity(api, opt_dict['APIClz'], extract_API_class_entity)
    API_code_entity = extract_or_return_empty_entity(api, opt_dict['APIVar'], extract_API_code_entity)
    API_para_name_entity = extract_or_return_empty_entity(api, opt_dict['APIParaName'], extract_para_name_entity)
    API_para_type_entity = extract_or_return_empty_entity(api, opt_dict['APIParaType'], extract_para_type_entity)
    API_string_entity = extract_or_return_empty_entity(api, opt_dict['APIString'], extract_API_string_entity)

    API_clean_entity = clean_entity(nlp, API_name_entity + API_class_entity + API_code_entity + API_para_name_entity + API_para_type_entity + API_string_entity)
    apientity = set_API_entity(api, API_para_name_entity, API_para_type_entity, API_name_entity, API_class_entity, API_code_entity, API_clean_entity)

    return apientity


def extract_or_return_empty_entity(api:API, flag:bool, extract_function)->list:
    '''
    Extract the entity from the API
    :param api:
    :return:
    '''
    if flag:
        return extract_function(api)
    else:
        return []