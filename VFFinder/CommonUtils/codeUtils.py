


def get_para_type_list(API_signature:str):
    """
    获取参数名列表
    :param API_signature:
    :return:
    """
    para_type_list = []
    para_list = API_signature.split("(")[1].split(")")[0].split(",")
    for para in para_list:
        para_normalized = para.strip().strip("[]").strip()
        para_type_list.append(para_normalized)
    return para_type_list


def form_para_str(para_type_list:list):
    '''

    :param para_type_list:
    :return:
    '''
    para_str = ":".join(para_type_list)
    return para_str
