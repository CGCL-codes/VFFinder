

def extract_API_description_entity(api)->list:
    '''
    Extract the description entity from the API
    :param api:
    :return:
    '''
    description = api.get_description().strip().strip("/**").strip().strip("*").strip()
    main_description = description.split("\n")[0]

    if main_description == "":
        return []
    else:
        return main_description.strip().split(" ")
