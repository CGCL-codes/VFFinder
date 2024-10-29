

from APIEntityExtraction.utils import split_camel_words
from CommonUtils.textUtils import extract_noun_verb_wordnet, extract_noun_verb
from noiseRemoval.util import remove_dup_word

def split_api_element(api_element_list: list) -> list:
    """
    :param api_element_list:
    :return:
    """
    new_api_element_list = []
    for api_element in api_element_list:
        new_api_element_list.extend(split_camel_words(api_element))
    return list(set(new_api_element_list))


def filter_meaningless_words(nlp, entity_list: list) -> list:
    """
    :param entity_list:
    :return:
    """
    new_entity_list = []
    for entity in entity_list:
        if len(entity) > 1 and "_" not in entity and "[" not in entity and "]" not in entity:
            new_entity_list.append(entity)

    noun_verb = extract_noun_verb_wordnet(new_entity_list)
    return noun_verb


def clean_entity(nlp, entity_list: list) -> list:
    """
    :param entity_list:
    :return:
    """
    entity_list = split_api_element(entity_list)
    entity_list = list(set([i.lower() for i in entity_list]))
    entity_list = filter_meaningless_words(nlp, entity_list)
    return entity_list

