


class APIEntity(object):
    def __init__(self):
        self.name = ""
        self.clz_name = ""
        self.para_type_list = []
        self.para_name_list = []
        self.description = ""
        #################################################
        self.processed_para_type_list = []
        self.processed_para_name_list = []
        self.clz_entity_lst = []
        self.code_entity_lst = []
        self.name_entity_lst = []
        self.description_entity_lst = []
        self.src_code = ""
        self.cleaned_entity = []

    def set_clz_name(self, clz_name):
        self.clz_name = clz_name

    def get_clz_name(self):
        return self.clz_name

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_clz_entity(self, clz_entity_lst):
        self.clz_entity_lst = clz_entity_lst

    def set_code_entity(self, code_entity_lst):
        self.code_entity_lst = code_entity_lst

    def set_name_entity(self, name_entity_lst):
        self.name_entity_lst = name_entity_lst

    def get_clz_entity(self):
        return self.clz_entity_lst

    def get_code_entity(self):
        return self.code_entity_lst

    def get_name_entity(self):
        return self.name_entity_lst

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_src_code(self, src_code):
        self.src_code = src_code

    def get_src_code(self):
        return self.src_code

    def set_cleaned_entity(self, cleaned_entity):
        self.cleaned_entity = cleaned_entity

    def get_cleaned_entity(self):
        return self.cleaned_entity

    def get_all_entity(self):
        return list(set(self.clz_entity_lst + self.code_entity_lst + self.name_entity_lst + self.processed_para_name_list + self.para_type_list))


    def set_para_type_list(self, para_type_list):
        self.para_type_list = para_type_list

    def get_para_type_list(self):
        return self.para_type_list

    def set_para_name_list(self, para_name_list):
        self.para_name_list = para_name_list

    def get_para_name_list(self):
        return self.para_name_list

    def set_processed_para_type_list(self, processed_para_type_list):
        self.processed_para_type_list = processed_para_type_list

    def get_processed_para_type_list(self):
        return self.processed_para_type_list

    def set_processed_para_name_list(self, processed_para_name_list):
        self.processed_para_name_list = processed_para_name_list

    def get_processed_para_name_list(self):
        return self.processed_para_name_list


    def set_description_entity(self, description_entity_lst):
        self.description_entity_lst = description_entity_lst

    def get_description_entity(self):
        return self.description_entity_lst

    def get_sole_clz_name(self):
        return self.clz_name.split('/')[-1].split('.')[0].strip()

    def get_name_signature(self):
        def pick_name(word):
            for i, char in enumerate(word):
                if not char.isalpha():
                    return word[:i]
            return word

        cleaned_para_type_list = []
        for para_type in self.get_para_type_list():
            cleaned_para_type_list.append(pick_name(para_type))

        return self.get_sole_clz_name() + "@" + self.get_name().split("@")[1] + "@" + ":".join(cleaned_para_type_list)


