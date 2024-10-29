
import os
import shutil
import json
from APIFunctionality.API import API
from APIEntityExtraction.utils import get_para_type_list, get_para_name_list


def transfer_json_obj(api_dict):
    api_list = []
    for api_name, api_content in api_dict.items():
        api = API()
        api.set_name(api_name)
        api.set_para_name_list(get_para_name_list(api_name.split("@")[2]))
        api.set_para_type_list(get_para_type_list(api_name.split("@")[2]))
        api.set_description(api_content["description"])
        api.set_misc_content(api_content["miscContent"])
        api.set_source(api_content["source"])
        api.set_file_name(api_content["fileName"])
        api_list.append(api)
    return api_list


def parse_json_content(API_content_json_dir:str)->dict:
    '''

    :return:
    '''
    json_file_list = os.listdir(API_content_json_dir)
    jar_API_dict = {}
    for json_file in json_file_list:
        with open(os.path.join(API_content_json_dir, json_file), "r") as f:
            data = json.load(f)  # 读取json文件
            api_list = transfer_json_obj(data)
            jar_API_dict[".".join(json_file.split(".")[:-1])] = api_list

    return jar_API_dict


def get_CVE_description(description_file_dir:str)->dict:
    '''

    :param description_file_dir:
    :return:
    '''
    CVE_description_dict = {}
    with open(description_file_dir, "r") as f:
        for line in f.readlines():
            CVE_ID = line.split(":")[0]
            CVE_description = ":".join(line.split(":")[1:])
            CVE_description_dict[CVE_ID] = CVE_description
    return CVE_description_dict


def get_CVE_GAV_mapping(mapping_file_dir:str)->dict:
    '''

    :param mapping_file_dir:
    :return:
    '''
    CVE_GAV_mapping = {}
    with open(mapping_file_dir, "r") as f:
        for line in f.readlines():
            CVE_ID, GAV = line.split("@")
            CVE_GAV_mapping[CVE_ID] = GAV.strip()
    return CVE_GAV_mapping


def filter_done(todo_list:list, done_list:list)->list:
    '''

    :param todo_list:
    :param done_list:
    :return:
    '''
    return [i for i in todo_list if i not in done_list]


def filter_done_dir(todo_list:list, done_dir:str)->list:
    '''

    :param todo_dir:
    :param done_dir:
    :return:
    '''
    done_list = os.listdir(done_dir)
    return filter_done(todo_list, done_list)


def filepath2filename(file_path:str)->str:
    '''

    :param file_path:
    :return:
    '''
    return file_path.split("/")[-1].split(".")[0]


def is_filename_too_long(filename):
    MAX_LENGTH = 255  # Change this value based on your OS and file system
    return len(filename) > MAX_LENGTH


def recreate_directory(path):
    # 判断目录是否存在
    if os.path.exists(path):
        # 若存在，则删除目录
        shutil.rmtree(path)
    # 创建目录
    os.makedirs(path)


def construct_opt_dir(base_dir:str, opt_dict:dict)->str:
    '''

    :param base_dir:
    :param opt_dict:
    :return:
    '''
    opt_dir = ""
    for opt_key, opt_value in opt_dict.items():
        if isinstance(opt_value, dict):
            for key, value in opt_value.items():
                opt_dir = opt_dir + "_" + str(value)
        elif isinstance(opt_value, bool):
            if opt_value:
                opt_dir = opt_dir + "_1"
            else:
                opt_dir = opt_dir + "_0"
        else:
            opt_dir = opt_dir + "_" + str(opt_value)
    opt_dir = base_dir + opt_dir
    return opt_dir


def create_dir_if_not_exist(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def mk_opt_dir(base_dir:str, opt_dict:dict)->str:
    '''

    :param base_dir:
    :param opt_dir:
    :return:
    '''
    opt_dir = construct_opt_dir(base_dir, opt_dict)
    create_dir_if_not_exist(opt_dir)
    return opt_dir


def mk_opt_binary_dir(base_dir:str, opt_dict:dict)->str:
    '''

    :param base_dir:
    :param opt_dict:
    :return:
    '''
    opt_dir = ""
    for opt in opt_dict.values():
        if opt:
            opt_dir = opt_dir + "_1"
        else:
            opt_dir = opt_dir + "_0"
    tgt_dir = base_dir + opt_dir
    create_dir_if_not_exist(tgt_dir)
    return tgt_dir


