

from APIFunctionality.API import API
from APIEntityExtraction.utils import split_camel_words


def extract_API_name_entity(api:API):
    api_name = api.get_name().split("@")[1]
    api_name_entity = split_camel_words(api_name)
    return api_name_entity
