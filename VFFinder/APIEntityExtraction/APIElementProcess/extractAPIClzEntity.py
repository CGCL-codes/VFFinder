

from APIFunctionality.API import API


def extract_API_class_entity(api:API):
    class_name = api.get_file_name().split('/')[-1].split('.')[0].strip()
    return [class_name]